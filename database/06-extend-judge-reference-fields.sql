-- ============================================================
-- HRA Prompt Evaluation — Extend Judge Reference Fields
-- Назначение:
--   Добавляет детальные оценки Judge в структуру БД
--   для teacher–student fine-tuning
--
-- Контекст:
--   Judge возвращает JSON с role_score, skills_score, etc.,
--   но workflow сохранял только reference_score и reference_reason.
--   Для fine-tuning нужны детальные оценки в структурированном виде.
--
-- Использование:
--   psql -U hr_user -d hr_assistant -f 06-extend-judge-reference-fields.sql
-- ============================================================

-- ============================================================
-- 1. Добавление колонок для детальных оценок Judge
-- ============================================================

-- Оценка роли / должности (0-30 баллов)
ALTER TABLE eval_prompt_case_vacancies
ADD COLUMN IF NOT EXISTS reference_role_score NUMERIC;

-- Оценка навыков (0-35 баллов)
ALTER TABLE eval_prompt_case_vacancies
ADD COLUMN IF NOT EXISTS reference_skills_score NUMERIC;

-- Оценка опыта (0-20 баллов)
ALTER TABLE eval_prompt_case_vacancies
ADD COLUMN IF NOT EXISTS reference_experience_score NUMERIC;

-- Оценка условий (0-15 баллов)
ALTER TABLE eval_prompt_case_vacancies
ADD COLUMN IF NOT EXISTS reference_conditions_score NUMERIC;

-- Полный JSON ответ Judge (для аудита и восстановления)
ALTER TABLE eval_prompt_case_vacancies
ADD COLUMN IF NOT EXISTS reference_raw_response_json JSONB;

-- Модель Judge (например, gpt-4.1-2025-04-14)
ALTER TABLE eval_prompt_case_vacancies
ADD COLUMN IF NOT EXISTS reference_model TEXT;

-- Время ответа Judge в миллисекундах
ALTER TABLE eval_prompt_case_vacancies
ADD COLUMN IF NOT EXISTS reference_latency_ms INTEGER;

-- Время генерации ответа Judge
ALTER TABLE eval_prompt_case_vacancies
ADD COLUMN IF NOT EXISTS reference_generated_at TIMESTAMPTZ;

-- ============================================================
-- 2. CHECK constraints для диапазонов оценок
-- ============================================================

-- Роль: 0-30 баллов
ALTER TABLE eval_prompt_case_vacancies
DROP CONSTRAINT IF EXISTS chk_reference_role_score_range;

ALTER TABLE eval_prompt_case_vacancies
ADD CONSTRAINT chk_reference_role_score_range
CHECK (reference_role_score IS NULL OR
      (reference_role_score >= 0 AND reference_role_score <= 30));

-- Навыки: 0-35 баллов
ALTER TABLE eval_prompt_case_vacancies
DROP CONSTRAINT IF EXISTS chk_reference_skills_score_range;

ALTER TABLE eval_prompt_case_vacancies
ADD CONSTRAINT chk_reference_skills_score_range
CHECK (reference_skills_score IS NULL OR
      (reference_skills_score >= 0 AND reference_skills_score <= 35));

-- Опыт: 0-20 баллов
ALTER TABLE eval_prompt_case_vacancies
DROP CONSTRAINT IF EXISTS chk_reference_experience_score_range;

ALTER TABLE eval_prompt_case_vacancies
ADD CONSTRAINT chk_reference_experience_score_range
CHECK (reference_experience_score IS NULL OR
      (reference_experience_score >= 0 AND reference_experience_score <= 20));

-- Условия: 0-15 баллов
ALTER TABLE eval_prompt_case_vacancies
DROP CONSTRAINT IF EXISTS chk_reference_conditions_score_range;

ALTER TABLE eval_prompt_case_vacancies
ADD CONSTRAINT chk_reference_conditions_score_range
CHECK (reference_conditions_score IS NULL OR
      (reference_conditions_score >= 0 AND reference_conditions_score <= 15));

-- Общий score: 0-100 баллов (если ещё не добавлен)
ALTER TABLE eval_prompt_case_vacancies
DROP CONSTRAINT IF EXISTS chk_reference_score_range;

ALTER TABLE eval_prompt_case_vacancies
ADD CONSTRAINT chk_reference_score_range
CHECK (reference_score IS NULL OR
      (reference_score >= 0 AND reference_score <= 100));

-- Decision: только 'match' или 'no_match' (если ещё не добавлен)
ALTER TABLE eval_prompt_case_vacancies
DROP CONSTRAINT IF EXISTS chk_reference_decision_values;

ALTER TABLE eval_prompt_case_vacancies
ADD CONSTRAINT chk_reference_decision_values
CHECK (reference_decision IS NULL OR
      reference_decision IN ('match', 'no_match'));

-- ============================================================
-- 3. Индексы для быстрого поиска
-- ============================================================

-- Индекс по decision (для фильтрации match/no_match)
CREATE INDEX IF NOT EXISTS idx_eval_prompt_case_vacancies_reference_decision
ON eval_prompt_case_vacancies(reference_decision);

-- Индекс по score (для сортировки и фильтрации)
CREATE INDEX IF NOT EXISTS idx_eval_prompt_case_vacancies_reference_score
ON eval_prompt_case_vacancies(reference_score);

-- Индекс по времени генерации (для аналитики)
CREATE INDEX IF NOT EXISTS idx_eval_prompt_case_vacancies_reference_generated_at
ON eval_prompt_case_vacancies(reference_generated_at);

-- ============================================================
-- 4. Комментарии к колонкам
-- ============================================================

COMMENT ON COLUMN eval_prompt_case_vacancies.reference_role_score IS 'Оценка роли/должности от Judge (0-30 баллов)';
COMMENT ON COLUMN eval_prompt_case_vacancies.reference_skills_score IS 'Оценка навыков от Judge (0-35 баллов)';
COMMENT ON COLUMN eval_prompt_case_vacancies.reference_experience_score IS 'Оценка опыта от Judge (0-20 баллов)';
COMMENT ON COLUMN eval_prompt_case_vacancies.reference_conditions_score IS 'Оценка условий от Judge (0-15 баллов)';
COMMENT ON COLUMN eval_prompt_case_vacancies.reference_raw_response_json IS 'Полный JSON ответ Judge (для аудита)';
COMMENT ON COLUMN eval_prompt_case_vacancies.reference_model IS 'Модель Judge (например, gpt-4.1-2025-04-14)';
COMMENT ON COLUMN eval_prompt_case_vacancies.reference_latency_ms IS 'Время ответа Judge в миллисекундах';
COMMENT ON COLUMN eval_prompt_case_vacancies.reference_generated_at IS 'Время генерации ответа Judge';

-- ============================================================
-- 5. Контрольная запись в журнал
-- ============================================================

INSERT INTO processing_logs (
    execution_id,
    stage,
    status,
    details,
    attempt
)
VALUES (
    'schema_migration',
    'extend_judge_reference_fields',
    'success',
    'Added columns: reference_role_score, reference_skills_score, reference_experience_score, reference_conditions_score, reference_raw_response_json, reference_model, reference_latency_ms, reference_generated_at. Added CHECK constraints and indexes.',
    1
)
ON CONFLICT DO NOTHING;

-- ============================================================
-- 6. Верификация изменений
-- ============================================================

SELECT
    'Schema Migration Complete' AS status,
    (SELECT COUNT(*) FROM information_schema.columns
     WHERE table_name = 'eval_prompt_case_vacancies'
     AND column_name IN ('reference_role_score', 'reference_skills_score',
                         'reference_experience_score', 'reference_conditions_score',
                         'reference_raw_response_json', 'reference_model',
                         'reference_latency_ms', 'reference_generated_at')) AS new_columns_added,
    (SELECT COUNT(*) FROM pg_indexes
     WHERE tablename = 'eval_prompt_case_vacancies'
     AND indexname IN ('idx_eval_prompt_case_vacancies_reference_decision',
                       'idx_eval_prompt_case_vacancies_reference_score',
                       'idx_eval_prompt_case_vacancies_reference_generated_at')) AS new_indexes_created;