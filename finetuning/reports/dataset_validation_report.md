# Отчёт по валидации датасета HRA-EXP-V1

**Дата:** 2026-06-28
**Статус:** ⚠️ ТРЕБУЕТ РЕШЕНИЯ ПО МЕТОДОЛОГИИ

---

## Критическое открытие: Judge ВОЗВРАЩАЕТ детальные оценки, но workflow их НЕ сохраняет

### Что происходит в workflow

**Prepare Judge Request (строка 162):**
```javascript
openai_body: {
  model: experimentData.model_judge || 'gpt-4.1-2025-04-14',
  response_format: {
    json_schema: {
      properties: {
        role_score: { type: 'number' },
        skills_score: { type: 'number' },
        experience_score: { type: 'number' },
        conditions_score: { type: 'number' },
        score: { type: 'number' },
        decision: { type: 'string' },
        reason: { type: 'string' }
      }
    }
  }
}
```

**Judge ВОЗВРАЩАЕТ JSON с детальными оценками:**
```json
{
  "role_score": 30,
  "skills_score": 33,
  "experience_score": 20,
  "conditions_score": 15,
  "score": 98,
  "decision": "match",
  "reason": "..."
}
```

**Parse Judge Response (строка 218):**
```javascript
return [{
  json: {
    case_vacancy_id: caseVacancyId,
    reference_score: parsed.score,
    reference_decision: parsed.decision,
    reference_reason: parsed.reason,  // <-- Текст с оценками
    raw_response: raw,                 // <-- Полный JSON
    latency_ms: latencyMs,
    parsed: parsed                     // <-- Детальные оценки
  }
}];
```

**PG: Update Reference Fields (строка 226):**
```sql
UPDATE eval_prompt_case_vacancies
SET
    reference_score = {{ $json.reference_score }},
    reference_decision = '{{ $json.reference_decision }}',
    reference_reason = '{{ $json.reference_reason }}'
WHERE id = '{{ $json.case_vacancy_id }}';
```

### Проблема

**Workflow НЕ сохраняет:**
- ❌ `raw_response` (полный JSON от Judge)
- ❌ `parsed.role_score`
- ❌ `parsed.skills_score`
- ❌ `parsed.experience_score`
- ❌ `parsed.conditions_score`

**Workflow сохраняет только:**
- ✅ `reference_score` (общий)
- ✅ `reference_decision` (match/no_match)
- ✅ `reference_reason` (текстовое обоснование)

---

## Данные в БД

### eval_prompt_results

| run_type | count | with_raw_response |
|----------|-------|-------------------|
| A | 91 | 91 |
| B | 91 | 91 |
| judge | 3 | 0 |

**Вывод:** Judge результаты НЕ сохранены в eval_prompt_results

### eval_prompt_case_vacancies

Поля:
- ✅ reference_score
- ✅ reference_decision
- ✅ reference_reason
- ❌ role_score (НЕТ)
- ❌ skills_score (НЕТ)
- ❌ experience_score (НЕТ)
- ❌ conditions_score (НЕТ)

---

## Что доступно для Teacher

### Вариант 1: Judge из reference_* полей

**Доступно:**
- reference_score (общий)
- reference_decision (match/no_match)
- reference_reason (текст)

**Недоступно:**
- Детальные оценки (role_score, etc.) в структурированном виде

**Проблема:**
- 48% кейсов НЕ содержат детальные оценки в тексте
- 2 кейса имеют противоречие decision vs score

### Вариант 2: Prompt A из eval_prompt_results

**Доступно:**
- score (общий)
- decision (match/no_match)
- role_score, skills_score, experience_score, conditions_score (детальные)
- reason (текст)

**Проблема:**
- ❌ Противоречит требованию "Prompt A и Prompt B не использовать как target"
- ❌ Prompt A — это сравниваемый промпт, не эталон

### Вариант 3: Перепрогнать Judge и сохранить полные ответы

**Требует:**
- Модификация workflow для сохранения raw_response
- Перепрогон всех 91 кейсов
- Затраты времени и API calls

**Даёт:**
- ✅ Полные JSON ответы от Judge
- ✅ Детальные оценки в структурированном виде
- ✅ Соответствие методологии Teacher-Student

---

## Статистика по качеству данных (из reference_reason)

**Всего кейсов:** 91

**Имеют все 4 детальные оценки в тексте:** 47 (52%)
- "(X/30)", "(X/35)", "(X/20)", "(X/15)" в reasoning

**Не имеют всех детальных оценок:** 44 (48%)
- Отсутствуют или неполные

**Противоречие decision vs score:** 2 (2%)
- score >= 60, но decision = no_match
- score < 60, но decision = match

---

## Примеры

### Кейс с полными детальными оценками (HRA-EVAL-000001, вакансия "Системный аналитик")

**reference_reason:**
```
Кандидат претендует на должность 'Системный аналитик', что полностью совпадает с вакансией (30/30). 
Все ключевые навыки (SQL, BPMN, REST API) присутствуют... (33/35). 
Опыт работы — 5 лет... (20/20). 
Зарплатные ожидания (180 000) находятся в пределах бюджета (15/15).
```

**Можно извлечь:**
- role_score: 30
- skills_score: 33
- experience_score: 20
- conditions_score: 15

### Кейс без детальных оценок (HRA-EVAL-000002, вакансия "Prompt Engineer")

**reference_reason:**
```
Кандидат полностью соответствует заявленной должности (Prompt Engineer), совпадение по названию и функционалу. 
Все ключевые навыки из требований присутствуют...
```

**НЕЛЬЗЯ извлечь:**
- Детальные оценки отсутствуют в тексте

---

## Решения

### Вариант A: Использовать только Judge (reference_*)

**JSON формат:**
```json
{
  "total_score": 98,
  "decision": "match",
  "reason": "Текстовое обоснование"
}
```

**Проблема:** Нет детальных оценок

### Вариант B: Парсить детальные оценки из reasoning (48% кейсов)

**Для 47 кейсов:** Извлечь оценки из текста
**Для 44 кейсов:** Пометить как requiring_manual_review или использовать только total_score

**Проблема:** Неполные данные, возможны ошибки парсинга

### Вариант C: Использовать Prompt A как teacher

**Противоречит требованию:** "Prompt A и Prompt B не использовать как target"

### Вариант D: Перепрогнать Judge с сохранением raw_response

**Требует:** Модификация workflow
**Даёт:** Полные данные для 100% кейсов

---

## Рекомендации

### Немедленные действия:

1. ✅ **Модифицировать workflow** для сохранения Judge raw_response:
   ```sql
   -- Добавить колонки в eval_prompt_case_vacancies
   ALTER TABLE eval_prompt_case_vacancies
   ADD COLUMN reference_role_score NUMERIC;
   ALTER TABLE eval_prompt_case_vacancies
   ADD COLUMN reference_skills_score NUMERIC;
   ALTER TABLE eval_prompt_case_vacancies
   ADD COLUMN reference_experience_score NUMERIC;
   ALTER TABLE eval_prompt_case_vacancies
   ADD COLUMN reference_conditions_score NUMERIC;
   ```

2. ✅ **Обновить workflow** "PG: Update Reference Fields":
   ```sql
   UPDATE eval_prompt_case_vacancies
   SET
       reference_score = {{ $json.reference_score }},
       reference_decision = '{{ $json.reference_decision }}',
       reference_reason = '{{ $json.reference_reason }}',
       reference_role_score = {{ $json.parsed.role_score }},
       reference_skills_score = {{ $json.parsed.skills_score }},
       reference_experience_score = {{ $json.parsed.experience_score }},
       reference_conditions_score = {{ $json.parsed.conditions_score }}
   WHERE id = '{{ $json.case_vacancy_id }}';
   ```

3. ✅ **Перепрогнать Judge** для всех 91 кейсов

4. ✅ **Извлечь полные данные** из обновлённой БД

### Альтернатива (если нельзя перепрогнать):

1. Парсить детальные оценки из reasoning (52% кейсов)
2. Для остальных кейсов использовать только total_score + decision + reason
3. Документировать ограничение

---

## Вывод

**Проблема:** Workflow НЕ сохраняет детальные оценки Judge в БД.

**Решение:** Модифицировать workflow + перепрогнать Judge.

**Альтернатива:** Парсить из reasoning (неполные данные).

**Требуется:** Решение заказчика по методологии.