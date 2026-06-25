# Проектирование workflow эксперимента HRA Prompt Evaluation

**Версия:** 1.0
**Создан:** 2026-06-25
**Статус:** Design

---

## Обзор

Workflow для проведения A/B-тестирования matching prompt в HR Assistant.

**Цель:** Сравнить production matching prompt (A) с experimental prompt (B) и определить, можно ли заменить production prompt на новый.

**Методология:**
- Judge model (gpt-4.1) создаёт reference scoring для всех пар
- Prompt A и Prompt B запускаются независимо на тех же парах
- Сравниваются метрики MAE (Mean Absolute Score Error) и Latency
- Решение о принятии Prompt B на основе MDE (Minimum Detectable Effect)

---

## Дизайн эксперимента

### Модели

| Run | Model | Temperature | Назначение |
|-----|-------|-------------|---------|
| **Judge** | gpt-4.1-2025-04-14 | 0 | Reference scoring |
| **Prompt A** | gpt-4o-mini-2024-07-18 | 0 | Production prompt |
| **Prompt B** | gpt-4o-mini-2024-07-18 | 0 | Experimental prompt |

### Датасет

**Код:** HRA-EVAL-V1
**Размер:** 30 кандидатов × 3 вакансии = 90 пар
**Типы:**
- 10 obvious_match кейсов
- 10 obvious_no_match кейсов
- 10 borderline кейсов

### Метрики

| Метрика | Тип | Описание | Формула |
|--------|------|-------------|---------|
| **MAE** | Primary | Mean Absolute Score Error | `AVG(ABS(model.score - reference_score))` |
| **Latency** | Guard | Среднее время ответа | `AVG(latency_ms)` |
| **Decision Accuracy** | Secondary | Точность match/no_match | `COUNT(model.decision = reference_decision) / COUNT(*)` |

### Критерии принятия

**Primary Metric:**
- Улучшение MAE ≥ 20%: `MAE_B ≤ 0.8 × MAE_A`

**Guard Metric:**
- Рост Latency ≤ 30%: `Latency_B ≤ 1.3 × Latency_A`

**Финальное решение:**
- Принять Prompt B, если **ОБА** условия выполнены
- Отклонить Prompt B, если **ЛЮБОЕ** условие не выполнено

---

## Шаги workflow

### Phase 0: Предварительные требования

**Проверка:**
- [ ] Датасет HRA-EVAL-V1 существует
- [ ] 90 пар в eval_prompt_case_vacancies
- [ ] Эксперимент HRA-EXP-V1 создан
- [ ] Все промпты определены

**SQL:**
```sql
-- Проверка датасета
SELECT COUNT(*) FROM eval_prompt_cases c
JOIN eval_prompt_datasets d ON c.dataset_id = d.id
WHERE d.dataset_code = 'HRA-EVAL-V1';
-- Ожидается: 30

-- Проверка пар
SELECT COUNT(*) FROM eval_prompt_case_vacancies cv
JOIN eval_prompt_cases c ON cv.case_id = c.id
JOIN eval_prompt_datasets d ON c.dataset_id = d.id
WHERE d.dataset_code = 'HRA-EVAL-V1';
-- Ожидается: 90

-- Проверка эксперимента
SELECT * FROM eval_prompt_experiments e
JOIN eval_prompt_datasets d ON e.dataset_id = d.id
WHERE d.dataset_code = 'HRA-EVAL-V1';
-- Ожидается: 1 строка
```

---

### Phase 1: Judge Run

**Назначение:** Заполнить reference_score, reference_decision, reference_reason для всех пар

**Шаги:**
1. Создать запись Judge Run
2. Для каждой пары (кандидат × вакансия):
   - Вызвать gpt-4.1 с judge prompt
   - Разобрать JSON-ответ
   - Извлечь score, decision, reason
   - Рассчитать latency
   - Обновить reference-поля в eval_prompt_case_vacancies
3. Пометить Judge Run как завершённый

**SQL:**
```sql
-- Создать Judge Run
INSERT INTO eval_prompt_runs (
    id,
    experiment_id,
    run_type,
    status,
    started_at,
    created_at
)
SELECT
    gen_random_uuid(),
    e.id,
    'judge',
    'running',
    now(),
    now()
FROM eval_prompt_experiments e
JOIN eval_prompt_datasets d ON e.dataset_id = d.id
WHERE d.dataset_code = 'HRA-EVAL-V1';

-- Получить run_id
SELECT id FROM eval_prompt_runs
WHERE run_type = 'judge'
  AND status = 'running'
ORDER BY created_at DESC
LIMIT 1;
```

**n8n Workflow:**

```javascript
// Node: Prepare Judge Request
const pairs = $('Get Pairs Without Reference').all();

return pairs.map(pair => {
  const candidate = pair.json.candidate_json;
  const vacancy = pair.json.vacancy_json;

  return {
    json: {
      case_vacancy_id: pair.json.id,
      openai_body: {
        model: 'gpt-4.1-2025-04-14',
        temperature: 0,
        messages: [
          {
            role: 'system',
            content: judgePromptText  // from experiment
          },
          {
            role: 'user',
            content: `Кандидат:\n${JSON.stringify(candidate, null, 2)}\n\nВакансия:\n${JSON.stringify(vacancy, null, 2)}\n\nПроведи детальную оценку соответствия кандидата вакансии по критериям:\n1. Должность / роль (0-30 баллов)\n2. Навыки (0-35 баллов)\n3. Опыт (0-20 баллов)\n4. Город / формат / зарплата (0-15 баллов)\n\nВерни JSON с оценками и обоснованием.`
          }
        ],
        response_format: {
          type: 'json_schema',
          json_schema: {
            name: 'judge_evaluation_result',
            strict: true,
            schema: {
              type: 'object',
              additionalProperties: false,
              properties: {
                vacancy_id: { type: ['string', 'null'] },
                title: { type: ['string', 'null'] },
                role_score: { type: 'number' },
                skills_score: { type: 'number' },
                experience_score: { type: 'number' },
                conditions_score: { type: 'number' },
                score: { type: 'number' },
                decision: {
                  type: 'string',
                  enum: ['match', 'no_match']
                },
                reason: { type: 'string' }
              },
              required: ['vacancy_id', 'title', 'role_score', 'skills_score',
                         'experience_score', 'conditions_score', 'score',
                         'decision', 'reason']
            }
          }
        }
      }
    }
  };
});
```

**Обновление reference-полей:**
```sql
-- Обновить reference-поля после вызова Judge
UPDATE eval_prompt_case_vacancies
SET
    reference_score = {{ $json.parsed.score }},
    reference_decision = '{{ $json.parsed.decision }}',
    reference_reason = '{{ $json.parsed.reason }}'
WHERE id = '{{ $json.case_vacancy_id }}';
```

**Пометить Judge Run завершённым:**
```sql
UPDATE eval_prompt_runs
SET
    status = 'completed',
    completed_at = now()
WHERE id = '{{ $json.run_id }}';
```

---

### Phase 2: Prompt A Run

**Назначение:** Запустить production prompt на всех парах

**Шаги:**
1. Создать запись Prompt A Run
2. Для каждой пары:
   - Вызвать gpt-4o-mini с Prompt A
   - Разобрать JSON-ответ
   - Вставить результат в eval_prompt_results
   - Записать latency
3. Пометить Prompt A Run как завершённый

**SQL:**
```sql
-- Создать Prompt A Run
INSERT INTO eval_prompt_runs (
    id,
    experiment_id,
    run_type,
    status,
    started_at,
    created_at
)
SELECT
    gen_random_uuid(),
    e.id,
    'A',
    'running',
    now(),
    now()
FROM eval_prompt_experiments e
JOIN eval_prompt_datasets d ON e.dataset_id = d.id
WHERE d.dataset_code = 'HRA-EVAL-V1';
```

**Вставка результатов:**
```sql
-- Вставить результат для каждой пары
INSERT INTO eval_prompt_results (
    id,
    run_id,
    case_vacancy_id,
    score,
    decision,
    latency_ms,
    raw_response_json,
    created_at
)
VALUES (
    gen_random_uuid(),
    '{{ $json.run_id }}',
    '{{ $json.case_vacancy_id }}',
    {{ $json.parsed.score }},
    '{{ $json.parsed.decision }}',
    {{ $json.latency_ms }},
    '{{ JSON.stringify($json.parsed) }}'::jsonb,
    now()
);
```

---

### Phase 3: Prompt B Run

**Назначение:** Запустить experimental prompt на всех парах

**Шаги:**
Те же, что и для Phase 2, но с Prompt B

---

### Phase 4: Calculate Metrics

**Назначение:** Рассчитать MAE, Latency, Decision Accuracy для обоих промптов

**SQL:**
```sql
-- Рассчитать MAE для Prompt A
WITH mae_a AS (
    SELECT
        AVG(ABS(r.score - cv.reference_score)) AS mae_a
    FROM eval_prompt_results r
    JOIN eval_prompt_case_vacancies cv ON r.case_vacancy_id = cv.id
    JOIN eval_prompt_runs run ON r.run_id = run.id
    WHERE run.run_type = 'A'
),

-- Рассчитать MAE для Prompt B
mae_b AS (
    SELECT
        AVG(ABS(r.score - cv.reference_score)) AS mae_b
    FROM eval_prompt_results r
    JOIN eval_prompt_case_vacancies cv ON r.case_vacancy_id = cv.id
    JOIN eval_prompt_runs run ON r.run_id = run.id
    WHERE run.run_type = 'B'
),

-- Рассчитать Latency для Prompt A
latency_a AS (
    SELECT
        AVG(r.latency_ms) AS latency_a
    FROM eval_prompt_results r
    JOIN eval_prompt_runs run ON r.run_id = run.id
    WHERE run.run_type = 'A'
),

-- Рассчитать Latency для Prompt B
latency_b AS (
    SELECT
        AVG(r.latency_ms) AS latency_b
    FROM eval_prompt_results r
    JOIN eval_prompt_runs run ON r.run_id = run.id
    WHERE run.run_type = 'B'
),

-- Рассчитать Decision Accuracy для Prompt A
accuracy_a AS (
    SELECT
        COUNT(*) FILTER (WHERE r.decision = cv.reference_decision)::NUMERIC / COUNT(*) AS accuracy_a
    FROM eval_prompt_results r
    JOIN eval_prompt_case_vacancies cv ON r.case_vacancy_id = cv.id
    JOIN eval_prompt_runs run ON r.run_id = run.id
    WHERE run.run_type = 'A'
),

-- Рассчитать Decision Accuracy для Prompt B
accuracy_b AS (
    SELECT
        COUNT(*) FILTER (WHERE r.decision = cv.reference_decision)::NUMERIC / COUNT(*) AS accuracy_b
    FROM eval_prompt_results r
    JOIN eval_prompt_case_vacancies cv ON r.case_vacancy_id = cv.id
    JOIN eval_prompt_runs run ON r.run_id = run.id
    WHERE run.run_type = 'B'
)

SELECT
    mae_a.mae_a,
    mae_b.mae_b,
    (mae_a.mae_a - mae_b.mae_b) / mae_a.mae_a AS mae_improvement,
    latency_a.latency_a,
    latency_b.latency_b,
    (latency_b.latency_b - latency_a.latency_a) / latency_a.latency_a AS latency_growth,
    accuracy_a.accuracy_a,
    accuracy_b.accuracy_b
FROM mae_a, mae_b, latency_a, latency_b, accuracy_a, accuracy_b;
```

---

### Phase 5: Generate Report

**Назначение:** Создать комплексный отчёт об эксперименте

**Содержимое отчёта:**
1. Метаданные эксперимента (код, датасет, модели)
2. Сводка метрик (MAE, Latency, Accuracy)
3. Проверка критериев принятия
4. Финальное решение
5. Детальная статистика

#### Заголовок

```markdown
# HRA Prompt Evaluation Report

**Experiment Code:** HRA-EXP-V1
**Dataset:** HRA-EVAL-V1
**Date:** {{ date }}
```

#### Модели

| Run | Model | Temperature |
|-----|-------|-------------|
| Judge | gpt-4.1-2025-04-14 | 0 |
| Prompt A | gpt-4o-mini-2024-07-18 | 0 |
| Prompt B | gpt-4o-mini-2024-07-18 | 0 |

#### Датасет

- **Всего пар:** 90
- **Obvious match:** 30
- **Obvious no_match:** 30
- **Borderline:** 30

#### Primary Metric: Mean Absolute Score Error

| Metric | Prompt A | Prompt B |
|--------|----------|----------|
| **MAE** | {{ mae_a }} | {{ mae_b }} |
| **Improvement** | - | {{ mae_improvement }} |

#### Guard Metric: Average Latency

| Metric | Prompt A | Prompt B |
|--------|----------|----------|
| **Latency (ms)** | {{ latency_a }} | {{ latency_b }} |
| **Growth** | - | {{ latency_growth }} |

#### Secondary Metric: Decision Accuracy

| Metric | Prompt A | Prompt B |
|--------|----------|----------|
| **Accuracy** | {{ accuracy_a }} | {{ accuracy_b }} |

#### Acceptance Criteria

| Criterion | Threshold | Actual | Status |
|-----------|-----------|--------|--------|
| MAE improvement | ≥ 20% | {{ mae_improvement }} | {{ status }} |
| Latency growth | ≤ 30% | {{ latency_growth }} | {{ status }} |

#### Final Decision

```markdown
{{ final_decision }}

**Reason:** {{ reason }}
```

#### Detailed Statistics

##### Score Distribution

| Statistic | Judge | Prompt A | Prompt B |
|-----------|-------|----------|----------|
| Mean | {{ judge_mean }} | {{ a_mean }} | {{ b_mean }} |
| Stddev | {{ judge_stddev }} | {{ a_stddev }} | {{ b_stddev }} |
| Min | {{ judge_min }} | {{ a_min }} | {{ b_min }} |
| Max | {{ judge_max }} | {{ a_max }} | {{ b_max }} |

##### Error Analysis

| Category | Prompt A Error | Prompt B Error |
|----------|----------------|----------------|
| role_score | {{ a_role_error }} | {{ b_role_error }} |
| skills_score | {{ a_skills_error }} | {{ b_skills_error }} |
| experience_score | {{ a_exp_error }} | {{ b_exp_error }} |
| conditions_score | {{ a_cond_error }} | {{ b_cond_error }} |

---

## Implementation Notes

### Error Handling

1. **LLM Call Failures:**
   - Retry with exponential backoff
   - Record error in eval_prompt_results.error_message
   - Continue with next pair

2. **JSON Parsing Errors:**
   - Try to extract JSON from response
   - Fallback to default values
   - Record in raw_response_json

3. **Timeout:**
   - Set 30-second timeout per LLM call
   - Record latency even for failures

### Concurrency

- Judge Run: Sequential (one model, one run)
- Prompt A Run: Sequential
- Prompt B Run: Sequential
- No parallel execution within a run

### Cost Management

**Estimated API Calls:**
- Judge: 90 calls × gpt-4.1
- Prompt A: 90 calls × gpt-4o-mini
- Prompt B: 90 calls × gpt-4o-mini
- **Total:** 270 LLM calls

**Estimated Cost:**
- Judge: ~$2-5
- Prompt A: ~$0.50-1
- Prompt B: ~$0.50-1
- **Total:** ~$3-7

---

## Files

| File | Purpose |
|------|---------|
| `04-create-experiment-v1.sql` | Create experiment record |
| [`docs/prompt_evaluation/PROMPTS.md`](./PROMPTS.md) | Полные тексты промптов |

---

## References

- [Database Schema](../../database/README.md)
- [Workflow Implementation](./WORKFLOW_IMPLEMENTATION.md)
- [Промпты](./PROMPTS.md)