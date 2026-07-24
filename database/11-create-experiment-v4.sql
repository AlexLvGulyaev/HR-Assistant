-- ============================================================
-- Experiment 004: Create balanced dataset with positive/borderline examples
-- ============================================================
--
-- Purpose:
--   1. Create new dataset HRA-EVAL-V4 containing:
--      - 41 existing candidates from HRA-EVAL-V3 (30 original + 11 hard negatives)
--      - 13 new positive/borderline candidates from Cycle 4 Stage 2
--   2. Register all 54 candidates in eval_prompt_cases.
--   3. Register all 3 target vacancies for every candidate
--      (54 candidates * 3 vacancies = 162 case-vacancy pairs).
--   4. Create experiment HRA-EXP-V4 pointing to HRA-EVAL-V4
--      with the same Judge configuration as HRA-EXP-V3.
--
-- Idempotency:
--   The script uses INSERT ... ON CONFLICT DO NOTHING where possible.
--   Designed to be run ONCE on a clean Experiment 004 state.
--
-- Prerequisites:
--   - Schema 02-prompt-evaluation.sql applied.
--   - Schema 06-extend-judge-reference-fields.sql applied.
--   - HRA-EVAL-V3 and HRA-EXP-V3 exist.
--   - Target vacancies exist in `vacancies` with status='open'.
-- ============================================================

-- ============================================================
-- 1. Create dataset HRA-EVAL-V4
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
    'HRA-EVAL-V4',
    'Matching Prompt Evaluation Dataset v4 - Experiment 004',
    'Датасет для Experiment 004. 41 кандидат HRA-EVAL-V3 + 13 новых positive/borderline кандидатов. Каждый кандидат проверяется против 3 целевых вакансий: 54 * 3 = 162 пары.',
    'active',
    now()
)
ON CONFLICT (dataset_code) DO NOTHING;

-- ============================================================
-- 2. Copy existing 41 candidates from HRA-EVAL-V3 into HRA-EVAL-V4
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
    d4.id,
    c3.case_code,
    c3.case_type,
    c3.candidate_json,
    c3.notes || ' (copied from HRA-EVAL-V3 for Experiment 004)',
    now()
FROM eval_prompt_cases c3
JOIN eval_prompt_datasets d3 ON c3.dataset_id = d3.id
JOIN eval_prompt_datasets d4 ON d4.dataset_code = 'HRA-EVAL-V4'
WHERE d3.dataset_code = 'HRA-EVAL-V3'
ON CONFLICT (dataset_id, case_code) DO NOTHING;

-- ============================================================
-- 3. Insert 13 new positive/borderline candidates
-- ============================================================
--
-- Source: cases/hr-assistant/finetuning/Experiment_004_Report.md Stage 2.
-- case_code conventions: HRA-EVAL-V2-000201 .. HRA-EVAL-V2-000213.

INSERT INTO eval_prompt_cases (id, dataset_id, case_code, case_type, candidate_json, notes, created_at)
SELECT gen_random_uuid(), d.id, 'HRA-EVAL-V2-000201', 'obvious_match',
    '{"full_name":"Сергей Системный","city":"Москва","desired_position":"Системный аналитик","experience_years":6,"skills":["SQL","BPMN","REST API","UML","Аналитика","Постановка задач разработчикам","Agile"],"salary_expectation":190000,"candidate_summary":"Senior системный аналитик с 6-летним опытом. Проектирую интеграции, пишу технические задания, постанавливаю задачи разработчикам, владею SQL, BPMN, REST API, UML."}'::jsonb,
    'Cycle 4 positive: senior системный аналитик. Исправляет false negative HRA-EVAL-V2-000010/Системный аналитик.',
    now()
FROM eval_prompt_datasets d WHERE d.dataset_code = 'HRA-EVAL-V4';

INSERT INTO eval_prompt_cases (id, dataset_id, case_code, case_type, candidate_json, notes, created_at)
SELECT gen_random_uuid(), d.id, 'HRA-EVAL-V2-000202', 'obvious_match',
    '{"full_name":"Алексей Автоматизатор","city":"Москва","desired_position":"AI Automation Specialist","experience_years":4,"skills":["Prompt engineering","n8n","LLM","REST API","JSON","Python","Автоматизация бизнес-процессов"],"salary_expectation":210000,"candidate_summary":"Senior AI Automation Specialist с 4-летним опытом. Проектирую AI-пайплайны, интегрирую LLM через API, автоматизирую бизнес-процессы в n8n."}'::jsonb,
    'Cycle 4 positive: strong AI Automation Specialist. Добавляет high-quality positive пример для Prompt Engineer.',
    now()
FROM eval_prompt_datasets d WHERE d.dataset_code = 'HRA-EVAL-V4';

INSERT INTO eval_prompt_cases (id, dataset_id, case_code, case_type, candidate_json, notes, created_at)
SELECT gen_random_uuid(), d.id, 'HRA-EVAL-V2-000203', 'obvious_match',
    '{"full_name":"Мария Разметчик","city":"Москва","desired_position":"Data Annotation Lead","experience_years":3,"skills":["Разметка данных","Инструкции для ML","Внимательность","Грамотность","Python basics","QA"],"salary_expectation":130000,"candidate_summary":"Data Annotation Lead с 3-летним опытом разметки данных для ML-проектов. Составляю инструкции, контролирую качество разметки, работаю с текстовыми датасетами."}'::jsonb,
    'Cycle 4 positive: data annotation lead. Исправляет false negative HRA-EVAL-V2-000030/Специалист по разметке данных.',
    now()
FROM eval_prompt_datasets d WHERE d.dataset_code = 'HRA-EVAL-V4';

INSERT INTO eval_prompt_cases (id, dataset_id, case_code, case_type, candidate_json, notes, created_at)
SELECT gen_random_uuid(), d.id, 'HRA-EVAL-V2-000204', 'borderline',
    '{"full_name":"Борис Бизнес-аналитик","city":"Москва","desired_position":"Бизнес-аналитик","experience_years":4,"skills":["BPMN","UML","Требования","Бизнес-процессы","n8n basics","REST API basics"],"salary_expectation":170000,"candidate_summary":"Бизнес-аналитик с 4-летним опытом. Описываю процессы, собираю требования, работаю с BPMN/UML, есть базовый опыт n8n и API."}'::jsonb,
    'Cycle 4 borderline: BA с базовыми навыками автоматизации. Учит границе между BA и Prompt Engineer/системным аналитиком.',
    now()
FROM eval_prompt_datasets d WHERE d.dataset_code = 'HRA-EVAL-V4';

INSERT INTO eval_prompt_cases (id, dataset_id, case_code, case_type, candidate_json, notes, created_at)
SELECT gen_random_uuid(), d.id, 'HRA-EVAL-V2-000205', 'borderline',
    '{"full_name":"Кирилл QA","city":"Москва","desired_position":"QA Engineer","experience_years":3,"skills":["Python","API testing","Тест-кейсы","Postman","SQL basics","Автоматизация тестирования"],"salary_expectation":160000,"candidate_summary":"QA engineer с 3-летним опытом. Пишу тест-кейсы, тестирую API, знаю Python и SQL на базовом уровне."}'::jsonb,
    'Cycle 4 borderline: QA engineer. Смежная IT-роль без полного профиля Prompt Engineer.',
    now()
FROM eval_prompt_datasets d WHERE d.dataset_code = 'HRA-EVAL-V4';

INSERT INTO eval_prompt_cases (id, dataset_id, case_code, case_type, candidate_json, notes, created_at)
SELECT gen_random_uuid(), d.id, 'HRA-EVAL-V2-000206', 'borderline',
    '{"full_name":"Елена Техписатель","city":"Москва","desired_position":"Technical Writer","experience_years":3,"skills":["Техническая документация","Инструкции","Python basics","Внимательность","Грамотность","Markdown"],"salary_expectation":140000,"candidate_summary":"Technical writer с 3-летним опытом. Пишу инструкции и техническую документацию, знаю Python на базовом уровне, внимательна к деталям."}'::jsonb,
    'Cycle 4 borderline: technical writer. Граница между документацией и разметкой данных для ML.',
    now()
FROM eval_prompt_datasets d WHERE d.dataset_code = 'HRA-EVAL-V4';

INSERT INTO eval_prompt_cases (id, dataset_id, case_code, case_type, candidate_json, notes, created_at)
SELECT gen_random_uuid(), d.id, 'HRA-EVAL-V2-000207', 'obvious_match',
    '{"full_name":"Дмитрий ML-инженер","city":"Москва","desired_position":"ML Engineer","experience_years":2,"skills":["LLM","Fine-tuning","Prompt engineering","Python","PyTorch","HuggingFace"],"salary_expectation":180000,"candidate_summary":"ML engineer с 2-летним опытом. Работаю с LLM, fine-tuning, prompt engineering, Python и PyTorch."}'::jsonb,
    'Cycle 4 positive: ML engineer с LLM опытом. Дополнительный strong positive пример для Prompt Engineer.',
    now()
FROM eval_prompt_datasets d WHERE d.dataset_code = 'HRA-EVAL-V4';

INSERT INTO eval_prompt_cases (id, dataset_id, case_code, case_type, candidate_json, notes, created_at)
SELECT gen_random_uuid(), d.id, 'HRA-EVAL-V2-000208', 'obvious_match',
    '{"full_name":"Игорь Аналитик","city":"Москва","desired_position":"Системный аналитик","experience_years":4,"skills":["SQL","BPMN","REST API","UML","Аналитика","Документирование"],"salary_expectation":175000,"candidate_summary":"Middle системный аналитик с 4-летним опытом. Проектирую API-интеграции, пишу SQL-запросы, работаю с BPMN и UML."}'::jsonb,
    'Cycle 4 positive (validation): middle системный аналитик. Контроль обобщения recall.',
    now()
FROM eval_prompt_datasets d WHERE d.dataset_code = 'HRA-EVAL-V4';

INSERT INTO eval_prompt_cases (id, dataset_id, case_code, case_type, candidate_json, notes, created_at)
SELECT gen_random_uuid(), d.id, 'HRA-EVAL-V2-000209', 'borderline',
    '{"full_name":"Ольга Дата-аналитик","city":"Москва","desired_position":"Data Analyst","experience_years":3,"skills":["SQL","Python","BI","Prompt engineering course","API basics"],"salary_expectation":160000,"candidate_summary":"Data analyst с 3-летним опытом. Анализирую данные в SQL/Python/BI, прошла курс prompt engineering, есть базовый опыт API."}'::jsonb,
    'Cycle 4 borderline (validation): data analyst с курсом prompt engineering. Контроль границы Prompt Engineer.',
    now()
FROM eval_prompt_datasets d WHERE d.dataset_code = 'HRA-EVAL-V4';

INSERT INTO eval_prompt_cases (id, dataset_id, case_code, case_type, candidate_json, notes, created_at)
SELECT gen_random_uuid(), d.id, 'HRA-EVAL-V2-000210', 'obvious_match',
    '{"full_name":"Анна Модератор","city":"Москва","desired_position":"Content Moderator","experience_years":3,"skills":["Модерация контента","Инструкции для AI","Разметка данных","Внимательность","Грамотность","QA"],"salary_expectation":120000,"candidate_summary":"Content moderator с 3-летним опытом. Размечаю контент для AI-систем, составляю инструкции, контролирую качество."}'::jsonb,
    'Cycle 4 positive (validation): content moderator с опытом разметки для AI. Контроль обобщения на разметку данных.',
    now()
FROM eval_prompt_datasets d WHERE d.dataset_code = 'HRA-EVAL-V4';

INSERT INTO eval_prompt_cases (id, dataset_id, case_code, case_type, candidate_json, notes, created_at)
SELECT gen_random_uuid(), d.id, 'HRA-EVAL-V2-000211', 'obvious_match',
    '{"full_name":"Павел Системный","city":"Москва","desired_position":"Системный аналитик","experience_years":4,"skills":["SQL","BPMN","REST API","UML","Аналитика","Постановка задач"],"salary_expectation":180000,"candidate_summary":"Системный аналитик с 4-летним опытом. Проектирую бизнес-процессы, пишу ТЗ, постанавливаю задачи разработчикам."}'::jsonb,
    'Cycle 4 positive (test): системный аналитик. Прямой тест recall на genuine match.',
    now()
FROM eval_prompt_datasets d WHERE d.dataset_code = 'HRA-EVAL-V4';

INSERT INTO eval_prompt_cases (id, dataset_id, case_code, case_type, candidate_json, notes, created_at)
SELECT gen_random_uuid(), d.id, 'HRA-EVAL-V2-000212', 'obvious_match',
    '{"full_name":"Роман Энтузиаст","city":"Москва","desired_position":"AI Automation Enthusiast","experience_years":2,"skills":["n8n","LLM","Prompt engineering","REST API","JSON","Python"],"salary_expectation":150000,"candidate_summary":"AI automation enthusiast с 2-летним опытом pet-projects. Автоматизирую процессы в n8n, интегрирую LLM, пишу промпты."}'::jsonb,
    'Cycle 4 positive (test): AI automation enthusiast. Прямой тест recall на Prompt Engineer.',
    now()
FROM eval_prompt_datasets d WHERE d.dataset_code = 'HRA-EVAL-V4';

INSERT INTO eval_prompt_cases (id, dataset_id, case_code, case_type, candidate_json, notes, created_at)
SELECT gen_random_uuid(), d.id, 'HRA-EVAL-V2-000213', 'obvious_match',
    '{"full_name":"Виктор Промпт-инженер","city":"Москва","desired_position":"Prompt Engineer","experience_years":5,"skills":["Prompt engineering","LLM","n8n","REST API","JSON","Python","Автоматизация"],"salary_expectation":230000,"candidate_summary":"Senior Prompt Engineer / AI Automation Specialist с 5-летним опытом. Проектирую промпты для LLM, строю автоматизации в n8n, интегрирую API."}'::jsonb,
    'Cycle 4 positive (train): senior Prompt Engineer. Дополнительный strong positive пример.',
    now()
FROM eval_prompt_datasets d WHERE d.dataset_code = 'HRA-EVAL-V4';

-- ============================================================
-- 4. Create case-vacancy pairs for ALL 54 candidates
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
WHERE d.dataset_code = 'HRA-EVAL-V4'
  AND v.status = 'open'
ON CONFLICT DO NOTHING;

-- ============================================================
-- 5. Create experiment HRA-EXP-V4 as a copy of HRA-EXP-V3
-- ============================================================
--
-- The Judge prompt, model, temperature, and output contract are
-- intentionally kept identical to Experiment 003.

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
    d4.id,
    'HRA-EXP-V4',
    e3.prompt_a_text,
    e3.prompt_b_text,
    e3.judge_prompt_text,
    e3.model_a,
    e3.model_b,
    e3.model_judge,
    e3.temperature_a,
    e3.temperature_b,
    e3.temperature_judge,
    e3.primary_metric,
    e3.guard_metric,
    e3.mde,
    'draft',
    now()
FROM eval_prompt_experiments e3
JOIN eval_prompt_datasets d3 ON e3.dataset_id = d3.id
JOIN eval_prompt_datasets d4 ON d4.dataset_code = 'HRA-EVAL-V4'
WHERE d3.dataset_code = 'HRA-EVAL-V3'
  AND e3.experiment_code = 'HRA-EXP-V3'
ON CONFLICT (experiment_code) DO NOTHING;

-- ============================================================
-- 6. Verification queries
-- ============================================================

SELECT
    'Experiment 004 created' AS status,
    (SELECT COUNT(*) FROM eval_prompt_datasets WHERE dataset_code = 'HRA-EVAL-V4') AS datasets,
    (SELECT COUNT(*) FROM eval_prompt_cases c
     JOIN eval_prompt_datasets d ON c.dataset_id = d.id
     WHERE d.dataset_code = 'HRA-EVAL-V4') AS cases_count,
    (SELECT COUNT(*) FROM eval_prompt_case_vacancies cv
     JOIN eval_prompt_cases c ON cv.case_id = c.id
     JOIN eval_prompt_datasets d ON c.dataset_id = d.id
     WHERE d.dataset_code = 'HRA-EVAL-V4') AS case_vacancies_count,
    (SELECT COUNT(*) FROM eval_prompt_experiments WHERE experiment_code = 'HRA-EXP-V4') AS experiments;

-- Distribution by case_type
SELECT
    c.case_type,
    COUNT(DISTINCT c.id) AS cases_count,
    COUNT(cv.id) AS pairs_count
FROM eval_prompt_cases c
JOIN eval_prompt_datasets d ON c.dataset_id = d.id
LEFT JOIN eval_prompt_case_vacancies cv ON cv.case_id = c.id
WHERE d.dataset_code = 'HRA-EVAL-V4'
GROUP BY c.case_type
ORDER BY c.case_type;

-- New candidates verification
SELECT
    'New positive/borderline candidates' AS check_name,
    COUNT(*) AS count
FROM eval_prompt_cases c
JOIN eval_prompt_datasets d ON c.dataset_id = d.id
WHERE d.dataset_code = 'HRA-EVAL-V4'
  AND c.case_code BETWEEN 'HRA-EVAL-V2-000201' AND 'HRA-EVAL-V2-000213';

-- Vacancies used
SELECT DISTINCT
    vacancy_json->>'id' AS vacancy_id,
    vacancy_json->>'title' AS title
FROM eval_prompt_case_vacancies cv
JOIN eval_prompt_cases c ON cv.case_id = c.id
JOIN eval_prompt_datasets d ON c.dataset_id = d.id
WHERE d.dataset_code = 'HRA-EVAL-V4';
