# AI Qualification: HR Assistant

Документ описывает реальные промпты, модели и параметры AI-компонентов HR Assistant на основе workflow файлов.

---

## Обзор AI-компонентов

HR Assistant использует OpenAI API для:
- Извлечения данных кандидата из текста резюме
- Ремонта невалидного JSON
- Matching кандидата с вакансиями

**Источник данных:** Файлы workflow в `workflows/HR Processing Worker.json`

---

## Используемые модели

| Модель | Назначение | Параметры |
|--------|-----------|-----------|
| **GPT-4o-mini** | Извлечение данных кандидата | Temperature: 0, Response format: JSON Schema |
| **GPT-4o-mini** | Ремонт невалидного JSON | Temperature: 0, Response format: JSON Schema |
| **GPT-4o-mini** | Matching кандидата с вакансиями | Temperature: 0, Response format: JSON Schema |

**Важно:** Все операции используют GPT-4o-mini, а не GPT-4.

---

## 1. Извлечение данных кандидата

### Модель

**GPT-4o-mini**

**Причины выбора:**
- Быстрая обработка
- Низкая стоимость токенов
- Поддержка JSON Schema
- Достаточное качество для извлечения данных

### Промпт

**System message:**
```
Ты — HR-ассистент для извлечения структурированных данных из резюме. 
Извлекай только явно присутствующие данные. 
Не выдумывай отсутствующие сведения.
```

**User message:**
```
Извлеки данные кандидата из текста резюме:

{{normalized_text}}
```

### JSON Schema

```json
{
  "type": "object",
  "additionalProperties": false,
  "properties": {
    "full_name": { "type": ["string", "null"] },
    "city": { "type": ["string", "null"] },
    "desired_position": { "type": ["string", "null"] },
    "experience_years": { "type": ["number", "null"] },
    "skills": { "type": "array", "items": { "type": "string" } },
    "salary_expectation": { "type": ["number", "null"] },
    "email": { "type": ["string", "null"] },
    "phone": { "type": ["string", "null"] },
    "summary": { "type": ["string", "null"] }
  },
  "required": [
    "full_name",
    "city",
    "desired_position",
    "experience_years",
    "skills",
    "salary_expectation",
    "email",
    "phone",
    "summary"
  ]
}
```

### Параметры

```json
{
  "model": "gpt-4o-mini",
  "temperature": 0,
  "response_format": {
    "type": "json_schema",
    "json_schema": {
      "name": "candidate_profile",
      "strict": true,
      "schema": { ... }
    }
  }
}
```

### Обработка результата

Workflow проверяет:
1. Валидность JSON
2. Наличие всех required полей
3. Типы данных (skills — массив, experience_years — number или null)
4. Meaningful content (минимум имя, должность, контакты или 2+ навыка)

Если JSON невалиден → переход к ремонту JSON.

---

## 2. Ремонт невалидного JSON

### Модель

**GPT-4o-mini**

### Промпт

**System message:**
```
Ты исправляешь JSON-ответ HR-ассистента. 
Нельзя добавлять данные, которых нет в исходном резюме.
```

**User message:**
```
Исходный текст резюме:
{{resume_text}}

Некорректный ответ модели:
{{rawBadResponse}}

Исправь ответ по строгой JSON-схеме.
```

### JSON Schema

Аналогична схеме извлечения данных кандидата.

### Параметры

```json
{
  "model": "gpt-4o-mini",
  "temperature": 0,
  "response_format": {
    "type": "json_schema",
    "json_schema": {
      "name": "candidate_profile_repair",
      "strict": true,
      "schema": { ... }
    }
  }
}
```

### Обработка результата

После ремонта:
1. Проверка валидности JSON
2. Проверка типов данных
3. Если всё ещё невалидный → fallback на processing error

---

## 3. Matching кандидата с вакансиями

### Модель

**GPT-4o-mini**

**Причины выбора:**
- Быстрая обработка
- Достаточное качество для matching
- Низкая стоимость

### Система оценки

Matching использует детальную систему оценки по 4 критериям:

| Критерий | Макс. баллов | Описание |
|----------|--------------|----------|
| **Должность / роль** | 30 | Соответствие желаемой должности и роли вакансии |
| **Навыки** | 35 | Пересечение навыков кандидата с требованиями вакансии |
| **Опыт** | 20 | Соответствие опыта работы требованиям |
| **Город / формат / зарплата** | 15 | Город, формат работы, зарплатные ожидания |
| **Итого** | **100** | Максимальный score |

**Порог для match:** score >= 60

### Промпт

**System message:**
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

**User message:**
```
Кандидат:
{{candidate_json}}

Вакансия:
{{vacancy_json}}
```

### JSON Schema

```json
{
  "type": "object",
  "additionalProperties": false,
  "properties": {
    "vacancy_id": { "type": ["string", "null"] },
    "title": { "type": ["string", "null"] },
    "role_score": { "type": "number" },
    "skills_score": { "type": "number" },
    "experience_score": { "type": "number" },
    "conditions_score": { "type": "number" },
    "score": { "type": "number" },
    "decision": {
      "type": "string",
      "enum": ["match", "no_match"]
    },
    "reason": { "type": "string" }
  },
  "required": [
    "vacancy_id",
    "title",
    "role_score",
    "skills_score",
    "experience_score",
    "conditions_score",
    "score",
    "decision",
    "reason"
  ]
}
```

### Параметры

```json
{
  "model": "gpt-4o-mini",
  "temperature": 0,
  "response_format": {
    "type": "json_schema",
    "json_schema": {
      "name": "vacancy_match_result",
      "strict": true,
      "schema": { ... }
    }
  }
}
```

### Обработка результата

Workflow:
1. Извлекает JSON из ответа LLM
2. Валидирует и clamps каждый score (role: 0-30, skills: 0-35, experience: 0-20, conditions: 0-15)
3. Вычисляет итоговый score как сумму или берёт из модели
4. Устанавливает decision на основе порога (>= 60 → match)
5. Сохраняет результат в БД

**Fallback:** Если JSON невалиден → score = 0, decision = "no_match", reason = "Не удалось разобрать ответ модели"

---

## 4. Обработка ошибок

### Невалидный JSON

**Стратегия:**
1. Первичная обработка → извлечение данных
2. Если JSON невалиден → ремонт JSON
3. Если после ремонта невалиден → fallback на processing error

**Код валидации (JavaScript):**
```javascript
const requiredFields = [
  'full_name',
  'city',
  'desired_position',
  'experience_years',
  'skills',
  'salary_expectation',
  'email',
  'phone',
  'summary'
];

const hasObject = candidate && typeof candidate === 'object' && !Array.isArray(candidate);
const hasAllFields = hasObject && requiredFields.every(field =>
  Object.prototype.hasOwnProperty.call(candidate, field)
);
const validTypes =
  hasObject &&
  Array.isArray(candidate.skills) &&
  (candidate.experience_years === null || typeof candidate.experience_years === 'number') &&
  (candidate.salary_expectation === null || typeof candidate.salary_expectation === 'number');

const isValid = Boolean(hasObject && hasAllFields && validTypes);
```

### Превышение лимита токенов

**Решение:** Нормализованный текст обрезается до разумного лимита перед отправкой в LLM.

### Rate limit

**Retry механизм:**
- Количество попыток: 3
- Интервал: 5 секунд
- Экспоненциальная задержка: да

---

## 5. Стоимость

### Токены

**Приблизительная стоимость на 1 резюме:**

| Операция | Модель | Токены | Стоимость |
|----------|--------|--------|-----------|
| Извлечение данных | GPT-4o-mini | ~1000 input + ~500 output | ~$0.002 |
| Ремонт JSON (при ошибке) | GPT-4o-mini | ~1000 input + ~500 output | ~$0.002 |
| Matching (на 1 вакансию) | GPT-4o-mini | ~500 input + ~300 output | ~$0.001 |
| **Итого (без ремонта, 1 вакансия)** | | | **~$0.003** |
| **Итого (с ремонтом, 3 вакансии)** | | | **~$0.006** |

**При 1000 резюме в месяц (среднее):** ~$3-6

**Примечание:** TTS и генерация изображений/видео не входят в базовый пайплайн и оплачиваются отдельно.

---

## 6. Оптимизация

### Рекомендации

1. **Кэширование:**
   - Кэшировать matching для одинаковых вакансий
   - Не генерировать TTS/визуалы для низких score

2. **Условная генерация:**
   - TTS только для score > 70
   - Визуалы только для score > 80
   - Видео только по запросу

3. **Batch processing:**
   - Группировка вакансий для одного кандидата
   - Параллельная обработка независимых кандидатов

---

## 7. Мониторинг качества

### Метрики

**Извлечение данных:**
- Полнота извлечения (recall)
- Точность извлечения (precision)
- F1-score

**Matching:**
- Accuracy (соответствие ручной оценке)
- Precision (доля правильных match)
- Recall (доля найденных match)
- Распределение score по диапазонам

**SQL для анализа:**
```sql
-- Распределение score
SELECT
  CASE
    WHEN score >= 80 THEN 'high (80-100)'
    WHEN score >= 60 THEN 'medium (60-79)'
    WHEN score >= 40 THEN 'low (40-59)'
    ELSE 'very_low (0-39)'
  END as score_range,
  decision,
  COUNT(*) as count
FROM matches
GROUP BY score_range, decision
ORDER BY score_range;

-- Доля match vs no_match
SELECT
  decision,
  COUNT(*) as count,
  ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) as percentage
FROM matches
GROUP BY decision;
```

---

## 8. Связанные файлы

- **Workflow:** `workflows/HR Processing Worker.json` — основной workflow с промптами
- **База данных:** `database/schema_hr_assistant.sql` — таблицы candidates, matches
- **Архитектура:** `docs/ARCHITECTURE.md` — общая архитектура системы

---

## 9. История изменений

**2026-06-24:**
- Переписано на основе реальных промптов из workflow
- Исправлена модель: GPT-4o-mini вместо GPT-4
- Добавлена детальная система оценки matching
- Добавлена схема валидации JSON
- Удалены выдуманные примеры
- Добавлены реальные параметры из workflow

---

**Статус документа:** Production-ready
**Последнее обновление:** 2026-06-24
**Источник:** `workflows/HR Processing Worker.json`