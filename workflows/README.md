# HR Assistant Workflows

**Last Updated:** 2026-06-23

---

## Состав workflow

### Основные workflow (6)

#### 1. HR Intake (hr-intake.json)

**Узлов:** 43

**Триггер:** Telegram webhook (message, callback_query)

**Функции:**
- Прием входящих сообщений из Telegram
- Роутинг: команды (/start, /help), callbacks (help, about, restart, apply, next, video)
- Классификация типа ввода: text, voice, document, image, callback
- Запись в `intake_events` и `candidate_inputs`

**Интеграции:**
- Telegram Bot API (webhook)
- PostgreSQL (INSERT)

---

#### 2. HR Processing Worker (hr-processing-worker.json)

**Узлов:** 47

**Триггер:** Schedule (каждые 10 секунд)

**Функции:**
- Чтение записей из `candidate_inputs` (status='prepared')
- Извлечение данных кандидата с помощью OpenAI GPT-4o-mini
- Валидация JSON-структуры
- Попытка ремонта невалидного JSON
- Создание/обновление записи кандидата в `candidates`
- Matching с вакансиями (GPT-4)
- Подготовка ответа в `outbox`

**Интеграции:**
- PostgreSQL (SELECT, UPDATE, INSERT)
- OpenAI API (GPT-4o-mini, GPT-4)

**Обработка ошибок:**
- Retry (3 попытки, интервал 5 секунд)
- Fallback на невалидный JSON
- Fallback на processing error

---

#### 3. HR Delivery Worker (hr-delivery-worker.json)

**Узлов:** 21

**Триггер:** Schedule (каждые 10 секунд)

**Функции:**
- Чтение записей из `outbox` (status='pending')
- Генерация TTS (при `metadata.tts_required`)
- Генерация визуалов (при `metadata.visual_required`)
- Отправка сообщения в Telegram
- Обновление статуса `outbox` (status='sent' или 'error')

**Интеграции:**
- PostgreSQL (SELECT FOR UPDATE SKIP LOCKED, UPDATE)
- OpenAI API (TTS, GPT-image-1)
- Telegram Bot API (sendMessage, sendVoice, sendPhoto)

---

#### 4. HR Generate Video (hr-generate-video.json)

**Узлов:** 15

**Триггер:** Manual / Execute Workflow Trigger

**Функции:**
- Генерация видео через OpenAI Sora-2
- Polling статуса генерации (до 20 попыток, интервал 15 секунд)
- Отправка результата в Telegram

**Интеграции:**
- OpenAI API (Sora-2)
- Telegram Bot API (sendVideo)

---

#### 5. HR Queue Watchdog - candidate_inputs (hr-queue-watchdog-candidate-inputs.json)

**Узлов:** 2

**Триггер:** Schedule (каждые 5 минут)

**Функции:**
- Сброс зависших записей в `candidate_inputs` (processing → prepared)

**Интеграции:**
- PostgreSQL (UPDATE)

---

#### 6. HR Queue Watchdog - outbox (hr-queue-watchdog-outbox.json)

**Узлов:** 2

**Триггер:** Schedule (каждые 10 минут)

**Функции:**
- Сброс зависящих записей в `outbox` (sending → pending)

**Интеграции:**
- PostgreSQL (UPDATE)

---

### Вспомогательные workflow (1)

#### 7. error_handler (error-handler.json)

**Узлов:** 5

**Триггер:** Execute Workflow Trigger

**Функции:**
- Централизованная обработка ошибок
- Логирование в `processing_logs`

---

## Импорт в n8n

```bash
# Импорт всех workflow
for workflow in workflows/*.json; do
  n8n import:workflow --input="$workflow"
done

# Или через UI:
# Settings → Import from File → выберите .json файл
```

---

## Конфигурация

### Credentials в n8n

Workflows используют n8n credential store для хранения credentials:

#### 1. PostgreSQL Credential

| Параметр | Значение |
|----------|----------|
| **Type** | Postgres account |
| **Host** | postgres_hr |
| **Port** | 5432 |
| **Database** | hr_assistant |
| **User** | hr_user |
| **Password** | (из docker-compose.yml) |

**Используется:** Все workflows (PostgreSQL nodes)

#### 2. OpenAI API Credential

| Параметр | Значение |
|----------|----------|
| **Type** | Header Auth |
| **Name** | Authorization |
| **Value** | Bearer YOUR_OPENAI_API_KEY |

**Используется:** HR Intake, HR Processing Worker, HR Delivery Worker, HR Generate Video (OpenAI HTTP Request nodes)

#### 3. Telegram API Credential

| Параметр | Значение |
|----------|----------|
| **Type** | Telegram API |
| **Bot Token** | YOUR_TELEGRAM_BOT_TOKEN |

**Используется:**
- HR Intake (Telegram Trigger, get voice, get document, get image)
- HR Generate Video (send generated video)
- Error Handler (send text message)

**Важно:** HR Delivery Worker НЕ использует этот credential, а читает bot_token из таблицы `bot_credentials`.

### bot_credentials Таблица

HR Delivery Worker читает Telegram bot token из БД:

```sql
SELECT bot_token FROM bot_credentials WHERE bot_code = 'hr_assistant';
```

**Для обновления токена:**
```sql
UPDATE bot_credentials
SET bot_token = 'NEW_TOKEN'
WHERE bot_code = 'hr_assistant';
```

### Переменные окружения (Docker Compose)

Для production-развёртывания используйте `.env` файл:

```bash
cp .env.example .env
# Отредактируйте .env
```

Переменные в `.env`:
- `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`
- `N8N_HOST`, `WEBHOOK_URL`, `N8N_ENCRYPTION_KEY`

Для быстрого старта можно использовать defaults из `config/docker-compose.yml`.

**Важно:** `TELEGRAM_BOT_TOKEN` и `OPENAI_API_KEY` НЕ используются в environment variables.
Credentials настраиваются в n8n credential store.

### Telegram Bot Token

Перед первым запуском замените placeholder в `database/schema_hr_assistant.sql`:

```sql
'REPLACE_ME_WITH_YOUR_BOT_TOKEN' → 'ВАШ_РЕАЛЬНЫЙ_ТОКЕН'
```

Или обновите после запуска:

```sql
UPDATE bot_credentials
SET bot_token = 'ВАШ_РЕАЛЬНЫЙ_ТОКЕН'
WHERE bot_code = 'hr_assistant';
```

---

## Известные проблемы

См. [known-issues.md](../docs/known-issues.md):
- KP-001: НЕСОВМЕСТИМОСТЬ metadata — поле не заполняется в Processing Worker

---

## References

- [SPEC.md](../docs/SPEC.md) — функциональная спецификация
- [database/README.md](../database/README.md) — схема БД
- [../README.md](../README.md) — описание кейса