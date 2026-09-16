# 🛡️ SECURITY_NOTES — HR Assistant

**Назначение:** сводная модель безопасности системы — где хранятся secrets, что доступно извне, какие риски известны и какие меры применяются.

**Основной читатель:** инженер, сопровождающий систему; владелец, оценивающий риски перед передачей заказчику.

---

## 🧭 1. Куда смотреть по конкретным вопросам

| Вопрос | Документ |
|--------|----------|
| Как настроить credentials при развёртывании | [🚀 DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) |
| Как ротировать токен / реагировать на инцидент | [⚙️ SUPPORT_RUNBOOK.md](SUPPORT_RUNBOOK.md) |
| Реестр дефектов безопасности | [🛠️ known-issues.md](known-issues.md) |

---

## 🔐 2. Модель хранения secrets

| Secret | Хранение | Кто читает | Ротация |
|--------|----------|------------|---------|
| **PostgreSQL (логин/пароль)** | `.env` (вне репозитория) → переменные compose | Все workflows через n8n credential | Смена в `.env`, перезапуск stack |
| **OpenAI API Key** | n8n credential store | Все AI-операции (Processing Worker, Delivery Worker, Generate Video) | Смена credential в n8n UI |
| **Telegram Bot Token (Intake, Generate Video, Error Handler)** | n8n credential store | Соответствующие workflows | Смена credential в n8n UI |
| **Telegram Bot Token (Delivery Worker)** | Таблица `bot_credentials` (БД) | HR Delivery Worker (SQL) | `UPDATE bot_credentials SET bot_token = ...` без перезапуска n8n |
| **N8N_ENCRYPTION_KEY** | `.env` (вне репозитория) | n8n (шифрование credential store) | Смена только с осознанным решением — расшифровка credentials зависит от ключа |

**Правила:**

- Реальные secrets не коммитируются. В репозитории — только `.env.example` с placeholder-значениями.
- Bot token в SQL-файле схемы — placeholder `REPLACE_ME_WITH_YOUR_BOT_TOKEN` (исправление KP-002, 2026-06-24); реальный токен задаётся при развёртывании.
- Живые URL стендов (RunPod proxy, домены) в публичной документации не публикуются — используется placeholder-нотация.

---

## 🌐 3. Периметр доступа

| Компонент | Доступ извне | Комментарий |
|-----------|--------------|-------------|
| **Telegram Webhook** | ✅ Публичный HTTPS endpoint (`/webhook/hr-assistant`) | Единственная публичная точка входа; валидация payload на стороне n8n |
| **n8n Editor** | Закрыт доменной настройкой | Доступ только администратора |
| **PostgreSQL** | `127.0.0.1:5432` (bind localhost) | Порт не открыт наружу (см. `config/docker-compose.yml`) |
| **RunPod proxy (экспериментальный стенд)** | Доступен без аутентификации | Только тестовый workflow; production его не использует |

---

## 👤 4. Персональные данные

**Обрабатываются:** ФИО кандидатов, контакты (email, телефон), зарплатные ожидания, опыт, навыки.

**Меры:**
- Данные хранятся в PostgreSQL; доступ ограничен credentials
- Персональные данные не логируются в публичную документацию
- Демо-контур принимает только обезличенные данные (см. [🧭 DEMO_ROUTE.md](DEMO_ROUTE.md))

**⚠️ Открытые направления:**
- Шифрование чувствительных полей — не реализовано
- Политики хранения/удаления данных кандидатов (GDPR/ФЗ-152) — требуется проработка при коммерческой передаче

---

## 🚨 5. Известные проблемы безопасности

| ID | Проблема | Приоритет | Статус |
|----|---------|-----------|--------|
| KP-002 | Bot token в репозитории | ⚠️ Medium | ✅ Fixed (2026-06-24) — placeholder в SQL, документация обновления, токен в `bot_credentials` |

**Ссылка:** [known-issues.md#kp-002-bot-token-в-репозитории](known-issues.md#kp-002-bot-token-в-репозитории)

---

## 📋 6. Рекомендации при коммерческой передаче

1. Сменить все credentials (OpenAI, bot token, пароль БД, N8N_ENCRYPTION_KEY).
2. Удалить демо-данные из БД перед подключением заказчика.
3. Настроить rotation policy для bot token (см. архитектуру ротации в [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)).
4. Заполнить контактные роли в [AUTOMATION_PASSPORT.md](AUTOMATION_PASSPORT.md) и [SUPPORT_RUNBOOK.md](SUPPORT_RUNBOOK.md).

---

## 📚 7. Связанные документы

- [🪪 AUTOMATION_PASSPORT.md](AUTOMATION_PASSPORT.md) — паспорт автоматизации
- [🏗️ ARCHITECTURE.md](ARCHITECTURE.md) — архитектура (раздел «Безопасность»)
- [🚀 DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) — настройка credentials при развёртывании
- [⚙️ SUPPORT_RUNBOOK.md](SUPPORT_RUNBOOK.md) — инциденты и ротация токена
- [🛠️ known-issues.md](known-issues.md) — реестр дефектов

---

**Статус:** Рабочий документ модели безопасности
**Последнее обновление:** 2026-09-16**История изменений:** [📝 CHANGE_LOG.md](CHANGE_LOG.md#-4-история-изменений-документации)
