# Teacher Dataset Report
**Date:** 2026-06-28
**Experiment:** HRA-EXP-V4
**Dataset:** HRA-EVAL-V4

## Summary

- **Total records:** 162
- **Train:** 114
- **Validation:** 27
- **Test:** 15
- **Hard Negative Holdout:** 6

## Distribution by Groups

### Train

- **obvious_match:** 39
- **borderline:** 42
- **obvious_no_match:** 33

### Validation

- **obvious_match:** 9
- **borderline:** 9
- **obvious_no_match:** 9

### Test

- **obvious_match:** 9
- **borderline:** 3
- **obvious_no_match:** 3

### Hard Negative Holdout

- **obvious_match:** 0
- **borderline:** 0
- **obvious_no_match:** 6

## Case Codes by Split

### Train

```
HRA-EVAL-V2-000001, HRA-EVAL-V2-000002, HRA-EVAL-V2-000003, HRA-EVAL-V2-000004, HRA-EVAL-V2-000005, HRA-EVAL-V2-000006, HRA-EVAL-V2-000007, HRA-EVAL-V2-000008, HRA-EVAL-V2-000009, HRA-EVAL-V2-000011, HRA-EVAL-V2-000012, HRA-EVAL-V2-000013, HRA-EVAL-V2-000014, HRA-EVAL-V2-000015, HRA-EVAL-V2-000016, HRA-EVAL-V2-000017, HRA-EVAL-V2-000018, HRA-EVAL-V2-000019, HRA-EVAL-V2-000021, HRA-EVAL-V2-000022, HRA-EVAL-V2-000023, HRA-EVAL-V2-000024, HRA-EVAL-V2-000025, HRA-EVAL-V2-000026, HRA-EVAL-V2-000027, HRA-EVAL-V2-000028, HRA-EVAL-V2-000029, HRA-EVAL-V2-000101, HRA-EVAL-V2-000102, HRA-EVAL-V2-000103, HRA-EVAL-V2-000104, HRA-EVAL-V2-000107, HRA-EVAL-V2-000109, HRA-EVAL-V2-000201, HRA-EVAL-V2-000202, HRA-EVAL-V2-000203, HRA-EVAL-V2-000204, HRA-EVAL-V2-000207
```

### Validation

```
HRA-EVAL-V2-000105, HRA-EVAL-V2-000106, HRA-EVAL-V2-000108, HRA-EVAL-V2-000205, HRA-EVAL-V2-000206, HRA-EVAL-V2-000208, HRA-EVAL-V2-000209, HRA-EVAL-V2-000210, HRA-EVAL-V2-000213
```

### Test

```
HRA-EVAL-V2-000010, HRA-EVAL-V2-000020, HRA-EVAL-V2-000030, HRA-EVAL-V2-000211, HRA-EVAL-V2-000212
```

### Hard Negative Holdout

```
HRA-EVAL-V2-000110, HRA-EVAL-V2-000111
```

## Threshold-Inconsistent Cases (score >= 60, decision = no_match)

## Confirmations

- ✅ All 162 records present
- ✅ No NULL values
- ✅ Assistant messages fully formed
- ✅ System messages filled (production Prompt A)
- ✅ User messages filled (candidate + vacancy)
- ✅ All 0 threshold-inconsistent cases (score >= 60, decision = no_match) documented
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
