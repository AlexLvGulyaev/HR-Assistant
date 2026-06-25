# Руководство по промпт-инжинирингу: HR Assistant

**Навигационный документ по системе промптов проекта.**

---

## Обзор системы промптов

HR Assistant использует промпты в двух контекстах:

1. **Боевая система (Production)** — промпты для обработки резюме и matching
2. **Экспериментальный контур (Prompt Evaluation)** — промпты для A/B-тестирования

**Ключевой принцип:** Все промпты используют JSON Schema для структурированного ответа.

---

## Боевые промпты (Production)

### 1. Candidate Extraction

**Workflow:** HR Processing Worker

**Модель:** gpt-4o-mini-2024-07-18

**Temperature:** 0

**Назначение:** Извлечение структурированных данных кандидата из нормализованного текста резюме.

**Формат ответа:** JSON Schema (candidate_profile)

**Поля JSON Schema:**
- `full_name` (string | null)
- `city` (string | null)
- `desired_position` (string | null)
- `experience_years` (number | null)
- `skills` (array of strings)
- `salary_expectation` (number | null)
- `email` (string | null)
- `phone` (string | null)
- `summary` (string | null)

**Обработка результата:**
- Валидация JSON
- Проверка наличия всех required полей
- Проверка типов данных
- Meaningful content check
- Если JSON невалиден → переход к JSON Repair

**Ограничения:**
- Извлекает только явно указанные данные
- Не выдумывает отсутствующие сведения
- Может не извлечь контакты, если они не указаны явно
- При низком качестве текста (OCR, STT) точность снижается

**Статус:** Production-ready

**SSOT:** [AI_QUALIFICATION.md](AI_QUALIFICATION.md#1-извлечение-данных-кандидата)

---

### 2. JSON Repair

**Workflow:** HR Processing Worker

**Модель:** gpt-4o-mini-2024-07-18

**Temperature:** 0

**Назначение:** Ремонт невалидного JSON от Candidate Extraction.

**Формат ответа:** JSON Schema (candidate_profile)

**Обработка результата:**
1. Проверка валидности JSON
2. Проверка типов данных
3. Если всё ещё невалидный → fallback на processing error

**Статус:** Production-ready

**SSOT:** [AI_QUALIFICATION.md](AI_QUALIFICATION.md#2-ремонт-невалидного-json)

---

### 3. Matching (Production Prompt A)

**Workflow:** HR Processing Worker

**Модель:** gpt-4o-mini-2024-07-18

**Temperature:** 0

**Назначение:** Сравнение профиля кандидата с вакансиями, формирование score и recommendation.

**Формат ответа:** JSON Schema (vacancy_match_result)

**Поля JSON Schema:**
- `vacancy_id` (string | null)
- `title` (string | null)
- `role_score` (number, 0-30)
- `skills_score` (number, 0-35)
- `experience_score` (number, 0-20)
- `conditions_score` (number, 0-15)
- `score` (number, 0-100)
- `decision` (enum: "match" | "no_match")
- `reason` (string)

**Система оценки:**

| Критерий | Макс. баллов | Описание |
|----------|--------------|----------|
| **Должность / роль** | 30 | Соответствие желаемой должности и роли вакансии |
| **Навыки** | 35 | Пересечение навыков кандидата с требованиями вакансии |
| **Опыт** | 20 | Соответствие опыта работы требованиям |
| **Город / формат / зарплата** | 15 | Город, формат работы, зарплатные ожидания |
| **Итого** | **100** | Максимальный score |

**Порог для match:** score >= 60

**Обработка результата:**
1. Извлечение JSON из ответа LLM
2. Валидация и clamps каждого score (role: 0-30, skills: 0-35, experience: 0-20, conditions: 0-15)
3. Вычисление итогового score как суммы или берётся из модели
4. Установка decision на основе порога (>= 60 → match)
5. Сохранение результата в БД

**Fallback:** Если JSON невалиден → score = 0, decision = "no_match", reason = "Не удалось разобрать ответ модели"

**Ограничения:**
- Работает только с русским языком
- Требует структурированных данных кандидата и вакансии
- Не учитывает мягкие навыки и культурное соответствие
- При неполных данных кандидата score может быть занижен

**Статус:** Production-ready

**SSOT:** [AI_QUALIFICATION.md](AI_QUALIFICATION.md#3-matching-кандидата-с-вакансиями)

---

## Экспериментальные промпты (Prompt Evaluation)

### Подсистема Prompt Evaluation

**Документация:** [docs/prompt_evaluation/README.md](prompt_evaluation/README.md)

Prompt Evaluation — изолированная подсистема для A/B-тестирования промптов и принятия инженерных решений о замене production-промптов.

---

### Judge Prompt

**Контекст:** Prompt Evaluation (HRA-EXP-V1)

**Модель:** gpt-4.1-2025-04-14

**Temperature:** 0

**Назначение:** Создание эталонной оценки (reference scoring) для сравнения промптов. Не используется в production.

**Формат ответа:** JSON Schema (vacancy_match_result)

**Особенности:**
- Детальные инструкции по каждому критерию
- Максимум объективности
- Используется только в исследованиях

**Статус:** Experimental

**SSOT:** [prompt_evaluation/PROMPTS.md](prompt_evaluation/PROMPTS.md#judge-prompt)

---

### Prompt B (Experimental)

**Контекст:** Prompt Evaluation (HRA-EXP-V1)

**Модель:** gpt-4o-mini-2024-07-18

**Temperature:** 0

**Назначение:** Экспериментальный промпт для тестирования гипотезы о том, что детальные инструкции и few-shot примеры улучшают качество скоринга.

**Формат ответа:** JSON Schema (vacancy_match_result)

**Особенности:**
- Детальные шкалы оценки для каждого критерия
- Few-shot примеры для всех типов кейсов (obvious_match, obvious_no_match, borderline)
- Явные правила и обоснования
- Структурированные таблицы весов
- Длина: ~3000 символов (vs ~480 символов у Prompt A)

**Результат эксперимента HRA-EXP-V1:**

**Решение:** REJECT PROMPT B

**Причина:** MAE увеличился на 52.86% вместо улучшения минимум на 20%.

**Подробный анализ:** [prompt_evaluation/AB_TEST_REPORT.md](prompt_evaluation/AB_TEST_REPORT.md)

**Статус:** Experimental

**Результат:** REJECT

**SSOT:** [prompt_evaluation/PROMPTS.md](prompt_evaluation/PROMPTS.md#prompt-b-experimental)

---

## Сравнение промптов

| Аспект | Judge | Prompt A (Production) | Prompt B (Experimental) |
|--------|-------|----------------------|------------------------|
| **Модель** | gpt-4.1 | gpt-4o-mini | gpt-4o-mini |
| **Temperature** | 0 | 0 | 0 |
| **Длина** | 2073 символов | 480 символов | 3000 символов |
| **Структура** | Детальная | Краткая | Детальная |
| **Примеры (few-shot)** | Нет | Нет | Да (3 примера) |
| **Явные веса** | Детализированы | Упомянуты | Да (таблица) |
| **Назначение** | Reference | Production | Experimental |
| **Результат HRA-EXP-V1** | — | **MAE: 10.30** | MAE: 15.74 |

---

## Как безопасно изменять промпты

### Рекомендуемый процесс

**Принцип:** Изменения в production-промпты должны проходить через экспериментальный контур Prompt Evaluation.

---

### Шаг 1: Подготовка эксперимента

1. Создать датасет для тестирования (или использовать существующий)
2. Определить метрики успеха (MAE, Accuracy, Latency)
3. Установить минимальный порог улучшения (например, -20% MAE)
4. Подготовить новый промпт (Prompt B)

---

### Шаг 2: Проведение эксперимента

**Подробная инструкция:** [prompt_evaluation/REPRODUCIBILITY.md](prompt_evaluation/REPRODUCIBILITY.md)

1. Запустить Judge Run для создания эталонных оценок
2. Запустить Prompt A Run (baseline)
3. Запустить Prompt B Run (candidate)
4. Собрать метрики

---

### Шаг 3: Анализ результатов

1. Вычислить MAE для каждого промпта
2. Сравнить с Judge (reference)
3. Проанализировать распределение ошибок
4. Проверить сегментный анализ

**Пример анализа:** [prompt_evaluation/SEGMENT_ANALYSIS.md](prompt_evaluation/SEGMENT_ANALYSIS.md)

---

### Шаг 4: Принятие решения

**Критерии принятия:**

| Условие | Решение |
|---------|---------|
| MAE(B) < MAE(A) × 0.8 | ACCEPT |
| MAE(B) >= MAE(A) × 0.8 | REJECT |
| Accuracy(B) > Accuracy(A) | Усиление решения |
| Latency(B) < Latency(A) | Бонус |

**Документирование решения:** [prompt_evaluation/AB_TEST_REPORT.md](prompt_evaluation/AB_TEST_REPORT.md)

---

### Шаг 5: Развёртывание в production

Если решение ACCEPT:

1. Обновить промпт в workflow
2. Обновить документацию [AI_QUALIFICATION.md](AI_QUALIFICATION.md)
3. Добавить запись в [CHANGE_LOG.md](CHANGE_LOG.md)
4. Провести smoke-тестирование
5. Мониторить метрики в течение 24 часов

---

### Контролируемые переменные

При A/B-тестировании **всегда** контролируйте:

| Переменная | Значение |
|------------|----------|
| Модель | Одинаковая для Prompt A и Prompt B |
| Temperature | Одинаковая (обычно 0) |
| Датасет | Одинаковый |
| JSON Schema | Одинаковая |
| Prompt Text | Разный |

**Изменяется только текст промпта.**

---

### Типичные ошибки

**❌ Ошибка:** Изменять промпт напрямую в production

**✅ Правильно:** Провести A/B-тестирование через Prompt Evaluation

---

**❌ Ошибка:** Тестировать на разных датасетах

**✅ Правильно:** Использовать одинаковый датасет для всех прогонов

---

**❌ Ошибка:** Не документировать результаты

**✅ Правильно:** Создать отчёт в AB_TEST_REPORT.md

---

**❌ Ошибка:** Игнорировать latency

**✅ Правильно:** Учитывать latency как часть метрик

---

## Стоимость промптов

### Токены на запрос

| Промпт | Input токенов | Output токенов | Total | Стоимость (GPT-4o-mini) |
|--------|---------------|----------------|-------|------------------------|
| Candidate Extraction | ~1000 | ~500 | ~1500 | ~$0.002 |
| JSON Repair | ~1000 | ~500 | ~1500 | ~$0.002 |
| Matching | ~500 | ~300 | ~800 | ~$0.001 |
| **Итого (без ремонта, 1 вакансия)** | | | | **~$0.003** |
| **Итого (с ремонтом, 3 вакансии)** | | | | **~$0.006** |

**Подробнее:** [AI_QUALIFICATION.md](AI_QUALIFICATION.md#5-стоимость)

---

## Метрики качества

### Production-метрики

| Метрика | Значение | Источник |
|---------|----------|----------|
| Полнота извлечения (recall) | Данные в production | [AI_QUALIFICATION.md](AI_QUALIFICATION.md#6-мониторинг-качества) |
| Точность извлечения (precision) | Данные в production | [AI_QUALIFICATION.md](AI_QUALIFICATION.md#6-мониторинг-качества) |
| F1-score | Данные в production | [AI_QUALIFICATION.md](AI_QUALIFICATION.md#6-мониторинг-качества) |
| Accuracy (matching) | Данные в production | [AI_QUALIFICATION.md](AI_QUALIFICATION.md#6-мониторинг-качества) |

---

### Экспериментальные метрики

Для получения актуальных результатов экспериментов см. [prompt_evaluation/AB_TEST_REPORT.md](prompt_evaluation/AB_TEST_REPORT.md).

**Как провести новый эксперимент:** [prompt_evaluation/REPRODUCIBILITY.md](prompt_evaluation/REPRODUCIBILITY.md)

---

## Документация промптов

### SSOT для промптов

| Промпт | SSOT |
|--------|------|
| Candidate Extraction | [AI_QUALIFICATION.md](AI_QUALIFICATION.md#1-извлечение-данных-кандидата) |
| JSON Repair | [AI_QUALIFICATION.md](AI_QUALIFICATION.md#2-ремонт-невалидного-json) |
| Matching (Prompt A) | [AI_QUALIFICATION.md](AI_QUALIFICATION.md#3-matching-кандидата-с-вакансиями) |
| Judge | [prompt_evaluation/PROMPTS.md](prompt_evaluation/PROMPTS.md#judge-prompt) |
| Prompt B | [prompt_evaluation/PROMPTS.md](prompt_evaluation/PROMPTS.md#prompt-b-experimental) |

---

### История экспериментов

**HRA-EXP-V1:** Сравнение Prompt A и Prompt B

**Дата:** 2026-06-24

**Результат:** REJECT Prompt B (MAE +52.86%)

**Отчёт:** [prompt_evaluation/AB_TEST_REPORT.md](prompt_evaluation/AB_TEST_REPORT.md)

---

### Как добавить новый эксперимент

1. Создать директорию `database/05-create-experiment-v2.sql`
2. Определить промпты в SQL
3. Подготовить датасет
4. Запустить эксперимент по [REPRODUCIBILITY.md](prompt_evaluation/REPRODUCIBILITY.md)
5. Задокументировать результаты в AB_TEST_REPORT.md

---

## Связанные документы

- [AI_QUALIFICATION.md](AI_QUALIFICATION.md) — промпты, модели, параметры (SSOT)
- [SUCCESS_METRICS.md](SUCCESS_METRICS.md) — метрики успеха
- [prompt_evaluation/README.md](prompt_evaluation/README.md) — подсистема Prompt Evaluation
- [prompt_evaluation/PROMPTS.md](prompt_evaluation/PROMPTS.md) — полные промпты (SSOT)
- [prompt_evaluation/AB_TEST_REPORT.md](prompt_evaluation/AB_TEST_REPORT.md) — отчёт HRA-EXP-V1

---

**Статус документа:** Production-ready
**Последнее обновление:** 2026-06-27