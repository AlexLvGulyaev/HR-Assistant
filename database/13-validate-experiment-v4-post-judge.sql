-- ============================================================
-- Experiment 004: Post-Judge validation
-- ============================================================
--
-- Purpose:
--   Run these checks AFTER the Judge run for HRA-EXP-V4 completes.
--   All queries should return zero/expected values.

-- ============================================================
-- 1. All 162 pairs have reference annotations
-- ============================================================

SELECT
    'Pairs without reference_score' AS check_name,
    COUNT(*) AS violation_count,
    (COUNT(*) = 0) AS passed
FROM eval_prompt_case_vacancies cv
JOIN eval_prompt_cases c ON cv.case_id = c.id
JOIN eval_prompt_datasets d ON c.dataset_id = d.id
WHERE d.dataset_code = 'HRA-EVAL-V4'
  AND cv.reference_score IS NULL;

SELECT
    'Pairs without reference_decision' AS check_name,
    COUNT(*) AS violation_count,
    (COUNT(*) = 0) AS passed
FROM eval_prompt_case_vacancies cv
JOIN eval_prompt_cases c ON cv.case_id = c.id
JOIN eval_prompt_datasets d ON c.dataset_id = d.id
WHERE d.dataset_code = 'HRA-EVAL-V4'
  AND cv.reference_decision IS NULL;

-- ============================================================
-- 2. All detailed reference_* fields are filled
-- ============================================================

SELECT
    'Pairs with NULL detailed reference fields' AS check_name,
    COUNT(*) AS violation_count,
    (COUNT(*) = 0) AS passed
FROM eval_prompt_case_vacancies cv
JOIN eval_prompt_cases c ON cv.case_id = c.id
JOIN eval_prompt_datasets d ON c.dataset_id = d.id
WHERE d.dataset_code = 'HRA-EVAL-V4'
  AND (
       cv.reference_role_score IS NULL
    OR cv.reference_skills_score IS NULL
    OR cv.reference_experience_score IS NULL
    OR cv.reference_conditions_score IS NULL
    OR cv.reference_reason IS NULL
    OR cv.reference_model IS NULL
    OR cv.reference_generated_at IS NULL
  );

-- ============================================================
-- 3. reference_raw_response_json is valid JSON
-- ============================================================

SELECT
    'Pairs with invalid reference_raw_response_json' AS check_name,
    COUNT(*) AS violation_count,
    (COUNT(*) = 0) AS passed
FROM eval_prompt_case_vacancies cv
JOIN eval_prompt_cases c ON cv.case_id = c.id
JOIN eval_prompt_datasets d ON c.dataset_id = d.id
WHERE d.dataset_code = 'HRA-EVAL-V4'
  AND cv.reference_raw_response_json IS NOT NULL
  AND jsonb_typeof(cv.reference_raw_response_json) != 'object';

-- ============================================================
-- 4. Score arithmetic
-- ============================================================

SELECT
    'Pairs with score arithmetic mismatch' AS check_name,
    COUNT(*) AS violation_count,
    (COUNT(*) = 0) AS passed
FROM eval_prompt_case_vacancies cv
JOIN eval_prompt_cases c ON cv.case_id = c.id
JOIN eval_prompt_datasets d ON c.dataset_id = d.id
WHERE d.dataset_code = 'HRA-EVAL-V4'
  AND cv.reference_score IS NOT NULL
  AND cv.reference_role_score IS NOT NULL
  AND cv.reference_skills_score IS NOT NULL
  AND cv.reference_experience_score IS NOT NULL
  AND cv.reference_conditions_score IS NOT NULL
  AND ABS(
        cv.reference_score
        - (cv.reference_role_score + cv.reference_skills_score + cv.reference_experience_score + cv.reference_conditions_score)
      ) > 0.01;

-- ============================================================
-- 5. Decision matches score threshold
-- ============================================================

SELECT
    'Pairs with score/decision mismatch' AS check_name,
    COUNT(*) AS violation_count,
    (COUNT(*) = 0) AS passed
FROM eval_prompt_case_vacancies cv
JOIN eval_prompt_cases c ON cv.case_id = c.id
JOIN eval_prompt_datasets d ON c.dataset_id = d.id
WHERE d.dataset_code = 'HRA-EVAL-V4'
  AND cv.reference_score IS NOT NULL
  AND cv.reference_decision IS NOT NULL
  AND (
       (cv.reference_score >= 60 AND cv.reference_decision != 'match')
    OR (cv.reference_score < 60 AND cv.reference_decision != 'no_match')
  );

-- ============================================================
-- 6. Distribution of decisions
-- ============================================================

SELECT
    reference_decision,
    COUNT(*) AS count,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS pct
FROM eval_prompt_case_vacancies cv
JOIN eval_prompt_cases c ON cv.case_id = c.id
JOIN eval_prompt_datasets d ON c.dataset_id = d.id
WHERE d.dataset_code = 'HRA-EVAL-V4'
  AND cv.reference_decision IS NOT NULL
GROUP BY reference_decision
ORDER BY reference_decision;

-- ============================================================
-- 7. New positive/borderline candidates: match rate
-- ============================================================

SELECT
    'New Cycle 4 candidates: match rate' AS check_name,
    SUM(CASE WHEN cv.reference_decision = 'match' THEN 1 ELSE 0 END) AS match_count,
    SUM(CASE WHEN cv.reference_decision = 'no_match' THEN 1 ELSE 0 END) AS no_match_count,
    COUNT(*) AS total,
    ROUND(100.0 * SUM(CASE WHEN cv.reference_decision = 'match' THEN 1 ELSE 0 END) / COUNT(*), 2) AS match_pct
FROM eval_prompt_case_vacancies cv
JOIN eval_prompt_cases c ON cv.case_id = c.id
JOIN eval_prompt_datasets d ON c.dataset_id = d.id
WHERE d.dataset_code = 'HRA-EVAL-V4'
  AND c.case_code BETWEEN 'HRA-EVAL-V2-000201' AND 'HRA-EVAL-V2-000213'
  AND cv.reference_decision IS NOT NULL;

-- ============================================================
-- 8. No extreme or impossible scores
-- ============================================================

SELECT
    'Pairs with score outside [0,100]' AS check_name,
    COUNT(*) AS violation_count,
    (COUNT(*) = 0) AS passed
FROM eval_prompt_case_vacancies cv
JOIN eval_prompt_cases c ON cv.case_id = c.id
JOIN eval_prompt_datasets d ON c.dataset_id = d.id
WHERE d.dataset_code = 'HRA-EVAL-V4'
  AND cv.reference_score IS NOT NULL
  AND (cv.reference_score < 0 OR cv.reference_score > 100);

-- ============================================================
-- 9. No duplicate pairs after annotation
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
    WHERE d.dataset_code = 'HRA-EVAL-V4'
    GROUP BY c.case_code, cv.vacancy_json->>'title'
    HAVING COUNT(*) > 1
) dup;

-- ============================================================
-- 10. Overall balance target
-- ============================================================

SELECT
    'Overall match percentage' AS check_name,
    ROUND(100.0 * SUM(CASE WHEN cv.reference_decision = 'match' THEN 1 ELSE 0 END) / COUNT(*), 2) AS match_pct,
    COUNT(*) AS total_pairs
FROM eval_prompt_case_vacancies cv
JOIN eval_prompt_cases c ON cv.case_id = c.id
JOIN eval_prompt_datasets d ON c.dataset_id = d.id
WHERE d.dataset_code = 'HRA-EVAL-V4'
  AND cv.reference_decision IS NOT NULL;

-- ============================================================
-- 11. Summary row for quick PASS/FAIL
-- ============================================================

SELECT
    'OVERALL POST-JUDGE VALIDATION' AS check_name,
    (
        (SELECT COUNT(*) FROM eval_prompt_case_vacancies cv
         JOIN eval_prompt_cases c ON cv.case_id = c.id
         JOIN eval_prompt_datasets d ON c.dataset_id = d.id
         WHERE d.dataset_code = 'HRA-EVAL-V4' AND cv.reference_score IS NULL) = 0
        AND
        (SELECT COUNT(*) FROM eval_prompt_case_vacancies cv
         JOIN eval_prompt_cases c ON cv.case_id = c.id
         JOIN eval_prompt_datasets d ON c.dataset_id = d.id
         WHERE d.dataset_code = 'HRA-EVAL-V4'
           AND cv.reference_decision IS NULL) = 0
        AND
        (SELECT COUNT(*) FROM eval_prompt_case_vacancies cv
         JOIN eval_prompt_cases c ON cv.case_id = c.id
         JOIN eval_prompt_datasets d ON c.dataset_id = d.id
         WHERE d.dataset_code = 'HRA-EVAL-V4'
           AND cv.reference_score IS NOT NULL
           AND cv.reference_decision IS NOT NULL
           AND (
                (cv.reference_score >= 60 AND cv.reference_decision != 'match')
             OR (cv.reference_score < 60 AND cv.reference_decision != 'no_match')
           )) = 0
    ) AS all_checks_passed;
