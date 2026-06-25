# Success Metrics: HR Assistant

**Полный справочник метрик успеха проекта HR Assistant.**

---

## Как использовать этот документ

Этот документ объединяет все метрики проекта в одном месте. Каждая метрика ссылается на SSOT (Source of Truth) для получения детальной информации.

---

## Business Metrics

### Время обработки резюме

| Метрика | До | После | Изменение | SSOT |
|---------|----|----|-----------|------|
| **Время на анализ резюме** | 10-15 минут | < 1 минута | 10-15x | [BUSINESS_VALUE.md](BUSINESS_VALUE.md#измеримый-эффект) |

**Целевое значение:** < 1 минута

**Как измеряется:**
```sql
SELECT AVG(EXTRACT(EPOCH FROM (fd.created_at - ci.created_at))) as avg_seconds
FROM final_decisions fd
JOIN candidates c ON c.id = fd.candidate_id
JOIN candidate_inputs ci ON ci.id = c.source_input_id
WHERE fd.created_at > NOW() - INTERVAL '1 hour';
```

---

### Форматы ввода

| Метрика | До | После | Изменение | SSOT |
|---------|----|----|-----------|------|
| **Форматы ввода** | 1 (текст/документ) | 4 (текст, голос, документ, изображение) | 4x | [BUSINESS_VALUE.md](BUSINESS_VALUE.md#измеримый-эффект) |

**Целевое значение:** 4 формата

**Поддерживаемые форматы:**
- Текст (прямой ввод в Telegram)
- Голос (аудио сообщение)
- Документ (PDF, DOCX)
- Изображение (фото резюме)

---

### Автоматизация

| Метрика | До | После | Изменение | SSOT |
|---------|----|----|-----------|------|
| **Извлечение данных** | Вручную | Автоматически (AI) | 100% авто | [BUSINESS_VALUE.md](BUSINESS_VALUE.md#измеримый-эффект) |
| **Matching** | Вручную | Автоматически (AI) | 100% авто | [BUSINESS_VALUE.md](BUSINESS_VALUE.md#измеримый-эффект) |

**Целевое значение:** 100% автоматизация

---

### Конверсия по форматам

| Формат | Конверсия | SSOT |
|--------|-----------|------|
| Текст | Данные в production | [AUTOMATION_PASSPORT.md](AUTOMATION_PASSPORT.md#метрики) |
| Голос | Данные в production | [AUTOMATION_PASSPORT.md](AUTOMATION_PASSPORT.md#метрики) |
| Документ | Данные в production | [AUTOMATION_PASSPORT.md](AUTOMATION_PASSPORT.md#метрики) |
| Изображение | Данные в production | [AUTOMATION_PASSPORT.md](AUTOMATION_PASSPORT.md#метрики) |

**Как измеряется:**
```sql
SELECT
  input_type,
  COUNT(*) as count,
  ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) as percentage
FROM candidate_inputs
WHERE created_at > NOW() - INTERVAL '7 days'
GROUP BY input_type;
```

---

### Score distribution

**Распределение кандидатов по score:**

```sql
SELECT
  CASE
    WHEN score >= 80 THEN 'high (80-100)'
    WHEN score >= 60 THEN 'medium (60-79)'
    WHEN score >= 40 THEN 'low (40-59)'
    ELSE 'very_low (0-39)'
  END as score_range,
  decision,
  COUNT(*) as count
FROM matches
GROUP BY score_range, decision
ORDER BY score_range;
```

**Целевое распределение:**
- High (80-100): 20-30% кандидатов
- Medium (60-79): 30-40% кандидатов
- Low (40-59): 20-30% кандидатов
- Very low (0-39): 10-20% кандидатов

**SSOT:** [AI_QUALIFICATION.md](AI_QUALIFICATION.md#6-мониторинг-качества)

---

## Technical Metrics

### Latency

| Метрика | Целевое значение | SSOT |
|---------|-----------------|------|
| **Среднее время ответа (текст)** | < 30 сек | [AUTOMATION_PASSPORT.md](AUTOMATION_PASSPORT.md#ключевые-метрики) |
| **Среднее время ответа (голос)** | < 60 сек | [AUTOMATION_PASSPORT.md](AUTOMATION_PASSPORT.md#ключевые-метрики) |
| **Среднее время ответа (документ)** | < 60 сек | [AUTOMATION_PASSPORT.md](AUTOMATION_PASSPORT.md#ключевые-метрики) |
| **Среднее время ответа (изображение)** | < 90 сек | [AUTOMATION_PASSPORT.md](AUTOMATION_PASSPORT.md#ключевые-метрики) |

**Как измеряется:**
```sql
SELECT
  ci.input_type,
  AVG(EXTRACT(EPOCH FROM (fd.created_at - ci.created_at))) as avg_seconds
FROM final_decisions fd
JOIN candidates c ON c.id = fd.candidate_id
JOIN candidate_inputs ci ON ci.id = c.source_input_id
WHERE fd.created_at > NOW() - INTERVAL '1 hour'
GROUP BY ci.input_type;
```

---

### Availability

| Метрика | Целевое значение | SSOT |
|---------|-----------------|------|
| **Доступность (SLA)** | 99% | [AUTOMATION_PASSPORT.md](AUTOMATION_PASSPORT.md#ключевые-метрики) |

**Как измеряется:**
- Uptime мониторинг (n8n, PostgreSQL, Telegram Bot)
- Healthcheck endpoints
- Логи ошибок

---

### Workflow Success Rate

| Метрика | Целевое значение | SSOT |
|---------|-----------------|------|
| **HR Intake success rate** | > 99% | [SUPPORT_RUNBOOK.md](SUPPORT_RUNBOOK.md#мониторинг) |
| **Processing Worker success rate** | > 95% | [SUPPORT_RUNBOOK.md](SUPPORT_RUNBOOK.md#мониторинг) |
| **Delivery Worker success rate** | > 99% | [SUPPORT_RUNBOOK.md](SUPPORT_RUNBOOK.md#мониторинг) |

**Как измеряется:**
```sql
-- Ошибки за час
SELECT
  COUNT(*) FILTER (WHERE status = 'error') as errors,
  COUNT(*) FILTER (WHERE status = 'success') as successes,
  ROUND(COUNT(*) FILTER (WHERE status = 'success') * 100.0 / COUNT(*), 2) as success_rate
FROM processing_logs
WHERE created_at > NOW() - INTERVAL '1 hour';
```

---

### JSON Validity

| Метрика | Целевое значение | SSOT |
|---------|-----------------|------|
| **Валидность JSON (извлечение)** | > 95% | [AI_QUALIFICATION.md](AI_QUALIFICATION.md#1-извлечение-данных-кандидата) |
| **Валидность JSON (matching)** | > 99% | [AI_QUALIFICATION.md](AI_QUALIFICATION.md#3-matching-кандидата-с-вакансиями) |

**Fallback:** Если JSON невалиден → JSON Repair → Processing Error

---

### Эксплуатационные показатели

| Метрика | Порог | Действие | SSOT |
|---------|-------|----------|------|
| **Processing time > 60 sec** | Warning | Проверить OpenAI API | [AUTOMATION_PASSPORT.md](AUTOMATION_PASSPORT.md#мониторинг-и-алертинг) |
| **Error rate > 5%** | Critical | Проверить логи | [AUTOMATION_PASSPORT.md](AUTOMATION_PASSPORT.md#мониторинг-и-алертинг) |
| **Queue backlog > 100** | Warning | Проверить Workers | [AUTOMATION_PASSPORT.md](AUTOMATION_PASSPORT.md#мониторинг-и-алертинг) |
| **DB connections > 80%** | Critical | Проверить PostgreSQL | [AUTOMATION_PASSPORT.md](AUTOMATION_PASSPORT.md#мониторинг-и-алертинг) |

---

## Prompt Engineering Metrics

### Эксперимент HRA-EXP-V1

**Подсистема:** Prompt Evaluation

**Документация:** [prompt_evaluation/AB_TEST_REPORT.md](prompt_evaluation/AB_TEST_REPORT.md)

---

### MAE (Mean Absolute Error)

| Промпт | MAE | Изменение vs Judge | SSOT |
|--------|-----|-------------------|------|
| **Prompt A (Production)** | 10.30 | Baseline | [prompt_evaluation/AB_TEST_REPORT.md](prompt_evaluation/AB_TEST_REPORT.md) |
| **Prompt B (Experimental)** | 15.74 | +52.86% | [prompt_evaluation/AB_TEST_REPORT.md](prompt_evaluation/AB_TEST_REPORT.md) |

**Целевое значение:** MAE < 10

**MDE (Minimum Detectable Effect):** -20% (улучшение минимум на 20%)

**Результат:** REJECT Prompt B (MAE увеличился вместо улучшения)

---

### Accuracy

| Промпт | Accuracy | Изменение | SSOT |
|--------|----------|-----------|------|
| **Prompt A** | 70% | Baseline | [prompt_evaluation/AB_TEST_REPORT.md](prompt_evaluation/AB_TEST_REPORT.md) |
| **Prompt B** | 50% | -20 pp | [prompt_evaluation/AB_TEST_REPORT.md](prompt_evaluation/AB_TEST_REPORT.md) |

**Accuracy** — доля случаев, когда decision промпта совпадает с decision Judge.

---

### Guard Metrics

| Метрика | Prompt A | Prompt B | SSOT |
|---------|----------|----------|------|
| **JSON validity** | 100% | 100% | [prompt_evaluation/TECHNICAL_FOUNDATION.md](prompt_evaluation/TECHNICAL_FOUNDATION.md) |
| **Score range** | 0-100 | 0-100 | [prompt_evaluation/TECHNICAL_FOUNDATION.md](prompt_evaluation/TECHNICAL_FOUNDATION.md) |
| **Decision valid** | 100% | 100% | [prompt_evaluation/TECHNICAL_FOUNDATION.md](prompt_evaluation/TECHNICAL_FOUNDATION.md) |

**Guard Metrics** — метрики, которые должны быть 100% для валидности эксперимента.

---

### Latency

| Промпт | Latency | Изменение | SSOT |
|--------|---------|-----------|------|
| **Prompt A** | 1.2s | Baseline | [prompt_evaluation/AB_TEST_REPORT.md](prompt_evaluation/AB_TEST_REPORT.md) |
| **Prompt B** | 1.8s | +50% | [prompt_evaluation/AB_TEST_REPORT.md](prompt_evaluation/AB_TEST_REPORT.md) |

**Latency** — время ответа модели на один запрос.

---

### Acceptance Criteria

| Критерий | Порог | Результат HRA-EXP-V1 |
|----------|-------|---------------------|
| **MAE** | < MAE(A) × 0.8 | ❌ MAE(B) = 15.74 > 10.30 × 0.8 = 8.24 |
| **Accuracy** | > Accuracy(A) | ❌ Accuracy(B) = 50% < 70% |
| **Latency** | < Latency(A) | ❌ Latency(B) = 1.8s > 1.2s |

**Итог:** Все критерии не выполнены → REJECT

---

### Связь с Prompt Evaluation

**Подсистема Prompt Evaluation:**

| Компонент | Назначение | Документация |
|-----------|-----------|--------------|
| **Judge** | Создание эталонных оценок | [prompt_evaluation/PROMPTS.md](prompt_evaluation/PROMPTS.md#judge-prompt) |
| **Prompt A** | Production промпт | [prompt_evaluation/PROMPTS.md](prompt_evaluation/PROMPTS.md#prompt-a-production) |
| **Prompt B** | Experimental промпт | [prompt_evaluation/PROMPTS.md](prompt_evaluation/PROMPTS.md#prompt-b-experimental) |
| **Dataset** | HRA-EVAL-V1 | [prompt_evaluation/DATASET.md](prompt_evaluation/DATASET.md) |
| **Report** | AB_TEST_REPORT.md | [prompt_evaluation/AB_TEST_REPORT.md](prompt_evaluation/AB_TEST_REPORT.md) |

**Как провести эксперимент:** [prompt_evaluation/REPRODUCIBILITY.md](prompt_evaluation/REPRODUCIBILITY.md)

---

## Dashboard

### Где смотреть метрики

**SQL-запросы:**

| Метрика | SQL | SSOT |
|---------|-----|------|
| **Количество обработанных за час** | `SELECT COUNT(*) FROM final_decisions WHERE created_at > NOW() - INTERVAL '1 hour'` | [SUPPORT_RUNBOOK.md](SUPPORT_RUNBOOK.md#sql-запросы-для-мониторинга) |
| **Среднее время обработки** | `SELECT AVG(EXTRACT(EPOCH FROM (fd.created_at - ci.created_at))) ...` | [SUPPORT_RUNBOOK.md](SUPPORT_RUNBOOK.md#sql-запросы-для-мониторинга) |
| **Ошибки за час** | `SELECT COUNT(*) FROM processing_logs WHERE status = 'error' AND created_at > NOW() - INTERVAL '1 hour'` | [SUPPORT_RUNBOOK.md](SUPPORT_RUNBOOK.md#sql-запросы-для-мониторинга) |
| **Зависшие обработки** | `SELECT COUNT(*) FROM candidate_inputs WHERE processing_status = 'processing_started'` | [SUPPORT_RUNBOOK.md](SUPPORT_RUNBOOK.md#sql-запросы-для-мониторинга) |

---

### n8n Logs

```bash
# Логи n8n
docker compose -f docker-compose.n8n.yml logs n8n

# Логи PostgreSQL
docker compose -f docker-compose.db.yml logs postgres
```

---

### Processing Logs

**Таблица:** `processing_logs`

**Поля:**
- `id` — идентификатор
- `execution_id` — идентификатор выполнения
- `stage` — этап (intake, processing, delivery)
- `status` — статус (success, error)
- `error_text` — текст ошибки
- `created_at` — время

**SQL:**
```sql
SELECT stage, status, error_text, created_at
FROM processing_logs
WHERE created_at > NOW() - INTERVAL '1 hour'
ORDER BY created_at DESC;
```

---

### Prompt Evaluation Dashboard

**Отчёты Prompt Evaluation:**

| Отчёт | Назначение | SSOT |
|-------|-----------|------|
| **AB_TEST_REPORT.md** | Полный отчёт по эксперименту | [prompt_evaluation/AB_TEST_REPORT.md](prompt_evaluation/AB_TEST_REPORT.md) |
| **SEGMENT_ANALYSIS.md** | Анализ по сегментам | [prompt_evaluation/SEGMENT_ANALYSIS.md](prompt_evaluation/SEGMENT_ANALYSIS.md) |
| **TECHNICAL_FOUNDATION.md** | Технические детали | [prompt_evaluation/TECHNICAL_FOUNDATION.md](prompt_evaluation/TECHNICAL_FOUNDATION.md) |

---

## Интерпретация результатов

### Целевые показатели

| Метрика | Целевое значение | Порог внимания | Критический порог |
|---------|-----------------|----------------|-------------------|
| **Время обработки** | < 60 сек | > 60 сек | > 90 сек |
| **Доступность** | 99% | < 99% | < 95% |
| **Success rate** | > 95% | < 95% | < 90% |
| **Error rate** | < 5% | > 5% | > 10% |
| **Queue backlog** | < 10 | > 50 | > 100 |

---

### Показатели, требующие внимания

**Если вы наблюдаете:**

| Симптом | Возможная причина | Действие | SSOT |
|---------|------------------|----------|------|
| **Processing time > 60 сек** | OpenAI API latency | Проверить status.openai.com | [SUPPORT_RUNBOOK.md](SUPPORT_RUNBOOK.md#инцидент-2-openai-api-недоступен) |
| **Error rate > 5%** | Ошибки в workflow | Проверить processing_logs | [SUPPORT_RUNBOOK.md](SUPPORT_RUNBOOK.md#диагностика) |
| **Queue backlog > 100** | Workers не справляются | Проверить Watchdog | [SUPPORT_RUNBOOK.md](SUPPORT_RUNBOOK.md#проблема-зависшие-записи) |
| **JSON validity < 95%** | Проблемы с промптом | Проверить промпт, запустить ремонт | [AI_QUALIFICATION.md](AI_QUALIFICATION.md#2-ремонт-невалидного-json) |

---

### Критические показатели

**Если вы наблюдаете:**

| Симптом | Критичность | Действие | SSOT |
|---------|-------------|----------|------|
| **Processing time > 90 сек** | 🔴 Critical | Немедленно проверить OpenAI API | [SUPPORT_RUNBOOK.md](SUPPORT_RUNBOOK.md#инцидент-2-openai-api-недоступен) |
| **Availability < 95%** | 🔴 Critical | Проверить все компоненты | [SUPPORT_RUNBOOK.md](SUPPORT_RUNBOOK.md#инцидент-3-база-данных-недоступна) |
| **Error rate > 10%** | 🔴 Critical | Проверить логи, перезапустить Workers | [SUPPORT_RUNBOOK.md](SUPPORT_RUNBOOK.md#диагностика) |
| **MAE > 20** | 🟡 Attention | Провести анализ качества промпта | [PROMPT_ENGINEERING_GUIDE.md](PROMPT_ENGINEERING_GUIDE.md) |

---

## Связанные документы

### Business Metrics

- [BUSINESS_VALUE.md](BUSINESS_VALUE.md) — ценность для бизнеса
- [E2E_SCENARIOS.md](E2E_SCENARIOS.md) — сквозные сценарии

### Technical Metrics

- [AUTOMATION_PASSPORT.md](AUTOMATION_PASSPORT.md) — паспорт автоматизации, TCO, метрики
- [SUPPORT_RUNBOOK.md](SUPPORT_RUNBOOK.md) — диагностика, метрики мониторинга
- [ARCHITECTURE.md](ARCHITECTURE.md) — архитектура системы

### Prompt Engineering Metrics

- [AI_QUALIFICATION.md](AI_QUALIFICATION.md) — промпты, модели, параметры
- [PROMPT_ENGINEERING_GUIDE.md](PROMPT_ENGINEERING_GUIDE.md) — руководство по промпт-инжинирингу
- [prompt_evaluation/README.md](prompt_evaluation/README.md) — подсистема Prompt Evaluation
- [prompt_evaluation/AB_TEST_REPORT.md](prompt_evaluation/AB_TEST_REPORT.md) — отчёт HRA-EXP-V1

---

**Статус документа:** Production-ready
**Последнее обновление:** 2026-06-27