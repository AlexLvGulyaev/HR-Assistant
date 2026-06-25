-- ============================================================
-- HRA-EVAL-SMOKE: Smoke Dataset for Workflow Testing
-- Минимальный датасет для безопасной проверки workflow
-- ============================================================

-- ============================================================
-- 1. Создать smoke dataset
-- ============================================================

INSERT INTO eval_prompt_datasets (
    id,
    dataset_code,
    name,
    description,
    status,
    created_at
)
SELECT
    gen_random_uuid(),
    'HRA-EVAL-SMOKE',
    'Smoke Test Dataset',
    'Минимальный датасет для безопасной проверки workflow. 1 кандидат × 1 вакансия = 1 пара.',
    'active',
    now()
WHERE NOT EXISTS (
    SELECT 1 FROM eval_prompt_datasets WHERE dataset_code = 'HRA-EVAL-SMOKE'
);

-- ============================================================
-- 2. Создать smoke case (скопировать первый case из HRA-EVAL-V1)
-- ============================================================

INSERT INTO eval_prompt_cases (
    id,
    dataset_id,
    case_code,
    case_type,
    candidate_json,
    notes,
    created_at
)
SELECT
    gen_random_uuid(),
    d.id,
    'HRA-SMOKE-000001',
    'obvious_match',
    c.candidate_json,
    'SMOKE TEST: Скопировано из HRA-EVAL-000001 для безопасной проверки workflow.',
    now()
FROM eval_prompt_datasets d
CROSS JOIN eval_prompt_cases c
WHERE d.dataset_code = 'HRA-EVAL-SMOKE'
  AND c.case_code = 'HRA-EVAL-000001'
  AND NOT EXISTS (
      SELECT 1 FROM eval_prompt_cases WHERE case_code = 'HRA-SMOKE-000001'
  );

-- ============================================================
-- 3. Создать smoke pair (скопировать первую вакансию из HRA-EVAL-V1)
-- ============================================================

INSERT INTO eval_prompt_case_vacancies (
    id,
    case_id,
    vacancy_json,
    reference_score,
    reference_decision,
    reference_reason,
    created_at
)
SELECT
    gen_random_uuid(),
    c.id,
    cv.vacancy_json,
    NULL,  -- reference_score должен быть пустым для smoke run
    NULL,  -- reference_decision должен быть пустым
    NULL,  -- reference_reason должен быть пустым
    now()
FROM eval_prompt_cases c
JOIN eval_prompt_datasets d ON c.dataset_id = d.id
CROSS JOIN eval_prompt_case_vacancies cv
JOIN eval_prompt_cases c_orig ON cv.case_id = c_orig.id
WHERE d.dataset_code = 'HRA-EVAL-SMOKE'
  AND c.case_code = 'HRA-SMOKE-000001'
  AND c_orig.case_code = 'HRA-EVAL-000001'
  AND NOT EXISTS (
      SELECT 1
      FROM eval_prompt_case_vacancies cv2
      JOIN eval_prompt_cases c2 ON cv2.case_id = c2.id
      JOIN eval_prompt_datasets d2 ON c2.dataset_id = d2.id
      WHERE d2.dataset_code = 'HRA-EVAL-SMOKE'
  )
LIMIT 1;

-- ============================================================
-- 4. Создать smoke experiment (скопировать настройки из HRA-EXP-V1)
-- ============================================================

INSERT INTO eval_prompt_experiments (
    id,
    dataset_id,
    experiment_code,
    prompt_a_text,
    prompt_b_text,
    judge_prompt_text,
    model_a,
    model_b,
    model_judge,
    temperature_a,
    temperature_b,
    temperature_judge,
    primary_metric,
    guard_metric,
    mde,
    status,
    created_at
)
SELECT
    gen_random_uuid(),
    d.id,
    'HRA-EXP-SMOKE',
    e.prompt_a_text,
    e.prompt_b_text,
    e.judge_prompt_text,
    e.model_a,
    e.model_b,
    e.model_judge,
    e.temperature_a,
    e.temperature_b,
    e.temperature_judge,
    e.primary_metric,
    e.guard_metric,
    e.mde,
    'draft',
    now()
FROM eval_prompt_datasets d
CROSS JOIN eval_prompt_experiments e
WHERE d.dataset_code = 'HRA-EVAL-SMOKE'
  AND e.experiment_code = 'HRA-EXP-V1'
  AND NOT EXISTS (
      SELECT 1 FROM eval_prompt_experiments WHERE experiment_code = 'HRA-EXP-SMOKE'
  );

-- ============================================================
-- 5. Verification queries
-- ============================================================

-- Проверка создания smoke dataset
SELECT
    'SMOKE DATASET' AS check_type,
    dataset_code,
    status,
    'OK' AS status_message
FROM eval_prompt_datasets
WHERE dataset_code = 'HRA-EVAL-SMOKE';

-- Проверка размера smoke dataset
SELECT
    'SMOKE SIZE' AS check_type,
    COUNT(DISTINCT c.id) AS cases_count,
    COUNT(cv.id) AS pairs_count,
    CASE
        WHEN COUNT(DISTINCT c.id) = 1 AND COUNT(cv.id) = 1 THEN 'OK'
        ELSE 'FAIL'
    END AS status_message
FROM eval_prompt_datasets d
JOIN eval_prompt_cases c ON c.dataset_id = d.id
JOIN eval_prompt_case_vacancies cv ON cv.case_id = c.id
WHERE d.dataset_code = 'HRA-EVAL-SMOKE';

-- Проверка создания smoke experiment
SELECT
    'SMOKE EXPERIMENT' AS check_type,
    e.experiment_code,
    d.dataset_code,
    e.model_a,
    e.model_b,
    e.model_judge,
    e.primary_metric,
    e.guard_metric,
    'OK' AS status_message
FROM eval_prompt_experiments e
JOIN eval_prompt_datasets d ON d.id = e.dataset_id
WHERE e.experiment_code = 'HRA-EXP-SMOKE';

-- Проверка пустых reference fields
SELECT
    'SMOKE REFERENCE FIELDS' AS check_type,
    COUNT(*) AS pairs_without_reference,
    CASE
        WHEN COUNT(*) = 1 THEN 'OK'
        ELSE 'FAIL'
    END AS status_message
FROM eval_prompt_datasets d
JOIN eval_prompt_cases c ON c.dataset_id = d.id
JOIN eval_prompt_case_vacancies cv ON cv.case_id = c.id
WHERE d.dataset_code = 'HRA-EVAL-SMOKE'
  AND cv.reference_score IS NULL;

-- ============================================================
-- 6. Итоговый статус
-- ============================================================

SELECT
    'SMOKE READY' AS final_status,
    (SELECT COUNT(*) FROM eval_prompt_datasets WHERE dataset_code = 'HRA-EVAL-SMOKE') AS datasets_created,
    (SELECT COUNT(DISTINCT c.id) FROM eval_prompt_cases c JOIN eval_prompt_datasets d ON c.dataset_id = d.id WHERE d.dataset_code = 'HRA-EVAL-SMOKE') AS cases_created,
    (SELECT COUNT(cv.id) FROM eval_prompt_case_vacancies cv JOIN eval_prompt_cases c ON cv.case_id = c.id JOIN eval_prompt_datasets d ON c.dataset_id = d.id WHERE d.dataset_code = 'HRA-EVAL-SMOKE') AS pairs_created,
    (SELECT COUNT(*) FROM eval_prompt_experiments WHERE experiment_code = 'HRA-EXP-SMOKE') AS experiments_created;