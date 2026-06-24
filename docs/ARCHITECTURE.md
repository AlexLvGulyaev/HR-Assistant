# Архитектура системы HR Assistant

Документ описывает архитектуру, компоненты, потоки данных и технические решения HR Assistant.

---

## Обзор архитектуры

HR Assistant построен по принципу **event-driven architecture** с использованием n8n как оркестратора и PostgreSQL для хранения данных.

**Ключевые принципы:**
- Декомпозиция на независимые этапы обработки
- Слабая связность между компонентами
- Асинхронное взаимодействие через БД
- Идемпотентность операций
- Устойчивость к ошибкам

---

## Архитектурная диаграмма

![Архитектура HR Assistant](screenshots/raw/report_v2_-000.png)

*Архитектура системы: Telegram Bot → n8n Workflows → PostgreSQL → OpenAI API*

```
┌─────────────────────────────────────────────────────────────┐
│                     Telegram Bot API                        │
│                  (Webhook + Inline Keyboard)                 │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                     n8n Workflows                            │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  HR Intake   │──│ Processing   │──│  Delivery    │      │
│  │  (Webhook)   │  │   Worker     │  │   Worker     │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│         │                  │                  │              │
│         └──────────────────┼──────────────────┘              │
│                            ▼                                 │
│                   ┌──────────────┐                           │
│                   │  PostgreSQL  │                           │
│                   │   Database   │                           │
│                   └──────────────┘                           │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ HR Generate  │  │   Watchdog   │  │   Watchdog   │      │
│  │    Video     │  │  (inputs)    │  │  (outbox)    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                      OpenAI API                              │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐       │
│  │  GPT-4   │ │ GPT-4o   │ │  TTS     │ │  Sora-2  │       │
│  │          │ │  mini    │ │          │ │          │       │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘       │
└─────────────────────────────────────────────────────────────┘
```

---

## Компоненты системы

### 1. HR Intake Workflow

**Назначение:** Приём и классификация входящих сообщений из Telegram.

**Триггер:** Telegram Webhook (message, callback_query)

**Функции:**
- Приём входящих сообщений
- Классификация типа: text, voice, document, image, callback
- Нормализация данных
- Запись в `intake_events` и `candidate_inputs`

**Узлы:** 43

**Поток данных:**
```
Telegram Message → Webhook → Classification → Normalization → DB Insert
```

---

### 2. HR Processing Worker

**Назначение:** Извлечение данных кандидата и matching с вакансиями.

**Триггер:** Schedule (каждые 10 секунд)

**Функции:**
- Чтение записей из `candidate_inputs` (status='prepared')
- Извлечение данных с помощью GPT-4o-mini
- Валидация JSON-структуры
- Создание записи кандидата в `candidates`
- Matching с вакансиями (GPT-4)
- Подготовка ответа в `outbox`

**Узлы:** 47

**Поток данных:**
```
DB Query → OpenAI (Extract) → JSON Validate → DB Insert (candidates) → OpenAI (Match) → DB Insert (outbox)
```

**Обработка ошибок:**
- Попытка ремонта JSON (repair)
- Fallback на невалидный JSON
- Fallback на processing error

---

### 3. HR Delivery Worker

**Назначение:** Доставка мультимедийного ответа кандидату.

**Триггер:** Schedule (каждые 10 секунд)

**Функции:**
- Чтение записей из `outbox` (status='pending')
- Генерация TTS (если metadata.tts_required)
- Генерация визуалов (если metadata.visual_required)
- Отправка сообщения в Telegram
- Обновление статуса `outbox`

**Узлы:** 21

**Поток данных:**
```
DB Query → TTS Generation → Visual Generation → Telegram Send → DB Update
```

---

### 4. HR Generate Video

**Назначение:** Генерация видео по запросу пользователя.

**Триггер:** Manual / Execute Workflow Trigger

**Функции:**
- Генерация видео через OpenAI Sora-2
- Polling статуса генерации (до 20 попыток)
- Отправка результата в Telegram

**Узлы:** 15

---

### 5. HR Queue Watchdog - candidate_inputs

**Назначение:** Сброс зависших обработок.

**Триггер:** Schedule (каждые 5 минут)

**Функции:**
- Поиск записей со статусом `processing_started` > 5 минут
- Сброс в `prepared` или `error`

**Узлы:** 2

---

### 6. HR Queue Watchdog - outbox

**Назначение:** Сброс зависших сообщений.

**Триггер:** Schedule (каждые 10 минут)

**Функции:**
- Поиск записей со статусом `sending` > 10 минут
- Сброс в `pending` или `error`

**Узлы:** 2

---

## База данных

### ER-диаграмма

![ER-диаграмма базы данных HR Assistant](screenshots/raw/report_v2_-001.png)

*ER-диаграмма базы данных HR Assistant*

```
┌─────────────────┐
│  intake_events   │
│  ─────────────── │
│  id (PK)         │
│  execution_id    │
│  source          │
│  input_type      │
│  telegram_chat_id│
│  telegram_user_id│
│  received_at     │
│  status          │
└────────┬─────────┘
         │
         │ 1:1
         ▼
┌─────────────────────┐
│  candidate_inputs   │
│  ────────────────── │
│  id (PK)            │
│  intake_event_id(FK)│
│  input_type         │
│  normalized_text    │
│  processing_status  │
└────────┬─────────────┘
         │
         │ 1:1
         ▼
┌─────────────────────┐      ┌─────────────────────┐
│    candidates       │      │ candidate_contacts  │
│  ────────────────── │      │  ────────────────── │
│  id (PK)            │──1:N─│  id (PK)            │
│  full_name          │      │  candidate_id (FK)  │
│  city               │      │  contact_type       │
│  desired_position   │      │  contact_value      │
│  experience_years   │      └─────────────────────┘
│  skills             │
│  salary_expectation │
│  source_input_id(FK)│
└────────┬─────────────┘
         │
         │ N:M
         ▼
┌─────────────────────┐      ┌─────────────────────┐
│      matches        │      │     vacancies       │
│  ────────────────── │      │  ────────────────── │
│  id (PK)            │      │  id (PK)            │
│  candidate_id (FK)  │      │  title              │
│  vacancy_id (FK)    │      │  description        │
│  score              │      │  requirements       │
│  decision           │      │  salary_min         │
│  reason             │      │  salary_max         │
│  created_at         │      │  status             │
└─────────────────────┘      └─────────────────────┘
         │
         │ 1:1
         ▼
┌─────────────────────┐
│  final_decisions    │
│  ────────────────── │
│  id (PK)            │
│  candidate_id (FK)  │
│  best_match_id (FK)│
│  has_match          │
│  decision_reason    │
└─────────────────────┘
         │
         │ 1:1
         ▼
┌─────────────────────┐
│      outbox         │
│  ────────────────── │
│  id (PK)            │
│  intake_event_id(FK)│
│  candidate_id (FK)  │
│  channel            │
│  recipient          │
│  message_type       │
│  body               │
│  metadata (jsonb)   │
│  status             │
└─────────────────────┘
```

---

### Основные таблицы

| Таблица | Назначение | Ключевые поля |
|---------|-----------|---------------|
| `intake_events` | Входящие события | id, execution_id, input_type, telegram_chat_id |
| `candidate_inputs` | Входные данные | id, intake_event_id, normalized_text, processing_status |
| `candidates` | Профили кандидатов | id, full_name, city, skills, salary_expectation |
| `candidate_contacts` | Контакты | id, candidate_id, contact_type, contact_value |
| `vacancies` | Вакансии | id, title, description, salary_min, salary_max |
| `matches` | Результаты matching | id, candidate_id, vacancy_id, score, decision |
| `final_decisions` | Итоговые решения | id, candidate_id, best_match_id, has_match |
| `outbox` | Исходящие сообщения | id, channel, recipient, body, status, metadata |
| `processing_logs` | Журнал обработки | id, execution_id, stage, status, error_text |
| `generated_assets` | Сгенерированные материалы | id, candidate_id, asset_type, asset_url |
| `bot_credentials` | Учётные данные | bot_code, bot_token |

---

### Индексы

| Индекс | Таблица | Поля | Назначение |
|--------|---------|------|-----------|
| `idx_intake_events_execution_id` | intake_events | execution_id | Поиск по execution_id |
| `idx_intake_events_telegram` | intake_events | telegram_chat_id, telegram_user_id | Поиск по Telegram ID |
| `idx_candidate_inputs_execution_id` | candidate_inputs | execution_id | Поиск по execution_id |
| `idx_candidate_inputs_file_hash` | candidate_inputs | file_hash | Дедупликация файлов |
| `idx_candidate_contacts_normalized` | candidate_contacts | normalized_value | Поиск по нормализованным контактам |
| `idx_vacancies_status` | vacancies | status | Поиск активных вакансий |
| `idx_matches_candidate_score` | matches | candidate_id, score | Поиск лучших matching |
| `idx_processing_logs_execution_id` | processing_logs | execution_id | Поиск логов по execution |
| `idx_outbox_status` | outbox | status | Выборка pending сообщений |

---

## Потоки данных

### Общий pipeline обработки

```
Пользователь (Telegram)
    │
    ▼
HR Intake
    │
    ├─ Классификация типа (text/voice/document/image/callback)
    ├─ Нормализация данных
    └─ Запись в БД (intake_events, candidate_inputs)
    │
    ▼
PostgreSQL (candidate_inputs: status='prepared')
    │
    ▼
HR Processing Worker
    │
    ├─ Извлечение данных (GPT-4o-mini)
    ├─ Валидация JSON
    ├─ Создание кандидата (candidates)
    ├─ Matching с вакансиями (GPT-4)
    └─ Подготовка ответа (outbox)
    │
    ▼
PostgreSQL (outbox: status='pending')
    │
    ▼
HR Delivery Worker
    │
    ├─ Генерация TTS (OpenAI TTS)
    ├─ Генерация визуалов (GPT-image-1)
    ├─ Отправка в Telegram
    └─ Обновление статуса (outbox: status='sent')
    │
    ▼
Telegram (ответ пользователю)
```

---

### Мультимодальный ввод

#### Текст

```
Telegram Message (text)
    │
    ▼
HR Intake
    │
    ├─ Классификация: text
    ├─ Нормализация: text → normalized_text
    └─ Запись: candidate_inputs
    │
    ▼
Processing (стандартный pipeline)
```

---

#### Голосовое сообщение

```
Telegram Message (voice)
    │
    ▼
HR Intake
    │
    ├─ Загрузка аудио (Telegram API)
    ├─ STT (OpenAI Whisper)
    ├─ Классификация: voice
    ├─ Нормализация: text → normalized_text
    └─ Запись: candidate_inputs
    │
    ▼
Processing (стандартный pipeline)
```

---

#### Документ (PDF/DOCX)

```
Telegram Message (document)
    │
    ▼
HR Intake
    │
    ├─ Загрузка файла (Telegram API)
    ├─ Извлечение текста (PDF/DOCX parser)
    ├─ Классификация: document
    ├─ Нормализация: text → normalized_text
    └─ Запись: candidate_inputs
    │
    ▼
Processing (стандартный pipeline)
```

---

#### Изображение

```
Telegram Message (photo)
    │
    ▼
HR Intake
    │
    ├─ Загрузка изображения (Telegram API)
    ├─ OCR (GPT-4 Vision или Tesseract)
    ├─ Классификация: image
    ├─ Нормализация: text → normalized_text
    └─ Запись: candidate_inputs
    │
    ▼
Processing (стандартный pipeline)
```

---

## Интеграции

### Telegram Bot API

**Тип:** Webhook

**Входящие сообщения:**
- `message` (text, voice, document, photo)
- `callback_query` (inline keyboard)

**Исходящие сообщения:**
- `sendMessage` (текст)
- `sendVoice` (голосовые сообщения)
- `sendPhoto` (изображения)
- `sendVideo` (видео)

**Webhook setup:**
```bash
curl -X POST "https://api.telegram.org/bot<token>/setWebhook" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://your-n8n-instance.com/webhook/hr-assistant"}'
```

---

### OpenAI API

**Модели:**

| Модель | Назначение | Параметры |
|--------|-----------|-----------|
| **GPT-4o-mini** | Извлечение данных кандидата | Temperature: 0, Response format: JSON Schema |
| **GPT-4** | Matching кандидата с вакансиями | Temperature: 0 |
| **GPT-image-1** | Генерация визуальных материалов | Size: 1024x1024 |
| **Sora-2** | Генерация видео | Size: 720x1280, Duration: 4 sec |
| **TTS** | Генерация голосовых сообщений | Language: Russian |

---

## Обработка ошибок

### Уровни обработки

| Уровень | Workflow | Типы ошибок | Обработка |
|---------|----------|-------------|-----------|
| **Intake** | HR Intake | Ошибки входных данных | Fallback-сообщение пользователю |
| **Processing** | HR Processing Worker | Ошибки LLM, JSON | Retry, JSON repair, fallback |
| **Delivery** | HR Delivery Worker | Ошибки отправки | Retry, error status |
| **Watchdog** | Watchdogs | Зависшие записи | Сброс статуса |

---

### Retry механизм

**Параметры:**
- Количество попыток: 3
- Интервал: 5 секунд

**Применяется:**
- OpenAI API calls
- Telegram API calls
- Database operations

---

### Fallback сценарии

**Processing Worker:**
1. Попытка извлечь данные (GPT-4o-mini)
2. При ошибке → JSON repair
3. При ошибке → fallback на невалидный JSON
4. При ошибке → processing error (сообщение пользователю)

**Delivery Worker:**
1. Попытка отправить сообщение
2. При ошибке → retry (3 попытки)
3. При ошибке → error status в `outbox`

---

## Масштабируемость

### Горизонтальное масштабирование

**Возможно:**
- Запуск нескольких Processing Worker
- Запуск нескольких Delivery Worker
- Разделение по типам обработки

**Ограничения:**
- n8n не является high-load платформой
- PostgreSQL single instance

---

### Расширение системы

**Добавление новых каналов:**
- Email (входящие письма)
- Web-form (веб-форма на сайте)
- WhatsApp (через Twilio)

**Добавление новых типов обработки:**
- Новые модели LLM
- Новые форматы вывода
- Интеграция с ATS/CRM

---

## Ограничения архитектуры

### Технические ограничения

1. **n8n не является high-load платформой**
   - Ограниченная производительность
   - Нет встроенного масштабирования

2. **PostgreSQL Single Instance**
   - Нет горизонтального масштабирования БД
   - Ограничения по объёму данных

3. **OpenAI API Rate Limits**
   - Зависимость от лимитов OpenAI
   - Стоимость токенов при масштабировании

---

### Функциональные ограничения

1. **Один язык**
   - Система работает только с русским языком
   - Нет мультиязычной поддержки

2. **Нет аутентификации**
   - Любой пользователь Telegram может использовать бота
   - Нет разграничения доступа

3. **Нет персистентности сессий**
   - Каждый запрос обрабатывается независимо
   - Нет контекста предыдущих сообщений

---

## Безопасность

### Текущее состояние

**Credentials:**

| Credential | Хранение | Использование |
|------------|----------|---------------|
| **PostgreSQL** | n8n credential store | Все workflows |
| **OpenAI API** | n8n credential store | Все AI-операции |
| **Telegram Bot Token** | Два источника: | |
| └─ HR Intake | n8n credential store | Telegram Trigger, get voice/doc/image |
| └─ HR Delivery Worker | `bot_credentials` таблица | HTTP Telegram requests |
| └─ HR Generate Video | n8n credential store | sendVideo |
| └─ Error Handler | n8n credential store | sendMessage |

**Архитектура хранения Telegram токена:**

HR Assistant использует гибридную архитектуру хранения Telegram Bot Token:

1. **n8n credential store** — для HR Intake, HR Generate Video, Error Handler
2. **bot_credentials таблица** — для HR Delivery Worker

**Обоснование:**
- Delivery Worker читает токен из БД, что позволяет менять его без перезапуска n8n
- Упрощает ротацию токенов
- Не требует обновления n8n credentials при смене токена

**⚠️ KP-002: Bot token в репозитории**

**Проблема:**
- Файл `schema_hr_assistant.sql` содержит реальный bot token в INSERT-запросе

**Решение:**
- Заменить реальный токен на placeholder для GitHub-публикации
- Документировать процесс обновления токена в DEPLOYMENT_GUIDE

**Рекомендации:**
- Хранить токен в n8n credential store (для HR Intake, HR Generate Video, Error Handler)
- Использовать bot_credentials для Delivery Worker
- Внедрить rotation policy для токенов

---

### Данные пользователей

**Персональные данные:**
- ФИО кандидатов
- Контакты (email, телефон)
- Информация о зарплате

**Рекомендации:**
- Анонимизация данных для аналитики
- Шифрование чувствительных полей
- GDPR/ФЗ-152 compliance

---

## Связанные документы

- [SPEC.md](SPEC.md) — спецификация системы
- [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) — руководство по развёртыванию
- [AI_QUALIFICATION.md](AI_QUALIFICATION.md) — промпты и модели
- [SUPPORT_RUNBOOK.md](SUPPORT_RUNBOOK.md) — инструкция для поддержки
- [known-issues.md](known-issues.md) — известные проблемы

---

**Статус документа:** Production-ready
**Последнее обновление:** 2026-06-23