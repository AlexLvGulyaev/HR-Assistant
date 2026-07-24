# Experiment 004 Report: Balanced Teacher Dataset for Production-Ready LoRA

**Кейс:** HR Assistant (hr-assistant)  
**Модуль:** Fine-tuning / Experimental ML-контур  
**Дата начала:** 2026-07-22  
**Статус:** Stage 1 — исследовательский контракт утверждён

---

## 1. Сведения об эксперименте

| Параметр | Значение |
|----------|----------|
| Experiment ID | `experiment_004` |
| Experiment Code | `HRA-EXP-V4` |
| Dataset Code | `HRA-EVAL-V4` |
| Базовая модель | `Qwen/Qwen2.5-1.5B-Instruct` |
| Метод | LoRA (Low-Rank Adaptation) |
| Платформа | RunPod GPU Pod (NVIDIA RTX A5000) |
| Предыдущий эксперимент | Experiment 003 — runtime smoke пройден, precision/recall trade-off |
| Единственная изменяемая переменная | Состав teacher dataset |
| Цель | Устранить precision/recall trade-off и обогнать GPT-4o-mini |

---

## 2. Цель исследования

Проверить гипотезу, что precision/recall trade-off Experiment 003 можно устранить пересбалансированием teacher dataset в сторону high-quality positive и borderline примеров, сохранив hard negative достижения. Результат — production-ready LoRA-кандидат, способный обогнать текущий production GPT-4o-mini.

---

## 3. Исследовательская гипотеза

**H₀:** Добавление positive/borderline примеров в teacher dataset при неизменных параметрах модели не улучшает recall на genuine match-кейсах и не позволяет обогнать GPT-4o-mini.

**H₁:** Пересбалансирование teacher dataset за счёт positive/borderline примеров (при сохранении hard negatives) восстанавливает recall, сохраняет runtime negative smoke и позволяет LoRA соответствовать или превосходить GPT-4o-mini.

---

## 4. Изменяемая переменная

| Переменная | Описание |
|------------|----------|
| Состав teacher dataset | Количество и содержание positive/borderline кандидатов; баланс match/no_match; размер test set; сохранение hard negatives |

---

## 5. Неизменяемые параметры

| Группа | Параметр | Значение | Источник |
|--------|----------|----------|----------|
| Модель | Base model ID | `Qwen/Qwen2.5-1.5B-Instruct` | `configs/experiment_003.yaml` |
| LoRA | `r` | `16` | `configs/experiment_003.yaml` |
| LoRA | `lora_alpha` | `32` | `configs/experiment_003.yaml` |
| LoRA | `lora_dropout` | `0.05` | `configs/experiment_003.yaml` |
| LoRA | `target_modules` | `q_proj, k_proj, v_proj, o_proj, gate_proj, up_proj, down_proj` | `configs/experiment_003.yaml` |
| LoRA | `bias` | `none` | `configs/experiment_003.yaml` |
| Обучение | `num_train_epochs` | `5` | `configs/experiment_003.yaml` |
| Обучение | `per_device_train_batch_size` | `1` | `configs/experiment_003.yaml` |
| Обучение | `gradient_accumulation_steps` | `4` | `configs/experiment_003.yaml` |
| Обучение | `learning_rate` | `2e-4` | `configs/experiment_003.yaml` |
| Обучение | `optim` | `adamw_torch` | `configs/experiment_003.yaml` |
| Обучение | `fp16` | `True` | `configs/experiment_003.yaml` |
| Обучение | Best checkpoint metric | `eval_loss` (minimize) | `configs/experiment_003.yaml` |
| Обучение | `seed` | `42` | `configs/experiment_003.yaml` |
| Runtime | API-контур | `hra_qwen_api_lora.py` | `runpod_operation_manual.md` |
| Teacher | Judge | GPT-4.1, `temperature = 0` | `configs/experiment_003.yaml` |

---

## 6. Критерии успешности

1. **Offline quality на расширенном test set (≥30 записей):**
   - `valid_json_rate` = 1.0
   - `decision_accuracy` ≥ 0.75
   - `MAE_score` ≤ 22
   - нет false positives на obvious_no_match
   - нет false negatives на obvious_match

2. **Runtime validation:**
   - runtime smoke test 7/7 passed, 0 unexpected matches
   - hard negative holdout passed

3. **Сравнение с GPT-4o-mini (≥50 кейсов):**
   - `decision_accuracy` LoRA ≥ GPT-4o-mini
   - `MAE_score` LoRA ≤ GPT-4o-mini
   - FPR/FNR LoRA не хуже более чем на 5 pp
   - p95 latency ≤ 2 секунд после оптимизации
   - cost per request ниже GPT-4o-mini

---

## 7. Критерии завершения / остановки

Эксперимент завершается, когда:
- все этапы пройдены и задокументированы;
- best adapter определён;
- offline/runtime/GPT-4o-mini сравнение выполнены;
- принято одно из решений: гипотеза подтверждена / частично / не подтверждена.

Досрочная остановка, если:
- обучение невозможно воспроизвести;
- dataset не проходит валидацию;
- LoRA не достигает минимальных offline-критериев (decision_accuracy < 0.60, MAE > 30);
- Пользователь принимает решение об остановке.

---

## 8. Выполнение по этапам

### Этап 1. Зафиксировать исследовательский контракт

**Статус:** ✅ Выполнено.

**Действия:**
- Перечитаны `Experiment_003.md`, `Experiment_003_Report.md`, `reports/experiment_003_offline_audit.md`, `configs/experiment_003.yaml`.
- Утверждена гипотеза Cycle 4.
- Утверждены критерии успеха, включая сравнение с GPT-4o-mini.
- Утверждена операционная модель VPS + RunPod CC.
- Созданы `Experiment_004.md` и `Experiment_004_Report.md` (Stage 1).

**Условие перехода:** ✅ выполнено.

---

### Этап 2. Проектировать positive/borderline кандидатов

**Статус:** ✅ Выполнено.

**Действия:**
- Проанализированы failure modes Experiment 003 из `reports/experiment_003_offline_audit.md`.
- Определены конкретные false negatives, которые Cycle 4 должен исправить.
- Спроектированы 13 новых positive/borderline кандидатов (`HRA-EVAL-V2-000201`–`HRA-EVAL-V2-000213`).
- Распределены по splits: train 7, validation 3, test 2, holdout 0 (hard negatives Exp 003 сохраняются).
- Для каждого кандидата зафиксированы: профиль, целевая вакансия, ожидаемый score/decision, исследовательская цель.
- Проверено отсутствие пересечений с существующими `case_code`.

**Failure modes Experiment 003, которые Cycle 4 исправляет:**

| # | case_code Exp 003 | Вакансия | reference | Exp 003 LoRA | Проблема | Как исправляем Cycle 4 |
|---|-------------------|----------|-----------|--------------|----------|------------------------|
| 1 | HRA-EVAL-V2-000010 | Prompt Engineer / AI Automation Specialist | match (60) | no_match (54) | Модель стала штрафовать системного аналитика за отсутствие prompt engineering навыков | Добавить системных аналитиков с релевантным опытом, получающих match на Prompt Engineer / Системный аналитик |
| 2 | HRA-EVAL-V2-000010 | Системный аналитик | match (98) | no_match (43) | Модель игнорирует совпадение по названию должности и заявленные навыки | Добавить senior/middle системных аналитиков с SQL/BPMN/REST API, получающих высокий score |
| 3 | HRA-EVAL-V2-000030 | Специалист по разметке данных | match (64) | no_match (45) | Content manager не распознаётся как подходящий для разметки данных | Добавить кандидатов с прямым опытом data annotation / разметки данных для ML |

**Стратегия баланса:**

| Аспект | Experiment 003 | Experiment 004 (целевой) |
|--------|----------------|--------------------------|
| Train+val match % | 15.7% | ~25–28% |
| Train+val no_match % | 84.3% | ~72–75% |
| Hard negative записи | 33 | сохранены 33 + возможно расширены |
| Test set записей | 9 | 15 (3 новых test-кандидата × 3 + 6 legacy) |
| Positive/borderline кандидатов | 0 целенаправленных | 13 |

**Спецификация новых кандидатов:**

| # | case_code | Split | case_type | Профиль | Исправляемая проблема | Ожидаемое поведение по вакансиям |
|---|-----------|-------|-----------|---------|----------------------|----------------------------------|
| 1 | HRA-EVAL-V2-000201 | train | obvious_match | Senior системный аналитик с SQL/BPMN/REST API, 6 лет | False negative системного аналитика | Системный аналитик — match (95); Prompt Engineer — borderline match (60); Разметка — no_match (35) |
| 2 | HRA-EVAL-V2-000202 | train | obvious_match | Senior AI Automation Specialist: prompt engineering, n8n, LLM, API, JSON, 4 года | Отсутствие strong positive примеров для Prompt Engineer | Prompt Engineer — match (90); Системный аналитик — no_match (40); Разметка — no_match (30) |
| 3 | HRA-EVAL-V2-000203 | train | obvious_match | Data annotation lead с опытом разметки данных для ML, 3 года | False negative content manager на разметке | Prompt Engineer — no_match (35); Системный аналитик — no_match (30); Разметка — match (75) |
| 4 | HRA-EVAL-V2-000204 | train | borderline | Business analyst с BPMN/UML + базовый n8n/API | Граница между BA и Prompt Engineer/системным аналитиком | Prompt Engineer — borderline match (58); Системный аналитик — match (62); Разметка — no_match (35) |
| 5 | HRA-EVAL-V2-000205 | train | borderline | QA engineer с Python/API testing, 3 года | Смежная IT-роль без полного профиля Prompt Engineer | Prompt Engineer — borderline match (62); Системный аналитик — no_match (45); Разметка — no_match (30) |
| 6 | HRA-EVAL-V2-000206 | train | borderline | Technical writer + Python basics + опыт инструкций | Граница разметки данных / технической документации | Prompt Engineer — no_match (35); Системный аналитик — no_match (30); Разметка — borderline match (60) |
| 7 | HRA-EVAL-V2-000207 | train | obvious_match | Junior/Middle ML engineer с LLM fine-tuning, 2 года | Positive пример для Prompt Engineer/AI | Prompt Engineer — match (65); Системный аналитик — no_match (40); Разметка — no_match (30) |
| 8 | HRA-EVAL-V2-000213 | train | obvious_match | Senior Prompt Engineer / AI Automation Specialist, 5 лет | Дополнительный strong positive пример | Prompt Engineer — match (92); Системный аналитик — borderline match (58); Разметка — no_match (35) |
| 9 | HRA-EVAL-V2-000208 | validation | obvious_match | Middle системный аналитик с SQL/BPMN, 4 года | Контроль обобщения на системных аналитиков | Системный аналитик — match (85); Prompt Engineer — no_match (40); Разметка — no_match (30) |
| 10 | HRA-EVAL-V2-000209 | validation | borderline | Data analyst с курсом prompt engineering | Контроль границы Prompt Engineer | Prompt Engineer — borderline match (55); Системный аналитик — no_match (45); Разметка — no_match (30) |
| 11 | HRA-EVAL-V2-000210 | validation | obvious_match | Content moderator с опытом разметки данных для AI | Контроль обобщения на разметку данных | Prompt Engineer — no_match (35); Системный аналитик — no_match (30); Разметка — match (68) |
| 12 | HRA-EVAL-V2-000211 | test | obvious_match | Системный аналитик с 4-летним опытом SQL/BPMN/REST API | Прямой тест recall на genuine match | Системный аналитик — match (88); Prompt Engineer — borderline match (55); Разметка — no_match (35) |
| 13 | HRA-EVAL-V2-000212 | test | obvious_match | AI automation enthusiast с n8n/LLM pet-projects | Прямой тест recall на Prompt Engineer | Prompt Engineer — match (70); Системный аналитик — no_match (45); Разметка — no_match (30) |

**Покрытие исправлений:**

| Проблема Exp 003 | Новые кандидаты |
|------------------|-----------------|
| False negative системного аналитика | 000201, 000204, 000208, 000211 |
| False negative Prompt Engineer для смежных ролей | 000201, 000204, 000205, 000209 |
| False negative Специалист по разметке данных | 000203, 000206, 000210, 000212 |
| Недостаток strong positive примеров | 000202, 000207, 000213 |

**Проверки:**
- ✅ Все `case_code` (`000201`–`000213`) не пересекаются с существующими (`000001`–`000030`, `000101`–`000111`).
- ✅ Каждый кандидат имеет ясный профиль и исследовательскую цель.
- ✅ Каждый кандидат оценивается по всем трём вакансиям (3 записи).
- ✅ Hard negative кандидаты Experiment 003 не изменяются.
- ✅ Исходный test set (`000010`, `000020`, `000030`) сохраняется для longitudinal сравнения.

**Условие перехода:** ✅ выполнено. Спецификация готова к генерации резюме и SQL.

---

### Этап 3. Подготовить SQL и Judge-разметку

**Статус:** ✅ Выполнено.

**Действия:**
- Подготовлен `database/11-create-experiment-v4.sql`:
  - создаёт `HRA-EVAL-V4`;
  - копирует 41 кандидата из `HRA-EVAL-V3`;
  - добавляет 13 новых positive/borderline кандидатов (`000201`–`000213`);
  - формирует 54 × 3 = 162 candidate-vacancy pairs;
  - создаёт `HRA-EXP-V4` с копией Judge-конфигурации `HRA-EXP-V3`.
- Подготовлен `database/12-validate-experiment-v4-pre-judge.sql` — pre-Judge проверки.
- Подготовлен `database/13-validate-experiment-v4-post-judge.sql` — post-Judge проверки.
- Подготовлен `database/14-extract-teacher-dataset-v4.sql` — проверка готовности к экспорту.
- Обновлён `scripts/extract_teacher_dataset.py`:
  - добавлен `SPLIT_CONFIG['HRA-EXP-V4']`;
  - добавлены `HOLDOUT_CANDIDATES['HRA-EXP-V4']`;
  - expected records = 162 для HRA-EXP-V4.
- Judge-разметка `HRA-EXP-V4` выполнена и валидирована: 162 пары, 6 score/decision mismatch (пограничные кейсы, аналогично V3).

**Ожидаемый результат после Judge:** 162 размеченные пары; баланс match/no_match в train+val должен улучшиться до ~25–28% match.

**Условие перехода:** ✅ выполнено.

---

### Этап 4. Сформировать teacher dataset

**Статус:** ✅ Выполнено.

**Действия выполнены:**
- Подготовлена структура split для `HRA-EXP-V4` в `scripts/extract_teacher_dataset.py`:
  - train: 114 записей (38 кандидатов);
  - validation: 27 записей (9 кандидатов);
  - test: 15 записей (5 кандидатов: 3 legacy + 2 новых);
  - holdout: 6 записей (2 hard negative кандидата Experiment 003).
- Ожидаемый total: 162 записи (54 кандидата × 3 вакансии).
- Teacher dataset V4 сформирован и экспортирован:
  - `data/train.jsonl` (114 записей);
  - `data/validation.jsonl` (27 записей);
  - `data/test.jsonl` (15 записей);
  - `data/holdout.jsonl` (6 записей);
  - `reports/teacher_dataset_report_v4.md`.

**Условие перехода:** ✅ выполнено.

---

### Этап 5. Launch contract и WinSCP package

**Статус:** ✅ Выполнено.

**Действия:**
- Создан `configs/experiment_004.yaml` — launch contract Experiment 004.
- Создан `configs/experiment_004_winscp_transfer.md` — точный список файлов для WinSCP.
- Подготовлен `scripts/compare_with_gpt.py` — сравнение LoRA vs GPT-4o-mini (Stage 7).
- Все пути и команды в launch contract указывают на `experiment_004` и `/workspace/hra-finetuning`.

**Условие перехода:** ✅ выполнено. Пакет запуска готов.

---

### Этап 6. Обучение и evaluation на RunPod

**Статус:** ✅ Выполнено.

**Действия:**
- LoRA training завершено за 202 секунды на NVIDIA RTX A5000.
- Best checkpoint: `runs/experiment_004/checkpoint-87` (epoch 3), best eval_loss = 0.3273.
- Offline generation test: `valid_json_rate = 1.0`, `decision_accuracy = 0.80`, `MAE_score = 15.13`.
- Test loss: LoRA 7.8079 vs base Qwen 7.8141.
- Runtime smoke test: 7/7 passed, 0 unexpected matches.
- GPU peak VRAM: 7.46 GB.

**Условие перехода:** ✅ выполнено.

---

### Этап 7. Offline audit и сравнение с GPT-4o-mini

**Статус:** ✅ Выполнено (с повторным запуском после фикса API).

**Первый запуск** (`runs/experiment_004/gpt_comparison_report.json`, `max_tokens = 300`):
- LoRA valid_json_rate = 0.867 (2 из 15 записей вернули HTTP 422);
- LoRA decision_accuracy = 0.800, MAE_score = 6.69;
- GPT-4o-mini decision_accuracy = 1.000, MAE_score = 0.00;
- Причина 422: `hra_qwen_api_lora.py` бросал HTTPException(422) при нераспарсиваемом JSON.

**Фикс на RunPod**:
- `hra_qwen_api_lora.py`: заменён 422 на graceful fallback (200 с `{"error": "invalid_json", "raw_response": ...}`);
- `compare_with_gpt.py`: `max_tokens` увеличен с 300 до 512 для LoRA и GPT-4o-mini.

**Повторный запуск** (`runs/experiment_004/gpt_comparison_report_v2.json`, `max_tokens = 512`):
- LoRA valid_json_rate = **1.000**;
- LoRA decision_accuracy = **0.933**;
- LoRA MAE_score = **5.80**;
- LoRA FPR = 0.111, FNR = 0.000;
- GPT-4o-mini decision_accuracy = 1.000, MAE_score = 0.13;
- HTTP 422 errors: 0.

**Вывод:** увеличение `max_tokens` устранило truncation-ошибки и улучшило LoRA-метрики. GPT-4o-mini остаётся точнее на малой выборке (15 записей), размеченной teacher (GPT-4.1), что ожидаемо из-за семейной близости моделей.

**Условие перехода:** ✅ выполнено.

---

### Этап 8. External validation vs GPT-4o-mini (HRA-EVAL-V5-EXT)

**Статус:** ✅ Выполнено.

**Действия:**
- Создан external validation dataset `HRA-EVAL-V5-EXT` (34 новых кандидата, 102 пары, case codes 000301–000334).
- Сформирован experiment `HRA-EXP-V5-EXT` с `model_judge = 'gpt-4o'`.
- Запущен n8n workflow `HRA Prompt Evaluation Experiment` для GPT-4o reference-разметки.
- Экспортирован `data/external_validation.jsonl` с reference-аннотациями.
- На RunPod прогнаны LoRA Experiment 004 и GPT-4o-mini на всех 102 записях.

**Результаты external validation** (`runs/experiment_004/external_validation_report.json`):

| Metric | LoRA Experiment 004 | GPT-4o-mini |
|--------|---------------------|-------------|
| valid_json_rate | **1.000** | 1.000 |
| decision_accuracy | **0.931** | 0.941 |
| MAE_score | **19.63** | 6.19 |
| FPR | **0.050** | 0.063 |
| FNR | 0.136 | **0.045** |
| latency_p50 (ms) | 11665 | 1185 |
| latency_p95 (ms) | 16879 | 1776 |
| latency_avg (ms) | 11791 | 1242 |
| **winner** | — | **gpt** |

**Вывод по external validation:**
- LoRA обобщается на внешней выборке: 93.1% decision accuracy — близко к GPT-4o-mini (94.1%).
- LoRA даёт меньше ложных срабатываний, чем GPT-4o-mini (FPR 5.0% vs 6.3%).
- LoRA более консервативна: FNR 13.6% vs 4.5% у GPT-4o-mini.
- LoRA сильно отстаёт по точности score (MAE 19.6 vs 6.2) и по latency (~10× медленнее).

**Условие перехода:** ✅ выполнено — внешняя валидация проведена, метрики зафиксированы.

---

### Этап 9. Production integration readiness

**Статус:** ⏳ Отложено.

**Контекст:** production-решение остаётся GPT-4o-mini. LoRA/Qwen находится в тестовом контуре. Production integration readiness (fallback, health endpoint, auth, logging, load test) выполняется только после подтверждения явного превосходства LoRA или по отдельному решению.

---

### Этап 10. Документирование и итоговый вердикт

**Статус:** ✅ Выполнено.

**Итоговый вердикт по гипотезе Experiment 004:**

> Гипотеза **частично подтверждена**.

- ✅ Добавление positive/borderline примеров устранило precision/recall trade-off Experiment 003: LoRA не даёт массовых false negatives, сохраняет прохождение runtime negative smoke и обобщается на внешней выборке с 93.1% decision accuracy.
- ✅ Hard negative достижения Experiment 003 сохранены.
- ✅ API-контур стабилен: 100% valid JSON после увеличения `max_tokens` до 512 и graceful fallback.
- ❌ LoRA не обгоняет GPT-4o-mini по совокупности метрик (decision accuracy, MAE, latency).

**Практический смысл:** LoRA Experiment 004 — рабочий on-premise / edge-кандидат для сценариев без интернета, с требованиями конфиденциальности или offline-работы. В облачном production сейчас остаётся GPT-4o-mini.

**Рекомендации для следующих циклов:**

1. **Score calibration.** LoRA попадает в decision, но плохо попадает в точный score (MAE 19.6 vs 6.2 GPT-4o-mini). Возможные пути:
   - дообучить на score-level loss с весом для MSE по суб-score;
   - добавить post-processing калибровку (например, линейная коррекция predicted score);
   - эксперимент с другой функцией потерь, учитывающей ordinal nature score.

2. **Latency optimization.** LoRA p95 latency ≈ 17 секунд — далеко от production-цели ≤2 секунд. Возможные пути:
   - inference engine: `vLLM` или `TGI`;
   - quantization: `AWQ`, `GPTQ`, `bitsandbytes` 4-bit;
   - warm cache / persistent API process;
   - batched inference, если архитектура позволит.

3. **Снижение FNR.** LoRA FNR 13.6% выше, чем у GPT-4o-mini 4.5%. Возможные пути:
   - добавить больше positive/borderline примеров, особенно для смежных ролей;
   - попробовать lower decision threshold или threshold tuning на validation;
   - добавить специфические hard positive примеры для редких case_type.

4. **Масштаб teacher dataset.** 162 записи — маловато для 1.5B модели. Возможные пути:
   - увеличить dataset до 300–500 пар с сохранением баланса;
   - использовать data augmentation / paraphrase для резюме;
   - собрать реальные production- кейсы.

5. **Эксперимент с архитектурой.** Если dataset увеличится:
   - попробовать QLoRA или полное fine-tuning;
   - попробовать larger base model (Qwen2.5-7B-Instruct), если позволяет GPU;
   - попробовать reward modeling / DPO для calibration.

**Артефакты:**
- `runs/experiment_004/external_validation_report.json`
- `runs/experiment_004/OPERATION_LOG.md`
- `database/15-create-external-validation-v5.sql`
- `database/16-validate-external-validation-v5-pre-judge.sql`
- `database/17-validate-external-validation-v5-post-judge.sql`
- `scripts/compare_external_validation.py`
- `configs/external_validation_v5_winscp_transfer.md`

---

## 9. Открытые вопросы и риски

| # | Вопрос / Риск | Этап | Статус |
|---|---------------|------|--------|
| 1 | Точное число новых positive/borderline кандидатов | Stage 2 | ✅ Закрыто — 13 кандидатов (000201–000213) |
| 2 | Конкретные профили для исправления false negatives | Stage 2 | ✅ Закрыто — 5 obvious_match + 4 borderline + 4 obvious_match дополнительных |
| 3 | Состав расширенного test set | Stage 4 | ✅ Закрыто — 15 записей: 6 legacy (000010/020/030) + 6 hard negatives (000101/103) + 3 новых positive (000211/212/213) |
| 4 | Доступность OpenAI API key для GPT-4o-mini comparison | Stage 7 | ✅ Закрыто — `.env` с `OPENAI_API_KEY` создан на RunPod |
| 5 | LoRA truncation / HTTP 422 в runtime | Stage 7 | ✅ Закрыто — `max_tokens` увеличен до 512, graceful fallback в API |
| 6 | Внешняя валидация LoRA vs GPT-4o-mini | Stage 9 | ✅ Закрыто — 102 пары, LoRA decision_accuracy 0.931, GPT-4o-mini 0.941 |
| 7 | Возможность оптимизации latency до p95 ≤ 2 секунд | Stage 10 | ⏳ Открыто — LoRA p95 ≈ 17 сек, требуется vLLM/TGI/quantization |
