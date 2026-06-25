# Воспроизводимость эксперимента

**Пошаговая инструкция по проведению A/B-тестирования промптов**

---

## Обзор

Документ описывает полный процесс проведения эксперимента Prompt Evaluation, от развёртывания до анализа результатов.

---

## Предварительные требования

### Программное обеспечение

| Компонент | Версия | Назначение |
|-----------|--------|------------|
| PostgreSQL | 16+ | База данных |
| n8n | Latest | Workflow automation |
| OpenAI API | — | LLM вызовы |

### Доступы

| Ресурс | Назначение |
|--------|------------|
| PostgreSQL | Хранение данных эксперимента |
| OpenAI API | Вызовы Judge, Prompt A, Prompt B |
| n8n | Запуск workflow |

---

## Шаг 1: Создание схемы БД

### SQL-скрипт

```bash
PGPASSWORD="your_password" psql -h localhost -U hr_user -d hr_assistant \
  -f database/02-prompt-evaluation.sql
```

### Создаваемые таблицы

| Таблица | Назначение |
|---------|------------|
| `eval_prompt_datasets` | Датасеты |
| `eval_prompt_experiments` | Эксперименты |
| `eval_prompt_cases` | Кандидаты |
| `eval_prompt_case_vacancies` | Пары кандидат-вакансия |
| `eval_prompt_runs` | Запуски |
| `eval_prompt_results` | Результаты |

### Проверка

```sql
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
  AND table_name LIKE 'eval_prompt%';
```

Ожидаемый результат: 6 таблиц.

---

## Шаг 2: Загрузка датасета

### SQL-скрипт

```bash
PGPASSWORD="your_password" psql -h localhost -U hr_user -d hr_assistant \
  -f database/03-seed-eval-dataset-v1.sql
```

### Проверка

```sql
-- Проверка количества кейсов
SELECT COUNT(*) FROM eval_prompt_cases;
-- Ожидается: 30

-- Проверка количества пар
SELECT COUNT(*) FROM eval_prompt_case_vacancies;
-- Ожидается: 90

-- Проверка распределения по типам
SELECT case_type, COUNT(*) 
FROM eval_prompt_cases 
GROUP BY case_type;
-- Ожидается: 10 obvious_match, 10 obvious_no_match, 10 borderline
```

---

## Шаг 3: Создание эксперимента

### SQL-скрипт

```bash
PGPASSWORD="your_password" psql -h localhost -U hr_user -d hr_assistant \
  -f database/04-create-experiment-v1.sql
```

### Проверка

```sql
SELECT 
    e.experiment_code,
    e.model_a,
    e.model_b,
    e.model_judge,
    e.temperature_a,
    e.temperature_b,
    e.temperature_judge,
    e.primary_metric,
    e.guard_metric,
    e.mde,
    e.status
FROM eval_prompt_experiments e
JOIN eval_prompt_datasets d ON e.dataset_id = d.id
WHERE d.dataset_code = 'HRA-EVAL-V1';
```

Ожидаемый результат:
- experiment_code: HRA-EXP-V1
- model_a: gpt-4o-mini-2024-07-18
- model_b: gpt-4o-mini-2024-07-18
- model_judge: gpt-4.1-2025-04-14
- temperatures: 0
- status: draft

---

## Шаг 4: Импорт workflow

### Действия

1. Открыть n8n
2. Перейти в **Workflows** → **Import from File**
3. Выбрать файл `workflows/HRA Prompt Evaluation Experiment.json`
4. Подтвердить импорт

### Структура workflow

```
Phase 0: Validation
Phase 1: Judge Run
Phase 2: Prompt A Run
Phase 3: Prompt B Run
Phase 4: Calculate Metrics
Phase 5: Generate Report
```

---

## Шаг 5: Настройка credentials

### PostgreSQL

1. В n8n перейти в **Settings** → **Credentials**
2. Создать credential типа **PostgreSQL**
3. Указать:
   - Host: localhost (или ваш сервер)
   - Port: 5432
   - Database: hr_assistant
   - User: hr_user
   - Password: your_password
4. Сохранить credential

### OpenAI

1. В n8n перейти в **Settings** → **Credentials**
2. Создать credential типа **OpenAI**
3. Указать:
   - API Key: your_openai_api_key
4. Сохранить credential

### Привязка к workflow

1. Открыть workflow
2. Для каждого PostgreSQL node:
   - Выбрать созданный credential
3. Для каждого HTTP Request node (OpenAI):
   - Выбрать созданный credential

---

## Шаг 6: Smoke Run

### Цель

Проверить работоспособность workflow на одной паре.

### Создание smoke dataset

```bash
PGPASSWORD="your_password" psql -h localhost -U hr_user -d hr_assistant \
  -f database/05-create-smoke-experiment.sql
```

### Настройка Run Config

В workflow найти node **Run Config** и установить:

```javascript
return [{
  json: {
    experiment_code: 'HRA-EXP-SMOKE',
    dataset_code: 'HRA-EVAL-SMOKE',
    expected_pairs: 1
  }
}];
```

### Запуск

1. Нажать **Execute Workflow**
2. Дождаться завершения
3. Проверить результат

### Ожидаемый результат

- Judge Run: 1 pair processed
- Prompt A Run: 1 result
- Prompt B Run: 1 result
- Metrics calculated
- Report generated

### Проверка в БД

```sql
-- Проверка Judge Run
SELECT run_type, status, COUNT(*) 
FROM eval_prompt_runs r
JOIN eval_prompt_experiments e ON r.experiment_id = e.id
WHERE e.experiment_code = 'HRA-EXP-SMOKE'
GROUP BY run_type, status;

-- Ожидается: 1 judge run, status: completed

-- Проверка результатов
SELECT run_type, COUNT(*) 
FROM eval_prompt_results r
JOIN eval_prompt_runs run ON r.run_id = run.id
JOIN eval_prompt_experiments e ON run.experiment_id = e.id
WHERE e.experiment_code = 'HRA-EXP-SMOKE'
GROUP BY run_type;

-- Ожидается: A: 1, B: 1
```

---

## Шаг 7: Full Run

### Сброс окружения (если нужно)

Если уже были запуски HRA-EXP-V1:

```sql
-- Удалить результаты
DELETE FROM eval_prompt_results WHERE run_id IN (
  SELECT id FROM eval_prompt_runs WHERE experiment_id = (
    SELECT id FROM eval_prompt_experiments WHERE experiment_code = 'HRA-EXP-V1'
  )
);

-- Сбросить reference scores
UPDATE eval_prompt_case_vacancies SET
  reference_score = NULL,
  reference_decision = NULL,
  reference_reason = NULL
WHERE case_id IN (
  SELECT id FROM eval_prompt_cases WHERE dataset_id = (
    SELECT id FROM eval_prompt_datasets WHERE dataset_code = 'HRA-EVAL-V1'
  )
);

-- Удалить runs
DELETE FROM eval_prompt_runs WHERE experiment_id = (
  SELECT id FROM eval_prompt_experiments WHERE experiment_code = 'HRA-EXP-V1'
);
```

### Настройка Run Config

В workflow найти node **Run Config** и установить:

```javascript
return [{
  json: {
    experiment_code: 'HRA-EXP-V1',
    dataset_code: 'HRA-EVAL-V1',
    expected_pairs: 90
  }
}];
```

### Запуск

1. Нажать **Execute Workflow**
2. Дождаться завершения (~10-15 минут)
3. Проверить результат

### Ожидаемый результат

- Judge Run: 90 pairs processed (~4 min)
- Prompt A Run: 90 results (~3 min)
- Prompt B Run: 90 results (~3 min)
- Metrics calculated
- Report generated

---

## Шаг 8: Анализ результатов

### Проверка в БД

```sql
-- Статистика runs
SELECT run_type, status, started_at, completed_at
FROM eval_prompt_runs r
JOIN eval_prompt_experiments e ON r.experiment_id = e.id
WHERE e.experiment_code = 'HRA-EXP-V1'
ORDER BY run_type;

-- Ожидается: judge, A, B — все completed

-- Количество результатов
SELECT run_type, COUNT(*) as results
FROM eval_prompt_results r
JOIN eval_prompt_runs run ON r.run_id = run.id
JOIN eval_prompt_experiments e ON run.experiment_id = e.id
WHERE e.experiment_code = 'HRA-EXP-V1'
GROUP BY run_type;

-- Ожидается: A: 90, B: 90
```

### Расчёт метрик

```sql
WITH mae_a AS (
    SELECT AVG(ABS(r.score - cv.reference_score)) AS mae_a
    FROM eval_prompt_results r
    JOIN eval_prompt_case_vacancies cv ON r.case_vacancy_id = cv.id
    JOIN eval_prompt_runs run ON r.run_id = run.id
    JOIN eval_prompt_experiments e ON run.experiment_id = e.id
    WHERE e.experiment_code = 'HRA-EXP-V1' AND run.run_type = 'A'
),
mae_b AS (
    SELECT AVG(ABS(r.score - cv.reference_score)) AS mae_b
    FROM eval_prompt_results r
    JOIN eval_prompt_case_vacancies cv ON r.case_vacancy_id = cv.id
    JOIN eval_prompt_runs run ON r.run_id = run.id
    JOIN eval_prompt_experiments e ON run.experiment_id = e.id
    WHERE e.experiment_code = 'HRA-EXP-V1' AND run.run_type = 'B'
),
latency_a AS (
    SELECT AVG(r.latency_ms) AS latency_a
    FROM eval_prompt_results r
    JOIN eval_prompt_runs run ON r.run_id = run.id
    JOIN eval_prompt_experiments e ON run.experiment_id = e.id
    WHERE e.experiment_code = 'HRA-EXP-V1' AND run.run_type = 'A'
),
latency_b AS (
    SELECT AVG(r.latency_ms) AS latency_b
    FROM eval_prompt_results r
    JOIN eval_prompt_runs run ON r.run_id = run.id
    JOIN eval_prompt_experiments e ON run.experiment_id = e.id
    WHERE e.experiment_code = 'HRA-EXP-V1' AND run.run_type = 'B'
)
SELECT
    ROUND(mae_a.mae_a::NUMERIC, 4) AS mae_a,
    ROUND(mae_b.mae_b::NUMERIC, 4) AS mae_b,
    ROUND(((mae_a.mae_a - mae_b.mae_b) / mae_a.mae_a)::NUMERIC, 4) AS mae_improvement,
    ROUND(latency_a.latency_a::NUMERIC, 2) AS latency_a_ms,
    ROUND(latency_b.latency_b::NUMERIC, 2) AS latency_b_ms,
    ROUND(((latency_b.latency_b - latency_a.latency_a) / latency_a.latency_a)::NUMERIC, 4) AS latency_growth
FROM mae_a, mae_b, latency_a, latency_b;
```

### Интерпретация результатов

| Критерий | Условие | Решение |
|----------|---------|---------|
| MAE Improvement | ≥ 20% | ✅ PASS |
| Latency Growth | ≤ 30% | ✅ PASS |
| **Финальное** | BOTH PASS | ACCEPT |
| **Финальное** | ANY FAIL | REJECT |

---

## Проведение нового эксперимента

### Создание нового датасета (опционально)

```sql
-- Создать новый датасет
INSERT INTO eval_prompt_datasets (dataset_code, name, description, status)
VALUES ('HRA-EVAL-V2', 'Dataset v2', 'Новый датасет', 'active');

-- Добавить кейсы и пары
-- (аналогично 03-seed-eval-dataset-v1.sql)
```

### Создание нового эксперимента

```sql
INSERT INTO eval_prompt_experiments (
    id,
    dataset_id,
    experiment_code,
    prompt_a_text,
    prompt_b_text,  -- НОВЫЙ ПРОМПТ
    judge_prompt_text,
    model_a,
    model_b,  -- ОПЦИОНАЛЬНО: ДРУГАЯ МОДЕЛЬ
    model_judge,
    temperature_a,
    temperature_b,
    temperature_judge,
    primary_metric,
    guard_metric,
    mde,
    status
)
SELECT
    gen_random_uuid(),
    (SELECT id FROM eval_prompt_datasets WHERE dataset_code = 'HRA-EVAL-V1'),
    'HRA-EXP-V2',
    prompt_a_text,  -- SAME as V1
    'НОВЫЙ ПРОМПТ B',
    judge_prompt_text,  -- SAME as V1
    'gpt-4o-mini-2024-07-18',  -- SAME as V1
    'gpt-4o-mini-2024-07-18',  -- или 'gpt-4.1-2025-04-14'
    'gpt-4.1-2025-04-14',  -- SAME as V1
    0, 0, 0,  -- SAME as V1
    'mean_absolute_score_error',
    'latency_ms',
    'MAE improvement >= 20%',
    'draft'
FROM eval_prompt_experiments
WHERE experiment_code = 'HRA-EXP-V1';
```

### Запуск

```javascript
return [{
  json: {
    experiment_code: 'HRA-EXP-V2',
    dataset_code: 'HRA-EVAL-V1',  // или V2
    expected_pairs: 90
  }
}];
```

---

## Сравнение результатов с предыдущим экспериментом

```sql
WITH v1 AS (
    SELECT
        'V1' as version,
        AVG(ABS(r.score - cv.reference_score)) AS mae
    FROM eval_prompt_results r
    JOIN eval_prompt_case_vacancies cv ON r.case_vacancy_id = cv.id
    JOIN eval_prompt_runs run ON r.run_id = run.id
    JOIN eval_prompt_experiments e ON run.experiment_id = e.id
    WHERE e.experiment_code = 'HRA-EXP-V1' AND run.run_type = 'B'
),
v2 AS (
    SELECT
        'V2' as version,
        AVG(ABS(r.score - cv.reference_score)) AS mae
    FROM eval_prompt_results r
    JOIN eval_prompt_case_vacancies cv ON r.case_vacancy_id = cv.id
    JOIN eval_prompt_runs run ON r.run_id = run.id
    JOIN eval_prompt_experiments e ON run.experiment_id = e.id
    WHERE e.experiment_code = 'HRA-EXP-V2' AND run.run_type = 'B'
)
SELECT * FROM v1
UNION ALL
SELECT * FROM v2;
```

---

## Частые проблемы

### Workflow не запускается

1. Проверьте credentials (PostgreSQL, OpenAI)
2. Проверьте connection к БД
3. Проверьте OpenAI API key

### Неверное количество пар

1. Проверьте `expected_pairs` в Run Config
2. Проверьте количество записей в `eval_prompt_case_vacancies`
3. Убедитесь, что dataset_code совпадает

### Ошибки типа данных

1. Проверьте, что temperature — число, не строка
2. Проверьте, что score — число в диапазоне 0-100
3. Проверьте, что latency_ms — целое число

---

*Инструкция по воспроизводимости эксперимента*