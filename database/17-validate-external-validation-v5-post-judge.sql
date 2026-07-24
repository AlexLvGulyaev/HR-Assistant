-- ============================================================
-- External Validation V5 — Post-Judge Validation
-- ============================================================
--
-- Purpose:
--   Run after GPT-4o judge workflow completed for HRA-EXP-V5-EXT.
--   All checks should return PASS before extracting JSONL.
--
-- ============================================================

WITH checks AS (
    SELECT 'all_pairs_annotated' AS check_name,
           (SELECT COUNT(*) FROM eval_prompt_case_vacancies cv
            JOIN eval_prompt_cases c ON cv.case_id = c.id
            JOIN eval_prompt_datasets d ON c.dataset_id = d.id
            WHERE d.dataset_code = 'HRA-EVAL-V5-EXT'
              AND cv.reference_score IS NOT NULL
              AND cv.reference_decision IS NOT NULL) = 102 AS passed,
           'All 102 pairs must have reference_score and reference_decision from GPT-4o'

    UNION ALL
    SELECT 'valid_decisions',
           NOT EXISTS (
               SELECT 1
               FROM eval_prompt_case_vacancies cv
               JOIN eval_prompt_cases c ON cv.case_id = c.id
               JOIN eval_prompt_datasets d ON c.dataset_id = d.id
               WHERE d.dataset_code = 'HRA-EVAL-V5-EXT'
                 AND cv.reference_decision NOT IN ('match', 'no_match')
           ),
           'All reference_decision values must be match or no_match'

    UNION ALL
    SELECT 'valid_score_range',
           NOT EXISTS (
               SELECT 1
               FROM eval_prompt_case_vacancies cv
               JOIN eval_prompt_cases c ON cv.case_id = c.id
               JOIN eval_prompt_datasets d ON c.dataset_id = d.id
               WHERE d.dataset_code = 'HRA-EVAL-V5-EXT'
                 AND (cv.reference_score < 0 OR cv.reference_score > 100)
           ),
           'All reference_score values must be between 0 and 100'

    UNION ALL
    SELECT 'detailed_scores_present',
           (SELECT COUNT(*) FROM eval_prompt_case_vacancies cv
            JOIN eval_prompt_cases c ON cv.case_id = c.id
            JOIN eval_prompt_datasets d ON c.dataset_id = d.id
            WHERE d.dataset_code = 'HRA-EVAL-V5-EXT'
              AND cv.reference_role_score IS NOT NULL
              AND cv.reference_skills_score IS NOT NULL
              AND cv.reference_experience_score IS NOT NULL
              AND cv.reference_conditions_score IS NOT NULL) = 102,
           'All 102 pairs must have detailed role/skills/experience/conditions scores'

    UNION ALL
    SELECT 'judge_model_recorded',
           (SELECT COUNT(*) FROM eval_prompt_case_vacancies cv
            JOIN eval_prompt_cases c ON cv.case_id = c.id
            JOIN eval_prompt_datasets d ON c.dataset_id = d.id
            WHERE d.dataset_code = 'HRA-EVAL-V5-EXT'
              AND cv.reference_model = 'gpt-4o') = 102,
           'All reference annotations must be recorded as gpt-4o'
)
SELECT check_name, passed,
       CASE WHEN passed THEN 'PASS' ELSE 'FAIL' END AS status
FROM checks
ORDER BY check_name;
