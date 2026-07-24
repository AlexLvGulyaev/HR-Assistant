-- ============================================================
-- Experiment 003: Create dataset, cases, and experiment
-- ============================================================
--
-- Purpose:
--   1. Create new dataset HRA-EVAL-V3 containing:
--      - 30 existing candidates from HRA-EVAL-V2
--      - 11 new hard negative / edge case candidates from Stage 5
--   2. Register all 41 candidates in eval_prompt_cases.
--   3. Register all 3 target vacancies for every candidate
--      (41 candidates * 3 vacancies = 123 case-vacancy pairs).
--   4. Create experiment HRA-EXP-V3 pointing to HRA-EVAL-V3
--      with the same Judge configuration as HRA-EXP-V2.
--
-- Idempotency:
--   The script uses INSERT ... ON CONFLICT DO NOTHING where possible.
--   However, it is designed to be run ONCE on a clean Experiment 003 state.
--   Re-running after data was annotated would require a separate reset script.
--
-- Prerequisites:
--   - Schema 02-prompt-evaluation.sql applied.
--   - Schema 06-extend-judge-reference-fields.sql applied.
--   - Seed 03-seed-eval-dataset-v2.sql applied.
--   - Target vacancies exist in `vacancies` with status='open'.
-- ============================================================

-- ============================================================
-- 1. Create dataset HRA-EVAL-V3
-- ============================================================

INSERT INTO eval_prompt_datasets (
    id,
    dataset_code,
    name,
    description,
    status,
    created_at
)
VALUES (
    gen_random_uuid(),
    'HRA-EVAL-V3',
    'Matching Prompt Evaluation Dataset v3 - Experiment 003',
    'Датасет для Experiment 003. 30 кандидатов HRA-EVAL-V2 + 11 новых hard negative / edge case кандидатов. Каждый кандидат проверяется против 3 целевых вакансий: 41 * 3 = 123 пары.',
    'active',
    now()
)
ON CONFLICT (dataset_code) DO NOTHING;

-- ============================================================
-- 2. Copy existing 30 candidates from HRA-EVAL-V2 into HRA-EVAL-V3
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
    d3.id,
    c2.case_code,
    c2.case_type,
    c2.candidate_json,
    c2.notes || ' (copied from HRA-EVAL-V2 for Experiment 003)',
    now()
FROM eval_prompt_cases c2
JOIN eval_prompt_datasets d2 ON c2.dataset_id = d2.id
JOIN eval_prompt_datasets d3 ON d3.dataset_code = 'HRA-EVAL-V3'
WHERE d2.dataset_code = 'HRA-EVAL-V2'
  AND c2.case_code BETWEEN 'HRA-EVAL-V2-000001' AND 'HRA-EVAL-V2-000030'
ON CONFLICT (dataset_id, case_code) DO NOTHING;

-- ============================================================
-- 3. Insert 11 new hard negative / edge case candidates
-- ============================================================
--
-- Source: cases/hr-assistant/finetuning/Experiment_003_Report.md
-- Stage 5 specification (11 candidates, primary categories, splits).
--
-- case_code conventions:
--   HRA-EVAL-V2-000101 .. HRA-EVAL-V2-000111 are new candidates.
--   They share the dataset prefix with existing candidates to keep
--   the same case_code namespace as Experiment 002.

INSERT INTO eval_prompt_cases (id, dataset_id, case_code, case_type, candidate_json, notes, created_at)
SELECT gen_random_uuid(), d.id, 'HRA-EVAL-V2-000101', 'obvious_no_match',
    '{"full_name":"Врач Терапевт","city":"Москва","desired_position":"Врач-терапевт","experience_years":7,"skills":["Диагностика","Лечение","Пациенты","Медицинская документация","Коммуникация"],"salary_expectation":120000,"candidate_summary":"Врач-терапевт с 7-летним опытом работы в поликлинике. Веду приём пациентов, ставлю диагнозы, веду медицинскую документацию."}'::jsonb,
    'HN-1: Полностью нерелевантная профессия (non-IT в IT). Должен получать низкий score для всех трёх IT-вакансий.',
    now()
FROM eval_prompt_datasets d WHERE d.dataset_code = 'HRA-EVAL-V3';

INSERT INTO eval_prompt_cases (id, dataset_id, case_code, case_type, candidate_json, notes, created_at)
SELECT gen_random_uuid(), d.id, 'HRA-EVAL-V2-000102', 'borderline',
    '{"full_name":"Бизнес-аналитик","city":"Москва","desired_position":"Бизнес-аналитик","experience_years":3,"skills":["BPMN","UML","Требования","Бизнес-процессы","Аналитика"],"salary_expectation":160000,"candidate_summary":"Бизнес-аналитик с 3-летним опытом. Описываю бизнес-процессы, формирую требования, работаю с BPMN и UML."}'::jsonb,
    'HN-2 / EC-3: Смежная роль без обязательных hard skills; формально похожее название «аналитик».',
    now()
FROM eval_prompt_datasets d WHERE d.dataset_code = 'HRA-EVAL-V3';

INSERT INTO eval_prompt_cases (id, dataset_id, case_code, case_type, candidate_json, notes, created_at)
SELECT gen_random_uuid(), d.id, 'HRA-EVAL-V2-000103', 'borderline',
    '{"full_name":"Data Analyst","city":"Москва","desired_position":"Data Analyst","experience_years":4,"skills":["SQL","Python","BI","Визуализация данных","Excel"],"salary_expectation":170000,"candidate_summary":"Data analyst с опытом SQL, Python и BI-инструментов. Строю дашборды, анализирую метрики, визуализирую данные."}'::jsonb,
    'HN-3 / EC-3: Лексическое совпадение «аналитик» без совпадения компетенций prompt engineering / n8n / LLM.',
    now()
FROM eval_prompt_datasets d WHERE d.dataset_code = 'HRA-EVAL-V3';

INSERT INTO eval_prompt_cases (id, dataset_id, case_code, case_type, candidate_json, notes, created_at)
SELECT gen_random_uuid(), d.id, 'HRA-EVAL-V2-000104', 'obvious_no_match',
    '{"full_name":"Python Backend Developer","city":"Москва","desired_position":"Python Backend Developer","experience_years":5,"skills":["Python","Backend","API","Django","PostgreSQL"],"salary_expectation":250000,"candidate_summary":"Сильный Python backend-разработчик с 5-летним опытом. Проектирую API и серверную архитектуру."}'::jsonb,
    'HN-4: Сильный профиль в нерелевантной специализации (backend разработка вместо prompt engineering / автоматизации).',
    now()
FROM eval_prompt_datasets d WHERE d.dataset_code = 'HRA-EVAL-V3';

INSERT INTO eval_prompt_cases (id, dataset_id, case_code, case_type, candidate_json, notes, created_at)
SELECT gen_random_uuid(), d.id, 'HRA-EVAL-V2-000105', 'obvious_no_match',
    '{"full_name":"Копирайтер","city":"Москва","desired_position":"Копирайтер","experience_years":3,"skills":["Копирайтинг","Тексты","JSON","Редактура","Грамотность"],"salary_expectation":130000,"candidate_summary":"Копирайтер с опытом написания текстов и базовым знанием JSON из онлайн-курсов."}'::jsonb,
    'HN-5: Одиночное совпадение навыка (JSON) без основного профиля в prompt engineering / LLM / автоматизации.',
    now()
FROM eval_prompt_datasets d WHERE d.dataset_code = 'HRA-EVAL-V3';

INSERT INTO eval_prompt_cases (id, dataset_id, case_code, case_type, candidate_json, notes, created_at)
SELECT gen_random_uuid(), d.id, 'HRA-EVAL-V2-000106', 'obvious_no_match',
    '{"full_name":"Коммьюнити-менеджер","city":"Москва","desired_position":"Community Manager","experience_years":4,"skills":["Коммуникация","Организация мероприятий","SMM","Нетворкинг","Soft skills"],"salary_expectation":140000,"candidate_summary":"Коммьюнити-менеджер с сильными коммуникационными навыками и опытом организации мероприятий."}'::jsonb,
    'HN-8: Дисбаланс soft skills и hard skills — сильные коммуникации, но отсутствие технической базы.',
    now()
FROM eval_prompt_datasets d WHERE d.dataset_code = 'HRA-EVAL-V3';

INSERT INTO eval_prompt_cases (id, dataset_id, case_code, case_type, candidate_json, notes, created_at)
SELECT gen_random_uuid(), d.id, 'HRA-EVAL-V2-000107', 'borderline',
    '{"full_name":"Middle AI Automation Specialist","city":"Москва","desired_position":"AI Automation Specialist","experience_years":2,"skills":["Prompt engineering","n8n","API","JSON","LLM"],"salary_expectation":300000,"candidate_summary":"Middle AI-автоматизатор с частичным набором навыков. Знаю prompt engineering, n8n, API, JSON и LLM."}'::jsonb,
    'EC-1 / EC-4: Пограничный кандидат с частичным соответствием по навыкам и критичным несоответствием по зарплате/условиям.',
    now()
FROM eval_prompt_datasets d WHERE d.dataset_code = 'HRA-EVAL-V3';

INSERT INTO eval_prompt_cases (id, dataset_id, case_code, case_type, candidate_json, notes, created_at)
SELECT gen_random_uuid(), d.id, 'HRA-EVAL-V2-000108', 'obvious_no_match',
    '{"full_name":"Junior Python Developer","city":"Москва","desired_position":"Junior Python Developer","experience_years":1,"skills":["Python","Базовые скрипты","Git","SQL","REST API"],"salary_expectation":100000,"candidate_summary":"Junior Python-разработчик с 1-летним опытом. Пишу базовые скрипты, изучаю API."}'::jsonb,
    'HN-6: Разница в уровне опыта — junior кандидат на роли, требующие senior-level навыков.',
    now()
FROM eval_prompt_datasets d WHERE d.dataset_code = 'HRA-EVAL-V3';

INSERT INTO eval_prompt_cases (id, dataset_id, case_code, case_type, candidate_json, notes, created_at)
SELECT gen_random_uuid(), d.id, 'HRA-EVAL-V2-000109', 'borderline',
    '{"full_name":"Пограничный аналитик","city":"Москва","desired_position":"Системный аналитик","experience_years":3,"skills":["SQL","BPMN","REST API","Аналитика"],"salary_expectation":200000,"candidate_summary":"Системный аналитик с 3-летним опытом. Часть hard skills вакансий присутствует, но не полный профиль."}'::jsonb,
    'EC-1: Пограничный кандидат с частичным соответствием по роли/навыкам; score около порога 60.',
    now()
FROM eval_prompt_datasets d WHERE d.dataset_code = 'HRA-EVAL-V3';

INSERT INTO eval_prompt_cases (id, dataset_id, case_code, case_type, candidate_json, notes, created_at)
SELECT gen_random_uuid(), d.id, 'HRA-EVAL-V2-000110', 'obvious_no_match',
    '{"full_name":"IT Project Manager","city":"Москва","desired_position":"IT Project Manager","experience_years":8,"skills":["Управление командами","Проекты","Стейкхолдерами","Agile","Jira"],"salary_expectation":280000,"candidate_summary":"IT-руководитель / project manager с управленческим опытом. Управляю командами, проектами и стейкхолдерами."}'::jsonb,
    'HN-7: Разница в функциональной роли — управленческий опыт для исполнительских ролей prompt engineering / системного анализа.',
    now()
FROM eval_prompt_datasets d WHERE d.dataset_code = 'HRA-EVAL-V3';

INSERT INTO eval_prompt_cases (id, dataset_id, case_code, case_type, candidate_json, notes, created_at)
SELECT gen_random_uuid(), d.id, 'HRA-EVAL-V2-000111', 'obvious_no_match',
    '{"full_name":"Сильный бизнес-аналитик","city":"Санкт-Петербург","desired_position":"Senior Business Analyst","experience_years":6,"skills":["BPMN","UML","SQL","Требования","Аналитика"],"salary_expectation":350000,"candidate_summary":"Сильный бизнес-аналитик с 6-летним опытом. Серьёзный профиль, но в смежной области; зарплатные ожидания выше бюджета."}'::jsonb,
    'EC-4 / EC-3: Сильный профиль в смежной области с критичным несоответствием по условиям и формально похожим названием.',
    now()
FROM eval_prompt_datasets d WHERE d.dataset_code = 'HRA-EVAL-V3';

-- ============================================================
-- 4. Create case-vacancy pairs for ALL 41 candidates
--    Cross join with the 3 target open vacancies.
-- ============================================================

INSERT INTO eval_prompt_case_vacancies (
    id,
    case_id,
    vacancy_json,
    created_at
)
SELECT
    gen_random_uuid(),
    c.id,
    jsonb_build_object(
        'id', v.id::text,
        'title', v.title,
        'description', v.description,
        'requirements', v.requirements,
        'salary_min', v.salary_min,
        'salary_max', v.salary_max
    ),
    now()
FROM eval_prompt_cases c
CROSS JOIN vacancies v
JOIN eval_prompt_datasets d ON c.dataset_id = d.id
WHERE d.dataset_code = 'HRA-EVAL-V3'
  AND v.status = 'open'
ON CONFLICT DO NOTHING;

-- ============================================================
-- 5. Create experiment HRA-EXP-V3 as a copy of HRA-EXP-V2
-- ============================================================
--
-- The Judge prompt, model, temperature, and output contract are
-- intentionally kept identical to Experiment 002.

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
    d3.id,
    'HRA-EXP-V3',
    e2.prompt_a_text,
    e2.prompt_b_text,
    e2.judge_prompt_text,
    e2.model_a,
    e2.model_b,
    e2.model_judge,
    e2.temperature_a,
    e2.temperature_b,
    e2.temperature_judge,
    e2.primary_metric,
    e2.guard_metric,
    e2.mde,
    'draft',
    now()
FROM eval_prompt_experiments e2
JOIN eval_prompt_datasets d2 ON e2.dataset_id = d2.id
JOIN eval_prompt_datasets d3 ON d3.dataset_code = 'HRA-EVAL-V3'
WHERE d2.dataset_code = 'HRA-EVAL-V2'
  AND e2.experiment_code = 'HRA-EXP-V2'
ON CONFLICT (experiment_code) DO NOTHING;

-- ============================================================
-- 6. Verification queries
-- ============================================================

SELECT
    'Experiment 003 created' AS status,
    (SELECT COUNT(*) FROM eval_prompt_datasets WHERE dataset_code = 'HRA-EVAL-V3') AS datasets,
    (SELECT COUNT(*) FROM eval_prompt_cases c
     JOIN eval_prompt_datasets d ON c.dataset_id = d.id
     WHERE d.dataset_code = 'HRA-EVAL-V3') AS cases_count,
    (SELECT COUNT(*) FROM eval_prompt_case_vacancies cv
     JOIN eval_prompt_cases c ON cv.case_id = c.id
     JOIN eval_prompt_datasets d ON c.dataset_id = d.id
     WHERE d.dataset_code = 'HRA-EVAL-V3') AS case_vacancies_count,
    (SELECT COUNT(*) FROM eval_prompt_experiments WHERE experiment_code = 'HRA-EXP-V3') AS experiments;

-- Distribution by case_type
SELECT
    c.case_type,
    COUNT(DISTINCT c.id) AS cases_count,
    COUNT(cv.id) AS pairs_count
FROM eval_prompt_cases c
JOIN eval_prompt_datasets d ON c.dataset_id = d.id
LEFT JOIN eval_prompt_case_vacancies cv ON cv.case_id = c.id
WHERE d.dataset_code = 'HRA-EVAL-V3'
GROUP BY c.case_type
ORDER BY c.case_type;

-- Vacancies used
SELECT DISTINCT
    vacancy_json->>'id' AS vacancy_id,
    vacancy_json->>'title' AS title
FROM eval_prompt_case_vacancies cv
JOIN eval_prompt_cases c ON cv.case_id = c.id
JOIN eval_prompt_datasets d ON c.dataset_id = d.id
WHERE d.dataset_code = 'HRA-EVAL-V3';
