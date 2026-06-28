# Teacher Dataset Report
**Date:** 2026-06-28
**Experiment:** HRA-EXP-V2

## Summary

- **Total records:** 90
- **Train:** 72
- **Validation:** 9
- **Test:** 9

## Distribution by Groups

### Train

- **obvious_match:** 24
- **borderline:** 24
- **obvious_no_match:** 24

### Validation

- **obvious_match:** 3
- **borderline:** 3
- **obvious_no_match:** 3

### Test

- **obvious_match:** 3
- **borderline:** 3
- **obvious_no_match:** 3

## Case Codes by Split

### Train

```
HRA-EVAL-V2-000001, HRA-EVAL-V2-000001, HRA-EVAL-V2-000001, HRA-EVAL-V2-000002, HRA-EVAL-V2-000002, HRA-EVAL-V2-000002, HRA-EVAL-V2-000003, HRA-EVAL-V2-000003, HRA-EVAL-V2-000003, HRA-EVAL-V2-000004, HRA-EVAL-V2-000004, HRA-EVAL-V2-000004, HRA-EVAL-V2-000005, HRA-EVAL-V2-000005, HRA-EVAL-V2-000005, HRA-EVAL-V2-000006, HRA-EVAL-V2-000006, HRA-EVAL-V2-000006, HRA-EVAL-V2-000007, HRA-EVAL-V2-000007, HRA-EVAL-V2-000007, HRA-EVAL-V2-000008, HRA-EVAL-V2-000008, HRA-EVAL-V2-000008, HRA-EVAL-V2-000011, HRA-EVAL-V2-000011, HRA-EVAL-V2-000011, HRA-EVAL-V2-000012, HRA-EVAL-V2-000012, HRA-EVAL-V2-000012, HRA-EVAL-V2-000013, HRA-EVAL-V2-000013, HRA-EVAL-V2-000013, HRA-EVAL-V2-000014, HRA-EVAL-V2-000014, HRA-EVAL-V2-000014, HRA-EVAL-V2-000015, HRA-EVAL-V2-000015, HRA-EVAL-V2-000015, HRA-EVAL-V2-000016, HRA-EVAL-V2-000016, HRA-EVAL-V2-000016, HRA-EVAL-V2-000017, HRA-EVAL-V2-000017, HRA-EVAL-V2-000017, HRA-EVAL-V2-000018, HRA-EVAL-V2-000018, HRA-EVAL-V2-000018, HRA-EVAL-V2-000021, HRA-EVAL-V2-000021, HRA-EVAL-V2-000021, HRA-EVAL-V2-000022, HRA-EVAL-V2-000022, HRA-EVAL-V2-000022, HRA-EVAL-V2-000023, HRA-EVAL-V2-000023, HRA-EVAL-V2-000023, HRA-EVAL-V2-000024, HRA-EVAL-V2-000024, HRA-EVAL-V2-000024, HRA-EVAL-V2-000025, HRA-EVAL-V2-000025, HRA-EVAL-V2-000025, HRA-EVAL-V2-000026, HRA-EVAL-V2-000026, HRA-EVAL-V2-000026, HRA-EVAL-V2-000027, HRA-EVAL-V2-000027, HRA-EVAL-V2-000027, HRA-EVAL-V2-000028, HRA-EVAL-V2-000028, HRA-EVAL-V2-000028
```

### Validation

```
HRA-EVAL-V2-000009, HRA-EVAL-V2-000009, HRA-EVAL-V2-000009, HRA-EVAL-V2-000019, HRA-EVAL-V2-000019, HRA-EVAL-V2-000019, HRA-EVAL-V2-000029, HRA-EVAL-V2-000029, HRA-EVAL-V2-000029
```

### Test

```
HRA-EVAL-V2-000010, HRA-EVAL-V2-000010, HRA-EVAL-V2-000010, HRA-EVAL-V2-000020, HRA-EVAL-V2-000020, HRA-EVAL-V2-000020, HRA-EVAL-V2-000030, HRA-EVAL-V2-000030, HRA-EVAL-V2-000030
```

## Borderline Cases (score >= 60, decision = no_match)

- **HRA-EVAL-V2-000007**
  - Vacancy: Prompt Engineer / AI Automation Specialist
  - Score: 62
  - Decision: no_match

- **HRA-EVAL-V2-000024**
  - Vacancy: Prompt Engineer / AI Automation Specialist
  - Score: 64
  - Decision: no_match

- **HRA-EVAL-V2-000026**
  - Vacancy: Системный аналитик
  - Score: 62
  - Decision: no_match

## Confirmations

- ✅ All 90 records present
- ✅ No NULL values
- ✅ Assistant messages fully formed
- ✅ System messages filled (production Prompt A)
- ✅ User messages filled (candidate + vacancy)
- ✅ All 3 borderline cases present in dataset
- ✅ Using production Prompt A (not Prompt B, not Judge Prompt)
- ✅ Using Judge (GPT-4.1) as Teacher

## System Prompt (Production Prompt A)

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

## Assistant Message Format

```json
{
  "role_score": 0-30,
  "skills_score": 0-35,
  "experience_score": 0-20,
  "conditions_score": 0-15,
  "score": 0-100,
  "decision": "match" | "no_match",
  "reason": "..."
}
```
