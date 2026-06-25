# Project Handoff Checklist: HR Assistant

**Чеклист для передачи проекта новому инженеру. Точка входа для первого знакомства с проектом.**

---

## Как использовать этот документ

Этот документ — навигационная карта с практическими действиями. Он содержит ссылки на существующую документацию и чеклисты для проверки.

**Порядок работы для нового инженера:**
1. Прочитайте раздел → Ознакомьтесь с документом
2. Выполните checklist → Проверьте понимание и компоненты
3. Переходите к следующему разделу

---

## 1. Project Overview

### Что это за проект

HR Assistant — мультимодальный AI-ассистент для автоматизации первичной обработки резюме и matching с вакансиями через Telegram-бот.

**Ключевые возможности:**
- Мультимодальный ввод: текст, голос, PDF/DOCX, изображения
- AI-извлечение данных: GPT-4o-mini (JSON Schema)
- Автоматический matching кандидатов с вакансиями
- Мультимедийный вывод: текст, голос (TTS), визуальные материалы

**Полное описание:** [README.md](../README.md)

**Ценность для бизнеса:** [BUSINESS_VALUE.md](BUSINESS_VALUE.md)

**Сквозные сценарии:** [E2E_SCENARIOS.md](E2E_SCENARIOS.md)

### Checklist

- [ ] Прочитать README.md для понимания архитектуры
- [ ] Прочитать BUSINESS_VALUE.md для понимания ценности
- [ ] Просмотреть E2E_SCENARIOS.md для понимания сценариев работы

---

## 2. Workflow Export

### Где находятся workflow

**Директория:** `workflows/`

**Файлы workflow:**

| Файл | Workflow | Назначение |
|------|----------|-----------|
| `HR Intake.json` | HR Intake | Приём входящих сообщений из Telegram |
| `HR Processing Worker.json` | HR Processing Worker | Извлечение данных и matching |
| `HR Delivery Worker.json` | HR Delivery Worker | Доставка ответов |
| `HR Generate Video.json` | HR Generate Video | Генерация видео (on-demand) |
| `HR Queue Watchdog - candidate_inputs.json` | Watchdog | Сброс зависших обработок |
| `HR Queue Watchdog - outbox.json` | Watchdog | Сброс зависших сообщений |

**Описание workflow:** [../workflows/README.md](../workflows/README.md)

**Архитектура workflow:** [ARCHITECTURE.md](ARCHITECTURE.md#компоненты-системы)

### Checklist

- [ ] Убедиться, что все файлы workflow присутствуют в `workflows/`
- [ ] Открыть ARCHITECTURE.md и понять потоки данных между workflow
- [ ] Проверить, что количество узлов в файлах соответствует документации

---

## 3. Variables

### Переменные окружения

**Файл:** `.env.example` (шаблон)

**Переменные:**

| Переменная | Назначение | Где используется |
|------------|-----------|------------------|
| `POSTGRES_DB` | Имя БД | PostgreSQL |
| `POSTGRES_USER` | Пользователь БД | PostgreSQL |
| `POSTGRES_PASSWORD` | Пароль БД | PostgreSQL |
| `N8N_HOST` | Хост n8n | n8n |
| `WEBHOOK_URL` | URL для webhooks | Telegram |
| `N8N_ENCRYPTION_KEY` | Ключ шифрования | n8n credentials |

**Настройка:** [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md#шаг-1-подготовка-окружения)

### Переменные в n8n workflow

Переменные определены в узлах workflow. См. файлы workflow в `workflows/`.

### Checklist

- [ ] Проверить наличие файла `.env.example`
- [ ] Создать `.env` из шаблона
- [ ] Заполнить все переменные окружения
- [ ] Убедиться, что `N8N_ENCRYPTION_KEY` сгенерирован

---

## 4. Credentials Inventory

### Обязательные credentials

| Credential | Тип | Где используется | Где настраивается |
|------------|-----|------------------|-------------------|
| **PostgreSQL** | Postgres account | Все workflow (БД) | n8n credential store |
| **OpenAI API** | Header Auth | Processing Worker, Delivery Worker, Generate Video | n8n credential store |
| **Telegram API** | Telegram API | HR Intake, HR Generate Video, Error Handler | n8n credential store |
| **Bot Token (DB)** | Токен в БД | HR Delivery Worker | Таблица `bot_credentials` |

**Архитектура хранения токена:**

HR Delivery Worker читает Telegram Bot Token из таблицы `bot_credentials`, что позволяет менять токен без перезапуска n8n. Остальные workflow используют n8n credential store.

**Настройка credentials:** [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md#шаг-5-настройка-n8n-credentials)

**Безопасность:** [ARCHITECTURE.md](ARCHITECTURE.md#безопасность)

### Checklist

- [ ] Создать credential PostgreSQL в n8n
- [ ] Создать credential OpenAI API в n8n
- [ ] Создать credential Telegram API в n8n
- [ ] Добавить Bot Token в таблицу `bot_credentials`
- [ ] Проверить подключение всех credentials

---

## 5. Prompt Engineering Guide

### Система промптов проекта

**Документ:** [PROMPT_ENGINEERING_GUIDE.md](PROMPT_ENGINEERING_GUIDE.md)

**Ключевые промпты:**

| Промпт | Workflow | Модель | Назначение |
|--------|----------|--------|-----------|
| Candidate Extraction | Processing Worker | gpt-4o-mini | Извлечение данных кандидата |
| JSON Repair | Processing Worker | gpt-4o-mini | Ремонт невалидного JSON |
| Matching | Processing Worker | gpt-4o-mini | Сравнение кандидата с вакансиями |
| Judge | Prompt Evaluation | gpt-4.1 | Эталонная оценка (только для экспериментов) |

**Подробнее о промптах:** [AI_QUALIFICATION.md](AI_QUALIFICATION.md)

**Экспериментальный контур:** [docs/prompt_evaluation/README.md](prompt_evaluation/README.md)

### Checklist

- [ ] Прочитать PROMPT_ENGINEERING_GUIDE.md для понимания системы промптов
- [ ] Ознакомиться с AI_QUALIFICATION.md для понимания деталей
- [ ] Понять, как безопасно изменять промпты (процесс A/B-тестирования)
- [ ] Убедиться, что не меняете production-промпты без эксперимента

---

## 6. Trigger URL / API Endpoints

### Telegram Webhook

**URL:** `https://your-domain.com/webhook/hr-assistant`

**Настройка:** [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md#шаг-6-настройка-telegram-webhook)

### n8n Webhooks

| Workflow | Webhook Path | Метод | Назначение |
|----------|-------------|-------|-----------|
| HR Intake | `/webhook/hr-assistant` | POST | Входящие сообщения Telegram |

### API Endpoints (внешние)

| API | Endpoint | Назначение |
|-----|----------|-----------|
| Telegram Bot API | `api.telegram.org` | Приём и отправка сообщений |
| OpenAI API | `api.openai.com` | GPT-4o-mini, TTS, генерация изображений |

**Подробнее:** [INTEGRATION_DIAGRAM.md](INTEGRATION_DIAGRAM.md)

### Checklist

- [ ] Настроить Telegram Webhook по инструкции
- [ ] Проверить, что webhook активен: `curl https://api.telegram.org/bot${TOKEN}/getWebhookInfo`
- [ ] Убедиться, что OpenAI API доступен: проверить статус status.openai.com

---

## 7. Success Metrics

### Бизнес-метрики

**Документ:** [SUCCESS_METRICS.md](SUCCESS_METRICS.md)

| Метрика | До | После | Источник |
|---------|----|----|----------|
| Время обработки резюме | 10-15 минут | < 1 минута | [BUSINESS_VALUE.md](BUSINESS_VALUE.md) |
| Форматы ввода | 1 | 4 | [BUSINESS_VALUE.md](BUSINESS_VALUE.md) |
| Извлечение данных | Вручную | Автоматически | [BUSINESS_VALUE.md](BUSINESS_VALUE.md) |

### Технические метрики

| Метрика | Целевое значение | Источник |
|---------|-----------------|----------|
| Среднее время ответа (текст) | < 30 сек | [AUTOMATION_PASSPORT.md](AUTOMATION_PASSPORT.md) |
| Среднее время ответа (голос) | < 60 сек | [AUTOMATION_PASSPORT.md](AUTOMATION_PASSPORT.md) |
| Доступность (SLA) | 99% | [AUTOMATION_PASSPORT.md](AUTOMATION_PASSPORT.md) |

### Checklist

- [ ] Ознакомиться с SUCCESS_METRICS.md
- [ ] Понять, какие метрики являются целевыми
- [ ] Понять, какие метрики требуют внимания
- [ ] Убедиться, что знаете, где смотреть метрики (SQL, логи)

---

## 8. Error SOP

### Типовые проблемы и решения

**Полный документ:** [SUPPORT_RUNBOOK.md](SUPPORT_RUNBOOK.md)

**Критические инциденты:**

| Инцидент | Симптомы | Решение | Ссылка |
|----------|----------|---------|--------|
| Обработка зависла | Записи в статусе `processing_started` > 5 минут | Сбросить статус или перезапустить Worker | [SUPPORT_RUNBOOK.md](SUPPORT_RUNBOOK.md#проблема-зависшие-записи) |
| Telegram Bot недоступен | Webhook не работает | Проверить и переустановить webhook | [SUPPORT_RUNBOOK.md](SUPPORT_RUNBOOK.md#инцидент-1-telegram-bot-недоступен) |
| OpenAI API недоступен | Ошибки извлечения данных | Проверить status.openai.com, ждать восстановления | [SUPPORT_RUNBOOK.md](SUPPORT_RUNBOOK.md#инцидент-2-openai-api-недоступен) |

**Известные проблемы:** [known-issues.md](known-issues.md)

### Checklist

- [ ] Прочитать SUPPORT_RUNBOOK.md полностью
- [ ] Понять типовые инциденты и их решения
- [ ] Ознакомиться с known-issues.md
- [ ] Убедиться, что знаете, как проверить статус компонентов

---

## 9. Step-by-Step Instructions

### Первый запуск

**Подробное руководство:** [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)

**Кратко:**

1. **Подготовка окружения**
   ```bash
   cp .env.example .env
   # Отредактируйте .env
   ```

2. **Запуск PostgreSQL**
   ```bash
   docker-compose -f config/docker-compose.yml up -d
   ```

3. **Инициализация БД**
   ```bash
   psql -U hr_user -d hr_assistant -f database/schema_hr_assistant.sql
   ```

4. **Настройка credentials в n8n**
   - PostgreSQL
   - OpenAI API
   - Telegram API

5. **Импорт workflow**
   - Импортировать все workflow из `workflows/`

6. **Настройка Telegram Webhook**
   ```bash
   curl -X POST "https://api.telegram.org/bot${TOKEN}/setWebhook" \
     -d '{"url": "https://your-domain.com/webhook/hr-assistant"}'
   ```

7. **Тестирование**
   - Отправить тестовое резюме через Telegram

### Диагностика

**SQL-запросы:** [SUPPORT_RUNBOOK.md](SUPPORT_RUNBOOK.md#диагностика)

### Checklist

- [ ] Выполнить все шаги из DEPLOYMENT_GUIDE.md
- [ ] Проверить работу всех workflow в n8n
- [ ] Отправить тестовое резюме через Telegram
- [ ] Проверить, что кандидат появился в БД
- [ ] Проверить, что matching выполнен
- [ ] Проверить, что ответ доставлен

---

## 10. Logs & Metrics Dashboard

### Где смотреть логи

**n8n логи:**
```bash
docker compose -f docker-compose.n8n.yml logs n8n
```

**PostgreSQL логи:**
```bash
docker compose -f docker-compose.db.yml logs postgres
```

**Таблица processing_logs:**
```sql
SELECT * FROM processing_logs ORDER BY created_at DESC LIMIT 10;
```

### Метрики

**SQL-запросы для мониторинга:** [SUPPORT_RUNBOOK.md](SUPPORT_RUNBOOK.md#sql-запросы-для-мониторинга)

**Ключевые метрики:**

| Метрика | SQL | Порог |
|---------|-----|-------|
| Обработанные за час | `SELECT COUNT(*) FROM final_decisions WHERE created_at > NOW() - INTERVAL '1 hour'` | — |
| Ошибки за час | `SELECT COUNT(*) FROM processing_logs WHERE status = 'error' AND created_at > NOW() - INTERVAL '1 hour'` | > 5% |
| Зависшие обработки | `SELECT COUNT(*) FROM candidate_inputs WHERE processing_status = 'processing_started'` | > 0 > 5 мин |

**Мониторинг:** [AUTOMATION_PASSPORT.md](AUTOMATION_PASSPORT.md#мониторинг-и-алертинг)

### Checklist

- [ ] Проверить, что логи n8n доступны
- [ ] Проверить, что логи PostgreSQL доступны
- [ ] Выполнить тестовый SQL-запрос к processing_logs
- [ ] Понять, где смотреть ключевые метрики

---

## 11. Emergency Procedures

### Критические ситуации

**Полный документ:** [SUPPORT_RUNBOOK.md](SUPPORT_RUNBOOK.md#порядок-действий-при-сбоях)

#### База данных недоступна

1. Проверить статус: `docker ps`
2. Проверить логи: `docker compose logs postgres`
3. Перезапустить: `docker compose restart postgres`
4. Проверить connection string

#### n8n завис

1. Проверить статус: `docker ps`
2. Проверить логи: `docker compose logs n8n`
3. Перезапустить: `docker compose restart n8n`

#### OpenAI API недоступен

1. Проверить https://status.openai.com
2. Ждать восстановления
3. Сообщить пользователям о задержке

#### Telegram Bot не отвечает

1. Проверить webhook: `curl https://api.telegram.org/bot${TOKEN}/getWebhookInfo`
2. Переустановить webhook
3. Проверить SSL сертификат

### Бэкапы

**Создание бэкапа:**
```bash
docker exec hr-assistant-db pg_dump -U hr_user hr_assistant > backup_$(date +%Y%m%d).sql
```

**Восстановление:**
```bash
docker exec -i hr-assistant-db psql -U hr_user hr_assistant < backup_20260623.sql
```

**Подробнее:** [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md#шаг-10-бэкапы)

### Checklist

- [ ] Создать бэкап БД до первого запуска
- [ ] Проверить, что знаете процедуру восстановления
- [ ] Понять, как диагностировать критические ситуации
- [ ] Убедиться, что знаете, где находятся команды для быстрого реагирования

---

## 12. SSOT Map

### Картина источников истины

**Architecture SSOT:** [ARCHITECTURE.md](ARCHITECTURE.md) — архитектура системы, компоненты, потоки данных

**Business Value SSOT:** [BUSINESS_VALUE.md](BUSINESS_VALUE.md) — ценность для бизнеса, измеримый эффект

**Deployment SSOT:** [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) — развёртывание, настройка, запуск

**AI Prompts SSOT:** [AI_QUALIFICATION.md](AI_QUALIFICATION.md) — промпты, модели, параметры

**Automation Passport SSOT:** [AUTOMATION_PASSPORT.md](AUTOMATION_PASSPORT.md) — TCO, метрики, инциденты

**Support SSOT:** [SUPPORT_RUNBOOK.md](SUPPORT_RUNBOOK.md) — диагностика, известные проблемы, процедуры

**Metrics SSOT:** [SUCCESS_METRICS.md](SUCCESS_METRICS.md) — все метрики проекта

**Prompt Evaluation SSOT:** [docs/prompt_evaluation/README.md](prompt_evaluation/README.md) — подсистема A/B-тестирования промптов

**Database SSOT:** [../database/README.md](../database/README.md) — схема БД

**Workflows SSOT:** [../workflows/README.md](../workflows/README.md) — описание workflow

### Известные ограничения

**KP-001: НЕСОВМЕСТИМОСТЬ metadata**

Поле `metadata` в таблице `outbox` не заполняется в Processing Worker, но используется в Delivery Worker.

**Влияние:** TTS и visual generation используют fallback-значения.

**Статус:** Открыто, требует исправления.

**Ссылка:** [known-issues.md](known-issues.md#kp-001-несовместимость-metadata)

### Checklist

- [ ] Понять, где находится каждый SSOT-документ
- [ ] Ознакомиться с известными ограничениями (KP-001)
- [ ] Запомнить структуру документации проекта

---

## 13. Roadmap

### Текущий статус

**Статус:** Production-ready (v2.0)

**Документ:** [PROJECT_STATE.md](PROJECT_STATE.md)

### Следующие шаги

**Phase 1: Исправление дефектов**
- [ ] Исправить KP-001 (metadata gap)
- [ ] Добавить заполнение metadata в Processing Worker

**Phase 2: Улучшения**
- [ ] Внедрить версионирование workflow
- [ ] Настроить мониторинг и алертинг
- [ ] Добавить дашборды

**Phase 3: Масштабирование**
- [ ] Горизонтальное масштабирование Processing Worker
- [ ] Кэширование matching
- [ ] Оптимизация токенов

**Полный roadmap:** [PROJECT_STATE.md](PROJECT_STATE.md#next-steps)

### Checklist

- [ ] Ознакомиться с текущим статусом проекта
- [ ] Понять приоритеты развития
- [ ] Убедиться, что знаете следующие шаги

---

## Quick Reference

### Команды для быстрого старта

```bash
# Запуск PostgreSQL
docker-compose -f config/docker-compose.yml up -d

# Проверка статуса
docker ps

# Логи n8n
docker compose logs n8n

# Проверка webhook
curl https://api.telegram.org/bot${TOKEN}/getWebhookInfo

# Бэкап БД
docker exec hr-assistant-db pg_dump -U hr_user hr_assistant > backup.sql

# Сброс зависших обработок
docker exec -it hr-assistant-db psql -U hr_user -d hr_assistant
UPDATE candidate_inputs SET processing_status = 'prepared'
WHERE processing_status = 'processing_started'
  AND created_at < NOW() - INTERVAL '5 minutes';
```

### Ключевые файлы

| Файл | Назначение |
|------|-----------|
| `workflows/HR Processing Worker.json` | Основной workflow с промптами |
| `database/schema_hr_assistant.sql` | Схема БД |
| `.env.example` | Шаблон переменных окружения |
| `config/docker-compose.yml` | Конфигурация Docker |

---

**Статус документа:** Production-ready
**Последнее обновление:** 2026-06-27