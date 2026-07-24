# Offline Audit: Experiment 003 vs Experiment 002

**Дата:** 2026-07-22  
**Кейс:** HR Assistant (hr-assistant)  
**Модуль:** Fine-tuning / Experimental ML-контур  
**Автор:** VPS Claude Code  
**Статус:** Завершён — рекомендации для Cycle 4

---

## 1. Цель аудита

Определить, почему Experiment 003 не является production-ready, несмотря на прохождение runtime negative smoke test. Найти конкретные failure mode, которые Cycle 4 должен устранить через изменение teacher dataset.

---

## 2. Источники

| Файл | Назначение |
|------|------------|
| `runs/experiment_003/generation_test/generation_test_report.json` | Offline evaluation Experiment 003 на original test set (9 записей) |
| `runs/experiment_002/generation_test/generation_test_report.json` | Базовое сравнение Experiment 002 |
| `runs/experiment_003/runtime_smoke_report.json` | Runtime smoke test (7 кейсов) |
| `data/train.jsonl`, `data/validation.jsonl` | Teacher dataset Experiment 003 |
| `Experiment_003_Report.md` | Спецификация hard negative категорий |

---

## 3. Сводка метрик

| Метрика | Base Qwen (Exp 003) | LoRA Exp 002 | LoRA Exp 003 | Вывод |
|---------|---------------------|--------------|--------------|-------|
| valid_json_rate | 1.0 | 1.0 | 1.0 | Стабильно |
| decision_accuracy | 0.222 | 0.778 | 0.667 | Exp 003 хуже Exp 002 на original test |
| MAE_score | 38.33 | 21.89 | 22.22 | Незначительно выше Exp 002 |
| Runtime negative smoke | — | ❌ Fail | ✅ 7/7 passed | Ключевой успех Exp 003 |

---

## 4. Per-record анализ original test set

### 4.1. Ложные отрицательные решения (false negatives) — главная проблема

| # | case_code | Вакансия | reference | Exp 002 LoRA | Exp 003 LoRA | Дельта score | Причина |
|---|-----------|----------|-----------|--------------|--------------|--------------|---------|
| 1 | HRA-EVAL-V2-000010 | Prompt Engineer / AI Automation Specialist | match (60) | match (70) | **no_match (54)** | −16 | Модель стала резко снижать `role_score` и `skills_score` за отсутствие явных ключевых слов |
| 2 | HRA-EVAL-V2-000010 | Системный аналитик | match (98) | match (97) | **no_match (43)** | −54 | То же: кандидат-системный аналитик с 6-летним опытом теперь оценивается как почти нерелевантный |
| 3 | HRA-EVAL-V2-000030 | Специалист по разметке данных | match (64) | no_match (40) | no_match (45) | +5 | Остался no_match, но score подрос; всё ещё не достигает порога |

**Вывод:** Experiment 003 сильно перестраховывается на кейсах, где профиль смежный, но reference всё равно `match`. Это over-correction после добавления hard negatives.

### 4.2. Правильно отклонённые кейсы — позитивный эффект hard negatives

| # | case_code | Вакансия | reference | Exp 002 LoRA | Exp 003 LoRA | Дельта score | Комментарий |
|---|-----------|----------|-----------|--------------|--------------|--------------|-------------|
| 1 | HRA-EVAL-V2-000010 | Специалист по разметке данных | no_match (39) | no_match (60) | no_match (50) | −10 | Exp 002 был на грани false positive; Exp 003 убрал риск |
| 2 | HRA-EVAL-V2-000020 | Prompt Engineer / AI Automation Specialist | no_match (19) | no_match (57) | no_match (46) | −11 | Оба no_match, но score ближе к reference |
| 3 | HRA-EVAL-V2-000020 | Системный аналитик | no_match (39) | no_match (55) | no_match (45) | −10 | Score ближе к reference |
| 4 | HRA-EVAL-V2-000020 | Специалист по разметке данных | no_match (27) | **match (72)** — false positive | no_match (58) | −14 | **Ключевое исправление:** Exp 002 выдавал match на врача для разметки данных |

### 4.3. Нейтральные кейсы

| case_code | Вакансия | reference | Exp 002 | Exp 003 | Комментарий |
|-----------|----------|-----------|---------|---------|-------------|
| HRA-EVAL-V2-000030 | Prompt Engineer / AI Automation Specialist | no_match (20) | no_match (47) | no_match (42) | Оба корректны, Exp 003 чуть ближе к reference |
| HRA-EVAL-V2-000030 | Системный аналитик | no_match (25) | no_match (40) | no_match (45) | Оба корректны |

---

## 5. Анализ component scores

### Дельты Exp 003 vs Exp 002 по компонентам

| case | Вакансия | Δ role_score | Δ skills_score | Δ experience_score | Δ conditions_score |
|------|----------|--------------|----------------|----------------------|--------------------|
| HRA-EVAL-V2-000010 | Prompt Engineer | −7.0 | −6.0 | −3.0 | 0.0 |
| HRA-EVAL-V2-000010 | Системный аналитик | **−25.0** | **−26.0** | −3.0 | 0.0 |
| HRA-EVAL-V2-000010 | Специалист по разметке | +2.0 | −9.0 | −3.0 | 0.0 |
| HRA-EVAL-V2-000020 | Все вакансии | −1…−8 | −3…−11 | −5.0 | 0.0 |
| HRA-EVAL-V2-000030 | Все вакансии | 0.0 | 0.0 | −5.0 | 0.0 |

**Ключевое наблюдение:**
- `role_score` и `skills_score` резко снизились на смежных, но релевантных профилях (`HRA-EVAL-V2-000010`).
- `experience_score` снизился практически на всех кейсах (−3…−5) — модель начала недооценивать опыт.
- `conditions_score` не изменился — проблема не в зарплате/городе.

**Интерпретация:** hard negative примеры научили модель сильно штрафовать за отсутствие прямых ключевых слов. Это хорошо для нерелевантных профилей, но плохо для смежных ролей, где reference даёт `match`.

---

## 6. Анализ reasoning

### HRA-EVAL-V2-000010 / Системный аналитик — ложный отказ

**Teacher / reference reason (Exp 003):**
> Кандидат полностью соответствует заявленной должности ("Системный аналитик"), совпадение по названию и опыту работы. Все ключевые навыки из требований присутствуют...

**LoRA Exp 003 reason:**
> Кандидат претендует на позицию "системный аналитик", но не указывает явно на аналитические или технические навыки (SQL, BPMN, REST API), что составляет 3 балла. Из требуемых навыков у кандидата только базовые аналитические навыки (агилка, документирование). Зарплатные ожидания кандидата (190 000) значительно выше бюджета вакансии (максимум 220 000)...

**Расхождение:**
- Teacher оценивает профиль как почти идеальный (score 98).
- LoRA игнорирует совпадение по названию должности и заявленные навыки, снижая `role_score` с 28 до 3 и `skills_score` с 34 до 8.
- LoRA неправильно трактует зарплату: 190 000 в диапазоне 150 000–220 000 — это вписывается, а не "значительно выше".

**Вывод:** модель научилась искать **отсутствие** ключевых слов и завышать критичность mismatch, но потеряла способность признавать **наличие** соответствия.

---

## 7. Runtime smoke test — позитивный результат

| case_code | Категория | decision | score | passed |
|-----------|-----------|----------|-------|--------|
| SMOKE-POSITIVE-001 | positive | match | 85.0 | ✅ |
| SMOKE-NEGATIVE-001 | obvious_negative | no_match | 0.0 | ✅ |
| SMOKE-HARDNEG-001 | hard_negative | no_match | 10.0 | ✅ |
| SMOKE-EDGECASE-001 | edge_case | no_match | 0.0 | ✅ |
| SMOKE-HARDNEG-002 | hard_negative | no_match | 10.0 | ✅ |
| SMOKE-INVALID-001 | invalid_input | no_match | 0.0 | ✅ |
| SMOKE-STABILITY-001 | stability_repeat | match | 85.0 | ✅ |

**Вывод:** hard negative примеры работают — runtime negative smoke test пройден стабильно. Это достижение нужно сохранить в Cycle 4.

---

## 8. Анализ состава teacher dataset

### Class balance

| Split | Записей | match | no_match | % match |
|-------|---------|-------|----------|---------|
| train | 93 | 14 | 79 | 15.1% |
| validation | 15 | 3 | 12 | 20.0% |
| train+val | 108 | 17 | 91 | 15.7% |
| test | 9 | 3 | 6 | 33.3% |
| holdout | 6 | 1 | 5 | 16.7% |

**Проблема:** combined train+val имеет всего 15.7% positive примеров. Модель учится преимущественно отказывать.

### Новые hard negative кандидаты

| case_code | Primary category | Split | Записей |
|-----------|------------------|-------|---------|
| HRA-EVAL-V2-000101 | HN-1 | train | 3 |
| HRA-EVAL-V2-000102 | HN-2 / EC-3 | train | 3 |
| HRA-EVAL-V2-000103 | HN-3 / EC-3 | train | 3 |
| HRA-EVAL-V2-000104 | HN-4 | train | 3 |
| HRA-EVAL-V2-000105 | HN-5 | train | 3 |
| HRA-EVAL-V2-000106 | HN-8 | train | 3 |
| HRA-EVAL-V2-000107 | EC-1 / EC-4 | train | 3 |
| HRA-EVAL-V2-000108 | HN-6 | validation | 3 |
| HRA-EVAL-V2-000109 | EC-1 | validation | 3 |
| HRA-EVAL-V2-000110 | HN-7 | holdout | 3 |
| HRA-EVAL-V2-000111 | EC-4 / EC-3 | holdout | 3 |

Все 11 новых кандидатов вносят 33 записи, преимущественно `no_match`. Положительных примеров не добавлено.

---

## 9. Root cause

1. **Дисбаланс в сторону no_match.** train+val содержит 84.3% отказов. Модель минимизирует loss, предсказывая conservative `no_match`.
2. **Hard negatives без компенсирующих positive/borderline примеров.** Новые кейсы учат модель штрафовать за отсутствие ключевых слов, но не учат сохранять positive решения на смежных профилях.
3. **Teacher-prompt mismatch.** System prompt для обучения — production Prompt A, который сам по себе требует `score >= 60` для `match`. LoRA усилила этот пороговый эффект.
4. **Малый test set.** 9 записей не позволяют надёжно измерить recall и calibrate threshold.

---

## 10. Рекомендации для Cycle 4

### 10.1. Пересбалансировать teacher dataset

- **Целевой баланс в train+val:** `match` 30–35% / `no_match` 65–70%. Это требует добавить **15–25 positive/borderline записей** при сохранении 33 hard negatives.
- **Добавить positive примеры для смежных профилей**, которые сейчас ломаются:
  - Системный аналитик с опытом SQL/BPMN/REST API и постановки задач разработчикам → `match` на вакансию "Системный аналитик".
  - Системный аналитик с базовым опытом API/BPMN → `match` на вакансию "Prompt Engineer / AI Automation Specialist" (score около 60).
- **Добавить borderline примеры** с reference score 55–65 и обоими решениями (match/no_match) для калибровки порога.

### 10.2. Сохранить достижения Experiment 003

- Все 11 hard negative кандидатов (`HRA-EVAL-V2-000101`–`HRA-EVAL-V2-000111`) должны остаться в dataset.
- Runtime smoke set (`data/smoke_set.jsonl`) должен остаться без изменений, чтобы не потерять верифицируемость.

### 10.3. Расширить test set

- Увеличить test split до **30–50 записей**, сохранив стратификацию.
- Использовать как исходные 9 записей Experiment 002, так и новые репрезентативные кейсы.

### 10.4. Не менять модель и LoRA

- Базовая модель, LoRA параметры, learning rate, epochs — всё то же, что в Experiment 003.
- Изменяемая переменная — только состав teacher dataset.

### 10.5. Оценить threshold calibration как отдельный шаг

- Если после Cycle 4 offline metrics улучшатся, но decision accuracy всё ещё ниже 0.75, откалибровать порог `score >= 60` на основании распределения score на валидации.
- Это должно делаться после обучения, на валидационной выборке, без leakage в test.

### 10.6. Production-цель: beat GPT-4o-mini

- После Cycle 4 сравнить LoRA и GPT-4o-mini на одной выборке (≥50 кейсов) по:
  - decision accuracy
  - MAE score
  - false positive / false negative rate
  - latency
  - cost per request
- Только если LoRA статистически не уступает GPT-4o-mini и latency/cost лучше — рекомендовать production transition.

---

## 11. Заключение

**Experiment 003 не production-ready из-за over-correction:** hard negatives сработали, но модель стала слишком консервативной и отклоняет genuine matches.

**Cycle 4 должен:**
1. Сохранить 33 hard negative записи Experiment 003.
2. Добавить 15–25 high-quality positive/borderline записей, особенно для смежных IT-ролей.
3. Довести баланс match/no_match в train+val до 30/70.
4. Расширить test set до 30–50 записей.
5. Пройти offline и runtime validation с критериями:
   - decision_accuracy ≥ 0.75
   - MAE_score ≤ 22
   - valid_json_rate = 1.0
   - runtime smoke 7/7 passed
   - hard negative holdout passed

**Следующий шаг:** спроектировать конкретный набор новых positive/borderline кандидатов для Cycle 4.
