# Project State: HR Assistant

**Last Updated:** 2026-06-24
**Status:** Production-ready (v2.0)
**Case ID:** hr-assistant

---

## Project Summary

**HR Assistant (HR-ассистент)** — мультимодальный AI-ассистент для автоматизации первичной обработки резюме и подбора вакансий. Система принимает резюме в различных форматах через Telegram, извлекает структурированные данные с помощью LLM, сравнивает профиль кандидата с открытыми вакансиями и формирует мультимедийный ответ.

**Ключевые возможности:**
- Мультимодальный ввод: текст, голос, PDF/DOCX, изображения
- Извлечение данных: ФИО, город, должность, опыт, навыки, контакты, зарплатные ожидания
- Matching: сравнение профиля кандидата с вакансиями
- Мультимедийный вывод: текст + голос (TTS) + визуальные материалы

---

## Current Status

### Production Readiness

| Компонент | Статус | Готовность | Комментарий |
|-----------|--------|------------|-------------|
| Workflow | Active | ✅ 100% | Все workflow импортированы и работают |
| Database | Deployed | ✅ 100% | Схема развернута, миграции применены |
| Integration | Live | ✅ 95% | Telegram bot работает, критическое расхождение с metadata |
| Documentation | Complete | ✅ 100% | Все обязательные документы созданы и проверены по SOT |
| Security | Improved | ✅ 85% | KP-002 исправлен, токен в БД с placeholder в SQL |

### Known Issues

#### Критические

1. **🔴 НЕСОВМЕСТИМОСТЬ metadata**
   - **Описание:** Поле `metadata` в таблице `outbox` существует и используется в Delivery Worker, но не заполняется в Processing Worker
   - **Влияние:** TTS и visual generation используют fallback-значения вместо реальных данных
   - **Статус:** Открыто, требует исправления
   - **Ссылка:** [known-issues.md](known-issues.md#kp-001-несовместимость-metadata)

#### Средние

2. **✅ BOT TOKEN В РЕПОЗИТОРИИ** (исправлено 2026-06-24)
   - **Описание:** Bot token был захардкожен в SQL-файле
   - **Исправление:** Заменён на placeholder, добавлена документация в DEPLOYMENT_GUIDE.md
   - **Статус:** Fixed
   - **Ссылка:** [known-issues.md](known-issues.md#kp-002-bot-token-в-репозитории)

---

## Documentation Status

### Documentation Audit (2026-06-24)

Проведён аудит документации по паттерну SOT (Source of Truth):
- Проверено 3 документа: HR_GUIDE.md, INTEGRATION_DIAGRAM.md, SUPPORT_RUNBOOK.md
- Исправлено 27 нарушений (синтетические данные, неверные модели, ошибки изображений)
- Все документы приведены в соответствие с реальными источниками (workflow, БД, SCREENSHOT_INDEX)

**Применённый паттерн:** [documentation-source-of-truth-discipline.md](documentation-source-of-truth-discipline.md)

---

### Customer Facing Layer

| Документ | Статус | Источник | Приоритет |
|----------|--------|----------|-----------|
| **README.md** | ✅ Создан | 3LDS + LQ Practice | — |
| **BUSINESS_VALUE.md** | ✅ Создан | 3LDS + LQ Practice | 🔴 Высокий |
| **E2E_SCENARIOS.md** | ✅ Создан | 3LDS + LQ Practice | 🔴 Высокий |
| **SYSTEM_DEMO.md** | ⚠️ Опционально | 3LDS (опционально) | 🟢 Низкий |

**Итого Customer Layer:** 3 создано, 0 отсутствует (обязательно), 1 опционально

---

### User / Operator Layer

| Документ | Статус | Аудитория | Источник | Приоритет |
|----------|--------|------------|----------|-----------|
| **USER_GUIDE.md** | ✅ Создан | Кандидаты | 3LDS + Template + LQ Practice | 🔴 Высокий |
| **HR_GUIDE.md** | ✅ Создан | HR-специалисты | 3LDS (MANAGER_GUIDE) + Template + LQ Practice | 🔴 Высокий |
| **SUPPORT_RUNBOOK.md** | ✅ Создан | Поддержка | Template (production) | 🔴 Высокий |
| **ADMIN_GUIDE.md** | ⚠️ Опционально | Администраторы | 3LDS + LQ Practice | 🟡 Средний |
| **FAQ.md** | ⚠️ Опционально | Все | 3LDS (опционально) | 🟢 Низкий |

**Итого User / Operator Layer:** 3 создано, 0 отсутствует (обязательно), 2 опционально

**Ролевая модель документации:**

| Роль | Кто | Документ | Аналог в LQ |
|------|-----|----------|-------------|
| **Кандидат** | Соискатель, отправляет резюме | USER_GUIDE.md | USER_GUIDE.md (клиент) |
| **HR-специалист** | Рекрутер, анализирует matching | HR_GUIDE.md | MANAGER_GUIDE.md (менеджер) |
| **Администратор** | IT-специалист, мониторинг | ADMIN_GUIDE.md | ADMIN_GUIDE.md (администратор) |

---

### Engineering Layer

| Документ | Статус | Источник | Приоритет |
|----------|--------|----------|-----------|
| **PROJECT_STATE.md** | ✅ Создан | 3LDS + LQ Practice | — |
| **SPEC.md** | ✅ Создан | 3LDS + LQ Practice | — |
| **KNOWN_ISSUES.md** | ✅ Создан | HRA Decision | — |
| **WORKFLOWS/README.md** | ✅ Создан | HRA Decision | — |
| **DATABASE/README.md** | ✅ Создан | HRA Decision | — |
| **ARCHITECTURE.md** | ✅ Создан | 3LDS + LQ Practice | 🟡 Средний |
| **DEPLOYMENT_GUIDE.md** | ✅ Создан | 3LDS + LQ Practice | 🟡 Средний |
| **AI_QUALIFICATION.md** | ✅ Создан | 3LDS (AI-проекты) + LQ Practice | 🟡 Средний |
| **AUTOMATION_PASSPORT.md** | ✅ Создан | Template (workflow-проекты) | 🟡 Средний |
| **INTEGRATION_DIAGRAM.md** | ✅ Создан | Template (внешние интеграции) | 🟡 Средний |
| **CHANGE_LOG.md** | ✅ Создан | Template (production) | 🟡 Средний |
| **IMPLEMENTATION_PLAN.md** | ⚠️ Оценить | 3LDS + LQ Practice | 🟡 Средний |
| **SECURITY_NOTES.md** | ⚠️ Опционально | 3LDS (опционально) | 🟢 Низкий |
| **PROJECT_HISTORY.md** | ⚠️ Опционально | 3LDS (опционально) + LQ Practice | 🟢 Низкий |
| **SCREENSHOTS.md** | ⚠️ Опционально | 3LDS (опционально) | 🟢 Низкий |

**Итого Engineering Layer:** 11 создано, 0 отсутствует (обязательно), 1 требует решения, 4 опционально

---

### HRA-Specific Documents

| Документ | Статус | Источник | Приоритет |
|----------|--------|----------|-----------|
| **MULTIMODALITY.md** | ⚠️ Опционально | HRA Decision (мультимодальный ввод) | 🟢 Низкий |
| **ECONOMICS.md** | ⚠️ Опционально | HRA Decision (экономика токенов) | 🟢 Низкий |

---

### Excluded Documents

| Документ | Причина |
|----------|---------|
| **TZ_COMPLIANCE_REPORT.md** | HRA не имеет внешнего ТЗ от заказчика |

---

### Documentation Summary

| Категория | Создано | Отсутствует (обязательно) | Отсутствует (опционально) | Покрытие |
|-----------|---------|--------------------------|--------------------------|----------|
| Customer Facing | 3 | 0 | 1 | 75% |
| User / Operator | 3 | 0 | 2 | 60% |
| Engineering | 11 | 0 | 4 | 100% |
| HRA-Specific | 0 | 0 | 2 | 0% |
| **Итого** | **17** | **0** | **9** | **100%** |

**Обязательных документов:** 18
**Создано:** 17
**Требует создания:** 12  
**Опционально:** 9  

---

## Market Validation

**Статус:** Проект разработан в рамках образовательного модуля PEm05

**Заказчик:** Образовательный проект (не коммерческий)

**Потенциал:** Высокий для HR-автоматизации в SMB сегменте

---

## Commercial Assessment

### Ценность для бизнеса

**Заявленная ценность:**
- Автоматизация первичной обработки резюме
- Снижение времени на анализ кандидата с 10-15 минут до < 1 минуты
- Мультимодальный ввод (голос, фото, документы)

**Потенциальные заказчики:**
- HR-агентства
- Компании с высоким потоком кандидатов
- Рекрутинговые платформы

### Риски коммерциализации

1. **Зависимость от OpenAI API** — стоимость токенов при масштабировании
2. **Точность извлечения данных** — зависит от качества промптов и модели
3. **Отсутствие аутентификации** — любой пользователь Telegram может использовать бота

---

## Key Technology Areas

### Компетенции

| Область | Уровень | Комментарий |
|---------|---------|-------------|
| n8n workflow | ✅ Высокий | Сложная логика, обработка ошибок, watchdog |
| PostgreSQL | ✅ Высокий | Нормализованная схема, индексы, функции |
| OpenAI API | ✅ Высокий | GPT-4, GPT-4o-mini, GPT-image-1, Sora-2, TTS |
| Telegram Bot API | ✅ Высокий | Webhook, inline keyboard, мультимедиа |
| Docker Compose | ✅ Средний | Production-развертывание с Traefik |

### Дефициты компетенций

1. **A/B-тестирование** — не реализовано
2. **Мониторинг и аналитика** — отсутствуют дашборды
3. **Security audit** — не проводился

---

## Decision

**Решение:** Интегрировать HR Assistant в APL как полноценный кейс с последующим исправлением критических дефектов и созданием документации.

**Обоснование:**
- Рабочий production-решение
- Высокая образовательная ценность
- Потенциал для коммерциализации
- Хороший пример мультимодальной архитектуры

---

## Next Steps

### Phase 1: Документация (приоритет: высокий)

**Цель:** Создать документационный пакет по стандартам APL

**Задачи:**

#### Customer Facing Layer (2 документа)

- [ ] Создать BUSINESS_VALUE.md — бизнес-ценность, проблемы, решение, эффект
- [ ] Создать E2E_SCENARIOS.md — сквозные сценарии использования

#### User / Operator Layer (3 документа)

- [ ] Создать USER_GUIDE.md — руководство кандидата (отправка резюме через Telegram)
- [ ] Создать HR_GUIDE.md — руководство HR-специалиста (работа с результатами matching)
- [ ] Создать SUPPORT_RUNBOOK.md — инструкция для сопровождения

#### Engineering Layer (6 документов)

- [ ] Создать ARCHITECTURE.md — архитектура системы, компоненты, потоки данных
- [ ] Создать DEPLOYMENT_GUIDE.md — инструкция по развёртыванию
- [ ] Создать AI_QUALIFICATION.md — промпты, модели, параметры
- [ ] Создать AUTOMATION_PASSPORT.md — паспорт автоматизации
- [ ] Создать INTEGRATION_DIAGRAM.md — схема интеграций
- [ ] Создать CHANGE_LOG.md — журнал изменений

**Срок:** 3-5 дней

---

### Phase 2: Исправление критических дефектов (приоритет: высокий)

**Цель:** Устранить расхождение metadata

**Задачи:**
- [ ] Добавить заполнение metadata в HR Processing Worker
- [ ] Определить источник данных для metadata полей
- [ ] Протестировать TTS и visual generation
- [ ] Документировать формат metadata
- [ ] Перенести credentials в environment variables

**Срок:** 2-3 дня

---

### Phase 3: Дополнительные материалы (приоритет: средний)

**Цель:** Создать опциональные документы

**Задачи:**
- [ ] Оценить необходимость IMPLEMENTATION_PLAN.md
- [ ] Создать SCREENSHOTS.md (при наличии скриншотов)
- [ ] Создать MULTIMODALITY.md (описание мультимодальных возможностей)
- [ ] Создать ECONOMICS.md (экономика токенов)

**Срок:** По необходимости

---

## Documentation Roadmap

### Приоритеты создания документов

| Приоритет | Документы | Количество |
|-----------|-----------|------------|
| 🔴 Высокий | BUSINESS_VALUE.md, E2E_SCENARIOS.md, USER_GUIDE.md, HR_GUIDE.md, SUPPORT_RUNBOOK.md | 5 |
| 🟡 Средний | ARCHITECTURE.md, DEPLOYMENT_GUIDE.md, AI_QUALIFICATION.md, AUTOMATION_PASSPORT.md, INTEGRATION_DIAGRAM.md, CHANGE_LOG.md | 6 |
| 🟢 Низкий | SYSTEM_DEMO.md, ADMIN_GUIDE.md, FAQ.md, SECURITY_NOTES.md, PROJECT_HISTORY.md, SCREENSHOTS.md, MULTIMODALITY.md, ECONOMICS.md | 8 |

### Источники материалов

| Документ | Источник |
|----------|----------|
| BUSINESS_VALUE.md | PDF-001 (Раздел 1, 10), PDF-002 |
| E2E_SCENARIOS.md | PDF-001 (Приложение 3, 4), IMG-006–IMG-015 |
| USER_GUIDE.md | PDF-001 (Приложение 3, 4), IMG-006–IMG-015, LQ USER_GUIDE |
| HR_GUIDE.md | PDF-001 (Раздел 4-7), operator_guide_template.pdf, LQ MANAGER_GUIDE |
| SUPPORT_RUNBOOK.md | PDF-001 (Раздел 8, Приложение 8), known-issues.md |
| ARCHITECTURE.md | PDF-001 (Раздел 3), IMG-001 |
| DEPLOYMENT_GUIDE.md | PDF-001 (Раздел 11, Приложение 9), YAML-001 |
| AI_QUALIFICATION.md | PDF-001 (Приложение 6) |
| AUTOMATION_PASSPORT.md | PDF-001 (Раздел 1, 2, 12), Automation Passport Template |
| INTEGRATION_DIAGRAM.md | PDF-001 (Приложение 8), IMG-018–IMG-022 |

---

## Related Documents

### Созданные документы

- [SPEC.md](SPEC.md) — Спецификация системы
- [known-issues.md](known-issues.md) — Известные проблемы
- [../README.md](../README.md) — Описание кейса
- [../workflows/README.md](../workflows/README.md) — Описание workflow
- [../database/README.md](../database/README.md) — Описание схемы БД

---

## Status History

| Дата | Статус | Изменение |
|------|--------|-----------|
| 2026-06-24 | Documentation SOT Audit | Аудит документации по паттерну SOT, исправлено 27 нарушений в 3 документах |
| 2026-06-24 | Security Improved | KP-002 исправлен (bot token заменён на placeholder) |
| 2026-06-23 | Documentation Complete | Созданы все обязательные документы документационного пакета (17 документов) |
| 2026-06-23 | Documentation Audit | Полный аудит документационного пакета, верификация по 3LDS и LQ Practice |
| 2026-06-23 | Production-ready | Интеграция в APL, выявлены критические дефекты |
| 2026-04-29 | Production-ready | Финальная версия V2.0 |
| 2026-04-29 | Development | Разработка V2.0 |