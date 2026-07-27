# Experiment 004 Report: Balanced Teacher Dataset for Production-Ready LoRA

**Кейс:** HR Assistant (hr-assistant)  
**Модуль:** Fine-tuning / Experimental ML-контур  
**Дата начала:** 2026-07-22  
**Дата завершения:** 2026-07-23  
**Статус:** Завершён — гипотеза частично подтверждена, модель не production-ready

---

## 1. Контекст

Experiment 004 — ответ на precision/recall trade-off, выявленный в Experiment 003.

В Experiment 003 добавление hard-negative и edge-case примеров в teacher dataset позволило модели пройти runtime negative smoke test: ложные срабатывания на нерелевантных профилях исчезли. Однако модель стала чрезмерно консервативной и стала отклонять частично или полностью подходящих кандидатов — появились ложные отрицательные решения на genuine match-кейсах. Возник trade-off: precision вырос, recall упал.

Experiment 004 проверяет, можно ли восстановить recall, сохранив достижения Experiment 003, за счёт пересбалансирования teacher dataset в сторону high-quality positive и borderline примеров. Все параметры модели, LoRA и обучения остаются неизменными; единственная изменяемая переменная — состав teacher dataset.

Как и Experiment 003, Experiment 004 выполнялся с Claude Code на VPS и на RunPod: GPU-preflight, обучение, выбор checkpoint, offline/runtime evaluation, baseline comparison и external validation проходили в среде RunPod под управлением Claude Code. Это продолжение эволюции процесса, начатой в Experiment 003.

---

## 2. Гипотеза

**H₀ (нулевая гипотеза):**  
Добавление positive/borderline примеров в teacher dataset при неизменных параметрах модели не улучшает recall на genuine match-кейсах и не позволяет LoRA соответствовать или превосходить GPT-4o-mini.

**H₁ (альтернативная гипотеза):**  
Пересбалансирование teacher dataset за счёт positive/borderline примеров (при сохранении hard negatives) восстанавливает recall, сохраняет runtime negative smoke и позволяет LoRA соответствовать или превосходить GPT-4o-mini.

**Критерий подтверждения гипотезы:**
- `valid_json_rate` = 1.0 на offline и runtime-тестах;
- `decision_accuracy` ≥ 0.75 на расширенном test set (≥15 записей);
- отсутствуют false positives на obvious_no_match;
- отсутствуют false negatives на obvious_match;
- runtime smoke test проходит 7/7 без unexpected matches;
- `decision_accuracy` LoRA ≥ `decision_accuracy` GPT-4o-mini на сравнительной выборке.

---

## 3. Изменения относительно предыдущего эксперимента

| Компонент | Experiment 003 | Experiment 004 |
|-----------|----------------|----------------|
| Teacher dataset | HRA-EXP-V3, 123 записи (41 кандидат) | HRA-EXP-V4, 162 записи (54 кандидата) |
| Новые positive/borderline кандидаты | 0 целенаправленных | 13 (`HRA-EVAL-V2-000201`–`HRA-EVAL-V2-000213`) |
| Train+val match % | 15.7% | ~25–28% |
| Train+val no_match % | 84.3% | ~72–75% |
| Test set записей | 9 (исходный V2) | 15 (6 legacy + 3 новых positive + 6 hard negative holdout) |
| Hard negative записи | 33 (11 новых кандидатов V3) | сохранены 33 + унаследованы в V4 |
| External validation | не проводилась | HRA-EVAL-V5-EXT, 102 записи, 34 кандидата |
| GPT-4o-mini comparison | не проводился | 15 записей test set, повторный запуск после truncation fix |
| Telegram smoke test | не проводился | 23 hard-negative/edge анкеты в реальном Telegram-контуре |

Единственная изменяемая переменная — состав teacher dataset. Все параметры модели, LoRA, обучения, runtime-контура и Judge остаются неизменными.

---

## 4. Неизменяемые параметры

| Группа | Параметр | Значение | Источник |
|--------|----------|----------|----------|
| Модель | Base model ID | `Qwen/Qwen2.5-1.5B-Instruct` | [`configs/experiment_004.yaml`](configs/experiment_004.yaml) |
| LoRA | `r` | `16` | [`configs/experiment_004.yaml`](configs/experiment_004.yaml) |
| LoRA | `lora_alpha` | `32` | [`configs/experiment_004.yaml`](configs/experiment_004.yaml) |
| LoRA | `lora_dropout` | `0.05` | [`configs/experiment_004.yaml`](configs/experiment_004.yaml) |
| LoRA | `target_modules` | `q_proj, k_proj, v_proj, o_proj, gate_proj, up_proj, down_proj` | [`configs/experiment_004.yaml`](configs/experiment_004.yaml) |
| LoRA | `bias` | `none` | [`configs/experiment_004.yaml`](configs/experiment_004.yaml) |
| Обучение | `num_train_epochs` | `5` | [`configs/experiment_004.yaml`](configs/experiment_004.yaml) |
| Обучение | `per_device_train_batch_size` | `1` | [`configs/experiment_004.yaml`](configs/experiment_004.yaml) |
| Обучение | `gradient_accumulation_steps` | `4` | [`configs/experiment_004.yaml`](configs/experiment_004.yaml) |
| Обучение | `learning_rate` | `2e-4` | [`configs/experiment_004.yaml`](configs/experiment_004.yaml) |
| Обучение | `optim` | `adamw_torch` | [`configs/experiment_004.yaml`](configs/experiment_004.yaml) |
| Обучение | `fp16` | `True` | [`configs/experiment_004.yaml`](configs/experiment_004.yaml) |
| Обучение | Best checkpoint metric | `eval_loss` (minimize) | [`configs/experiment_004.yaml`](configs/experiment_004.yaml) |
| Обучение | `seed` | `42` | [`configs/experiment_004.yaml`](configs/experiment_004.yaml) |
| Runtime | API-контур | FastAPI + Transformers + PEFT ([`../api/hra_qwen_api_lora.py`](../api/hra_qwen_api_lora.py)) | [`configs/experiment_004.yaml`](configs/experiment_004.yaml) |
| Teacher | Judge | GPT-4.1, `temperature = 0` | [`configs/experiment_004.yaml`](configs/experiment_004.yaml) |

Подробное описание технической основы — в [`TECHNICAL_FOUNDATION.md`](TECHNICAL_FOUNDATION.md).

---

## 5. Датасет

### 5.1. Teacher dataset Experiment 004

| Параметр | Значение |
|----------|----------|
| Эксперимент | `HRA-EXP-V4` |
| Dataset | `HRA-EVAL-V4` |
| Всего записей | 162 (54 кандидата × 3 вакансии) |
| Train | 114 записей (38 кандидатов) |
| Validation | 27 записей (9 кандидатов) |
| Test | 15 записей (5 кандидатов) |
| Hard negative holdout | 6 записей (2 кандидата) |

Teacher dataset формировался в три слоя:
- **База Experiment 002** — 30 кандидатов (90 записей), сохранённые в V4.
- **Hard negatives Experiment 003** — 11 кандидатов (`HRA-EVAL-V2-000101`–`HRA-EVAL-V2-000111`, 33 записи), добавленные в train/validation/holdout.
- **Positive/borderline кандидаты Experiment 004** — 13 новых кандидатов (`HRA-EVAL-V2-000201`–`HRA-EVAL-V2-000213`, 39 записей), направленных на восстановление recall.

### 5.2. Стратификация train/validation/test

| Split | obvious_match | borderline | obvious_no_match |
|-------|---------------|------------|------------------|
| Train | 39 | 42 | 33 |
| Validation | 9 | 9 | 9 |
| Test | 9 | 3 | 3 |
| Holdout | 0 | 0 | 6 |

### 5.3. Вакансии

Каждый кандидат оценивается по трём вакансиям:
- Prompt Engineer / AI Automation Specialist;
- Системный аналитик;
- Специалист по разметке данных.

### 5.4. External validation dataset

| Параметр | Значение |
|----------|----------|
| Dataset | `HRA-EVAL-V5-EXT` |
| Эксперимент | `HRA-EXP-V5-EXT` |
| Всего записей | 102 (34 кандидата × 3 вакансии) |
| obvious_match | 45 |
| borderline | 33 |
| obvious_no_match | 24 |
| Reference judge | GPT-4o |

External validation dataset не пересекается с train/validation/test Experiment 004 по `case_code` и формировался независимым Judge-проходом. Подробнее — в [`reports/external_validation_report.md`](reports/external_validation_report.md).

### 5.5. Формат данных

Публичный обезличенный пример формата данных: [`data_sample/example.jsonl`](data_sample/example.jsonl).  
Полное описание схемы, истории версий и анализ hard negatives — в [`reports/teacher_dataset_report.md`](reports/teacher_dataset_report.md).

---

## 6. Выполнение

### 6.1. Участники и роли

| Роль | Ответственность |
|------|-----------------|
| **Пользователь** | Инициатор, владелец решения, утверждение гипотез, критериев успеха и итогового вердикта. |
| **VPS Claude Code** | Подготовка кода, конфигураций, датасетов, SQL-скриптов, offline evaluation и документации. |
| **RunPod Claude Code** | GPU-preflight, обучение, checkpoint selection, offline/runtime evaluation, возврат артефактов. |
| **GPT-4.1 (Teacher / Judge)** | Формирование reference labels для teacher dataset и external validation. |
| **GPT-4o-mini** | Production baseline для сравнения. |
| **Telegram / n8n** | Runtime-контур для real-world smoke test. |

### 6.2. Stage-by-stage исполнители

| Этап | Вход | Инструмент | Исполнитель | Выходной артефакт | Критерий завершения |
|------|------|------------|-------------|-------------------|---------------------|
| 1. Исследовательский контракт | Результаты Experiment 003 | Markdown-шаблон отчёта | Пользователь + VPS Claude Code | `Experiment_004_Report.md` (Stage 1) | Гипотеза и критерии утверждены |
| 2. Проектирование positive/borderline кандидатов | Failure modes Exp 003 | Анализ отчётов | VPS Claude Code | Спецификация 13 кандидатов | Покрытие категорий, уникальность `case_code` |
| 3. SQL и Judge-разметка | Спецификация кандидатов | SQL-скрипты + n8n workflow | VPS Claude Code + Пользователь | Размеченные 162 пары | 162 пары валидированы |
| 4. Формирование teacher dataset | Reference-разметка | [`scripts/extract_teacher_dataset.py`](scripts/extract_teacher_dataset.py) | VPS Claude Code | `train.jsonl`, `validation.jsonl`, `test.jsonl`, `holdout.jsonl` | Стратификация и отсутствие leakage |
| 5. Launch contract и transfer package | Dataset + параметры | [`configs/experiment_004.yaml`](configs/experiment_004.yaml) | VPS Claude Code | Launch contract, transfer list | Все пути и команды зафиксированы |
| 6. Обучение и offline evaluation на RunPod | Dataset + launch contract | [`scripts/train_lora.py`](scripts/train_lora.py), [`scripts/evaluate_generation_test.py`](scripts/evaluate_generation_test.py), [`scripts/evaluate_test.py`](scripts/evaluate_test.py) | RunPod Claude Code | Best adapter, offline metrics | Best checkpoint выбран, offline criteria passed |
| 7. Offline audit и GPT-4o-mini comparison | Test set, best adapter | [`scripts/compare_with_gpt.py`](scripts/compare_with_gpt.py) | RunPod Claude Code | Сравнительный отчёт | LoRA vs GPT-4o-mini метрики зафиксированы |
| 8. External validation | HRA-EVAL-V5-EXT | [`scripts/compare_external_validation.py`](scripts/compare_external_validation.py) | RunPod Claude Code | External validation report | 102 пары прогнаны для LoRA и GPT-4o-mini |
| 9. Runtime validation | `data/smoke_set.jsonl` | [`../api/hra_qwen_api_lora.py`](../api/hra_qwen_api_lora.py) + [`scripts/runtime_smoke_test.py`](scripts/runtime_smoke_test.py) | RunPod Claude Code | Runtime smoke report | 7/7 passed, 0 unexpected matches |
| 10. Real-world Telegram smoke test | 23 hard-negative/edge анкеты | Telegram-бот + n8n workflow | Пользователь + Telegram/n8n | Telegram smoke results | Результаты LoRA vs GPT-4o-mini зафиксированы |
| 11. Документирование и вердикт | Все метрики | Отчёт эксперимента | VPS Claude Code + Пользователь | `Experiment_004_Report.md` | Вердикт принят и задокументирован |

### 6.3. Ключевые отклонения и инженерные решения

- **Этап 7 выполнен дважды.** Первый запуск с `max_tokens = 300` выявил truncation bug: два кейса вернули HTTP 422 из-за нераспарсиваемого JSON. После фикса (`max_tokens` увеличен до 512 и добавлен graceful JSON fallback в [`hra_qwen_api_lora.py`](../api/hra_qwen_api_lora.py)) сравнение повторено.
- **Latency optimization.** Основной runtime на Transformers + PEFT давал p95 latency ≈ 17 сек. В рамках Exp 004 исследованы альтернативные runtime: 4-bit NF4-квантизация ([`../api/hra_qwen_api_lora_4bit.py`](../api/hra_qwen_api_lora_4bit.py)) и vLLM OpenAI-compatible runtime ([`../api/hra_qwen_api_lora_vllm.py`](../api/hra_qwen_api_lora_vllm.py)). vLLM сократил p95 latency до ~2.1 сек. Канонический runtime Experiments 003–004 — FastAPI + Transformers + PEFT.

---

## 7. Результаты обучения

| Метрика | Значение |
|---------|----------|
| Experiment ID | `experiment_004` |
| Лучший чекпоинт | `checkpoint-87` (конец эпохи 3) |
| Best `eval_loss` | **0.3273** |
| Train epochs | 5 |
| Время обучения | 202 секунды |
| Peak VRAM | 7.46 GB |
| GPU | NVIDIA RTX A5000 (RunPod) |

**Динамика обучения:**

| Epoch | Avg Train Loss | Eval Loss | Eval Token Accuracy | Checkpoint | Best |
|-------|----------------|-----------|---------------------|------------|------|
| 1 | 0.658 | 0.3667 | 0.9107 | `checkpoint-29` | — |
| 2 | 0.230 | 0.3308 | 0.9211 | `checkpoint-58` | — |
| 3 | 0.150 | **0.3273** | 0.9254 | `checkpoint-87` | ✅ |
| 4 | 0.100 | 0.3636 | 0.9233 | `checkpoint-116` | — |
| 5 | 0.075 | 0.3722 | 0.9252 | `checkpoint-145` | — |

Early convergence: лучший чекпоинт достигается на эпохе 3; дальнейшее обучение не улучшает validation loss.

---

## 8. Offline evaluation

### 8.1. Generation test (test set, 15 записей)

| Модель | valid_json_rate | decision_accuracy | MAE_score | MAE_role | MAE_skills | MAE_experience | MAE_conditions |
|--------|-----------------|-------------------|-----------|----------|------------|----------------|----------------|
| Base Qwen | 1.000 | 0.333 | 34.13 | — | — | — | — |
| **LoRA Experiment 004** | **1.000** | **0.800** | **15.13** | 2.40 | 3.07 | 6.00 | 4.73 |

> **Доказательство:** summary метрик и примеры Base vs LoRA — в [`data/evidence/experiment_004_generation_test_summary.json`](data/evidence/experiment_004_generation_test_summary.json). Эта оценка проведена скриптом `evaluate_generation_test.py` на `test.jsonl` HRA-EVAL-V4.

### 8.2. Test loss evaluation

| Модель | eval_loss |
|--------|-----------|
| Base Qwen | 7.8141 |
| LoRA Experiment 004 | 7.8079 |

### 8.3. Интерпретация offline-метрик

- LoRA значительно превосходит base Qwen по decision accuracy (+0.467) и MAE (−18.99).
- По сравнению с Experiment 003 (decision_accuracy 0.667 на original test) Experiment 004 показывает восстановление recall (0.800) благодаря positive/borderline примерам.
- Test loss почти идентичен у base Qwen и LoRA, что подтверждает, что perplexity не является ведущей бизнес-метрикой для этой задачи.

---

## 9. Runtime validation

### 9.1. Runtime smoke test

| Категория | Cases | Passed | Failed |
|-----------|-------|--------|--------|
| positive | 1 | 1 | 0 |
| obvious_negative | 1 | 1 | 0 |
| hard_negative | 2 | 2 | 0 |
| edge_case | 1 | 1 | 0 |
| invalid_input | 1 | 1 | 0 |
| stability_repeat | 1 | 1 | 0 |
| **Итого** | **7** | **7** | **0** |

**Ключевой вывод:** все заранее зафиксированные отрицательные и edge-case сценарии корректно отклонены; unexpected matches отсутствуют. Достижения Experiment 003 по hard negatives сохранены.

> **Доказательство:** полные ответы LoRA по каждому smoke-кейсу — в [`data/evidence/experiment_004_runtime_smoke.json`](data/evidence/experiment_004_runtime_smoke.json).

#### Representative example: успешное восстановление genuine match

**Candidate:** AI Automation Specialist / Prompt Engineer, 4 года опыта в prompt engineering, LLM, n8n, REST API, Python, зарплата 200 000 ₽.

**Vacancy:** Prompt Engineer / AI Automation Specialist; бюджет 150 000–250 000 ₽.

**Reference / expected:** `match`.

**Model prediction (LoRA Experiment 004):** `match`, score 87, с обоснованием по всем четырём компонентам (роль, навыки, опыт, условия).

**Почему этот пример важен:** Подтверждает, что добавление positive/borderline примеров в V4 восстановило recall: LoRA снова признаёт genuine match, сохраняя при этом runtime negative smoke 7/7.

**Evidence:** [`data/evidence/experiment_004_runtime_smoke.json`](data/evidence/experiment_004_runtime_smoke.json), кейс `SMOKE-POSITIVE-001`, category `positive`.

### 9.2. Truncation bug и max_tokens bump

В ходе GPT-4o-mini comparison (Этап 7) первый запуск с `max_tokens = 300` выявил проблему:

- **Симптом:** `valid_json_rate` LoRA = 0.867; 2 из 15 записей вернули HTTP 422.
- **Причина:** JSON-ответ модели обрезался по `max_tokens`, и [`hra_qwen_api_lora.py`](../api/hra_qwen_api_lora.py) бросал `HTTPException(422)` при нераспарсиваемом JSON.

**Фикс:**
1. В [`hra_qwen_api_lora.py`](../api/hra_qwen_api_lora.py) заменён raise `HTTPException(422)` на graceful fallback: HTTP 200 с JSON-объектом `{"error": "invalid_json", "raw_response": "..."}`. Это позволяет downstream-клиентам обрабатывать malformed output без разрыва соединения.
2. В скрипте сравнения `max_tokens` увеличен с 300 до 512 для LoRA и GPT-4o-mini.

**Результат после фикса (в рамках GPT-4o-mini comparison, `compare_with_gpt.py`):**
- `valid_json_rate` LoRA: 0.867 → 1.000;
- `decision_accuracy` LoRA: 0.800 → 0.933;
- `MAE_score` LoRA: 6.69 → 5.80;
- HTTP 422 errors: 0.

> **Примечание:** значения 0.800 / 15.13 в разделе 8.1 получены скриптом `evaluate_generation_test.py`; значения 0.933 / 5.80 — скриптом `compare_with_gpt.py` после увеличения `max_tokens` до 512. Это два независимых прогона с разными downstream-скриптами, поэтому их MAE_score отличаются.

### 9.3. Latency

| Runtime | p50 (ms) | p95 (ms) | avg (ms) |
|---------|----------|----------|----------|
| FastAPI + Transformers + PEFT (канонический) | ~11 700 | ~16 900 | ~11 800 |
| vLLM OpenAI-compatible (исследовательский) | ~1 700 | ~2 100 | ~1 640 |
| GPT-4o-mini | ~1 200 | ~1 800 | ~1 240 |

Канонический runtime на базе Transformers + PEFT не укладывается в production-цель p95 ≤ 2 сек. vLLM как альтернатива сокращает latency до production-acceptable диапазона, но требует отдельной инженерной доработки контура.

---

## 10. Дополнительная валидация

### 10.1. Сравнение с GPT-4o-mini (test set, 15 записей)

| Metric | LoRA Experiment 004 | GPT-4o-mini |
|--------|---------------------|-------------|
| valid_json_rate | 1.000 | 1.000 |
| decision_accuracy | 0.933 | 1.000 |
| MAE_score | 5.80 | 0.13 |
| FPR | 0.111 | 0.000 |
| FNR | 0.000 | 0.000 |
| latency_p50 (ms) | 11 059 | 1 557 |
| latency_p95 (ms) | 13 499 | 3 148 |

GPT-4o-mini остаётся точнее на малой teacher-размеченной выборке (15 записей), что ожидаемо из-за семейной близости с teacher-моделью GPT-4.1. LoRA после фикса достигает 93.3% decision accuracy при нулевом FNR.

> **Доказательство:** примеры prediction/reference/LoRA/GPT для записей с расхождениями — в [`data/evidence/experiment_004_gpt_comparison_examples.jsonl`](data/evidence/experiment_004_gpt_comparison_examples.jsonl).

### 10.2. External validation vs GPT-4o-mini (HRA-EVAL-V5-EXT, 102 записи)

| Metric | LoRA Experiment 004 | GPT-4o-mini |
|--------|---------------------|-------------|
| valid_json_rate | 1.000 | 1.000 |
| decision_accuracy | **0.931** | 0.941 |
| MAE_score | 19.63 | 6.19 |
| FPR | **0.050** | 0.063 |
| FNR | 0.136 | **0.045** |
| latency_p50 (ms) | 11 665 | 1 185 |
| latency_p95 (ms) | 16 879 | 1 776 |

**Выводы external validation:**
- LoRA обобщается на внешней выборке: 93.1% decision accuracy — близко к GPT-4o-mini (94.1%).
- LoRA даёт меньше ложных срабатываний (FPR 5.0% vs 6.3%).
- LoRA более консервативна: FNR 13.6% vs 4.5% у GPT-4o-mini.
- LoRA сильно отстаёт по точности score (MAE 19.6 vs 6.2) и по latency (~10× медленнее канонического runtime).

> **Доказательство:** примеры с ошибками LoRA на HRA-EVAL-V5-EXT — в [`data/evidence/experiment_004_external_validation_examples.jsonl`](data/evidence/experiment_004_external_validation_examples.jsonl).

### 10.2b. External validation с vLLM-ускорением vs GPT-4o-mini (HRA-EVAL-V5-EXT, 102 записи, 3 прогона)

После latency optimization LoRA была переключена на vLLM OpenAI-compatible runtime ([`../api/hra_qwen_api_lora_vllm.py`](../api/hra_qwen_api_lora_vllm.py)), и тот же внешний датасет HRA-EVAL-V5-EXT был прогнан 3 раза для сравнения с GPT-4o-mini.

| Metric | LoRA Experiment 004 (vLLM) avg 3 runs | GPT-4o-mini avg 3 runs |
|--------|--------------------------------------|------------------------|
| valid_json_rate | 1.000 | 0.997 |
| decision_accuracy | **0.931** | 0.925 |
| MAE_score | 19.53 | **6.73** |
| FPR | **0.050** | 0.079 |
| FNR | 0.136 | **0.045** |
| latency_p50 (ms) | 1 688 | 1 296 |
| latency_p95 (ms) | 2 104 | 2 007 |

**Выводы external validation после ускорения:**
- С vLLM LoRA достигает **сопоставимого с GPT-4o-mini decision accuracy** (0.931 vs 0.925) и даже немного превосходит по среднему по 3 прогонам.
- FPR у LoRA ниже, чем у GPT-4o-mini (5.0% vs 7.9%).
- FNR остаётся выше (13.6% vs 4.5%), и MAE score по-прежнему существенно хуже (19.5 vs 6.7).
- Latency p95 становится **сопоставимым** с GPT-4o-mini (~2.1 сек vs ~2.0 сек), в отличие от канонического runtime (~16.9 сек).

> **Доказательство:** summary трёх повторных прогонов и representative examples — в [`data/evidence/experiment_004_external_validation_vllm_examples.jsonl`](data/evidence/experiment_004_external_validation_vllm_examples.jsonl).

#### Representative example: LoRA консервативнее GPT-4o-mini на смежной роли

**Candidate:** AI Automation Specialist, 4 года опыта автоматизации бизнес-процессов, REST API, работа с бизнес-процессами; без SQL и BPMN.

**Vacancy:** Системный аналитик; требуется SQL, BPMN, REST API, аналитика, постановка задач разработчикам.

**Reference (GPT-4o):** `match`, score 63.

**Model prediction (LoRA Experiment 004, vLLM):** `no_match`, score 57, с обоснованием, что кандидат — AI Automation Specialist, а не системный аналитик, и не хватает ключевых hard skills.

**GPT-4o-mini prediction:** `match`, score 70.

**Почему этот пример важен:** Иллюстрирует, почему у LoRA выше FNR (13.6% vs 4.5%): она строже штрафует за отсутствие прямых ключевых навыков, даже когда reference judge считает смежный профиль подходящим.

**Evidence:** [`data/evidence/experiment_004_external_validation_vllm_examples.jsonl`](data/evidence/experiment_004_external_validation_vllm_examples.jsonl), запись `HRA-EVAL-V2-000305`, vacancy "Системный аналитик".

#### Representative example: LoRA завышает score на borderline-кейсе

**Candidate:** Системный аналитик, 2 года опыта, SQL, BPMN, REST API, UML, аналитика; недостаточно опыта постановки задач разработчикам, зарплата ниже минимума бюджета.

**Vacancy:** Системный аналитик; требуется опыт постановки задач разработчикам, зарплата в бюджете.

**Reference (GPT-4o):** `no_match`, score 67.

**Model prediction (LoRA Experiment 004, vLLM):** `match`, score 98, с обоснованием, что кандидат "идеально подходит", игнорируя недостаток опыта постановки задач и salary mismatch.

**GPT-4o-mini prediction:** `match`, score 80.

**Почему этот пример важен:** Показывает проблему калибровки score у LoRA: даже при правильном decision (GPT-4o-mini тоже выдал `match`) LoRA сильно завышает absolute score (98 vs reference 67), что объясняет высокий MAE 19.5.

**Evidence:** [`data/evidence/experiment_004_external_validation_vllm_examples.jsonl`](data/evidence/experiment_004_external_validation_vllm_examples.jsonl), запись `HRA-EVAL-V2-000316`, vacancy "Системный аналитик".

#### Representative example: ошибка, оставшаяся после внешней валидации

**Candidate:** Специалист по разметке данных, 4 года опыта разметки данных, проверки ИИ, написания инструкций, внимательность, грамотность.

**Vacancy:** Prompt Engineer / AI Automation Specialist; требуется prompt engineering, n8n, API, JSON, LLM, автоматизация бизнес-процессов.

**Reference (GPT-4o):** `no_match`, score 45.

**Model prediction (LoRA Experiment 004):** `match`, score 62, с обоснованием, что разметка данных — смежная область с prompt engineering.

**Почему этот пример важен:** Показывает, что даже при высокой aggregate decision accuracy (0.931) LoRA всё ещё даёт false positives на смежных ролях без прямых hard skills; это одна из причин, почему модель не production-ready.

**Evidence:** [`data/evidence/experiment_004_external_validation_examples.jsonl`](data/evidence/experiment_004_external_validation_examples.jsonl), запись `HRA-EVAL-V2-000308`, vacancy "Prompt Engineer / AI Automation Specialist".

### 10.3. Real-world Telegram smoke test

| Параметр | Значение |
|----------|----------|
| Анкет | 23 |
| Тип кейсов | hard-negative / edge / positive / obvious_no_match |
| LoRA correct rate | **35%** |
| GPT-4o-mini correct rate | **43%** |
| Сравнение | LoRA уступает GPT-4o-mini на 8 pp |

> **Доказательство:** детальная таблица 23 анкет и representative failures — в [`data/evidence/telegram_smoke_test_summary.json`](data/evidence/telegram_smoke_test_summary.json).

**Классификация кейсов:**

| Категория | Описание |
|-----------|----------|
| POSITIVE | Явные positive-кейсы, которые должны получить match. |
| OBVIOUSNOMATCH | Явные несовпадения, которые должны получить no_match. |
| BORDERLINE | Пограничные кейсы около порога 60. |
| HN1–HN8 | Hard-negative категории, определённые в Experiment 003 ([`Experiment_003_Report.md`](Experiment_003_Report.md)). |
| EC1 / EC3 / EC4 | Edge-case категории, определённые в Experiment 003. |

#### Representative example: характерный failure mode Telegram smoke

**Candidate:** Стажёр, 0 лет опыта, в резюме указан 1 навык SQL.

**Vacancy:** Системный аналитик; требуется SQL, BPMN, REST API, аналитика, постановка задач разработчикам.

**Expected:** `no_match`.

**Model prediction (LoRA Experiment 004, vLLM):** `match`, score 80, с галлюцинациями SQL, BPMN, REST API и аналитики — навыков, которых у кандидата нет.

**Почему этот пример важен:** Иллюстрирует главный production-риск LoRA: на extreme sparse junior/стажёрских профилях модель "дорисовывает" недостающие hard skills и завышает score, из-за чего real-world correct rate LoRA (35 %) ниже, чем у GPT-4o-mini (43 %).

**Evidence:** [`data/evidence/telegram_smoke_test_summary.json`](data/evidence/telegram_smoke_test_summary.json), строка #11 (HN6) и блок `representative_failures`.

**Основные failure modes LoRA в Telegram smoke:**

1. **Галлюцинации навыков у junior/стажёрских профилей.** Модель приписывает кандидатам компетенции, которых нет в резюме, и завышает score.
2. **Путаница BA / DA / процессного аналитика с системным аналитиком.** Смежные роли без обязательных hard skills (SQL/BPMN/REST API) получают завышенный role_score и skills_score.
3. **Игнорирование salary mismatch.** При сильном профиле по роли/навыкам модель не снижает conditions_score при критичном несоответствии зарплатных ожиданий.

**Почему external validation не поймала эти failure modes:**
- External validation dataset HRA-EVAL-V5-EXT содержит преимущественно obvious_match/borderline/obvious_no_match записи и не покрывает production-like hard-negative сценарии Telegram (процессный аналитик, salary mismatch 450 000, extreme sparse junior/стажёр).
- Доля hard-negative-like записей во внешней выборке недостаточна для измерения production-качества на сложных кейсах.
- Подробный анализ hard negatives и teacher-label mismatch — в [`reports/teacher_dataset_report.md`](reports/teacher_dataset_report.md).

---

## 11. Интерпретация

### 11.1. Что показал эксперимент

1. **Dataset engineering сильнее тюнинга адаптера.** Гиперпараметры LoRA неизменны с Experiment 002/003. Рост decision accuracy с 0.667 (Exp 003) до 0.800 (Exp 004) и восстановление recall достигнуты исключительно за счёт добавления positive/borderline примеров.
2. **Hard-negative достижения сохранены.** Runtime smoke 7/7 без unexpected matches подтверждает, что добавление positives не вернуло ложные срабатывания на нерелевантных профилях.
3. **Best checkpoint selection по eval_loss корректен.** Минимум eval_loss на `checkpoint-87` (эпоха 3) совпадает с лучшими offline-метриками.

### 11.2. Почему offline и real-world результаты расходятся

- Offline test set (15 записей) и external validation (102 записи) показывают decision accuracy ~0.93, но они плохо покрывают hard-negative/edge сценарии, которые встречаются в production Telegram-контуре.
- Telegram smoke test на 23 hard-negative/edge анкетах даёт только 35% корректных ответов у LoRA. Это указывает на **teacher-label mismatch** и недостаточную репрезентативность датасета по сложным отрицательным кейсам.
- Модель воспроизводит teacher labels, но если teacher размечает часть hard-negative-like записей как match, модель наследует эту ошибку.

### 11.3. Ограничения teacher labels

- Модель действительно выучила структуру ответа и порог decision, но плохо калибрует score (MAE 19.6 на external validation).
- Высокая offline-метрика не гарантирует production-качество без stratified hard-negative smoke set.

---

## 12. Вердикт

> **Гипотеза частично подтверждена.**

| Критерий | Результат |
|----------|-----------|
| Устранение precision/recall trade-off в offline | ✅ Подтверждено — decision_accuracy 0.800, нет unexpected matches в runtime smoke |
| Сохранение hard-negative достижений Exp 003 | ✅ Подтверждено — runtime smoke 7/7 passed |
| Соответствие / превосходство GPT-4o-mini | ❌ Не подтверждено — LoRA уступает по MAE и latency, на Telegram smoke 35% vs 43% |
| Production-ready | ❌ Нет |

**Практический смысл:** LoRA Experiment 004 — рабочий on-premise / edge-кандидат для сценариев без интернета, с требованиями конфиденциальности или offline-работы. В облачном production сейчас остаётся GPT-4o-mini.

---

## 13. Следующий эксперимент

Результаты Experiment 004 непосредственно ведут к proposal Experiment 005. Цель следующего цикла — устранить разрыв между высокой offline decision accuracy (~93%) и низким production-качеством на hard-negative/edge кейсах (35% в Telegram smoke).

### 13.1. Что исправить

1. **Teacher-label audit и re-label hard negatives.** Пересмотреть hard-negative-like записи, размеченные teacher как match. Сформировать production smoke set 30–50 кейсов, покрывающий HN1–HN8, EC1, EC3, EC4, POSITIVE, OBVIOUSNOMATCH.
2. **Stratified metrics.** Ввести decision accuracy / FPR / FNR по стратам POSITIVE, OBVIOUSNOMATCH, BORDERLINE, HARD NEGATIVE. Цель: MAE ≤ 15 на POSITIVE / OBVIOUSNOMATCH strata.
3. **Score calibration.** Добавить post-processing калибровку predicted score или экспериментировать с loss-функциями, учитывающими ordinal nature score. Цель: снизить MAE с 19.6 до ≤10 на external validation.
4. **Latency optimization в production-контур.** Перевести production-serving на vLLM (p95 ~2.1 сек) или исследовать QLoRA / AWQ / GPTQ. Цель: p95 latency ≤ 2 сек в production.
5. **Снижение FNR.** Добавить больше positive/borderline примеров для редких case_type; попробовать threshold tuning на validation.

### 13.2. Что оставить неизменным

- Базовая модель `Qwen/Qwen2.5-1.5B-Instruct`;
- LoRA параметры (`r=16`, `alpha=32`, `target_modules`);
- Параметры обучения (5 эпох, batch=1, grad_accum=4, lr=2e-4);
- Runtime graceful JSON fallback и `max_tokens = 512`;
- Teacher Judge GPT-4.1, `temperature = 0`.

### 13.3. Критерии следующего цикла

- Telegram smoke correct rate LoRA ≥ GPT-4o-mini;
- или, при неизменном baseline, рост Telegram correct rate LoRA ≥ +15 pp относительно Experiment 004;
- external validation MAE_score LoRA ≤ 10;
- production runtime p95 latency ≤ 2 сек;
- stratified FPR на HARD NEGATIVE ≤ 10%.

---

## 14. Источники и артефакты

### 14.1. Публичные конфигурации и скрипты

- [`configs/experiment_004.yaml`](configs/experiment_004.yaml) — launch contract;
- [`scripts/train_lora.py`](scripts/train_lora.py) — обучение;
- [`scripts/evaluate_generation_test.py`](scripts/evaluate_generation_test.py) — generation test;
- [`scripts/evaluate_test.py`](scripts/evaluate_test.py) — eval loss;
- [`scripts/compare_with_gpt.py`](scripts/compare_with_gpt.py) — сравнение с GPT-4o-mini;
- [`scripts/compare_external_validation.py`](scripts/compare_external_validation.py) — external validation;
- [`scripts/runtime_smoke_test.py`](scripts/runtime_smoke_test.py) — runtime smoke;
- [`../api/hra_qwen_api_lora.py`](../api/hra_qwen_api_lora.py) — канонический runtime API;
- [`../api/hra_qwen_api_lora_vllm.py`](../api/hra_qwen_api_lora_vllm.py) — исследовательский vLLM runtime.

### 14.2. Отчёты и данные

- [`TECHNICAL_FOUNDATION.md`](TECHNICAL_FOUNDATION.md) — техническая основа;
- [`Experiment_003_Report.md`](Experiment_003_Report.md) — предыдущий эксперимент;
- [`reports/teacher_dataset_report.md`](reports/teacher_dataset_report.md) — анализ teacher dataset;
- [`reports/external_validation_report.md`](reports/external_validation_report.md) — external validation dataset;
- [`data_sample/example.jsonl`](data_sample/example.jsonl) — обезличенный пример формата данных.

### 14.3. Идентификаторы запуска

- Experiment ID: `experiment_004`;
- Dataset code: `HRA-EVAL-V4`;
- Experiment code: `HRA-EXP-V4`;
- External validation: `HRA-EVAL-V5-EXT` / `HRA-EXP-V5-EXT`;
- Best checkpoint: `checkpoint-87` (эпоха 3), выбран по `eval_loss = 0.3273`.

Датасет `HRA-EVAL-V4`, external validation set `HRA-EVAL-V5-EXT`, smoke set и манифесты включены в репозиторий в каталоге [`data/`](data/). Все профили в них синтетические: HR Assistant никогда не работал в реальном боевом режиме. Первичные артефакты обучения (weights, raw metrics, evaluation JSON, operation logs) хранятся в закрытом рабочем контуре и не публикуются.
