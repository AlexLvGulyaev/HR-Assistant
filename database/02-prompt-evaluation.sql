-- ============================================================
-- HR Assistant — Prompt Evaluation Schema
-- Назначение:
--   Создаёт отдельный контур для A/B-тестирования matching prompt.
--   Предназначен для регрессионной проверки и уроков Prompt Engineering.
--
-- ВАЖНО:
--   Это полностью изолированный контур.
--   Боевые таблицы HRA (candidates, vacancies, matches, outbox) НЕ изменяются.
--
-- Использование:
--   psql -U hr_user -d hr_assistant -f 02-prompt-evaluation.sql
-- ============================================================

-- Extension pgcrypto уже создан в основной схеме (schema_hr_assistant.sql)
-- Но для идемпотентности добавляем проверку
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- ============================================================
-- 1. eval_prompt_datasets
-- Хранит версию датасета тестовых кейсов
-- ============================================================

CREATE TABLE IF NOT EXISTS eval_prompt_datasets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    dataset_code TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    status TEXT NOT NULL DEFAULT 'draft',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),

    CONSTRAINT chk_dataset_status CHECK (status IN ('draft', 'active', 'archived'))
);

COMMENT ON TABLE eval_prompt_datasets IS 'Версии датасетов для A/B-тестирования промптов';
COMMENT ON COLUMN eval_prompt_datasets.dataset_code IS 'Уникальный код датасета (например, HRA-EVAL-V1)';
COMMENT ON COLUMN eval_prompt_datasets.status IS 'Статус: draft, active, archived';

-- ============================================================
-- 2. eval_prompt_cases
-- Хранит кандидата как тестовый кейс
-- ============================================================

CREATE TABLE IF NOT EXISTS eval_prompt_cases (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    dataset_id UUID NOT NULL REFERENCES eval_prompt_datasets(id) ON DELETE CASCADE,
    case_code TEXT UNIQUE NOT NULL,
    case_type TEXT NOT NULL,
    candidate_json JSONB NOT NULL,
    notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),

    CONSTRAINT chk_case_type CHECK (case_type IN ('obvious_match', 'obvious_no_match', 'borderline'))
);

COMMENT ON TABLE eval_prompt_cases IS 'Тестовые кейсы (кандидаты) для evaluation';
COMMENT ON COLUMN eval_prompt_cases.case_code IS 'Уникальный код кейса (например, HRA-EVAL-000001)';
COMMENT ON COLUMN eval_prompt_cases.case_type IS 'Тип кейса: obvious_match, obvious_no_match, borderline';
COMMENT ON COLUMN eval_prompt_cases.candidate_json IS 'Структура данных кандидата (JSON)';

-- ============================================================
-- 3. eval_prompt_case_vacancies
-- Хранит вакансии внутри кейса и reference-разметку judge
-- ============================================================

CREATE TABLE IF NOT EXISTS eval_prompt_case_vacancies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_id UUID NOT NULL REFERENCES eval_prompt_cases(id) ON DELETE CASCADE,
    vacancy_json JSONB NOT NULL,
    reference_score NUMERIC CHECK (reference_score >= 0 AND reference_score <= 100),
    reference_decision TEXT,
    reference_reason TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),

    CONSTRAINT chk_reference_decision CHECK (reference_decision IS NULL OR reference_decision IN ('match', 'no_match'))
);

COMMENT ON TABLE eval_prompt_case_vacancies IS 'Вакансии внутри тестового кейса с эталонной разметкой';
COMMENT ON COLUMN eval_prompt_case_vacancies.reference_score IS 'Эталонный score от judge (0-100)';
COMMENT ON COLUMN eval_prompt_case_vacancies.reference_decision IS 'Эталонное решение: match, no_match';
COMMENT ON COLUMN eval_prompt_case_vacancies.reference_reason IS 'Эталонное обоснование';

-- ============================================================
-- 4. eval_prompt_experiments
-- Хранит определение эксперимента над конкретным датасетом
-- ============================================================

CREATE TABLE IF NOT EXISTS eval_prompt_experiments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    dataset_id UUID NOT NULL REFERENCES eval_prompt_datasets(id) ON DELETE CASCADE,
    experiment_code TEXT UNIQUE NOT NULL,
    prompt_a_text TEXT NOT NULL,
    prompt_b_text TEXT NOT NULL,
    judge_prompt_text TEXT NOT NULL,
    model_a TEXT NOT NULL,
    model_b TEXT NOT NULL,
    model_judge TEXT NOT NULL,
    temperature_a NUMERIC NOT NULL DEFAULT 0,
    temperature_b NUMERIC NOT NULL DEFAULT 0,
    temperature_judge NUMERIC NOT NULL DEFAULT 0,
    primary_metric TEXT NOT NULL DEFAULT 'mean_absolute_score_error',
    guard_metric TEXT NOT NULL DEFAULT 'latency_ms',
    mde TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'draft',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),

    CONSTRAINT chk_experiment_status CHECK (status IN ('draft', 'active', 'completed', 'archived')),
    CONSTRAINT chk_temperature_a CHECK (temperature_a >= 0 AND temperature_a <= 2),
    CONSTRAINT chk_temperature_b CHECK (temperature_b >= 0 AND temperature_b <= 2),
    CONSTRAINT chk_temperature_judge CHECK (temperature_judge >= 0 AND temperature_judge <= 2)
);

COMMENT ON TABLE eval_prompt_experiments IS 'Определения экспериментов A/B-тестирования';
COMMENT ON COLUMN eval_prompt_experiments.experiment_code IS 'Уникальный код эксперимента';
COMMENT ON COLUMN eval_prompt_experiments.prompt_a_text IS 'Текст промпта A';
COMMENT ON COLUMN eval_prompt_experiments.prompt_b_text IS 'Текст промпта B';
COMMENT ON COLUMN eval_prompt_experiments.judge_prompt_text IS 'Промпт для judge-модели';
COMMENT ON COLUMN eval_prompt_experiments.model_a IS 'Модель для промпта A (например, gpt-4o-mini)';
COMMENT ON COLUMN eval_prompt_experiments.model_b IS 'Модель для промпта B';
COMMENT ON COLUMN eval_prompt_experiments.model_judge IS 'Модель для judge (например, gpt-4o)';
COMMENT ON COLUMN eval_prompt_experiments.primary_metric IS 'Основная метрика эксперимента';
COMMENT ON COLUMN eval_prompt_experiments.guard_metric IS 'Guard-метрика (лимит)';
COMMENT ON COLUMN eval_prompt_experiments.mde IS 'Minimum Detectable Effect';

-- ============================================================
-- 5. eval_prompt_runs
-- Хранит один запуск judge/A/B
-- ============================================================

CREATE TABLE IF NOT EXISTS eval_prompt_runs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    experiment_id UUID NOT NULL REFERENCES eval_prompt_experiments(id) ON DELETE CASCADE,
    run_type TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),

    CONSTRAINT chk_run_type CHECK (run_type IN ('judge', 'A', 'B')),
    CONSTRAINT chk_run_status CHECK (status IN ('pending', 'running', 'completed', 'failed'))
);

COMMENT ON TABLE eval_prompt_runs IS 'Запуски экспериментов (judge, A, B)';
COMMENT ON COLUMN eval_prompt_runs.run_type IS 'Тип запуска: judge, A, B';
COMMENT ON COLUMN eval_prompt_runs.status IS 'Статус: pending, running, completed, failed';

-- ============================================================
-- 6. eval_prompt_results
-- Хранит результат по одной паре candidate × vacancy
-- ============================================================

CREATE TABLE IF NOT EXISTS eval_prompt_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id UUID NOT NULL REFERENCES eval_prompt_runs(id) ON DELETE CASCADE,
    case_vacancy_id UUID NOT NULL REFERENCES eval_prompt_case_vacancies(id) ON DELETE CASCADE,
    score NUMERIC CHECK (score >= 0 AND score <= 100),
    decision TEXT,
    latency_ms INTEGER,
    raw_response_json JSONB,
    error_message TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),

    CONSTRAINT chk_result_decision CHECK (decision IS NULL OR decision IN ('match', 'no_match'))
);

COMMENT ON TABLE eval_prompt_results IS 'Результаты выполнения по парам candidate × vacancy';
COMMENT ON COLUMN eval_prompt_results.score IS 'Score от модели (0-100)';
COMMENT ON COLUMN eval_prompt_results.decision IS 'Решение модели: match, no_match';
COMMENT ON COLUMN eval_prompt_results.latency_ms IS 'Время выполнения в миллисекундах';
COMMENT ON COLUMN eval_prompt_results.raw_response_json IS 'Полный ответ модели (JSON)';
COMMENT ON COLUMN eval_prompt_results.error_message IS 'Сообщение об ошибке (если есть)';

-- ============================================================
-- Индексы
-- ============================================================

CREATE INDEX IF NOT EXISTS idx_eval_prompt_cases_dataset_id
    ON eval_prompt_cases(dataset_id);

CREATE INDEX IF NOT EXISTS idx_eval_prompt_case_vacancies_case_id
    ON eval_prompt_case_vacancies(case_id);

CREATE INDEX IF NOT EXISTS idx_eval_prompt_experiments_dataset_id
    ON eval_prompt_experiments(dataset_id);

CREATE INDEX IF NOT EXISTS idx_eval_prompt_runs_experiment_id
    ON eval_prompt_runs(experiment_id);

CREATE INDEX IF NOT EXISTS idx_eval_prompt_results_run_id
    ON eval_prompt_results(run_id);

CREATE INDEX IF NOT EXISTS idx_eval_prompt_results_case_vacancy_id
    ON eval_prompt_results(case_vacancy_id);

-- Дополнительные индексы для частых запросов
CREATE INDEX IF NOT EXISTS idx_eval_prompt_datasets_status
    ON eval_prompt_datasets(status);

CREATE INDEX IF NOT EXISTS idx_eval_prompt_cases_case_type
    ON eval_prompt_cases(case_type);

CREATE INDEX IF NOT EXISTS idx_eval_prompt_experiments_status
    ON eval_prompt_experiments(status);

CREATE INDEX IF NOT EXISTS idx_eval_prompt_runs_status
    ON eval_prompt_runs(status);

CREATE INDEX IF NOT EXISTS idx_eval_prompt_results_decision
    ON eval_prompt_results(decision);

-- ============================================================
-- Schema initialized
-- ============================================================
-- Примечание: eval-контур полностью автономен.
-- Логирование инициализации не требуется, так как eval-таблицы
-- изолированы от боевого контура HRA.