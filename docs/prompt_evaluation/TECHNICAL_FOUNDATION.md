# HRA-EXP-V1: Технический фундамент эксперимента

**Тип документа:** Исследовательский фундамент
**Создан:** 2026-06-25
**Назначение:** Исходные материалы для отчёта об эксперименте
**Статус:** Завершён

> ⚠️ **Предупреждение о дублировании:**
> Этот документ содержит технические детали, которые также представлены в других документах:
> - **Датасет** → см. [DATASET.md](./DATASET.md)
> - **Промпты** → см. [PROMPTS.md](./PROMPTS.md)
> - **Workflow** → см. [WORKFLOW_DESIGN.md](./WORKFLOW_DESIGN.md) и [WORKFLOW_IMPLEMENTATION.md](./WORKFLOW_IMPLEMENTATION.md)
> - **Результаты** → см. [AB_TEST_REPORT.md](./AB_TEST_REPORT.md)
>
> Используйте этот документ как технический справочник для поиска SQL-запросов, параметров моделей и полных текстов промптов. Для понимания эксперимента в целом начните с [AB_TEST_REPORT.md](./AB_TEST_REPORT.md).

---

## 1. Контекст эксперимента

### Цель

A/B-тестирование matching prompt для определения возможности замены production prompt (Prompt A) на experimental prompt (Prompt B) в HR Assistant.

### Связь с HR Assistant

Matching prompt — ключевой компонент HR Assistant, отвечающий за оценку соответствия кандидата вакансии. Качество промпта напрямую влияет на:
- точность подбора кандидатов;
- удовлетворённость HR-специалистов;
- репутацию продукта.

### Почему Prompt A vs Prompt B

**Prompt A (Production):**
- Краткий промпт (480 символов)
- Простой список критериев
- Минимальные инструкции
- Работает в production

**Prompt B (Experimental):**
- Детальный промпт (3000 символов)
- Структурированные шкалы оценки
- Few-shot примеры для каждого типа кейса
- Явные правила оценки

**Гипотеза:** Prompt B должен давать более консистентные и обоснованные оценки за счёт детальных инструкций и примеров.

**Источник:** [`database/04-create-experiment-v1.sql`](../../database/04-create-experiment-v1.sql), строки 33-137

---

## 2. Дизайн эксперимента

### Датасет

| Параметр | Значение |
|-----------|-------|
| **Код датасета** | `HRA-EVAL-V1` |
| **Всего кейсов** | 30 кандидатов |
| **Всего пар** | 90 (30 × 3 вакансии) |
| **Статус** | `active` |

**Источник:** [`database/03-seed-eval-dataset-v1.sql`](../../database/03-seed-eval-dataset-v1.sql)

### Модель Judge

| Параметр | Значение |
|-----------|-------|
| **Модель** | `gpt-4.1-2025-04-14` |
| **Temperature** | 0 |
| **Назначение** | Reference scoring (surrogate ground truth) |
| **Файл промпта** | [`database/04-create-experiment-v1.sql`](../../database/04-create-experiment-v1.sql) — встроен в SQL |


### Prompt A (Production)

| Параметр | Значение |
|-----------|-------|
| **Модель** | `gpt-4o-mini-2024-07-18` |
| **Temperature** | 0 |
| **Длина промпта** | 480 символов |
| **Тип** | Production matching prompt |


### Prompt B (Experimental)

| Параметр | Значение |
|-----------|-------|
| **Модель** | `gpt-4o-mini-2024-07-18` |
| **Temperature** | 0 |
| **Длина промпта** | 3000 символов |
| **Тип** | Experimental matching prompt with detailed criteria |

**Источник:** [`docs/prompt_evaluation/PROMPTS.md`](./PROMPTS.md) — полные тексты промптов

### Порядок выполнения workflow

```
Phase 0: Validation
    └── Check experiment exists
    └── Check dataset has expected pairs
Phase 1: Judge Run
    └── Create Judge Run record
    └── For each pair: call gpt-4.1
    └── Save reference_score, reference_decision, reference_reason
Phase 2: Prompt A Run
    └── Create Prompt A Run record
    └── For each pair: call gpt-4o-mini with Prompt A
    └── Save score, decision, latency_ms
Phase 3: Prompt B Run
    └── Create Prompt B Run record
    └── For each pair: call gpt-4o-mini with Prompt B
    └── Save score, decision, latency_ms
Phase 4: Calculate Metrics
    └── MAE_A, MAE_B, Latency_A, Latency_B, Accuracy_A, Accuracy_B
Phase 5: Generate Report
    └── Compare against acceptance criteria
    └── Output ACCEPT or REJECT decision
```

**Источник:** [`docs/prompt_evaluation/WORKFLOW_DESIGN.md`](./WORKFLOW_DESIGN.md)

---

## 3. Описание датасета

### Подтверждённый состав

```text
30 кандидатов
3 вакансии
90 пар кандидат-вакансия
```

**Источник:** [`database/03-seed-eval-dataset-v1.sql`](../../database/03-seed-eval-dataset-v1.sql)

### Распределение по типам кейсов

| Тип кейса | Кейсов | Пар с вакансиями |
|-----------|-------|---------------|
| `obvious_match` | 10 | 30 |
| `obvious_no_match` | 10 | 30 |
| `borderline` | 10 | 30 |


### Используемые вакансии

| ID вакансии | Название | Зарплатный диапазон |
|------------|-------|--------------|
| `3cc72567-e82a-4b5f-803a-497878f223b9` | Prompt Engineer / AI Automation Specialist | 120k-250k |
| `3f11544a-458c-4c1b-b853-702286378cec` | Специалист по разметке данных | 60k-120k |
| `43c55b9c-367e-4b40-9261-212c204b1872` | Системный аналитик | 150k-220k |


### Характеристики типов кейсов

#### obvious_match (10 кейсов)

- Точное совпадение должности или родственная позиция
- Все ключевые навыки совпадают
- Опыт в требуемом диапазоне
- Зарплата в бюджете вакансии
- Город совпадает или релокация

**Примеры:**
- Системный аналитик → Системный аналитик (точное совпадение)
- AI Engineer → Prompt Engineer (родственная позиция)


#### obvious_no_match (10 кейсов)

- Совершенно разные профессиональные области
- Навыки не совпадают
- Опыт не релевантен
- Зарплата вне бюджета

**Примеры:**
- Java Developer → Системный аналитик (разные роли)
- UI/UX Designer → Prompt Engineer (разные области)


#### borderline (10 кейсов)

- Частичное совпадение навыков
- Родственные позиции
- Недостаточный опыт
- Зарплата на границе бюджета
- Отсутствие ключевых навыков

**Примеры:**
- Business Analyst → Системный аналитик (родственная позиция, нет SQL)
- Junior Prompt Engineer → Prompt Engineer (опыт маленький, зарплата высокая)


---

## 4. Конвейер оценки

### Используемые таблицы БД

| Таблица | Назначение | Фаза |
|-------|---------|-------|
| `eval_prompt_datasets` | Метаданные датасета | Phase 0 |
| `eval_prompt_experiments` | Конфигурация эксперимента | Phase 0 |
| `eval_prompt_cases` | Кандидаты для тестирования | Все фазы |
| `eval_prompt_case_vacancies` | Пары кандидат-вакансия + reference scores | Все фазы |
| `eval_prompt_runs` | Отслеживание запусков (judge, A, B) | Phases 1-3 |
| `eval_prompt_results` | Результаты Prompt A/B | Phases 2-3 |

**Источник:** [`database/02-prompt-evaluation.sql`](../../database/02-prompt-evaluation.sql)

### Записи, создаваемые во время эксперимента

#### Phase 1: Judge Run

1. **eval_prompt_runs** — 1 запись:
   - `run_type = 'judge'`
   - `status = 'running'` → `'completed'`

2. **eval_prompt_case_vacancies** — 90 обновлений:
   - `reference_score` — заполнен
   - `reference_decision` — заполнен ('match' или 'no_match')
   - `reference_reason` — заполнен

#### Phase 2: Prompt A Run

1. **eval_prompt_runs** — 1 запись:
   - `run_type = 'A'`
   - `status = 'running'` → `'completed'`

2. **eval_prompt_results** — 90 записей:
   - `run_id`
   - `case_vacancy_id`
   - `score`
   - `decision`
   - `latency_ms`
   - `raw_response_json`

#### Phase 3: Prompt B Run

1. **eval_prompt_runs** — 1 запись:
   - `run_type = 'B'`
   - `status = 'running'` → `'completed'`

2. **eval_prompt_results** — 90 записей:
   - Та же структура, что и для Prompt A

**Источник:** [`docs/prompt_evaluation/WORKFLOW_IMPLEMENTATION.md`](./WORKFLOW_IMPLEMENTATION.md)

### Обновляемые поля

| Таблица | Поле | Фаза | Назначение |
|-------|-------|-------|---------|
| `eval_prompt_case_vacancies` | `reference_score` | Judge | Оценка Judge (0-100) |
| `eval_prompt_case_vacancies` | `reference_decision` | Judge | Решение Judge (match/no_match) |
| `eval_prompt_case_vacancies` | `reference_reason` | Judge | Обоснование Judge |
| `eval_prompt_runs` | `started_at` | Все | Время начала запуска |
| `eval_prompt_runs` | `completed_at` | Все | Время завершения запуска |
| `eval_prompt_runs` | `status` | Все | Статус запуска |
| `eval_prompt_results` | `score` | A, B | Оценка модели |
| `eval_prompt_results` | `decision` | A, B | Решение модели |
| `eval_prompt_results` | `latency_ms` | A, B | Время ответа в миллисекундах |
| `eval_prompt_results` | `raw_response_json` | A, B | Полный ответ JSON |

**Источник:** [`database/02-prompt-evaluation.sql`](../../database/02-prompt-evaluation.sql), строки 66-172

---

## 5. Определение метрик

### Primary Metric: Mean Absolute Score Error (MAE)

**Определение:**

```text
MAE = AVG(ABS(model_score - reference_score))
```

**Формула для Prompt A:**

```sql
MAE_A = AVG(ABS(a.score - cv.reference_score))
```

**Формула для Prompt B:**

```sql
MAE_B = AVG(ABS(b.score - cv.reference_score))
```

**Интерпретация:** Чем ниже — тем лучше. Среднее отклонение от оценки Judge.


### Guard Metric: Average Latency

**Определение:**

```text
Latency = AVG(response_time_ms)
```

**Формула для Prompt A:**

```sql
LATENCY_A = AVG(a.latency_ms)
```

**Формула для Prompt B:**

```sql
LATENCY_B = AVG(b.latency_ms)
```

**Интерпретация:** Чем ниже — тем лучше. Среднее время ответа на вызов.


### Secondary Metric: Decision Accuracy

**Определение:**

```text
Decision Accuracy = COUNT(model.decision = reference_decision) / COUNT(*)
```

**Назначение:** Только для дополнительной аналитики. Не используется для принятия решения.


### Minimum Detectable Effect (MDE)

**Правило:**

```text
Prompt B принимается, если MAE_B минимум на 20% ниже, чем MAE_A.
```

**Формула:**

```text
MAE_improvement = (MAE_A - MAE_B) / MAE_A
```

**Условие принятия:**

```text
MAE_improvement >= 0.20 (20%)
```


### Критерии принятия

**Оба условия должны быть выполнены:**

| Критерий | Порог | Условие |
|-----------|-----------|-----------|
| Primary Metric | Улучшение MAE | `>= 20%` |
| Guard Metric | Рост Latency | `<= 30%` |

**Правила финального решения:**

```text
ACCEPT PROMPT B: если MAE_improvement >= 20% И Latency_growth <= 30%
REJECT PROMPT B: если любое условие не выполнено
```


---

## 6. Реализация workflow

### Ключевые узлы

**Всего узлов:** 27 узлов

**По фазам:**

| Фаза | Узлов | Назначение |
|-------|-------|---------|
| Phase 0 | 4 | Validation |
| Phase 1 | 9 | Judge Run |
| Phase 2 | 9 | Prompt A Run |
| Phase 3 | 2 | Prompt B Run (placeholder → implemented) |
| Phase 4 | 1 | Calculate Metrics |
| Phase 5 | 2 | Generate Report |

**Источник:** [`docs/prompt_evaluation/WORKFLOW_IMPLEMENTATION.md`](./WORKFLOW_IMPLEMENTATION.md)

### Типы узлов

| Тип | Количество |
|------|-------|
| Manual Trigger | 1 |
| PostgreSQL | 12 |
| Code | 9 |
| HTTP Request | 2 |
| IF | 1 |
| Split In Batches | 2 |


### Цикл обработки

**Паттерн Split In Batches:**

```
Split In Batches (batch size: 1)
├── output 0 (done) → Complete Run → Next Phase
└── output 1 (loop) → Prepare Request
                      → HTTP: Call Model
                      → Parse Response
                      → Save Result
                      → Loop Continue
                      → Split In Batches (return)
```


### Пакетная обработка

- **Размер батча:** 1 (последовательная обработка)
- **Оценочное время:** ~10-15 минут для 90 пар
- **Judge Run:** ~4.5 мин (90 пар × ~3 сек)
- **Prompt A Run:** ~3 мин (90 пар × ~2 сек)
- **Prompt B Run:** ~3 мин (90 пар × ~2 сек)

**Источник:** [`docs/prompt_evaluation/WORKFLOW_IMPLEMENTATION.md`](./WORKFLOW_IMPLEMENTATION.md)

### Расчёт метрик

**SQL-запрос:**

```sql
WITH mae_a AS (
    SELECT AVG(ABS(r.score - cv.reference_score)) AS mae_a
    FROM eval_prompt_results r
    JOIN eval_prompt_case_vacancies cv ON r.case_vacancy_id = cv.id
    JOIN eval_prompt_runs run ON r.run_id = run.id
    WHERE run.run_type = 'A'
),
mae_b AS (
    SELECT AVG(ABS(r.score - cv.reference_score)) AS mae_b
    FROM eval_prompt_results r
    JOIN eval_prompt_case_vacancies cv ON r.case_vacancy_id = cv.id
    JOIN eval_prompt_runs run ON r.run_id = run.id
    WHERE run.run_type = 'B'
),
latency_a AS (
    SELECT AVG(r.latency_ms) AS latency_a
    FROM eval_prompt_results r
    JOIN eval_prompt_runs run ON r.run_id = run.id
    WHERE run.run_type = 'A'
),
latency_b AS (
    SELECT AVG(r.latency_ms) AS latency_b
    FROM eval_prompt_results r
    JOIN eval_prompt_runs run ON r.run_id = run.id
    WHERE run.run_type = 'B'
),
accuracy_a AS (
    SELECT COUNT(*) FILTER (WHERE r.decision = cv.reference_decision)::NUMERIC / COUNT(*) AS accuracy_a
    FROM eval_prompt_results r
    JOIN eval_prompt_case_vacancies cv ON r.case_vacancy_id = cv.id
    JOIN eval_prompt_runs run ON r.run_id = run.id
    WHERE run.run_type = 'A'
),
accuracy_b AS (
    SELECT COUNT(*) FILTER (WHERE r.decision = cv.reference_decision)::NUMERIC / COUNT(*) AS accuracy_b
    FROM eval_prompt_results r
    JOIN eval_prompt_case_vacancies cv ON r.case_vacancy_id = cv.id
    JOIN eval_prompt_runs run ON r.run_id = run.id
    WHERE run.run_type = 'B'
)
SELECT
    mae_a.mae_a,
    mae_b.mae_b,
    (mae_a.mae_a - mae_b.mae_b) / NULLIF(mae_a.mae_a, 0) AS mae_improvement,
    latency_a.latency_a,
    latency_b.latency_b,
    (latency_b.latency_b - latency_a.latency_a) / NULLIF(latency_a.latency_a, 0) AS latency_growth,
    accuracy_a.accuracy_a,
    accuracy_b.accuracy_b
FROM mae_a, mae_b, latency_a, latency_b, accuracy_a, accuracy_b;
```

**Источник:** [`docs/prompt_evaluation/WORKFLOW_IMPLEMENTATION.md`](./WORKFLOW_IMPLEMENTATION.md)

### Генерация финального отчёта

**Формат отчёта:** Markdown

**Структура:**
1. Метаданные эксперимента
2. Используемые модели
3. Статистика датасета
4. Результаты (MAE, Latency, Accuracy)
5. Проверка критериев принятия
6. Финальное решение (ACCEPT/REJECT)
7. Детальная статистика

**Источник:** [`docs/prompt_evaluation/WORKFLOW_DESIGN.md`](./WORKFLOW_DESIGN.md)

---

## 7. Smoke Run

### Назначение

Валидация корректности workflow перед полным экспериментентом:
- Тестирование всех фаз
- Проверка конвертации типов
- Проверка расчёта latency
- Подтверждение SQL-запросов
- Валидация генерации отчёта


### Конфигурация Smoke

| Параметр | Значение |
|-----------|-------|
| **Код датасета** | `HRA-EVAL-SMOKE` |
| **Код эксперимента** | `HRA-EXP-SMOKE` |
| **Пар** | 1 |


### Найденные дефекты

| Дефект | Проблема | Исправление |
|--------|---------|-----|
| **Дефект 1** | IF сравнивал строки вместо чисел | `Number($json.total_pairs)` и `Number($('Run Config').first().json.expected_pairs)` |
| **Дефект 2** | OpenAI temperature — строка вместо числа | `Number(experimentData.temperature_X ?? 0)` |
| **Дефект 3** | latency_ms = timestamp вместо duration | Явный расчёт через `request_started_at` |


### Результаты Smoke

**Тестовый кейс:**
- Тип: `obvious_match`
- Кандидат: Системный аналитик, 5 лет опыта
- Вакансия: Системный аналитик, 150–220k

**Оценка Judge:** 98 (match)

| Метрика | Prompt A | Prompt B |
|--------|----------|----------|
| **Score** | 100 | 97 |
| **Decision** | match | match |
| **Latency** | 2,092 ms | 2,284 ms |

| Метрика | Prompt A | Prompt B | Улучшение/Рост |
|--------|----------|----------|-------------------|
| **MAE** | 2.00 | 1.00 | 50.00% ↓ |
| **Latency** | 2,092 ms | 2,284 ms | +9.18% |
| **Accuracy** | 100% | 100% | — |

**Решение Smoke:** ✅ Все критерии пройдены


---

## 8. Результаты полного запуска

### Подтверждённые финальные значения (источник: Production Database)

| Метрика | Prompt A | Prompt B |
|--------|----------|----------|
| **MAE** | 10.3000 | 15.7444 |
| **Latency** | 2,049.77 ms | 2,241.19 ms |
| **Accuracy** | 95.56% (86/90) | 94.44% (85/90) |

### Анализ метрик

| Метрика | Значение | Порог | Статус |
|--------|-------|-----------|--------|
| **Улучшение MAE** | -52.86% | ≥ 20% | ❌ **FAIL** |
| **Рост Latency** | +9.34% | ≤ 30% | ✅ PASS |

**Формула улучшения MAE:**
```text
MAE_improvement = (MAE_A - MAE_B) / MAE_A
MAE_improvement = (10.3000 - 15.7444) / 10.3000 = -0.5286 (-52.86%)
```

**Интерпретация:** Отрицательное улучшение означает, что Prompt B имеет **на 52.86% большую ошибку**, чем Prompt A.

### Статистика запусков

| Тип запуска | Статус | Результаты | Длительность |
|----------|--------|---------|----------|
| Judge | completed | 90 references | ~4 min |
| Prompt A | completed | 90 results | ~3 min |
| Prompt B | completed | 90 results | ~3 min |

### Анализ решения

**Проверка Primary Metric:**
- Требуется: улучшение MAE ≥ 20%
- Фактически: ухудшение на 52.86%
- Результат: ❌ FAIL

**Проверка Guard Metric:**
- Требуется: рост Latency ≤ 30%
- Фактически: рост Latency 9.34%
- Результат: ✅ PASS

### Финальное решение

```text
REJECT PROMPT B
```

**Причина:** Порог primary metric не достигнут. Prompt B работает значительно хуже, чем Prompt A:
- MAE увеличился на 52.86% (с 10.3 до 15.74)
- Accuracy снизилась на 1.12 процентных пункта (с 95.56% до 94.44%)
- Latency увеличилась на 9.34% (приемлемо, но не имеет значения, так как primary metric не пройдена)

**Вывод:** Prompt B (экспериментальный промпт с детальными инструкциями и примерами) не улучшает Prompt A (production промпт с краткими инструкциями). Гипотеза о том, что более детальные промпты улучшают скоринг, не подтвердилась.

**Источник:** Production PostgreSQL database, запрос выполнен 2026-06-25

---

## 9. Инвентарь источников

### Файлы БД

| Файл | Назначение |
|------|---------|
| `database/02-prompt-evaluation.sql` | Схема для eval таблиц |
| `database/03-seed-eval-dataset-v1.sql` | Датасет HRA-EVAL-V1 seeding |
| `database/04-create-experiment-v1.sql` | Эксперимент HRA-EXP-V1 creation |
| `database/05-create-smoke-experiment.sql` | Smoke датасет и эксперимент |
| `database/schema_hr_assistant.sql` | Основная схема HRA |
| `database/README.md` | Документация БД |

### Файлы workflow

| Файл | Назначение |
|------|---------|
| `workflows/HRA Prompt Evaluation Experiment.json` | Определение n8n workflow |

### Файлы промптов

| Файл | Назначение |
|------|---------|
| [`docs/prompt_evaluation/PROMPTS.md`](./PROMPTS.md) | Полные тексты Judge, Prompt A, Prompt B |

### Файлы документации

| Файл | Назначение |
|------|---------|
| `docs/prompt_evaluation/WORKFLOW_DESIGN.md` | Документ проектирования workflow |
| `docs/prompt_evaluation/WORKFLOW_IMPLEMENTATION.md` | Детали реализации |

---

## Appendix A: Prompt A (Production)

```
Ты HR matching assistant.

Сравни кандидата и вакансию по критериям:

1. Должность / роль — 30 баллов
2. Навыки — 35 баллов
3. Опыт — 20 баллов
4. Город / формат / зарплатные ожидания — 15 баллов

Итоговый score должен быть от 0 до 100.

Правила:
- score >= 60 → decision = "match"
- score < 60 → decision = "no_match"
- не выдумывай навыки и опыт
- если данных недостаточно, снижай score
- reason должен кратко объяснять, почему выставлен такой score

Верни строго JSON по схеме.
```

**Длина:** 480 символов

**Источник:** [`database/04-create-experiment-v1.sql`](../../database/04-create-experiment-v1.sql), строки 34-52

---

## Appendix B: Различия между Prompt B и Prompt A

| Аспект | Prompt A | Prompt B |
|--------|----------|----------|
| **Структура** | Краткий список критериев | Детальные шкалы оценки |
| **Примеры** | Нет | 3 примера (obvious_match, obvious_no_match, borderline) |
| **Веса** | Упомянуты, не детализированы | Явная таблица с весами |
| **Правила** | Краткие | Детальные правила с примерами |
| **Обоснование** | Краткое объяснение | Явное требование для каждого критерия |
| **Длина** | 480 символов | 3000 символов |

**Источник:** [`docs/prompt_evaluation/PROMPTS.md`](./PROMPTS.md) — полные тексты промптов, строки 264-273

---

## Appendix C: JSON Schema для ответа модели

```json
{
  "type": "object",
  "additionalProperties": false,
  "properties": {
    "vacancy_id": { "type": ["string", "null"] },
    "title": { "type": ["string", "null"] },
    "role_score": { "type": "number", "description": "Оценка по должности (0-30)" },
    "skills_score": { "type": "number", "description": "Оценка по навыкам (0-35)" },
    "experience_score": { "type": "number", "description": "Оценка по опыту (0-20)" },
    "conditions_score": { "type": "number", "description": "Оценка по условиям (0-15)" },
    "score": { "type": "number", "description": "Итоговый score (сумма компонент, 0-100)" },
    "decision": { "type": "string", "enum": ["match", "no_match"] },
    "reason": { "type": "string", "description": "Краткое обоснование решения" }
  },
  "required": ["vacancy_id", "title", "role_score", "skills_score",
               "experience_score", "conditions_score", "score",
               "decision", "reason"]
}
```

**Источник:** [`docs/prompt_evaluation/PROMPTS.md`](./PROMPTS.md), строки 88-143

---

## Статус документа

| Секция | Статус |
|---------|--------|
| 1. Контекст эксперимента | ✅ Завершено |
| 2. Дизайн эксперимента | ✅ Завершено |
| 3. Описание датасета | ✅ Завершено |
| 4. Конвейер оценки | ✅ Завершено |
| 5. Определение метрик | ✅ Завершено |
| 6. Реализация workflow | ✅ Завершено |
| 7. Smoke Run | ✅ Завершено |
| 8. Результаты полного запуска | ✅ Завершено (верифицировано по БД) |
| 9. Инвентарь источников | ✅ Завершено |

---

*Документ сгенерирован из исходных файлов и production базы данных 2026-06-25*