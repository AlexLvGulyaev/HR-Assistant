# Project State: HR Assistant

**Last Updated:** 2026-07-25
**Status:** Production-ready (v2.1) + Experimental ML-контур (Experiment 004 completed; LoRA validated as on-premise candidate) + LoRA storytelling landing deployed
**Case ID:** hr-assistant

---

## Project Summary

**HR Assistant (HR-ассистент)** — мультимодальный AI-ассистент для автоматизации первичной обработки резюме и подбора вакансий. Система принимает резюме в различных форматах через Telegram, извлекает структурированные данные с помощью LLM, сравнивает профиль кандидата с открытыми вакансиями и формирует мультимедийный ответ.

**Ключевые возможности:**
- Мультимодальный ввод: текст, голос, PDF/DOCX, изображения
- Извлечение данных: ФИО, город, должность, опыт, навыки, контакты, зарплатные ожидания
- Matching: сравнение профиля кандидата с вакансиями
- Мультимедийный вывод: текст + голос (TTS) + визуальные материалы

**Экспериментальный ML-контур:**
- Prompt Evaluation: A/B-тестирование промптов, формирование reference dataset
- Fine-tuning: LoRA-адаптеры для улучшения matching
- Runtime Smoke Validation: инженерный стенд для тестирования моделей

---

## Current Status

### Production-контур

| Компонент | Статус | Готовность | Комментарий |
|-----------|--------|------------|-------------|
| Workflow | Active | ✅ 100% | Все workflow импортированы и работают |
| Database | Deployed | ✅ 100% | Схема развернута, миграции применены |
| Integration | Live | ✅ 95% | Telegram bot работает, критическое расхождение с metadata |
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
| LoRA Model Production | Not Ready | ❌ 0% | LoRA не обгоняет GPT-4o-mini и не готова к production; открытые вопросы: score calibration, latency optimization, production smoke set |

**Ключевой вывод:** Fine-tuning Documentation Package завершён. Architecture 1.0 реализована: публичная документация `finetuning/` содержит `README.md`, `TECHNICAL_FOUNDATION.md`, отчёты Experiments 001–004, `teacher_dataset_report.md` и `external_validation_report.md`. LoRA-модель не production-ready; следующий цикл должен устранить hard-negative failures в real-world условиях через teacher-label audit и production smoke set.

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

3. **⚠️ LoRA PRECISION / RECALL TRADE-OFF** (открыто 2026-07-22, частично устранён 2026-07-22)
   - **Описание:** Experiment 003 прошёл runtime negative smoke, но на original test set появились ложные отрицательные решения на genuine match-кейсах. Модель стала слишком консервативной после добавления hard negatives.
   - **Влияние:** LoRA-адаптер не может заменить GPT-4o-mini в production, но пригоден как on-premise / edge альтернатива.
   - **Статус:** Частично устранён. Experiment 004 прошёл runtime smoke (7/7). На внешней валидации HRA-EVAL-V5-EXT (102 пары, GPT-4o reference) LoRA достигла decision_accuracy 0.931 vs GPT-4o-mini 0.941 на каноническом runtime. После vLLM-ускорения (3 повторных прогона) LoRA достигла decision_accuracy 0.931 vs GPT-4o-mini 0.925 при сопоставимом p95 latency (~2.1 сек vs ~2.0 сек). Score calibration (MAE 19.6 vs 6.2) остаётся открытым.
   - **Ссылки:** [Experiment_003_Report.md](../finetuning/Experiment_003_Report.md), [Experiment_004_Report.md](../finetuning/Experiment_004_Report.md), [teacher_dataset_report.md](../finetuning/reports/teacher_dataset_report.md)
   - **Рекомендации:** score calibration, vLLM/TGI inference, quantization, расширение teacher dataset, production smoke set.

4. **🟡 VALIDATION ACCURACY VS PRODUCTION HARD NEGATIVES MISMATCH** (открыто 2026-07-22)
   - **Описание:** LoRA показывает decision_accuracy 0.931 на external validation (и 0.931 vs 0.925 GPT-4o-mini после vLLM-ускорения), но в реальном Telegram smoke test на 23 hard-negative/edge анкетах даёт только 35 % корректных ответов (vs 43 % у GPT-4o-mini). Анализ teacher dataset V4 показал, что 5 из 33 hard-negative-like записей (15 %) размечены reference-teacher как `match` (BA → SA, DA → SA и др.). External validation V5-EXT не покрывает ключевые failure modes Telegram: процессный аналитик, salary mismatch 450 000, extreme sparse junior/стажёр. В результате `decision_accuracy` по всему набору не отражает production-качество на сложных кейсах. Детальные примеры — в [`finetuning/data/evidence/telegram_smoke_test_summary.json`](finetuning/data/evidence/telegram_smoke_test_summary.json) и [`finetuning/data/evidence/teacher_label_mismatch_v4.json`](finetuning/data/evidence/teacher_label_mismatch_v4.json).
   - **Влияние:** Метрика 0.931 создаёт ложное ощущение готовности LoRA к production; критические false positives (аналитики на SA, junior, salary mismatch) остаются незамеченными до реального тестирования.
   - **Статус:** Открыто. Решение: ввести stratified metrics и production smoke set.
   - **Ссылки:** [teacher_dataset_report.md](../finetuning/reports/teacher_dataset_report.md), [Experiment_004_Report.md](../finetuning/Experiment_004_Report.md)
   - **Рекомендации:**
     - Ввести stratified decision accuracy: POSITIVE, OBVIOUSNOMATCH, BORDERLINE, HARD NEGATIVE.
     - Считать FPR по категориям hard negatives (BA/DA/process analyst → SA, junior/стажёр, salary mismatch, одиночный навык).
     - Сформировать production smoke set (~30–50 кейсов), покрывающий HN1–HN8, EC1, EC3, EC4, POSITIVE, OBVIOUSNOMATCH.
     - Перед следующим циклом дообучения ре-разметить hard negatives с жёстким критерием: без прямых ключевых навыков → `no_match`.
     - Добавить в teacher dataset extreme sparse profiles и salary mismatch.

#### Representative example: teacher-label mismatch в production-like hard negative

**Candidate:** Data Analyst, 4 года опыта, SQL, Python, BI, визуализация данных, Excel; без BPMN, REST API и опыта постановки задач разработчикам.

**Vacancy:** Системный аналитик; требуется SQL, BPMN, REST API, аналитика, постановка задач разработчикам.

**Teacher label (GPT-4.1):** `match`, score 71.

**Почему этот пример важен:** Иллюстрирует причину расхождения между aggregate validation accuracy и production-качеством: teacher разметил hard-negative-like запись как `match`, поэтому LoRA наследует эту ошибку и принимает смежные роли без обязательных hard skills.

**Evidence:** [`finetuning/data/evidence/teacher_label_mismatch_v4.json`](finetuning/data/evidence/teacher_label_mismatch_v4.json), запись `HRA-EVAL-V2-000103`, vacancy "Системный аналитик".

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

## Documentation Status

### Documentation Audit (2026-06-24)

Проведён аудит документации по паттерну SOT (Source of Truth):
- Проверено 3 документа: HR_GUIDE.md, INTEGRATION_DIAGRAM.md, SUPPORT_RUNBOOK.md
- Исправлено 27 нарушений (синтетические данные, неверные модели, ошибки изображений)
- Все документы приведены в соответствие с реальными источниками (workflow, БД, SCREENSHOT_INDEX)

**Применённый паттерн:** [documentation-source-of-truth-discipline.md](../../../shared/patterns/documentation-source-of-truth-discipline.md)

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

### Fine-tuning Documents

| Документ | Статус | Источник | Приоритет |
|----------|--------|----------|-----------|
| **finetuning/README.md** | ✅ Обновлён | HRA Decision | 🔴 Высокий |
| **finetuning/TECHNICAL_FOUNDATION.md** | ✅ Создан | HRA Decision | 🟡 Средний |
| **finetuning/Experiment_001_Report.md** | ✅ Создан | HRA Decision | 🟡 Средний |
| **finetuning/Experiment_002_Report.md** | ✅ Создан | HRA Decision | 🟡 Средний |
| **finetuning/Experiment_003_Report.md** | ✅ Создан | HRA Decision | 🔴 Высокий |
| **finetuning/Experiment_004_Report.md** | ✅ Создан | HRA Decision | 🔴 Высокий |
| **finetuning/runs/experiment_002/README.md** | ✅ Создан | Auto-generated | 🟡 Средний |
| **api/hra_qwen_api.py** | ✅ Создан | HRA Decision | 🟡 Средний |
| **api/hra_qwen_api_lora.py** | ✅ Создан | HRA Decision | 🟡 Средний |
| **finetuning/reports/teacher_dataset_report.md** | ✅ Создан | HRA Decision | 🟡 Средний |
| **finetuning/reports/external_validation_report.md** | ✅ Создан | HRA Decision | 🟡 Средний |

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
| **Prompt Evaluation** | ✅ Высокий | A/B-тестирование, Judge methodology, reproducibility |
| **LoRA Fine-tuning** | ⚠️ Средний | Experiment 002 завершён, не production-ready |
| **Multi-Provider Runtime** | ⚠️ Средний | Инженерный стенд для smoke validation |

### Дефициты компетенций

1. **Hard Negative Examples** — teacher dataset требует расширения
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

### Phase 0: Fine-tuning Cycle 3 — Experiment 003 (приоритет: критический)

**Цель:** Проверить гипотезу о влиянии hard negative примеров на runtime negative smoke test

**Задачи:**
- [x] Расширить teacher dataset (hard negative examples)
- [x] Провести experiment_003
- [x] Пройти runtime smoke validation
- [x] Документировать результаты

**Результат:** Гипотеза подтверждена частично — runtime negative smoke пройден, но появился precision/recall trade-off.

**Срок:** завершён 2026-07-22

---

### Phase 0b: Fine-tuning Cycle 4 — Experiment 004 (приоритет: критический) ✅ ЗАВЕРШЁН

**Цель:** Устранить precision/recall trade-off Experiment 003 и подготовить LoRA-модель к production

**Задачи:**
- [x] Сформулировать и утвердить гипотезу Cycle 4 — баланс positive/borderline примеров, сохранение hard negatives, сравнение с GPT-4o-mini
- [x] Подготовить изменённый teacher dataset — 13 новых positive/borderline примеров, SQL-скрипты V4 и валидация
- [x] Провести проектирование Experiment_004 (конфиг, launch contract, transfer list, smoke set)
- [x] Провести обучение Experiment_004 в RunPod CC
- [x] Пройти runtime smoke validation без ложных отрицательных решений
- [x] Подтвердить сохранение качества на internal test set
- [x] Выполнить A/B-сравнение с GPT-4o-mini на internal test set (15 records)
- [x] Выполнить A/B-сравнение с GPT-4o-mini на external validation set (HRA-EVAL-V5-EXT, 102 pairs, GPT-4o reference judge)
- [x] Зафиксировать итоговый вердикт по гипотезе в Experiment_004_Report.md

**Результат:**
- Гипотеза частично подтверждена.
- LoRA обобщается на external validation: decision_accuracy 0.931 vs GPT-4o-mini 0.941.
- LoRA не обгоняет GPT-4o-mini по совокупности метрик (MAE, latency).
- LoRA подходит как on-premise / edge кандидат.

**Рекомендации для следующих циклов:**
1. Score calibration (MAE 19.6 vs 6.2)
2. Latency optimization (vLLM/TGI, quantization)
3. Снижение FNR (дополнительные positive/borderline примеры)
4. Расширение teacher dataset до 300–500 пар
5. Эксперименты с QLoRA / larger base model

**Срок:** завершён 2026-07-22

---

### Phase 0c: Latency Optimization — Experiment 004 (приоритет: средний) ✅ ЗАВЕРШЁН

**Цель:** Снизить p95 latency LoRA inference с ~17 секунд до ≤2 секунд без переобучения, сохранив decision_accuracy в пределах 5 pp от 0.931 на external validation.

**Результат:**
- Созданы экспериментальные runtime: 4-bit quantized API (`api/hra_qwen_api_lora_4bit.py`) и vLLM launcher (`api/hra_qwen_api_lora_vllm.py`).
- vLLM сократил p95 latency до ~2.1 сек.
- Канонический runtime Experiments 003–004 — FastAPI + Transformers + PEFT.
- Подробнее — `finetuning/Experiment_004_Report.md`, раздел 9.3 и 6.3.

**Срок:** завершён 2026-07-22

---

### Phase 0d: Hard-Negative Dataset Fix & Production Metrics (приоритет: критический) ⛔ НЕ ВЫПОЛНЯЕТСЯ (решение владельца, 2026-09-01)

> **Решение владельца (01.09.2026):** Phase 0d закрывается как неисполнимый — GPU-бюджета нет (Runpod не оплачен с августа 2026), fix hard negatives и прогоны LoRA на production smoke set выполнить и **проверить невозможно**. Задачи ниже остаются как задел на будущее при возобновлении GPU-финансирования. Живой контур продолжает работать на GPT-4o-mini.

**Цель:** Устранить mismatch между validation accuracy и production-качеством на hard negatives; подготовить метрики и production smoke set для принятия решения о внедрении LoRA.

**Контекст:**
- Teacher dataset V4 содержит hard negatives, размеченные как `match` (5 / 33 hard-negative-like записей). Детали — в [`finetuning/data/evidence/teacher_label_mismatch_v4.json`](finetuning/data/evidence/teacher_label_mismatch_v4.json).
- External validation V5-EXT недостаточно покрывает production-failure modes (процессный аналитик, salary mismatch 450k, extreme sparse junior).
- Telegram smoke test показал: LoRA 35 %, GPT-4o-mini 43 % на 23 hard-negative/edge анкетах.

**Задачи:**
- [ ] Сформулировать жёсткий критерий разметки hard negatives (BA/DA/process analyst → SA = no_match без прямых скиллов; junior/стажёр → senior/middle вакансия = no_match; salary > max на 50 %+ = no_match).
- [ ] Ре-разметить hard negatives в teacher dataset V4 (или создать V5) с учётом критерия.
- [ ] Добавить extreme sparse profiles: стажёр с 1 навыком SQL, junior с 0 лет опытом, кандидат без IT-коннотаций.
- [ ] Добавить salary mismatch примеры (salary выше максимума на 50 %+ при сильном профиле).
- [ ] Добавить процессного аналитика на SA и Prompt Engineer.
- [ ] Сформировать production smoke set 30–50 кейсов, покрывающий HN1–HN8, EC1, EC3, EC4, POSITIVE, OBVIOUSNOMATCH.
- [ ] Ввести stratified metrics: accuracy/FPR по POSITIVE / OBVIOUSNOMATCH / BORDERLINE / HARD NEGATIVE.
- [ ] Прогнать LoRA и GPT-4o-mini на production smoke set и зафиксировать сравнение.
- [ ] Обновить `finetuning/reports/teacher_dataset_report.md`, `finetuning/Experiment_004_Report.md` и `docs/PROJECT_STATE.md` по результатам.

**Критерий готовности LoRA к production:**
- ≥ 70 % correct на production smoke set;
- FPR ≤ 15 % на hard-negative категориях;
- MAE score ≤ 15 на POSITIVE / OBVIOUSNOMATCH strata.

**Срок:** 2–3 дня (после завершения Phase 0c).

---

### Phase 1: Документация кейса HR Assistant (приоритет: высокий) ✅ ЗАВЕРШЁН

**Документационный пакет корневой документации создан полностью (2026-06-23, «Documentation Complete» — см. Status History) и верифицирован SOT-аудитом (2026-06-24).** Фактическая база `docs/` включает все документы из этого плана и больше:

- **Customer Facing Layer:** BUSINESS_VALUE.md, E2E_SCENARIOS.md, NARRATIVE_BLUEPRINT.md
- **User / Operator Layer:** USER_GUIDE.md, HR_GUIDE.md, SUPPORT_RUNBOOK.md
- **Engineering Layer:** ARCHITECTURE.md, DEPLOYMENT_GUIDE.md, AI_QUALIFICATION.md, AUTOMATION_PASSPORT.md, INTEGRATION_DIAGRAM.md, CHANGE_LOG.md, MULTI_PROVIDER_ARCHITECTURE.md, EXPERIMENTAL_ML_PIPELINE.md, PROMPT_ENGINEERING_GUIDE.md, WORKFLOW_MODIFICATION_GUIDE.md
- **Плюс:** SPEC.md, SUCCESS_METRICS.md, PROJECT_HANDOFF_CHECKLIST.md, known-issues.md, PROJECT_STATE.md, screenshots/

> Исторический чек-лист этого Phase (11 пунктов «создать …») удалён 01.09.2026 как не соответствующий факту: все перечисленные документы существуют с июня 2026. Устаревшая запись дезориентировала аудит корпуса (PORTFOLIO_CORPUS_AUDIT) и планирование.

---

### Phase 2: Исправление критических дефектов (приоритет: высокий) ✅ ЗАВЕРШЁН (2026-09-01)

**Цель:** Устранить расхождение metadata (KP-001)

**Задачи:**
- [x] Определить источник данных для metadata полей — узел `Build TG response` Processing Worker
- [x] Добавить заполнение metadata в HR Processing Worker — все 5 INSERT в обеих версиях workflow (`HR Processing Worker.json`, `HR Processing Worker - Multi Provider Test.json`); ветки ошибок пишут NULL
- [x] Документировать формат metadata — `SPEC.md`, раздел «Контракт metadata» (8 ключей, распределение по типам сообщений)
- [x] Перенести credentials в environment variables — проверка показала: ключи уже НЕ в репозитории. OpenAI — n8n credential store (`genericCredentialType`), bot token — таблица `bot_credentials` с placeholder (KP-002, исправлено 24.06); документировано в DEPLOYMENT_GUIDE §5. Пункт закрыт «как уже выполненный», переноса не требуется
- [x] Протестировать TTS и visual generation — живая проверка 01.09.2026 пройдена, приёмка владельца ✅ (голос — связный текст, картинка — карточка с кандидатом/вакансией/скором)

**Срок:** завершён 2026-09-01, включая живую проверку

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

### Phase 4: Web-консоль HR-специалиста (приоритет: средний, планируемый)

**Цель:** Дать HR-специалисту и рекрутеру удобный интерфейс для просмотра кандидатов, match score и принятия решений — вместо прямого доступа к PostgreSQL.

**Контекст:**
- Сейчас HR-специалист работает с результатами matching через прямой доступ к БД (`candidates`, `matches`, `candidate_contacts`) или видит только Telegram-ответ, который бот отправил кандидату.
- В лендинге и документации используется визуальная «карточка кандидата с match score», но это планируемый UI, а не реализованный интерфейс.

**Минимальный scope консоли:**
- Список кандидатов с фильтрами по статусу, вакансии, score, дате.
- Карточка кандидата: профиль, контакты, разбивка score по 4 критериям, reason, raw_llm_response.
- Действия: «Пригласить», «Отклонить», «Отложить», «Назначить на другую вакансию».
- История решений и комментариев HR.

**Технические варианты:**
1. **n8n Form / n8n Dashboard** — быстрее всего, если уже используется n8n.
2. **Минимальный веб-интерфейс на FastAPI + Jinja2 / React** — self-hosted, гибче.
3. **Интеграция с существующей HR-системой** — через API или webhooks.

**Критерий готовности:**
- HR-специалист может зайти в консоль и принять решение по кандидату без SQL.
- Решение HR сохраняется в БД и может использоваться для замыкания feedback loop (KB learning).

**Зависимости:**
- Phase 2 (исправление metadata и credentials) — для корректной передачи данных.
- Уточнение ролевой модели: кто может видеть/редактировать кандидатов.

**Срок:** По решению владельца проекта; не входит в текущий production-ready контур.

---

## Documentation Roadmap — ✅ выполнен

Документационный пакет создан полностью (2026-06-23) и верифицирован SOT-аудитом (2026-06-24). Исторический план создания (приоритеты «высокий/средний/низкий» на 19 документов и таблица источников материалов) удалён 01.09.2026 как исполненный — актуальный состав документации см. в Phase 1 (✅) и разделе Documentation Status. Таблица источников сохранена в истории git (до 01.09.2026).

---

## Related Documents

### Созданные документы

Корневая документация кейса (`docs/`): SPEC.md, BUSINESS_VALUE.md, E2E_SCENARIOS.md, NARRATIVE_BLUEPRINT.md, USER_GUIDE.md, HR_GUIDE.md, SUPPORT_RUNBOOK.md, ARCHITECTURE.md, DEPLOYMENT_GUIDE.md, AI_QUALIFICATION.md, AUTOMATION_PASSPORT.md, INTEGRATION_DIAGRAM.md, CHANGE_LOG.md, MULTI_PROVIDER_ARCHITECTURE.md, EXPERIMENTAL_ML_PIPELINE.md, PROMPT_ENGINEERING_GUIDE.md, WORKFLOW_MODIFICATION_GUIDE.md, SUCCESS_METRICS.md, PROJECT_HANDOFF_CHECKLIST.md, known-issues.md, PROJECT_STATE.md.

Прочее: [README.md](../README.md) — описание кейса, [workflows/README.md](../workflows/README.md) — описание workflow, [database/README.md](../database/README.md) — описание схемы БД, `finetuning/` — пакет документации fine-tuning контура.

---

## Status History

| Дата | Статус | Изменение |
|------|--------|-----------|
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