# Журнал изменений HR Assistant

Документ отслеживает изменения в HR Assistant на уровне системы.

---

## Формат

Журнал изменений следует [Keep a Changelog](https://keepachangelog.com/).

**Типы изменений:**
- `Added` — новые функции
- `Changed` — изменения в существующих функциях
- `Deprecated` — функции, которые будут удалены
- `Removed` — удалённые функции
- `Fixed` — исправления ошибок
- `Security` — изменения безопасности

---

## [2.0.0] - 2026-04-29

### Fixed

- **KP-002** — Захардкоженные credentials в SQL (2026-06-24)
  - Заменён реальный bot token на placeholder: `REPLACE_ME_WITH_YOUR_BOT_TOKEN`
  - Добавлена документация по архитектуре хранения токена в DEPLOYMENT_GUIDE.md
  - Добавлено предупреждение в README.md о необходимости замены токена перед запуском

### Added

#### Мультимодальный ввод

- **Текстовые сообщения** — приём текстовых резюме через Telegram
- **Голосовые сообщения** — STT-транскрибация голосовых сообщений (OpenAI Whisper)
- **Документы (PDF/DOCX)** — извлечение текста из документов
- **Изображения** — OCR-распознавание фото резюме (GPT-4 Vision)

#### Извлечение данных

- **Структурированные данные** — автоматическое извлечение ФИО, города, должности, опыта, навыков, зарплаты, контактов
- **JSON Schema** — валидация структуры ответа LLM
- **JSON Repair** — автоматическое исправление невалидного JSON

#### Matching с вакансиями

- **Автоматический matching** — сравнение профиля кандидата с открытыми вакансиями
- **Score (0-100)** — оценка соответствия кандидата вакансии
- **Decision (match/no_match)** — рекомендация системы
- **Reason** — обоснование решения

#### Мультимедийный вывод

- **Текстовые сообщения** — текстовый ответ в Telegram
- **Голосовые сообщения (TTS)** — аудиоверсия ответа (OpenAI TTS)
- **Визуальные материалы** — инфографика с результатами matching (DALL-E 3)

#### Telegram Bot

- **Webhook интеграция** — приём сообщений через Telegram Bot API
- **Inline Keyboard** — интерактивные кнопки
- **Команды** — `/start`, `/help`, `/about`

#### Workflow

- **HR Intake Workflow** (43 узла) — приём и классификация входящих сообщений
- **HR Processing Worker** (47 узлов) — извлечение данных и matching
- **HR Delivery Worker** (21 узел) — доставка мультимедийных ответов
- **HR Generate Video** (15 узлов) — генерация видео по запросу
- **HR Queue Watchdog - candidate_inputs** (2 узла) — сброс зависших обработок
- **HR Queue Watchdog - outbox** (2 узла) — сброс зависших сообщений

#### База данных

- **11 таблиц** — intake_events, candidate_inputs, candidates, candidate_contacts, vacancies, matches, final_decisions, outbox, processing_logs, generated_assets, bot_credentials
- **Индексы** — оптимизация запросов
- **Функции** — log_processing_event()

### Changed

#### Архитектура

- **Event-driven architecture** — переход на событийную модель
- **Queue-based processing** — обработка через очереди в БД
- **Idempotency** — идемпотентность операций

#### Обработка ошибок

- **Retry механизм** — 3 попытки с экспоненциальной задержкой
- **Fallback сценарии** — обработка ошибок на каждом этапе
- **Watchdogs** — автоматический сброс зависших записей

### Fixed

- Обработка невалидного JSON от LLM
- Обработка пустых сообщений
- Обработка неподдерживаемых форматов

### Security

- ✅ **KP-002** — Захардкоженные credentials в SQL (исправлено: заменён на placeholder, добавлена документация)

---

## [1.0.0] - 2026-04-15

### Added

#### Базовая функциональность

- Приём текстовых резюме через Telegram
- Извлечение данных с помощью GPT-4o-mini
- Сравнение с вакансиями
- Текстовый ответ в Telegram

#### Инфраструктура

- Docker Compose конфигурация
- PostgreSQL база данных
- n8n workflows

---

## Критические проблемы

### KP-001: НЕСОВМЕСТИМОСТЬ metadata

**Статус:** Open

**Приоритет:** 🔴 Critical

**Описание:** Поле `metadata` в таблице `outbox` не заполняется в Processing Worker, но используется в Delivery Worker.

**Влияние:**
- TTS не работает корректно (fallback на текст из `body`)
- Visual generation не работает корректно (fallback на default prompt)

**План исправления:**
1. Определить источник данных для metadata полей
2. Добавить заполнение metadata в Processing Worker
3. Протестировать TTS и visual generation
4. Документировать формат metadata

**Дата выявления:** 2026-06-23

---

### KP-002: ЗАХАРДКОЖЕННЫЕ CREDENTIALS

**Статус:** Open

**Приоритет:** ⚠️ Medium

**Описание:** Bot token захардкожен в SQL-файле.

**Влияние:**
- Риск утечки credentials при публикации
- Сложность ротации токена

**План исправления:**
1. Удалить INSERT из SQL-файла
2. Настроить чтение токена из environment variable
3. Добавить инструкцию по настройке в README.md

**Дата выявления:** 2026-06-23

---

### KP-003: ОТСУТСТВИЕ ВЕРСИОНИРОВАНИЯ WORKFLOW

**Статус:** Open

**Приоритет:** ⚠️ Medium

**Описание:** Отсутствует версионирование workflow n8n.

**Влияние:**
- Сложность отката изменений
- Отсутствие истории изменений

**План исправления:**
1. Внедрить Git-based версионирование workflow JSON
2. Создать CHANGELOG.md (этот документ)
3. Добавить теги версий в README.md

**Дата выявления:** 2026-06-23

---

## Roadmap

### [2.1.0] - Планируется

#### Добавить

- **Email-канал** — приём резюме через email
- **Web-form** — веб-форма для подачи резюме
- **WhatsApp** — интеграция с WhatsApp через Twilio

#### Исправить

- **KP-001** — Заполнение metadata в Processing Worker
- **KP-002** — Перенос credentials в environment variables

---

### [2.2.0] - Планируется

#### Добавить

- **Аутентификация** — ограничение доступа к боту
- **Персонализация** — контекст предыдущих сообщений
- **Мультиязычность** — поддержка английского языка

#### Изменить

- **Масштабирование** — разделение на микросервисы
- **Мониторинг** — добавление дашбордов

---

### [3.0.0] - Будущее

#### Добавить

- **Интеграция с ATS/CRM** — автоматическая передача кандидатов в HR-системы
- **Аналитика** — дашборды для HR-специалистов
- **A/B-тестирование** — сравнение промптов и моделей

#### Изменить

- **High-load архитектура** — переход на микросервисы
- **Очереди** — внедрение RabbitMQ/Kafka

---

## Деплой-ноты

### [2.0.0]

**Требования:**
- Docker 20.10+
- Docker Compose 2.0+
- PostgreSQL 14+
- n8n 1.0+

**Миграция БД:**
```sql
-- Выполнить schema_hr_assistant.sql
\i database/schema_hr_assistant.sql
```

**Переменные окружения:**
```bash
TELEGRAM_BOT_TOKEN=<your_bot_token>
OPENAI_API_KEY=<your_openai_api_key>
POSTGRES_USER=hr_assistant
POSTGRES_PASSWORD=<secure_password>
POSTGRES_DB=hr_assistant
```

**Workflows:**
- Импортировать все workflow из `workflows/`
- Активировать workflows

**Webhook:**
```bash
curl -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/setWebhook" \
  -H "Content-Type: application/json" \
  -d "{\"url\": \"https://your-domain.com/webhook/hr-assistant\"}"
```

---

## Ссылки

- [SPEC.md](SPEC.md) — спецификация системы
- [ARCHITECTURE.md](ARCHITECTURE.md) — архитектура системы
- [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) — руководство по развёртыванию
- [known-issues.md](known-issues.md) — известные проблемы

---

**Статус документа:** Production-ready
**Последнее обновление:** 2026-06-24