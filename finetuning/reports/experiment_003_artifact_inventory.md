# Инвентаризация артефактов Experiment 003

**Кейс:** `hr-assistant`  
**Эксперимент:** `finetuning/runs/experiment_003/`  
**Дата инвентаризации:** 2026-07-23  
**Статус:** Завершено  
**Цель:** Максимально полно извлечь все доступные данные, метрики, графики и примеры из Experiment 003 для дальнейшего использования в demo-landing и обновления Visual Assets Registry.

---

## 1. Сводка эксперимента

| Параметр | Значение | Источник |
|----------|----------|----------|
| Базовая модель | `Qwen/Qwen2.5-1.5B-Instruct` | `best_adapter/adapter_config.json` → `base_model_name_or_path` |
| LoRA r | 16 | `best_adapter/adapter_config.json` → `r` |
| LoRA alpha | 32 | `best_adapter/adapter_config.json` → `lora_alpha` |
| LoRA dropout | 0.05 | `best_adapter/adapter_config.json` → `lora_dropout` |
| Target modules | 7 модулей: `down_proj`, `k_proj`, `q_proj`, `o_proj`, `up_proj`, `gate_proj`, `v_proj` | `best_adapter/adapter_config.json` → `target_modules` |
| Train batch size | 1 | `trainer_state.json` → `train_batch_size` |
| Количество эпох (план) | 5 | `trainer_state.json` → `num_train_epochs` |
| Количество шагов (план) | 120 | `trainer_state.json` → `max_steps` |
| Лучший checkpoint | `checkpoint-48` (epoch 2, step 48) | `training_report.json` → `best_checkpoint`; `trainer_state.json` → `best_model_checkpoint` |
| Лучший eval loss | **0.310811847448349** | `training_report.json` → `best_metric`; `trainer_state.json` → `best_metric` |
| Время обучения | **180.47 с** (~3 мин) | `training_report.json` → `elapsed_seconds` |
| Пик VRAM | **7397.20 МБ** (~7.4 ГБ) | `training_report.json` → `peak_vram_mb`; `OPERATION_LOG.md` |
| Decision accuracy (LoRA) | **0.667** (66.7%) | `generation_test/generation_test_report.json` → `best_lora.summary.decision_accuracy` |
| Decision accuracy (base Qwen) | **0.222** (22.2%) | `generation_test/generation_test_report.json` → `base_qwen.summary.decision_accuracy` |
| MAE score (LoRA) | **22.22** | `generation_test/generation_test_report.json` → `best_lora.summary.mae_score` |
| MAE score (base Qwen) | **38.33** | `generation_test/generation_test_report.json` → `base_qwen.summary.mae_score` |
| Valid JSON rate | **1.0** (100%) для обеих моделей | `generation_test/generation_test_report.json` → `*.summary.valid_json_rate` |
| Runtime smoke | **7/7 passed**, 0 unexpected matches | `runtime_smoke_report.json` → `passed`, `unexpected_matches` |

**Ключевое отличие от Exp 001/002:** в датасет добавлены hard negatives и edge cases (123 записи против 90 в Exp 001/002); гиперпараметры LoRA не изменялись. Результат: base accuracy 22.2% → LoRA 66.7%, но снижение recall по сравнению с Exp 002 (78%).

---

## 2. Список доступных файлов

### 2.1 Прочитанные файлы

| Путь | Тип | Что содержит |
|------|-----|--------------|
| `experiment_003/README.md` | Markdown | Model card, версии фреймворков (TRL 1.7.0, Transformers 5.12.1, PyTorch 2.6.0+cu124) |
| `experiment_003/OPERATION_LOG.md` | Markdown | Человекочитаемый журнал операций: GPU, длительность, peak VRAM, smoke категории |
| `experiment_003/best_adapter/adapter_config.json` | JSON | Конфигурация LoRA-адаптера (r=16, alpha=32, dropout=0.05, 7 target modules) |
| `experiment_003/trainer_state.json` | JSON | Копия `checkpoint-48/trainer_state.json` — состояние на лучшем checkpoint |
| `experiment_003/checkpoint-24/trainer_state.json` | JSON | Trainer state после 1 эпохи |
| `experiment_003/checkpoint-48/trainer_state.json` | JSON | Trainer state после 2 эпох (глобальный best) |
| `experiment_003/checkpoint-72/trainer_state.json` | JSON | Trainer state после 3 эпох |
| `experiment_003/checkpoint-96/trainer_state.json` | JSON | Trainer state после 4 эпох |
| `experiment_003/checkpoint-120/trainer_state.json` | JSON | Полная trainer state за все 5 эпох + флаг остановки обучения |
| `experiment_003/training_report.json` | JSON | Сводный training report: best checkpoint, elapsed time, peak VRAM |
| `experiment_003/generation_test/generation_test_report.json` | JSON | Per-example и summary метрики generation test для base Qwen и best LoRA |
| `experiment_003/test_evaluation/test_metrics.json` | JSON | Стандартная held-out eval loss: base Qwen 7.8971, best LoRA 8.2578 |
| `experiment_003/runtime_smoke_report.json` | JSON | 7 production smoke cases: категории, latency, pass/fail |
| `finetuning/data/manifest_experiment_003.json` | JSON | Состав датасета 003: 123 записи, splits, case_type distribution |

### 2.2 Дополнительные файлы в каталоге эксперимента

| Путь | Примечание |
|------|------------|
| `experiment_003/best_adapter/adapter_model.safetensors` | Веса адаптера — бинарный артефакт |
| `experiment_003/best_adapter/tokenizer.json`, `tokenizer_config.json`, `chat_template.jinja` | Токенизатор и шаблон чата |
| `experiment_003/checkpoint-*/adapter_config.json` | Идентичная конфигурация LoRA для каждого checkpoint |
| `experiment_003/checkpoint-*/adapter_model.safetensors` | Веса адаптера на каждом checkpoint — бинарный артефакт |
| `experiment_003/checkpoint-*/optimizer.pt`, `scheduler.pt`, `rng_state.pth`, `scaler.pt` | Состояния оптимизатора и тренера — не анализировались |
| `experiment_003/checkpoint-*/training_args.bin` | Аргументы тренера — бинарный формат |

### 2.3 Отсутствующие ожидаемые файлы

| Файл | Где ожидался | Влияние на повествование |
|------|--------------|--------------------------|
| `holdout_evaluation/*` | `experiment_003/holdout_evaluation/` | Нет отдельной оценки holdout (6 записей, все `obvious_no_match`). Невозможно количественно подтвердить качество на hard-negative holdout |
| `per_checkpoint_generation_test.json` | `experiment_003/` | Нет generation test для checkpoint-24/72/96/120 — неизвестно, как менялась business-метрика внутри обучения |
| `latency_profile_report.json` | `experiment_003/` | Нет разложения latency по стадиям (prompt processing / generation) для неоптимизированного API |
| `baseline_validation/metrics.json` | `experiment_003/baseline_validation/` | Базовый eval loss до обучения отсутствует как отдельный файл; base Qwen данные есть только в `generation_test` и `test_evaluation` |
| `preflight_*.json` | `experiment_003/` | Нет preflight-check артефактов |

---

## 3. Training dynamics (per-step / per-epoch)

Полная история обучения содержится в `checkpoint-120/trainer_state.json` → `log_history`. Eval-метрики фиксируются на шагах 24, 48, 72, 96, 120 (один eval в конце каждой эпохи). `trainer_state.json` в корне эксперимента — копия `checkpoint-48/trainer_state.json`, потому что `checkpoint-48` является лучшим.

### 3.1 Per-epoch summary

| Эпоха | Global step | Train loss (последний logged step в эпохе) | Eval loss | Eval token accuracy | Eval entropy | Learning rate (начало → конец эпохи) | Best checkpoint на этой стадии | Примечание |
|-------|-------------|-------------------------------------------|-----------|---------------------|--------------|---------------------------------------|--------------------------------|------------|
| 1 | 24 | 0.3613 (step 20) | **0.3555423617362976** | 0.91666 | 0.33131 | 1.933e-4 → 1.600e-4 | `checkpoint-24` | — |
| 2 | 48 | 0.2027 (step 45) | **0.310811847448349** | 0.92492 | 0.23546 | 1.600e-4 → 1.183e-4 | `checkpoint-48` ← **глобальный best** | Ранняя остановка по eval loss |
| 3 | 72 | 0.1400 (step 70) | **0.3262978792190552** | 0.92233 | 0.18988 | 1.183e-4 → 7.667e-5 | `checkpoint-72` | Eval loss выше best |
| 4 | 96 | 0.09865 (step 95) | **0.3354070782661438** | 0.92883 | 0.16267 | 7.667e-5 → 3.500e-5 | `checkpoint-96` | Eval loss продолжает расти |
| 5 | 120 | 0.07724 (step 120) | **0.34977948665618896** | 0.92888 | 0.15162 | 3.500e-5 → 1.667e-6 | `checkpoint-120` | Train loss минимален, но eval loss ушёл далеко от best |

Примечания:
- Train loss для эпохи взят с последнего logged training step внутри эпохи (`logging_steps=5`).
- Learning rate уменьшается линейно от ~2.0e-4 на step 5 до 1.67e-6 на step 120.
- Eval loss достигает минимума на эпохе 2 и растёт на эпохах 3–5, тогда как train loss продолжает падать — классическое переобучение.
- `checkpoint-120/trainer_state.json` фиксирует `should_training_stop: true` на step 120.

### 3.2 Per-step training dynamics (все logged steps)

| Step | Epoch | Loss | Token accuracy | Learning rate | Entropy | Grad norm | Num tokens | Тип записи |
|------|-------|------|----------------|---------------|---------|-----------|------------|------------|
| 5 | 0.215 | 1.32958 | 0.72157 | 1.933e-4 | 1.25880 | 0.62725 | 13 923 | train |
| 10 | 0.430 | 0.74509 | 0.82446 | 1.850e-4 | 0.84136 | 0.70885 | 27 677 | train |
| 15 | 0.645 | 0.47054 | 0.88373 | 1.767e-4 | 0.50998 | 0.47227 | 41 651 | train |
| 20 | 0.860 | 0.36133 | 0.90594 | 1.683e-4 | 0.39448 | 0.54914 | 55 401 | train |
| **24** | **1.000** | — | **0.91666** | 1.600e-4 | — | — | 64 254 | **eval** (loss 0.35554, entropy 0.33131) |
| 25 | 1.043 | 0.32291 | 0.91753 | 1.600e-4 | 0.33252 | 0.58981 | 67 068 | train |
| 30 | 1.258 | 0.24581 | 0.93311 | 1.517e-4 | 0.29974 | 0.42949 | 80 644 | train |
| 35 | 1.473 | 0.24403 | 0.93175 | 1.433e-4 | 0.26651 | 0.45835 | 94 541 | train |
| 40 | 1.688 | 0.22137 | 0.93898 | 1.350e-4 | 0.24709 | 0.39224 | 108 117 | train |
| 45 | 1.903 | 0.20268 | 0.94319 | 1.267e-4 | 0.23206 | 0.44618 | 122 192 | train |
| **48** | **2.000** | — | **0.92492** | 1.183e-4 | — | — | 128 508 | **eval** (loss **0.31081**, entropy 0.23546) |
| 50 | 2.086 | 0.17870 | 0.94912 | 1.183e-4 | 0.21453 | 0.40668 | 133 876 | train |
| 55 | 2.301 | 0.16215 | 0.95147 | 1.100e-4 | 0.18804 | 0.38952 | 147 818 | train |
| 60 | 2.516 | 0.15543 | 0.95269 | 1.017e-4 | 0.17865 | 0.41830 | 161 749 | train |
| 65 | 2.731 | 0.14209 | 0.95663 | 9.333e-5 | 0.17501 | 0.45014 | 175 455 | train |
| 70 | 2.946 | 0.13999 | 0.95886 | 8.500e-5 | 0.16993 | 0.47443 | 189 204 | train |
| **72** | **3.000** | — | **0.92233** | 7.667e-5 | — | — | 192 762 | **eval** (loss 0.32630, entropy 0.18988) |
| 75 | 3.129 | 0.11956 | 0.96521 | 7.667e-5 | 0.15011 | 0.42593 | 200 716 | train |
| 80 | 3.344 | 0.11365 | 0.96573 | 6.833e-5 | 0.15037 | 0.45473 | 214 543 | train |
| 85 | 3.559 | 0.10630 | 0.96811 | 6.000e-5 | 0.14196 | 0.42002 | 228 344 | train |
| 90 | 3.774 | 0.10556 | 0.96770 | 5.167e-5 | 0.13442 | 0.44336 | 242 180 | train |
| 95 | 3.989 | 0.09865 | 0.97068 | 4.333e-5 | 0.12760 | 0.45943 | 256 282 | train |
| **96** | **4.000** | — | **0.92883** | 3.500e-5 | — | — | 257 016 | **eval** (loss 0.33541, entropy 0.16267) |
| 100 | 4.172 | 0.08721 | 0.97563 | 3.500e-5 | 0.11911 | 0.39304 | 267 858 | train |
| 105 | 4.387 | 0.08412 | 0.97421 | 2.667e-5 | 0.11931 | 0.39703 | 281 444 | train |
| 110 | 4.602 | 0.08632 | 0.97556 | 1.833e-5 | 0.11735 | 0.43529 | 295 316 | train |
| 115 | 4.817 | 0.07449 | 0.97733 | 1.000e-5 | 0.10750 | 0.35623 | 309 584 | train |
| 120 | 5.000 | 0.07724 | 0.97577 | 1.667e-6 | 0.11179 | 0.65869 | 321 270 | train |
| **120** | **5.000** | — | **0.92888** | 1.667e-6 | — | — | 321 270 | **eval** (loss 0.34978, entropy 0.15162) |

---

## 4. Checkpoint comparison

| Checkpoint | Эпоха | Global step | Eval loss | Eval token accuracy | Eval entropy | Best global step (согласно state) | Best metric (eval loss) | Примечание |
|------------|-------|-------------|-----------|---------------------|--------------|-------------------------------------|-------------------------|------------|
| `checkpoint-24` | 1.0 | 24 | 0.35554 | 0.91666 | 0.33131 | 48 | 0.31081 | — |
| `checkpoint-48` | 2.0 | 48 | **0.31081** | 0.92492 | 0.23546 | 48 | 0.31081 | **Глобальный best** |
| `checkpoint-72` | 3.0 | 72 | 0.32630 | 0.92233 | 0.18988 | 48 | 0.31081 | Eval loss выше best |
| `checkpoint-96` | 4.0 | 96 | 0.33541 | 0.92883 | 0.16267 | 48 | 0.31081 | Eval loss продолжает расти |
| `checkpoint-120` | 5.0 | 120 | 0.34978 | 0.92888 | 0.15162 | 48 | 0.31081 | Финальный checkpoint |

Все checkpoint-ы согласуются, что лучшая модель — `checkpoint-48`. Это подтверждает раннюю сходимость и переобучение после эпохи 2.

---

## 5. Generation test summary и per-example breakdown

### 5.1 Summary

| Модель | Records | Valid JSON rate | Decision accuracy | MAE score | MAE role | MAE skills | MAE experience | MAE conditions |
|--------|---------|-----------------|-------------------|-----------|----------|------------|----------------|----------------|
| Base Qwen | 9 | 1.0 | 0.222 (22.2%) | 38.33 | `null` | `null` | `null` | `null` |
| Best LoRA Exp 003 | 9 | 1.0 | 0.667 (66.7%) | 22.22 | 7.33 | 6.67 | 5.56 | 4.89 |

Источник: `generation_test/generation_test_report.json` → `base_qwen.summary` и `best_lora.summary`.

### 5.2 Per-example breakdown (best LoRA)

| # | Case type | Вакансия | Reference decision | Reference score | LoRA decision | LoRA score | Decision match | Score AE | Role AE | Skills AE | Experience AE | Conditions AE |
|---|-----------|----------|--------------------|-----------------|---------------|------------|----------------|----------|---------|-----------|---------------|---------------|
| 1 | `obvious_match` | Prompt Engineer / AI Automation Specialist | match | 60.0 | no_match | 54.0 | ❌ | 6.0 | 2.0 | 1.0 | 3.0 | 0.0 |
| 2 | `obvious_match` | Системный аналитик | match | 98.0 | no_match | 43.0 | ❌ | 55.0 | 27.0 | 25.0 | 3.0 | 0.0 |
| 3 | `obvious_match` | Специалист по разметке данных | no_match | 36.0 | no_match | 50.0 | ✅ | 14.0 | 5.0 | 2.0 | 3.0 | 14.0 |
| 4 | `obvious_no_match` | Prompt Engineer / AI Automation Specialist | no_match | 19.0 | no_match | 46.0 | ✅ | 27.0 | 5.0 | 7.0 | 15.0 | 0.0 |
| 5 | `obvious_no_match` | Системный аналитик | no_match | 39.0 | no_match | 45.0 | ✅ | 6.0 | 5.0 | 6.0 | 5.0 | 0.0 |
| 6 | `obvious_no_match` | Специалист по разметке данных | no_match | 27.0 | no_match | 58.0 | ✅ | 31.0 | 8.0 | 3.0 | 5.0 | 15.0 |
| 7 | `borderline` | Prompt Engineer / AI Automation Specialist | no_match | 20.0 | no_match | 42.0 | ✅ | 22.0 | 2.0 | 2.0 | 3.0 | 15.0 |
| 8 | `borderline` | Системный аналитик | no_match | 25.0 | no_match | 45.0 | ✅ | 20.0 | 5.0 | 7.0 | 8.0 | 0.0 |
| 9 | `borderline` | Специалист по разметке данных | match | 64.0 | no_match | 45.0 | ❌ | 19.0 | 7.0 | 7.0 | 5.0 | 0.0 |

Источник: `generation_test/generation_test_report.json` → `best_lora.results[*].metadata`, `teacher`, `parsed_output`, `metrics`.

### 5.3 Base Qwen per-example decisions (для сравнения)

| # | Case type | Вакансия | Reference decision | Base Qwen decision | Decision match |
|---|-----------|----------|--------------------|--------------------|----------------|
| 1 | `obvious_match` | Prompt Engineer / AI Automation Specialist | match | match | ✅ |
| 2 | `obvious_match` | Системный аналитик | match | match | ✅ |
| 3 | `obvious_match` | Специалист по разметке данных | no_match | match | ❌ |
| 4 | `obvious_no_match` | Prompt Engineer / AI Automation Specialist | no_match | match | ❌ |
| 5 | `obvious_no_match` | Системный аналитик | no_match | match | ❌ |
| 6 | `obvious_no_match` | Специалист по разметке данных | no_match | match | ❌ |
| 7 | `borderline` | Prompt Engineer / AI Automation Specialist | no_match | match | ❌ |
| 8 | `borderline` | Системный аналитик | no_match | match | ❌ |
| 9 | `borderline` | Специалист по разметке данных | match | no_match | ❌ |

Base Qwen корректно решил только 2 из 9 примеров, причём оба — очевидные match. Все no_match и borderline примеры base модель либо завысила до match, либо (в одном случае) занизила match до no_match.

---

## 6. Runtime smoke detailed results

### 6.1 Summary

| Метрика | Значение | Источник |
|---------|----------|----------|
| Total cases | 7 | `runtime_smoke_report.json` → `total_cases` |
| Passed | 7 | `runtime_smoke_report.json` → `passed` |
| Failed | 0 | `runtime_smoke_report.json` → `failed` |
| Pass rate | 1.0 (100%) | `runtime_smoke_report.json` → `pass_rate` |
| Unexpected matches | 0 | `runtime_smoke_report.json` → `unexpected_matches` |
| Latency min | 6 566 мс | `runtime_smoke_report.json` → `results[3].api_response.latency_ms` (SMOKE-EDGECASE-001) |
| Latency max | 19 161 мс | `runtime_smoke_report.json` → `results[0].api_response.latency_ms` (SMOKE-POSITIVE-001) |
| Timestamp | 2026-07-22T02:16:27Z | `runtime_smoke_report.json` → `timestamp` |

### 6.2 Per-case breakdown

| Case code | Category | Vacancy | Decision | Score | Latency, ms | Valid JSON | Passed | Unexpected match |
|-----------|----------|---------|----------|-------|-------------|------------|--------|------------------|
| SMOKE-POSITIVE-001 | positive | Prompt Engineer / AI Automation Specialist | match | 85.0 | 19 161 | ✅ | ✅ | ❌ |
| SMOKE-NEGATIVE-001 | obvious_negative | Prompt Engineer / AI Automation Specialist | no_match | 0.0 | 17 286 | ✅ | ✅ | ❌ |
| SMOKE-HARDNEG-001 | hard_negative | Prompt Engineer / AI Automation Specialist | no_match | 10.0 | 17 563 | ✅ | ✅ | ❌ |
| SMOKE-EDGECASE-001 | edge_case | Prompt Engineer / AI Automation Specialist | no_match | 0.0 | 6 566 | ✅ | ✅ | ❌ |
| SMOKE-HARDNEG-002 | hard_negative | Prompt Engineer / AI Automation Specialist | no_match | 10.0 | 13 395 | ✅ | ✅ | ❌ |
| SMOKE-INVALID-001 | invalid_input | Prompt Engineer / AI Automation Specialist | no_match | 0.0 | 10 640 | ✅ | ✅ | ❌ |
| SMOKE-STABILITY-001 | stability_repeat | Prompt Engineer / AI Automation Specialist | match | 85.0 | 12 184 | ✅ | ✅ | ❌ |

Категория `stability_repeat` повторяет `positive` пример и показывает детерминированность: оба вызова вернули score=85.0 и decision=match.

### 6.3 Category-level pass/total

| Category | Total | Passed | Share |
|----------|-------|--------|-------|
| positive | 1 | 1 | 14.3% |
| obvious_negative | 1 | 1 | 14.3% |
| hard_negative | 2 | 2 | 28.6% |
| edge_case | 1 | 1 | 14.3% |
| invalid_input | 1 | 1 | 14.3% |
| stability_repeat | 1 | 1 | 14.3% |
| **Total** | **7** | **7** | **100%** |

---

## 7. Test evaluation summary

| Модель | Eval loss | Eval runtime, с | Eval samples/sec | Eval steps/sec | Примечание |
|--------|-----------|-----------------|------------------|----------------|------------|
| Base Qwen | 7.897119998931885 | 2.6123 | 3.445 | 3.445 | — |
| Best LoRA Exp 003 | 8.257781982421875 | 1.794 | 5.017 | 5.017 | LoRA быстрее в throughput, но loss выше |

Источник: `test_evaluation/test_metrics.json` → `base_qwen` и `best_lora`.

**Интерпретация:** стандартная held-out eval loss для LoRA выше, чем у base Qwen, на маленьком 9-записном тесте. Это согласуется с наблюдением в `OPERATION_LOG.md`: loss-based метрика не является ведущим бизнес-индикатором; генеративная accuracy — ведущий показатель.

---

## 8. Состав датасета (Experiment 003)

| Split | Records | Candidates | obvious_match | obvious_no_match | borderline | Примечание |
|-------|---------|------------|---------------|------------------|------------|------------|
| train | 93 | 31 | 24 | 36 | 33 | Основной обучающий набор |
| validation | 15 | 5 | 3 | 6 | 6 | Early-stopping / best checkpoint selection |
| test | 9 | 3 | 3 | 3 | 3 | Generation test |
| holdout | 6 | 2 | 0 | 6 | 0 | Hard-negative holdout (только no_match) |
| **Total** | **123** | **41** | **30** | **51** | **42** | 41 кандидат × 3 вакансии |

Источник: `finetuning/data/manifest_experiment_003.json`.

---

## 9. Предлагаемые новые визуальные артефакты

Предлагаемые ID в диапазонах **G-101…G-199**, **D-101…D-199**, **C-101…C-199**, **T-101…T-199**.

### 9.1 Графики (G)

| ID | Название | Раздел | Главный вывод | Источник данных | Примечание |
|----|----------|--------|---------------|-----------------|------------|
| **G-101** | Exp 003 Training Dynamics — Loss & Eval Loss | Engineering Appendix / Training Story | Eval loss достигает минимума на эпохе 2, затем растёт — раннее переобучение | `checkpoint-120/trainer_state.json` → `log_history` | Двойная ось или два subplots: train loss + eval loss |
| **G-102** | Exp 003 Token Accuracy & Entropy Dynamics | Engineering Appendix / Training Story | Модель быстро выучила формат JSON (accuracy >0.92 с первой эпохи), entropy монотонно падает | `checkpoint-120/trainer_state.json` → `log_history` | Twin-Y: token accuracy (0–1) + entropy (0–1.3) |
| **G-103** | Exp 003 Predicted vs Reference Score Scatter | Main Story / Experiment 003 | Hard negatives сдвинули предсказания вниз, но истинные match тоже получили низкие score — визуализация precision/recall компромисса | `generation_test/generation_test_report.json` → `best_lora.results` | Диагональ reference=y=x; точки по case_type цветом |
| **G-104** | Exp 003 Per-Component MAE Breakdown | Engineering Appendix | Наибольшая ошибка — по роли (`mae_role=7.33`), наименьшая — по условиям (`mae_conditions=4.89`) | `generation_test/generation_test_report.json` → `best_lora.summary` | Горизонтальный bar chart |
| **G-105** | Exp 003 Runtime Smoke Latency Distribution | Engineering Appendix | Latency неоптимизированного API варьируется 6.6–19.2 с | `runtime_smoke_report.json` → `results[*].api_response.latency_ms` | Box plot + точки по категориям |

### 9.2 Диаграммы (D)

| ID | Название | Раздел | Главный вывод | Источник данных | Примечание |
|----|----------|--------|---------------|-----------------|------------|
| **D-101** | Exp 003 Dataset Composition by Split & Case Type | Teacher Dataset / Experiment 003 | Holdout состоит полностью из hard negatives (`obvious_no_match`), train — сбалансирован по case_type | `finetuning/data/manifest_experiment_003.json` | Stacked bars или Sankey-like flow |
| **D-102** | Exp 003 Precision / Recall Trade-off Diagram | Main Story / Experiment 003 | Hard negatives убили false positives, но снизили recall: 6 правильных no_match vs 3 упущенных match | `generation_test/generation_test_report.json` | 2×2 confusion-style icons |
| **D-103** | Exp 003 Best Checkpoint at Epoch 2 vs Full 5 Epochs | Training Story | Почему обучение остановилось не на финальной эпохе | `checkpoint-120/trainer_state.json` + `training_report.json` | Timeline с маркером best checkpoint |

### 9.3 Карточки (C)

| ID | Название | Раздел | Главный вывод | Источник данных | Примечание |
|----|----------|--------|---------------|-----------------|------------|
| **C-101** | Exp 003 Hard Negative Smoke Example Card | Main Story / Experiment 003 | Конкретные hard negative cases (Data Analyst → Prompt Engineer, junior Python → Prompt Engineer) корректно отклонены со score=10 | `runtime_smoke_report.json` → `results[2]` и `results[4]` | До/после: base Qwen vs LoRA (base выдавал match) |
| **C-102** | Exp 003 Overfit Warning Card | Training Story | Лучшая модель — на эпохе 2 из 5; дальнейшее обучение только ухудшало eval loss | `checkpoint-120/trainer_state.json` + `training_report.json` | Визуал "stop here" |
| **C-103** | Exp 003 Edge Case / Invalid Input Robustness Card | Production Reality Check | Модель устойчива к искажённым/невалидным входам: invalid_input и edge_case прошли с no_match | `runtime_smoke_report.json` → `results[3]`, `results[5]` | Мини-карточка с примером входа |

### 9.4 Таблицы (T)

| ID | Название | Раздел | Главный вывод | Источник данных | Примечание |
|----|----------|--------|---------------|-----------------|------------|
| **T-101** | Exp 003 Full Per-Example Generation Test Table | Engineering Appendix | Каждая из 9 записей с reference и LoRA-предсказанием, decision match, component errors | `generation_test/generation_test_report.json` | Сортируемая таблица для рецензентов |
| **T-102** | Exp 003 Runtime Smoke Details Table | Engineering Appendix | Все 7 smoke cases: category, latency, decision, score, pass/fail | `runtime_smoke_report.json` | Сопровождает G-105 |
| **T-103** | Exp 003 Dataset Split Composition Table | Methodology | Структура train/val/test/holdout по case_type | `finetuning/data/manifest_experiment_003.json` | Сопровождает D-101 |

---

## 10. Выявленные пропуски и ограничения

| Пропуск / ограничение | Где ожидалось | Влияние на повествование | Возможное действие |
|-----------------------|---------------|--------------------------|--------------------|
| Нет отдельной оценки holdout (`holdout.jsonl`, 6 записей) | `experiment_003/holdout_evaluation/` | Holdout заявлен как hard-negative, но нет метрик; нельзя количественно доказать качество на hard negatives | Провести generation test на `holdout.jsonl` и сохранить отчёт |
| Нет generation test для промежуточных checkpoint | `experiment_003/checkpoint-{24,72,96,120}/` | Неизвестно, как менялась decision accuracy внутри обучения; лучший checkpoint выбран только по eval loss | Провести per-checkpoint generation test в будущих экспериментах |
| Нет per-component ошибок для base Qwen | `generation_test/generation_test_report.json` → `base_qwen.summary` | Нельзя сравнить, в каких компонентах LoRA улучшилась больше всего | Добавить sub-component MAE для base в скрипте оценки |
| Нет precision / recall / F1 по score-threshold | `generation_test/` | Decision accuracy — бинарная метрика; не видно, где проходит порог | Добавить threshold sweep |
| Нет confusion matrix | `generation_test/` | Трудно быстро оценить баланс FP/FN | Добавить confusion matrix в отчёт |
| Нет calibration curve | `generation_test/` | Неизвестно, насколько predicted score калиброван относительно reference score | Добавить scatter + reliability diagram |
| Маленький test set (9 записей) | `data/test.jsonl` | Высокая дисперсия метрик; 66.7% — точка на малой выборке | Расширить test set или внешнюю валидацию |
| Test set не содержит hard negatives напрямую | `data/manifest_experiment_003.json` | Hard-negative качество проверено только через runtime smoke (7 cases) | Включить hard negatives в generation test или отдельный holdout evaluation |
| Loss-based eval_loss выше у LoRA | `test_evaluation/test_metrics.json` | Конфликт с business-метрикой; требует явного объяснения в повествовании | Использовать как доказательство ограничения perplexity-метрик |
| Нет разложения latency по стадиям | `experiment_003/` | Неизвестно, где именно теряется 6.6–19.2 с | Провести latency profiling (как в последующих экспериментах) |
| Нет GPU utilization time series | `experiment_003/` | Не видно, был ли bottleneck в compute или memory | Добавить nvidia-smi логирование |
| Нет примеров teacher reasoning для hard negatives | `generation_test/` | Нельзя показать, насколько LoRA воспроизводит teacher rationale | Добавить reason-similarity metric |

---

## 11. Наблюдения для narrative blueprint

1. **Hard negatives убили false positives.** Base Qwen на generation test принял 6 из 7 no_match/borderline записей за match (FP). Exp 003 LoRA корректно отклонила все 6 no_match/borderline примеров в test и все 4 hard-negative/edge/invalid сценария в runtime smoke. Это ключевое достижение эксперимента.

2. **Recall упал.** LoRA пропустила 3 истинных match из 9: системного аналитика на Prompt Engineer (score 54 vs reference 60), системного аналитика на собственную вакансию (score 43 vs reference 98) и content-менеджера на специалиста по разметке данных (score 45 vs reference 64). Модель стала консервативной — хорошо отсеивает негативы, но занижает score на «почти подходящих» кандидатах.

3. **Ранняя остановка на эпохе 2.** Несмотря на 5 запланированных эпох, лучший checkpoint — `checkpoint-48` (epoch 2). Eval loss вырос с 0.3108 (epoch 2) до 0.3498 (epoch 5), в то время как train loss упал до 0.0772. Это чёткая иллюстрация переобучения и обоснование early stopping по eval loss.

4. **Loss-based метрика врёт.** На 9-записном тесте eval_loss LoRA (8.26) выше, чем у base Qwen (7.90), хотя генеративная accuracy выросла с 22.2% до 66.7%. Это центральный тезис для раздела «почему offline-метрики недостаточны».

5. **Production smoke прошёл идеально.** 7/7, 0 unexpected matches, стабильный повтор positive case. Это показывает, что модель держит формат JSON и решения под API-нагрузкой.

6. **Latency ещё не оптимизирован.** Диапазон 6.6–19.2 с на неоптимизированном API — отправная точка для истории оптимизации (vLLM, warm process), которая разворачивается в Exp 004 и позже.

7. **Датасет engineering важнее тюнинга адаптера.** LoRA параметры неизменны относительно Exp 002, но качество пошло в другую сторону из-за изменения состава датасета. Это подтверждает narrative: ключевой рычаг — данные, не архитектура.

---

## 12. Источники и cross-references

- `finetuning/runs/experiment_003/README.md`
- `finetuning/runs/experiment_003/OPERATION_LOG.md`
- `finetuning/runs/experiment_003/training_report.json`
- `finetuning/runs/experiment_003/trainer_state.json`
- `finetuning/runs/experiment_003/checkpoint-{24,48,72,96,120}/trainer_state.json`
- `finetuning/runs/experiment_003/best_adapter/adapter_config.json`
- `finetuning/runs/experiment_003/generation_test/generation_test_report.json`
- `finetuning/runs/experiment_003/test_evaluation/test_metrics.json`
- `finetuning/runs/experiment_003/runtime_smoke_report.json`
- `finetuning/data/manifest_experiment_003.json`
- `../../landing/docs/visual_assets_registry.md`
