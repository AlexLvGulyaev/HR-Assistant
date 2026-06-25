# HRA-EXP-V1: A/B Testing Matching Prompt

**Experiment Report**

| Attribute | Value |
|------------|-------|
| **Experiment Code** | HRA-EXP-V1 |
| **Dataset** | HRA-EVAL-V1 |
| **Date** | 2026-06-25 |
| **Status** | Completed |
| **Decision** | **REJECT PROMPT B** |

---

## 1. Краткое резюме

### Цель

A/B-тестирование matching prompt для определения возможности замены production prompt (Prompt A) на experimental prompt (Prompt B) в HR Assistant.

### Результаты

| Metric | Prompt A | Prompt B | Δ |
|--------|----------|----------|---|
| **MAE** | 10.30 | 15.74 | +52.86% |
| **Accuracy** | 95.56% | 94.44% | -1.12 pp |
| **Latency** | 2,050 ms | 2,241 ms | +9.34% |

### Decision

```
REJECT PROMPT B
```

**Reason:** Primary metric threshold not met. MAE increased by 52.86% instead of improving by at least 20%.

---

## 2. Background

**Полное описание подсистемы:** см. [EVALUATION_SUBSYSTEM.md](./EVALUATION_SUBSYSTEM.md)

HR Assistant — система автоматизации подбора кандидатов на вакансии. Matching prompt — ключевой компонент, оценивающий соответствие кандидата вакансии.

Production matching prompt (Prompt A) работает в продакшене, но его качество не было систематически измерено. Гипотеза: детальный промпт с few-shot примерами (Prompt B) улучшит качество скоринга.

---

## 3. SMART-гипотеза

### Specific (Конкретность)

Детальный промпт с явными шкалами оценки и few-shot примерами (Prompt B) покажет более точные результаты по сравнению с кратким production промптом (Prompt A).

### Measurable (Измеримость)

| Метрика | Цель |
|--------|--------|
| Улучшение MAE | ≥ 20% |
| Рост Latency | ≤ 30% |

### Achievable (Достижимость)

- Датасет: 90 пар кандидат-вакансия
- Модели: gpt-4o-mini для A/B, gpt-4.1 для Judge
- Инфраструктура: PostgreSQL + n8n workflow

### Relevant (Релевантность)

Качество matching напрямую влияет на удовлетворённость HR-специалистов и репутацию продукта.

### Time-Bound (Ограниченность во времени)

- Подготовка датасета: 1 день
- Реализация workflow: 1 день
- Выполнение эксперимента: ~10 минут

---

## 4. Дизайн эксперимента

### Датасет

**Полное описание:** см. [DATASET.md](./DATASET.md)

| Parameter | Value |
|-----------|-------|
| **Code** | HRA-EVAL-V1 |
| **Size** | 30 candidates × 3 vacancies = 90 pairs |
| **Types** | obvious_match (30), obvious_no_match (30), borderline (30) |

### Модели

**Полное описание промптов:** см. [PROMPTS.md](./PROMPTS.md)

| Run | Model | Temperature | Purpose |
|-----|-------|-------------|---------|
| **Judge** | gpt-4.1-2025-04-14 | 0 | Reference scoring |
| **Prompt A** | gpt-4o-mini-2024-07-18 | 0 | Production prompt |
| **Prompt B** | gpt-4o-mini-2024-07-18 | 0 | Experimental prompt |

### Конвейер оценки

**Полное описание workflow:** см. [WORKFLOW_DESIGN.md](./WORKFLOW_DESIGN.md) и [WORKFLOW_IMPLEMENTATION.md](./WORKFLOW_IMPLEMENTATION.md)

```
Phase 0: Validation
Phase 1: Judge Run (gpt-4.1)
Phase 2: Prompt A Run (gpt-4o-mini)
Phase 3: Prompt B Run (gpt-4o-mini)
Phase 4: Calculate Metrics
Phase 5: Generate Report
```

---

## 5. Варианты промптов

**Полное описание:** см. [PROMPTS.md](./PROMPTS.md)

| Промпт | Назначение | Модель | Длина |
|--------|------------|--------|-------|
| **Judge** | Reference scoring | gpt-4.1-2025-04-14 | 2073 символов |
| **Prompt A** | Production matching | gpt-4o-mini-2024-07-18 | 480 символов |
| **Prompt B** | Experimental matching | gpt-4o-mini-2024-07-18 | 3000 символов |

### Ключевые различия

| Аспект | Prompt A | Prompt B |
|--------|----------|----------|
| **Структура** | Краткий список критериев | Детальные шкалы оценки |
| **Примеры** | Нет | 3 few-shot примера |
| **Веса** | Упомянуты, не детализированы | Явная таблица |
| **Правила** | Краткие | Детальные с примерами |

---

## 6. Результаты

### Финальные значения (из Production Database)

| Metric | Prompt A | Prompt B | Δ |
|--------|----------|----------|---|
| **MAE** | 10.30 | 15.74 | +52.86% |
| **Accuracy** | 95.56% (86/90) | 94.44% (85/90) | -1.12 pp |
| **Latency** | 2,049.77 ms | 2,241.19 ms | +9.34% |

### Анализ метрик

| Метрика | Значение | Порог | Статус |
|--------|-------|-----------|--------|
| **Улучшение MAE** | -52.86% | ≥ 20% | ❌ **FAIL** |
| **Рост Latency** | +9.34% | ≤ 30% | ✅ PASS |

### Проверка решения

| Критерий | Требуется | Фактически | Результат |
|-----------|----------|--------|--------|
| Улучшение MAE | ≥ 20% | -52.86% | ❌ FAIL |
| Рост Latency | ≤ 30% | 9.34% | ✅ PASS |
| **Финальное решение** | ОБА ПРОЙДЕНЫ | ОДИН FAIL | ❌ **REJECT** |

---

## 7. Анализ

### Почему Prompt B отклонён

**Нарушение Primary Metric:**
- MAE Prompt B увеличился на 52.86% вместо улучшения
- Это означает, что Prompt B **значительно менее точен**, чем Prompt A
- Детальные инструкции и примеры НЕ улучшили скоринг

**Гипотеза опровергнута:**
- Гипотеза: "Детальные промпты с примерами улучшают скоринг"
- Реальность: "Детальные промпты с примерами УХУДШИЛИ точность скоринга"

### Ключевые наблюдения

1. **Prompt B работает хуже на всех сегментах** — см. [SEGMENT_ANALYSIS.md](./SEGMENT_ANALYSIS.md)
2. **Наибольшая деградация на borderline кейсах** — рост MAE на 88.3%
3. **Нет улучшения accuracy на очевидных кейсах**
4. **Latency приемлем** — рост 9.34% в пределах лимитов

### Анализ root cause

**Возможные объяснения:**
1. **Информационная перегрузка** — 3000 символов могут путать модель
2. **Избыточная спецификация** — Детальные рубрики могут ограничивать суждение
3. **Утечка примеров** — Few-shot примеры могут смещать к конкретным паттернам
4. **Ёмкость модели** — gpt-4o-mini может не справляться со сложными промптами

---

## 8. Угрозы валидности

### Внутренняя валидность

| Угроза | Митигация |
|--------|------------|
| Смещение датасета | Сбалансированные типы кейсов (obvious_match, obvious_no_match, borderline) |
| Один Judge | Модель Judge обеспечивает консистентный reference scoring |
| Temperature = 0 | Устраняет случайность, обеспечивает воспроизводимость |
| Одна модель для A/B | Контролируемое сравнение, отличается только текст промпта |

### Внешняя валидность

| Угроза | Митигация |
|--------|------------|
| Размер датасета | 90 пар обеспечивает разумную статистическую мощность |
| Разнообразие кандидатов | 30 кандидатов по 3 типам кейсов |
| Специфичность вакансий | 3 реальные production вакансии |
| Специфичность модели | gpt-4o-mini репрезентативна для задач matching |

### Конструктная валидность

| Угроза | Митигация |
|--------|------------|
| MAE как прокси качества | MAE напрямую измеряет отклонение от reference |
| Judge как ground truth | Модель Judge обучена давать экспертную оценку |
| Один порог решения | Порог 60 — production стандарт |

---

## 9. Production-решение

```
REJECT PROMPT B
```

### Обоснование решения

**Основная причина:** Порог улучшения MAE не достигнут. Prompt B работает значительно хуже, чем Prompt A.

**Подтверждающие доказательства:**
- MAE увеличился на 52.86%
- Accuracy снизилась на 1.12 процентных пункта
- Гипотеза о том, что детальные промпты улучшают скоринг, не подтвердилась

**Guard Metric:** Рост Latency на 9.34% приемлем, но не имеет значения, так как primary metric не пройдена.

### Рекомендация

1. **Продолжать использовать Prompt A** в production
2. **Не заменять** на Prompt B
3. **Рассмотреть альтернативные подходы**:
   - Другая модель (gpt-4.1 вместо gpt-4o-mini)
   - Другая структура промпта
   - Гибридный подход (ансамбль)

---

## 10. Как запустить HRA-EXP-V2

**Полная инструкция:** см. [REPRODUCIBILITY.md](./REPRODUCIBILITY.md)

### Что МОЖНО менять

- Текст Prompt B (новый экспериментальный промпт)
- Модель Prompt B (например, gpt-4.1 вместо gpt-4o-mini)
- Датасет (создать HRA-EVAL-V2)

### Что НЕЛЬЗЯ менять

- Модель Judge (gpt-4.1)
- Промпт Judge
- Модель Prompt A
- Промпт Prompt A
- Temperature (0 для всех моделей)
- Primary metric (MAE)
- Guard metric (Latency)
- Критерии принятия

### Быстрый старт

```sql
-- Create new experiment
INSERT INTO eval_prompt_experiments (...)
VALUES ('HRA-EXP-V2', ...);
```

```javascript
// Configure workflow
return [{
  json: {
    experiment_code: 'HRA-EXP-V2',
    dataset_code: 'HRA-EVAL-V1',  // or V2
    expected_pairs: 90
  }
}];
```

---

## Ссылки

1. **Архитектура подсистемы:** [EVALUATION_SUBSYSTEM.md](./EVALUATION_SUBSYSTEM.md)
2. **Датасет:** [DATASET.md](./DATASET.md)
3. **Промпты:** [PROMPTS.md](./PROMPTS.md)
4. **Проектирование workflow:** [WORKFLOW_DESIGN.md](./WORKFLOW_DESIGN.md)
5. **Реализация workflow:** [WORKFLOW_IMPLEMENTATION.md](./WORKFLOW_IMPLEMENTATION.md)
6. **Сегментный анализ:** [SEGMENT_ANALYSIS.md](./SEGMENT_ANALYSIS.md)
7. **Визуализации:** [VISUALIZATIONS.md](./VISUALIZATIONS.md)
8. **Инструкция воспроизведения:** [REPRODUCIBILITY.md](./REPRODUCIBILITY.md)
9. **Технические детали:** [TECHNICAL_FOUNDATION.md](./TECHNICAL_FOUNDATION.md)

---

*Отчёт сгенерирован: 2026-06-25*
*Эксперимент: HRA-EXP-V1*
*Решение: REJECT PROMPT B*