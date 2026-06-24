# Руководство по развёртыванию HR Assistant

Документ описывает процесс развёртывания HR Assistant в production-окружении.

---

## Предварительные требования

### Программное обеспечение

| Компонент | Версия | Назначение |
|-----------|--------|-----------|
| **Docker** | 20.10+ | Контейнеризация |
| **Docker Compose** | 2.0+ | Оркестрация контейнеров |
| **PostgreSQL** | 14+ | База данных |
| **n8n** | 1.0+ | Workflow automation |

### Внешние сервисы

| Сервис | Назначение | Требования |
|--------|-----------|------------|
| **Telegram Bot API** | Входной канал | Bot token |
| **OpenAI API** | AI-модели | API key |

### Ресурсы

**Минимальные:**
- CPU: 2 cores
- RAM: 4 GB
- Disk: 20 GB

**Рекомендуемые:**
- CPU: 4 cores
- RAM: 8 GB
- Disk: 50 GB

---

## Шаг 1: Подготовка окружения

### 1.1. Установка Docker

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y docker.io docker-compose-plugin

# Добавление пользователя в группу docker
sudo usermod -aG docker $USER
newgrp docker

# Проверка установки
docker --version
docker compose version
```

---

### 1.2. Создание директории проекта

```bash
mkdir -p /opt/hr-assistant
cd /opt/hr-assistant

mkdir -p {database,workflows,logs,backups}
```

---

### 1.3. Настройка окружения

#### Вариант A: Быстрый старт (для тестирования)

Используйте значения из `.env.example`:
```bash
cp .env.example .env
```

Отредактируйте `.env`:
- Измените пароли на надёжные
- Укажите ваш домен
- Сгенерируйте encryption key

**Важно:** Для production-развёртывания обязательно используйте надёжные пароли!

#### Вариант B: Production-развёртывание

1. Скопируйте `.env.example` в `.env`:
   ```bash
   cp .env.example .env
   ```

2. Отредактируйте `.env`:
   ```env
   POSTGRES_DB=hr_assistant
   POSTGRES_USER=hr_user
   POSTGRES_PASSWORD=YOUR_SECURE_PASSWORD

   N8N_HOST=your-domain.com
   WEBHOOK_URL=https://your-domain.com/
   N8N_ENCRYPTION_KEY=YOUR_ENCRYPTION_KEY
   ```

3. Docker Compose автоматически подставит значения из `.env`.

**Важно:** Telegram Bot Token и OpenAI API Key настраиваются в n8n credential store, НЕ в `.env`. См. Шаг 5.

---

## Шаг 2: Развёртывание PostgreSQL

### 2.1. Docker Compose для PostgreSQL

**Вариант A: Использование готового docker-compose.yml**

Проект уже содержит настроенный `config/docker-compose.yml`. См. Шаг 1.3.

**Вариант B: Отдельный PostgreSQL контейнер**

Создайте `docker-compose.db.yml`:

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:14
    container_name: hr-assistant-db
    restart: unless-stopped
    environment:
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: ${POSTGRES_DB}
    volumes:
      - ./database/data:/var/lib/postgresql/data
      - ./database/schema_hr_assistant.sql:/docker-entrypoint-initdb.d/01_schema.sql
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER:-hr_user}"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  postgres-data:
```

**Примечание:** Синтаксис `${VAR:-default}` использует значение из `.env` или default-значение, если переменная не определена.

---

### 2.2. Запуск PostgreSQL

```bash
# Запуск PostgreSQL (переменные из .env или defaults)
docker compose -f docker-compose.db.yml up -d

# Проверка статуса
docker compose -f docker-compose.db.yml ps

# Проверка логов
docker compose -f docker-compose.db.yml logs postgres
```

---

### 2.3. Инициализация схемы БД

```bash
# Подключение к БД
docker exec -it hr-assistant-db psql -U ${POSTGRES_USER} -d ${POSTGRES_DB}

# Проверка таблиц
\dt

# Выход
\q
```

**Ожидаемый результат:**
- Созданы все таблицы (intake_events, candidate_inputs, candidates, etc.)
- Созданы индексы
- Созданы функции
- Создана таблица `bot_credentials` с записью для `hr_assistant`

---

### 2.4. Настройка Telegram Bot Token

Таблица `bot_credentials` автоматически создаётся и заполняется при выполнении `schema_hr_assistant.sql`.

**Для смены токена:**

```sql
-- Подключение к БД
docker exec -it hr-assistant-db psql -U hr_user -d hr_assistant

-- Обновление токена
UPDATE bot_credentials
SET bot_token = 'YOUR_NEW_BOT_TOKEN'
WHERE bot_code = 'hr_assistant';
```

**Архитектура хранения токена:**

| Workflow | Источник токена |
|----------|----------------|
| HR Intake | n8n credential "Pem05" |
| HR Processing Worker | Не использует Telegram |
| HR Delivery Worker | `bot_credentials` таблица |
| HR Generate Video | n8n credential "Pem05" |
| Error Handler | n8n credential "Pem05" |

**Почему Delivery Worker использует БД:**
- Позволяет менять токен без перезапуска n8n
- Упрощает ротацию токенов
- Не требует обновления n8n credentials

---

## Шаг 3: Развёртывание n8n

### 3.1. Docker Compose для n8n

Создайте `docker-compose.n8n.yml`:

```yaml
version: '3.8'

services:
  n8n:
    image: n8nio/n8n:latest
    container_name: hr-assistant-n8n
    restart: unless-stopped
    environment:
      - DB_TYPE=postgresdb
      - DB_POSTGRESDB_HOST=postgres
      - DB_POSTGRESDB_PORT=5432
      - DB_POSTGRESDB_DATABASE=${POSTGRES_DB}
      - DB_POSTGRESDB_USER=${POSTGRES_USER}
      - DB_POSTGRESDB_PASSWORD=${POSTGRES_PASSWORD}
      - N8N_ENCRYPTION_KEY=${N8N_ENCRYPTION_KEY}
      - WEBHOOK_URL=${WEBHOOK_URL}
      - N8N_HOST=${N8N_HOST}
      - N8N_PORT=${N8N_PORT}
      - N8N_PROTOCOL=${N8N_PROTOCOL}
    ports:
      - "5678:5678"
    volumes:
      - ./workflows:/home/node/.n8n
    depends_on:
      - postgres
    command: n8n start

volumes:
  n8n-data:
```

---

### 3.2. Запуск n8n

```bash
# Запуск n8n
docker compose -f docker-compose.n8n.yml up -d

# Проверка статуса
docker compose -f docker-compose.n8n.yml ps

# Проверка логов
docker compose -f docker-compose.n8n.yml logs n8n
```

---

### 3.3. Настройка n8n

**Веб-интерфейс:**
**Веб-интерфейс:**
1. Откройте `https://your-domain.com:5678`
2. Создайте аккаунт администратора
3. Перейдите к Шагу 5 для настройки credentials

---

## Шаг 4: Импорт Workflows

### 4.1. Экспорт workflows из проекта

Workflows находятся в `workflows/`:
- `hr_intake.json`
- `hr_processing_worker.json`
- `hr_delivery_worker.json`
- `hr_generate_video.json`
- `hr_queue_watchdog_candidate_inputs.json`
- `hr_queue_watchdog_outbox.json`

---

### 4.2. Импорт в n8n

**Вариант 1: Веб-интерфейс**

1. Откройте n8n
2. Перейдите в Workflows → Import from File
3. Выберите файл `hr_intake.json`
4. Повторите для всех workflows

**Вариант 2: CLI**

```bash
# Импорт всех workflows
for workflow in workflows/*.json; do
  docker exec -it hr-assistant-n8n n8n import:workflow --input=/home/node/.n8n/workflows/$(basename $workflow)
done
```

---

### 4.3. Активация Workflows

```bash
# Активация через API (пример)
curl -X POST http://localhost:5678/api/v1/workflows/1/activate \
  -H "Content-Type: application/json" \
  -H "X-N8N-API-KEY: your-api-key"
```

**Или через веб-интерфейс:**
1. Откройте каждый workflow
2. Нажмите "Activate" в правом верхнем углу

---

## Шаг 5: Настройка n8n Credentials

### 5.1. Обзор

HR Assistant использует n8n credential store для хранения credentials:

| Credential | Type | Usage |
|------------|------|-------|
| **PostgreSQL** | Postgres account | Все workflows (БД) |
| **OpenAI API** | Header Auth | Все AI-операции |
| **Telegram API** | Telegram API | HR Intake, HR Generate Video, Error Handler |

**Важно:** HR Delivery Worker использует `bot_credentials` таблицу (см. Шаг 2.3), не n8n Telegram credential.

---

### 5.2. Настройка PostgreSQL Credential

1. Откройте n8n → Settings → Credentials
2. Создайте новый credential:
   - **Type:** PostgreSQL
   - **Name:** `Postgres account` (или любое название)
   - **Host:** `postgres_hr` (или ваш хост)
   - **Port:** `5432`
   - **Database:** `hr_assistant`
   - **User:** `hr_user`
   - **Password:** (пароль из docker-compose.yml или .env)

3. Сохраните credential

**После импорта workflows:**
1. Откройте каждый workflow в n8n
2. Найдите PostgreSQL nodes
3. Выберите созданный credential из dropdown
4. Сохраните workflow

---

### 5.3. Настройка OpenAI API Credential

1. Откройте n8n → Settings → Credentials
2. Создайте новый credential:
   - **Type:** Header Auth
   - **Name:** `OpenAI API` (или любое название)
   - **Header Name:** `Authorization`
   - **Header Value:** `Bearer YOUR_OPENAI_API_KEY`

3. Сохраните credential

**После импорта workflows:**
1. Откройте каждый workflow с OpenAI nodes
2. Найдите HTTP Request nodes с OpenAI calls
3. Выберите созданный credential из dropdown
4. Сохраните workflow

---

### 5.4. Настройка Telegram API Credential

1. Откройте n8n → Settings → Credentials
2. Создайте новый credential:
   - **Type:** Telegram API
   - **Name:** Любое название (например, `HR Bot`)
   - **Bot Token:** `YOUR_TELEGRAM_BOT_TOKEN`

3. Сохраните credential

**После импорта workflows:**
1. Откройте HR Intake workflow
2. Найдите Telegram Trigger и Telegram API nodes
3. Выберите созданный credential из dropdown
4. Сохраните workflow
5. Повторите для HR Generate Video и Error Handler

---

### 5.5. Проверка Credentials

После настройки всех credentials:

1. Откройте любой workflow
2. Проверьте, что все nodes показывают зелёный статус credentials
3. Выполните тестовый запуск workflow
4. Проверьте подключение к БД, OpenAI API, Telegram API

---

## Шаг 6: Настройка Telegram Webhook

### 5.1. Получение URL Webhook

URL зависит от вашего домена:
```
https://your-domain.com/webhook/hr-assistant
```

---

### 6.1. Установка Webhook

Замените `YOUR_BOT_TOKEN` на токен вашего бота:

```bash
curl -X POST "https://api.telegram.org/botYOUR_BOT_TOKEN/setWebhook" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://your-domain.com/webhook/hr-assistant"}'
```

**Примечание:** Bot token хранится в:
- n8n credential "Pem05" — для HR Intake, HR Generate Video, Error Handler
- `bot_credentials` таблица — для HR Delivery Worker

**Ожидаемый ответ:**
```json
{
  "ok": true,
  "result": true,
  "description": "Webhook was set"
}
```

---

### 6.2. Проверка Webhook

```bash
curl -X GET "https://api.telegram.org/botYOUR_BOT_TOKEN/getWebhookInfo"
```

**Ожидаемый ответ:**
```json
{
  "ok": true,
  "result": {
    "url": "https://your-domain.com/webhook/hr-assistant",
    "has_custom_certificate": false,
    "pending_update_count": 0
  }
}
```

---

## Шаг 6: Настройка SSL (опционально)

### 6.1. Docker Compose с Traefik

Создайте `docker-compose.traefik.yml`:

```yaml
version: '3.8'

services:
  traefik:
    image: traefik:v2.10
    container_name: hr-assistant-traefik
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - ./traefik/traefik.yml:/etc/traefik/traefik.yml
      - ./traefik/acme.json:/acme.json
    environment:
      - TRAEFIK_EMAIL=${TRAEFIK_EMAIL}

  n8n:
    image: n8nio/n8n:latest
    container_name: hr-assistant-n8n
    restart: unless-stopped
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.n8n.rule=Host(`your-domain.com`)"
      - "traefik.http.routers.n8n.tls=true"
      - "traefik.http.routers.n8n.tls.certresolver=letsencrypt"
    environment:
      - DB_TYPE=postgresdb
      - DB_POSTGRESDB_HOST=postgres
      - DB_POSTGRESDB_PORT=5432
      - DB_POSTGRESDB_DATABASE=${POSTGRES_DB}
      - DB_POSTGRESDB_USER=${POSTGRES_USER}
      - DB_POSTGRESDB_PASSWORD=${POSTGRES_PASSWORD}
      - N8N_ENCRYPTION_KEY=${N8N_ENCRYPTION_KEY}
      - WEBHOOK_URL=https://your-domain.com
    depends_on:
      - postgres
      - traefik

  postgres:
    image: postgres:14
    container_name: hr-assistant-db
    restart: unless-stopped
    environment:
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: ${POSTGRES_DB}
    volumes:
      - ./database/data:/var/lib/postgresql/data
    labels:
      - "traefik.enable=false"
```

---

### 6.2. Конфигурация Traefik

Создайте `traefik/traefik.yml`:

```yaml
entryPoints:
  web:
    address: ":80"
    http:
      redirections:
        entryPoint:
          to: websecure
          scheme: https
  websecure:
    address: ":443"

certificatesResolvers:
  letsencrypt:
    acme:
      email: ${TRAEFIK_EMAIL}
      storage: acme.json
      httpChallenge:
        entryPoint: web

providers:
  docker:
    exposedByDefault: false
```

---

## Шаг 7: Загрузка вакансий

### 7.1. Добавление вакансий в БД

```sql
INSERT INTO vacancies (title, description, requirements, salary_min, salary_max, status)
VALUES
  ('Senior Frontend Developer', 'Разработка frontend-приложений на React', 'React, TypeScript, 5+ лет опыта', 180000, 250000, 'active'),
  ('UX Designer', 'Проектирование UX/UI интерфейсов', 'Figma, Sketch, 3+ года опыта', 120000, 180000, 'active'),
  ('Backend Developer', 'Разработка backend-сервисов на Java', 'Java, Spring Boot, 5+ лет опыта', 200000, 300000, 'active');
```

---

### 7.2. Проверка вакансий

```sql
SELECT id, title, status FROM vacancies WHERE status = 'active';
```

---

## Шаг 8: Тестирование

### 8.1. Тестирование Telegram Bot

```bash
# Отправка тестового сообщения в Telegram-бот
# Команда: /start
# Ожидаемый ответ: приветственное сообщение
```

---

### 8.2. Тестирование обработки резюме

```bash
# Отправка тестового резюме (текст)
# Ожидаемый результат:
# 1. Запись в intake_events
# 2. Запись в candidate_inputs (status='prepared')
# 3. Запись в candidates
# 4. Запись в matches
# 5. Запись в outbox
# 6. Ответ в Telegram
```

---

### 8.3. Проверка логов

```bash
# Логи n8n
docker compose -f docker-compose.n8n.yml logs n8n

# Логи PostgreSQL
docker compose -f docker-compose.db.yml logs postgres

# Логи обработки
SELECT * FROM processing_logs ORDER BY created_at DESC LIMIT 10;
```

---

## Шаг 9: Мониторинг

### 9.1. Healthcheck

```bash
# Проверка PostgreSQL
docker exec -it hr-assistant-db pg_isready -U ${POSTGRES_USER}

# Проверка n8n
curl -f http://localhost:5678/healthz || exit 1
```

---

### 9.2. Метрики

**SQL-запросы для мониторинга:**

```sql
-- Количество обработанных за час
SELECT COUNT(*) FROM final_decisions WHERE created_at > NOW() - INTERVAL '1 hour';

-- Ошибки за час
SELECT COUNT(*) FROM processing_logs WHERE status = 'error' AND created_at > NOW() - INTERVAL '1 hour';

-- Зависшие записи
SELECT
  (SELECT COUNT(*) FROM candidate_inputs WHERE processing_status = 'processing_started') as stuck_processing,
  (SELECT COUNT(*) FROM outbox WHERE status = 'sending') as stuck_sending;
```

---

## Шаг 10: Бэкапы

### 10.1. Бэкап PostgreSQL

```bash
# Создание бэкапа
docker exec hr-assistant-db pg_dump -U ${POSTGRES_USER} ${POSTGRES_DB} > backup_$(date +%Y%m%d).sql

# Восстановление
docker exec -i hr-assistant-db psql -U ${POSTGRES_USER} ${POSTGRES_DB} < backup_20260623.sql
```

---

### 10.2. Автоматические бэкапы

```bash
# Добавить в crontab
crontab -e

# Ежедневный бэкап в 2:00
0 2 * * * /opt/hr-assistant/scripts/backup.sh >> /var/log/hr-assistant/backup.log 2>&1
```

**Скрипт `scripts/backup.sh`:**

```bash
#!/bin/bash
source /opt/hr-assistant/.env

BACKUP_DIR="/opt/hr-assistant/backups"
DATE=$(date +%Y%m%d)

docker exec hr-assistant-db pg_dump -U ${POSTGRES_USER} ${POSTGRES_DB} > ${BACKUP_DIR}/backup_${DATE}.sql

# Удаление старых бэкапов (старше 7 дней)
find ${BACKUP_DIR} -name "backup_*.sql" -mtime +7 -delete
```

---

## Обновление

### Обновление Workflows

```bash
# Остановка n8n
docker compose -f docker-compose.n8n.yml stop

# Обновление файлов workflows
cp workflows/*.json /home/node/.n8n/workflows/

# Запуск n8n
docker compose -f docker-compose.n8n.yml start
```

---

### Обновление БД

```bash
# Применение миграций
docker exec -i hr-assistant-db psql -U ${POSTGRES_USER} ${POSTGRES_DB} < migrations/001_update_schema.sql
```

---

## Устранение неполадок

### Проблема: n8n не запускается

**Проверка:**
```bash
docker compose -f docker-compose.n8n.yml logs n8n
```

**Возможные причины:**
- Неверный DB_POSTGRESDB_PASSWORD
- PostgreSQL недоступен
- Неверный N8N_ENCRYPTION_KEY

---

### Проблема: Webhook не работает

**Проверка:**
```bash
# Замените YOUR_BOT_TOKEN на токен из bot_credentials или n8n credential
curl -X GET "https://api.telegram.org/botYOUR_BOT_TOKEN/getWebhookInfo"
```

**Возможные причины:**
- Неверный WEBHOOK_URL
- SSL сертификат недействителен
- n8n недоступен извне
- Bot token невалиден

---

### Проблема: OpenAI API ошибки

**Проверка:**
- Проверьте credential "OpenAI API" в n8n
- Проверьте баланс OpenAI
- Проверьте rate limits
- Проверьте правильность Authorization header (должен быть `Bearer YOUR_API_KEY`)

---

### Проблема: PostgreSQL недоступен

**Проверка:**
```bash
docker compose -f docker-compose.db.yml logs postgres
```

**Возможные причины:**
- Неверные credentials
- Порт 5432 занят
- Диск заполнен

---

## Связанные документы

- [ARCHITECTURE.md](ARCHITECTURE.md) — архитектура системы
- [SPEC.md](SPEC.md) — спецификация системы
- [SUPPORT_RUNBOOK.md](SUPPORT_RUNBOOK.md) — инструкция для поддержки
- [known-issues.md](known-issues.md) — известные проблемы

---

**Статус документа:** Production-ready
**Последнее обновление:** 2026-06-23