-- ============================================================
-- External Validation Dataset V5 (HRA-EVAL-V5-EXT)
-- ============================================================
--
-- Purpose:
--   1. Create a hold-out dataset for unbiased LoRA vs GPT-4o-mini
--      comparison using GPT-4o as the external reference judge.
--   2. The dataset contains 34 new candidates that do NOT overlap
--      with HRA-EVAL-V2 / V3 / V4 train/validation/test splits.
--   3. Each candidate is evaluated against the same 3 open vacancies
--      (34 candidates * 3 vacancies = 102 candidate-vacancy pairs).
--   4. Create experiment HRA-EXP-V5-EXT pointing to HRA-EVAL-V5-EXT
--      with GPT-4o as the external judge (temperature = 0).
--
-- Idempotency:
--   Uses INSERT ... ON CONFLICT DO NOTHING where possible.
--   Designed to be run ONCE on a clean external validation state.
--
-- Prerequisites:
--   - Schema 02-prompt-evaluation.sql applied.
--   - Schema 06-extend-judge-reference-fields.sql applied.
--   - Target vacancies exist in `vacancies` with status='open'.
-- ============================================================

-- ============================================================
-- 1. Create dataset HRA-EVAL-V5-EXT
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
    'HRA-EVAL-V5-EXT',
    'External Validation Dataset v5 - GPT-4o Reference',
    'Внешний валидационный датасет для Experiment 004. 34 новых кандидата, не пересекающихся с HRA-EVAL-V4. Каждый кандидат проверяется против 3 целевых вакансий: 34 * 3 = 102 пары. Reference-разметка выполняется GPT-4o (внешний judge, не teacher GPT-4.1).',
    'active',
    now()
)
ON CONFLICT (dataset_code) DO NOTHING;

-- ============================================================
-- 2. Insert 34 new external-validation candidates
-- ============================================================
--
-- Distribution target:
--   obvious_match  : 15 candidates -> 45 pairs
--   obvious_no_match: 8 candidates -> 24 pairs
--   borderline     : 11 candidates -> 33 pairs
--   Total          : 34 candidates -> 102 pairs
--
-- case_code convention: HRA-EVAL-V2-000301 .. HRA-EVAL-V2-000334
-- (prefix V2 kept to keep the same case namespace as earlier datasets)

INSERT INTO eval_prompt_cases (id, dataset_id, case_code, case_type, candidate_json, notes, created_at)
SELECT gen_random_uuid(), d.id, 'HRA-EVAL-V2-000301', 'obvious_match',
    '{"full_name":"Александр Старший Системный Аналитик","city":"Москва","desired_position":"Системный аналитик","experience_years":7,"skills":["SQL","BPMN","REST API","UML","Аналитика","Постановка задач разработчикам","Agile","Jira","Confluence"],"salary_expectation":210000,"candidate_summary":"Senior системный аналитик с 7-летним опытом. Проектирую интеграции, пишу технические задания, постанавливаю задачи разработчикам, владею SQL, BPMN, REST API, UML, Agile."}'::jsonb,
    'External validation: senior системный аналитик, obvious match для системного аналитика.',
    now()
FROM eval_prompt_datasets d WHERE d.dataset_code = 'HRA-EVAL-V5-EXT';

INSERT INTO eval_prompt_cases (id, dataset_id, case_code, case_type, candidate_json, notes, created_at)
SELECT gen_random_uuid(), d.id, 'HRA-EVAL-V2-000302', 'obvious_match',
    '{"full_name":"Екатерина Ведущий Системный Аналитик","city":"Москва","desired_position":"Системный аналитик","experience_years":6,"skills":["SQL","BPMN","REST API","UML","Системная аналитика","Технические задания","Postman","ER-диаграммы"],"salary_expectation":195000,"candidate_summary":"Ведущий системный аналитик с 6-летним опытом. Проектирую API, описываю бизнес-процессы в BPMN, пишу ТЗ, тестирую REST API в Postman."}'::jsonb,
    'External validation: lead системный аналитик, obvious match.',
    now()
FROM eval_prompt_datasets d WHERE d.dataset_code = 'HRA-EVAL-V5-EXT';

INSERT INTO eval_prompt_cases (id, dataset_id, case_code, case_type, candidate_json, notes, created_at)
SELECT gen_random_uuid(), d.id, 'HRA-EVAL-V2-000303', 'obvious_match',
    '{"full_name":"Михаил Архитектор Процессов","city":"Москва","desired_position":"Системный аналитик","experience_years":8,"skills":["BPMN","UML","SQL","REST API","SOA","Микросервисы","Документирование","Аналитика"],"salary_expectation":230000,"candidate_summary":"Системный аналитик / архитектор бизнес-процессов с 8-летним опытом. Специализируюсь на микросервисах, SOA, REST API, BPMN."}'::jsonb,
    'External validation: architect-level системный аналитик, obvious match.',
    now()
FROM eval_prompt_datasets d WHERE d.dataset_code = 'HRA-EVAL-V5-EXT';

INSERT INTO eval_prompt_cases (id, dataset_id, case_code, case_type, candidate_json, notes, created_at)
SELECT gen_random_uuid(), d.id, 'HRA-EVAL-V2-000304', 'obvious_match',
    '{"full_name":"Иван Старший Промпт-Инженер","city":"Москва","desired_position":"Prompt Engineer","experience_years":5,"skills":["Prompt engineering","LLM","n8n","REST API","JSON","Python","LangChain","OpenAI API"],"salary_expectation":240000,"candidate_summary":"Senior Prompt Engineer с 5-летним опытом. Проектирую промпты для LLM, строю AI-автоматизации в n8n, интегрирую OpenAI API, работаю с LangChain."}'::jsonb,
    'External validation: senior prompt engineer, obvious match для Prompt Engineer.',
    now()
FROM eval_prompt_datasets d WHERE d.dataset_code = 'HRA-EVAL-V5-EXT';

INSERT INTO eval_prompt_cases (id, dataset_id, case_code, case_type, candidate_json, notes, created_at)
SELECT gen_random_uuid(), d.id, 'HRA-EVAL-V2-000305', 'obvious_match',
    '{"full_name":"София AI Automation Lead","city":"Москва","desired_position":"AI Automation Specialist","experience_years":4,"skills":["n8n","Make","LLM","Prompt engineering","REST API","JSON","Python","Бизнес-процессы"],"salary_expectation":220000,"candidate_summary":"AI Automation Lead с 4-летним опытом. Автоматизирую бизнес-процессы в n8n и Make, интегрирую LLM, проектирую промпты, работаю с REST API."}'::jsonb,
    'External validation: AI automation lead, obvious match для Prompt Engineer.',
    now()
FROM eval_prompt_datasets d WHERE d.dataset_code = 'HRA-EVAL-V5-EXT';

INSERT INTO eval_prompt_cases (id, dataset_id, case_code, case_type, candidate_json, notes, created_at)
SELECT gen_random_uuid(), d.id, 'HRA-EVAL-V2-000306', 'obvious_match',
    '{"full_name":"Денис LLM Integration Engineer","city":"Москва","desired_position":"Prompt Engineer / AI Automation Specialist","experience_years":5,"skills":["LLM","Prompt engineering","n8n","REST API","JSON","Python","HuggingFace","API интеграции"],"salary_expectation":230000,"candidate_summary":"LLM Integration Engineer с 5-летним опытом. Интегрирую LLM в бизнес-процессы, проектирую промпты, автоматизирую workflow в n8n, работаю с HuggingFace."}'::jsonb,
    'External validation: LLM integration engineer, obvious match для Prompt Engineer.',
    now()
FROM eval_prompt_datasets d WHERE d.dataset_code = 'HRA-EVAL-V5-EXT';

INSERT INTO eval_prompt_cases (id, dataset_id, case_code, case_type, candidate_json, notes, created_at)
SELECT gen_random_uuid(), d.id, 'HRA-EVAL-V2-000307', 'obvious_match',
    '{"full_name":"Анна Ведущий Специалист по Разметке","city":"Москва","desired_position":"Data Annotation Lead","experience_years":5,"skills":["Разметка данных","Инструкции для ML","Контроль качества","Внимательность","Грамотность","Python basics","QA"],"salary_expectation":140000,"candidate_summary":"Data Annotation Lead с 5-летним опытом. Размечаю данные для ML-моделей, составляю инструкции для разметчиков, контролирую качество, работаю с текстовыми датасетами."}'::jsonb,
    'External validation: senior data annotation lead, obvious match для разметки данных.',
    now()
FROM eval_prompt_datasets d WHERE d.dataset_code = 'HRA-EVAL-V5-EXT';

INSERT INTO eval_prompt_cases (id, dataset_id, case_code, case_type, candidate_json, notes, created_at)
SELECT gen_random_uuid(), d.id, 'HRA-EVAL-V2-000308', 'obvious_match',
    '{"full_name":"Ольга Старший Разметчик Данных","city":"Москва","desired_position":"Специалист по разметке данных","experience_years":4,"skills":["Разметка данных","Проверка ИИ","Инструкции для ML","Внимательность","Грамотный русский язык","QA","Работа с текстом"],"salary_expectation":120000,"candidate_summary":"Senior data annotator с 4-летним опытом. Размечаю контент для AI-систем, проверяю качество разметки, составляю инструкции, работаю с текстовыми данными."}'::jsonb,
    'External validation: senior data annotator, obvious match для разметки данных.',
    now()
FROM eval_prompt_datasets d WHERE d.dataset_code = 'HRA-EVAL-V5-EXT';

INSERT INTO eval_prompt_cases (id, dataset_id, case_code, case_type, candidate_json, notes, created_at)
SELECT gen_random_uuid(), d.id, 'HRA-EVAL-V2-000309', 'obvious_match',
    '{"full_name":"Татьяна QA в Разметке","city":"Москва","desired_position":"Специалист по разметке данных","experience_years":4,"skills":["Разметка данных","Контроль качества","Инструкции","Внимательность","Грамотность","Проверка AI","Работа с датасетами"],"salary_expectation":110000,"candidate_summary":"QA-специалист в области разметки данных с 4-летним опытом. Контролирую качество разметки, составляю инструкции, проверяю работу AI-моделей."}'::jsonb,
    'External validation: QA in data annotation, obvious match для разметки данных.',
    now()
FROM eval_prompt_datasets d WHERE d.dataset_code = 'HRA-EVAL-V5-EXT';

INSERT INTO eval_prompt_cases (id, dataset_id, case_code, case_type, candidate_json, notes, created_at)
SELECT gen_random_uuid(), d.id, 'HRA-EVAL-V2-000310', 'obvious_no_match',
    '{"full_name":"Сергей Врач Хирург","city":"Москва","desired_position":"Хирург","experience_years":12,"skills":["Хирургия","Диагностика","Операции","Медицинская документация","Пациенты"],"salary_expectation":250000,"candidate_summary":"Хирург с 12-летним опытом. Выполняю операции, веду медицинскую документацию, консультирую пациентов."}'::jsonb,
    'External validation: surgeon, obvious no match для всех IT-вакансий.',
    now()
FROM eval_prompt_datasets d WHERE d.dataset_code = 'HRA-EVAL-V5-EXT';

INSERT INTO eval_prompt_cases (id, dataset_id, case_code, case_type, candidate_json, notes, created_at)
SELECT gen_random_uuid(), d.id, 'HRA-EVAL-V2-000311', 'obvious_no_match',
    '{"full_name":"Мария Бухгалтер","city":"Москва","desired_position":"Главный бухгалтер","experience_years":10,"skills":["1С","Бухгалтерия","Налоги","Отчётность","Excel","Кадры"],"salary_expectation":180000,"candidate_summary":"Главный бухгалтер с 10-летним опытом. Веду бухгалтерский учёт, налоговую отчётность, кадровый учёт, работаю в 1С."}'::jsonb,
    'External validation: accountant, obvious no match для всех IT-вакансий.',
    now()
FROM eval_prompt_datasets d WHERE d.dataset_code = 'HRA-EVAL-V5-EXT';

INSERT INTO eval_prompt_cases (id, dataset_id, case_code, case_type, candidate_json, notes, created_at)
SELECT gen_random_uuid(), d.id, 'HRA-EVAL-V2-000312', 'obvious_no_match',
    '{"full_name":"Андрей Юрист","city":"Москва","desired_position":"Юрисконсульт","experience_years":6,"skills":["Право","Договоры","Консультирование","Суды","Документоведение"],"salary_expectation":170000,"candidate_summary":"Юрист с 6-летним опытом. Составляю договоры, консультирую по правовым вопросам, представляю интересы в судах."}'::jsonb,
    'External validation: lawyer, obvious no match для всех IT-вакансий.',
    now()
FROM eval_prompt_datasets d WHERE d.dataset_code = 'HRA-EVAL-V5-EXT';

INSERT INTO eval_prompt_cases (id, dataset_id, case_code, case_type, candidate_json, notes, created_at)
SELECT gen_random_uuid(), d.id, 'HRA-EVAL-V2-000313', 'obvious_no_match',
    '{"full_name":"Наталья Младший Копирайтер","city":"Москва","desired_position":"Копирайтер","experience_years":1,"skills":["Копирайтинг","Тексты","SMM","Грамотность","Canva"],"salary_expectation":90000,"candidate_summary":"Junior копирайтер с 1-годичным опытом. Пишу тексты для соцсетей, знаю грамотность, умею работать в Canva."}'::jsonb,
    'External validation: junior copywriter, obvious no match для Prompt Engineer / системный аналитик / разметка данных.',
    now()
FROM eval_prompt_datasets d WHERE d.dataset_code = 'HRA-EVAL-V5-EXT';

INSERT INTO eval_prompt_cases (id, dataset_id, case_code, case_type, candidate_json, notes, created_at)
SELECT gen_random_uuid(), d.id, 'HRA-EVAL-V2-000314', 'obvious_no_match',
    '{"full_name":"Дмитрий Курьер","city":"Москва","desired_position":"Курьер","experience_years":3,"skills":["Вождение","Доставка","Клиентоориентированность","Навигация"],"salary_expectation":80000,"candidate_summary":"Курьер с 3-летним опытом. Доставляю посылки, знаю город, ориентирован на клиента."}'::jsonb,
    'External validation: courier, obvious no match для всех IT-вакансий.',
    now()
FROM eval_prompt_datasets d WHERE d.dataset_code = 'HRA-EVAL-V5-EXT';

INSERT INTO eval_prompt_cases (id, dataset_id, case_code, case_type, candidate_json, notes, created_at)
SELECT gen_random_uuid(), d.id, 'HRA-EVAL-V2-000315', 'borderline',
    '{"full_name":"Виктор Бизнес-Аналитик с Автоматизацией","city":"Москва","desired_position":"Бизнес-аналитик","experience_years":4,"skills":["BPMN","UML","Требования","Бизнес-процессы","n8n","REST API basics","SQL basics"],"salary_expectation":175000,"candidate_summary":"Бизнес-аналитик с 4-летним опытом. Описываю процессы, собираю требования, работаю с BPMN/UML, есть базовый опыт n8n и REST API."}'::jsonb,
    'External validation: BA with basic automation, borderline для Prompt Engineer / системный аналитик.',
    now()
FROM eval_prompt_datasets d WHERE d.dataset_code = 'HRA-EVAL-V5-EXT';

INSERT INTO eval_prompt_cases (id, dataset_id, case_code, case_type, candidate_json, notes, created_at)
SELECT gen_random_uuid(), d.id, 'HRA-EVAL-V2-000316', 'borderline',
    '{"full_name":"Елена Младший Системный Аналитик","city":"Москва","desired_position":"Системный аналитик","experience_years":2,"skills":["SQL","BPMN","REST API","UML","Аналитика","Jira"],"salary_expectation":140000,"candidate_summary":"Junior системный аналитик с 2-летним опытом. Знаю SQL, BPMN, REST API, UML, работаю в Jira, но мало опыта постановки задач разработчикам."}'::jsonb,
    'External validation: junior systems analyst, borderline для системного аналитика.',
    now()
FROM eval_prompt_datasets d WHERE d.dataset_code = 'HRA-EVAL-V5-EXT';

INSERT INTO eval_prompt_cases (id, dataset_id, case_code, case_type, candidate_json, notes, created_at)
SELECT gen_random_uuid(), d.id, 'HRA-EVAL-V2-000317', 'borderline',
    '{"full_name":"Кирилл QA с Python","city":"Москва","desired_position":"QA Engineer","experience_years":3,"skills":["Python","API testing","Postman","Тест-кейсы","SQL basics","REST API","Автоматизация тестирования"],"salary_expectation":160000,"candidate_summary":"QA engineer с 3-летним опытом. Пишу автотесты на Python, тестирую API в Postman, знаю SQL, понимаю REST."}'::jsonb,
    'External validation: QA with Python/API, borderline для Prompt Engineer / системный аналитик.',
    now()
FROM eval_prompt_datasets d WHERE d.dataset_code = 'HRA-EVAL-V5-EXT';

INSERT INTO eval_prompt_cases (id, dataset_id, case_code, case_type, candidate_json, notes, created_at)
SELECT gen_random_uuid(), d.id, 'HRA-EVAL-V2-000318', 'borderline',
    '{"full_name":"Алёна Промпт-Инженер без Опыта Работы","city":"Москва","desired_position":"Prompt Engineer","experience_years":1,"skills":["Prompt engineering","LLM","ChatGPT","Копирайтинг","Грамотность","JSON basics"],"salary_expectation":130000,"candidate_summary":"Начинающий prompt engineer с 1-годичным опытом pet-projects. Проектирую промпты для ChatGPT, пишу тексты, знаю JSON на базовом уровне, нет коммерческого опыта."}'::jsonb,
    'External validation: prompt engineer without commercial experience, borderline для Prompt Engineer.',
    now()
FROM eval_prompt_datasets d WHERE d.dataset_code = 'HRA-EVAL-V5-EXT';

INSERT INTO eval_prompt_cases (id, dataset_id, case_code, case_type, candidate_json, notes, created_at)
SELECT gen_random_uuid(), d.id, 'HRA-EVAL-V2-000319', 'borderline',
    '{"full_name":"Павел Технический Писатель","city":"Москва","desired_position":"Technical Writer","experience_years":3,"skills":["Техническая документация","Инструкции","Markdown","Python basics","Внимательность","Грамотность"],"salary_expectation":135000,"candidate_summary":"Technical writer с 3-летним опытом. Пишу техническую документацию и инструкции, знаю Markdown и Python basics, внимателен к деталям."}'::jsonb,
    'External validation: technical writer, borderline для разметки данных / системного аналитика.',
    now()
FROM eval_prompt_datasets d WHERE d.dataset_code = 'HRA-EVAL-V5-EXT';

INSERT INTO eval_prompt_cases (id, dataset_id, case_code, case_type, candidate_json, notes, created_at)
SELECT gen_random_uuid(), d.id, 'HRA-EVAL-V2-000320', 'borderline',
    '{"full_name":"Светлана Контент-Менеджер с Опытом AI","city":"Москва","desired_position":"Content Manager","experience_years":3,"skills":["Контент","Редактура","Грамотность","Внимательность","ChatGPT","Prompt engineering course"],"salary_expectation":120000,"candidate_summary":"Content manager с 3-летним опытом. Работаю с текстами и редактурой, прошла курс prompt engineering, использую ChatGPT в работе."}'::jsonb,
    'External validation: content manager with prompt course, borderline для Prompt Engineer / разметка данных.',
    now()
FROM eval_prompt_datasets d WHERE d.dataset_code = 'HRA-EVAL-V5-EXT';

INSERT INTO eval_prompt_cases (id, dataset_id, case_code, case_type, candidate_json, notes, created_at)
SELECT gen_random_uuid(), d.id, 'HRA-EVAL-V2-000321', 'obvious_match',
    '{"full_name":"Георгий Senior System Analyst","city":"Москва","desired_position":"Системный аналитик","experience_years":6,"skills":["SQL","BPMN","REST API","UML","Аналитика","Постановка задач","Agile","Swagger"],"salary_expectation":200000,"candidate_summary":"Senior системный аналитик с 6-летним опытом. Проектирую API-интеграции, описываю процессы в BPMN/UML, постанавливаю задачи, работаю со Swagger."}'::jsonb,
    'External validation: senior system analyst, obvious match.',
    now()
FROM eval_prompt_datasets d WHERE d.dataset_code = 'HRA-EVAL-V5-EXT';

INSERT INTO eval_prompt_cases (id, dataset_id, case_code, case_type, candidate_json, notes, created_at)
SELECT gen_random_uuid(), d.id, 'HRA-EVAL-V2-000322', 'obvious_match',
    '{"full_name":"Ирина Senior Prompt Engineer","city":"Москва","desired_position":"Prompt Engineer","experience_years":6,"skills":["Prompt engineering","LLM","n8n","REST API","JSON","Python","OpenAI API","Автоматизация"],"salary_expectation":240000,"candidate_summary":"Senior Prompt Engineer с 6-летним опытом. Проектирую сложные промпты, автоматизирую процессы в n8n, интегрирую LLM через API."}'::jsonb,
    'External validation: senior prompt engineer, obvious match.',
    now()
FROM eval_prompt_datasets d WHERE d.dataset_code = 'HRA-EVAL-V5-EXT';

INSERT INTO eval_prompt_cases (id, dataset_id, case_code, case_type, candidate_json, notes, created_at)
SELECT gen_random_uuid(), d.id, 'HRA-EVAL-V2-000323', 'obvious_match',
    '{"full_name":"Юлия Senior Data Annotator","city":"Москва","desired_position":"Data Annotation Specialist","experience_years":5,"skills":["Разметка данных","Инструкции для ML","Контроль качества","Внимательность","Грамотность","Python basics","QA"],"salary_expectation":130000,"candidate_summary":"Senior data annotator с 5-летним опытом. Размечаю данные для ML, составляю инструкции, контролирую качество, работаю с текстовыми датасетами."}'::jsonb,
    'External validation: senior data annotator, obvious match.',
    now()
FROM eval_prompt_datasets d WHERE d.dataset_code = 'HRA-EVAL-V5-EXT';

INSERT INTO eval_prompt_cases (id, dataset_id, case_code, case_type, candidate_json, notes, created_at)
SELECT gen_random_uuid(), d.id, 'HRA-EVAL-V2-000324', 'obvious_match',
    '{"full_name":"Артём Middle System Analyst","city":"Москва","desired_position":"Системный аналитик","experience_years":4,"skills":["SQL","BPMN","REST API","UML","Аналитика","Jira","Confluence"],"salary_expectation":170000,"candidate_summary":"Middle системный аналитик с 4-летним опытом. Проектирую интеграции, пишу ТЗ, работаю с BPMN/UML/SQL, веду документацию в Confluence."}'::jsonb,
    'External validation: middle system analyst, obvious match.',
    now()
FROM eval_prompt_datasets d WHERE d.dataset_code = 'HRA-EVAL-V5-EXT';

INSERT INTO eval_prompt_cases (id, dataset_id, case_code, case_type, candidate_json, notes, created_at)
SELECT gen_random_uuid(), d.id, 'HRA-EVAL-V2-000325', 'obvious_match',
    '{"full_name":"Максим Middle Prompt Engineer","city":"Москва","desired_position":"Prompt Engineer","experience_years":3,"skills":["Prompt engineering","LLM","n8n","REST API","JSON","Python","Автоматизация бизнес-процессов"],"salary_expectation":190000,"candidate_summary":"Middle Prompt Engineer с 3-летним опытом. Проектирую промпты, строю AI-автоматизации, интегрирую API, работаю с LLM."}'::jsonb,
    'External validation: middle prompt engineer, obvious match.',
    now()
FROM eval_prompt_datasets d WHERE d.dataset_code = 'HRA-EVAL-V5-EXT';

INSERT INTO eval_prompt_cases (id, dataset_id, case_code, case_type, candidate_json, notes, created_at)
SELECT gen_random_uuid(), d.id, 'HRA-EVAL-V2-000326', 'obvious_match',
    '{"full_name":"Людмила Middle Data Annotator","city":"Москва","desired_position":"Специалист по разметке данных","experience_years":3,"skills":["Разметка данных","Инструкции","Контроль качества","Внимательность","Грамотность","QA"],"salary_expectation":110000,"candidate_summary":"Middle data annotator с 3-летним опытом. Размечаю данные, составляю инструкции, проверяю качество, внимательна к деталям."}'::jsonb,
    'External validation: middle data annotator, obvious match.',
    now()
FROM eval_prompt_datasets d WHERE d.dataset_code = 'HRA-EVAL-V5-EXT';

INSERT INTO eval_prompt_cases (id, dataset_id, case_code, case_type, candidate_json, notes, created_at)
SELECT gen_random_uuid(), d.id, 'HRA-EVAL-V2-000327', 'borderline',
    '{"full_name":"Пётр Junior System Analyst","city":"Москва","desired_position":"Системный аналитик","experience_years":1,"skills":["SQL","BPMN","REST API","UML","Аналитика","Jira"],"salary_expectation":110000,"candidate_summary":"Junior системный аналитик с 1-годичным опытом. Знаю SQL, BPMN, REST API, UML, работаю в Jira, мало практики."}'::jsonb,
    'External validation: junior system analyst, borderline для системного аналитика.',
    now()
FROM eval_prompt_datasets d WHERE d.dataset_code = 'HRA-EVAL-V5-EXT';

INSERT INTO eval_prompt_cases (id, dataset_id, case_code, case_type, candidate_json, notes, created_at)
SELECT gen_random_uuid(), d.id, 'HRA-EVAL-V2-000328', 'borderline',
    '{"full_name":"Валерия Junior Prompt Engineer","city":"Москва","desired_position":"Prompt Engineer","experience_years":1,"skills":["Prompt engineering","ChatGPT","n8n basics","JSON","Грамотность","Копирайтинг"],"salary_expectation":110000,"candidate_summary":"Junior prompt engineer с 1-годичным опытом pet-projects. Проектирую простые промпты, использую ChatGPT, знаю n8n basics."}'::jsonb,
    'External validation: junior prompt engineer, borderline для Prompt Engineer.',
    now()
FROM eval_prompt_datasets d WHERE d.dataset_code = 'HRA-EVAL-V5-EXT';

INSERT INTO eval_prompt_cases (id, dataset_id, case_code, case_type, candidate_json, notes, created_at)
SELECT gen_random_uuid(), d.id, 'HRA-EVAL-V2-000329', 'borderline',
    '{"full_name":"Инна Junior Data Annotator","city":"Москва","desired_position":"Специалист по разметке данных","experience_years":1,"skills":["Разметка данных","Внимательность","Грамотность","Инструкции","QA basics"],"salary_expectation":90000,"candidate_summary":"Junior data annotator с 1-годичным опытом. Размечаю данные, внимательна к деталям, грамотна, знаю базовые инструкции."}'::jsonb,
    'External validation: junior data annotator, borderline для разметки данных.',
    now()
FROM eval_prompt_datasets d WHERE d.dataset_code = 'HRA-EVAL-V5-EXT';

INSERT INTO eval_prompt_cases (id, dataset_id, case_code, case_type, candidate_json, notes, created_at)
SELECT gen_random_uuid(), d.id, 'HRA-EVAL-V2-000330', 'obvious_no_match',
    '{"full_name":"Роман DevOps Engineer","city":"Москва","desired_position":"DevOps Engineer","experience_years":5,"skills":["Linux","Docker","Kubernetes","CI/CD","Terraform","Ansible","AWS"],"salary_expectation":250000,"candidate_summary":"DevOps engineer с 5-летним опытом. Работаю с Linux, Docker, Kubernetes, CI/CD, Terraform, облаками."}'::jsonb,
    'External validation: DevOps engineer, obvious no match для Prompt Engineer / системный аналитик / разметка данных.',
    now()
FROM eval_prompt_datasets d WHERE d.dataset_code = 'HRA-EVAL-V5-EXT';

INSERT INTO eval_prompt_cases (id, dataset_id, case_code, case_type, candidate_json, notes, created_at)
SELECT gen_random_uuid(), d.id, 'HRA-EVAL-V2-000331', 'obvious_no_match',
    '{"full_name":"Никита Frontend Developer","city":"Москва","desired_position":"Frontend Developer","experience_years":4,"skills":["JavaScript","React","TypeScript","CSS","HTML","Webpack"],"salary_expectation":220000,"candidate_summary":"Frontend developer с 4-летним опытом. Разрабатываю интерфейсы на React/TypeScript, знаю JavaScript, CSS, HTML."}'::jsonb,
    'External validation: frontend developer, obvious no match для Prompt Engineer / системный аналитик / разметка данных.',
    now()
FROM eval_prompt_datasets d WHERE d.dataset_code = 'HRA-EVAL-V5-EXT';

INSERT INTO eval_prompt_cases (id, dataset_id, case_code, case_type, candidate_json, notes, created_at)
SELECT gen_random_uuid(), d.id, 'HRA-EVAL-V2-000332', 'obvious_no_match',
    '{"full_name":"Дарья Data Engineer","city":"Москва","desired_position":"Data Engineer","experience_years":4,"skills":["Python","SQL","Spark","Airflow","Kafka","ETL","Hadoop"],"salary_expectation":240000,"candidate_summary":"Data engineer с 4-летним опытом. Строю ETL-пайплайны, работаю с Spark, Airflow, Kafka, Hadoop."}'::jsonb,
    'External validation: data engineer, obvious no match для Prompt Engineer / системный аналитик / разметка данных.',
    now()
FROM eval_prompt_datasets d WHERE d.dataset_code = 'HRA-EVAL-V5-EXT';

INSERT INTO eval_prompt_cases (id, dataset_id, case_code, case_type, candidate_json, notes, created_at)
SELECT gen_random_uuid(), d.id, 'HRA-EVAL-V2-000333', 'borderline',
    '{"full_name":"Константин Product Manager с AI","city":"Москва","desired_position":"Product Manager","experience_years":4,"skills":["Продукт","Roadmap","LLM","Prompt engineering","API","Аналитика","Agile"],"salary_expectation":230000,"candidate_summary":"Product Manager с 4-летним опытом. Управляю продуктом, работаю с LLM и prompt engineering, понимаю API и аналитику."}'::jsonb,
    'External validation: product manager with AI, borderline для Prompt Engineer / системный аналитик.',
    now()
FROM eval_prompt_datasets d WHERE d.dataset_code = 'HRA-EVAL-V5-EXT';

INSERT INTO eval_prompt_cases (id, dataset_id, case_code, case_type, candidate_json, notes, created_at)
SELECT gen_random_uuid(), d.id, 'HRA-EVAL-V2-000334', 'borderline',
    '{"full_name":"Тимур Technical Support с API","city":"Москва","desired_position":"Technical Support Engineer","experience_years":3,"skills":["Поддержка","REST API","Postman","SQL basics","JSON","Коммуникация","Документирование"],"salary_expectation":130000,"candidate_summary":"Technical support engineer с 3-летним опытом. Поддерживаю API-интеграции, работаю в Postman, знаю SQL basics и JSON."}'::jsonb,
    'External validation: technical support with API, borderline для системный аналитик / Prompt Engineer.',
    now()
FROM eval_prompt_datasets d WHERE d.dataset_code = 'HRA-EVAL-V5-EXT';

-- ============================================================
-- 3. Create case-vacancy pairs for ALL 34 candidates
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
WHERE d.dataset_code = 'HRA-EVAL-V5-EXT'
  AND v.status = 'open'
ON CONFLICT DO NOTHING;

-- ============================================================
-- 4. Create experiment HRA-EXP-V5-EXT
--    Judge model = gpt-4o (external judge, not teacher GPT-4.1)
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
    'HRA-EXP-V5-EXT',
    e4.prompt_a_text,
    e4.prompt_b_text,
    e4.judge_prompt_text,
    e4.model_a,
    e4.model_b,
    'gpt-4o',
    e4.temperature_a,
    e4.temperature_b,
    0,
    e4.primary_metric,
    e4.guard_metric,
    e4.mde,
    'draft',
    now()
FROM eval_prompt_experiments e4
JOIN eval_prompt_datasets d4 ON e4.dataset_id = d4.id
JOIN eval_prompt_datasets d ON d.dataset_code = 'HRA-EVAL-V5-EXT'
WHERE d4.dataset_code = 'HRA-EVAL-V4'
  AND e4.experiment_code = 'HRA-EXP-V4'
ON CONFLICT (experiment_code) DO NOTHING;

-- ============================================================
-- 5. Verification queries
-- ============================================================

SELECT
    'External Validation V5 created' AS status,
    (SELECT COUNT(*) FROM eval_prompt_datasets WHERE dataset_code = 'HRA-EVAL-V5-EXT') AS datasets,
    (SELECT COUNT(*) FROM eval_prompt_cases c
     JOIN eval_prompt_datasets d ON c.dataset_id = d.id
     WHERE d.dataset_code = 'HRA-EVAL-V5-EXT') AS cases_count,
    (SELECT COUNT(*) FROM eval_prompt_case_vacancies cv
     JOIN eval_prompt_cases c ON cv.case_id = c.id
     JOIN eval_prompt_datasets d ON c.dataset_id = d.id
     WHERE d.dataset_code = 'HRA-EVAL-V5-EXT') AS case_vacancies_count,
    (SELECT COUNT(*) FROM eval_prompt_experiments WHERE experiment_code = 'HRA-EXP-V5-EXT') AS experiments;

-- Distribution by case_type
SELECT
    c.case_type,
    COUNT(DISTINCT c.id) AS cases_count,
    COUNT(cv.id) AS pairs_count
FROM eval_prompt_cases c
JOIN eval_prompt_datasets d ON c.dataset_id = d.id
LEFT JOIN eval_prompt_case_vacancies cv ON cv.case_id = c.id
WHERE d.dataset_code = 'HRA-EVAL-V5-EXT'
GROUP BY c.case_type
ORDER BY c.case_type;

-- Check for overlap with V4
SELECT
    'Overlap with HRA-EVAL-V4' AS check_name,
    COUNT(*) AS overlap_count
FROM eval_prompt_cases c5
JOIN eval_prompt_datasets d5 ON c5.dataset_id = d5.id
JOIN eval_prompt_cases c4 ON c4.case_code = c5.case_code
JOIN eval_prompt_datasets d4 ON c4.dataset_id = d4.id
WHERE d5.dataset_code = 'HRA-EVAL-V5-EXT'
  AND d4.dataset_code = 'HRA-EVAL-V4';

-- Vacancies used
SELECT DISTINCT
    vacancy_json->>'id' AS vacancy_id,
    vacancy_json->>'title' AS title
FROM eval_prompt_case_vacancies cv
JOIN eval_prompt_cases c ON cv.case_id = c.id
JOIN eval_prompt_datasets d ON c.dataset_id = d.id
WHERE d.dataset_code = 'HRA-EVAL-V5-EXT';
