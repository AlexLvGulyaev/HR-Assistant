# SPEC: HR Assistant

**Version:** 2.0  
**Last Updated:** 2026-06-23  
**Status:** Production-ready

---

## 1. Общее описание

### 1.1 Назначение системы

**HR Assistant** — AI-ассистент для автоматизации первичной обработки резюме и подбора вакансий. Система предоставляет пользователям возможность отправить резюме в любом удобном формате (текст, голос, документ, изображение) через Telegram-бота, автоматически извлекает структурированные данные кандидата, сравнивает профиль с открытыми вакансиями и формирует мультимедийный ответ.

### 1.2 Бизнес-цели

1. **Автоматизация рутинных операций** — снизить время на первичный анализ резюме с 10-15 минут до < 1 минуты
2. **Мультимодальный ввод** — принять резюме в любом формате (текст, голос, документ, фото)
3. **Структурирование данных** — автоматически извлекать ФИО, контакты, опыт, навыки, зарплатные ожидания
4. **Matching кандидатов** — автоматически сравнивать профиль кандидата с открытыми вакансиями
5. **Мультимедийный вывод** — предоставлять ответ в удобном формате (текст + голос + визуальные материалы)

### 1.3 Целевые пользователи

**Основные:**
- HR-специалисты
- Рекрутеры
- Кандидаты (через Telegram-бот)

**Вторичные:**
- Разработчики (интеграция с существующими HR-системами)
- Product Manager (аналитика процесса подбора)

### 1.4 Ключевые сценарии использования

#### Scenario 1: Обработка текстового резюме

1. Пользователь отправляет текст резюме в Telegram-бот
2. Система извлекает структурированные данные (ФИО, город, должность, опыт, навыки, контакты)
3. Система сравнивает профиль кандидата с открытыми вакансиями
4. Система формирует ответ: подходящая вакансия или сообщение об отсутствии подходящей позиции
5. Пользователь получает мультимедийный ответ (текст + голос + визуал)

#### Scenario 2: Обработка голосового сообщения

1. Пользователь отправляет голосовое сообщение с описанием опыта
2. Система транскрибирует голос в текст (OpenAI Whisper)
3. Система извлекает данные и выполняет matching
4. Пользователь получает ответ

#### Scenario 3: Обработка документа (PDF/DOCX)

1. Пользователь отправляет файл резюме
2. Система извлекает текст из документа
3. Система выполняет стандартную обработку
4. Пользователь получает ответ

#### Scenario 4: Обработка изображения

1. Пользователь отправляет фото резюме
2. Система извлекает текст с помощью OCR (или GPT-4 Vision)
3. Система выполняет стандартную обработку
4. Пользователь получает ответ

---

## 2. Архитектура

### 2.1 Тип архитектуры

**Event-driven architecture** с использованием n8n как оркестратора и PostgreSQL для хранения данных.

### 2.2 Компоненты системы

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

### 2.3 Workflow состав

#### HR Intake (43 узла)

**Триггер:** Telegram webhook (message, callback_query)

**Функции:**
- Прием входящих сообщений из Telegram
- Роутинг: команды (/start, /help), callbacks (help, about, restart, apply, next, video), обычные сообщения
- Классификация типа ввода: text, voice, document, image, callback
- Запись в `intake_events` и `candidate_inputs`

**Обработка:**
- Команды → немедленный ответ
- Callbacks → роутинг по кнопкам
- Обычные сообщения → классификация и подготовка к обработке

#### HR Processing Worker (47 узлов)

**Триггер:** Schedule (каждые 10 секунд)

**Функции:**
- Чтение записей из `candidate_inputs` (status='prepared')
- Извлечение данных кандидата с помощью OpenAI GPT-4o-mini
- Валидация JSON-структуры
- Создание/обновление записи кандидата в `candidates`
- Matching с вакансиями (GPT-4)
- Подготовка ответа в `outbox`

**Обработка ошибок:**
- Попытка ремонта JSON (repair)
- Fallback на невалидный JSON
- Fallback на processing error

#### HR Delivery Worker (21 узел)

**Триггер:** Schedule (каждые 10 секунд)

**Функции:**
- Чтение записей из `outbox` (status='pending')
- Генерация TTS (если metadata.tts_required)
- Генерация визуалов (если metadata.visual_required)
- Отправка сообщения в Telegram
- Обновление статуса `outbox` (status='sent' или 'error')

**Мультимедиа:**
- Text-to-Speech (OpenAI TTS)
- Image Generation (GPT-image-1)
- Video Generation (Sora-2)

#### HR Generate Video (15 узлов)

**Триггер:** Manual / Execute Workflow Trigger

**Функции:**
- Генерация видео через OpenAI Sora-2
- Polling статуса генерации (до 20 попыток)
- Отправка результата в Telegram

#### HR Queue Watchdog - candidate_inputs (2 узла)

**Триггер:** Schedule (каждые 5 минут)

**Функции:**
- Сброс зависших записей (processing → prepared)

#### HR Queue Watchdog - outbox (2 узла)

**Триггер:** Schedule (каждые 10 минут)

**Функции:**
- Сброс зависящих записей (sending → pending)

### 2.4 База данных

#### Таблицы (11)

1. **intake_events** — входящие события из Telegram
   - `id` (UUID, PK)
   - `execution_id` (TEXT, UNIQUE)
   - `source` (TEXT)
   - `input_type` (TEXT)
   - `external_message_id` (TEXT)
   - `telegram_chat_id` (BIGINT)
   - `telegram_user_id` (BIGINT)
   - `email_from` (TEXT)
   - `email_subject` (TEXT)
   - `received_at` (TIMESTAMPTZ)
   - `raw_payload` (JSONB)
   - `status` (TEXT)
   - `event_type` (TEXT)
   - `created_at` (TIMESTAMPTZ)

2. **candidate_inputs** — нормализованные входные данные
   - `id` (UUID, PK)
   - `intake_event_id` (UUID, FK)
   - `execution_id` (TEXT)
   - `source` (TEXT)
   - `input_type` (TEXT)
   - `original_text` (TEXT)
   - `normalized_text` (TEXT)
   - `file_name` (TEXT)
   - `file_mime_type` (TEXT)
   - `file_hash` (TEXT)
   - `processing_status` (TEXT)
   - `created_at` (TIMESTAMPTZ)

3. **candidates** — карточки кандидатов
   - `id` (UUID, PK)
   - `full_name` (TEXT)
   - `city` (TEXT)
   - `desired_position` (TEXT)
   - `experience_years` (NUMERIC)
   - `skills` (TEXT[])
   - `salary_expectation` (NUMERIC)
   - `candidate_summary` (TEXT)
   - `source_input_id` (UUID, FK)
   - `data_quality_status` (TEXT)
   - `created_at` (TIMESTAMPTZ)
   - `updated_at` (TIMESTAMPTZ)

4. **candidate_contacts** — контакты кандидатов
   - `id` (UUID, PK)
   - `candidate_id` (UUID, FK)
   - `contact_type` (TEXT)
   - `contact_value` (TEXT)
   - `normalized_value` (TEXT)
   - `is_primary` (BOOLEAN)
   - `created_at` (TIMESTAMPTZ)

5. **vacancies** — вакансии
   - `id` (UUID, PK)
   - `title` (TEXT)
   - `description` (TEXT)
   - `requirements` (TEXT)
   - `salary_min` (NUMERIC)
   - `salary_max` (NUMERIC)
   - `status` (TEXT)
   - `created_at` (TIMESTAMPTZ)
   - `updated_at` (TIMESTAMPTZ)

6. **matches** — результаты matching
   - `id` (UUID, PK)
   - `candidate_id` (UUID, FK)
   - `vacancy_id` (UUID, FK)
   - `score` (NUMERIC, CHECK >= 0 AND <= 100)
   - `decision` (TEXT, CHECK IN ('match', 'no_match'))
   - `reason` (TEXT)
   - `raw_llm_response` (JSONB)
   - `created_at` (TIMESTAMPTZ)

7. **final_decisions** — итоговые решения
   - `id` (UUID, PK)
   - `candidate_id` (UUID, FK)
   - `best_match_id` (UUID, FK)
   - `has_match` (BOOLEAN)
   - `decision_status` (TEXT)
   - `decision_reason` (TEXT)
   - `created_at` (TIMESTAMPTZ)

8. **outbox** — исходящие сообщения
   - `id` (UUID, PK)
   - `intake_event_id` (UUID, FK)
   - `candidate_id` (UUID, FK)
   - `channel` (TEXT)
   - `recipient` (TEXT)
   - `message_type` (TEXT)
   - `subject` (TEXT)
   - `body` (TEXT)
   - `reply_markup` (JSONB)
   - `metadata` (JSONB) **← КРИТИЧЕСКОЕ ПОЛЕ**
   - `error_text` (TEXT)
   - `status` (TEXT)
   - `sent_at` (TIMESTAMPTZ)
   - `created_at` (TIMESTAMPTZ)

9. **processing_logs** — журнал обработки
   - `id` (UUID, PK)
   - `execution_id` (TEXT)
   - `intake_event_id` (UUID, FK)
   - `stage` (TEXT)
   - `status` (TEXT)
   - `details` (TEXT)
   - `error_text` (TEXT)
   - `attempt` (INTEGER)
   - `created_at` (TIMESTAMPTZ)

10. **generated_assets** — сгенерированные материалы
    - `id` (UUID, PK)
    - `candidate_id` (UUID, FK)
    - `asset_type` (TEXT)
    - `prompt` (TEXT)
    - `provider` (TEXT)
    - `asset_url` (TEXT)
    - `file_path` (TEXT)
    - `status` (TEXT)
    - `created_at` (TIMESTAMPTZ)

11. **bot_credentials** — учетные данные ботов
    - `bot_code` (TEXT, PK)
    - `bot_token` (TEXT)
    - `description` (TEXT)
    - `created_at` (TIMESTAMPTZ)

#### Функции

- `log_processing_event()` — логирование событий обработки

#### Индексы

- `idx_intake_events_execution_id`
- `idx_intake_events_telegram`
- `idx_candidate_inputs_execution_id`
- `idx_candidate_inputs_file_hash`
- `idx_candidate_contacts_normalized`
- `idx_vacancies_status`
- `idx_matches_candidate_score`
- `idx_processing_logs_execution_id`
- `idx_outbox_status`
- `uq_intake_telegram_message`
- `uq_candidate_contacts_normalized`

### 2.5 Интеграции

#### Telegram Bot API

**Тип:** Webhook

**Поддерживаемые типы сообщений:**
- `message` (text, voice, document, photo)
- `callback_query` (inline keyboard)

**Отправка:**
- `sendMessage` (текст)
- `sendVoice` (голосовые сообщения)
- `sendPhoto` (изображения)
- `sendVideo` (видео)

#### OpenAI API

**Используемые модели:**

1. **GPT-4o-mini**
   - Извлечение данных кандидата из текста резюме
   - Температура: 0
   - Response format: JSON Schema

2. **GPT-4**
   - Matching кандидата с вакансиями
   - Анализ соответствия

3. **GPT-image-1**
   - Генерация визуальных материалов (инфографика)
   - Размер: 1024x1024

4. **Sora-2**
   - Генерация видео
   - Размер: 720x1280 (vertical)
   - Длительность: 4 секунды

5. **TTS**
   - Генерация голосовых сообщений
   - Язык: русский

---

## 3. Функциональные требования

### 3.1 Обработка входящих сообщений

**FR-001:** Система должна принимать сообщения из Telegram в форматах:
- Текст
- Голосовое сообщение
- Документ (PDF, DOCX)
- Изображение (фото резюме)

**FR-002:** Система должна классифицировать входящие сообщения по типу:
- text, voice, document, image, callback

**FR-003:** Система должна сохранять все входящие события в `intake_events` с полным логированием.

**FR-004:** Система должна создавать записи в `candidate_inputs` для обработки.

### 3.2 Извлечение данных

**FR-005:** Система должна извлекать структурированные данные кандидата:
- ФИО (full_name)
- Город (city)
- Желаемая должность (desired_position)
- Опыт в годах (experience_years)
- Навыки (skills, массив)
- Зарплатные ожидания (salary_expectation)
- Email
- Телефон (phone)
- Краткое описание (summary)

**FR-006:** Система должна валидировать JSON-структуру ответа LLM.

**FR-007:** Система должна пытаться восстановить невалидный JSON (repair).

**FR-008:** Система должна использовать fallback при невозможности извлечь данные.

### 3.3 Matching кандидатов

**FR-009:** Система должна сравнивать профиль кандидата с открытыми вакансиями.

**FR-010:** Система должна формировать scoring (score 0-100).

**FR-011:** Система должна формировать decision ('match' или 'no_match').

**FR-012:** Система должна сохранять reason (обоснование решения).

### 3.4 Формирование ответа

**FR-013:** Система должна формировать ответное сообщение в Telegram.

**FR-014:** Система должна поддерживать inline keyboard (кнопки).

**FR-015:** Система должна генерировать TTS при наличии `metadata.tts_required`.

**FR-016:** Система должна генерировать визуальные материалы при наличии `metadata.visual_required`.

### 3.5 Отправка ответа

**FR-017:** Система должна отправлять сообщения через Telegram Bot API.

**FR-018:** Система должна обрабатывать ошибки отправки.

**FR-019:** Система должна логировать все этапы обработки.

---

## 4. Нефункциональные требования

### 4.1 Производительность

**NFR-001:** Время ответа на текстовое сообщение: < 30 секунд (включая LLM inference).

**NFR-002:** Время ответа с TTS: < 60 секунд.

**NFR-003:** Время ответа с визуалами: < 90 секунд.

**NFR-004:** Время ответа с видео: < 180 секунд.

### 4.2 Надежность

**NFR-005:** Retry механизм для внешних API (3 попытки с интервалом 5 секунд).

**NFR-006:** Watchdog для зависших записей (каждые 5-10 минут).

**NFR-007:** Логирование всех этапов обработки в `processing_logs`.

### 4.3 Безопасность

**NFR-008:** Хранение credentials в таблице `bot_credentials` (⚠️ Требуется улучшение — вынести в env).

**NFR-009:** Уникальные индексы для предотвращения дублирования сообщений.

### 4.4 Масштабируемость

**NFR-010:** Горизонтальное масштабирование через queue-based архитектуру.

**NFR-011:** Возможность добавления новых каналов (email, web-form).

---

## 5. Ограничения и допущения

### 5.1 Технические ограничения

1. **OpenAI API Rate Limits** — зависит от лимитов OpenAI
2. **Telegram Bot API Limits** — зависит от лимитов Telegram
3. **PostgreSQL Single Instance** — текущая конфигурация не масштабируется горизонтально

### 5.2 Функциональные ограничения

1. **Один язык** — система работает только с русским языком
2. **Нет аутентификации** — любой пользователь Telegram может использовать бота
3. **Нет персистентности сессий** — каждый запрос обрабатывается независимо

### 5.3 Допущения

1. Пользователи отправляют корректные резюме (не спам)
2. OpenAI API доступен и стабилен
3. Telegram Bot API доступен и стабилен

---

## 6. Известные проблемы

### 6.1 Критические

#### KP-001: НЕСОВМЕСТИМОСТЬ metadata

**Описание:** Поле `metadata` в таблице `outbox` существует и используется в Delivery Worker, но не заполняется в Processing Worker.

**Влияние:** TTS и visual generation используют fallback-значения вместо реальных данных.

**Статус:** Открыто.

**Решение:** Добавить заполнение metadata в Processing Worker INSERT запросы.

### 6.2 Средние

#### KP-002: ЗАХАРДКОЖЕННЫЕ CREDENTIALS

**Описание:** Bot token в SQL-файле (строка 288-294).

**Влияние:** Риск утечки credentials при публикации.

**Статус:** Открыто.

**Решение:** Перенести в environment variables.

---

## 7. Glossary

| Термин | Определение |
|--------|-------------|
| **Intake** | Прием входящего сообщения |
| **Matching** | Сравнение профиля кандидата с вакансией |
| **Outbox** | Исходящая очередь сообщений |
| **Watchdog** | Фоновый процесс для сброса зависших записей |
| **TTS** | Text-to-Speech, генерация голосовых сообщений |
| **Inline Keyboard** | Интерактивные кнопки в Telegram |
| **Webhook** | Механизм доставки событий от Telegram к n8n |

---

## 8. References

- [OpenAI API Documentation](https://platform.openai.com/docs)
- [Telegram Bot API Documentation](https://core.telegram.org/bots/api)
- [n8n Documentation](https://docs.n8n.io)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)