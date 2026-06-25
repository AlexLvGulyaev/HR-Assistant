-- ============================================================
-- HRA-EVAL-V1: Evaluation Dataset for Matching Prompt (v2)
-- Каждый кандидат проверяется против ВСЕХ открытых вакансий
-- ============================================================

-- ============================================================
-- 1. Создать датасет
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
    'HRA-EVAL-V1',
    'Matching Prompt Evaluation Dataset v1',
    'Датасет для оценки качества matching prompt. 30 кандидатов × 3 вакансии = 90 пар. Каждый кандидат проверяется против всех открытых вакансий.',
    'active',
    now()
);

-- ============================================================
-- 2. obvious_match кейсы (10 кандидатов)
-- Кандидаты, которые явно подходят к одной из вакансий
-- ============================================================

-- Кейс 1: Системный аналитик → подходит к вакансии "Системный аналитик"
INSERT INTO eval_prompt_cases (
    id, dataset_id, case_code, case_type, candidate_json, notes, created_at
)
SELECT gen_random_uuid(), d.id, 'HRA-EVAL-000001', 'obvious_match',
    '{"full_name":"Иванов Иван Иванович","city":"Москва","desired_position":"Системный аналитик","experience_years":5,"skills":["SQL","BPMN","REST API","UML","Agile"],"salary_expectation":180000,"candidate_summary":"Опытный системный аналитик, специализируюсь на описании бизнес-процессов и подготовке технических заданий. Владею SQL, BPMN, REST API."}'::jsonb,
    'Явное совпадение: все навыки совпадают, опыт в диапазоне, зарплата в бюджете.', now()
FROM eval_prompt_datasets d WHERE d.dataset_code = 'HRA-EVAL-V1';

-- Кейс 2: Prompt Engineer → подходит к вакансии "Prompt Engineer"
INSERT INTO eval_prompt_cases (
    id, dataset_id, case_code, case_type, candidate_json, notes, created_at
)
SELECT gen_random_uuid(), d.id, 'HRA-EVAL-000002', 'obvious_match',
    '{"full_name":"Петрова Мария Сергеевна","city":"Москва","desired_position":"Prompt Engineer","experience_years":3,"skills":["Prompt engineering","n8n","API","JSON","LLM","GPT-4","Claude"],"salary_expectation":200000,"candidate_summary":"Prompt engineer с опытом работы с LLM и автоматизации бизнес-процессов через n8n. Создаю эффективные промпты для различных задач."}'::jsonb,
    'Явное совпадение: все ключевые навыки совпадают, опыт достаточный, зарплата в бюджете.', now()
FROM eval_prompt_datasets d WHERE d.dataset_code = 'HRA-EVAL-V1';

-- Кейс 3: Специалист по разметке → подходит к вакансии "Специалист по разметке"
INSERT INTO eval_prompt_cases (
    id, dataset_id, case_code, case_type, candidate_json, notes, created_at
)
SELECT gen_random_uuid(), d.id, 'HRA-EVAL-000003', 'obvious_match',
    '{"full_name":"Сидоров Алексей Петрович","city":"Санкт-Петербург","desired_position":"Специалист по разметке данных","experience_years":1,"skills":["Внимательность","Грамотный русский язык","Работа с текстами","Качественная разметка"],"salary_expectation":80000,"candidate_summary":"Начинающий специалист, готов к разметке данных. Внимательный, грамотный, умею следовать инструкциям."}'::jsonb,
    'Явное совпадение: все требования fulfilled, зарплата в бюджете.', now()
FROM eval_prompt_datasets d WHERE d.dataset_code = 'HRA-EVAL-V1';

-- Кейс 4: Системный аналитик с неполным набором навыков
INSERT INTO eval_prompt_cases (
    id, dataset_id, case_code, case_type, candidate_json, notes, created_at
)
SELECT gen_random_uuid(), d.id, 'HRA-EVAL-000004', 'obvious_match',
    '{"full_name":"Козлова Анна Дмитриевна","city":"Казань","desired_position":"Системный аналитик","experience_years":4,"skills":["SQL","REST API","UML","Agile"],"salary_expectation":160000,"candidate_summary":"Системный аналитик, работаю с API и базами данных. Умею описывать требования и взаимодействовать с разработчиками."}'::jsonb,
    'Неполный набор навыков (нет BPMN), но опыт и ключевые навыки совпадают, должность точная.', now()
FROM eval_prompt_datasets d WHERE d.dataset_code = 'HRA-EVAL-V1';

-- Кейс 5: Junior аналитик
INSERT INTO eval_prompt_cases (
    id, dataset_id, case_code, case_type, candidate_json, notes, created_at
)
SELECT gen_random_uuid(), d.id, 'HRA-EVAL-000005', 'obvious_match',
    '{"full_name":"Новиков Дмитрий Олегович","city":"Москва","desired_position":"Junior Системный аналитик","experience_years":1,"skills":["SQL","UML","Agile","Документирование"],"salary_expectation":150000,"candidate_summary":"Начинающий системный аналитик, хочу развиваться. Умею писать документацию, знаю основы SQL и UML."}'::jsonb,
    'Junior кандидат, но навыки совпадают, зарплата в нижней границе бюджета.', now()
FROM eval_prompt_datasets d WHERE d.dataset_code = 'HRA-EVAL-V1';

-- Кейс 6: Senior Prompt Engineer
INSERT INTO eval_prompt_cases (
    id, dataset_id, case_code, case_type, candidate_json, notes, created_at
)
SELECT gen_random_uuid(), d.id, 'HRA-EVAL-000006', 'obvious_match',
    '{"full_name":"Морозова Елена Викторовна","city":"Москва","desired_position":"Senior Prompt Engineer","experience_years":5,"skills":["Prompt engineering","n8n","API","JSON","LLM","GPT-4","Claude","Team Lead"],"salary_expectation":250000,"candidate_summary":"Senior prompt engineer с опытом лидерства команды. Эксперт в LLM и автоматизации бизнес-процессов."}'::jsonb,
    'Senior кандидат, все навыки совпадают, зарплата на верхней границе бюджета.', now()
FROM eval_prompt_datasets d WHERE d.dataset_code = 'HRA-EVAL-V1';

-- Кейс 7: Аналитик (общая позиция)
INSERT INTO eval_prompt_cases (
    id, dataset_id, case_code, case_type, candidate_json, notes, created_at
)
SELECT gen_random_uuid(), d.id, 'HRA-EVAL-000007', 'obvious_match',
    '{"full_name":"Волков Сергей Игоревич","city":"Москва","desired_position":"Аналитик","experience_years":7,"skills":["SQL","BPMN","REST API","UML","Agile","Scrum","Документирование"],"salary_expectation":200000,"candidate_summary":"Опытный аналитик, работаю с бизнес-требованиями и техническими заданиями. Знаю SQL, BPMN, REST API."}'::jsonb,
    'Общая позиция Аналитик, но навыки полностью совпадают с требованиями Системного аналитика.', now()
FROM eval_prompt_datasets d WHERE d.dataset_code = 'HRA-EVAL-V1';

-- Кейс 8: AI Engineer → Prompt Engineer
INSERT INTO eval_prompt_cases (
    id, dataset_id, case_code, case_type, candidate_json, notes, created_at
)
SELECT gen_random_uuid(), d.id, 'HRA-EVAL-000008', 'obvious_match',
    '{"full_name":"Кузнецов Павел Андреевич","city":"Москва","desired_position":"AI Engineer","experience_years":4,"skills":["Prompt engineering","API","JSON","LLM","GPT-4","Python","LangChain"],"salary_expectation":220000,"candidate_summary":"AI Engineer с опытом работы с LLM и промптами. Разрабатываю AI-интеграции и пайплайны."}'::jsonb,
    'AI Engineer → Prompt Engineer: родственные позиции, все ключевые навыки совпадают.', now()
FROM eval_prompt_datasets d WHERE d.dataset_code = 'HRA-EVAL-V1';

-- Кейс 9: Data Specialist → Специалист по разметке
INSERT INTO eval_prompt_cases (
    id, dataset_id, case_code, case_type, candidate_json, notes, created_at
)
SELECT gen_random_uuid(), d.id, 'HRA-EVAL-000009', 'obvious_match',
    '{"full_name":"Лебедева Ольга Сергеевна","city":"Екатеринбург","desired_position":"Data Specialist","experience_years":2,"skills":["Внимательность","Грамотный русский язык","Работа с данными","Контроль качества"],"salary_expectation":90000,"candidate_summary":"Специалист по работе с данными, умею следовать инструкциям, внимательная и грамотная."}'::jsonb,
    'Data Specialist → Специалист по разметке: навыки совпадают, зарплата в бюджете.', now()
FROM eval_prompt_datasets d WHERE d.dataset_code = 'HRA-EVAL-V1';

-- Кейс 10: Аналитик из другого города
INSERT INTO eval_prompt_cases (
    id, dataset_id, case_code, case_type, candidate_json, notes, created_at
)
SELECT gen_random_uuid(), d.id, 'HRA-EVAL-000010', 'obvious_match',
    '{"full_name":"Попов Максим Викторович","city":"Новосибирск","desired_position":"Системный аналитик","experience_years":6,"skills":["SQL","BPMN","REST API","UML","Agile","Документирование"],"salary_expectation":190000,"candidate_summary":"Опытный системный аналитик из Новосибирска, готов к релокации в Москву. Умею работать с бизнес-требованиями."}'::jsonb,
    'Другой город, но готов к релокации, все навыки и опыт совпадают.', now()
FROM eval_prompt_datasets d WHERE d.dataset_code = 'HRA-EVAL-V1';

-- ============================================================
-- 3. obvious_no_match кейсы (10 кандидатов)
-- Кандидаты, которые НЕ подходят ни к одной из вакансий
-- ============================================================

-- Кейс 11: Java Developer
INSERT INTO eval_prompt_cases (
    id, dataset_id, case_code, case_type, candidate_json, notes, created_at
)
SELECT gen_random_uuid(), d.id, 'HRA-EVAL-000011', 'obvious_no_match',
    '{"full_name":"Смирнов Артём Павлович","city":"Москва","desired_position":"Java Developer","experience_years":5,"skills":["Java","Spring Boot","Microservices","Kubernetes","Docker"],"salary_expectation":300000,"candidate_summary":"Java разработчик, специализируюсь на микросервисах и Spring. Не работал аналитиком."}'::jsonb,
    'Java Developer: совершенно другая роль, навыки не совпадают ни с одной вакансией.', now()
FROM eval_prompt_datasets d WHERE d.dataset_code = 'HRA-EVAL-V1';

-- Кейс 12: UI/UX Designer
INSERT INTO eval_prompt_cases (
    id, dataset_id, case_code, case_type, candidate_json, notes, created_at
)
SELECT gen_random_uuid(), d.id, 'HRA-EVAL-000012', 'obvious_no_match',
    '{"full_name":"Крылова Дарья Александровна","city":"Москва","desired_position":"UI/UX Designer","experience_years":4,"skills":["Figma","Sketch","Adobe XD","Prototyping","User Research"],"salary_expectation":180000,"candidate_summary":"UI/UX дизайнер, создаю интерфейсы и прототипы. Работаю в Figma и Sketch."}'::jsonb,
    'UI/UX Designer: совершенно другая область, навыки не совпадают.', now()
FROM eval_prompt_datasets d WHERE d.dataset_code = 'HRA-EVAL-V1';

-- Кейс 13: Студент без опыта
INSERT INTO eval_prompt_cases (
    id, dataset_id, case_code, case_type, candidate_json, notes, created_at
)
SELECT gen_random_uuid(), d.id, 'HRA-EVAL-000013', 'obvious_no_match',
    '{"full_name":"Зайцев Никита Александрович","city":"Москва","desired_position":"Стажёр","experience_years":0,"skills":["Excel","PowerPoint","Word"],"salary_expectation":50000,"candidate_summary":"Студент 3 курса, ищу стажировку. Умею работать в Excel и PowerPoint."}'::jsonb,
    'Студент без опыта: нет нужных навыков, зарплата ниже бюджета.', now()
FROM eval_prompt_datasets d WHERE d.dataset_code = 'HRA-EVAL-V1';

-- Кейс 14: Marketing Manager
INSERT INTO eval_prompt_cases (
    id, dataset_id, case_code, case_type, candidate_json, notes, created_at
)
SELECT gen_random_uuid(), d.id, 'HRA-EVAL-000014', 'obvious_no_match',
    '{"full_name":"Соколова Анна Михайловна","city":"Москва","desired_position":"Marketing Manager","experience_years":5,"skills":["SMM","Content Marketing","SEO","Google Analytics","Email Marketing"],"salary_expectation":150000,"candidate_summary":"Маркетолог, специализируюсь на digital-маркетинге и SMM. Умею работать с аналитикой."}'::jsonb,
    'Marketing Manager: совершенно другая область, навыки не совпадают.', now()
FROM eval_prompt_datasets d WHERE d.dataset_code = 'HRA-EVAL-V1';

-- Кейс 15: Продавец-консультант
INSERT INTO eval_prompt_cases (
    id, dataset_id, case_code, case_type, candidate_json, notes, created_at
)
SELECT gen_random_uuid(), d.id, 'HRA-EVAL-000015', 'obvious_no_match',
    '{"full_name":"Козлов Игорь Сергеевич","city":"Воронеж","desired_position":"Продавец-консультант","experience_years":3,"skills":["Продажи","Обслуживание клиентов","Кассовые операции","Мерчандайзинг"],"salary_expectation":70000,"candidate_summary":"Продавец-консультант, работаю в розничной торговле. Умею общаться с клиентами."}'::jsonb,
    'Продавец: совершенно другая профессия, навыки не совпадают.', now()
FROM eval_prompt_datasets d WHERE d.dataset_code = 'HRA-EVAL-V1';

-- Кейс 16: Водитель
INSERT INTO eval_prompt_cases (
    id, dataset_id, case_code, case_type, candidate_json, notes, created_at
)
SELECT gen_random_uuid(), d.id, 'HRA-EVAL-000016', 'obvious_no_match',
    '{"full_name":"Петров Василий Иванович","city":"Москва","desired_position":"Водитель","experience_years":10,"skills":["Вождение","Знание города","Пунктуальность","Вежливость"],"salary_expectation":100000,"candidate_summary":"Водитель с большим стажем, знаю город, пунктуальный и вежливый."}'::jsonb,
    'Водитель: совершенно другая профессия, навыки не совпадают.', now()
FROM eval_prompt_datasets d WHERE d.dataset_code = 'HRA-EVAL-V1';

-- Кейс 17: HR Manager
INSERT INTO eval_prompt_cases (
    id, dataset_id, case_code, case_type, candidate_json, notes, created_at
)
SELECT gen_random_uuid(), d.id, 'HRA-EVAL-000017', 'obvious_no_match',
    '{"full_name":"Белова Екатерина Павловна","city":"Москва","desired_position":"HR Manager","experience_years":4,"skills":["Рекрутинг","Onboarding","HR-аналитика","Interpersonal skills","Training"],"salary_expectation":160000,"candidate_summary":"HR-менеджер, занимаюсь подбором персонала и онбордингом. Умею работать с людьми."}'::jsonb,
    'HR Manager: другая область, навыки не совпадают.', now()
FROM eval_prompt_datasets d WHERE d.dataset_code = 'HRA-EVAL-V1';

-- Кейс 18: Бухгалтер
INSERT INTO eval_prompt_cases (
    id, dataset_id, case_code, case_type, candidate_json, notes, created_at
)
SELECT gen_random_uuid(), d.id, 'HRA-EVAL-000018', 'obvious_no_match',
    '{"full_name":"Фёдорова Наталья Викторовна","city":"Москва","desired_position":"Бухгалтер","experience_years":8,"skills":["1С","Налоговый учёт","Зарплата","Отчётность","Excel"],"salary_expectation":140000,"candidate_summary":"Бухгалтер, работаю в 1С, веду налоговый учёт и расчёт зарплаты."}'::jsonb,
    'Бухгалтер: совершенно другая область, навыки не совпадают.', now()
FROM eval_prompt_datasets d WHERE d.dataset_code = 'HRA-EVAL-V1';

-- Кейс 19: Переводчик
INSERT INTO eval_prompt_cases (
    id, dataset_id, case_code, case_type, candidate_json, notes, created_at
)
SELECT gen_random_uuid(), d.id, 'HRA-EVAL-000019', 'obvious_no_match',
    '{"full_name":"Романова Мария Андреевна","city":"Москва","desired_position":"Переводчик","experience_years":6,"skills":["Английский язык","Перевод текстов","Локализация","CAT-инструменты"],"salary_expectation":120000,"candidate_summary":"Переводчик, специализируюсь на техническом переводе. Знаю английский в совершенстве."}'::jsonb,
    'Переводчик: другая область, навыки не совпадают.', now()
FROM eval_prompt_datasets d WHERE d.dataset_code = 'HRA-EVAL-V1';

-- Кейс 20: Врач
INSERT INTO eval_prompt_cases (
    id, dataset_id, case_code, case_type, candidate_json, notes, created_at
)
SELECT gen_random_uuid(), d.id, 'HRA-EVAL-000020', 'obvious_no_match',
    '{"full_name":"Орлов Андрей Владимирович","city":"Москва","desired_position":"Врач","experience_years":15,"skills":["Медицина","Диагностика","Лечение","Пациенты"],"salary_expectation":200000,"candidate_summary":"Врач с большим стажем, специализируюсь на диагностике и лечении."}'::jsonb,
    'Врач: совершенно другая область, навыки не совпадают.', now()
FROM eval_prompt_datasets d WHERE d.dataset_code = 'HRA-EVAL-V1';

-- ============================================================
-- 4. borderline кейсы (10 кандидатов)
-- Кандидаты с пограничным соответствием
-- ============================================================

-- Кейс 21: Business Analyst
INSERT INTO eval_prompt_cases (
    id, dataset_id, case_code, case_type, candidate_json, notes, created_at
)
SELECT gen_random_uuid(), d.id, 'HRA-EVAL-000021', 'borderline',
    '{"full_name":"Григорьев Дмитрий Александрович","city":"Москва","desired_position":"Business Analyst","experience_years":3,"skills":["BPMN","UML","Agile","Документирование","Requirements gathering"],"salary_expectation":170000,"candidate_summary":"Business Analyst, работаю с требованиями и процессами. Знаю BPMN и UML, но не владею SQL и REST API."}'::jsonb,
    'Business Analyst → Системный аналитик: родственная позиция, но нет ключевых навыков (SQL, REST API).', now()
FROM eval_prompt_datasets d WHERE d.dataset_code = 'HRA-EVAL-V1';

-- Кейс 22: Junior Prompt Engineer
INSERT INTO eval_prompt_cases (
    id, dataset_id, case_code, case_type, candidate_json, notes, created_at
)
SELECT gen_random_uuid(), d.id, 'HRA-EVAL-000022', 'borderline',
    '{"full_name":"Николаева Анна Петровна","city":"Москва","desired_position":"Prompt Engineer","experience_years":0.5,"skills":["Prompt engineering","ChatGPT","Нейросети"],"salary_expectation":150000,"candidate_summary":"Начинающий prompt engineer, работаю с ChatGPT. Знаком с нейросетями, но нет опыта с n8n и API."}'::jsonb,
    'Junior Prompt Engineer: позиция совпадает, но опыт маленький, а зарплата на границе. Навыков недостаточно.', now()
FROM eval_prompt_datasets d WHERE d.dataset_code = 'HRA-EVAL-V1';

-- Кейс 23: Data Analyst
INSERT INTO eval_prompt_cases (
    id, dataset_id, case_code, case_type, candidate_json, notes, created_at
)
SELECT gen_random_uuid(), d.id, 'HRA-EVAL-000023', 'borderline',
    '{"full_name":"Степанова Виктория Олеговна","city":"Москва","desired_position":"Data Analyst","experience_years":2,"skills":["Python","SQL","Pandas","Data Visualization","Excel"],"salary_expectation":180000,"candidate_summary":"Data Analyst, работаю с Python и SQL. Умею визуализировать данные, но не работала с бизнес-требованиями."}'::jsonb,
    'Data Analyst → Системный аналитик: есть SQL, но нет BPMN, REST API, опыта постановки задач.', now()
FROM eval_prompt_datasets d WHERE d.dataset_code = 'HRA-EVAL-V1';

-- Кейс 24: Product Manager
INSERT INTO eval_prompt_cases (
    id, dataset_id, case_code, case_type, candidate_json, notes, created_at
)
SELECT gen_random_uuid(), d.id, 'HRA-EVAL-000024', 'borderline',
    '{"full_name":"Михайлов Илья Сергеевич","city":"Москва","desired_position":"Product Manager","experience_years":4,"skills":["Product Strategy","Agile","User Stories","API","Data Analysis"],"salary_expectation":230000,"candidate_summary":"Product Manager, работаю с продуктами и API. Знаю Agile, но не работал с LLM и n8n."}'::jsonb,
    'Product Manager → Prompt Engineer: есть API и Agile, но нет LLM и n8n навыков.', now()
FROM eval_prompt_datasets d WHERE d.dataset_code = 'HRA-EVAL-V1';

-- Кейс 25: Junior Data Analyst
INSERT INTO eval_prompt_cases (
    id, dataset_id, case_code, case_type, candidate_json, notes, created_at
)
SELECT gen_random_uuid(), d.id, 'HRA-EVAL-000025', 'borderline',
    '{"full_name":"Кузнецова Елена Александровна","city":"Москва","desired_position":"Junior Data Analyst","experience_years":0.5,"skills":["Excel","Внимательность","Грамотный русский язык","Data Analysis"],"salary_expectation":100000,"candidate_summary":"Начинающий Data Analyst, хочу работать с данными. Внимательная, грамотная."}'::jsonb,
    'Junior Data Analyst → Специалист по разметке: есть внимательность и грамотность, но нет понимания ИИ.', now()
FROM eval_prompt_datasets d WHERE d.dataset_code = 'HRA-EVAL-V1';

-- Кейс 26: QA Engineer
INSERT INTO eval_prompt_cases (
    id, dataset_id, case_code, case_type, candidate_json, notes, created_at
)
SELECT gen_random_uuid(), d.id, 'HRA-EVAL-000026', 'borderline',
    '{"full_name":"Соколов Артём Викторович","city":"Москва","desired_position":"QA Engineer","experience_years":3,"skills":["Testing","API","SQL","Agile","Test Automation"],"salary_expectation":160000,"candidate_summary":"QA Engineer, работаю с тестированием и API. Знаю SQL, но не работал с BPMN и бизнес-требованиями."}'::jsonb,
    'QA Engineer → Системный аналитик: есть SQL и API, но нет BPMN и опыта постановки задач.', now()
FROM eval_prompt_datasets d WHERE d.dataset_code = 'HRA-EVAL-V1';

-- Кейс 27: Technical Writer
INSERT INTO eval_prompt_cases (
    id, dataset_id, case_code, case_type, candidate_json, notes, created_at
)
SELECT gen_random_uuid(), d.id, 'HRA-EVAL-000027', 'borderline',
    '{"full_name":"Петрова Светлана Николаевна","city":"Москва","desired_position":"Technical Writer","experience_years":5,"skills":["Документирование","API","JSON","Грамотность","Technical Writing"],"salary_expectation":180000,"candidate_summary":"Technical Writer, пишу документацию для API. Знаю JSON, но не работала с LLM и промптами."}'::jsonb,
    'Technical Writer → Prompt Engineer: есть JSON и API, но нет LLM и n8n навыков.', now()
FROM eval_prompt_datasets d WHERE d.dataset_code = 'HRA-EVAL-V1';

-- Кейс 28: Студент IT
INSERT INTO eval_prompt_cases (
    id, dataset_id, case_code, case_type, candidate_json, notes, created_at
)
SELECT gen_random_uuid(), d.id, 'HRA-EVAL-000028', 'borderline',
    '{"full_name":"Смирнов Андрей Дмитриевич","city":"Москва","desired_position":"Junior Системный аналитик","experience_years":0,"skills":["SQL","UML","Excel","Английский язык"],"salary_expectation":80000,"candidate_summary":"Студент 4 курса IT-факультета, знаю SQL и UML. Хочу стать системным аналитиком."}'::jsonb,
    'Студент → Системный аналитик: есть базовые навыки, но нет опыта. Зарплата ниже бюджета.', now()
FROM eval_prompt_datasets d WHERE d.dataset_code = 'HRA-EVAL-V1';

-- Кейс 29: ML Engineer
INSERT INTO eval_prompt_cases (
    id, dataset_id, case_code, case_type, candidate_json, notes, created_at
)
SELECT gen_random_uuid(), d.id, 'HRA-EVAL-000029', 'borderline',
    '{"full_name":"Волков Павел Андреевич","city":"Москва","desired_position":"ML Engineer","experience_years":3,"skills":["Python","Machine Learning","TensorFlow","API","Data Science"],"salary_expectation":280000,"candidate_summary":"ML Engineer, работаю с TensorFlow и Python. Знаю API, но не работал с n8n и промптами."}'::jsonb,
    'ML Engineer → Prompt Engineer: есть ML и API, но нет n8n и prompt engineering. Зарплата выше бюджета.', now()
FROM eval_prompt_datasets d WHERE d.dataset_code = 'HRA-EVAL-V1';

-- Кейс 30: Content Manager
INSERT INTO eval_prompt_cases (
    id, dataset_id, case_code, case_type, candidate_json, notes, created_at
)
SELECT gen_random_uuid(), d.id, 'HRA-EVAL-000030', 'borderline',
    '{"full_name":"Козлова Мария Александровна","city":"Москва","desired_position":"Content Manager","experience_years":2,"skills":["Контент","Внимательность","Грамотный русский язык","Social Media"],"salary_expectation":90000,"candidate_summary":"Content Manager, работаю с контентом. Внимательная, грамотная, но не работала с ИИ."}'::jsonb,
    'Content Manager → Специалист по разметке: есть внимательность и грамотность, но нет понимания ИИ.', now()
FROM eval_prompt_datasets d WHERE d.dataset_code = 'HRA-EVAL-V1';

-- ============================================================
-- 5. Создать вакансии для каждого кейса (CROSS JOIN с открытыми вакансиями)
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
WHERE d.dataset_code = 'HRA-EVAL-V1'
  AND v.status = 'open';

-- ============================================================
-- 6. Проверка количества записей
-- ============================================================

SELECT
    'Dataset created' AS status,
    (SELECT COUNT(*) FROM eval_prompt_datasets WHERE dataset_code = 'HRA-EVAL-V1') AS datasets,
    (SELECT COUNT(*) FROM eval_prompt_cases c
     JOIN eval_prompt_datasets d ON c.dataset_id = d.id
     WHERE d.dataset_code = 'HRA-EVAL-V1') AS cases_count,
    (SELECT COUNT(*) FROM eval_prompt_case_vacancies cv
     JOIN eval_prompt_cases c ON cv.case_id = c.id
     JOIN eval_prompt_datasets d ON c.dataset_id = d.id
     WHERE d.dataset_code = 'HRA-EVAL-V1') AS case_vacancies_count;

-- Статистика по типам кейсов
SELECT
    c.case_type,
    COUNT(DISTINCT c.id) AS cases_count,
    COUNT(cv.id) AS vacancies_per_case_type
FROM eval_prompt_cases c
JOIN eval_prompt_datasets d ON c.dataset_id = d.id
LEFT JOIN eval_prompt_case_vacancies cv ON cv.case_id = c.id
WHERE d.dataset_code = 'HRA-EVAL-V1'
GROUP BY c.case_type
ORDER BY c.case_type;

-- Показать все вакансии в датасете
SELECT DISTINCT
    vacancy_json->>'id' AS vacancy_id,
    vacancy_json->>'title' AS title
FROM eval_prompt_case_vacancies cv
JOIN eval_prompt_cases c ON cv.case_id = c.id
JOIN eval_prompt_datasets d ON c.dataset_id = d.id
WHERE d.dataset_code = 'HRA-EVAL-V1';