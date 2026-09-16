# 📝 CHANGE_LOG — HR Assistant

**Назначение:** журнал изменений системы. Фиксирует, что и когда менялось, и почему. Не является реестром открытых дефектов (см. [`known-issues.md`](known-issues.md)) и не содержит планов развития (см. [`PROJECT_STATE.md`](PROJECT_STATE.md)).

---

## 📋 1. Формат записи

| Поле | Значение |
|------|----------|
| Дата | Дата завершения изменения |
| Автор | Исполнитель |
| Тип | `FEAT` (новая функциональность) / `FIX` (исправление) / `DOCS` (документация) |
| Что изменено | Суть изменения |
| Причина | Зачем |
| Затронуто | Компоненты/документы |
| Статус | Выполнено / Отменено / Отложено |

Версии: SemVer (`MAJOR.MINOR.PATCH`). История версий ведётся сверху вниз — новые записи первыми.

---

## 🔄 2. Текущая версия

### [2.3.0] — 2026-09-01

| Дата | Автор | Тип | Что изменено | Причина | Затронуто | Статус |
|------|-------|-----|--------------|---------|-----------|--------|
| 2026-09-01 | Alexander Gulyaev | FIX | KP-001: все 5 INSERT в `outbox` в Processing Worker заполняют колонку `metadata`; Build TG response формирует контракт `tts_required`, `visual_required`, `visual_title`, `visual_score`, `visual_candidate_name`, `visual_vacancy_title`; Delivery Worker не менялся (контракт потребителя сверен) | Поле `metadata` не заполнялось, но использовалось Delivery Worker → TTS и visual generation работали через fallback | `HR Processing Worker.json`, `HR Processing Worker - Multi Provider Test.json`; контракт документирован в SPEC §3.4 | ✅ Выполнено |
| 2026-09-01 | Alexander Gulyaev | FIX | Формат metadata документирован в SPEC.md (раздел «Контракт metadata») | Зафиксировать потребительский контракт после KP-001 | SPEC.md | ✅ Выполнено |

### Документация — 2026-09-15

| Дата | Автор | Тип | Что изменено | Причина | Затронуто | Статус |
|------|-------|-----|--------------|---------|-----------|--------|
| 2026-09-16 | Alexander Gulyaev | DOCS | Из публичной документации убрано слово-штамп «ключевой» (33 формулировки: заголовки «Ключевые возможности/метрики/файлы» → «Возможности/Метрики/Основные файлы», обороты «Ключевой вывод/принцип» → «Вывод/Принцип», табличный заголовок «Ключевые поля» → «Основные поля»); «полноценный» → «самостоятельный» в PROJECT_STATE. Анкоры на «Ключевые метрики» PASSPORT обновлены (9 ссылок) | Штамп не зафиксирован ни в одном стандарте APL; решение владельца — убрать | 15 документов docs/, README.md | ✅ Выполнено |
| 2026-09-16 | Alexander Gulyaev | DOCS | AUTOMATION_PASSPORT §18: конкурирующая таблица версий (своя схема «2.0.1», обрыв на 2026-06-24) заменена ссылкой на единый журнал CHANGE_LOG; AI_QUALIFICATION §11: протокольный список правок сжат в однострочник по норме «дата + суть» | Устранение дублирования истории версий и её рассинхрона с CHANGE_LOG | AUTOMATION_PASSPORT.md, AI_QUALIFICATION.md | ✅ Выполнено |
| 2026-09-16 | Alexander Gulyaev | DOCS | Футеры SPEC и ARCHITECTURE: из статуса убрана версия продукта «(v2.3.0)» | Версия продукта живёт только в CHANGE_LOG; склейка статуса с версией — артефакт старой шапки | SPEC.md, ARCHITECTURE.md | ✅ Выполнено |
| 2026-09-16 | Alexander Gulyaev | DOCS | Оформление: H2 всех документов приведены к формату «эмодзи + номер + название» (сквозная нумерация); метаданные документа собраны в футер «Статус / Последнее обновление» (шапочные Version/Last Updated убраны); в ARCHITECTURE вводный текст перенесён под витринную дарк-картинку; обновлены анкорные ссылки на переименованные разделы | Единообразие оформления пакета (правило H2-формата из documentation-emoji-contract) | 21 документ docs/, README.md | ✅ Выполнено |
| 2026-09-15 | Alexander Gulyaev | DOCS | Ревизия публичной документации к стандарту APL: README переписан (entry point, витринный hero, Live Demo, трёхслойная карта документации); созданы PROJECT_STRUCTURE.md, MEDIA_INDEX.md, SECURITY_NOTES.md; SCREENSHOT_INDEX.md слит в MEDIA_INDEX.md; CHANGE_LOG переведён на табличный формат; статусы KP приведены к фактическим во всех документах; живые RunPod URL и credential id в доках заменены на placeholder | Документация рассинхронизирована с состоянием проекта (версии, статусы дефектов, имена workflow) | docs/, README.md | ✅ Выполнено |

---

## 📜 3. История версий

### [2.2.0] — 2026-06-28

| Дата | Автор | Тип | Что изменено | Причина | Затронуто | Статус |
|------|-------|-----|--------------|---------|-----------|--------|
| 2026-06-28 | Alexander Gulyaev | FEAT | Экспериментальный ML-контур: каталог `finetuning/`, Experiment 002, runtime API (`api/hra_qwen_api.py`, `hra_qwen_api_lora.py`) | Постоянное улучшение качества matching | finetuning/, api/ | ✅ Выполнено |
| 2026-06-28 | Alexander Gulyaev | FEAT | Введён формальный пайплайн экспериментального контура: Prompt Engineering → A/B Evaluation → Reference Dataset → Teacher Dataset → Fine-tuning (LoRA) → Offline Validation → Runtime Smoke Validation → Production Readiness | Формализация цикла улучшения | docs/ARCHITECTURE.md, EXPERIMENTAL_ML_PIPELINE.md | ✅ Выполнено |
| 2026-06-28 | Alexander Gulyaev | FEAT | Multi Provider Test workflow — инженерный стенд тестирования LLM-провайдеров (не production) | Тестирование альтернативных провайдеров без риска для production | workflows/ | ✅ Выполнено |
| 2026-06-28 | Alexander Gulyaev | DOCS | Актуализация finetuning/README.md, prompt_evaluation/README.md, PROJECT_STATE.md, README.md, ARCHITECTURE.md, MULTI_PROVIDER_ARCHITECTURE.md | Отразить ML-контур в документации | docs/ | ✅ Выполнено |

### [2.1.0] — 2026-06-28

| Дата | Автор | Тип | Что изменено | Причина | Затронуто | Статус |
|------|-------|-----|--------------|---------|-----------|--------|
| 2026-06-28 | Alexander Gulyaev | FEAT | Multi-Provider LLM Architecture: централизованная конфигурация провайдеров (`llm-provider-config.js`), поддержка RunPod (OpenAI-compatible endpoint), условный structured output, общие обработчики ошибок | Независимость от единственного LLM-провайдера | workflows/, docs/MULTI_PROVIDER_ARCHITECTURE.md | ✅ Выполнено |
| 2026-06-28 | Alexander Gulyaev | FIX | Исправлены broken connections после переименования нод; правильная схема credentials (IF + прямые connections); error outputs для RunPod-веток; удалены Merge-ноды для взаимоисключающих веток | Корректность архитектуры multi-provider | workflows/HR Processing Worker - Multi Provider Test.json | ✅ Выполнено |

### [2.0.0] — 2026-04-29

| Дата | Автор | Тип | Что изменено | Причина | Затронуто | Статус |
|------|-------|-----|--------------|---------|-----------|--------|
| 2026-06-24 | Alexander Gulyaev | FIX | KP-002: реальный bot token заменён на placeholder `REPLACE_ME_WITH_YOUR_BOT_TOKEN` в схеме БД | Риск утечки credentials при публикации | database/schema_hr_assistant.sql | ✅ Выполнено |
| 2026-04-29 | Alexander Gulyaev | FEAT | Мультимодальный ввод: текст, голос (STT), PDF/DOCX, фото (OCR) | Мультимодальность входного канала | HR Intake, HR Processing Worker | ✅ Выполнено |
| 2026-04-29 | Alexander Gulyaev | FEAT | Извлечение данных (JSON Schema + JSON Repair) и matching (score 0–100, decision, reason) | Автоматизация первичной обработки | HR Processing Worker | ✅ Выполнено |
| 2026-04-29 | Alexander Gulyaev | FEAT | Мультимедийный вывод: текст, TTS, визуальная карточка | Качество ответа кандидату | HR Delivery Worker | ✅ Выполнено |
| 2026-04-29 | Alexander Gulyaev | FEAT | Event-driven архитектура: очереди в БД, идемпотентность, retry, watchdogs, 11 таблиц БД | Надёжность обработки | БД, workflows | ✅ Выполнено |

### [1.0.0] — 2026-04-15

| Дата | Автор | Тип | Что изменено | Причина | Затронуто | Статус |
|------|-------|-----|--------------|---------|-----------|--------|
| 2026-04-15 | Alexander Gulyaev | FEAT | MVP: приём текстовых резюме через Telegram, извлечение данных GPT-4o-mini, сравнение с вакансиями, текстовый ответ; Docker Compose, PostgreSQL, n8n | Первая рабочая версия | Весь проект | ✅ Выполнено |

---

## ⏸️ 4. Отложенные и исторические пункты

Записи этого раздела **не являются текущими обязательствами** — они зафиксированы как история планирования. Актуальные направления развития — только в [`PROJECT_STATE.md`](PROJECT_STATE.md) (Next Steps).

| Дата | Пункт | Тип | Статус |
|------|-------|-----|--------|
| 2026-09-01 | Phase 0d (LoRA hard negatives: teacher-label audit, production smoke set) | Отложено владельцем — GPU-бюджета нет (RunPod не оплачен с августа 2026) | ⏸️ Отложено — задел на будущее |
| 2026-06-24 | Roadmap v2.1.0/v2.2.0 (email-канал, web-form, WhatsApp, аутентификация, мультиязычность, микросервисы) | Исторический план, составлен до выхода v2.0; частично реализовано иным составом | 🗄️ Историческое — не действует как обязательство |
| 2026-06-23 | Roadmap v3.0.0 (ATS/CRM-интеграция, аналитика, high-load) | Исторический план | 🗄️ Историческое — не действует как обязательство |

---

## 📚 5. Связанные документы

- [📊 `PROJECT_STATE.md`](PROJECT_STATE.md) — текущее состояние и направления развития
- [📜 `known-issues.md`](known-issues.md) — реестр дефектов с актуальными статусами
- [🚀 `DEPLOYMENT_GUIDE.md`](DEPLOYMENT_GUIDE.md) — развёртывание (Source of Truth)
- [🏗️ `ARCHITECTURE.md`](ARCHITECTURE.md) — архитектура системы

---

**Последнее обновление:** 2026-09-15