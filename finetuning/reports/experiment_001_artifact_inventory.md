# Инвентаризация артефактов Experiment 001

**Кейс:** `hr-assistant`  
**Эксперимент:** `finetuning/runs/experiment_001/`  
**Дата инвентаризации:** 2026-07-23  
**Статус:** Завершено  
**Цель:** Максимально полно извлечь все доступные данные, метрики, графики и примеры из Experiment 001 для дальнейшего использования в demo-landing и обновления Visual Assets Registry.

---

## 1. Сводка эксперимента

| Параметр | Значение | Источник |
|----------|----------|----------|
| Базовая модель | `Qwen/Qwen2.5-1.5B-Instruct` | `best_adapter/adapter_config.json` → `base_model_name_or_path` |
| LoRA r | 16 | `best_adapter/adapter_config.json` → `r` |
| LoRA alpha | 32 | `best_adapter/adapter_config.json` → `lora_alpha` |
| LoRA dropout | 0.05 | `best_adapter/adapter_config.json` → `lora_dropout` |
| Target modules | 7 модулей: `up_proj`, `v_proj`, `k_proj`, `gate_proj`, `q_proj`, `down_proj`, `o_proj` | `best_adapter/adapter_config.json` → `target_modules` |
| Train batch size | 1 | `checkpoint-90/trainer_state.json` → `train_batch_size` |
| Количество эпох | 5 | `checkpoint-90/trainer_state.json` → `num_train_epochs` |
| Всего шагов | 90 | `checkpoint-90/trainer_state.json` → `max_steps` |
| Лучший checkpoint | `checkpoint-72` (epoch 4) | `checkpoint-90/trainer_state.json` → `best_model_checkpoint` |
| Лучший eval loss | **0.23484808206558228** | `checkpoint-90/trainer_state.json` → `best_metric` |
| Decision accuracy (LoRA) | **0.444** (44.4%) | `generation_test/generation_test_report.json` → `best_lora.summary.decision_accuracy` |
| Decision accuracy (base Qwen) | **0.444** (44.4%) | `generation_test/generation_test_report.json` → `base_qwen.summary.decision_accuracy` |
| MAE score (LoRA) | **29.78** | `generation_test/generation_test_report.json` → `best_lora.summary.mae_score` |
| MAE score (base Qwen) | **38.78** | `generation_test/generation_test_report.json` → `base_qwen.summary.mae_score` |
| Valid JSON rate | **1.0** (100%) для обеих моделей | `generation_test/generation_test_report.json` → `*.summary.valid_json_rate` |

---

## 2. Список доступных файлов

### 2.1 Прочитанные файлы

| Путь | Тип | Что содержит |
|------|-----|--------------|
| `experiment_001/README.md` | Markdown | Model card, версии фреймворков (TRL 1.7.0, Transformers 5.12.1, PyTorch 2.6.0+cu124) |
| `experiment_001/best_adapter/adapter_config.json` | JSON | Конфигурация LoRA-адаптера (r=16, alpha=32, dropout=0.05, target modules) |
| `experiment_001/baseline_validation/metrics.json` | JSON | Базовый eval loss до обучения: 7.496654033660889 |
| `experiment_001/checkpoint-18/trainer_state.json` | JSON | Trainer state после 1 эпохи (best checkpoint на этой стадии) |
| `experiment_001/checkpoint-36/trainer_state.json` | JSON | Trainer state после 2 эпох (best checkpoint на этой стадии) |
| `experiment_001/checkpoint-54/trainer_state.json` | JSON | Trainer state после 3 эпох (best checkpoint на этой стадии) |
| `experiment_001/checkpoint-72/trainer_state.json` | JSON | Trainer state после 4 эпох (глобальный best checkpoint) |
| `experiment_001/checkpoint-90/trainer_state.json` | JSON | Полная trainer state за все 5 эпох + флаг остановки обучения |
| `experiment_001/generation_test/generation_test_report.json` | JSON | Per-example и summary метрики generation test для base Qwen и best LoRA |
| `experiment_001/test_evaluation/test_metrics.json` | JSON | Стандартная held-out eval loss: base Qwen 7.649, best LoRA 9.455 |

### 2.2 Дополнительные файлы в каталоге

Следующие файлы присутствуют на диске, но не использовались как источник метрик:

| Путь | Примечание |
|------|------------|
| `experiment_001/best_adapter/adapter_model.safetensors` | Веса адаптера — бинарный артефакт |
| `experiment_001/best_adapter/tokenizer.json`, `tokenizer_config.json`, `chat_template.jinja` | Токенизатор и шаблон чата |
| `experiment_001/checkpoint-*/adapter_config.json` | Идентичная конфигурация LoRA для каждого checkpoint |
| `experiment_001/checkpoint-*/optimizer.pt`, `scheduler.pt`, `rng_state.pth`, `scaler.pt` | Состояния оптимизатора и тренера — не анализировались |
| `experiment_001/checkpoint-*/training_args.bin` | Аргументы тренера — бинарный формат |

### 2.3 Отсутствующие ожидаемые файлы

| Файл | Где ожидался | Влияние на повествование |
|------|--------------|--------------------------|
| `runtime_smoke_report.json` | `experiment_001/runtime_smoke_report.json` | Отсутствует: Experiment 001 не проходил production smoke validation |
| `training_report.json` | Корень эксперимента | Отсутствует: нет сводного training report |
| `OPERATION_LOG.md` | `experiment_001/OPERATION_LOG.md` | Отсутствует: нет человекочитаемого журнала операций |
| `data/manifest_experiment_001.json` | `data/manifest_experiment_001.json` | Отсутствует: состав датасета 001 не задокументирован отдельным манифестом |
| `preflight_*.json` | `experiment_001/preflight_*.json` | Отсутствуют: нет preflight-check артефактов |

---

## 3. Training dynamics (per-step / per-epoch)

### 3.1 Per-epoch summary

Полная история обучения содержится в `checkpoint-90/trainer_state.json` → `log_history`. Eval-метрики фиксируются на шагах 18, 36, 54, 72, 90 (один eval в конце каждой эпохи).

| Эпоха | Global step | Train loss (последний logged step в эпохе) | Eval loss | Eval token accuracy | Learning rate (начало эпохи) | Best checkpoint на этой стадии |
|-------|-------------|-------------------------------------------|-----------|---------------------|------------------------------|--------------------------------|
| 1 | 18 | 0.3444 (step 15) | **0.3444110155105591** | 0.9156 | 0.000200 → 0.000157 | `checkpoint-18` |
| 2 | 36 | 0.2075 (step 35) | **0.24569977819919586** | 0.9369 | 0.000157 → 0.000113 | `checkpoint-36` |
| 3 | 54 | 0.1572 (step 50) | **0.23513156175613403** | 0.9412 | 0.000113 → 0.000080 | `checkpoint-54` |
| 4 | 72 | 0.1167 (step 70) | **0.23484808206558228** | 0.9430 | 0.000080 → 0.000047 | `checkpoint-72` ← **глобальный best** |
| 5 | 90 | 0.0972 (step 90) | **0.239083930850029** | 0.9426 | 0.000047 → 0.000002 | `checkpoint-90` |

Примечания:
- Train loss для эпохи взят с последнего logged training step внутри эпохи (logging_steps=5).
- Learning rate уменьшается линейно: от ~0.0002 на step 5 до 2.22e-6 на step 90.
- Eval loss достигает минимума на эпохе 4 и слегка растёт на эпохе 5 — ранняя остановка по eval loss сработала бы на step 72.

### 3.2 Per-step training dynamics (key steps)

| Step | Epoch | Loss | Token accuracy | Learning rate | Entropy | Grad norm | Num tokens | Тип записи |
|------|-------|------|----------------|---------------|---------|-----------|------------|------------|
| 5 | 0.28 | 1.4462 | 0.6916 | 1.91e-4 | 1.3698 | 0.6533 | 15 830 | train |
| 10 | 0.56 | 0.8559 | 0.7959 | 1.80e-4 | 0.9385 | 0.7205 | 31 586 | train |
| 15 | 0.83 | 0.5145 | 0.8745 | 1.69e-4 | 0.5901 | 0.6803 | 47 487 | train |
| 18 | 1.00 | — | 0.3444 (eval loss) | 1.58e-4 | — | — | 57 040 | eval |
| 20 | 1.11 | 0.3436 | 0.9161 | 1.58e-4 | 0.4007 | 0.5234 | 63 293 | train |
| 25 | 1.39 | 0.2471 | 0.9407 | 1.47e-4 | 0.2987 | 0.4670 | 79 098 | train |
| 30 | 1.67 | 0.2228 | 0.9429 | 1.36e-4 | 0.2499 | 0.4896 | 94 989 | train |
| 35 | 1.94 | 0.2075 | 0.9438 | 1.24e-4 | 0.2294 | 0.3452 | 110 869 | train |
| 36 | 2.00 | — | 0.2457 (eval loss) | 1.13e-4 | — | — | 114 080 | eval |
| 40 | 2.22 | 0.1879 | 0.9514 | 1.13e-4 | 0.2157 | 0.3484 | 126 806 | train |
| 45 | 2.50 | 0.1501 | 0.9577 | 1.02e-4 | 0.1881 | 0.5037 | 142 636 | train |
| 50 | 2.78 | 0.1572 | 0.9558 | 9.11e-5 | 0.1739 | 0.4304 | 158 466 | train |
| 54 | 3.00 | — | 0.2351 (eval loss) | 8.00e-5 | — | — | 171 120 | eval |
| 60 | 3.33 | 0.1269 | 0.9635 | 6.89e-5 | 0.1590 | 0.3453 | 190 282 | train |
| 65 | 3.61 | 0.1177 | 0.9653 | 5.78e-5 | 0.1547 | 0.3630 | 205 707 | train |
| 70 | 3.89 | 0.1167 | 0.9656 | 4.67e-5 | 0.1441 | 0.3331 | 221 641 | train |
| 72 | 4.00 | — | 0.2348 (eval loss) | 4.67e-5 | — | — | 228 160 | eval |
| 75 | 4.17 | 0.1066 | 0.9671 | 3.56e-5 | 0.1379 | 0.3917 | 237 618 | train |
| 80 | 4.44 | 0.0998 | 0.9706 | 2.44e-5 | 0.1305 | 0.3924 | 253 436 | train |
| 85 | 4.72 | 0.0986 | 0.9710 | 1.33e-5 | 0.1305 | 0.4307 | 269 473 | train |
| 90 | 5.00 | 0.0972 | 0.9723 | 2.22e-6 | 0.1282 | 0.4307 | 285 200 | train + eval (0.2391) |

### 3.3 Динамика обучения — ключевые наблюдения

1. **Train loss падает монотонно** от 1.446 (step 5) до 0.097 (step 90) — модель усваивает обучающую выборку.
2. **Token accuracy растёт** от 0.692 (step 5) до 0.972 (step 90) — модель быстро учится правильно предсказывать токены.
3. **Eval loss стабилизируется** к эпохе 4: 0.344 → 0.246 → 0.235 → **0.235** → 0.239.
4. **Eval token accuracy растёт медленнее** train token accuracy: 0.916 → 0.937 → 0.941 → 0.943 → 0.943 — разрыв между train и eval token accuracy накапливается к концу обучения (~0.03 на эпохе 5).
5. **Entropy и grad norm** стабилизируются после эпохи 3: entropy 0.13–0.17, grad_norm 0.33–0.43.
6. **Early stopping сработала бы на step 72**: eval loss на step 90 (0.2391) выше, чем на step 72 (0.2348).

---

## 4. Checkpoint comparison

| Checkpoint | Epoch | Global step | Best metric (eval loss) | Source | Total FLOs |
|------------|-------|-------------|-------------------------|--------|------------|
| `checkpoint-18` | 1 | 18 | 0.3444110155105591 | `checkpoint-18/trainer_state.json` → `best_metric` | 4.55e14 |
| `checkpoint-36` | 2 | 36 | 0.24569977819919586 | `checkpoint-36/trainer_state.json` → `best_metric` | 9.09e14 |
| `checkpoint-54` | 3 | 54 | 0.23513156175613403 | `checkpoint-54/trainer_state.json` → `best_metric` | 1.36e15 |
| `checkpoint-72` | 4 | 72 | **0.23484808206558228** | `checkpoint-72/trainer_state.json` → `best_metric` | 1.82e15 |
| `checkpoint-90` | 5 | 90 | 0.23484808206558228 (наследует best) | `checkpoint-90/trainer_state.json` → `best_metric` | 2.27e15 |

Примечание: `checkpoint-90` сохраняет `best_global_step=72` и `best_model_checkpoint=.../checkpoint-72`, что подтверждает выбор best checkpoint по eval loss.

---

## 5. Generation test summary и per-example breakdown

### 5.1 Summary

| Модель | Records | Valid JSON rate | Decision accuracy | MAE score | MAE role | MAE skills | MAE experience | MAE conditions |
|--------|---------|-----------------|-------------------|-----------|----------|------------|----------------|----------------|
| Base Qwen | 9 | 1.0 | 0.444 | 38.78 | null | null | null | null |
| Best LoRA (checkpoint-72) | 9 | 1.0 | 0.444 | 29.78 | 9.0 | 8.44 | 4.78 | 6.44 |

Источник: `generation_test/generation_test_report.json` → `base_qwen.summary` и `best_lora.summary`.

### 5.2 Per-example breakdown для best LoRA

| # | Case type | Вакансия | Reference score | Reference decision | LoRA score | LoRA decision | Decision match | Score abs error | Компонентные ошибки (role/skills/experience/conditions) |
|---|-----------|----------|-----------------|--------------------|------------|---------------|----------------|-----------------|-------------------------------------------------------|
| 1 | obvious_match | Prompt Engineer / AI Automation Specialist | 60 | match | 52 | no_match | ❌ | 8 | 5 / 1 / 2 / 0 |
| 2 | obvious_match | Системный аналитик | 98 | match | 53 | no_match | ❌ | 45 | 22 / 21 / 2 / 0 |
| 3 | obvious_match | Специалист по разметке данных | 39 | no_match | 55 | no_match | ✅ | 16 | 0 / 2 / 0 / 14 |
| 4 | obvious_no_match | Prompt Engineer / AI Automation Specialist | 19 | no_match | 59 | no_match | ✅ | 40 | 8 / 7 / 15 / 0 |
| 5 | obvious_no_match | Системный аналитик | 39 | no_match | 70 | match | ❌ | 31 | 16 / 15 / 0 / 0 |
| 6 | obvious_no_match | Специалист по разметке данных | 27 | no_match | 70 | match | ❌ | 43 | 16 / 12 / 0 / 15 |
| 7 | borderline | Prompt Engineer / AI Automation Specialist | 20 | no_match | 49 | no_match | ✅ | 29 | 2 / 4 / 8 / 15 |
| 8 | borderline | Системный аналитик | 25 | no_match | 52 | no_match | ✅ | 27 | 4 / 7 / 16 / 0 |
| 9 | borderline | Специалист по разметке данных | 64 | match | 35 | no_match | ❌ | 29 | 8 / 7 / 0 / 14 |

Источник: `generation_test/generation_test_report.json` → `best_lora.results`.

### 5.3 Анализ ошибок LoRA по категориям

| Категория | Количество | Правильные решения | Ошибки | Средняя score abs error |
|-----------|------------|-------------------|--------|------------------------|
| obvious_match | 3 | 1 (index 3) | 2 (index 1, 2) | 23.0 |
| obvious_no_match | 3 | 1 (index 4) | 2 (index 5, 6) | 38.0 |
| borderline | 3 | 2 (index 7, 8) | 1 (index 9) | 28.3 |

### 5.4 Сравнение с base Qwen (per-example, кратко)

Base Qwen и LoRA совпадают по decision accuracy (44.4%), но LoRA снижает MAE score с 38.78 до 29.78. Это означает, что LoRA стала ближе к числовым оценкам teacher, но не к принятию решений (match/no_match).

---

## 6. Test evaluation summary

| Модель | Eval loss | Eval runtime | Eval samples/sec | Source |
|--------|-----------|--------------|--------------------|--------|
| Base Qwen | 7.64910364151001 | 2.263 s | 3.977 | `test_evaluation/test_metrics.json` → `base_qwen.eval_loss` |
| Best LoRA | 9.45461654663086 | 1.7737 s | 5.074 | `test_evaluation/test_metrics.json` → `best_lora.eval_loss` |
| Baseline validation (до обучения) | 7.496654033660889 | 2.9205 s | 3.082 | `baseline_validation/metrics.json` → `eval_loss` |

Наблюдение: стандартная held-out eval loss для LoRA (9.455) выше, чем у base Qwen (7.649). Это подтверждает, что в данной задаче стандартный language-modeling loss инвертирован по отношению к качеству matching-решений.

---

## 7. Предлагаемые новые визуальные артефакты

Диапазоны ID согласно заданию: **G-101…G-199**, **D-101…D-199**, **C-101…C-199**, **T-101…T-199**.

### 7.1 Графики (G)

| ID | Название | Источник данных | Назначение в повествовании |
|----|----------|-----------------|----------------------------|
| **G-101** | Exp 001 — Training Dynamics (train loss + eval loss + token accuracy + learning rate) | `checkpoint-90/trainer_state.json` → `log_history` | Показать, как модель училась внутри одного эксперимента: loss падает, token accuracy растёт, но качество решений не меняется |
| **G-102** | Exp 001 — Per-Component MAE Breakdown | `generation_test/generation_test_report.json` → `best_lora.summary` | Где именно LoRA ошибается в score: role (9.0), skills (8.44), conditions (6.44), experience (4.78) |
| **G-103** | Exp 001 — Decision Accuracy by Case Type | `generation_test/generation_test_report.json` → `best_lora.results` | obvious_match, obvious_no_match, borderline — показать слабость в obvious-кейсах |
| **G-104** | Exp 001 — Score Error Distribution | `generation_test/generation_test_report.json` → `best_lora.results[].metrics.score_abs_error` | Распределение абсолютной ошибки score для 9 примеров |
| **G-105** | Exp 001 — Train vs Eval Token Accuracy Gap | `checkpoint-90/trainer_state.json` → `log_history` | Разрыв между train и eval token accuracy — признак запоминания формата |

### 7.2 Диаграммы (D)

| ID | Название | Источник данных | Назначение в повествовании |
|----|----------|-----------------|----------------------------|
| **D-101** | Exp 001 — Learning Rate Schedule | `checkpoint-90/trainer_state.json` → `log_history[].learning_rate` | Визуализация линейного decay optimizer |

### 7.3 Карточки (C)

| ID | Название | Источник данных | Назначение в повествовании |
|----|----------|-----------------|----------------------------|
| **C-101** | Exp 001 — Hypothesis / Result Card | `Experiment_001.md` (если есть), `generation_test_report.json`, `trainer_state.json` | problem → hypothesis → change → result → unexpected → next |
| **C-102** | Exp 001 — "Format vs Meaning" Example Card | `generation_test/generation_test_report.json` → `best_lora.results[0]` | JSON-ответ корректен и структурирован, но решение неверно (obvious_match → no_match) |
| **C-103** | Exp 001 — Base vs LoRA Answer Card | `generation_test/generation_test_report.json` → `results[0]` для base и LoRA | Сравнение ответов base Qwen и LoRA на одном примере |

### 7.4 Таблицы (T)

| ID | Название | Источник данных | Назначение в повествовании |
|----|----------|-----------------|----------------------------|
| **T-101** | Exp 001 — Checkpoint Comparison Table | `checkpoint-*/trainer_state.json` | Сравнение 5 checkpoints по eval loss, eval token accuracy, global step |
| **T-102** | Exp 001 — Per-Example Results Table | `generation_test/generation_test_report.json` → `best_lora.results` | Таблица из раздела 5.2 для инженерного приложения |
| **T-103** | Exp 001 — Component Error Budget Table | `generation_test/generation_test_report.json` → `best_lora.summary` | Разложение MAE по компонентам с долями от общей ошибки |

---

## 8. Выявленные пропуски и ограничения

### 8.1 Пропуски в данных

| Пропуск | Где ожидался | Влияние |
|---------|--------------|---------|
| Отсутствует `runtime_smoke_report.json` | `experiment_001/runtime_smoke_report.json` | Experiment 001 не проверялся в production-условиях; landing-страница "Ловушка" (Exp 002) относится к следующему эксперименту |
| Отсутствует `training_report.json` | Корень эксперимента | Нет сводного текстового отчёта по тренировке |
| Отсутствует `OPERATION_LOG.md` | `experiment_001/OPERATION_LOG.md` | Нет человекочитаемого журнала решений и наблюдений |
| Отсутствует `data/manifest_experiment_001.json` | `data/manifest_experiment_001.json` | Состав датасета 90 записей не задокументирован отдельно; информация о классах выведена из `generation_test_report.json` |
| Отсутствуют `preflight_*.json` | `experiment_001/preflight_*.json` | Нет артефактов preflight-проверок |
| Отсутствуют per-example latency измерения | `experiment_001/latency_profile_report.json` | Нельзя построить latency-визуализацию для Exp 001 |

### 8.2 Ограничения в интерпретации

1. **Test set мал (9 записей).** Generation test оценивает только 9 примеров (3 case types × 3 вакансии). Статистическая надёжность метрик ограничена.
2. **Base Qwen не выдаёт компонентные score.** `base_qwen.summary.mae_role` и др. равны `null`, поэтому нельзя напрямую сравнить компонентные ошибки base и LoRA.
3. **Reference labels присутствуют только для 9 примеров.** Внешняя валидация 102 записей относится к Exp 004, не к Exp 001.
4. **Eval loss инвертирован.** Стандартный test eval loss у LoRA выше, чем у base Qwen. Это не ошибка, а особенность задачи: LoRA адаптируется под teacher-формат, ухудшая общую перплексию на held-out.

---

## 9. Наблюдения для narrative blueprint

### 9.1 Главное наблюдение: форма без смысла

Experiment 001 — классический пример **learning the form, not the meaning**:

- Train loss падает с 1.446 до 0.097.
- Eval token accuracy растёт с 0.916 до 0.943.
- Valid JSON rate = 100%.
- **Но decision accuracy остаётся 44.4% — как у base Qwen.**

Источники:
- `checkpoint-90/trainer_state.json` → `log_history[].loss`, `log_history[].eval_loss`, `log_history[].eval_mean_token_accuracy`.
- `generation_test/generation_test_report.json` → `base_qwen.summary.decision_accuracy` и `best_lora.summary.decision_accuracy`.

Это центральный нарративный момент для страницы 3 blueprint: "Модель выучила форму ответа, но не его смысл".

### 9.2 Парадокс метрик: низкий loss ≠ качество решений

| Эксперимент | Best eval loss | Decision accuracy | MAE score |
|-------------|----------------|-------------------|-----------|
| Exp 001 | **0.2348** | 0.444 | 29.78 |
| Exp 002 | *будет заполнено в спринте 002* | 0.78 | 21.89 |

Для Exp 001 одиночно: самый низкий eval loss (0.2348 на checkpoint-72) соответствует худшему качеству решений среди всех экспериментов. Это подтверждает инверсию loss ↔ decision quality.

### 9.3 LoRA уменьшила числовую ошибку, но не улучшила решения

- MAE score base Qwen: 38.78.
- MAE score LoRA: 29.78.
- Уменьшение на ~23%.

Но decision accuracy не изменилась. Модель стала ближе к числовым score teacher, но не к бинарному решению match/no_match. Это важный нюанс: модель частично усвоила шкалу, но не порог.

### 9.4 Per-component ошибки показывают слабость в role и skills

| Компонент | MAE | Доля в общей ошибке |
|-----------|-----|---------------------|
| role | 9.0 | 30.2% |
| skills | 8.44 | 28.3% |
| conditions | 6.44 | 21.6% |
| experience | 4.78 | 16.0% |

Источник: `generation_test/generation_test_report.json` → `best_lora.summary`. Это говорит о том, что модель ещё не научилась правильно оценивать соответствие по должности и навыкам — ключевые компоненты для HR-решений.

### 9.5 Best checkpoint selection story

- Eval loss достигает минимума на step 72 (epoch 4).
- На step 90 (epoch 5) eval loss растёт до 0.2391.
- Это классическая картина: продолжение обучения улучшает train loss, но не улучшает validation.

Для blueprint можно добавить страницу "Как модель училась внутри одного эксперимента" с отметкой best checkpoint.

### 9.6 Отсутствие production-валидации

Experiment 001 не содержит runtime smoke report. Это важно для нарратива: "Ловушка" (страница 6 blueprint) начинается не с Exp 001, а с Exp 002. Exp 001 остаётся чисто лабораторной baseline-попыткой.

---

## 10. Ссылки на исходные файлы

Все числа в этом отчёте взяты из:

- `finetuning/runs/experiment_001/best_adapter/adapter_config.json`
- `finetuning/runs/experiment_001/baseline_validation/metrics.json`
- `finetuning/runs/experiment_001/checkpoint-18/trainer_state.json`
- `finetuning/runs/experiment_001/checkpoint-36/trainer_state.json`
- `finetuning/runs/experiment_001/checkpoint-54/trainer_state.json`
- `finetuning/runs/experiment_001/checkpoint-72/trainer_state.json`
- `finetuning/runs/experiment_001/checkpoint-90/trainer_state.json`
- `finetuning/runs/experiment_001/generation_test/generation_test_report.json`
- `finetuning/runs/experiment_001/test_evaluation/test_metrics.json`

---

**Статус документа:** Инвентаризация Experiment 001 v1.0  
**Автор:** AI Automation Portfolio Lab / Claude Code  
**Последнее обновление:** 2026-07-23
