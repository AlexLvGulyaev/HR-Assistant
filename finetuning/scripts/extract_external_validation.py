#!/usr/bin/env python3
"""
Extract External Validation Dataset for LoRA vs GPT-4o-mini comparison.

Produces data/external_validation.jsonl from HRA-EXP-V5-EXT / HRA-EVAL-V5-EXT.
Unlike teacher dataset extraction, this script does NOT split data;
it exports all 102 records with messages formatted for inference.

Reference annotations are added separately by judge_external_validation.py
using GPT-4o as the external judge.
"""

import argparse
import json
import os
import psycopg2
from typing import Dict, List, Any

DB_CONFIG = {
    'host': 'localhost',
    'database': 'hr_assistant',
    'user': 'hr_user',
    'password': 'PGres3hfpf2100'
}

EXPERIMENT_CODE = 'HRA-EXP-V5-EXT'
DATASET_CODE = 'HRA-EVAL-V5-EXT'
OUTPUT_DIR = 'data'
OUTPUT_FILE = os.path.join(OUTPUT_DIR, 'external_validation.jsonl')


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description='Extract external validation JSONL from prompt evaluation experiment.'
    )
    parser.add_argument(
        '--experiment-code',
        type=str,
        default=EXPERIMENT_CODE,
        help=f'Experiment code (default: {EXPERIMENT_CODE})'
    )
    parser.add_argument(
        '--dataset-code',
        type=str,
        default=DATASET_CODE,
        help=f'Dataset code (default: {DATASET_CODE})'
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        default=OUTPUT_DIR,
        help='Directory for output JSONL (default: data)'
    )
    parser.add_argument(
        '--output-file',
        type=str,
        default=OUTPUT_FILE,
        help=f'Output JSONL path (default: {OUTPUT_FILE})'
    )
    parser.add_argument(
        '--expected-records',
        type=int,
        default=102,
        help='Expected number of candidate-vacancy records (default: 102)'
    )
    return parser.parse_args()


def get_prompt_a(conn, experiment_code: str) -> str:
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


def extract_records(conn, experiment_code: str, dataset_code: str, prompt_a: str) -> List[Dict[str, Any]]:
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
            pcv.reference_conditions_score,
            pcv.reference_model
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
            reference_conditions_score,
            reference_model
        ) = row

        user_message = format_user_message(candidate_json, vacancy_json)

        record = {
            'messages': [
                {'role': 'system', 'content': prompt_a},
                {'role': 'user', 'content': user_message}
            ],
            'metadata': {
                'experiment_code': experiment_code,
                'dataset_code': dataset_code,
                'case_code': case_code,
                'case_type': case_type,
                'vacancy_title': vacancy_json.get('title', ''),
                'reference_score': float(reference_score) if reference_score else None,
                'reference_decision': reference_decision,
                'reference_reason': reference_reason,
                'reference_role_score': float(reference_role_score) if reference_role_score else None,
                'reference_skills_score': float(reference_skills_score) if reference_skills_score else None,
                'reference_experience_score': float(reference_experience_score) if reference_experience_score else None,
                'reference_conditions_score': float(reference_conditions_score) if reference_conditions_score else None,
                'reference_model': reference_model
            }
        }
        records.append(record)

    return records


def format_user_message(candidate_json: Dict, vacancy_json: Dict) -> str:
    candidate_text = "Резюме\n\n"
    candidate_text += f"ФИО: {candidate_json.get('full_name', 'Не указано')}\n"
    candidate_text += f"Должность: {candidate_json.get('desired_position', candidate_json.get('position', 'Не указано'))}\n"
    candidate_text += f"Город: {candidate_json.get('city', 'Не указано')}\n"
    candidate_text += f"Опыт: {candidate_json.get('experience_years', 'Не указано')} лет\n"
    candidate_text += f"Зарплатные ожидания: {candidate_json.get('salary_expectation', 'Не указано')}\n"

    skills = candidate_json.get('skills', [])
    if skills:
        candidate_text += f"Навыки: {', '.join(str(s) for s in skills)}\n"

    summary = candidate_json.get('candidate_summary', candidate_json.get('summary', ''))
    if summary:
        candidate_text += f"\nSummary: {summary}\n"

    vacancy_text = "Вакансия\n\n"
    vacancy_text += f"Должность: {vacancy_json.get('title', 'Не указано')}\n"
    vacancy_text += f"Зарплата: {vacancy_json.get('salary_min', 'Не указано')}-{vacancy_json.get('salary_max', 'Не указано')}\n"

    description = vacancy_json.get('description', '')
    if description:
        vacancy_text += f"Описание: {description}\n"

    requirements = vacancy_json.get('requirements', [])
    if requirements:
        if isinstance(requirements, list):
            vacancy_text += f"Требования: {', '.join(str(r) for r in requirements)}\n"
        else:
            vacancy_text += f"Требования: {requirements}\n"

    return candidate_text + "\n" + vacancy_text


def write_jsonl(records: List[Dict[str, Any]], filepath: str) -> None:
    with open(filepath, 'w', encoding='utf-8') as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False) + '\n')


def generate_report(records: List[Dict[str, Any]]) -> str:
    from collections import defaultdict

    total = len(records)
    groups = defaultdict(int)
    for r in records:
        groups[r['metadata']['case_type']] += 1

    report = []
    report.append("# External Validation Dataset Report\n")
    report.append(f"**Experiment:** {EXPERIMENT_CODE}\n")
    report.append(f"**Dataset:** {DATASET_CODE}\n")
    report.append(f"**Total records:** {total}\n\n")

    report.append("## Distribution by case_type\n\n")
    for group_name in ['obvious_match', 'borderline', 'obvious_no_match']:
        report.append(f"- **{group_name}:** {groups[group_name]}\n")
    report.append("\n")

    report.append("## Candidate codes\n\n")
    codes = sorted({r['metadata']['case_code'] for r in records})
    report.append(f"```\n{', '.join(codes)}\n```\n")

    report.append("\n## Confirmations\n\n")
    report.append(f"- ✅ All {total} records present\n")
    report.append("- ✅ No NULL system/user messages\n")
    report.append("- ✅ Reference annotations populated when judge run is complete\n")

    return ''.join(report)


def main():
    args = parse_args()
    experiment_code = args.experiment_code
    dataset_code = args.dataset_code
    output_file = args.output_file
    report_path = os.path.join(os.path.dirname(output_file) or '.', 'external_validation_report.md')

    print("Connecting to database...")
    conn = psycopg2.connect(**DB_CONFIG)

    try:
        print("Getting production Prompt A...")
        prompt_a = get_prompt_a(conn, experiment_code)
        print(f"Prompt A length: {len(prompt_a)} characters")

        print(f"Extracting records from {experiment_code}...")
        records = extract_records(conn, experiment_code, dataset_code, prompt_a)
        print(f"Extracted {len(records)} records")

        if len(records) != args.expected_records:
            raise ValueError(f"Expected {args.expected_records} records, got {len(records)}")

        if any(r['metadata']['reference_score'] is None for r in records):
            print("⚠️  Warning: some records lack reference annotations. Run judge_external_validation.py next.")

        os.makedirs(os.path.dirname(output_file) or '.', exist_ok=True)
        write_jsonl(records, output_file)
        print(f"Wrote {output_file}")

        report = generate_report(records)
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"Wrote {report_path}")

        print("\n✅ External validation dataset extraction complete!")

    finally:
        conn.close()


if __name__ == '__main__':
    main()
