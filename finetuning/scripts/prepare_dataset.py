#!/usr/bin/env python3
"""
Dataset Preparation Script for HRA Finetuning

Prepares stratified train/validation/test splits from HRA-EXP-V1 experiment results.

Source: docs/prompt_evaluation/FULL_RESULTS_DETAIL.md

IMPORTANT CLARIFICATIONS:
- Source dataset: HRA-EXP-V1 results (90 candidate × vacancy pairs)
- Input (user message): Candidate resume + Job vacancy
- Target (assistant message): Judge scores (gpt-4.1) as ground truth
- System prompt: Prompt A (production) from experiment
- DO NOT use Prompt A or Prompt B results as ground truth
- Judge scores must be extracted from reasoning text (e.g., "Должность: ... (30/30)")

Stratification:
- 30 obvious_match cases → 24 train / 3 validation / 3 test
- 30 borderline cases → 24 train / 3 validation / 3 test
- 30 obvious_no_match cases → 24 train / 3 validation / 3 test

Total: 72 train / 9 validation / 9 test

Author: HRA Team
Date: 2026-06-28
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple


def load_config(config_path: str) -> Dict[str, Any]:
    """Load experiment configuration from YAML file."""
    import yaml
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def parse_judge_reasoning(reasoning: str) -> Dict[str, int]:
    """
    Extract score components from Judge reasoning text.

    Judge format (from gpt-4.1):
        "1. Должность: ... (30/30)"
        "2. Навыки: ... (33/35)"
        "3. Опыт: ... (20/20)"
        "4. Условия: ... (15/15)"

    Or alternative format:
        "Кандидат претендует на должность 'Системный аналитик', что полностью совпадает с вакансией (30/30)."

    Returns:
        Dict with role_score, skills_score, experience_score, conditions_score
        Returns empty dict if parsing fails.
    """
    scores = {}

    # Pattern: number/total in context of each criterion
    patterns = {
        'role_score': [
            r'Должност[иь][^\d]*(\d{1,2})/30',
            r'должност[иью][^\d]*(\d{1,2})/30',
            r'рол[иью][^\d]*(\d{1,2})/30',
        ],
        'skills_score': [
            r'Навыки[^\d]*(\d{1,2})/35',
            r'навык[а-я]*[^\d]*(\d{1,2})/35',
            r'ключевые навыки[^\d]*(\d{1,2})/35',
        ],
        'experience_score': [
            r'Опыт[^\d]*(\d{1,2})/20',
            r'опыт работы[^\d]*(\d{1,2})/20',
        ],
        'conditions_score': [
            r'Услови[яй][^\d]*(\d{1,2})/15',
            r'условия[^\d]*(\d{1,2})/15',
            r'Зарплат[а-я]*[^\d]*(\d{1,2})/15',
        ],
    }

    for score_name, score_patterns in patterns.items():
        for pattern in score_patterns:
            match = re.search(pattern, reasoning, re.IGNORECASE)
            if match:
                scores[score_name] = int(match.group(1))
                break

    return scores


def parse_full_results_file(file_path: str) -> List[Dict[str, Any]]:
    """
    Parse FULL_RESULTS_DETAIL.md to extract all 90 cases.

    Returns:
        List of case dictionaries with:
        - case_code: str
        - case_type: 'obvious_match' | 'borderline' | 'obvious_no_match'
        - candidate: dict
        - vacancy: dict
        - judge_score: int
        - judge_decision: str
        - judge_reasoning: str
        - judge_scores: dict (extracted scores from reasoning)
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    cases = []

    # Split by case headers
    case_pattern = r'### (HRA-EVAL-\d+) — Пара #(\d+)'
    case_matches = list(re.finditer(case_pattern, content))

    for i, match in enumerate(case_matches):
        case_code = match.group(1)
        pair_num = int(match.group(2))

        # Extract case content until next case or section
        start_pos = match.end()
        if i + 1 < len(case_matches):
            end_pos = case_matches[i + 1].start()
        else:
            # Find next major section
            next_section = re.search(r'\n---\n\n## ', content[start_pos:])
            if next_section:
                end_pos = start_pos + next_section.start()
            else:
                end_pos = len(content)

        case_content = content[start_pos:end_pos]

        # Parse candidate
        candidate = {}
        candidate_patterns = {
            'full_name': r'\*\*ФИО:\*\* (.+)',
            'desired_position': r'\*\*Должность:\*\* (.+)',
            'experience_years': r'\*\*Опыт:\*\* ([\d.]+)',
            'city': r'\*\*Город:\*\* (.+)',
            'salary_expectation': r'\*\*Зарплатные ожидания:\*\* ([\d\s]+)',
            'skills': r'\*\*Навыки:\*\* (.+)',
            'candidate_summary': r'\*\*Summary:\*\* (.+)',
        }

        for field, pattern in candidate_patterns.items():
            m = re.search(pattern, case_content)
            if m:
                value = m.group(1).strip()
                if field == 'experience_years':
                    value = float(value)
                elif field == 'salary_expectation':
                    value = int(value.replace(' ', '').replace('₽', '').replace(',', ''))
                elif field == 'skills':
                    value = [s.strip() for s in value.split(',')]
                candidate[field] = value

        # Parse vacancy
        vacancy = {}
        vacancy_section = re.search(r'#### 💼 Вакансия\n\n(.+?)(?=\n#### |$)', case_content, re.DOTALL)
        if vacancy_section:
            vacancy_text = vacancy_section.group(1)
            vacancy_patterns = {
                'title': r'\*\*Должность:\*\* (.+)',
                'salary_min': r'\*\*Зарплата:\*\* ([\d\s]+)–',
                'salary_max': r'\*\*Зарплата:\*\* [\d\s]+–([\d\s]+)',
                'description': r'\*\*Описание:\*\* (.+)',
                'requirements': r'\*\*Требования:\*\* (.+)',
            }
            for field, pattern in vacancy_patterns.items():
                m = re.search(pattern, vacancy_text)
                if m:
                    value = m.group(1).strip()
                    if field in ['salary_min', 'salary_max']:
                        value = int(value.replace(' ', '').replace('₽', '').replace(',', ''))
                    vacancy[field] = value

        # Parse Judge
        judge_section = re.search(
            r'#### ⚖️ Judge.*?\n\n\*\*Score:\*\* (\d+) \((✅|❌) (\w+)\)\n\n\*\*Обоснование:\*\* (.+?)(?=\n\n#### |$)',
            case_content,
            re.DOTALL
        )
        if judge_section:
            judge_score = int(judge_section.group(1))
            judge_decision = judge_section.group(3)  # 'match' or 'no_match'
            judge_reasoning = judge_section.group(4).strip()

            # Extract score components from reasoning
            judge_scores = parse_judge_reasoning(judge_reasoning)

            # Determine case type from case code
            case_num = int(case_code.split('-')[-1])
            if 1 <= case_num <= 10:
                case_type = 'obvious_match'
            elif 11 <= case_num <= 20:
                case_type = 'obvious_no_match'
            elif 21 <= case_num <= 30:
                case_type = 'borderline'
            else:
                case_type = 'unknown'

            case_data = {
                'case_code': case_code,
                'pair_num': pair_num,
                'case_type': case_type,
                'candidate': candidate,
                'vacancy': vacancy,
                'judge_score': judge_score,
                'judge_decision': judge_decision,
                'judge_reasoning': judge_reasoning,
                'judge_scores': judge_scores,
            }

            cases.append(case_data)

    return cases


def validate_judge_scores(case: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """
    Validate that judge_scores were extracted correctly.

    Returns:
        (is_valid, error_message)
    """
    judge_scores = case.get('judge_scores', {})
    expected_keys = {'role_score', 'skills_score', 'experience_score', 'conditions_score'}

    if not judge_scores:
        return False, "No scores extracted from Judge reasoning"

    missing_keys = expected_keys - set(judge_scores.keys())
    if missing_keys:
        return False, f"Missing score components: {missing_keys}"

    # Validate sum
    total = sum(judge_scores.values())
    judge_score = case.get('judge_score', 0)

    if abs(total - judge_score) > 2:  # Allow small rounding errors
        return False, f"Score sum ({total}) doesn't match Judge score ({judge_score})"

    return True, None


def case_to_messages(case: Dict[str, Any], system_prompt: str) -> Dict[str, Any]:
    """
    Convert a case to messages format for training.

    Args:
        case: Case dictionary with candidate, vacancy, judge data
        system_prompt: System prompt (Prompt A from production)

    Returns:
        Dictionary with 'messages' key
    """
    candidate = case['candidate']
    vacancy = case['vacancy']
    judge_scores = case['judge_scores']

    # Build user content
    user_content = f"""КАНДИДАТ:

ФИО: {candidate.get('full_name', '[АНОНИМИЗИРОВАНО]')}
Должность: {candidate.get('desired_position', '')}
Опыт: {candidate.get('experience_years', 0)} лет
Город: {candidate.get('city', '')}
Зарплатные ожидания: {candidate.get('salary_expectation', 0)}
Навыки: {', '.join(candidate.get('skills', []))}

Summary: {candidate.get('candidate_summary', '')}

ВАКАНСИЯ:

Должность: {vacancy.get('title', '')}
Зарплата: {vacancy.get('salary_min', 0)}-{vacancy.get('salary_max', 0)}
Описание: {vacancy.get('description', '')}
Требования: {vacancy.get('requirements', '')}"""

    # Build assistant content (JSON output from Judge)
    assistant_content = json.dumps({
        'role_score': judge_scores['role_score'],
        'skills_score': judge_scores['skills_score'],
        'experience_score': judge_scores['experience_score'],
        'conditions_score': judge_scores['conditions_score'],
        'total_score': case['judge_score'],
        'decision': case['judge_decision'],
        'reason': case['judge_reasoning'],
    }, ensure_ascii=False)

    return {
        'messages': [
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': user_content},
            {'role': 'assistant', 'content': assistant_content},
        ]
    }


def stratify_split(
    cases: List[Dict[str, Any]],
    train_per_group: int = 24,
    val_per_group: int = 3,
    test_per_group: int = 3,
    seed: int = 42
) -> Tuple[List[Dict], List[Dict], List[Dict]]:
    """
    Stratify cases into train/validation/test splits.

    Ensures each group (obvious_match, borderline, obvious_no_match)
    is represented proportionally in each split.

    Args:
        cases: List of all 90 cases
        train_per_group: Cases per group for training (default: 24)
        val_per_group: Cases per group for validation (default: 3)
        test_per_group: Cases per group for testing (default: 3)
        seed: Random seed for reproducibility

    Returns:
        Tuple of (train_cases, val_cases, test_cases)
    """
    import random
    random.seed(seed)

    groups = {
        'obvious_match': [],
        'borderline': [],
        'obvious_no_match': []
    }

    # Group cases
    for case in cases:
        group_name = case.get('case_type', 'borderline')
        if group_name in groups:
            groups[group_name].append(case)

    # Validate group sizes
    for group_name, group_cases in groups.items():
        expected = 30
        if len(group_cases) != expected:
            print(f"Warning: Group '{group_name}' has {len(group_cases)} cases, expected {expected}")

    train_cases = []
    val_cases = []
    test_cases = []

    for group_name, group_cases in groups.items():
        # Shuffle within group
        random.shuffle(group_cases)

        # Split
        train_cases.extend(group_cases[:train_per_group])
        val_cases.extend(group_cases[train_per_group:train_per_group + val_per_group])
        test_cases.extend(group_cases[train_per_group + val_per_group:])

    return train_cases, val_cases, test_cases


def save_jsonl(cases: List[Dict[str, Any]], output_path: str) -> None:
    """
    Save cases to JSONL file.

    Args:
        cases: List of cases in messages format
        output_path: Path to output file
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        for case in cases:
            f.write(json.dumps(case, ensure_ascii=False) + '\n')


def main():
    """Main entry point for dataset preparation."""
    parser = argparse.ArgumentParser(
        description="Prepare stratified dataset for HRA finetuning from HRA-EXP-V1 results"
    )
    parser.add_argument(
        '--config',
        type=str,
        default='configs/experiment_001.yaml',
        help='Path to experiment configuration'
    )
    parser.add_argument(
        '--input',
        type=str,
        default='../docs/prompt_evaluation/FULL_RESULTS_DETAIL.md',
        help='Path to FULL_RESULTS_DETAIL.md'
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        default='data',
        help='Output directory for dataset files'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Validate input without creating output files'
    )
    parser.add_argument(
        '--require-manual-review',
        action='store_true',
        help='Flag cases with missing scores as requiring manual review'
    )

    args = parser.parse_args()

    print("=" * 60)
    print("HRA Dataset Preparation")
    print("=" * 60)

    # Load config
    print(f"\nLoading config: {args.config}")
    config = load_config(args.config)

    # Parse FULL_RESULTS_DETAIL.md
    print(f"\nParsing: {args.input}")
    cases = parse_full_results_file(args.input)

    print(f"\nParsed {len(cases)} cases from HRA-EXP-V1")

    # Group statistics
    case_types = {}
    for case in cases:
        ct = case.get('case_type', 'unknown')
        case_types[ct] = case_types.get(ct, 0) + 1

    print("\nCase type distribution:")
    for ct, count in sorted(case_types.items()):
        print(f"  {ct}: {count}")

    # Validate Judge scores
    print("\nValidating Judge scores...")
    valid_cases = []
    invalid_cases = []

    for case in cases:
        is_valid, error = validate_judge_scores(case)
        if is_valid:
            valid_cases.append(case)
        else:
            invalid_cases.append((case, error))
            if args.require_manual_review:
                case['requires_manual_review'] = True

    print(f"  Valid: {len(valid_cases)}")
    print(f"  Invalid: {len(invalid_cases)}")

    if invalid_cases:
        print("\nInvalid cases (missing or incorrect scores):")
        for case, error in invalid_cases[:5]:  # Show first 5
            print(f"  {case['case_code']} Pair #{case['pair_num']}: {error}")

    if args.dry_run:
        print("\n[DRY RUN] Validation complete. Exiting.")
        return 0

    # Stratified split
    print("\nStratifying dataset...")
    train_cases, val_cases, test_cases = stratify_split(valid_cases)

    print(f"\nSplit:")
    print(f"  Train: {len(train_cases)} cases")
    print(f"  Validation: {len(val_cases)} cases")
    print(f"  Test: {len(test_cases)} cases")

    # System prompt: Prompt A (production)
    # IMPORTANT: This is the production prompt from HRA-EXP-V1 experiment
    # Used for training Qwen to match production behavior
    system_prompt = """Ты HR matching assistant.

Сравни кандидата и вакансию по критериям:

1. Должность / роль — 30 баллов
2. Навыки — 35 баллов
3. Опыт — 20 баллов
4. Город / формат / зарплатные ожидания — 15 баллов

Итоговый score должен быть от 0 до 100.

Правила:
- score >= 60 → decision = "match"
- score < 60 → decision = "no_match"
- не выдумывай навыки и опыт
- если данных недостаточно, снижай score
- reason должен кратко объяснять, почему выставлен такой score

Верни строго JSON по схеме."""

    # Convert to messages format
    print("\nConverting to messages format...")
    train_data = [case_to_messages(c, system_prompt) for c in train_cases]
    val_data = [case_to_messages(c, system_prompt) for c in val_cases]
    test_data = [case_to_messages(c, system_prompt) for c in test_cases]

    # Save datasets
    print(f"\nSaving to {args.output_dir}/...")
    save_jsonl(train_data, os.path.join(args.output_dir, 'train.jsonl'))
    save_jsonl(val_data, os.path.join(args.output_dir, 'validation.jsonl'))
    save_jsonl(test_data, os.path.join(args.output_dir, 'test.jsonl'))

    print(f"\n✅ Dataset created successfully!")
    print(f"   - train.jsonl: {len(train_data)} cases")
    print(f"   - validation.jsonl: {len(val_data)} cases")
    print(f"   - test.jsonl: {len(test_data)} cases")

    if invalid_cases:
        print(f"\n⚠️  {len(invalid_cases)} cases require manual review (missing Judge scores)")

    return 0


if __name__ == '__main__':
    sys.exit(main())