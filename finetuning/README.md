# Модуль Finetuning для HR Assistant

## Назначение

Модуль finetuning для проекта HR Assistant (HRA) — обучение адаптеров для matching кандидат-вакансия.

**ВАЖНО:** Этот модуль является **экспериментальным** и работает изолированно от production.

## Связь с HRA Production

| Аспект | Production | Experimental (этот модуль) |
|--------|------------|----------------------------|
| Workflow | HR Processing Worker | HR Processing Worker - Multi Provider Test |
| LLM | OpenAI GPT-4o-mini | RunPod (Qwen + LoRA) |
| База данных | Production tables | Изолированный teacher dataset |
| Назначение | Обработка реальных запросов | Исследование и тестирование |

**Runtime API:**
- `/workspace/hra_qwen_api.py` — базовая Qwen модель
- `/workspace/hra_qwen_api_lora.py` — Qwen + LoRA адаптер

**Эти API используются только для smoke validation, не для production.**

---

## Архитектурная цепочка

Fine-tuning является **уровнем 2** в экспериментальном ML-контуре HR Assistant:

```
Prompt Engineering
      ↓
Prompt A/B Evaluation (уровень 1)
      ↓
Reference Dataset (Judge оценки)
      ↓
Teacher Dataset (этот модуль)
      ↓
Fine-tuning LoRA (уровень 2)
      ↓
Offline Validation
      ↓
Runtime Smoke Validation (уровень 3)
      ↓
Принятие решения о Production Readiness
```

**Результаты уровня 1 (Prompt Evaluation):**
- HRA-EXP-V1 завершён
- Reference dataset: 90 кейсов с Judge-оценками
- Метрики: MAE, accuracy, latency
- Документация: [docs/prompt_evaluation/](../docs/prompt_evaluation/)

---

## Текущий статус

### Experiment 003 (последний результат)

**Статус:** Завершён 2026-07-22, гипотеза подтверждена частично, не production-ready

**Результаты:**

| Метрика | Base Qwen | Qwen + LoRA (Exp 002) | Qwen + LoRA (Exp 003) |
|---------|-----------|----------------------|-----------------------|
| Dataset | 90 кейсов | 90 кейсов | 123 кейса (+33 hard negative) |
| Best eval_loss | — | 0.44 | **0.31** |
| Offline decision_accuracy | 0.222 / 0.444* | 0.778 | 0.667 |
| Offline MAE_score | 38.33 / 38.78* | 21.89 | 22.22 |
| valid_json_rate | 1.0 | 1.0 | 1.0 |
| Runtime Positive Test | ✅ Pass | ✅ Pass | ✅ Pass |
| Runtime Negative Test | ✅ Pass | ❌ **Failed** | ✅ **Pass (7/7)** |

*Base Qwen результаты различаются между запусками из-за незаданного temperature/sampling; в каждом эксперименте используется собственный base baseline.

**Ключевой вывод:**
- Hard negative примеры **решили проблему runtime negative smoke test**.
- Однако модель стала более консервативной: decision accuracy на исходном test set снизилась с 0.778 до 0.667, появились ложные отрицательные решения.
- Модель **не является production-ready** — требуется баланс precision/recall.

### Cycle 4 / Experiment 004 (завершён)

**Статус:** Обучение завершено 2026-07-22, внутренняя и внешняя валидация пройдены, гипотеза частично подтверждена

**Цель:** Преодолеть precision/recall trade-off Experiment 003 и подготовить LoRA-модель к production сравнением с GPT-4o-mini.

**Гипотеза:**
- Добавить **13 positive/borderline примеров** для восстановления recall на genuine match-кейсах.
- Сохранить **все hard negative примеры Experiment 003**.
- Оставить неизменными модель, LoRA-гиперпараметры и параметры обучения — единственная переменная = состав teacher dataset.
- Добавить **A/B-сравнение с GPT-4o-mini** как production baseline.

**Датасет:**
- 41 кандидат Experiment 003 (90 + 33 hard negative записи) + 13 новых positive/borderline кандидатов = **54 кандидата, 162 записи**
- Train: 114, Validation: 27, Test: 15, Holdout: 6
- SQL-скрипты: `database/11-create-experiment-v4.sql`

**Результаты Experiment 004:**

| Метрика | Base Qwen | LoRA Exp 004 | GPT-4o-mini |
|---------|-----------|--------------|-------------|
| valid_json_rate (internal test, n=15) | 1.0 | 1.0 | 1.0 |
| decision_accuracy | 0.333 | **0.933** | 1.000 |
| MAE_score | 34.13 | **5.80** | 0.13 |
| FPR | — | 0.111 | 0.000 |
| FNR | — | 0.000 | 0.000 |
| Runtime smoke | — | **7/7 pass** | — |

- Обучение: 5 epochs, best checkpoint epoch 3, eval_loss 0.3273.
- Важный инсайт: первоначальные HTTP 422 были вызваны `max_tokens=300` — ответы обрезались. После увеличения до `512` valid_json_rate вырос до 1.0, decision accuracy — с 0.80 до 0.933.

**Результаты external validation (HRA-EVAL-V5-EXT, n=102, GPT-4o reference):**

| Метрика | LoRA Exp 004 | GPT-4o-mini |
|---------|--------------|-------------|
| valid_json_rate | 1.0 | 1.0 |
| decision_accuracy | **0.931** | 0.941 |
| MAE_score | 19.63 | **6.19** |
| FPR | **0.050** | 0.063 |
| FNR | 0.136 | **0.045** |
| latency_p95 | 16.9 сек | **1.8 сек** |

**Итоговый вердикт:** гипотеза частично подтверждена. LoRA обобщается на внешних данных, но не обгоняет GPT-4o-mini. LoRA — рабочий on-premise / edge кандидат.

**Артефакты Cycle 4:**
- [Experiment_004.md](Experiment_004.md) — протокол эксперимента
- [Experiment_004_Report.md](Experiment_004_Report.md) — рабочий отчёт с итоговым вердиктом и рекомендациями
- `configs/experiment_004.yaml` — конфигурация обучения
- `configs/experiment_004_winscp_transfer.md` — список файлов для WinSCP
- `configs/external_validation_v5_winscp_transfer.md` — список файлов для external validation
- `scripts/runtime_smoke_test.py` — runtime smoke test
- `scripts/compare_with_gpt.py` — сравнение LoRA vs GPT-4o-mini (internal test)
- `scripts/compare_external_validation.py` — сравнение LoRA vs GPT-4o-mini (external validation)
- `database/11-create-experiment-v4.sql` — SQL для генерации V4
- `database/15-create-external-validation-v5.sql` — external validation dataset
- `database/16-validate-external-validation-v5-pre-judge.sql` — pre-Judge checks
- `database/17-validate-external-validation-v5-post-judge.sql` — post-Judge checks

---

## Связь с Ped08/Ped09

Модуль служит практической основой для уроков Ped08/Ped09:
- **Ped08:** Подготовка датасета из 90 эталонных HRA-кейсов
- **Ped09:** LoRA/QLoRA finetuning и сравнение моделей

Сравниваем:
- Base Qwen/Qwen2.5-1.5B-Instruct
- Qwen + LoRA адаптер
- Эталонная GPT-модель (базлайн для сравнения качества)

## Инфраструктура

- **Базовая модель:** Qwen/Qwen2.5-1.5B-Instruct
- **Платформа:** RunPod GPU Pod (NVIDIA RTX A5000)
- **Метод:** LoRA (Low-Rank Adaptation), с возможностью QLoRA
- **Рабочий каталог:** `/workspace/hra-finetuning` (на RunPod)

## Изоляция от продакшена

**Важно:** Модуль не затрагивает продакшен-системы:
- Продакшен API `/workspace/hra_qwen_api.py` остаётся без изменений
- Датасет использует анонимизированные кейсы из HRA базы
- Обученные адаптеры экспериментальные до валидации

## Структура каталогов

```
finetuning/
├── README.md                    # Этот файл
├── TECHNICAL_FOUNDATION.md      # Технические спецификации
├── requirements.txt             # Зависимости Python
├── configs/                     # Конфигурации экспериментов
│   └── experiment_001.yaml
├── scripts/                     # Скрипты пайплайна обучения
│   └── prepare_dataset.py
├── data_sample/                 # Анонимизированные примеры
│   └── example.jsonl
├── reports/                     # Отчёты экспериментов
├── data/                        # [gitignore] Реальный датасет
├── runs/                        # [gitignore] Логи обучения
└── models/                      # [gitignore] Загруженные/адаптированные модели
```

## Быстрый старт

```bash
# Установка зависимостей
pip install -r requirements.txt

# Подготовка датасета (требуется доступ к HRA базе)
python scripts/prepare_dataset.py --config configs/experiment_001.yaml

# Обучение (после подготовки датасета)
# python scripts/train.py --config configs/experiment_001.yaml
```

## Текущий статус

**Фаза:** Cycle 4 / Experiment 004 — завершён, гипотеза частично подтверждена

**Выполнено:**
- [x] Структура каталогов
- [x] Техническая документация
- [x] Шаблон конфигурации эксперимента
- [x] Параметризованные скрипты обучения и evaluation (`--config`)
- [x] Каркас скрипта подготовки датасета
- [x] Experiment 001 (базовый)
- [x] Experiment 002 (baseline)
- [x] Experiment 003 (hard negative teacher dataset)
- [x] Offline validation
- [x] Runtime smoke validation
- [x] Автоматический локальный runtime smoke test
- [x] **Проектирование Experiment 004 / Cycle 4**
- [x] **Teacher dataset V4 (162 кейса, +13 positive/borderline)**
- [x] **Конфигурация `experiment_004.yaml`**
- [x] **Launch contract и WinSCP transfer list**
- [x] **Скрипт сравнения с GPT-4o-mini**
- [x] **Обучение Experiment 004 в RunPod CC**
- [x] **Runtime smoke validation (7/7 pass)**
- [x] **A/B-сравнение с GPT-4o-mini на internal test set**
- [x] **External validation dataset V5 (HRA-EVAL-V5-EXT, 102 pairs)**
- [x] **External validation A/B comparison (LoRA vs GPT-4o-mini)**

**Результаты Experiment 003:**
- ✅ Offline validation: eval_loss улучшилась (0.44 → 0.31)
- ✅ Runtime positive test: pass
- ✅ Runtime negative test: **pass (7/7)**
- ⚠️ Original test quality: **умеренное снижение** decision accuracy (0.778 → 0.667)
- ❌ Production readiness: **не готова** (precision/recall trade-off)

**Результаты Experiment 004 (internal test, n=15):**
- ✅ Runtime smoke: 7/7 pass
- ✅ LoRA decision_accuracy: 0.933
- ✅ LoRA MAE_score: 5.80
- ✅ LoRA FNR: 0.000
- ⚠️ LoRA FPR: 0.111 (1 false positive)
- ⚠️ GPT-4o-mini остаётся точнее (decision_accuracy 1.000, MAE 0.13), что ожидаемо на teacher-разметке GPT-4.1

**Результаты Experiment 004 (external validation HRA-EVAL-V5-EXT, n=102, GPT-4o reference):**
- ✅ LoRA valid_json_rate: 1.000
- ✅ LoRA decision_accuracy: 0.931
- ⚠️ GPT-4o-mini decision_accuracy: 0.941
- ⚠️ LoRA MAE_score: 19.63 vs GPT-4o-mini 6.19
- ✅ LoRA FPR: 0.050 vs GPT-4o-mini 0.063
- ⚠️ LoRA FNR: 0.136 vs GPT-4o-mini 0.045
- ❌ LoRA latency p95: 16.9 сек vs GPT-4o-mini 1.8 сек

**Итоговый вердикт:** гипотеза частично подтверждена. LoRA обобщается на внешних данных и достигает 93.1% decision accuracy, но не обгоняет GPT-4o-mini. LoRA — рабочий on-premise / edge кандидат; production остаётся за GPT-4o-mini.

**Рекомендации для следующих циклов:**
1. Score calibration (снизить MAE score)
2. Latency optimization (vLLM/TGI, quantization)
3. Снижение FNR (дополнительные positive/borderline примеры)
4. Расширение teacher dataset до 300–500 пар
5. Эксперименты с QLoRA / larger base model

**Следующие шаги:**
- [ ] Score calibration
- [x] Latency optimization (запущена, см. ниже)
- [ ] Следующий цикл fine-tuning (Cycle 5) или архивирование экспериментального контура

### Latency Optimization Experiment 004 (в процессе)

**Цель:** снизить p95 latency LoRA inference с ~17 секунд до ≤2 секунд без переобучения, сохранив decision_accuracy в пределах 5 pp от 0.931 на `data/external_validation.jsonl`.

**Подготовленные артефакты:**
- `scripts/profile_lora_latency.py` — профилирование latency по стадиям;
- `scripts/benchmark_lora_engines.py` — сравнение transformers fp16 / transformers 4-bit / vLLM fp16;
- `api/hra_qwen_api_lora_4bit.py` — FastAPI с 4-bit quantized base + LoRA;
- `api/hra_qwen_api_lora_vllm.py` — launcher vLLM OpenAI-compatible сервера с LoRA;
- `runpod_operation_manual_latency_optimization_experiment_004.md` — пошаговая инструкция для RunPod;
- `configs/latency_optimization_winscp_transfer.md` — список файлов для WinSCP.

**План:**
1. Профилировать текущий API (`hra_qwen_api_lora.py`).
2. Запустить benchmark движков на `data/external_validation.jsonl`.
3. Установить vLLM на RunPod при необходимости и повторить benchmark.
4. Выбрать лучший engine и запустить optimized API.
5. Сравнить optimized LoRA с GPT-4o-mini на external validation и smoke set.
6. Зафиксировать report и обновить документацию.

**Статус:** пакет для передачи на RunPod готов, ожидается выполнение benchmark.

## Инженерный отчёт

**Полная документация инженерного процесса Fine-tuning:**

👉 **[FINETUNING_ENGINEERING_REPORT.md](FINETUNING_ENGINEERING_REPORT.md)** — детальный отчёт, отвечающий на вопросы:

1. Почему выбран Fine-tuning
2. Почему выбран именно LoRA
3. Подготовка данных (связь с Prompt Evaluation)
4. Организация обучения
5. Оценка качества (baseline, offline, runtime)
6. Experiment 001
7. Experiment 002
8. Runtime Validation
9. Production Validation
10. Инженерные выводы

## Ссылки

- Основной проект HRA: `/cases/hr-assistant/`
- Инструкции проекта: `/CLAUDE.md`
- Окружение RunPod: `/workspace/hra-finetuning/`
- Экспериментальный ML-контур: `docs/EXPERIMENTAL_ML_PIPELINE.md`