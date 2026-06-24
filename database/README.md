# HR Assistant Database

**Last Updated:** 2026-06-23

---

## Schema Overview

**Database:** PostgreSQL 16

**Schema File:** `schema_hr_assistant.sql`

---

## Tables

### Core Tables

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

---

## Migrations

**Текущая версия:** 1.0 (schema_hr_assistant.sql)

**История миграций:**
- **v1.0** (2026-04-29): Начальная схема
- **v1.1** (дата TBD): Добавлено поле `metadata` в `outbox`
- **v1.2** (дата TBD): Добавлено поле `event_type` в `intake_events`
- **v1.3** (дата TBD): Добавлено поле `error_text` в `outbox`

---

## Применение схемы

```bash
# Подключение к БД
psql -U hr_user -d hr_assistant

# Применение схемы
\i schema_hr_assistant.sql

# Или из командной строки
psql -U hr_user -d hr_assistant -f schema_hr_assistant.sql
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