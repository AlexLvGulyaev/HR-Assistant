# HRA Prompt Evaluation Experiment Workflow

**Version:** 1.0
**Created:** 2026-06-25
**Status:** Design

---

## Overview

Workflow для проведения A/B-тестирования matching prompt в HR Assistant.

**Цель:** Сравнить production matching prompt (A) с experimental prompt (B) и определить, можно ли заменить production prompt на новый.

**Методология:**
- Judge model (gpt-4.1) создаёт reference scoring для всех пар
- Prompt A и Prompt B запускаются независимо на тех же парах
- Сравниваются метрики MAE (Mean Absolute Score Error) и Latency
- Решение о принятии Prompt B на основе MDE (Minimum Detectable Effect)

---

## Experiment Design

### Models

| Run | Model | Temperature | Purpose |
|-----|-------|-------------|---------|
| **Judge** | gpt-4.1-2025-04-14 | 0 | Reference scoring |
| **Prompt A** | gpt-4o-mini-2024-07-18 | 0 | Production prompt |
| **Prompt B** | gpt-4o-mini-2024-07-18 | 0 | Experimental prompt |

### Dataset

**Code:** HRA-EVAL-V1
**Size:** 30 candidates × 3 vacancies = 90 pairs
**Types:**
- 10 obvious_match cases
- 10 obvious_no_match cases
- 10 borderline cases

### Metrics

| Metric | Type | Description | Formula |
|--------|------|-------------|---------|
| **MAE** | Primary | Mean Absolute Score Error | `AVG(ABS(model.score - reference_score))` |
| **Latency** | Guard | Average response time | `AVG(latency_ms)` |
| **Decision Accuracy** | Secondary | Match/no_match accuracy | `COUNT(model.decision = reference_decision) / COUNT(*)` |

### Acceptance Criteria

**Primary Metric:**
- MAE improvement ≥ 20%: `MAE_B ≤ 0.8 × MAE_A`

**Guard Metric:**
- Latency growth ≤ 30%: `Latency_B ≤ 1.3 × Latency_A`

**Final Decision:**
- Accept Prompt B if **BOTH** conditions are met
- Reject Prompt B if **ANY** condition fails

---

## Workflow Steps

### Phase 0: Prerequisites

**Check:**
- [ ] Dataset HRA-EVAL-V1 exists
- [ ] 90 pairs in eval_prompt_case_vacancies
- [ ] Experiment HRA-EXP-V1 created
- [ ] All prompts defined

**SQL:**
```sql
-- Check dataset
SELECT COUNT(*) FROM eval_prompt_cases c
JOIN eval_prompt_datasets d ON c.dataset_id = d.id
WHERE d.dataset_code = 'HRA-EVAL-V1';
-- Expected: 30

-- Check pairs
SELECT COUNT(*) FROM eval_prompt_case_vacancies cv
JOIN eval_prompt_cases c ON cv.case_id = c.id
JOIN eval_prompt_datasets d ON c.dataset_id = d.id
WHERE d.dataset_code = 'HRA-EVAL-V1';
-- Expected: 90

-- Check experiment
SELECT * FROM eval_prompt_experiments e
JOIN eval_prompt_datasets d ON e.dataset_id = d.id
WHERE d.dataset_code = 'HRA-EVAL-V1';
-- Expected: 1 row
```

---

### Phase 1: Judge Run

**Purpose:** Fill reference_score, reference_decision, reference_reason for all pairs

**Steps:**
1. Create Judge Run record
2. For each pair (candidate × vacancy):
   - Call gpt-4.1 with judge prompt
   - Parse response JSON
   - Extract score, decision, reason
   - Calculate latency
   - Update reference fields in eval_prompt_case_vacancies
3. Mark Judge Run as completed

**SQL:**
```sql
-- Create Judge Run
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

-- Get run_id
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

**Update reference fields:**
```sql
-- Update reference fields after Judge call
UPDATE eval_prompt_case_vacancies
SET
    reference_score = {{ $json.parsed.score }},
    reference_decision = '{{ $json.parsed.decision }}',
    reference_reason = '{{ $json.parsed.reason }}'
WHERE id = '{{ $json.case_vacancy_id }}';
```

**Mark Judge Run completed:**
```sql
UPDATE eval_prompt_runs
SET
    status = 'completed',
    completed_at = now()
WHERE id = '{{ $json.run_id }}';
```

---

### Phase 2: Prompt A Run

**Purpose:** Run production prompt on all pairs

**Steps:**
1. Create Prompt A Run record
2. For each pair:
   - Call gpt-4o-mini with Prompt A
   - Parse response JSON
   - Insert result into eval_prompt_results
   - Record latency
3. Mark Prompt A Run as completed

**SQL:**
```sql
-- Create Prompt A Run
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

**Insert results:**
```sql
-- Insert result for each pair
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

**Purpose:** Run experimental prompt on all pairs

**Steps:**
Same as Phase 2, but with Prompt B

---

### Phase 4: Calculate Metrics

**Purpose:** Calculate MAE, Latency, Decision Accuracy for both prompts

**SQL:**
```sql
-- Calculate MAE for Prompt A
WITH mae_a AS (
    SELECT
        AVG(ABS(r.score - cv.reference_score)) AS mae_a
    FROM eval_prompt_results r
    JOIN eval_prompt_case_vacancies cv ON r.case_vacancy_id = cv.id
    JOIN eval_prompt_runs run ON r.run_id = run.id
    WHERE run.run_type = 'A'
),

-- Calculate MAE for Prompt B
mae_b AS (
    SELECT
        AVG(ABS(r.score - cv.reference_score)) AS mae_b
    FROM eval_prompt_results r
    JOIN eval_prompt_case_vacancies cv ON r.case_vacancy_id = cv.id
    JOIN eval_prompt_runs run ON r.run_id = run.id
    WHERE run.run_type = 'B'
),

-- Calculate Latency for Prompt A
latency_a AS (
    SELECT
        AVG(r.latency_ms) AS latency_a
    FROM eval_prompt_results r
    JOIN eval_prompt_runs run ON r.run_id = run.id
    WHERE run.run_type = 'A'
),

-- Calculate Latency for Prompt B
latency_b AS (
    SELECT
        AVG(r.latency_ms) AS latency_b
    FROM eval_prompt_results r
    JOIN eval_prompt_runs run ON r.run_id = run.id
    WHERE run.run_type = 'B'
),

-- Calculate Decision Accuracy for Prompt A
accuracy_a AS (
    SELECT
        COUNT(*) FILTER (WHERE r.decision = cv.reference_decision)::NUMERIC / COUNT(*) AS accuracy_a
    FROM eval_prompt_results r
    JOIN eval_prompt_case_vacancies cv ON r.case_vacancy_id = cv.id
    JOIN eval_prompt_runs run ON r.run_id = run.id
    WHERE run.run_type = 'A'
),

-- Calculate Decision Accuracy for Prompt B
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

**Purpose:** Create comprehensive experiment report

**Report Contents:**
1. Experiment metadata (code, dataset, models)
2. Metrics summary (MAE, Latency, Accuracy)
3. Acceptance criteria check
4. Final decision
5. Detailed statistics

**Report Template:**
```markdown
# HRA Prompt Evaluation Report

**Experiment Code:** HRA-EXP-V1
**Dataset:** HRA-EVAL-V1
**Date:** {{ date }}

---

## Models

| Run | Model | Temperature |
|-----|-------|-------------|
| Judge | gpt-4.1-2025-04-14 | 0 |
| Prompt A | gpt-4o-mini-2024-07-18 | 0 |
| Prompt B | gpt-4o-mini-2024-07-18 | 0 |

---

## Dataset

- **Total pairs:** 90
- **Obvious match:** 30
- **Obvious no_match:** 30
- **Borderline:** 30

---

## Results

### Primary Metric: Mean Absolute Score Error

| Metric | Prompt A | Prompt B |
|--------|----------|----------|
| **MAE** | {{ mae_a }} | {{ mae_b }} |
| **Improvement** | - | {{ mae_improvement }} |

### Guard Metric: Average Latency

| Metric | Prompt A | Prompt B |
|--------|----------|----------|
| **Latency (ms)** | {{ latency_a }} | {{ latency_b }} |
| **Growth** | - | {{ latency_growth }} |

### Secondary Metric: Decision Accuracy

| Metric | Prompt A | Prompt B |
|--------|----------|----------|
| **Accuracy** | {{ accuracy_a }} | {{ accuracy_b }} |

---

## Acceptance Criteria

| Criterion | Threshold | Actual | Status |
|-----------|-----------|--------|--------|
| MAE improvement | ≥ 20% | {{ mae_improvement }} | {{ status }} |
| Latency growth | ≤ 30% | {{ latency_growth }} | {{ status }} |

---

## Final Decision

{{ final_decision }}

**Reason:** {{ reason }}

---

## Detailed Statistics

### Score Distribution

| Statistic | Judge | Prompt A | Prompt B |
|-----------|-------|----------|----------|
| Mean | {{ judge_mean }} | {{ a_mean }} | {{ b_mean }} |
| Stddev | {{ judge_stddev }} | {{ a_stddev }} | {{ b_stddev }} |
| Min | {{ judge_min }} | {{ a_min }} | {{ b_min }} |
| Max | {{ judge_max }} | {{ a_max }} | {{ b_max }} |

### Error Analysis

| Category | Prompt A Error | Prompt B Error |
|----------|----------------|----------------|
| role_score | {{ a_role_error }} | {{ b_role_error }} |
| skills_score | {{ a_skills_error }} | {{ b_skills_error }} |
| experience_score | {{ a_exp_error }} | {{ b_exp_error }} |
| conditions_score | {{ a_cond_error }} | {{ b_cond_error }} |
```

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
| `PROMPT_EVALUATION_WORKFLOW.md` | This document |

---

## References

- Project Decision: [task_history/2026-06-24_decision-hra-prompt-evaluation-metrics.md](../task_history/2026-06-24_decision-hra-prompt-evaluation-metrics.md)
- Dataset: HRA-EVAL-V1 (30 candidates × 3 vacancies)
- Production Prompt A: From HR Processing Worker workflow