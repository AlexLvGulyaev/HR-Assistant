# HR Assistant Database

**Last Updated:** 2026-06-25

---

## Schema Overview

**Database:** PostgreSQL 16

**Schema Files:**
- `schema_hr_assistant.sql` — основная схема БД (боевой контур)
- `02-prompt-evaluation.sql` — схема evaluation-контура для A/B-тестирования промптов
- `03-seed-eval-dataset-v1.sql` — сидирование датасета HRA-EVAL-V1
- `04-create-experiment-v1.sql` — создание эксперимента HRA-EXP-V1

---

## Tables

### Core Tables (Боевой контур)

#### 1. intake_events

**Назначение:** Входящие события из Telegram.

**Поля:**
- `id` (UUID, PK)
- `execution_id` (TEXT, UNIQUE) — идентификатор выполнения workflow
- `source` (TEXT) — источник (telegram, email, web)
- `input_type` (TEXT) — тип ввода (text, voice, document, image, callback)
- `external_message_id` (TEXT) — ID сообщения в Telegram
- `telegram_chat_id` (BIGINT)
- `telegram_user_id` (BIGINT)
- `email_from` (TEXT)
- `email_subject` (TEXT)
- `received_at` (TIMESTAMPTZ)
- `raw_payload` (JSONB) — полные данные сообщения
- `status` (TEXT) — статус (received, ignored_command, ignored_callback)
- `event_type` (TEXT) — тип события (message, callback)
- `created_at` (TIMESTAMPTZ)

**Индексы:**
- `idx_intake_events_execution_id`
- `idx_intake_events_telegram`
- `uq_intake_telegram_message` (UNIQUE, частичный)

---

#### 2. candidate_inputs

**Назначение:** Нормализованные входные данные кандидата.

**Поля:**
- `id` (UUID, PK)
- `intake_event_id` (UUID, FK → intake_events)
- `execution_id` (TEXT)
- `source` (TEXT)
- `input_type` (TEXT)
- `original_text` (TEXT)
- `normalized_text` (TEXT)
- `file_name` (TEXT)
- `file_mime_type` (TEXT)
- `file_hash` (TEXT)
- `processing_status` (TEXT) — статус (prepared, processing, processed, error)
- `created_at` (TIMESTAMPTZ)

**Индексы:**
- `idx_candidate_inputs_execution_id`
- `idx_candidate_inputs_file_hash`

---

#### 3. candidates

**Назначение:** Карточки кандидатов.

**Поля:**
- `id` (UUID, PK)
- `full_name` (TEXT)
- `city` (TEXT)
- `desired_position` (TEXT)
- `experience_years` (NUMERIC)
- `skills` (TEXT[])
- `salary_expectation` (NUMERIC)
- `candidate_summary` (TEXT)
- `source_input_id` (UUID, FK → candidate_inputs)
- `data_quality_status` (TEXT) — статус качества (draft, complete, incomplete)
- `created_at` (TIMESTAMPTZ)
- `updated_at` (TIMESTAMPTZ)

---

#### 4. candidate_contacts

**Назначение:** Контакты кандидатов.

**Поля:**
- `id` (UUID, PK)
- `candidate_id` (UUID, FK → candidates)
- `contact_type` (TEXT) — тип (email, phone, telegram)
- `contact_value` (TEXT)
- `normalized_value` (TEXT)
- `is_primary` (BOOLEAN)
- `created_at` (TIMESTAMPTZ)

**Индексы:**
- `idx_candidate_contacts_normalized`
- `uq_candidate_contacts_normalized` (UNIQUE, частичный)

---

#### 5. vacancies

**Назначение:** Вакансии.

**Поля:**
- `id` (UUID, PK)
- `title` (TEXT)
- `description` (TEXT)
- `requirements` (TEXT)
- `salary_min` (NUMERIC)
- `salary_max` (NUMERIC)
- `status` (TEXT) — статус (open, closed, paused)
- `created_at` (TIMESTAMPTZ)
- `updated_at` (TIMESTAMPTZ)

**Индексы:**
- `idx_vacancies_status`

---

#### 6. matches

**Назначение:** Результаты matching кандидат ↔ вакансия.

**Поля:**
- `id` (UUID, PK)
- `candidate_id` (UUID, FK → candidates)
- `vacancy_id` (UUID, FK → vacancies)
- `score` (NUMERIC, CHECK >= 0 AND <= 100)
- `decision` (TEXT, CHECK IN ('match', 'no_match'))
- `reason` (TEXT)
- `raw_llm_response` (JSONB)
- `created_at` (TIMESTAMPTZ)

**Индексы:**
- `idx_matches_candidate_score`

---

#### 7. final_decisions

**Назначение:** Итоговые решения по кандидатам.

**Поля:**
- `id` (UUID, PK)
- `candidate_id` (UUID, FK → candidates)
- `best_match_id` (UUID, FK → matches)
- `has_match` (BOOLEAN)
- `decision_status` (TEXT)
- `decision_reason` (TEXT)
- `created_at` (TIMESTAMPTZ)

---

#### 8. outbox

**Назначение:** Исходящие сообщения.

**Поля:**
- `id` (UUID, PK)
- `intake_event_id` (UUID, FK → intake_events)
- `candidate_id` (UUID, FK → candidates)
- `channel` (TEXT) — канал (telegram, email)
- `recipient` (TEXT)
- `message_type` (TEXT)
- `subject` (TEXT)
- `body` (TEXT)
- `reply_markup` (JSONB)
- `metadata` (JSONB) **← КРИТИЧЕСКОЕ ПОЛЕ**
- `error_text` (TEXT)
- `status` (TEXT) — статус (pending, sending, sent, error)
- `sent_at` (TIMESTAMPTZ)
- `created_at` (TIMESTAMPTZ)

**Индексы:**
- `idx_outbox_status`

**⚠️ KP-001:** Поле `metadata` существует, но не заполняется в Processing Worker. См. [known-issues.md](../docs/known-issues.md#kp-001-несовместимость-metadata).

---

#### 9. processing_logs

**Назначение:** Журнал обработки.

**Поля:**
- `id` (UUID, PK)
- `execution_id` (TEXT)
- `intake_event_id` (UUID, FK → intake_events)
- `stage` (TEXT)
- `status` (TEXT)
- `details` (TEXT)
- `error_text` (TEXT)
- `attempt` (INTEGER)
- `created_at` (TIMESTAMPTZ)

**Индексы:**
- `idx_processing_logs_execution_id`

---

#### 10. generated_assets

**Назначение:** Сгенерированные материалы.

**Поля:**
- `id` (UUID, PK)
- `candidate_id` (UUID, FK → candidates)
- `asset_type` (TEXT)
- `prompt` (TEXT)
- `provider` (TEXT)
- `asset_url` (TEXT)
- `file_path` (TEXT)
- `status` (TEXT)
- `created_at` (TIMESTAMPTZ)

---

#### 11. bot_credentials

**Назначение:** Учетные данные ботов.

**Поля:**
- `bot_code` (TEXT, PK)
- `bot_token` (TEXT)
- `description` (TEXT)
- `created_at` (TIMESTAMPTZ)

**⚠️ KP-002:** Захардкоженные credentials. См. [known-issues.md](../docs/known-issues.md#kp-002-захардкоженные-credentials).

---

## Prompt Evaluation Tables (Eval-контур)

> **ВАЖНО:** Eval-контур полностью изолирован от боевого.
> Таблицы eval_* не связаны с таблицами боевого контура.

### 1. eval_prompt_datasets

**Назначение:** Версии датасетов для A/B-тестирования промптов.

**Поля:**
- `id` (UUID, PK)
- `dataset_code` (TEXT, UNIQUE) — код датасета (например, HRA-EVAL-V1)
- `name` (TEXT) — название
- `description` (TEXT) — описание
- `status` (TEXT) — статус (draft, active, archived)
- `created_at` (TIMESTAMPTZ)

**CHECK-ограничения:**
- `status IN ('draft', 'active', 'archived')`

---

### 2. eval_prompt_cases

**Назначение:** Тестовые кейсы (кандидаты) для evaluation.

**Поля:**
- `id` (UUID, PK)
- `dataset_id` (UUID, FK → eval_prompt_datasets)
- `case_code` (TEXT, UNIQUE) — код кейса (например, HRA-EVAL-000001)
- `case_type` (TEXT) — тип (obvious_match, obvious_no_match, borderline)
- `candidate_json` (JSONB) — данные кандидата
- `notes` (TEXT)
- `created_at` (TIMESTAMPTZ)

**CHECK-ограничения:**
- `case_type IN ('obvious_match', 'obvious_no_match', 'borderline')`

---

### 3. eval_prompt_case_vacancies

**Назначение:** Вакансии внутри тестового кейса с эталонной разметкой.

**Поля:**
- `id` (UUID, PK)
- `case_id` (UUID, FK → eval_prompt_cases)
- `vacancy_json` (JSONB) — данные вакансии
- `reference_score` (NUMERIC) — эталонный score (0-100)
- `reference_decision` (TEXT) — эталонное решение (match, no_match)
- `reference_reason` (TEXT) — эталонное обоснование
- `created_at` (TIMESTAMPTZ)

**CHECK-ограничения:**
- `reference_score >= 0 AND reference_score <= 100`
- `reference_decision IS NULL OR reference_decision IN ('match', 'no_match')`

---

### 4. eval_prompt_experiments

**Назначение:** Определения экспериментов A/B-тестирования.

**Поля:**
- `id` (UUID, PK)
- `dataset_id` (UUID, FK → eval_prompt_datasets)
- `experiment_code` (TEXT, UNIQUE) — код эксперимента
- `prompt_a_text` (TEXT) — текст промпта A
- `prompt_b_text` (TEXT) — текст промпта B
- `judge_prompt_text` (TEXT) — промпт для judge-модели
- `model_a` (TEXT) — модель A (например, gpt-4o-mini)
- `model_b` (TEXT) — модель B
- `model_judge` (TEXT) — модель judge (например, gpt-4o)
- `temperature_a` (NUMERIC, DEFAULT 0) — температура A
- `temperature_b` (NUMERIC, DEFAULT 0) — температура B
- `temperature_judge` (NUMERIC, DEFAULT 0) — температура judge
- `primary_metric` (TEXT, DEFAULT 'mean_absolute_score_error')
- `guard_metric` (TEXT, DEFAULT 'latency_ms')
- `mde` (TEXT) — Minimum Detectable Effect
- `status` (TEXT) — статус (draft, active, completed, archived)
- `created_at` (TIMESTAMPTZ)

**CHECK-ограничения:**
- `status IN ('draft', 'active', 'completed', 'archived')`
- `temperature_a >= 0 AND temperature_a <= 2`
- `temperature_b >= 0 AND temperature_b <= 2`
- `temperature_judge >= 0 AND temperature_judge <= 2`

---

### 5. eval_prompt_runs

**Назначение:** Запуски экспериментов (judge, A, B).

**Поля:**
- `id` (UUID, PK)
- `experiment_id` (UUID, FK → eval_prompt_experiments)
- `run_type` (TEXT) — тип запуска (judge, A, B)
- `status` (TEXT) — статус (pending, running, completed, failed)
- `started_at` (TIMESTAMPTZ)
- `completed_at` (TIMESTAMPTZ)
- `created_at` (TIMESTAMPTZ)

**CHECK-ограничения:**
- `run_type IN ('judge', 'A', 'B')`
- `status IN ('pending', 'running', 'completed', 'failed')`

---

### 6. eval_prompt_results

**Назначение:** Результаты выполнения по парам candidate × vacancy.

**Поля:**
- `id` (UUID, PK)
- `run_id` (UUID, FK → eval_prompt_runs)
- `case_vacancy_id` (UUID, FK → eval_prompt_case_vacancies)
- `score` (NUMERIC) — score от модели (0-100)
- `decision` (TEXT) — решение модели (match, no_match)
- `latency_ms` (INTEGER) — время выполнения
- `raw_response_json` (JSONB) — полный ответ модели
- `error_message` (TEXT) — сообщение об ошибке
- `created_at` (TIMESTAMPTZ)

**CHECK-ограничения:**
- `score >= 0 AND score <= 100`
- `decision IS NULL OR decision IN ('match', 'no_match')`

---

## Functions

### log_processing_event()

**Назначение:** Логирование событий обработки.

**Параметры:**
- `p_execution_id` (TEXT)
- `p_intake_event_id` (UUID)
- `p_stage` (TEXT)
- `p_status` (TEXT)
- `p_details` (TEXT, DEFAULT NULL)
- `p_error_text` (TEXT, DEFAULT NULL)
- `p_attempt` (INTEGER, DEFAULT 1)

**Возвращает:** VOID

**Использование:**
```sql
SELECT log_processing_event(
    'exec-123',
    'uuid-456',
    'intake_received',
    'received',
    'Telegram input saved',
    NULL,
    1
);
```

---

## Indexes

### Primary Indexes

| Таблица | Индекс | Тип |
|---------|--------|-----|
| intake_events | idx_intake_events_execution_id | B-tree |
| intake_events | idx_intake_events_telegram | B-tree |
| intake_events | uq_intake_telegram_message | UNIQUE, Partial |
| candidate_inputs | idx_candidate_inputs_execution_id | B-tree |
| candidate_inputs | idx_candidate_inputs_file_hash | B-tree |
| candidate_contacts | idx_candidate_contacts_normalized | B-tree |
| candidate_contacts | uq_candidate_contacts_normalized | UNIQUE, Partial |
| vacancies | idx_vacancies_status | B-tree |
| matches | idx_matches_candidate_score | B-tree |
| processing_logs | idx_processing_logs_execution_id | B-tree |
| outbox | idx_outbox_status | B-tree |

### Prompt Evaluation Indexes

| Таблица | Индекс | Тип |
|---------|--------|-----|
| eval_prompt_datasets | idx_eval_prompt_datasets_status | B-tree |
| eval_prompt_cases | idx_eval_prompt_cases_dataset_id | B-tree |
| eval_prompt_cases | idx_eval_prompt_cases_case_type | B-tree |
| eval_prompt_case_vacancies | idx_eval_prompt_case_vacancies_case_id | B-tree |
| eval_prompt_experiments | idx_eval_prompt_experiments_dataset_id | B-tree |
| eval_prompt_experiments | idx_eval_prompt_experiments_status | B-tree |
| eval_prompt_runs | idx_eval_prompt_runs_experiment_id | B-tree |
| eval_prompt_runs | idx_eval_prompt_runs_status | B-tree |
| eval_prompt_results | idx_eval_prompt_results_run_id | B-tree |
| eval_prompt_results | idx_eval_prompt_results_case_vacancy_id | B-tree |
| eval_prompt_results | idx_eval_prompt_results_decision | B-tree |

---

## Migrations

**Текущая версия:** 1.0 (schema_hr_assistant.sql)

**История миграций:**
- **v1.0** (2026-04-29): Начальная схема
- **v1.1** (дата TBD): Добавлено поле `metadata` в `outbox`
- **v1.2** (дата TBD): Добавлено поле `event_type` в `intake_events`
- **v1.3** (дата TBD): Добавлено поле `error_text` в `outbox`
- **v2.0** (2026-06-24): Добавлен evaluation-контур (02-prompt-evaluation.sql) ✅ **Применено на production**

---

## Prompt Evaluation Schema

**Файл:** `02-prompt-evaluation.sql`

**Назначение:** Отдельный контур для A/B-тестирования matching prompt.

**Предназначен для:**
- Урока 4 по Prompt Engineering
- Регрессионной проверки matching prompt

**Таблицы:**
| Таблица | Назначение |
|---------|------------|
| eval_prompt_datasets | Версии датасетов тестовых кейсов |
| eval_prompt_cases | Тестовые кейсы (кандидаты) |
| eval_prompt_case_vacancies | Вакансии внутри кейса с reference-разметкой |
| eval_prompt_experiments | Определения экспериментов A/B-тестирования |
| eval_prompt_runs | Запуски экспериментов (judge, A, B) |
| eval_prompt_results | Результаты выполнения по парам candidate × vacancy |

**ВАЖНО:**
- Eval-контур полностью изолирован от боевого.
- Не использует таблицы candidates, vacancies, matches, outbox.
- Все таблицы имеют префикс `eval_prompt_`.

---

## Prompt Evaluation Experiments

### HRA-EXP-V1

**Файл:** `04-create-experiment-v1.sql`

**Назначение:** Создание эксперимента для сравнения production matching prompt с experimental prompt.

**Параметры эксперимента:**
- **Experiment Code:** HRA-EXP-V1
- **Dataset:** HRA-EVAL-V1 (30 candidates × 3 vacancies = 90 pairs)
- **Prompt A:** Production matching prompt (gpt-4o-mini)
- **Prompt B:** Experimental matching prompt (gpt-4o-mini)
- **Judge:** Reference scoring prompt (gpt-4.1)

**Метрики:**
- **Primary:** Mean Absolute Score Error (MAE)
- **Guard:** Average Latency (ms)
- **Secondary:** Decision Accuracy

**Критерии принятия:**
- MAE improvement ≥ 20%
- Latency growth ≤ 30%

**Документация:**
- [Judge Prompt](../shared/prompts/judge-matching-prompt-v1.md)
- [Experimental Prompt B](../shared/prompts/experimental-matching-prompt-v1.md)
- [Workflow Documentation](../docs/PROMPT_EVALUATION_WORKFLOW.md)

---

## Применение схемы

```bash
# Подключение к БД
psql -U hr_user -d hr_assistant

# Применение основной схемы (боевой контур)
\i schema_hr_assistant.sql

# Применение evaluation-схемы (eval-контур)
\i 02-prompt-evaluation.sql

# Или из командной строки
psql -U hr_user -d hr_assistant -f schema_hr_assistant.sql
psql -U hr_user -d hr_assistant -f 02-prompt-evaluation.sql
```

---

## Backup и восстановление

```bash
# Backup
pg_dump -U hr_user hr_assistant > backup_$(date +%Y%m%d).sql

# Восстановление
psql -U hr_user hr_assistant < backup_20260623.sql
```

---

## References

- [SPEC.md](../docs/SPEC.md) — функциональная спецификация
- [workflows/README.md](../workflows/README.md) — описание workflow
- [known-issues.md](../docs/known-issues.md) — известные проблемы