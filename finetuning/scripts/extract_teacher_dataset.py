#!/usr/bin/env python3
"""
Extract Teacher Dataset for LoRA Fine-tuning
============================================

Extracts data from a specified HRA experiment and prepares JSONL files
for teacher-student fine-tuning.

Defaults preserve backward compatibility with Experiment 002
(HRA-EXP-V2 / HRA-EVAL-V2, 90 records). Pass --experiment-code,
--dataset-code and --expected-records to target another experiment
such as Experiment 003 (HRA-EXP-V3 / HRA-EVAL-V3, 123 records).

Teacher: Judge (GPT-4.1)
Student: Qwen2.5-1.5B-Instruct
System Prompt: Production Prompt A
"""

import argparse
import json
import os
import psycopg2
from typing import Dict, List, Any
from collections import defaultdict

# Database connection defaults
DB_CONFIG = {
    'host': 'localhost',
    'database': 'hr_assistant',
    'user': 'hr_user',
    'password': 'PGres3hfpf2100'
}

# Experiment code default (Experiment 002 for backward compatibility)
EXPERIMENT_CODE = 'HRA-EXP-V2'

# Output files
OUTPUT_DIR = 'data'
TRAIN_FILE = os.path.join(OUTPUT_DIR, 'train.jsonl')
VALIDATION_FILE = os.path.join(OUTPUT_DIR, 'validation.jsonl')
TEST_FILE = os.path.join(OUTPUT_DIR, 'test.jsonl')

# Stratified split defaults for Experiment 002 (90 records, 10 candidates per group)
TRAIN_PER_GROUP = 24
VALIDATION_PER_GROUP = 3
TEST_PER_GROUP = 3

# Hard-negative holdout candidates per experiment.
# These case_codes are excluded from train/validation/test and written to a separate holdout file.
HOLDOUT_CANDIDATES = {
    'HRA-EXP-V3': [
        'HRA-EVAL-V2-000110',
        'HRA-EVAL-V2-000111',
    ],
    'HRA-EXP-V4': [
        'HRA-EVAL-V2-000110',
        'HRA-EVAL-V2-000111',
    ]
}

# Per-experiment manual split maps.
# V2 test set is preserved exactly. Remaining V2 candidates plus new candidates
# are split train/validation deterministically within each case_type group.
SPLIT_CONFIG = {
    'HRA-EXP-V3': {
        'test_candidates': [
            'HRA-EVAL-V2-000010',
            'HRA-EVAL-V2-000020',
            'HRA-EVAL-V2-000030',
        ],
        'train_per_group': {
            'obvious_match': 8,
            'obvious_no_match': 12,
            'borderline': 11,
        },
        'validation_per_group': {
            'obvious_match': 1,
            'obvious_no_match': 2,
            'borderline': 2,
        },
    },
    'HRA-EXP-V4': {
        'test_candidates': [
            'HRA-EVAL-V2-000010',
            'HRA-EVAL-V2-000020',
            'HRA-EVAL-V2-000030',
            'HRA-EVAL-V2-000211',
            'HRA-EVAL-V2-000212',
        ],
        'train_per_group': {
            'obvious_match': 13,
            'borderline': 14,
            'obvious_no_match': 11,
        },
        'validation_per_group': {
            'obvious_match': 3,
            'borderline': 3,
            'obvious_no_match': 3,
        },
    }
}

# Random seed for reproducibility
RANDOM_SEED = 42


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description='Extract teacher dataset JSONL from a prompt evaluation experiment.'
    )
    parser.add_argument(
        '--experiment-code',
        type=str,
        default=EXPERIMENT_CODE,
        help='Experiment code in eval_prompt_experiments (default: HRA-EXP-V2)'
    )
    parser.add_argument(
        '--dataset-code',
        type=str,
        default=None,
        help='Dataset code in eval_prompt_datasets (default: derived from experiment code)'
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        default=OUTPUT_DIR,
        help='Directory for train.jsonl, validation.jsonl, test.jsonl (default: data)'
    )
    parser.add_argument(
        '--report-path',
        type=str,
        default='reports/teacher_dataset_report.md',
        help='Path for generated markdown report (default: reports/teacher_dataset_report.md)'
    )
    parser.add_argument(
        '--expected-records',
        type=int,
        default=None,
        help='Expected total number of case-vacancy records (default: 90 for V2, 123 for V3)'
    )
    return parser.parse_args()


def derive_dataset_code(experiment_code: str) -> str:
    """Derive dataset code from experiment code, e.g. HRA-EXP-V2 -> HRA-EVAL-V2."""
    if experiment_code.startswith('HRA-EXP-'):
        return experiment_code.replace('HRA-EXP-', 'HRA-EVAL-')
    return experiment_code


def get_prompt_a(conn, experiment_code: str) -> str:
    """Get production Prompt A from experiment."""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT prompt_a_text
        FROM eval_prompt_experiments
        WHERE experiment_code = %s;
    """, (experiment_code,))

    result = cursor.fetchone()
    cursor.close()

    if not result:
        raise ValueError(f"Experiment {experiment_code} not found")

    return result[0]


def extract_data(conn, experiment_code: str, dataset_code: str, prompt_a: str) -> List[Dict[str, Any]]:
    """Extract all case-vacancy pairs from experiment."""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT
            e.experiment_code,
            d.dataset_code,
            c.case_code,
            c.case_type,
            c.candidate_json,
            pcv.vacancy_json,
            pcv.reference_score,
            pcv.reference_decision,
            pcv.reference_reason,
            pcv.reference_role_score,
            pcv.reference_skills_score,
            pcv.reference_experience_score,
            pcv.reference_conditions_score
        FROM eval_prompt_case_vacancies pcv
        JOIN eval_prompt_cases c ON pcv.case_id = c.id
        JOIN eval_prompt_datasets d ON c.dataset_id = d.id
        JOIN eval_prompt_experiments e ON d.id = e.dataset_id
        WHERE e.experiment_code = %s
          AND d.dataset_code = %s
        ORDER BY c.case_code, pcv.vacancy_json->>'title';
    """, (experiment_code, dataset_code))

    rows = cursor.fetchall()
    cursor.close()

    records = []
    for row in rows:
        (
            experiment_code,
            dataset_code,
            case_code,
            case_type,
            candidate_json,
            vacancy_json,
            reference_score,
            reference_decision,
            reference_reason,
            reference_role_score,
            reference_skills_score,
            reference_experience_score,
            reference_conditions_score
        ) = row

        # Format user message
        user_message = format_user_message(candidate_json, vacancy_json)

        # Format assistant message
        assistant_message = format_assistant_message(
            reference_role_score,
            reference_skills_score,
            reference_experience_score,
            reference_conditions_score,
            reference_score,
            reference_decision,
            reference_reason
        )

        # Create record
        record = {
            'messages': [
                {'role': 'system', 'content': prompt_a},
                {'role': 'user', 'content': user_message},
                {'role': 'assistant', 'content': assistant_message}
            ],
            'metadata': {
                'experiment_code': experiment_code,
                'dataset_code': dataset_code,
                'case_code': case_code,
                'case_type': case_type,
                'vacancy_title': vacancy_json.get('title', ''),
                'reference_score': float(reference_score) if reference_score else None,
                'reference_decision': reference_decision
            }
        }

        records.append(record)

    return records


def format_user_message(candidate_json: Dict, vacancy_json: Dict) -> str:
    """Format user message with candidate and vacancy."""

    # Format candidate
    candidate_text = "Резюме\n\n"
    candidate_text += f"ФИО: {candidate_json.get('full_name', 'Не указано')}\n"
    candidate_text += f"Должность: {candidate_json.get('desired_position', candidate_json.get('position', 'Не указано'))}\n"
    candidate_text += f"Город: {candidate_json.get('city', 'Не указано')}\n"
    candidate_text += f"Опыт: {candidate_json.get('experience_years', 'Не указано')} лет\n"
    candidate_text += f"Зарплатные ожидания: {candidate_json.get('salary_expectation', 'Не указано')}\n"

    # Skills
    skills = candidate_json.get('skills', [])
    if skills:
        candidate_text += f"Навыки: {', '.join(str(s) for s in skills)}\n"

    # Summary
    summary = candidate_json.get('candidate_summary', candidate_json.get('summary', ''))
    if summary:
        candidate_text += f"\nSummary: {summary}\n"

    # Format vacancy
    vacancy_text = "Вакансия\n\n"
    vacancy_text += f"Должность: {vacancy_json.get('title', 'Не указано')}\n"
    vacancy_text += f"Зарплата: {vacancy_json.get('salary_min', 'Не указано')}-{vacancy_json.get('salary_max', 'Не указано')}\n"

    # Description
    description = vacancy_json.get('description', '')
    if description:
        vacancy_text += f"Описание: {description}\n"

    # Requirements
    requirements = vacancy_json.get('requirements', [])
    if requirements:
        if isinstance(requirements, list):
            vacancy_text += f"Требования: {', '.join(str(r) for r in requirements)}\n"
        else:
            vacancy_text += f"Требования: {requirements}\n"

    # Combine
    return candidate_text + "\n" + vacancy_text


def format_assistant_message(
    role_score: float,
    skills_score: float,
    experience_score: float,
    conditions_score: float,
    total_score: float,
    decision: str,
    reason: str
) -> str:
    """Format assistant message with Judge scores."""

    response = {
        'role_score': float(role_score) if role_score else 0,
        'skills_score': float(skills_score) if skills_score else 0,
        'experience_score': float(experience_score) if experience_score else 0,
        'conditions_score': float(conditions_score) if conditions_score else 0,
        'score': float(total_score) if total_score else 0,
        'decision': decision if decision else 'no_match',
        'reason': reason if reason else ''
    }

    return json.dumps(response, ensure_ascii=False, indent=2)


def stratified_split(
    records: List[Dict[str, Any]],
    experiment_code: str,
    holdout_candidates: List[str]
) -> tuple:
    """Split records into train/validation/test with stratification.

    For Experiment 002 the default 24/3/3 per group is used.
    For Experiment 003 a deterministic proportional split is used:
    - V2 test set is preserved exactly;
    - configured holdout candidates are excluded from train/val/test;
    - remaining candidates are split train/validation within each case_type group.
    """

    # Separate holdout records
    holdout_records = [r for r in records if r['metadata']['case_code'] in holdout_candidates]
    active_records = [r for r in records if r['metadata']['case_code'] not in holdout_candidates]

    # Group active records by case_type
    groups = defaultdict(list)
    for record in active_records:
        case_type = record['metadata']['case_type']
        groups[case_type].append(record)

    # Use manual split config when available (Experiment 003)
    split_config = SPLIT_CONFIG.get(experiment_code)
    if split_config:
        test_candidates = set(split_config['test_candidates'])
        train_per_group = split_config['train_per_group']
        validation_per_group = split_config['validation_per_group']

        train_records = []
        validation_records = []
        test_records = []

        for case_type, group_records in groups.items():
            # Sort by case_code for reproducibility
            group_records.sort(key=lambda x: x['metadata']['case_code'])

            # Deduplicate by case_code: group_records are per candidate-vacancy pair
            unique_candidates = {}
            for r in group_records:
                code = r['metadata']['case_code']
                if code not in unique_candidates:
                    unique_candidates[code] = []
                unique_candidates[code].append(r)

            test_codes_in_group = [code for code in unique_candidates if code in test_candidates]
            train_val_codes = [code for code in unique_candidates if code not in test_candidates]

            for code in test_codes_in_group:
                test_records.extend(unique_candidates[code])

            n_train = train_per_group[case_type]
            n_val = validation_per_group[case_type]

            if len(train_val_codes) != n_train + n_val:
                raise ValueError(
                    f"Group {case_type}: expected {n_train + n_val} train+val candidates, "
                    f"got {len(train_val_codes)}"
                )

            for code in train_val_codes[:n_train]:
                train_records.extend(unique_candidates[code])
            for code in train_val_codes[n_train:n_train + n_val]:
                validation_records.extend(unique_candidates[code])

        return train_records, validation_records, test_records, holdout_records

    # Default Experiment 002 behaviour
    train_records = []
    validation_records = []
    test_records = []

    for case_type, group_records in groups.items():
        if len(group_records) != TRAIN_PER_GROUP + VALIDATION_PER_GROUP + TEST_PER_GROUP:
            raise ValueError(
                f"Group {case_type} has {len(group_records)} records, "
                f"expected {TRAIN_PER_GROUP + VALIDATION_PER_GROUP + TEST_PER_GROUP}"
            )

        group_records.sort(key=lambda x: x['metadata']['case_code'])
        train_records.extend(group_records[:TRAIN_PER_GROUP])
        validation_records.extend(group_records[TRAIN_PER_GROUP:TRAIN_PER_GROUP + VALIDATION_PER_GROUP])
        test_records.extend(group_records[TRAIN_PER_GROUP + VALIDATION_PER_GROUP:])

    return train_records, validation_records, test_records, []


def validate_records(records: List[Dict[str, Any]], borderline_cases: List[str]) -> None:
    """Validate records before writing."""

    # Check for NULL values
    for i, record in enumerate(records):
        if not record['messages'][0]['content']:
            raise ValueError(f"Record {i}: system message is empty")
        if not record['messages'][1]['content']:
            raise ValueError(f"Record {i}: user message is empty")
        if not record['messages'][2]['content']:
            raise ValueError(f"Record {i}: assistant message is empty")

        # Check assistant JSON
        try:
            assistant_data = json.loads(record['messages'][2]['content'])
            if 'score' not in assistant_data:
                raise ValueError(f"Record {i}: assistant missing 'score'")
            if 'decision' not in assistant_data:
                raise ValueError(f"Record {i}: assistant missing 'decision'")
        except json.JSONDecodeError as e:
            raise ValueError(f"Record {i}: assistant is not valid JSON: {e}")

    # Check borderline cases presence
    case_codes = [r['metadata']['case_code'] for r in records]
    for case_code in borderline_cases:
        if case_code not in case_codes:
            raise ValueError(f"Borderline case {case_code} not found in dataset")


def write_jsonl(records: List[Dict[str, Any]], filepath: str) -> None:
    """Write records to JSONL file."""
    with open(filepath, 'w', encoding='utf-8') as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False) + '\n')


def generate_report(
    train_records: List[Dict[str, Any]],
    validation_records: List[Dict[str, Any]],
    test_records: List[Dict[str, Any]],
    holdout_records: List[Dict[str, Any]],
    prompt_a: str,
    borderline_cases: List[Dict[str, Any]],
    experiment_code: str,
    dataset_code: str
) -> str:
    """Generate report."""

    total_records = len(train_records) + len(validation_records) + len(test_records)
    if holdout_records:
        total_records += len(holdout_records)

    report = []
    report.append("# Teacher Dataset Report\n")
    report.append(f"**Date:** 2026-06-28\n")
    report.append(f"**Experiment:** {experiment_code}\n")
    report.append(f"**Dataset:** {dataset_code}\n\n")

    report.append("## Summary\n\n")
    report.append(f"- **Total records:** {total_records}\n")
    report.append(f"- **Train:** {len(train_records)}\n")
    report.append(f"- **Validation:** {len(validation_records)}\n")
    report.append(f"- **Test:** {len(test_records)}\n")
    if holdout_records:
        report.append(f"- **Hard Negative Holdout:** {len(holdout_records)}\n")
    report.append("\n")

    report.append("## Distribution by Groups\n\n")

    # Count by group for each split
    split_lists = [('Train', train_records), ('Validation', validation_records), ('Test', test_records)]
    if holdout_records:
        split_lists.append(('Hard Negative Holdout', holdout_records))
    for split_name, split_records in split_lists:
        report.append(f"### {split_name}\n\n")
        groups = defaultdict(int)
        for record in split_records:
            groups[record['metadata']['case_type']] += 1

        for group_name in ['obvious_match', 'borderline', 'obvious_no_match']:
            report.append(f"- **{group_name}:** {groups[group_name]}\n")
        report.append("\n")

    report.append("## Case Codes by Split\n\n")

    # Train case codes
    report.append("### Train\n\n")
    train_codes = sorted({r['metadata']['case_code'] for r in train_records})
    report.append(f"```\n{', '.join(train_codes)}\n```\n\n")

    # Validation case codes
    report.append("### Validation\n\n")
    validation_codes = sorted({r['metadata']['case_code'] for r in validation_records})
    report.append(f"```\n{', '.join(validation_codes)}\n```\n\n")

    # Test case codes
    report.append("### Test\n\n")
    test_codes = sorted({r['metadata']['case_code'] for r in test_records})
    report.append(f"```\n{', '.join(test_codes)}\n```\n\n")

    # Holdout case codes
    if holdout_records:
        report.append("### Hard Negative Holdout\n\n")
        holdout_codes = sorted({r['metadata']['case_code'] for r in holdout_records})
        report.append(f"```\n{', '.join(holdout_codes)}\n```\n\n")

    # Borderline cases
    report.append("## Borderline Cases (score >= 60, decision = no_match)\n\n")
    for case in borderline_cases:
        report.append(f"- **{case['case_code']}**\n")
        report.append(f"  - Vacancy: {case['vacancy_title']}\n")
        report.append(f"  - Score: {case['score']}\n")
        report.append(f"  - Decision: {case['decision']}\n\n")

    report.append("## Confirmations\n\n")
    report.append(f"- ✅ All {total_records} records present\n")
    report.append(f"- ✅ No NULL values\n")
    report.append(f"- ✅ Assistant messages fully formed\n")
    report.append(f"- ✅ System messages filled (production Prompt A)\n")
    report.append(f"- ✅ User messages filled (candidate + vacancy)\n")
    report.append(f"- ✅ All {len(borderline_cases)} borderline cases present in dataset\n")
    report.append(f"- ✅ Using production Prompt A (not Prompt B, not Judge Prompt)\n")
    report.append(f"- ✅ Using Judge (GPT-4.1) as Teacher\n\n")

    report.append("## System Prompt (Production Prompt A)\n\n")
    report.append(f"```\n{prompt_a}\n```\n\n")

    report.append("## Assistant Message Format\n\n")
    report.append("```json\n")
    report.append("{\n")
    report.append("  \"role_score\": 0-30,\n")
    report.append("  \"skills_score\": 0-35,\n")
    report.append("  \"experience_score\": 0-20,\n")
    report.append("  \"conditions_score\": 0-15,\n")
    report.append("  \"score\": 0-100,\n")
    report.append("  \"decision\": \"match\" | \"no_match\",\n")
    report.append("  \"reason\": \"...\"\n")
    report.append("}\n")
    report.append("```\n")

    return ''.join(report)


def main():
    """Main entry point."""
    args = parse_args()

    experiment_code = args.experiment_code
    dataset_code = args.dataset_code or derive_dataset_code(experiment_code)
    output_dir = args.output_dir
    report_path = args.report_path

    # Default expected records: 90 for V2, 123 for V3, 162 for V4
    expected_records = args.expected_records
    if expected_records is None:
        if experiment_code == 'HRA-EXP-V2':
            expected_records = 90
        elif experiment_code == 'HRA-EXP-V3':
            expected_records = 123
        else:
            expected_records = 162

    train_file = os.path.join(output_dir, 'train.jsonl')
    validation_file = os.path.join(output_dir, 'validation.jsonl')
    test_file = os.path.join(output_dir, 'test.jsonl')

    print("Connecting to database...")
    conn = psycopg2.connect(**DB_CONFIG)

    try:
        # Get Prompt A
        print("Getting production Prompt A...")
        prompt_a = get_prompt_a(conn, experiment_code)
        print(f"Prompt A length: {len(prompt_a)} characters")

        # Extract data
        print(f"Extracting data from experiment {experiment_code}...")
        records = extract_data(conn, experiment_code, dataset_code, prompt_a)
        print(f"Extracted {len(records)} records")

        # Borderline cases
        if experiment_code == 'HRA-EXP-V2':
            borderline_cases = [
                {
                    'case_code': 'HRA-EVAL-V2-000007',
                    'vacancy_title': 'Prompt Engineer / AI Automation Specialist',
                    'score': 62,
                    'decision': 'no_match'
                },
                {
                    'case_code': 'HRA-EVAL-V2-000024',
                    'vacancy_title': 'Prompt Engineer / AI Automation Specialist',
                    'score': 64,
                    'decision': 'no_match'
                },
                {
                    'case_code': 'HRA-EVAL-V2-000026',
                    'vacancy_title': 'Системный аналитик',
                    'score': 62,
                    'decision': 'no_match'
                }
            ]
        else:
            borderline_cases = []

        # Validate records
        print("Validating records...")
        validate_records(records, [c['case_code'] for c in borderline_cases])
        print("Validation passed")

        # Check total count
        if len(records) != expected_records:
            raise ValueError(f"Expected {expected_records} records, got {len(records)}")

        # Stratified split
        print("Performing stratified split...")
        holdout_candidates = HOLDOUT_CANDIDATES.get(experiment_code, [])
        train_records, validation_records, test_records, holdout_records = stratified_split(
            records, experiment_code, holdout_candidates
        )
        print(f"Train: {len(train_records)}")
        print(f"Validation: {len(validation_records)}")
        print(f"Test: {len(test_records)}")
        if holdout_records:
            print(f"Hard Negative Holdout: {len(holdout_records)}")

        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        os.makedirs(os.path.dirname(report_path) or '.', exist_ok=True)

        # Write JSONL files
        print("Writing JSONL files...")
        write_jsonl(train_records, train_file)
        write_jsonl(validation_records, validation_file)
        write_jsonl(test_records, test_file)
        if holdout_records:
            holdout_file = os.path.join(output_dir, 'holdout.jsonl')
            write_jsonl(holdout_records, holdout_file)
            print(f"Wrote {holdout_file}")
        print(f"Wrote {train_file}")
        print(f"Wrote {validation_file}")
        print(f"Wrote {test_file}")

        # Generate report
        print("Generating report...")
        report = generate_report(
            train_records,
            validation_records,
            test_records,
            holdout_records,
            prompt_a,
            borderline_cases,
            experiment_code,
            dataset_code
        )
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"Wrote {report_path}")

        print("\n✅ Teacher dataset preparation complete!")
        print(f"   Train: {train_file}")
        print(f"   Validation: {validation_file}")
        print(f"   Test: {test_file}")
        print(f"   Report: {report_path}")

    finally:
        conn.close()


if __name__ == '__main__':
    main()
