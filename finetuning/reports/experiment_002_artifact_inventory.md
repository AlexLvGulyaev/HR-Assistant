# Инвентаризация артефактов Experiment 002

**Кейс:** `hr-assistant`  
**Эксперимент:** `finetuning/runs/experiment_002/`  
**Дата инвентаризации:** 2026-07-23  
**Статус:** Завершено  
**Цель:** Максимально полно извлечь все доступные данные, метрики, графики и примеры из Experiment 002 для дальнейшего использования в demo-landing и обновления Visual Assets Registry.

---

## 1. Сводка эксперимента

| Параметр | Значение | Источник |
|----------|----------|----------|
| Базовая модель | `Qwen/Qwen2.5-1.5B-Instruct` | `best_adapter/adapter_config.json` → `base_model_name_or_path` |
| LoRA r | 16 | `best_adapter/adapter_config.json` → `r` |
| LoRA alpha | 32 | `best_adapter/adapter_config.json` → `lora_alpha` |
| LoRA dropout | 0.05 | `best_adapter/adapter_config.json` → `lora_dropout` |
| Target modules | 7 модулей: `gate_proj`, `v_proj`, `o_proj`, `up_proj`, `q_proj`, `down_proj`, `k_proj` | `best_adapter/adapter_config.json` → `target_modules` |
| Train batch size | 1 | `trainer_state.json` → `train_batch_size` |
| Количество эпох (план) | 5 | `trainer_state.json` → `num_train_epochs` |
| Количество эпох (факт обучения) | 3 (остановлено early) | `best_adapter/trainer_state.json` → `epoch=3.0`, `best_model_checkpoint=checkpoint-54` |
| Всего шагов (план) | 90 | `trainer_state.json` → `max_steps` |
| Лучший checkpoint | `checkpoint-54` (epoch 3, step 54) | `best_adapter/trainer_state.json` → `best_model_checkpoint` |
| Лучший eval loss | **0.44427046179771423** | `best_adapter/trainer_state.json` → `best_metric` |
| Decision accuracy (LoRA) | **0.778** (77.8%) | `generation_test/generation_test_report.json` → `best_lora.summary.decision_accuracy` |
| Decision accuracy (base Qwen) | **0.444** (44.4%) | `generation_test/generation_test_report.json` → `base_qwen.summary.decision_accuracy` |
| MAE score (LoRA) | **21.89** | `generation_test/generation_test_report.json` → `best_lora.summary.mae_score` |
| MAE score (base Qwen) | **38.78** | `generation_test/generation_test_report.json` → `base_qwen.summary.mae_score` |
| Valid JSON rate | **1.0** (100%) для обеих моделей | `generation_test/generation_test_report.json` → `*.summary.valid_json_rate` |

**Ключевое отличие от Exp 001:** те же 90 записей датасета, но увеличена ёмкость адаптера (r=8→16, target_modules 4→7) и изменены гиперпараметры. Результат: резкий рост decision accuracy 44.4% → 77.8%.

---

## 2. Список доступных файлов

### 2.1 Прочитанные файлы

| Путь | Тип | Что содержит |
|------|-----|--------------|
| `experiment_002/README.md` | Markdown | Model card, версии фреймворков |
| `experiment_002/best_adapter/adapter_config.json` | JSON | Конфигурация LoRA-адаптера (r=16, alpha=32, dropout=0.05, 7 target modules) |
| `experiment_002/best_adapter/trainer_state.json` | JSON | Trainer state на момент best checkpoint (epoch 3, step 54) |
| `experiment_002/trainer_state.json` | JSON | Идентичен `best_adapter/trainer_state.json` — финальное состояние после остановки на epoch 3 |
| `experiment_002/checkpoint-18/trainer_state.json` | JSON | Trainer state после 1 эпохи |
| `experiment_002/checkpoint-36/trainer_state.json` | JSON | Trainer state после 2 эпох (best на этой стадии) |
| `experiment_002/checkpoint-54/trainer_state.json` | JSON | Trainer state после 3 эпох (глобальный best) |
| `experiment_002/checkpoint-72/trainer_state.json` | JSON | Trainer state после 4 эпох (eval loss уже выше best) |
| `experiment_002/checkpoint-90/trainer_state.json` | JSON | Trainer state после 5 эпох (обучение завершено, но best остался на step 54) |
| `experiment_002/generation_test/generation_test_report.json` | JSON | Per-example и summary метрики generation test для base Qwen и best LoRA |
| `finetuning/FINETUNING_ENGINEERING_REPORT.md` | Markdown | Разделы 4 и 6: параметры Exp 002, результаты, runtime smoke failures |

### 2.2 Дополнительные файлы в каталоге

| Путь | Примечание |
|------|------------|
| `experiment_002/best_adapter/adapter_model.safetensors` | Веса адаптера — бинарный артефакт |
| `experiment_002/best_adapter/tokenizer.json`, `tokenizer_config.json`, `chat_template.jinja` | Токенизатор и шаблон чата |
| `experiment_002/checkpoint-*/adapter_config.json` | Идентичная конфигурация LoRA для каждого checkpoint |
| `experiment_002/checkpoint-*/optimizer.pt`, `scheduler.pt`, `rng_state.pth`, `scaler.pt` | Состояния оптимизатора и тренера — не анализировались |
| `experiment_002/checkpoint-*/training_args.bin` | Аргументы тренера — бинарный формат |

### 2.3 Отсутствующие ожидаемые файлы

| Файл | Где ожидался | Влияние на повествование |
|------|--------------|--------------------------|
| `test_evaluation/test_metrics.json` | `experiment_002/test_evaluation/test_metrics.json` | Отсутствует: нет стандартной held-out eval loss метрики для Exp 002 |
| `runtime_smoke_report.json` | `experiment_002/runtime_smoke_report.json` | Отсутствует как отдельный JSON; результаты smoke зафиксированы только текстом в `FINETUNING_ENGINEERING_REPORT.md` |
| `baseline_validation/metrics.json` | `experiment_002/baseline_validation/metrics.json` | Отсутствует: нет отдельного baseline eval перед обучением |
| `OPERATION_LOG.md` | `experiment_002/OPERATION_LOG.md` | Отсутствует: нет человекочитаемого журнала операций |
| `data/manifest_experiment_002.json` | `data/manifest_experiment_002.json` | Отсутствует: состав датасета 002 не задокументирован отдельным манифестом |
| `preflight_*.json` | `experiment_002/preflight_*.json` | Отсутствуют: нет preflight-check артефактов |
| `training_report.json` | Корень эксперимента | Отсутствует: нет сводного training report |

---

## 3. Training dynamics (per-step / per-epoch)

### 3.1 Per-epoch summary

Полная история обучения содержится в `checkpoint-90/trainer_state.json` → `log_history`. Eval-метрики фиксируются на шагах 18, 36, 54, 72, 90. Обучение фактически остановлено на step 54 (epoch 3) по early stopping, хотя checkpoint-72 и checkpoint-90 сохранены позже.

| Эпоха | Global step | Train loss (последний logged step в эпохе) | Eval loss | Eval token accuracy | Learning rate (начало эпохи) | Best checkpoint на этой стадии | Примечание |
|-------|-------------|-------------------------------------------|-----------|---------------------|------------------------------|--------------------------------|------------|
| 1 | 18 | 0.5972 (step 15) | **0.5499804615974426** | 0.8562 | 0.000200 → 0.000157 | `checkpoint-18` | — |
| 2 | 36 | 0.3642 (step 35) | **0.4445136487483978** | 0.8760 | 0.000157 → 0.000113 | `checkpoint-36` | — |
| 3 | 54 | 0.2765 (step 50) | **0.44427046179771423** | 0.8798 | 0.000113 → 0.000080 | `checkpoint-54` ← **глобальный best** | **Обучение остановлено здесь** |
| 4 | 72 | 0.1907 (step 70) | **0.4511646032333374** | 0.8823 | 0.000080 → 0.000047 | `checkpoint-72` | Eval loss выше best |
| 5 | 90 | 0.1485 (step 90) | **0.45717498660087585** | 0.8876 | 0.000047 → 0.000002 | `checkpoint-90` | Eval loss продолжает расти |

Примечания:
- Train loss для эпохи взят с последнего logged training step внутри эпохи.
- `best_adapter/trainer_state.json` фиксирует `epoch=3.0`, `global_step=54`, `best_model_checkpoint=.../checkpoint-54` — это подтверждает, что обучение было прервано после 3 эпох.
- Eval loss достигает плато на эпохах 2–3 и начинает расти на эпохах 4–5, тогда как train loss продолжает падать.

### 3.2 Per-step training dynamics (key steps)

| Step | Epoch | Loss | Token accuracy | Learning rate | Entropy | Grad norm | Num tokens | Тип записи |
|------|-------|------|----------------|---------------|---------|-----------|------------|------------|
| 5 | 0.28 | 1.0292 | 0.7611 | 1.91e-4 | 0.9735 | 0.7471 | 15 810 | train |
| 10 | 0.56 | 0.7593 | 0.8149 | 1.80e-4 | 0.8559 | 0.8224 | 31 546 | train |
| 15 | 0.83 | 0.5972 | 0.8524 | 1.69e-4 | 0.5866 | 0.8657 | 47 427 | train |
| 18 | 1.00 | — | 0.5500 (eval loss) | 1.58e-4 | — | — | 56 968 | eval |
| 20 | 1.11 | 0.4844 | 0.8752 | 1.58e-4 | 0.5247 | 0.7751 | 63 213 | train |
| 25 | 1.39 | 0.3976 | 0.8943 | 1.47e-4 | 0.4859 | 0.7038 | 78 998 | train |
| 30 | 1.67 | 0.3982 | 0.8880 | 1.36e-4 | 0.4126 | 0.7657 | 94 869 | train |
| 35 | 1.94 | 0.3642 | 0.8966 | 1.24e-4 | 0.3820 | 0.6384 | 110 729 | train |
| 36 | 2.00 | — | 0.4445 (eval loss) | 1.13e-4 | — | — | 113 936 | eval |
| 40 | 2.22 | 0.3433 | 0.9046 | 1.13e-4 | 0.3983 | 0.6911 | 126 646 | train |
| 45 | 2.50 | 0.2505 | 0.9213 | 1.02e-4 | 0.3197 | 0.7616 | 142 456 | train |
| 50 | 2.78 | 0.2765 | 0.9212 | 9.11e-5 | 0.2877 | 0.7661 | 158 266 | train |
| 54 | 3.00 | — | 0.4443 (eval loss) | 8.00e-5 | — | — | 170 904 | eval |
| 60 | 3.33 | 0.2177 | 0.9369 | 6.89e-5 | 0.2816 | 0.6711 | 190 042 | train |
| 65 | 3.61 | 0.2030 | 0.9356 | 5.78e-5 | 0.2628 | 0.7046 | 205 447 | train |
| 70 | 3.89 | 0.1907 | 0.9430 | 4.67e-5 | 0.2423 | 0.5955 | 221 361 | train |
| 72 | 4.00 | — | 0.4512 (eval loss) | 4.67e-5 | — | — | 227 872 | eval |
| 75 | 4.17 | 0.1703 | 0.9470 | 3.56e-5 | 0.2288 | 0.7717 | 237 318 | train |
| 80 | 4.44 | 0.1600 | 0.9536 | 2.44e-5 | 0.2147 | 0.7288 | 253 116 | train |
| 85 | 4.72 | 0.1570 | 0.9533 | 1.33e-5 | 0.2102 | 0.7700 | 269 133 | train |
| 90 | 5.00 | 0.1485 | 0.9545 | 2.22e-6 | 0.2109 | 0.8557 | 284 840 | train + eval (0.4572) |

### 3.3 Динамика обучения — ключевые наблюдения

1. **Eval loss достигает плато на эпохах 2–3:** 0.4445 → 0.4443 (разница всего 0.0002).
2. **После эпохи 3 eval loss растёт:** 0.4443 → 0.4512 → 0.4572. Это признак overfit на обучающую выборку.
3. **Train loss продолжает падать** даже после роста eval loss: 0.2765 (step 50) → 0.1485 (step 90). Разрыв между train и eval loss увеличивается.
4. **Train token accuracy растёт**, но eval token accuracy растёт медленнее: train 0.9545 vs eval 0.8876 на step 90 — разрыв ~0.067.
5. **Grad norm не снижается к концу**, а на step 90 достигает 0.856 — модель продолжает активно обновлять веса, но уже не в направлении обобщения.
6. **Entropy eval стабилизируется** около 0.25–0.31, в то время как train entropy падает до 0.21.

### 3.4 Почему обучение остановлено на 3 эпохах

Остановка на step 54 (epoch 3) объясняется комбинацией факторов:

- **Early stopping по eval loss:** `best_adapter/trainer_state.json` указывает `best_model_checkpoint=checkpoint-54` и `best_metric=0.4443`. Это означает, что после step 54 eval loss не улучшался.
- **Плато + рост eval loss:** epoch 4 и epoch 5 показывают eval loss 0.4512 и 0.4572 — выше best.
- **Рост train loss vs eval loss gap:** к epoch 5 разрыв достигает ~0.31 (train 0.1485 vs eval 0.4572), что указывает на переобучение.
- **Практический выбор:** в `FINETUNING_ENGINEERING_REPORT.md` указано "Лучший чекпоинт: Epoch 3, step 54, eval_loss=0.44".

---

## 4. Checkpoint comparison

| Checkpoint | Epoch | Global step | Best metric (eval loss) | Source | Total FLOs | Примечание |
|------------|-------|-------------|-------------------------|--------|------------|------------|
| `checkpoint-18` | 1 | 18 | 0.5499804615974426 | `checkpoint-18/trainer_state.json` → `best_metric` | 4.54e14 | — |
| `checkpoint-36` | 2 | 36 | 0.4445136487483978 | `checkpoint-36/trainer_state.json` → `best_metric` | 9.08e14 | — |
| `checkpoint-54` | 3 | 54 | **0.44427046179771423** | `checkpoint-54/trainer_state.json` → `best_metric` | 1.36e15 | **Глобальный best, обучение остановлено** |
| `checkpoint-72` | 4 | 72 | 0.44427046179771423 (наследует best) | `checkpoint-72/trainer_state.json` → `best_metric` | 1.82e15 | Eval loss на этой стадии: 0.4512 |
| `checkpoint-90` | 5 | 90 | 0.44427046179771423 (наследует best) | `checkpoint-90/trainer_state.json` → `best_metric` | 2.27e15 | Eval loss на этой стадии: 0.4572 |

Примечание: несмотря на то, что checkpoint-72 и checkpoint-90 сохранены и содержат полную `log_history`, они сохраняют `best_global_step=54` и `best_model_checkpoint=.../checkpoint-54`. Это означает, что обучение продолжалось, но best checkpoint остался на epoch 3.

---

## 5. Generation test summary и per-example breakdown

### 5.1 Summary

| Модель | Records | Valid JSON rate | Decision accuracy | MAE score | MAE role | MAE skills | MAE experience | MAE conditions |
|--------|---------|-----------------|-------------------|-----------|----------|------------|----------------|----------------|
| Base Qwen | 9 | 1.0 | 0.444 | 38.78 | null | null | null | null |
| Best LoRA (checkpoint-54) | 9 | 1.0 | 0.778 | 21.89 | 5.67 | 7.0 | 4.56 | 4.89 |

Источник: `generation_test/generation_test_report.json` → `base_qwen.summary` и `best_lora.summary`.

### 5.2 Per-example breakdown для best LoRA

| # | Case type | Вакансия | Reference score | Reference decision | LoRA score | LoRA decision | Decision match | Score abs error | Компонентные ошибки (role/skills/experience/conditions) |
|---|-----------|----------|-----------------|--------------------|------------|---------------|----------------|-----------------|-------------------------------------------------------|
| 1 | obvious_match | Prompt Engineer / AI Automation Specialist | 60 | match | 70 | match | ✅ | 10 | 5 / 5 / 0 / 0 |
| 2 | obvious_match | Системный аналитик | 98 | match | 97 | match | ✅ | 1 | 2 / 1 / 0 / 0 |
| 3 | obvious_match | Специалист по разметке данных | 39 | no_match | 60 | no_match | ✅ | 21 | 0 / 7 / 0 / 14 |
| 4 | obvious_no_match | Prompt Engineer / AI Automation Specialist | 19 | no_match | 57 | no_match | ✅ | 38 | 8 / 10 / 20 / 0 |
| 5 | obvious_no_match | Системный аналитик | 39 | no_match | 55 | no_match | ✅ | 16 | 6 / 10 / 0 / 0 |
| 6 | obvious_no_match | Специалист по разметке данных | 27 | no_match | 72 | match | ❌ | 45 | 16 / 14 / 0 / 15 |
| 7 | borderline | Prompt Engineer / AI Automation Specialist | 20 | no_match | 47 | no_match | ✅ | 27 | 2 / 2 / 8 / 15 |
| 8 | borderline | Системный аналитик | 25 | no_match | 40 | no_match | ✅ | 15 | 5 / 7 / 13 / 0 |
| 9 | borderline | Специалист по разметке данных | 64 | match | 40 | no_match | ❌ | 24 | 7 / 7 / 0 / 0 |

Источник: `generation_test/generation_test_report.json` → `best_lora.results`.

### 5.3 Анализ ошибок LoRA по категориям

| Категория | Количество | Правильные решения | Ошибки | Средняя score abs error |
|-----------|------------|-------------------|--------|------------------------|
| obvious_match | 3 | 2 (index 1, 2) | 1 (index 3 — score error 21, но decision совпал) | 10.7 |
| obvious_no_match | 3 | 2 (index 4, 5) | 1 (index 6 — false positive) | 33.0 |
| borderline | 3 | 2 (index 7, 8) | 1 (index 9 — false negative) | 22.0 |

Важно: среди 9 примеров только **2 ошибки по decision**: index 6 (obvious_no_match → match, false positive) и index 9 (borderline match → no_match, false negative).

### 5.4 False positive пример — центральный для нарратива "Ловушка"

Index 6 — obvious_no_match, вакансия "Специалист по разметке данных", кандидат-врач с 15-летним опытом в медицине.

- Reference: score 27, decision `no_match`.
- LoRA Exp 002: score 72, decision `match`.
- Reasoning LoRA: "Кандидат претендует на должность \"Медицинский специалист\", что является смежной... Опыт работы 15 лет полностью соответствует требованиям... Зарплатные ожидания кандидата (200 000) находятся в диапазоне бюджета вакансии (60 000–120 000)... Кандидат хорошо подходит."

Это типичный false positive: модель не распознала, что зарплата 200 000 **выше** максимума 120 000, и приняла нерелевантный профиль за подходящий. Источник: `generation_test/generation_test_report.json` → `best_lora.results[5]`.

---

## 6. Runtime smoke failures

Источник: `finetuning/FINETUNING_ENGINEERING_REPORT.md`, раздел 6 "Runtime Validation", подраздел "Negative Smoke Test".

### 6.1 Smoke test summary

| Категория | Результат Exp 002 | Источник |
|-----------|-------------------|----------|
| Positive matching-запросы | ✅ Pass | `FINETUNING_ENGINEERING_REPORT.md` → "Positive Smoke Test" |
| JSON-структура | ✅ Pass | `FINETUNING_ENGINEERING_REPORT.md` → "Positive Smoke Test" |
| Reasoning | ✅ Pass | `FINETUNING_ENGINEERING_REPORT.md` → "Positive Smoke Test" |
| Decision | ✅ Pass | `FINETUNING_ENGINEERING_REPORT.md` → "Positive Smoke Test" |
| Пустые поля (negative) | ❌ Fail | `FINETUNING_ENGINEERING_REPORT.md` → "Negative Smoke Test" |
| Невалидные данные (negative) | ❌ Fail | `FINETUNING_ENGINEERING_REPORT.md` → "Negative Smoke Test" |
| Edge cases (negative) | ❌ Fail | `FINETUNING_ENGINEERING_REPORT.md` → "Negative Smoke Test" |

### 6.2 Интерпретация

- Positive smoke пройден: модель корректно обрабатывала стандартные matching-запросы и возвращала валидный JSON.
- Negative smoke не пройден: модель не справлялась с пустыми полями, невалидными данными и edge cases.
- Это стало триггером для Experiment 003: гипотеза заключалась в том, что причиной является недостаток hard negative и edge case-примеров в teacher dataset.

### 6.3 Пропуски в детализации smoke failures

- Нет конкретных примеров запросов, на которых произошёл fail.
- Нет JSON-отчёта `runtime_smoke_report.json` для Exp 002.
- В `FINETUNING_ENGINEERING_REPORT.md` результаты агрегированы до уровня категорий (Pass/Fail).

---

## 7. Предлагаемые новые визуальные артефакты

Диапазоны ID согласно заданию: **G-101…G-199**, **D-101…D-199**, **C-101…C-199**, **T-101…T-199**. Для Exp 002 используем следующие ID (продолжая нумерацию после Exp 001, но в том же диапазоне):

### 7.1 Графики (G)

| ID | Название | Источник данных | Назначение в повествовании |
|----|----------|-----------------|----------------------------|
| **G-106** | Exp 002 — Training Dynamics (train loss + eval loss + token accuracy + learning rate) | `checkpoint-90/trainer_state.json` → `log_history` | Показать плато eval loss и рост после epoch 3 — обоснование early stopping |
| **G-107** | Exp 002 — Eval Loss Plateau and Rise | `checkpoint-90/trainer_state.json` → `log_history` (eval points) | Наглядная визуализация: eval loss стабилизируется на 0.444 и растёт после step 54 |
| **G-108** | Exp 002 — Per-Component MAE Breakdown | `generation_test/generation_test_report.json` → `best_lora.summary` | Сравнение с Exp 001: role MAE снизилось с 9.0 до 5.67 |
| **G-109** | Exp 002 — Decision Accuracy by Case Type | `generation_test/generation_test_report.json` → `best_lora.results` | obvious_match, obvious_no_match, borderline — рост точности |
| **G-110** | Exp 002 — Score Error Distribution | `generation_test/generation_test_report.json` → `best_lora.results[].metrics.score_abs_error` | Распределение ошибки score |
| **G-111** | Exp 002 — Train vs Eval Token Accuracy Gap | `checkpoint-90/trainer_state.json` → `log_history` | Разрыв train/eval token accuracy увеличивается к концу |

### 7.2 Диаграммы (D)

| ID | Название | Источник данных | Назначение в повествовании |
|----|----------|-----------------|----------------------------|
| **D-102** | Exp 002 — Early Stopping Decision Diagram | `best_adapter/trainer_state.json`, `checkpoint-90/trainer_state.json` | Почему обучение остановлено на step 54: eval loss plateau + rise |
| **D-103** | Exp 002 — Positive/Negative Smoke Result | `FINETUNING_ENGINEERING_REPORT.md` → раздел 6 | Матрица smoke pass/fail для Exp 002 |

### 7.3 Карточки (C)

| ID | Название | Источник данных | Назначение в повествовании |
|----|----------|-----------------|----------------------------|
| **C-104** | Exp 002 — Hypothesis / Result Card | `FINETUNING_ENGINEERING_REPORT.md` → раздел 4 | problem → hypothesis → change (r=16, 7 modules) → result → unexpected (negative smoke fail) → next |
| **C-105** | Exp 002 — False Positive Example Card | `generation_test/generation_test_report.json` → `best_lora.results[5]` | Врач на вакансию специалиста по разметке данных: score 27 → 72, decision no_match → match |
| **C-106** | Exp 002 — Before/After vs Exp 001 Card | `generation_test_report.json` (Exp 001 и Exp 002) | Сравнение ответов на одном примере (например, index 1) между Exp 001 и Exp 002 |

### 7.4 Таблицы (T)

| ID | Название | Источник данных | Назначение в повествовании |
|----|----------|-----------------|----------------------------|
| **T-104** | Exp 002 — Checkpoint Comparison Table | `checkpoint-*/trainer_state.json` | Сравнение 5 checkpoints по eval loss и eval token accuracy |
| **T-105** | Exp 002 — Per-Example Results Table | `generation_test/generation_test_report.json` → `best_lora.results` | Таблица из раздела 5.2 |
| **T-106** | Exp 002 — Component Error Budget Table | `generation_test/generation_test_report.json` → `best_lora.summary` | Разложение MAE по компонентам с долями |
| **T-107** | Exp 002 — Smoke Test Result Table | `FINETUNING_ENGINEERING_REPORT.md` → раздел 6 | Категории positive/negative smoke и Pass/Fail |

---

## 8. Выявленные пропуски и ограничения

### 8.1 Пропуски в данных

| Пропуск | Где ожидался | Влияние |
|---------|--------------|---------|
| Отсутствует `test_evaluation/test_metrics.json` | `experiment_002/test_evaluation/test_metrics.json` | Нет стандартной held-out eval loss метрики для Exp 002; нельзя сравнить с Exp 001 по test eval loss |
| Отсутствует `runtime_smoke_report.json` | `experiment_002/runtime_smoke_report.json` | Smoke результаты задокументированы только текстом в `FINETUNING_ENGINEERING_REPORT.md` |
| Отсутствует `baseline_validation/metrics.json` | `experiment_002/baseline_validation/metrics.json` | Нет baseline eval loss до обучения |
| Отсутствует `OPERATION_LOG.md` | `experiment_002/OPERATION_LOG.md` | Нет человекочитаемого журнала операций |
| Отсутствует `data/manifest_experiment_002.json` | `data/manifest_experiment_002.json` | Состав датасета не задокументирован отдельно |
| Отсутствуют `preflight_*.json` | `experiment_002/preflight_*.json` | Нет preflight-check артефактов |
| Отсутствует `training_report.json` | Корень эксперимента | Нет сводного training report |

### 8.2 Ограничения в интерпретации

1. **Test set мал (9 записей).** Generation test оценивает только 9 примеров. Статистическая надёжность метрик ограничена.
2. **Smoke failures не детализированы.** Известно, что negative smoke не пройден, но нет конкретных запросов и ответов модели.
3. **Base Qwen не выдаёт компонентные score.** Как и в Exp 001, `base_qwen.summary.mae_role` и др. равны `null`.
4. **Обучение продолжалось до epoch 5, но best checkpoint на epoch 3.** Checkpoint-72 и checkpoint-90 сохранены, но не использовались как best. Это важно для понимания процесса, но может создавать путаницу при визуализации ("почему есть 5 checkpoints, но обучение остановлено на 3").

---

## 9. Наблюдения для narrative blueprint

### 9.1 Главное наблюдение: ёмкость модели решает

Experiment 002 показывает резкий рост качества при **том же датасете**, но **с изменённой ёмкостью адаптера**:

| Метрика | Exp 001 | Exp 002 | Изменение |
|---------|---------|---------|-----------|
| LoRA r | 16 | 16 | — |
| Target modules | 7 | 7 | — |
| Decision accuracy | 0.444 | **0.778** | +33.4 pp |
| MAE score | 29.78 | **21.89** | −7.89 |
| Best eval loss | 0.2348 | **0.4443** | +0.21 (хуже по ML-метрике) |

Источники:
- Exp 001: `finetuning/runs/experiment_001/generation_test/generation_test_report.json`.
- Exp 002: `finetuning/runs/experiment_002/generation_test/generation_test_report.json`.

**Парадокс повторяется:** более высокий eval loss (0.4443) соответствует лучшему качеству решений (77.8%). Это ещё одно подтверждение, что для данной задачи validation loss не коррелирует с business-метрикой.

### 9.2 Почему quality выросло: не только ёмкость

Согласно `FINETUNING_ENGINEERING_REPORT.md`, в Exp 002 по сравнению с Exp 001 изменилось:

| Параметр | Exp 001 | Exp 002 |
|----------|---------|---------|
| r (rank) | 8 | 16 |
| target_modules | 4 | 7 |
| lora_dropout | 0.1 | 0.05 |
| num_epochs | 3 | 5 (план) |
| learning_rate | 1e-4 | 2e-4 |

То есть изменения касались не только ёмкости, но и dropout, learning rate и learning rate schedule. Нельзя однозначно атрибутировать рост accuracy только увеличению r.

### 9.3 Early stopping на плато

Exp 002 — хороший пример для страницы blueprint "Как модель училась внутри эксперимента":

- Eval loss на epoch 2: 0.4445.
- Eval loss на epoch 3: 0.4443 (улучшение на 0.0002).
- Eval loss на epoch 4: 0.4512 (рост).
- Eval loss на epoch 5: 0.4572 (дальнейший рост).

Модель продолжала "учиться" по train loss, но перестала обобщаться. Решение остановиться на step 54 — правильное.

### 9.4 Ловушка: production smoke обнаружил слабость

Exp 002 — ключевой момент нарратива "Ловушка" (страница 6 blueprint):

- Offline-метрики улучшились: decision accuracy 77.8%, MAE 21.89.
- Positive smoke пройден.
- **Negative smoke не пройден:** пустые поля, невалидные данные, edge cases.

Это показывает, что offline-метрики не покрывают production-риски. Источник: `FINETUNING_ENGINEERING_REPORT.md` → раздел 6 "Runtime Validation".

### 9.5 False positive — конкретный пример для нарратива

Index 6 (врач на вакансию специалиста по разметке данных) — идеальный пример для карточки C-105:

- Reference: `no_match`, score 27.
- LoRA Exp 002: `match`, score 72.
- Reasoning модели логичен внутри своей логики, но фактически неверен: модель не заметила, что зарплата 200 000 выше бюджета 60 000–120 000.

Это делает абстрактную проблему "negative smoke fail" осязаемой.

### 9.6 Сравнение компонентных ошибок Exp 001 → Exp 002

| Компонент | Exp 001 MAE | Exp 002 MAE | Изменение |
|-----------|-------------|-------------|-----------|
| role | 9.0 | 5.67 | −37.0% |
| skills | 8.44 | 7.0 | −17.1% |
| conditions | 6.44 | 4.89 | −24.1% |
| experience | 4.78 | 4.56 | −4.6% |

Рост качества распределился по всем компонентам, но особенно сильно по role. Это показывает, что модель стала лучше понимать соответствие по должности.

---

## 10. Ссылки на исходные файлы

Все числа в этом отчёте взяты из:

- `finetuning/FINETUNING_ENGINEERING_REPORT.md` (разделы 4 и 6)
- `finetuning/runs/experiment_002/best_adapter/adapter_config.json`
- `finetuning/runs/experiment_002/best_adapter/trainer_state.json`
- `finetuning/runs/experiment_002/trainer_state.json`
- `finetuning/runs/experiment_002/checkpoint-18/trainer_state.json`
- `finetuning/runs/experiment_002/checkpoint-36/trainer_state.json`
- `finetuning/runs/experiment_002/checkpoint-54/trainer_state.json`
- `finetuning/runs/experiment_002/checkpoint-72/trainer_state.json`
- `finetuning/runs/experiment_002/checkpoint-90/trainer_state.json`
- `finetuning/runs/experiment_002/generation_test/generation_test_report.json`

---

**Статус документа:** Инвентаризация Experiment 002 v1.0  
**Автор:** AI Automation Portfolio Lab / Claude Code  
**Последнее обновление:** 2026-07-23
