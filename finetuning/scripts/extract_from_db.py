#!/usr/bin/env python3
"""
Извлечение датасета из PostgreSQL БД HRA.

Источник: eval_prompt_cases + eval_prompt_case_vacancies
System prompt: Prompt A (production)
Target: Judge (gpt-4.1) scores

Author: HRA Team
Date: 2026-06-28
"""

import json
import os
import random
import sys
from typing import Dict, List, Any, Tuple

import psycopg2
import yaml


def load_config(config_path: str) -> Dict[str, Any]:
    """Загрузка конфигурации эксперимента."""
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def connect_to_db(db_config: Dict[str, str]):
    """Подключение к PostgreSQL."""
    return psycopg2.connect(
        host=db_config.get('host', 'localhost'),
        port=db_config.get('port', 5432),
        database=db_config.get('database', 'hr_assistant'),
        user=db_config.get('user', 'hr_user'),
        password=db_config.get('password', '')
    )


def extract_cases_from_db(conn) -> List[Dict[str, Any]]:
    """
    Извлечение всех кейсов из БД.

    Returns:
        List of case dictionaries with:
        - case_code: str
        - case_type: 'obvious_match' | 'borderline' | 'obvious_no_match'
        - candidate: dict
        - vacancy: dict
        - judge_score: int
        - judge_decision: str
        - judge_reasoning: str
    """
    query = """
    SELECT
        c.case_code,
        c.case_type,
        c.candidate_json,
        v.vacancy_json,
        v.reference_score as judge_score,
        v.reference_decision as judge_decision,
        v.reference_reason as judge_reasoning
    FROM eval_prompt_cases c
    JOIN eval_prompt_case_vacancies v ON v.case_id = c.id
    WHERE c.dataset_id = (
        SELECT id FROM eval_prompt_datasets WHERE dataset_code = 'HRA-EVAL-V1'
    )
    ORDER BY c.case_code, v.vacancy_json->>'title'
    """

    cursor = conn.cursor()
    cursor.execute(query)

    cases = []
    for row in cursor.fetchall():
        case_code, case_type, candidate_json, vacancy_json, judge_score, judge_decision, judge_reasoning = row

        cases.append({
            'case_code': case_code,
            'case_type': case_type,
            'candidate': candidate_json,
            'vacancy': vacancy_json,
            'judge_score': int(judge_score) if judge_score else None,
            'judge_decision': judge_decision,
            'judge_reasoning': judge_reasoning,
        })

    cursor.close()
    return cases


def extract_scores_from_reasoning(reasoning: str) -> Dict[str, int]:
    """
    Извлечение подоценок из Judge reasoning.

    Judge format variations:
    1. "Должность: ... (12/30)" - явное указание критерия
    2. "(12/30), (13/35), (18/20), (15/15)" - перечисление
    3. "... что полностью совпадает с вакансией (30/30)" - в тексте

    Strategy:
    1. Find all (X/30), (X/35), (X/20), (X/15) patterns
    2. Try to match by context (Должность, Навыки, etc.)
    3. Fallback: assign by denominator (30→role, 35→skills, 20→experience, 15→conditions)
    """
    import re

    scores = {}

    # Try explicit keyword matching first
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

    # Fallback: find all (X/Y) patterns and assign by denominator
    if len(scores) < 4:
        all_matches = re.findall(r'\((\d{1,2})/(\d{2})\)', reasoning)

        denominator_map = {
            '30': 'role_score',
            '35': 'skills_score',
            '20': 'experience_score',
            '15': 'conditions_score',
        }

        for score_val, denom in all_matches:
            score_name = denominator_map.get(denom)
            if score_name and score_name not in scores:
                scores[score_name] = int(score_val)

    return scores


def validate_judge_scores(case: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Валидация Judge scores.

    Если детальные оценки не найдены в reasoning, вычисляем пропорционально.

    Returns:
        (is_valid, error_message)
    """
    if case['judge_score'] is None:
        return False, "No judge_score"

    if case['judge_decision'] is None:
        return False, "No judge_decision"

    if not case['judge_reasoning']:
        return False, "No judge_reasoning"

    # Извлекаем подоценки
    scores = extract_scores_from_reasoning(case['judge_reasoning'])

    # Если не все оценки найдены, вычисляем пропорционально
    if len(scores) < 4:
        total_score = case['judge_score']

        # Пропорциональное распределение
        # Веса: role=30%, skills=35%, experience=20%, conditions=15%
        if total_score >= 70:  # Высокий score - хорошие подоценки
            base_scores = {
                'role_score': min(30, int(total_score * 0.30)),
                'skills_score': min(35, int(total_score * 0.35)),
                'experience_score': min(20, int(total_score * 0.20)),
                'conditions_score': min(15, int(total_score * 0.15)),
            }
        elif total_score >= 50:  # Средний score - умеренные подоценки
            base_scores = {
                'role_score': int(total_score * 0.30),
                'skills_score': int(total_score * 0.35),
                'experience_score': int(total_score * 0.20),
                'conditions_score': int(total_score * 0.15),
            }
        else:  # Низкий score - низкие подоценки
            base_scores = {
                'role_score': max(0, int(total_score * 0.25)),
                'skills_score': max(0, int(total_score * 0.35)),
                'experience_score': max(0, int(total_score * 0.20)),
                'conditions_score': max(0, int(total_score * 0.20)),
            }

        # Заменяем найденные оценки
        for key in ['role_score', 'skills_score', 'experience_score', 'conditions_score']:
            if key not in scores and key in base_scores:
                scores[key] = base_scores[key]

    # Проверяем сумму (с допуском ±5)
    total = sum(scores.values())
    if abs(total - case['judge_score']) > 5:
        # Корректируем наиболее вариабельную оценку (skills)
        scores['skills_score'] = max(0, min(35, scores['skills_score'] + (case['judge_score'] - total)))
        total = sum(scores.values())

    case['judge_scores'] = scores
    return True, ""


def case_to_messages(case: Dict[str, Any], system_prompt: str) -> Dict[str, Any]:
    """
    Конвертация кейса в messages формат.

    System: Prompt A (production)
    User: Candidate + Vacancy
    Assistant: Judge scores as JSON
    """
    candidate = case['candidate']
    vacancy = case['vacancy']
    judge_scores = case.get('judge_scores', {})

    # User message
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

    # Assistant message (JSON)
    assistant_content = json.dumps({
        'role_score': judge_scores.get('role_score', 0),
        'skills_score': judge_scores.get('skills_score', 0),
        'experience_score': judge_scores.get('experience_score', 0),
        'conditions_score': judge_scores.get('conditions_score', 0),
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
    Стратифицированное разбиение на train/val/test.

    По 24/3/3 кейса в каждой группе (obvious_match, borderline, obvious_no_match).
    """
    random.seed(seed)

    groups = {
        'obvious_match': [],
        'borderline': [],
        'obvious_no_match': []
    }

    # Группировка кейсов
    for case in cases:
        group_name = case.get('case_type', 'borderline')
        if group_name in groups:
            groups[group_name].append(case)

    # Валидация размеров групп
    for group_name, group_cases in groups.items():
        expected = 30
        actual = len(group_cases) // 3  # Каждый кандидат × 3 вакансии
        print(f"  {group_name}: {len(group_cases)} пар ({actual} кандидатов)")

    train_cases = []
    val_cases = []
    test_cases = []

    for group_name, group_cases in groups.items():
        # Перемешивание внутри группы
        random.shuffle(group_cases)

        # Разбиение
        train_cases.extend(group_cases[:train_per_group])
        val_cases.extend(group_cases[train_per_group:train_per_group + val_per_group])
        test_cases.extend(group_cases[train_per_group + val_per_group:train_per_group + val_per_group + test_per_group])

    return train_cases, val_cases, test_cases


def save_jsonl(cases: List[Dict[str, Any]], output_path: str) -> None:
    """Сохранение кейсов в JSONL файл."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        for case in cases:
            f.write(json.dumps(case, ensure_ascii=False) + '\n')


def main():
    """Главная функция."""
    parser = argparse.ArgumentParser(
        description="Извлечение датасета из PostgreSQL БД HRA"
    )
    parser.add_argument(
        '--config',
        type=str,
        default='configs/experiment_001.yaml',
        help='Путь к конфигурации эксперимента'
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        default='data',
        help='Выходной каталог для датасета'
    )
    parser.add_argument(
        '--db-host',
        type=str,
        default='localhost',
        help='Хост PostgreSQL'
    )
    parser.add_argument(
        '--db-port',
        type=int,
        default=5432,
        help='Порт PostgreSQL'
    )
    parser.add_argument(
        '--db-name',
        type=str,
        default='hr_assistant',
        help='Имя БД'
    )
    parser.add_argument(
        '--db-user',
        type=str,
        default='hr_user',
        help='Пользователь БД'
    )
    parser.add_argument(
        '--db-password',
        type=str,
        default='PGres3hfpf2100',
        help='Пароль БД'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Валидация без создания файлов'
    )

    args = parser.parse_args()

    print("=" * 60)
    print("Извлечение датасета из БД HRA")
    print("=" * 60)

    # Подключение к БД
    print(f"\nПодключение к БД: {args.db_host}:{args.db_port}/{args.db_name}")
    conn = connect_to_db({
        'host': args.db_host,
        'port': args.db_port,
        'database': args.db_name,
        'user': args.db_user,
        'password': args.db_password,
    })

    # Извлечение кейсов
    print("\nИзвлечение кейсов из БД...")
    cases = extract_cases_from_db(conn)
    print(f"Извлечено {len(cases)} кейсов")

    conn.close()

    # Статистика по типам
    case_types = {}
    for case in cases:
        ct = case.get('case_type', 'unknown')
        case_types[ct] = case_types.get(ct, 0) + 1

    print("\nРаспределение по типам:")
    for ct, count in sorted(case_types.items()):
        print(f"  {ct}: {count}")

    # Валидация Judge scores
    print("\nВалидация Judge scores...")
    valid_cases = []
    invalid_cases = []

    for case in cases:
        is_valid, error = validate_judge_scores(case)
        if is_valid:
            valid_cases.append(case)
        else:
            invalid_cases.append((case, error))

    print(f"  Валидных: {len(valid_cases)}")
    print(f"  Невалидных: {len(invalid_cases)}")

    if invalid_cases:
        print("\nНевалидные кейсы:")
        for case, error in invalid_cases[:5]:
            print(f"  {case['case_code']}: {error}")

    if args.dry_run:
        print("\n[DRY RUN] Валидация завершена. Выход.")
        return 0

    # Стратифицированное разбиение
    print("\nСтратификация датасета...")
    train_cases, val_cases, test_cases = stratify_split(valid_cases)

    print(f"\nРазбиение:")
    print(f"  Train: {len(train_cases)} кейсов")
    print(f"  Validation: {len(val_cases)} кейсов")
    print(f"  Test: {len(test_cases)} кейсов")

    # System prompt: Prompt A (production)
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

    # Конвертация в messages формат
    print("\nКонвертация в messages формат...")
    train_data = [case_to_messages(c, system_prompt) for c in train_cases]
    val_data = [case_to_messages(c, system_prompt) for c in val_cases]
    test_data = [case_to_messages(c, system_prompt) for c in test_cases]

    # Сохранение
    print(f"\nСохранение в {args.output_dir}/...")
    save_jsonl(train_data, os.path.join(args.output_dir, 'train.jsonl'))
    save_jsonl(val_data, os.path.join(args.output_dir, 'validation.jsonl'))
    save_jsonl(test_data, os.path.join(args.output_dir, 'test.jsonl'))

    print(f"\n✅ Датасет успешно создан!")
    print(f"   - train.jsonl: {len(train_data)} кейсов")
    print(f"   - validation.jsonl: {len(val_data)} кейсов")
    print(f"   - test.jsonl: {len(test_data)} кейсов")

    if invalid_cases:
        print(f"\n⚠️  {len(invalid_cases)} кейсов требуют ручной проверки (отсутствуют Judge scores)")

    return 0


if __name__ == '__main__':
    import argparse
    sys.exit(main())