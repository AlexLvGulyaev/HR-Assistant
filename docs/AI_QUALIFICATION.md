# AI Qualification: HR Assistant

Документ описывает промпты, модели и параметры AI-компонентов HR Assistant.

---

## Обзор AI-компонентов

HR Assistant использует OpenAI API для:
- Извлечения данных кандидата из текста резюме
- Matching кандидата с вакансиями
- Генерации голосовых сообщений (TTS)
- Генерации визуальных материалов
- Генерации видео

---

## Используемые модели

| Модель | Назначение | Параметры |
|--------|-----------|-----------|
| **GPT-4o-mini** | Извлечение данных кандидата | Temperature: 0, Response format: JSON Schema |
| **GPT-4** | Matching кандидата с вакансиями | Temperature: 0 |
| **GPT-image-1** | Генерация визуальных материалов | Size: 1024x1024 |
| **Sora-2** | Генерация видео | Size: 720x1280, Duration: 4 sec |
| **TTS** | Генерация голосовых сообщений | Language: Russian |

---

## 1. Извлечение данных кандидата

### Модель

**GPT-4o-mini**

**Причины выбора:**
- Быстрая обработка
- Низкая стоимость токенов
- Поддержка JSON Schema

### Промпт

```
You are an HR data extraction assistant. Extract structured candidate information from the resume text.

Resume text:
{{normalized_text}}

Extract the following fields:
- full_name: Full name of the candidate (string)
- city: City of residence (string, null if not found)
- desired_position: Desired position or job title (string)
- experience_years: Years of experience (number, null if not found)
- skills: Array of key skills (array of strings)
- salary_expectation: Salary expectation in rubles per month (number, null if not found)
- email: Email address (string, null if not found)
- phone: Phone number in format +7XXXXXXXXXX (string, null if not found)
- summary: Brief summary of the candidate's profile (string)

Return a valid JSON object with the extracted data.
If a field is not found in the text, set it to null.

JSON Schema:
{
  "type": "object",
  "properties": {
    "full_name": {"type": "string"},
    "city": {"type": ["string", "null"]},
    "desired_position": {"type": "string"},
    "experience_years": {"type": ["number", "null"]},
    "skills": {"type": "array", "items": {"type": "string"}},
    "salary_expectation": {"type": ["number", "null"]},
    "email": {"type": ["string", "null"]},
    "phone": {"type": ["string", "null"]},
    "summary": {"type": "string"}
  },
  "required": ["full_name", "desired_position", "skills", "summary"]
}
```

### Параметры

```json
{
  "model": "gpt-4o-mini",
  "temperature": 0,
  "response_format": { "type": "json_object" }
}
```

### Пример входа

```
Resume text:
Иванов Иван Иванович
Frontend-разработчик
Опыт работы: 5 лет
Навыки: React, TypeScript, Node.js, Redux, Webpack
Город: Москва
Зарплата: 180 000 руб.
Email: ivanov@example.com
Телефон: +79001234567

Опыт работы:
- Senior Frontend Developer, Company A (2022-настоящее время)
- Middle Frontend Developer, Company B (2019-2022)
```

### Пример выхода

```json
{
  "full_name": "Иванов Иван Иванович",
  "city": "Москва",
  "desired_position": "Frontend-разработчик",
  "experience_years": 5,
  "skills": ["React", "TypeScript", "Node.js", "Redux", "Webpack"],
  "salary_expectation": 180000,
  "email": "ivanov@example.com",
  "phone": "+79001234567",
  "summary": "Frontend-разработчик с 5-летним опытом работы. Ключевые навыки: React, TypeScript, Node.js. Работал в Company A, Company B."
}
```

---

## 2. Matching кандидата с вакансиями

### Модель

**GPT-4**

**Причины выбора:**
- Высокое качество анализа
- Лучшее понимание контекста
- Консистентные решения

### Промпт

```
You are an HR matching assistant. Compare the candidate profile with open vacancies and find the best match.

Candidate profile:
{{candidate_profile}}

Open vacancies:
{{vacancies}}

For each vacancy, calculate:
1. Score (0-100): How well the candidate matches the vacancy
2. Decision (match/no_match): Whether the candidate is suitable
3. Reason (string): Explanation of the decision

Consider:
- Experience (years)
- Skills match
- City match (if remote work is not specified)
- Salary expectations (if within range)
- Position alignment

Return a valid JSON array with matching results for each vacancy.

JSON Schema:
{
  "type": "array",
  "items": {
    "type": "object",
    "properties": {
      "vacancy_id": {"type": "string"},
      "vacancy_title": {"type": "string"},
      "score": {"type": "number", "minimum": 0, "maximum": 100},
      "decision": {"type": "string", "enum": ["match", "no_match"]},
      "reason": {"type": "string"}
    },
    "required": ["vacancy_id", "vacancy_title", "score", "decision", "reason"]
  }
}
```

### Параметры

```json
{
  "model": "gpt-4",
  "temperature": 0
}
```

### Пример входа

```
Candidate profile:
{
  "full_name": "Иванов Иван Иванович",
  "city": "Москва",
  "desired_position": "Frontend-разработчик",
  "experience_years": 5,
  "skills": ["React", "TypeScript", "Node.js"],
  "salary_expectation": 180000
}

Open vacancies:
[
  {
    "id": "vac-001",
    "title": "Senior Frontend Developer",
    "requirements": "React, TypeScript, 5+ years experience",
    "salary_min": 180000,
    "salary_max": 250000
  },
  {
    "id": "vac-002",
    "title": "Backend Developer",
    "requirements": "Java, Spring Boot, 5+ years experience",
    "salary_min": 200000,
    "salary_max": 300000
  }
]
```

### Пример выхода

```json
[
  {
    "vacancy_id": "vac-001",
    "vacancy_title": "Senior Frontend Developer",
    "score": 85,
    "decision": "match",
    "reason": "Candidate has 5 years of experience, matches key skills (React, TypeScript), city matches (Moscow), salary expectations are within range."
  },
  {
    "vacancy_id": "vac-002",
    "vacancy_title": "Backend Developer",
    "score": 30,
    "decision": "no_match",
    "reason": "Skills do not match (React/TypeScript vs Java/Spring Boot), position alignment is poor."
  }
]
```

---

## 3. Генерация TTS (Text-to-Speech)

### Модель

**OpenAI TTS**

**Параметры:**
- Model: `tts-1` (быстрая) или `tts-1-hd` (высокое качество)
- Voice: `alloy`, `echo`, `fable`, `onyx`, `nova`, `shimmer`
- Language: Russian

### Пример использования

```javascript
const response = await openai.audio.speech.create({
  model: "tts-1",
  voice: "alloy",
  input: "Иван, спасибо за резюме! Мы нашли для вас вакансию: Senior Frontend Developer. Score: 85 из 100."
});

const buffer = Buffer.from(await response.arrayBuffer());
// Отправка в Telegram как voice message
```

---

## 4. Генерация визуальных материалов

### Модель

**GPT-image-1** (или DALL-E 3)

### Промпт

```
Create a professional infographic for a job candidate matching result.

Candidate: {{full_name}}
Position: {{desired_position}}
Experience: {{experience_years}} years
Key Skills: {{skills}}
Matched Vacancy: {{vacancy_title}}
Score: {{score}}/100

Style: Modern, clean, professional business infographic.
Colors: Blue, white, gray.
Layout: Header with candidate name, skills section, matching result section, score visualization.

Include:
- Candidate photo placeholder (avatar icon)
- Skills as tags
- Score as progress bar or radial chart
- Matched vacancy information
```

### Параметры

```json
{
  "model": "dall-e-3",
  "size": "1024x1024",
  "quality": "standard",
  "n": 1
}
```

---

## 5. Генерация видео

### Модель

**Sora-2**

**Ограничения:**
- Размер: 720x1280 (vertical)
- Длительность: 4 секунды
- Стоимость: высокая

### Промпт

```
Create a short video presentation for a job candidate matching result.

Candidate: {{full_name}}
Position: {{desired_position}}
Matched Vacancy: {{vacancy_title}}
Score: {{score}}%

Style: Professional, modern, animated text and graphics.
Duration: 4 seconds.
```

### Параметры

```json
{
  "model": "sora-2",
  "size": "720x1280",
  "duration": 4
}
```

---

## Обработка ошибок

### Ошибки LLM

**Типы ошибок:**
1. Невалидный JSON
2. Превышение лимита токенов
3. Rate limit
4. API недоступен

**Обработка:**

**Невалидный JSON:**
```javascript
// Попытка ремонта JSON
try {
  const data = JSON.parse(llmResponse);
} catch (error) {
  // Попытка ремонта
  const repaired = repairJson(llmResponse);
  const data = JSON.parse(repaired);
}
```

**Превышение лимита токенов:**
```javascript
// Усечь текст до лимита
const truncatedText = text.substring(0, maxTokens * 4); // ~4 chars per token
```

**Rate limit:**
```javascript
// Retry с экспоненциальной задержкой
await sleep(retryDelay * Math.pow(2, attempt));
```

---

### Retry механизм

**Параметры:**
- Количество попыток: 3
- Интервал: 5 секунд
- Экспоненциальная задержка: да

**Пример:**
```javascript
async function callWithRetry(fn, maxRetries = 3, delay = 5000) {
  for (let attempt = 0; attempt < maxRetries; attempt++) {
    try {
      return await fn();
    } catch (error) {
      if (attempt === maxRetries - 1) throw error;
      await sleep(delay * Math.pow(2, attempt));
    }
  }
}
```

---

## Стоимость

### Токены

**Приблизительная стоимость на 1 резюме:**

| Операция | Модель | Токены | Стоимость |
|----------|--------|--------|-----------|
| Извлечение данных | GPT-4o-mini | ~1000 input + ~500 output | ~$0.002 |
| Matching | GPT-4 | ~2000 input + ~500 output | ~$0.03 |
| TTS | tts-1 | ~200 chars | ~$0.004 |
| Визуалы | DALL-E 3 | 1 image | ~$0.04 |
| **Итого** | | | **~$0.08** |

**При 1000 резюме в месяц:** ~$80

---

## Оптимизация стоимости

### Рекомендации

1. **Кэширование результатов:**
   - Кэшировать matching для одинаковых вакансий
   - Не генерировать TTS/визуалы для низких score

2. **Условная генерация:**
   - TTS только для score > 70
   - Визуалы только для score > 80
   - Видео только по запросу

3. **Оптимизация промптов:**
   - Уменьшить длину промптов
   - Использовать более короткие модели (GPT-4o-mini вместо GPT-4)

---

## Мониторинг качества

### Метрики

**Извлечение данных:**
- Полнота извлечения (recall)
- Точность извлечения (precision)
- F1-score

**Matching:**
- Accuracy (соответствие ручной оценке)
- Precision (доля правильных match)
- Recall (доля найденных match)

**Пример оценки:**

```sql
-- Проверка распределения score
SELECT
  CASE
    WHEN score >= 80 THEN 'high'
    WHEN score >= 60 THEN 'medium'
    ELSE 'low'
  END as score_range,
  COUNT(*) as count
FROM matches
GROUP BY score_range;
```

---

## Связанные документы

- [ARCHITECTURE.md](ARCHITECTURE.md) — архитектура системы
- [SPEC.md](SPEC.md) — спецификация системы
- [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) — руководство по развёртыванию

---

**Статус документа:** Production-ready
**Последнее обновление:** 2026-06-23