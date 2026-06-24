# Диаграмма интеграций: HR Assistant

Документ описывает интеграции HR Assistant с внешними системами и внутренними компонентами.

---

## Обзор интеграций

HR Assistant интегрируется с:
- **Telegram Bot API** — входной канал и доставка ответов
- **OpenAI API** — AI-модели для извлечения данных и matching
- **PostgreSQL** — база данных

---

## Архитектурная диаграмма интеграций

```
┌─────────────────────────────────────────────────────────────────────────┐
│                              Внешние системы                             │
└─────────────────────────────────────────────────────────────────────────┘
                                     │
                                     │
                    ┌────────────────┼────────────────┐
                    │                │                │
                    ▼                ▼                ▼
            ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
            │   Telegram   │  │   OpenAI     │  │  PostgreSQL  │
            │   Bot API    │  │     API      │  │              │
            └──────────────┘  └──────────────┘  └──────────────┘
                    │                │                │
                    │                │                │
                    │                │                │
                    └────────────────┼────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                            n8n Workflows                                 │
│                                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                 │
│  │  HR Intake   │──│ Processing   │──│  Delivery    │                 │
│  │  (Webhook)   │  │   Worker     │  │   Worker     │                 │
│  └──────────────┘  └──────────────┘  └──────────────┘                 │
│         │                  │                  │                         │
│         │                  │                  │                         │
│         │           ┌──────┴──────┐          │                         │
│         │           │             │          │                         │
│         │           ▼             ▼          │                         │
│         │    ┌──────────────┐  ┌──────────────┐                       │
│         │    │   GPT-4o     │  │    GPT-4     │                       │
│         │    │   mini       │  │              │                       │
│         │    └──────────────┘  └──────────────┘                       │
│         │                                                             │
│         │           ┌──────────────┐  ┌──────────────┐               │
│         │           │     TTS      │  │  DALL-E 3    │               │
│         │           └──────────────┘  └──────────────┘               │
│         │                                                             │
│         └──────────────────┬──────────────────┘                        │
│                            │                                            │
│                            ▼                                            │
│                   ┌──────────────┐                                      │
│                   │  PostgreSQL  │                                      │
│                   │   Database   │                                      │
│                   └──────────────┘                                      │
│                                                                          │
│  ┌──────────────┐  ┌──────────────┐                                    │
│  │   Watchdog   │  │   Watchdog   │                                    │
│  │  (inputs)    │  │  (outbox)    │                                    │
│  └──────────────┘  └──────────────┘                                    │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Интеграция с Telegram Bot API

### Обзор

**Назначение:** Входной канал для резюме от кандидатов и доставка ответов.

**Тип интеграции:** Webhook

**Документация:** https://core.telegram.org/bots/api

---

### Настройка

#### Создание бота

```bash
# Создание бота через BotFather
/newbot
# Введите имя: HR Assistant
# Введите username: hr_assistant_bot
# Получите токен: 1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
```

---

#### Установка Webhook

```bash
curl -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/setWebhook" \
  -H "Content-Type: application/json" \
  -d "{\"url\": \"https://your-domain.com/webhook/hr-assistant\"}"
```

---

### Входящие сообщения

#### Типы сообщений

| Тип | Описание | Обработка |
|-----|-----------|-----------|
| **text** | Текстовое сообщение | STT не требуется |
| **voice** | Голосовое сообщение | STT (Whisper) |
| **document** | Документ (PDF/DOCX) | Извлечение текста |
| **photo** | Изображение | OCR |
| **callback_query** | Inline keyboard | Обработка кнопок |

---

#### Пример входящего сообщения

```json
{
  "update_id": 123456789,
  "message": {
    "message_id": 1,
    "from": {
      "id": 123456789,
      "first_name": "Ivan",
      "last_name": "Ivanov",
      "username": "ivanov"
    },
    "chat": {
      "id": 123456789,
      "type": "private"
    },
    "date": 1234567890,
    "text": "Привет! Меня зовут Иванов Иван. Опыт работы 5 лет..."
  }
}
```

---

### Исходящие сообщения

#### Типы сообщений

| Метод | Описание | Параметры |
|-------|-----------|-----------|
| **sendMessage** | Текстовое сообщение | chat_id, text, parse_mode |
| **sendVoice** | Голосовое сообщение | chat_id, voice |
| **sendPhoto** | Изображение | chat_id, photo, caption |
| **sendVideo** | Видео | chat_id, video, caption |

---

#### Пример исходящего сообщения

```json
{
  "method": "sendMessage",
  "chat_id": 123456789,
  "text": "Иван, спасибо за резюме!\n\nМы нашли для вас вакансию: **Senior Frontend Developer**\n\nScore: 85/100\nReason: Ваш опыт соответствует требованиям.",
  "parse_mode": "Markdown"
}
```

---

### Обработка ошибок

| Код ошибки | Описание | Действие |
|------------|----------|----------|
| **403** | Bot was blocked by user | Удалить chat_id из БД |
| **400** | Bad Request | Проверить формат сообщения |
| **429** | Too Many Requests | Retry с задержкой |
| **500** | Internal Server Error | Retry с экспоненциальной задержкой |

---

## Интеграция с OpenAI API

### Обзор

**Назначение:** AI-модели для извлечения данных, matching, TTS, генерации.

**Тип интеграции:** REST API

**Документация:** https://platform.openai.com/docs

---

### Используемые модели

| Модель | Назначение | Стоимость | Лимиты |
|--------|-----------|-----------|--------|
| **GPT-4o-mini** | Извлечение данных | ~$0.002/1K tokens | Rate limit |
| **GPT-4** | Matching | ~$0.03/1K tokens | Rate limit |
| **TTS** | Генерация голоса | ~$0.004/200 chars | Rate limit |
| **DALL-E 3** | Генерация изображений | ~$0.04/image | Rate limit |
| **Sora-2** | Генерация видео | High | Rate limit |

---

### Запрос к GPT-4o-mini

```javascript
const response = await openai.chat.completions.create({
  model: "gpt-4o-mini",
  temperature: 0,
  response_format: { type: "json_object" },
  messages: [
    {
      role: "system",
      content: "You are an HR data extraction assistant..."
    },
    {
      role: "user",
      content: `Resume text:\n${normalizedText}`
    }
  ]
});
```

---

### Запрос к GPT-4

```javascript
const response = await openai.chat.completions.create({
  model: "gpt-4",
  temperature: 0,
  messages: [
    {
      role: "system",
      content: "You are an HR matching assistant..."
    },
    {
      role: "user",
      content: `Candidate profile:\n${candidateProfile}\n\nOpen vacancies:\n${vacancies}`
    }
  ]
});
```

---

### Запрос к TTS

```javascript
const response = await openai.audio.speech.create({
  model: "tts-1",
  voice: "alloy",
  input: "Иван, спасибо за резюме! Мы нашли для вас вакансию..."
});

const buffer = Buffer.from(await response.arrayBuffer());
```

---

### Запрос к DALL-E 3

```javascript
const response = await openai.images.generate({
  model: "dall-e-3",
  size: "1024x1024",
  quality: "standard",
  n: 1,
  prompt: "Create a professional infographic for a job candidate matching result..."
});

const imageUrl = response.data[0].url;
```

---

### Обработка ошибок

| Код ошибки | Описание | Действие |
|------------|----------|----------|
| **401** | Invalid API key | Проверить OPENAI_API_KEY |
| **429** | Rate limit exceeded | Retry с экспоненциальной задержкой |
| **500** | Internal Server Error | Retry |
| **503** | Service Unavailable | Retry с задержкой |

---

### Retry механизм

```javascript
async function callWithRetry(fn, maxRetries = 3, delay = 5000) {
  for (let attempt = 0; attempt < maxRetries; attempt++) {
    try {
      return await fn();
    } catch (error) {
      if (error.status === 429 || error.status >= 500) {
        if (attempt < maxRetries - 1) {
          await sleep(delay * Math.pow(2, attempt));
          continue;
        }
      }
      throw error;
    }
  }
}
```

---

## Интеграция с PostgreSQL

### Обзор

**Назначение:** Хранение данных о кандидатах, вакансиях, результатах matching.

**Тип интеграции:** Прямое подключение

**Документация:** https://www.postgresql.org/docs/

---

### Схема БД

#### Основные таблицы

| Таблица | Назначение | Ключевые поля |
|---------|-----------|---------------|
| `intake_events` | Входящие события | id, execution_id, input_type |
| `candidate_inputs` | Входные данные | id, intake_event_id, normalized_text |
| `candidates` | Профили кандидатов | id, full_name, skills |
| `candidate_contacts` | Контакты | id, candidate_id, contact_value |
| `vacancies` | Вакансии | id, title, requirements |
| `matches` | Результаты matching | id, candidate_id, vacancy_id, score |
| `final_decisions` | Итоговые решения | id, candidate_id, best_match_id |
| `outbox` | Исходящие сообщения | id, status, body |

---

### Операции

#### Чтение кандидатов для обработки

```sql
SELECT * FROM candidate_inputs
WHERE processing_status = 'prepared'
ORDER BY created_at ASC
LIMIT 10;
```

---

#### Запись кандидата

```sql
INSERT INTO candidates (
  full_name, city, desired_position,
  experience_years, skills, salary_expectation,
  source_input_id, data_quality_status
)
VALUES (
  '{{full_name}}', '{{city}}', '{{desired_position}}',
  {{experience_years}}, '{{skills}}', {{salary_expectation}},
  '{{source_input_id}}', 'validated'
)
RETURNING id;
```

---

#### Запись matching

```sql
INSERT INTO matches (
  candidate_id, vacancy_id, score, decision, reason
)
VALUES (
  '{{candidate_id}}', '{{vacancy_id}}', {{score}}, '{{decision}}', '{{reason}}'
);
```

---

#### Чтение сообщений для доставки

```sql
SELECT * FROM outbox
WHERE status = 'pending'
ORDER BY created_at ASC
LIMIT 10;
```

---

### Обработка ошибок

| Ошибка | Описание | Действие |
|--------|-----------|----------|
| **Connection refused** | PostgreSQL недоступен | Retry с задержкой |
| **Duplicate key** | Нарушение уникальности | Игнорировать или обновить |
| **Foreign key violation** | Нарушение FK | Проверить связанные данные |
| **Deadlock** | Взаимная блокировка | Retry |

---

## Внутренние интеграции

### Workflow-схемы

**Общий поток обработки:**

```
HR Intake → candidate_inputs → HR Processing Worker → outbox → HR Delivery Worker
                  (prepared)                                  (pending)
```

**Workflow HR Intake (приём входящих сообщений):**

![Workflow HR Intake](screenshots/raw/report_v2_-017.png)

*Workflow HR Intake — приём и классификация входящих сообщений (43 узла)*

![Workflow HR Intake (детали)](screenshots/raw/report_v2_-018.png)

*Детали Workflow HR Intake*

**Workflow HR Processing Worker (обработка данных кандидата):**

![Workflow Processing Worker](screenshots/raw/report_v2_-019.png)

*Workflow HR Processing Worker — извлечение данных и matching (47 узлов)*

---

### HR Intake → HR Processing Worker

**Механизм:** База данных (таблица `candidate_inputs`)

**Протокол:**
1. HR Intake создаёт запись в `candidate_inputs` (status='prepared')
2. HR Processing Worker опрашивает таблицу каждые 10 секунд
3. Processing Worker обрабатывает и обновляет статус

**Статусы:**
- `prepared` — готов к обработке
- `processing_started` — в обработке
- `processed` — обработан
- `error` — ошибка

---

### HR Processing Worker → HR Delivery Worker

**Механизм:** База данных (таблица `outbox`)

**Протокол:**
1. Processing Worker создаёт запись в `outbox` (status='pending')
2. Delivery Worker опрашивает таблицу каждые 10 секунд
3. Delivery Worker отправляет и обновляет статус

**Статусы:**
- `pending` — готов к отправке
- `sending` — отправляется
- `sent` — отправлен
- `error` — ошибка

---

### Watchdogs → База данных

**Механизм:** SQL-запросы

**HR Queue Watchdog - candidate_inputs:**
```sql
UPDATE candidate_inputs
SET processing_status = 'prepared'
WHERE processing_status = 'processing_started'
  AND created_at < NOW() - INTERVAL '5 minutes';
```

**HR Queue Watchdog - outbox:**
```sql
UPDATE outbox
SET status = 'pending'
WHERE status = 'sending'
  AND created_at < NOW() - INTERVAL '10 minutes';
```

---

## Схема данных

### ER-диаграмма

```
intake_events (1) ── (1) candidate_inputs (1) ── (1) candidates
                                                      │
                                                      │ (1:N)
                                                      │
                                                      ▼
                                              candidate_contacts

candidates (N:M) ───────────────────────────── vacancies
    │                                               │
    │ (1:N)                                         │
    │                                               │
    ▼                                               │
  matches                                          │
    │                                               │
    │ (1:1)                                         │
    │                                               │
    ▼                                               │
final_decisions                                     │
    │                                               │
    │ (1:1)                                         │
    │                                               │
    ▼                                               │
  outbox ◄─────────────────────────────────────────┘
```

---

## Мониторинг интеграций

### Telegram Bot API

**Метрики:**
- Количество входящих сообщений в час
- Количество исходящих сообщений в час
- Ошибки webhook
- Latency

**SQL-запрос:**
```sql
SELECT
  COUNT(*) as messages_count,
  DATE_TRUNC('hour', received_at) as hour
FROM intake_events
WHERE received_at > NOW() - INTERVAL '24 hours'
GROUP BY hour
ORDER BY hour DESC;
```

---

### OpenAI API

**Метрики:**
- Количество запросов в час
- Количество токенов
- Ошибки API
- Latency

**SQL-запрос:**
```sql
SELECT
  COUNT(*) as requests_count,
  SUM((pl.details::jsonb->>'tokens')::int) as total_tokens
FROM processing_logs pl
WHERE pl.stage = 'llm_call'
  AND pl.created_at > NOW() - INTERVAL '24 hours';
```

---

### PostgreSQL

**Метрики:**
- Количество соединений
- Latency запросов
- Размер БД
- Количество записей

**SQL-запрос:**
```sql
SELECT
  (SELECT COUNT(*) FROM candidates) as candidates_count,
  (SELECT COUNT(*) FROM matches) as matches_count,
  (SELECT COUNT(*) FROM outbox WHERE status = 'pending') as pending_messages;
```

---

## Связанные документы

- [ARCHITECTURE.md](ARCHITECTURE.md) — архитектура системы
- [SPEC.md](SPEC.md) — спецификация системы
- [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) — руководство по развёртыванию
- [SUPPORT_RUNBOOK.md](SUPPORT_RUNBOOK.md) — инструкция для поддержки

---

**Статус документа:** Production-ready
**Последнее обновление:** 2026-06-23