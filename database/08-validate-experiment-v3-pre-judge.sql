-- ============================================================
-- Experiment 003: Pre-Judge validation
-- ============================================================
--
-- Purpose:
--   Run these checks BEFORE starting the Judge run for HRA-EXP-V3.
--   All queries should return zero/expected values.
--   If any query returns an unexpected result, do NOT start Judge.

-- ============================================================
-- 1. Dataset and experiment exist
-- ============================================================

SELECT
    'Dataset exists' AS check_name,
    COUNT(*) AS expected_1
FROM eval_prompt_datasets
WHERE dataset_code = 'HRA-EVAL-V3';

SELECT
    'Experiment exists' AS check_name,
    COUNT(*) AS expected_1
FROM eval_prompt_experiments
WHERE experiment_code = 'HRA-EXP-V3';

-- ============================================================
-- 2. Exactly 41 candidates registered
-- ============================================================

SELECT
    'Candidate count' AS check_name,
    COUNT(*) AS actual_count,
    41 AS expected_count,
    (COUNT(*) = 41) AS passed
FROM eval_prompt_cases c
JOIN eval_prompt_datasets d ON c.dataset_id = d.id
WHERE d.dataset_code = 'HRA-EVAL-V3';

-- ============================================================
-- 3. Exactly 123 candidate-vacancy pairs registered
-- ============================================================

SELECT
    'Pair count' AS check_name,
    COUNT(*) AS actual_count,
    123 AS expected_count,
    (COUNT(*) = 123) AS passed
FROM eval_prompt_case_vacancies cv
JOIN eval_prompt_cases c ON cv.case_id = c.id
JOIN eval_prompt_datasets d ON c.dataset_id = d.id
WHERE d.dataset_code = 'HRA-EVAL-V3';

-- ============================================================
-- 4. Every candidate has exactly 3 vacancies
-- ============================================================

SELECT
    'Candidates without exactly 3 vacancies' AS check_name,
    COUNT(*) AS violation_count,
    (COUNT(*) = 0) AS passed
FROM (
    SELECT c.id
    FROM eval_prompt_cases c
    JOIN eval_prompt_datasets d ON c.dataset_id = d.id
    LEFT JOIN eval_prompt_case_vacancies cv ON cv.case_id = c.id
    WHERE d.dataset_code = 'HRA-EVAL-V3'
    GROUP BY c.id
    HAVING COUNT(cv.id) != 3
) bad;

-- ============================================================
-- 5. No duplicate case_code within HRA-EVAL-V3
-- ============================================================

SELECT
    'Duplicate case_code' AS check_name,
    COUNT(*) AS violation_count,
    (COUNT(*) = 0) AS passed
FROM (
    SELECT case_code
    FROM eval_prompt_cases c
    JOIN eval_prompt_datasets d ON c.dataset_id = d.id
    WHERE d.dataset_code = 'HRA-EVAL-V3'
    GROUP BY case_code
    HAVING COUNT(*) > 1
) dup;

-- ============================================================
-- 6. No duplicate case-vacancy pairs (same case + same vacancy title)
-- ============================================================

SELECT
    'Duplicate case-vacancy pairs' AS check_name,
    COUNT(*) AS violation_count,
    (COUNT(*) = 0) AS passed
FROM (
    SELECT c.case_code, cv.vacancy_json->>'title' AS title
    FROM eval_prompt_case_vacancies cv
    JOIN eval_prompt_cases c ON cv.case_id = c.id
    JOIN eval_prompt_datasets d ON c.dataset_id = d.id
    WHERE d.dataset_code = 'HRA-EVAL-V3'
    GROUP BY c.case_code, cv.vacancy_json->>'title'
    HAVING COUNT(*) > 1
) dup;

-- ============================================================
-- 7. All pairs have required non-NULL fields (candidate_json, vacancy_json)
-- ============================================================

SELECT
    'Pairs with NULL candidate/vacancy JSON' AS check_name,
    COUNT(*) AS violation_count,
    (COUNT(*) = 0) AS passed
FROM eval_prompt_case_vacancies cv
JOIN eval_prompt_cases c ON cv.case_id = c.id
JOIN eval_prompt_datasets d ON c.dataset_id = d.id
WHERE d.dataset_code = 'HRA-EVAL-V3'
  AND (c.candidate_json IS NULL OR cv.vacancy_json IS NULL);

-- ============================================================
-- 8. Exactly the 3 target vacancies are used
-- ============================================================

SELECT
    'Vacancies used' AS check_name,
    COUNT(DISTINCT cv.vacancy_json->>'title') AS distinct_vacancy_count,
    (COUNT(DISTINCT cv.vacancy_json->>'title') = 3) AS passed
FROM eval_prompt_case_vacancies cv
JOIN eval_prompt_cases c ON cv.case_id = c.id
JOIN eval_prompt_datasets d ON c.dataset_id = d.id
WHERE d.dataset_code = 'HRA-EVAL-V3';

-- List the actual titles for manual review
SELECT DISTINCT
    cv.vacancy_json->>'title' AS vacancy_title
FROM eval_prompt_case_vacancies cv
JOIN eval_prompt_cases c ON cv.case_id = c.id
JOIN eval_prompt_datasets d ON c.dataset_id = d.id
WHERE d.dataset_code = 'HRA-EVAL-V3'
ORDER BY vacancy_title;

-- ============================================================
-- 9. No orphan pairs (case_vacancies without valid case)
-- ============================================================

SELECT
    'Orphan case_vacancies' AS check_name,
    COUNT(*) AS violation_count,
    (COUNT(*) = 0) AS passed
FROM eval_prompt_case_vacancies cv
LEFT JOIN eval_prompt_cases c ON cv.case_id = c.id
WHERE c.id IS NULL;

-- ============================================================
-- 10. No orphan cases (cases without dataset)
-- ============================================================

SELECT
    'Orphan cases' AS check_name,
    COUNT(*) AS violation_count,
    (COUNT(*) = 0) AS passed
FROM eval_prompt_cases c
LEFT JOIN eval_prompt_datasets d ON c.dataset_id = d.id
WHERE d.id IS NULL;

-- ============================================================
-- 11. Experiment uses correct dataset and Judge config matches HRA-EXP-V2
-- ============================================================

SELECT
    'Experiment config matches HRA-EXP-V2' AS check_name,
    e3.experiment_code,
    e3.model_judge,
    e3.temperature_judge,
    (e3.model_judge = e2.model_judge
     AND e3.temperature_judge = e2.temperature_judge
     AND e3.judge_prompt_text = e2.judge_prompt_text) AS config_matches
FROM eval_prompt_experiments e3
JOIN eval_prompt_experiments e2
    ON e2.experiment_code = 'HRA-EXP-V2'
WHERE e3.experiment_code = 'HRA-EXP-V3';

-- ============================================================
-- 12. Summary row for quick PASS/FAIL
-- ============================================================

SELECT
    'OVERALL PRE-JUDGE VALIDATION' AS check_name,
    (
        (SELECT COUNT(*) FROM eval_prompt_datasets WHERE dataset_code = 'HRA-EVAL-V3') = 1
        AND (SELECT COUNT(*) FROM eval_prompt_experiments WHERE experiment_code = 'HRA-EXP-V3') = 1
        AND (SELECT COUNT(*) FROM eval_prompt_cases c JOIN eval_prompt_datasets d ON c.dataset_id = d.id WHERE d.dataset_code = 'HRA-EVAL-V3') = 41
        AND (SELECT COUNT(*) FROM eval_prompt_case_vacancies cv JOIN eval_prompt_cases c ON cv.case_id = c.id JOIN eval_prompt_datasets d ON c.dataset_id = d.id WHERE d.dataset_code = 'HRA-EVAL-V3') = 123
        AND (SELECT COUNT(*) FROM (
            SELECT c.id
            FROM eval_prompt_cases c
            JOIN eval_prompt_datasets d ON c.dataset_id = d.id
            LEFT JOIN eval_prompt_case_vacancies cv ON cv.case_id = c.id
            WHERE d.dataset_code = 'HRA-EVAL-V3'
            GROUP BY c.id
            HAVING COUNT(cv.id) != 3
        ) bad) = 0
    ) AS all_checks_passed;
