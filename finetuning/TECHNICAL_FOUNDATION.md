# Техническая основа fine-tuning

Этот документ описывает воспроизводимую техническую основу всей серии экспериментов по fine-tuning в HR Assistant. Здесь собраны неизменные параметры модели, инфраструктуры, пайплайна, датасетов, метрик и runtime-контракта. Конкретные результаты и история отдельных циклов находятся в отчётах `Experiment_001_Report.md` … `Experiment_004_Report.md`.

---

## 1. Модель и метод

### 1.1. Базовая модель

| Параметр | Значение |
|----------|----------|
| Модель | `Qwen/Qwen2.5-1.5B-Instruct` |
| Размер | 1.5B параметров |
| Тип | instruction-tuned causal LM |
| Hugging Face Hub | https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct |

**Обоснование выбора:**
- Модель влезает в GPU-память с запасом для LoRA-адаптера.
- Поддерживает структурированный JSON-вывод и русский язык.
- Достаточно лёгкая для быстрых итераций экспериментов на RTX A5000.

### 1.2. Метод адаптации

Основной метод — **LoRA (Low-Rank Adaptation)** через библиотеку `peft`:
- Веса базовой модели заморожены.
- Обучаются только низкоранговые адаптер-слои, вставленные в целевые attention и MLP-модули.
- Адаптер легко сохранять, переключать и загружать поверх базовой модели.

### 1.3. Конфигурация LoRA

| Параметр | Значение |
|----------|----------|
| `r` (rank) | `16` |
| `lora_alpha` | `32` |
| `lora_dropout` | `0.05` |
| `bias` | `none` |
| `task_type` | `CAUSAL_LM` |
| `target_modules` | `q_proj`, `k_proj`, `v_proj`, `o_proj`, `gate_proj`, `up_proj`, `down_proj` |

Конфигурация зафиксирована в launch contract (`configs/experiment_003.yaml`, `configs/experiment_004.yaml`) и является неизменной для Experiments 003–004. Experiment 001 использовал меньший адаптер (`r=8`, 4 target modules); Experiment 002 проверил гипотезу о недостаточной ёмкости и перешёл к конфигурации выше (`r=16`, 7 target modules).

### 1.4. Tokenizer и формат обучения

Используется стандартный tokenizer модели `Qwen/Qwen2.5-1.5B-Instruct`:

```python
tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token
```

Данные для обучения подаются в формате чат-сообщений (`messages`) и преобразуются в текст через `tokenizer.apply_chat_template(..., tokenize=False, add_generation_prompt=False)`.

Пример структуры записи см. в [`data_sample/example.jsonl`](data_sample/example.jsonl).

### 1.5. Assistant-only masking

В репозитории есть два варианта обучающих скриптов:
- `scripts/train_lora.py` — стандартный SFTTrainer (канонический пайплайн для Experiments 003–004);
- `scripts/train_lora_assistant_only.py` — экспериментальный вариант с assistant-only loss (обучение только на токенах ответа ассистента).

Канонический пайплайн использует `train_lora.py`. Assistant-only masking оставлен как альтернативная гипотеза для будущих циклов.

### 1.6. Модельный JSON-контракт

Модель должна возвращать валидный JSON-объект со следующими полями:

| Поле | Диапазон | Назначение |
|------|----------|------------|
| `role_score` | 0–30 | Соответствие должности / роли |
| `skills_score` | 0–35 | Соответствие навыкам |
| `experience_score` | 0–20 | Соответствие опыту |
| `conditions_score` | 0–15 | Соответствие условиям (зарплата, город, формат) |
| `score` / `total_score` | 0–100 | Итоговый взвешенный score |
| `decision` | `match` / `no_match` | Решение по кандидату |
| `reason` | строка | Краткое обоснование score |

Правило decision:
- `score >= 60` → `match`;
- `score < 60` → `no_match`.

Системный prompt и схема score описаны в [`reports/teacher_dataset_report.md`](reports/teacher_dataset_report.md).

---

## 2. Инфраструктура

### 2.1. Платформа

| Компонент | Значение |
|-----------|----------|
| Провайдер | RunPod GPU Pod |
| GPU | NVIDIA RTX A5000, 24 GB VRAM |
| CUDA | 13.0 |
| Driver | 580.159.04 |
| Рабочий каталог | `/workspace/hra-finetuning` |
| Кэш моделей | `/root/.cache/huggingface` |

RunPod используется **только как инженерный стенд** для обучения и runtime-проверок. Production-контур HR Assistant использует OpenAI GPT-4o-mini.

### 2.2. Подтверждённые версии software stack

| Компонент | Версия |
|-----------|--------|
| Python | 3.12.3 |
| PyTorch | 2.6.0+cu124 |
| Transformers | 5.12.1 |
| TRL | 1.7.0 |
| Datasets | 5.0.0 |
| Tokenizers | 0.22.2 |
| PEFT | совместимая с указанными версиями |
| Accelerate | совместимая с указанными версиями |

Версии подтверждены в ходе запусков Experiments 003–004. Для воспроизведения рекомендуется использовать тот же stack.

### 2.3. Зависимости Python

Список зависимостей — [`requirements.txt`](requirements.txt). Основные пакеты:

```text
torch
transformers
datasets
accelerate
peft
trl
bitsandbytes
safetensors
sentencepiece
protobuf
scikit-learn
pandas
numpy
tqdm
```

Для воспроизводимости конкретные версии нужно зафиксировать в окружении (см. раздел «Правила воспроизводимости»).

### 2.4. Runtime-серверы

Runtime-файлы физически находятся в корневом каталоге `api/` уровня кейса, но по смыслу и использованию принадлежат подсистеме fine-tuning: все они созданы для serving Qwen/LoRA на RunPod и вызываются только из fine-tuning-контура.

**Канонический runtime Experiments 003–004** — FastAPI-совместимый сервер на базе Transformers + PEFT:
- [`../api/hra_qwen_api_lora.py`](../api/hra_qwen_api_lora.py) — LoRA-адаптер;
- [`../api/hra_qwen_api.py`](../api/hra_qwen_api.py) — базовая Qwen для baseline-сравнений.

Сервер разворачивается на RunPod и вызывается из n8n workflow `HR Processing Worker - Multi Provider Test` через OpenAI-compatible endpoint.

**Исследованные альтернативные реализации serving** (не являются каноническими):
- [`../api/hra_qwen_api_lora_4bit.py`](../api/hra_qwen_api_lora_4bit.py) — экспериментальный runtime с 4-bit NF4-квантизацией (`bitsandbytes`) для снижения потребления VRAM;
- [`../api/hra_qwen_api_lora_vllm.py`](../api/hra_qwen_api_lora_vllm.py) — экспериментальный OpenAI-compatible runtime на базе `vLLM` для снижения latency.

Оба файла относятся к инфраструктурным исследованиям и не заменяют основной runtime-контракт. Все сравнительные метрики Experiments 003–004 получены на каноническом FastAPI-сервере.

---

## 3. Общий экспериментальный пайплайн

Каждый цикл (Experiment) проходит общую последовательность этапов. Этапы 1–8 и 11 являются **обязательными** для каждого цикла. Этапы 9–10 (baseline comparison, external / real-world validation) применяются **дополнительно**, когда гипотеза эксперимента требует сравнения с baseline или проверки на независимой выборке. Отчёты по конкретным экспериментам описывают только изменения и отклонения от этого общего пайплайна.

```
Teacher Dataset
    ↓
Структурная проверка + split
    ↓
Launch contract (configs/experiment_NNN.yaml)
    ↓
GPU preflight на RunPod
    ↓
Обучение LoRA
    ↓
Выбор best checkpoint
    ↓
Offline evaluation
    ↓
Runtime smoke test
    ↓
Baseline comparison (опционально)
    ↓
External / real-world validation (опционально)
    ↓
Вердикт и решение о следующем цикле
```

### 3.1. Этапы пайплайна

| # | Этап | Вход | Инструмент | Исполнитель | Выходной артефакт | Критерий завершения |
|---|------|------|------------|-------------|-------------------|---------------------|
| 1 | Формирование teacher dataset | Размеченные пары candidate × vacancy из PostgreSQL | n8n workflow `HRA Prompt Evaluation Experiment` + `scripts/extract_teacher_dataset.py` | Пользователь / VPS Claude Code | `data/train.jsonl`, `data/validation.jsonl`, `data/test.jsonl`, `data/holdout.jsonl`, `data/manifest_experiment_NNN.json` | Ожидаемое число записей, отсутствие leakage, валидный JSON |
| 2 | Структурная проверка + split | JSONL-файлы, манифест | SQL-валидаторы + Python preflight | VPS Claude Code | Отчёт о проверке, подтверждение split | Все проверки `passed = true` |
| 3 | Launch contract | Гипотеза, параметры, пути | `configs/experiment_NNN.yaml` | VPS Claude Code | YAML-файл launch contract | Все неизменяемые параметры зафиксированы, единственная изменяемая переменная выделена |
| 4 | GPU preflight | Launch contract, файлы на RunPod | `scripts/01_environment_check.py` + ручные проверки | RunPod Claude Code *(Exp 003–004)* / Пользователь *(Exp 001–002)* | Запись в operation log со статусом READY FOR GPU | GPU доступна, Python venv работает, CUDA available, базовая модель кэширована |
| 5 | Обучение LoRA | `train.jsonl`, `validation.jsonl`, launch contract | `scripts/train_lora.py --config configs/experiment_NNN.yaml` | RunPod Claude Code *(Exp 003–004)* / Пользователь вручную на RunPod *(Exp 001–002)* | Чекпоинты в `runs/experiment_NNN/checkpoint-*`, `training_report.json`, `trainer_state.json` | Обучение завершилось без ошибок, eval_loss зафиксирован |
| 6 | Выбор best checkpoint | `trainer_state.json`, чекпоинты | Логика `load_best_model_at_end=True`, `metric_for_best_model=eval_loss` | RunPod Claude Code *(Exp 003–004)* / Пользователь вручную на RunPod *(Exp 001–002)* | `runs/experiment_NNN/best_adapter/` | Лучший чекпоинт однозначно определён |
| 7 | Offline evaluation | `data/test.jsonl`, best adapter | `scripts/evaluate_generation_test.py`, `scripts/evaluate_test.py` | RunPod Claude Code *(Exp 003–004)* / Пользователь вручную на RunPod *(Exp 001–002)* | `generation_test/generation_test_report.json`, `test_evaluation/test_metrics.json` | valid_json_rate, decision_accuracy, MAE_score зафиксированы |
| 8 | Runtime smoke test | `data/smoke_set.jsonl`, API с адаптером | `scripts/runtime_smoke_test.py` + `hra_qwen_api_lora.py` | RunPod Claude Code *(Exp 003–004)* / Пользователь вручную на RunPod *(Exp 001–002)* | `runtime_smoke_report.json` | Все кейсы smoke set пройдены с ожидаемыми решениями |
| 9 | Baseline comparison *(опционально)* | Test/holdout записи, LoRA, GPT-4o-mini | `scripts/compare_with_gpt.py` | RunPod Claude Code *(Exp 004)* | `gpt_comparison_report.json` | Метрики LoRA и baseline зафиксированы на одной выборке |
| 10 | External / real-world validation *(опционально)* | Внешний датасет или Telegram-анкеты | `scripts/compare_external_validation.py` + n8n Telegram workflow | RunPod Claude Code *(Exp 004)* / Пользователь *(Exp 001–002)* | `external_validation_report.json`, Telegram smoke report | Результаты на независимой выборке зафиксированы |
| 11 | Вердикт | Все метрики и отчёты | Инженерный анализ | Пользователь / Claude Code | `Experiment_NNN_Report.md` с вердиктом | Гипотеза подтверждена / частично / не подтверждена; принято решение о следующем цикле |

**Эволюция исполнителя GPU-этапов.** В Experiments 001–002 код пайплайна разрабатывался в диалоге с ChatGPT, а запуск и операционное управление на RunPod выполнял пользователь вручную. В Experiments 003–004 Claude Code был развёрнут непосредственно на RunPod и взял на себя GPU-preflight, обучение, выбор checkpoint, runtime smoke и валидацию — это следующий этап развития экспериментального процесса, а не просто смена инструмента. Исходный рабочий пайплайн, сформированный в Experiments 001–002, был сохранён и развит.

### 3.2. Стабильные роли

| Роль | Ответственность |
|------|-------------------|
| **Пользователь / Владелец решения** | Утверждает гипотезу, split-стратегию, критерии остановки; запускает обучение и контролирует процесс на RunPod в Experiments 001–002; принимает вердикт |
| **ChatGPT** | Подготовка кода экспериментального пайплайна, launch contract и документации в диалоге с пользователем в Experiments 001–002 |
| **VPS Claude Code** | Подготовка кода, конфигураций, SQL, launch contract, структурная preflight, offline evaluation на VPS в Experiments 003–004 |
| **RunPod Claude Code** | GPU-preflight, обучение, выбор checkpoint, runtime smoke, baseline comparison, external validation на RunPod в Experiments 003–004 |
| **Judge (GPT-4.1)** | Генерация reference labels для teacher dataset |
| **Baseline (GPT-4o-mini)** | Production baseline для сравнения с LoRA |
| **Telegram Bot / n8n** | Runtime-контур для real-world validation |

Подробная сводка ролей и эволюция инженерного процесса находятся в [`README.md`](README.md).

---

## 4. Датасеты и схемы

### 4.1. Teacher dataset

Teacher dataset формируется из reference dataset уровня Prompt Evaluation. Candidate-vacancy пары генерируются в PostgreSQL CROSS JOIN'ом кандидатов и открытых вакансий, а reference labels производит Judge workflow с моделью `gpt-4.1` и `temperature=0` по production Prompt A. Затем `scripts/extract_teacher_dataset.py` экспортирует пары в JSONL-файлы.

> **Важно:** HR Assistant никогда не работал в реальном боевом режиме. Все профили кандидатов и вакансий в `data/` — синтетические, созданные для экспериментов. Каталог `data/` включён в репозиторий, чтобы отчёты опирались на конкретные `case_code`, а не на голословные утверждения.

### 4.2. Структура записи

Каждая запись — объект с массивом `messages`:

```json
{
  "messages": [
    { "role": "system", "content": "Ты HR matching assistant..." },
    { "role": "user", "content": "КАНДИДАТ:\n[резюме]\n\nВАКАНСИЯ:\n[описание]" },
    { "role": "assistant", "content": "{\"role_score\": 30, ...}" }
  ]
}
```

Полная структура и анонимизированный пример — [`data_sample/example.jsonl`](data_sample/example.jsonl).

### 4.3. Reference fields

Judge сохраняет в БД детальные reference-оценки:

| Поле | Тип | Диапазон |
|------|-----|----------|
| `reference_role_score` | numeric | 0–30 |
| `reference_skills_score` | numeric | 0–35 |
| `reference_experience_score` | numeric | 0–20 |
| `reference_conditions_score` | numeric | 0–15 |
| `reference_score` | numeric | 0–100 |
| `reference_decision` | text | `match` / `no_match` |
| `reference_reason` | text | обоснование |

### 4.4. Split

| Split | Назначение |
|-------|-----------|
| `train` | Обучение модели |
| `validation` | Выбор best checkpoint, ранняя остановка |
| `test` | Отложенная оценка (используется только один раз) |
| `holdout` | Независимая проверка на ранее не встречавшихся hard negatives |

Стратификация ведётся по группам кандидатов: `obvious_match`, `borderline`, `obvious_no_match`. `case_code` — идентификатор кандидата; каждый кандидат оценивается по трём вакансиям, что даёт 3 записи teacher dataset.

### 4.5. Case codes

Формат идентификаторов: `HRA-EVAL-V2-XXXXXX`.

Примеры диапазонов:
- `000001`–`000030` — исходные кандидаты Experiment 002;
- `000101`–`000111` — hard negative кандидаты Experiment 003;
- `000201`–`000213` — positive/borderline кандидаты Experiment 004;
- `000301`–`000334` — кандидаты external validation set HRA-EVAL-V5-EXT.

### 4.6. External validation set

Отдельный внешний датасет `HRA-EVAL-V5-EXT` (102 пары, 34 новых кандидата). Reference labels генерирует `gpt-4o` вместо `gpt-4.1`, чтобы проверить обобщение на независимый judge. Подробнее — [`reports/external_validation_report.md`](reports/external_validation_report.md).

### 4.7. Production smoke set

Real-world validation проводится через Telegram Bot и n8n workflow. Smoke set формируется из реальных анкет и edge-кейсов, не входящих в teacher dataset. Результаты фиксируются в отчёте соответствующего эксперимента.

---

## 5. Метрики

### 5.1. Метрики обучения

| Метрика | Назначение |
|---------|-----------|
| `eval_loss` | Основная метрика выбора best checkpoint (minimize) |
| `train_loss` | Динамика обучения |
| `token_accuracy` | Точность предсказания токенов (опционально) |

### 5.2. Метрики offline evaluation

| Метрика | Назначение |
|---------|-----------|
| `valid_json_rate` | Доля записей, для которых модель вернула валидный JSON |
| `decision_accuracy` | Доля совпадений `decision` с reference |
| `MAE_score` | Средняя абсолютная ошибка по итоговому `score` |
| `MAE_role` / `MAE_skills` / `MAE_experience` / `MAE_conditions` | MAE по компонентным score |
| `FPR` | Доля ложных положительных решений |
| `FNR` | Доля ложных отрицательных решений |

### 5.3. Runtime и production метрики

| Метрика | Назначение |
|---------|-----------|
| `latency_p50` / `latency_p95` / `latency_avg` | Время ответа API в миллисекундах |
| `stratified_accuracy` | Accuracy внутри групп `obvious_match`, `borderline`, `obvious_no_match` |
| `hard_negative_fpr` | False-positive rate на hard-negative/edge кейсах |

### 5.4. Baseline comparison

LoRA сравнивается с двумя baseline:
- **Base Qwen** — zero-shot inference базовой модели без адаптера;
- **GPT-4o-mini** — production-модель HR Assistant.

Сравнение выполняется на одной и той же выборке, чтобы метрики были сопоставимы.

---

## 6. Runtime validation

### 6.1. Загрузка adapter и serving

Runtime API загружает базовую модель и LoRA-адаптер:

```python
model = AutoModelForCausalLM.from_pretrained(base_model_id, ...)
model = PeftModel.from_pretrained(model, adapter_path)
```

Путь к адаптеру задаётся в launch contract (`output.best_adapter_dir`).

### 6.2. JSON extraction

Модель может генерировать JSON с markdown-обёртками или артефактами. API извлекает первый валидный JSON-объект из ответа:

- Удаляет префиксы ```` ```json ```` и ```` ``` ````;
- Ищет первую открывающую фигурную скобку `{`;
- Парсит через `json.JSONDecoder.raw_decode`.

### 6.3. Graceful fallback

Поведение при неудаче парсинга JSON зависит от runtime:

- **Канонический LoRA runtime** [`hra_qwen_api_lora.py`](../api/hra_qwen_api_lora.py) реализует graceful fallback и **не** возвращает HTTP 422. Вместо этого ответ сохраняется как строка, а API возвращает HTTP 200 с телом вида:

  ```json
  {
    "error": "invalid_json",
    "raw_response": "..."
  }
  ```

  Это позволяет offline-скриптам продолжать обработку и фиксировать `valid_json_rate` корректно.

- **Базовый runtime** [`hra_qwen_api.py`](../api/hra_qwen_api.py) использует более строгую стратегию: при отсутствии валидного JSON он возвращает HTTP 422.

Описанный graceful fallback относится именно к LoRA runtime, а не ко всем реализациям API.

### 6.4. max_tokens

Для русскоязычных reasoning-ответов может потребоваться `max_tokens >= 512`. Значение `300` приводит к обрезанию длинных ответов и ошибкам парсинга. В каноническом пайплайне используется `max_tokens = 512` для LoRA и baseline.

### 6.5. Latency measurement

Latency измеряется на стороне клиента (n8n / скрипт сравнения) как время от отправки запроса до получения полного ответа. Все latency-замеры фиксируются в JSON-отчётах.

---

## 7. Правила воспроизводимости

Каждый run должен фиксировать следующие артефакты:

| Категория | Что фиксировать | Где хранится |
|-----------|-----------------|--------------|
| **Config** | Launch contract YAML (`configs/experiment_NNN.yaml`) | в репозитории |
| **Dataset** | `data/train.jsonl`, `data/validation.jsonl`, `data/test.jsonl`, `data/holdout.jsonl`, `data/smoke_set.jsonl`, `data/external_validation.jsonl`, `data/manifest_experiment_NNN.json` | в репозитории (синтетические данные) |
| **Manifest** | `data/manifest_experiment_NNN.json` — состав датасета, split, case codes | в репозитории |
| **Operation log** | Журнал запуска — шаги, версии, команды, замечания | в закрытом рабочем контуре |
| **Metrics** | `training_report.json`, `generation_test_report.json`, `test_metrics.json`, `runtime_smoke_report.json` | в закрытом рабочем контуре |
| **Outputs** | Чекпоинты, best adapter, отчёты сравнения | в закрытом рабочем контуре |
| **Checkpoint selection** | Запись о том, какой чекпоинт выбран и почему (`eval_loss`, эпоха) | в журнале запуска и `trainer_state.json` |
| **Environment versions** | Python, PyTorch, CUDA, Transformers, TRL, Datasets, Tokenizers, GPU driver | в журнале запуска |

### 7.1. Что публикуется в GitHub

- Документация (`README.md`, `TECHNICAL_FOUNDATION.md`, `Experiment_*_Report.md`, отчёты).
- Конфигурации без секретов (`configs/experiment_*.yaml`).
- Скрипты обучения и evaluation (`scripts/`).
- Синтетические датасеты (`data/`).
- Обезличенный пример формата данных (`data_sample/example.jsonl`).
- `requirements.txt`.

### 7.2. Что остаётся вне GitHub

- Артефакты обучения (`runs/`, `models/`).
- Checkpoints и adapter-веса (`*.safetensors`, `*.pt`, `*.bin`).
- API-ключи и переменные окружения (`.env`).
- HuggingFace кэш (`.cache/`).

Эти каталоги исключены через [`.gitignore`](.gitignore).

### 7.3. Параметризация

Все скрипты читают пути и параметры из launch contract через `--config`. Жёстко зашитые пути к конкретным экспериментам исключены. Это обеспечивает воспроизводимость без правки кода.

---

## Связанные документы

| Документ | Назначение |
|----------|-----------|
| [`README.md`](README.md) | Точка входа в подсистему fine-tuning |
| [`Experiment_001_Report.md`](Experiment_001_Report.md) | Базовый LoRA baseline, проверка технического пайплайна |
| [`Experiment_002_Report.md`](Experiment_002_Report.md) | Улучшение параметров LoRA, runtime negative failure |
| [`Experiment_003_Report.md`](Experiment_003_Report.md) | Hard negative teacher dataset, runtime smoke, precision/recall trade-off |
| [`Experiment_004_Report.md`](Experiment_004_Report.md) | Balanced dataset, GPT-4o-mini comparison, external validation, Telegram smoke test |
| [`reports/teacher_dataset_report.md`](reports/teacher_dataset_report.md) | Состав и структура teacher dataset |
| [`reports/external_validation_report.md`](reports/external_validation_report.md) | Состав внешнего датасета HRA-EVAL-V5-EXT |
