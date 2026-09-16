# 📊 PROJECT_STATE — HR Assistant

**Status:** Production-ready (v2.3.0, 2026-09-01) + Experimental ML-контур (Experiment 004 completed; LoRA validated as on-premise candidate) + LoRA storytelling landing deployed
**Case ID:** hr-assistant

---

## 🎯 1. Project Summary

**HR Assistant (HR-ассистент)** — мультимодальный AI-ассистент для автоматизации первичной обработки резюме и подбора вакансий. Система принимает резюме в различных форматах через Telegram, извлекает структурированные данные с помощью LLM, сравнивает профиль кандидата с открытыми вакансиями и формирует мультимедийный ответ.

**Возможности:**
- Мультимодальный ввод: текст, голос, PDF/DOCX, изображения
- Извлечение данных: ФИО, город, должность, опыт, навыки, контакты, зарплатные ожидания
- Matching: сравнение профиля кандидата с вакансиями
- Мультимедийный вывод: текст + голос (TTS) + визуальные материалы

**Экспериментальный ML-контур:**
- Prompt Evaluation: A/B-тестирование промптов, формирование reference dataset
- Fine-tuning: LoRA-адаптеры для улучшения matching
- Runtime Smoke Validation: инженерный стенд для тестирования моделей

---

## 📊 2. Current Status

### Production-контур

| Компонент | Статус | Готовность | Комментарий |
|-----------|--------|------------|-------------|
| Workflow | Active | ✅ 100% | Все workflow импортированы и работают |
| Database | Deployed | ✅ 100% | Схема развернута, миграции применены |
| Integration | Live | ✅ 100% | Telegram bot работает; metadata gap (KP-001) исправлен 2026-09-01, приёмка владельца пройдена |
| Documentation | Complete | ✅ 100% | Все обязательные документы созданы и проверены по SOT |
| Security | Improved | ✅ 85% | KP-002 исправлен, токен в БД с placeholder в SQL |

### Экспериментальный ML-контур

| Компонент | Статус | Готовность | Комментарий |
|-----------|--------|------------|-------------|
| Prompt Evaluation | Active | ✅ 100% | HRA-EXP-V1 завершён, сформирован reference dataset |
| Fine-tuning Infrastructure | Experimental | ✅ 100% | Каталог finetuning/, configs, scripts, runs, launch contract pattern |
| Fine-tuning Experiment 003 | Completed | ✅ 100% | Runtime negative smoke пройден (7/7), offline decision accuracy на original test снизилась до 0.667 |
| Fine-tuning Cycle 4 / Experiment 004 | Completed | ✅ 100% | External validation пройдена: LoRA 0.931 vs GPT-4o-mini 0.941 на каноническом runtime (102 пары, GPT-4o reference). После vLLM-ускорения: LoRA 0.931 vs GPT-4o-mini 0.925 (3 повторных прогона, p95 latency ~2.1 сек). LoRA является рабочим on-premise / edge кандидатом; production остаётся за GPT-4o-mini из-за Telegram smoke 35% vs 43%. |
| Runtime Smoke Validation | Engineering Test | ✅ 100% | Локальный `runtime_smoke_test.py` + Multi Provider Test workflow |
| LoRA Model Production | Not Ready | ❌ 0% | Offline external validation: LoRA обгоняет GPT-4o-mini (0.931 vs 0.925, vLLM), real-world Telegram smoke: 35% vs 43% — production остаётся за GPT-4o-mini. Открытые вопросы: score calibration, production smoke set |

**Вывод:** Fine-tuning Documentation Package завершён. Architecture 1.0 реализована: публичная документация `finetuning/` содержит `README.md`, `TECHNICAL_FOUNDATION.md`, отчёты Experiments 001–004, `teacher_dataset_report.md` и `external_validation_report.md`. LoRA-модель не production-ready; следующий цикл должен устранить hard-negative failures в real-world условиях через teacher-label audit и production smoke set.

### Известные проблемы

Единственный реестр дефектов с деталями и историей — [known-issues.md](known-issues.md): KP-001 (несовместимость metadata, ✅ Fixed 2026-09-01), KP-002 (bot token в репозитории, ✅ Fixed 2026-06-24), KP-003 (версионирование workflow, 🔴 Open).

Открытые вопросы ML-контура (детали и evidence — [EXPERIMENTAL_ML_PIPELINE.md](EXPERIMENTAL_ML_PIPELINE.md) и отчёты `finetuning/`):

- **LoRA precision/recall trade-off** — частично устранён (Experiment 004: runtime smoke 7/7; external validation 0.931 vs 0.925 после vLLM-ускорения); score calibration (MAE 19.6 vs 6.2) остаётся открытым — [Experiment_004_Report.md](../finetuning/Experiment_004_Report.md).
- **Validation accuracy vs production hard negatives mismatch**: LoRA 0.931 на external validation, но 35% корректных на реальном Telegram smoke (23 edge-анкеты) vs 43% у GPT-4o-mini. Решение: stratified metrics + production smoke set — [teacher_dataset_report.md](../finetuning/reports/teacher_dataset_report.md).

---

### LoRA Storytelling Landing

| Компонент | Статус | Готовность | Комментарий |
|-----------|--------|------------|-------------|
| **Landing HTML/CSS/JS** | Deployed | ✅ 100% | 15 сцен, scroll-анимации, адаптивность |
| **Engineering graphs** | Deployed | ✅ 100% | 15 SVG-графиков из артефактов экспериментов |
| **Evidence Room** | Deployed | ✅ 100% | 7 expandable box-ов с таблицами и графиками |
| **Production URL** | Live | ✅ 100% | https://hra-lora.alex-n8n.site, HTTPS, gzip, security headers |
| **Deployment Guide** | Updated | ✅ 100% | Docker + Traefik (current), Caddy/nginx (alternatives) |

---

## 📖 3. Documentation Status

Состав и назначение документов — [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md). История изменений документов — [CHANGE_LOG.md](CHANGE_LOG.md#-4-история-изменений-документации).

**Актуальное состояние:**
- Публичный пакет: 21 документ `docs/` + README + под-доки (finetuning/, workflows/, database/, docs/prompt_evaluation/README, docs/screenshots/MEDIA_INDEX) — все с футером «Статус / Последнее обновление / История изменений».
- Ревизия к стандарту APL — 2026-09-15 (вехи в Status History); норма «история документа — только в CHANGE_LOG» — 2026-09-16.
- Вне публичного пакета: внутренние инженерные материалы и замороженные eval-отчёты `docs/prompt_evaluation/*`.

Исторический SOT-аудит (2026-06-24) — веха в Status History.

---

## 💼 4. Market Validation

**Статус:** Проект разработан в инженерной среде AI Automation Portfolio Lab (учебно-портфельный проект)

**Заказчик:** Отсутствует (не коммерческий)

**Потенциал:** Высокий для HR-автоматизации в SMB сегменте

---

## 💰 5. Commercial Assessment

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

## 🛠️ 6. Key Technology Areas

### Компетенции

| Область | Уровень | Комментарий |
|---------|---------|-------------|
| n8n workflow | ✅ Высокий | Сложная логика, обработка ошибок, watchdog |
| PostgreSQL | ✅ Высокий | Нормализованная схема, индексы, функции |
| OpenAI API | ✅ Высокий | GPT-4, GPT-4o-mini, GPT-image-1, Sora-2, TTS |
| Telegram Bot API | ✅ Высокий | Webhook, inline keyboard, мультимедиа |
| Docker Compose | ✅ Средний | Production-развертывание с Traefik |
| **Prompt Evaluation** | ✅ Высокий | A/B-тестирование, Judge methodology, reproducibility |
| **LoRA Fine-tuning** | ⚠️ Средний | Experiment 002 завершён, не production-ready |
| **Multi-Provider Runtime** | ⚠️ Средний | Инженерный стенд для smoke validation |

### Дефициты компетенций

1. **Hard Negative Examples** — teacher dataset требует расширения
2. **Мониторинг и аналитика** — отсутствуют дашборды
3. **Security audit** — не проводился

---

## 🧭 7. Decision

**Решение:** Интегрировать HR Assistant в APL как самостоятельный кейс с последующим исправлением критических дефектов и созданием документации.

**Обоснование:**
- Рабочий production-решение
- Высокая образовательная ценность
- Потенциал для коммерциализации
- Хороший пример мультимодальной архитектуры

---

## 🗺️ 8. Next Steps

### Reproducibility debt (высокий приоритет)

- [ ] Clean-room Deployment Validation: развёртывание с нуля по DEPLOYMENT_GUIDE в чистом окружении

### Phase 0d: Hard-Negative Dataset Fix & Production Metrics ⛔ (решение владельца, 2026-09-01)

Не выполняется: GPU-бюджета нет (RunPod не оплачен с августа 2026). Задел при возобновлении GPU-финансирования:

- Жёсткий критерий разметки hard negatives (BA/DA/process analyst → SA = no_match без прямых скиллов; junior/стажёр; salary > max на 50 %+).
- Ре-разметка teacher dataset (V4 → V5), extreme sparse profiles, salary mismatch примеры.
- Production smoke set (30–50 кейсов: HN1–HN8, EC1, EC3, EC4, POSITIVE, OBVIOUSNOMATCH), stratified metrics (accuracy/FPR по категориям).
- Сравнительный прогон LoRA vs GPT-4o-mini на production smoke set.

### Phase 3: Дополнительные материалы (средний, по необходимости)

- [ ] Оценить необходимость IMPLEMENTATION_PLAN.md
- [ ] MULTIMODALITY.md (описание мультимодальных возможностей), ECONOMICS.md (экономика токенов)

### Phase 4: Web-консоль HR-специалиста (средний, планируемый)

Интерфейс просмотра кандидатов и принятия решений вместо прямого доступа к PostgreSQL. Минимальный scope: список с фильтрами (статус/вакансия/score/дата), карточка кандидата (профиль, контакты, разбивка score, reason), действия HR (пригласить/отклонить/отложить), история решений. Критерий готовности: решение по кандидату без SQL. Срок — по решению владельца; не входит в текущий production-ready контур.

### Выполненные фазы

Вехи — в Status History: Phase 0b/0c (Experiment 004 + latency optimization, vLLM), Phase 1 (документация кейса), Phase 2 (KP-001, KP-002, 2026-09-01).

---

## 📚 9. Related Documents

### Созданные документы

Корневая документация кейса (`docs/`): SPEC.md, BUSINESS_VALUE.md, E2E_SCENARIOS.md, DEMO_ROUTE.md, USER_GUIDE.md, HR_GUIDE.md, SUPPORT_RUNBOOK.md, ARCHITECTURE.md, DEPLOYMENT_GUIDE.md, AI_QUALIFICATION.md, AUTOMATION_PASSPORT.md, INTEGRATION_DIAGRAM.md, CHANGE_LOG.md, MULTI_PROVIDER_ARCHITECTURE.md, EXPERIMENTAL_ML_PIPELINE.md, PROMPT_ENGINEERING_GUIDE.md, SUCCESS_METRICS.md, PROJECT_HANDOFF_CHECKLIST.md, known-issues.md, PROJECT_STRUCTURE.md, SECURITY_NOTES.md, PROJECT_STATE.md, MEDIA_INDEX.md (docs/screenshots/).

Прочее: [README.md](../README.md) — описание кейса, [workflows/README.md](../workflows/README.md) — описание workflow, [database/README.md](../database/README.md) — описание схемы БД, `finetuning/` — пакет документации fine-tuning контура.

---

## 📜 10. Status History

| Дата | Статус | Изменение |
|------|--------|-----------|
| 2026-09-15 | Documentation Revision (APL Standard) | Публичная документация приведена к стандарту APL (трёхслойная модель, эмодзи-контракт, один документ — один читатель): README переписан как entry point; созданы PROJECT_STRUCTURE.md, MEDIA_INDEX.md (слит SCREENSHOT_INDEX), SECURITY_NOTES.md; DEPLOYMENT_GUIDE актуализирован по фактическому runtime (compose-сервисы, n8n image, vacancies.status='open'); WORKFLOW_MODIFICATION_GUIDE слит в MULTI_PROVIDER_ARCHITECTURE; внутренний narrative-документ исключён из публичного пакета; clean-room Deployment Validation не проводилась — зафиксирована как reproducibility debt. Продукт не изменялся |
| 2026-09-01 | Phase 2 Closed, Phase 0d Cancelled | Phase 2 завершён: KP-001 (metadata) исправлен в обеих версиях Processing Worker — 5 INSERT заполняют metadata из узла «Build TG response», контракт с Delivery Worker сверен по обеим сторонам, формат документирован в SPEC.md; пункт «credentials → env» оказался уже выполненным (n8n credential store + bot_credentials, KP-002). Phase 0d (hard negatives LoRA) отменён решением владельца: GPU-бюджета нет (Runpod не оплачен с августа), проверка невозможна. Живая проверка TTS/visual — приёмка владельца на живом инстансе |
| 2026-09-01 | Documentation Debt Removed | Из PROJECT_STATE удалён устаревший «долг» Phase 1 (11 чек-боксов «создать …»): все документы существуют с 23.06.2026 и верифицированы SOT-аудитом 24.06.2026; Documentation Roadmap помечен выполненным. Устаревшая запись дезориентировала аудит корпуса — реальный открытый долг кейса: Phase 0d (hard-negative fix + production smoke set), Phase 2 (metadata + credentials) |
| 2026-07-22 | Validation vs Production Mismatch | Анализ teacher dataset и external validation объяснил расхождение: hard negatives часто размечены как match, external validation не покрывает Telegram-failure modes; введён Phase 0d с stratified metrics и production smoke set |
| 2026-07-22 | Fine-tuning Experiment 003 | Runtime negative smoke пройден (7/7), но decision accuracy на original test снизилась (−11.1 pp); гипотеза подтверждена частично, модель не production-ready |
| 2026-06-28 | Fine-tuning Experiment 002 | Лучший результат offline, failed negative smoke test, не production-ready |
| 2026-06-28 | Multi-Provider Architecture | Добавлен инженерный стенд для smoke validation LLM-провайдеров |
| 2026-06-28 | Runtime API | Добавлены hra_qwen_api.py и hra_qwen_api_lora.py для LoRA-моделей |
| 2026-06-27 | Fine-tuning Infrastructure | Создан каталог finetuning/, configs, scripts, runs, reports |
| 2026-06-27 | Prompt Evaluation V2 | Обновлённый эксперимент HRA-EXP-V1, расширенная база данных |
| 2026-06-24 | Documentation SOT Audit | Аудит документации по паттерну SOT, исправлено 27 нарушений в 3 документах |
| 2026-06-24 | Security Improved | KP-002 исправлен (bot token заменён на placeholder) |
| 2026-06-23 | Documentation Complete | Созданы все обязательные документы документационного пакета (17 документов) |
| 2026-06-23 | Documentation Audit | Полный аудит документационного пакета, верификация по 3LDS и LQ Practice |
| 2026-06-23 | Production-ready | Интеграция в APL, выявлены критические дефекты |
| 2026-04-29 | Production-ready | Финальная версия V2.0 |
| 2026-04-29 | Development | Разработка V2.0 |

---

**Последнее обновление:** 2026-09-16
**История изменений:** [📝 CHANGE_LOG.md](CHANGE_LOG.md#-4-история-изменений-документации)
