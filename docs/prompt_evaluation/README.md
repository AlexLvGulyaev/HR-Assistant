# Prompt Evaluation

**Подсистема A/B-тестирования промптов в HR Assistant**

---

## Назначение

Prompt Evaluation — это изолированная подсистема для исследования качества промптов и принятия инженерных решений о замене production-промптов.

**Ключевые возможности:**

- A/B-тестирование промптов
- Сравнение с эталонной оценкой (Judge)
- Метрики качества (MAE, Accuracy, Latency)
- Воспроизводимость экспериментов
- Документирование решений

---

## Документация

### Основные документы

| Документ | Назначение |
|----------|------------|
| [**AB_TEST_REPORT.md**](./AB_TEST_REPORT.md) | Полный отчёт по эксперименту HRA-EXP-V1 |
| [**DATASET.md**](./DATASET.md) | Датасет HRA-EVAL-V1: вакансии и кандидаты |
| [**PROMPTS.md**](./PROMPTS.md) | Промпты: Judge, Prompt A, Prompt B |

### Архитектура и методология

| Документ | Назначение |
|----------|------------|
| [**EVALUATION_SUBSYSTEM.md**](./EVALUATION_SUBSYSTEM.md) | Архитектура подсистемы Prompt Evaluation |
| [**WORKFLOW_DESIGN.md**](./WORKFLOW_DESIGN.md) | Проектирование workflow |
| [**WORKFLOW_IMPLEMENTATION.md**](./WORKFLOW_IMPLEMENTATION.md) | Реализация workflow |

### Исследования и анализ

| Документ | Назначение |
|----------|------------|
| [**SEGMENT_ANALYSIS.md**](./SEGMENT_ANALYSIS.md) | Анализ результатов по сегментам |
| [**TECHNICAL_FOUNDATION.md**](./TECHNICAL_FOUNDATION.md) | Технические детали эксперимента |
| [**VISUALIZATIONS.md**](./VISUALIZATIONS.md) | Диаграммы и схемы |

### Практические руководства

| Документ | Назначение |
|----------|------------|
| [**REPRODUCIBILITY.md**](./REPRODUCIBILITY.md) | Пошаговая инструкция воспроизведения эксперимента |

---

## Порядок чтения

### Для понимания подсистемы

1. [EVALUATION_SUBSYSTEM.md](./EVALUATION_SUBSYSTEM.md) — что это за подсистема
2. [VISUALIZATIONS.md](./VISUALIZATIONS.md) — диаграммы архитектуры
3. [DATASET.md](./DATASET.md) — как устроен датасет
4. [PROMPTS.md](./PROMPTS.md) — какие промпты используются

### Для проведения эксперимента

1. [REPRODUCIBILITY.md](./REPRODUCIBILITY.md) — пошаговая инструкция
2. [WORKFLOW_DESIGN.md](./WORKFLOW_DESIGN.md) — как спроектирован workflow
3. [WORKFLOW_IMPLEMENTATION.md](./WORKFLOW_IMPLEMENTATION.md) — как реализован workflow

### Для анализа результатов

1. [AB_TEST_REPORT.md](./AB_TEST_REPORT.md) — полный отчёт по эксперименту
2. [SEGMENT_ANALYSIS.md](./SEGMENT_ANALYSIS.md) — анализ по сегментам
3. [TECHNICAL_FOUNDATION.md](./TECHNICAL_FOUNDATION.md) — технические детали

---

## Результат HRA-EXP-V1

**Решение:** `REJECT PROMPT B`

**Причина:** MAE увеличился на 52.86% вместо улучшения минимум на 20%.

**Подробнее:** См. [AB_TEST_REPORT.md](./AB_TEST_REPORT.md)

---

## Связь с остальной документацией

| Документ | Связь |
|----------|-------|
| [../SPEC.md](../SPEC.md) | Спецификация HR Assistant |
| [../ARCHITECTURE.md](../ARCHITECTURE.md) | Общая архитектура |
| [../README.md](../README.md) | Главная страница проекта |

---

*Документация подсистемы Prompt Evaluation*