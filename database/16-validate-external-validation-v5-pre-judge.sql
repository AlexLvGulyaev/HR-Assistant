-- ============================================================
-- External Validation V5 — Pre-Judge Validation
-- ============================================================
--
-- Purpose:
--   Run before launching GPT-4o judge workflow for HRA-EXP-V5-EXT.
--   All checks should return PASS.
--
-- ============================================================

WITH checks AS (
    SELECT 'dataset_exists' AS check_name,
           (SELECT COUNT(*) FROM eval_prompt_datasets WHERE dataset_code = 'HRA-EVAL-V5-EXT') = 1 AS passed,
           'HRA-EVAL-V5-EXT must exist' AS description

    UNION ALL
    SELECT 'experiment_exists',
           (SELECT COUNT(*) FROM eval_prompt_experiments WHERE experiment_code = 'HRA-EXP-V5-EXT') = 1,
           'HRA-EXP-V5-EXT must exist'

    UNION ALL
    SELECT 'experiment_uses_gpt4o_judge',
           (SELECT model_judge FROM eval_prompt_experiments WHERE experiment_code = 'HRA-EXP-V5-EXT') = 'gpt-4o',
           'External judge must be gpt-4o'

    UNION ALL
    SELECT 'cases_count_34',
           (SELECT COUNT(*) FROM eval_prompt_cases c
            JOIN eval_prompt_datasets d ON c.dataset_id = d.id
            WHERE d.dataset_code = 'HRA-EVAL-V5-EXT') = 34,
           'Must have exactly 34 candidate cases'

    UNION ALL
    SELECT 'pairs_count_102',
           (SELECT COUNT(*) FROM eval_prompt_case_vacancies cv
            JOIN eval_prompt_cases c ON cv.case_id = c.id
            JOIN eval_prompt_datasets d ON c.dataset_id = d.id
            WHERE d.dataset_code = 'HRA-EVAL-V5-EXT') = 102,
           'Must have exactly 102 candidate-vacancy pairs'

    UNION ALL
    SELECT 'no_overlap_with_v4',
           NOT EXISTS (
               SELECT 1
               FROM eval_prompt_cases c5
               JOIN eval_prompt_datasets d5 ON c5.dataset_id = d5.id
               JOIN eval_prompt_cases c4 ON c4.case_code = c5.case_code
               JOIN eval_prompt_datasets d4 ON c4.dataset_id = d4.id
               WHERE d5.dataset_code = 'HRA-EVAL-V5-EXT'
                 AND d4.dataset_code = 'HRA-EVAL-V4'
           ),
           'External validation candidates must not overlap with HRA-EVAL-V4'

    UNION ALL
    SELECT 'all_vacancies_open',
           NOT EXISTS (
               SELECT 1
               FROM eval_prompt_case_vacancies cv
               JOIN eval_prompt_cases c ON cv.case_id = c.id
               JOIN eval_prompt_datasets d ON c.dataset_id = d.id
               JOIN vacancies v ON (cv.vacancy_json->>'id')::uuid = v.id
               WHERE d.dataset_code = 'HRA-EVAL-V5-EXT'
                 AND v.status != 'open'
           ),
           'All target vacancies must be open'

    UNION ALL
    SELECT 'case_type_distribution',
           (SELECT COUNT(*) FROM eval_prompt_cases c
            JOIN eval_prompt_datasets d ON c.dataset_id = d.id
            WHERE d.dataset_code = 'HRA-EVAL-V5-EXT'
              AND c.case_type = 'obvious_match') = 15
           AND
           (SELECT COUNT(*) FROM eval_prompt_cases c
            JOIN eval_prompt_datasets d ON c.dataset_id = d.id
            WHERE d.dataset_code = 'HRA-EVAL-V5-EXT'
              AND c.case_type = 'obvious_no_match') = 8
           AND
           (SELECT COUNT(*) FROM eval_prompt_cases c
            JOIN eval_prompt_datasets d ON c.dataset_id = d.id
            WHERE d.dataset_code = 'HRA-EVAL-V5-EXT'
              AND c.case_type = 'borderline') = 11,
           'Expected case type distribution: 15 obvious_match, 8 obvious_no_match, 11 borderline'
)
SELECT check_name, passed, description,
       CASE WHEN passed THEN 'PASS' ELSE 'FAIL' END AS status
FROM checks
ORDER BY check_name;
