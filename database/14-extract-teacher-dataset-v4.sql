-- ============================================================
-- Experiment 004: Quick extraction verification query
-- ============================================================
--
-- Purpose:
--   After the Judge run completes and before running the Python
--   extract_teacher_dataset.py, verify that all 162 pairs are
--   ready for export.

SELECT
    'Ready for extraction' AS status,
    COUNT(*) AS total_pairs,
    COUNT(*) FILTER (WHERE reference_score IS NOT NULL) AS annotated_pairs,
    COUNT(*) FILTER (WHERE reference_score IS NULL) AS missing_pairs,
    COUNT(*) FILTER (WHERE reference_decision IS NOT NULL) AS with_decision,
    COUNT(*) FILTER (WHERE reference_role_score IS NOT NULL) AS with_role_score,
    COUNT(*) FILTER (WHERE reference_skills_score IS NOT NULL) AS with_skills_score,
    COUNT(*) FILTER (WHERE reference_experience_score IS NOT NULL) AS with_experience_score,
    COUNT(*) FILTER (WHERE reference_conditions_score IS NOT NULL) AS with_conditions_score
FROM eval_prompt_case_vacancies cv
JOIN eval_prompt_cases c ON cv.case_id = c.id
JOIN eval_prompt_datasets d ON c.dataset_id = d.id
WHERE d.dataset_code = 'HRA-EVAL-V4';
