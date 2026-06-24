-- ============================================================
-- HR Assistant 2.0 — PostgreSQL schema
-- Назначение:
--   Создаёт структуру БД для мультимодального HR-ассистента.
--
-- Основной принцип:
--   n8n выполняет роль оркестратора, а PostgreSQL хранит
--   бизнес-данные, логи, результаты matching и исходящие сообщения.
--
-- Использование:
--   psql -U hr_user -d hr_assistant -f schema_hr_assistant.sql
-- ============================================================

CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- ============================================================
-- 1. Входящие события
-- ============================================================

CREATE TABLE IF NOT EXISTS intake_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    execution_id TEXT NOT NULL UNIQUE,
    source TEXT NOT NULL,
    input_type TEXT NOT NULL,
    external_message_id TEXT,
    telegram_chat_id BIGINT,
    telegram_user_id BIGINT,
    email_from TEXT,
    email_subject TEXT,
    received_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    raw_payload JSONB,
    status TEXT NOT NULL DEFAULT 'received',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ============================================================
-- 2. Нормализованные входные данные кандидата
-- ============================================================

CREATE TABLE IF NOT EXISTS candidate_inputs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    intake_event_id UUID NOT NULL REFERENCES intake_events(id) ON DELETE CASCADE,
    execution_id TEXT NOT NULL,
    source TEXT NOT NULL,
    input_type TEXT NOT NULL,
    original_text TEXT,
    normalized_text TEXT,
    file_name TEXT,
    file_mime_type TEXT,
    file_hash TEXT,
    processing_status TEXT NOT NULL DEFAULT 'prepared',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ============================================================
-- 3. Единая карточка кандидата
-- ============================================================

CREATE TABLE IF NOT EXISTS candidates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    full_name TEXT,
    city TEXT,
    desired_position TEXT,
    experience_years NUMERIC,
    skills TEXT[],
    salary_expectation NUMERIC,
    candidate_summary TEXT,
    source_input_id UUID REFERENCES candidate_inputs(id),
    data_quality_status TEXT NOT NULL DEFAULT 'draft',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ============================================================
-- 4. Контакты кандидата
-- ============================================================

CREATE TABLE IF NOT EXISTS candidate_contacts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    candidate_id UUID NOT NULL REFERENCES candidates(id) ON DELETE CASCADE,
    contact_type TEXT NOT NULL,
    contact_value TEXT NOT NULL,
    normalized_value TEXT,
    is_primary BOOLEAN NOT NULL DEFAULT false,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ============================================================
-- 5. Вакансии
-- ============================================================

CREATE TABLE IF NOT EXISTS vacancies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    requirements TEXT,
    salary_min NUMERIC,
    salary_max NUMERIC,
    status TEXT NOT NULL DEFAULT 'open',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ============================================================
-- 6. Результаты matching кандидат ↔ вакансия
-- ============================================================

CREATE TABLE IF NOT EXISTS matches (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    candidate_id UUID NOT NULL REFERENCES candidates(id) ON DELETE CASCADE,
    vacancy_id UUID NOT NULL REFERENCES vacancies(id),
    score NUMERIC NOT NULL CHECK (score >= 0 AND score <= 100),
    decision TEXT NOT NULL CHECK (decision IN ('match', 'no_match')),
    reason TEXT,
    raw_llm_response JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ============================================================
-- 7. Итоговые решения
-- ============================================================

CREATE TABLE IF NOT EXISTS final_decisions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    candidate_id UUID NOT NULL REFERENCES candidates(id) ON DELETE CASCADE,
    best_match_id UUID REFERENCES matches(id),
    has_match BOOLEAN NOT NULL DEFAULT false,
    decision_status TEXT NOT NULL,
    decision_reason TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ============================================================
-- 8. Исходящие сообщения
-- ============================================================

CREATE TABLE IF NOT EXISTS outbox (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    intake_event_id UUID REFERENCES intake_events(id),
    candidate_id UUID REFERENCES candidates(id),
    channel TEXT NOT NULL,
    recipient TEXT NOT NULL,
    message_type TEXT NOT NULL,
    subject TEXT,
    body TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    sent_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ============================================================
-- 9. Журнал обработки
-- ============================================================

CREATE TABLE IF NOT EXISTS processing_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    execution_id TEXT NOT NULL,
    intake_event_id UUID REFERENCES intake_events(id),
    stage TEXT NOT NULL,
    status TEXT NOT NULL,
    details TEXT,
    error_text TEXT,
    attempt INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ============================================================
-- 10. Сгенерированные визуальные материалы
-- ============================================================

CREATE TABLE IF NOT EXISTS generated_assets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    candidate_id UUID REFERENCES candidates(id),
    asset_type TEXT NOT NULL,
    prompt TEXT,
    provider TEXT,
    asset_url TEXT,
    file_path TEXT,
    status TEXT NOT NULL DEFAULT 'created',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ============================================================
-- Индексы
-- ============================================================

CREATE INDEX IF NOT EXISTS idx_intake_events_execution_id
    ON intake_events(execution_id);

CREATE INDEX IF NOT EXISTS idx_intake_events_telegram
    ON intake_events(telegram_chat_id, external_message_id);

CREATE INDEX IF NOT EXISTS idx_candidate_inputs_execution_id
    ON candidate_inputs(execution_id);

CREATE INDEX IF NOT EXISTS idx_candidate_inputs_file_hash
    ON candidate_inputs(file_hash);

CREATE INDEX IF NOT EXISTS idx_candidate_contacts_normalized
    ON candidate_contacts(normalized_value);

CREATE INDEX IF NOT EXISTS idx_vacancies_status
    ON vacancies(status);

CREATE INDEX IF NOT EXISTS idx_matches_candidate_score
    ON matches(candidate_id, score DESC);

CREATE INDEX IF NOT EXISTS idx_processing_logs_execution_id
    ON processing_logs(execution_id);

CREATE INDEX IF NOT EXISTS idx_outbox_status
    ON outbox(status);

CREATE UNIQUE INDEX IF NOT EXISTS uq_intake_telegram_message
    ON intake_events(source, telegram_chat_id, external_message_id)
    WHERE source = 'telegram'
      AND telegram_chat_id IS NOT NULL
      AND external_message_id IS NOT NULL;

CREATE UNIQUE INDEX IF NOT EXISTS uq_candidate_contacts_normalized
ON candidate_contacts(contact_type, normalized_value)
WHERE normalized_value IS NOT NULL
  AND normalized_value <> '';

CREATE OR REPLACE FUNCTION log_processing_event(
    p_execution_id TEXT,
    p_intake_event_id UUID,
    p_stage TEXT,
    p_status TEXT,
    p_details TEXT DEFAULT NULL,
    p_error_text TEXT DEFAULT NULL,
    p_attempt INTEGER DEFAULT 1
)
RETURNS VOID AS $$
BEGIN
    INSERT INTO processing_logs (
        execution_id,
        intake_event_id,
        stage,
        status,
        details,
        error_text,
        attempt
    )
    VALUES (
        p_execution_id,
        p_intake_event_id,
        p_stage,
        p_status,
        p_details,
        p_error_text,
        COALESCE(p_attempt, 1)
    );
END;
$$ LANGUAGE plpgsql;

-- ============================================================
-- Контрольная запись в журнал
-- ============================================================

INSERT INTO processing_logs (
    execution_id,
    stage,
    status,
    details,
    attempt
)
VALUES (
    'schema_init',
    'database_schema',
    'success',
    'HR Assistant 2.0 schema initialized',
    1
)
ON CONFLICT DO NOTHING;

ALTER TABLE outbox
ADD COLUMN IF NOT EXISTS reply_markup jsonb;

CREATE TABLE IF NOT EXISTS bot_credentials (
    bot_code text PRIMARY KEY,
    bot_token text NOT NULL,
    description text,
    created_at timestamptz DEFAULT now()
);

INSERT INTO bot_credentials (bot_code, bot_token, description)
VALUES (
    'hr_assistant',
    'REPLACE_ME_WITH_YOUR_BOT_TOKEN',
    'HR assistant Telegram bot'
)
ON CONFLICT (bot_code)
DO UPDATE SET bot_token = EXCLUDED.bot_token;

ALTER TABLE intake_events
ADD COLUMN IF NOT EXISTS event_type text;

UPDATE intake_events
SET event_type = CASE
    WHEN input_type = 'callback' THEN 'callback'
    ELSE 'message'
END
WHERE event_type IS NULL;


ALTER TABLE outbox
ADD COLUMN IF NOT EXISTS error_text text;


CREATE EXTENSION IF NOT EXISTS pgcrypto;

ALTER TABLE intake_events
ADD COLUMN IF NOT EXISTS event_type text;

ALTER TABLE outbox
ADD COLUMN IF NOT EXISTS reply_markup jsonb;

ALTER TABLE outbox
ADD COLUMN IF NOT EXISTS error_text text;

CREATE OR REPLACE FUNCTION log_processing_event(
    p_execution_id TEXT,
    p_intake_event_id UUID,
    p_stage TEXT,
    p_status TEXT,
    p_details TEXT DEFAULT NULL,
    p_error_text TEXT DEFAULT NULL,
    p_attempt INTEGER DEFAULT 1
)
RETURNS VOID AS $$
BEGIN
    INSERT INTO processing_logs (
        execution_id,
        intake_event_id,
        stage,
        status,
        details,
        error_text,
        attempt
    )
    VALUES (
        COALESCE(p_execution_id, 'unknown'),
        p_intake_event_id,
        p_stage,
        p_status,
        p_details,
        p_error_text,
        COALESCE(p_attempt, 1)
    );
END;

ALTER TABLE outbox
ADD COLUMN IF NOT EXISTS metadata jsonb;
