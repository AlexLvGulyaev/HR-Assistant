# Техническая основа

## Базовая модель

**Модель:** Qwen/Qwen2.5-1.5B-Instruct

**Обоснование:**
- Лёгкая (1.5B параметров) — влезает в GPU-память с запасом для LoRA
- Instruction-tuned — подходит для структурированного JSON вывода
- Хорошее соотношение качество/размер для экспериментов
- Активная разработка и поддержка сообществом

**Hugging Face Hub:** https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct

## Инфраструктура

**Платформа:** RunPod GPU Pod

**Железо:**
- GPU: NVIDIA RTX A5000 (24GB VRAM)
- CUDA: Проверено, работает
- Хранилище: Временное рабочее пространство (`/workspace/`)

**Окружение:**
- Рабочий каталог: `/workspace/hra-finetuning`
- Python: 3.10+
- PyTorch: 2.0+ (CUDA support)
- Transformers: Latest stable

**Проверенный статус:**
- CUDA работает
- Модель Qwen загружается успешно
- Inference smoke test пройден

## Метод обучения

**Основной:** LoRA (Low-Rank Adaptation)

**Почему LoRA:**
- Замораживает веса базовой модели
- Обучает только адаптер-слои (rank decomposition)
- ~100x меньше, чем full finetuning
- Быстрые итерации обучения
- Легко переключать адаптеры

**Будущее:** QLoRA (Quantized LoRA)
- 4-bit квантование базовой модели
- Ещё меньшее потребление памяти
- Требует дополнительной настройки (bitsandbytes)

### Конфигурация LoRA (предварительная)

```yaml
# Черновик — требует тюнинга
lora_r: 8              # Rank LoRA
lora_alpha: 32        # Scaling factor
lora_dropout: 0.1      # Dropout probability
target_modules:       # Модули для адаптации
  - q_proj
  - v_proj
  - k_proj
  - o_proj
```

## Стратегия данных

### Датасет: HRA-EXP-V1

**Источник:** 90 эталонных кейсов из результатов эксперимента HRA-EXP-V1
**Файл:** `docs/prompt_evaluation/FULL_RESULTS_DETAIL.md`

**Структура кейса:**
- Вход: Резюме кандидата + Описание вакансии
- Выход: Структурированный JSON с оценками и решением

**Важно:**
- System prompt: **Prompt A (production)** из эксперимента
- Target output: **Judge (gpt-4.1)** оценки как ground truth
- **НЕ использовать Prompt A или Prompt B результаты как эталон**

### Разбиение данных

**Всего:** 90 кейсов

**Пропорции:**
- Train: 72 кейса (80%)
- Validation: 9 кейсов (10%)
- Test: 9 кейсов (10%)

### Стратификация

Кейсы разделены на три группы по сложности matching:

| Группа | Описание | Количество | Train | Validation | Test |
|--------|----------|------------|-------|------------|------|
| **Obvious Match** | Явное совпадение | 30 | 24 | 3 | 3 |
| **Borderline** | Пограничный случай | 30 | 24 | 3 | 3 |
| **Obvious No-Match** | Явное несовпадение | 30 | 24 | 3 | 3 |

**Стратификация обеспечивает:**
- Сбалансированное представление по уровням сложности
- Ни одна группа не перепредставлена в любом разбиении
- Надёжные метрики валидации и теста

### Использование Validation vs. Test

**Validation Set (9 кейсов):**
- Используется во время обучения для выбора чекпоинта
- Выбор лучшей эпохи по validation loss
- Можно тюнить гиперпараметры по валидации

**Test Set (9 кейсов):**
- Используется **только один раз** после выбора финальной модели
- Даёт несмещённую оценку обобщающей способности
- Никогда не используется для выбора модели или тюнинга

## Структура эксперимента

**Единица работы:** Experiment

Каждый эксперимент определяется:
1. Конфигурационным файлом (`configs/experiment_XXX.yaml`)
2. Разбиением датасета (train/validation/test)
3. Прогоном обучения с чекпоинтами
4. Результатами валидации (метрики по эпохам)
5. Результатами теста (финальная оценка)
6. Отчётом (`reports/experiment_XXX.md`)

### Жизненный цикл эксперимента

```
1. Подготовка датасета → train.jsonl, validation.jsonl, test.jsonl
2. Конфигурация эксперимента → configs/experiment_XXX.yaml
3. Обучение модели → runs/experiment_XXX/checkpoint-*
4. Валидация → выбор лучшего чекпоинта
5. Тест → оценка на отложенном тесте
6. Отчёт → сравнение base vs adapter vs GPT
```

### Соглашение об именовании

- Configs: `experiment_001.yaml`, `experiment_002.yaml`, ...
- Runs: `runs/experiment_001/`, `runs/experiment_002/`, ...
- Reports: `reports/experiment_001.md`, `reports/experiment_002.md`, ...

## Формат данных

### Формат входа (messages)

```json
{
  "messages": [
    {
      "role": "system",
      "content": "Ты HR matching assistant..."
    },
    {
      "role": "user",
      "content": "КАНДИДАТ:\n[резюме]\n\nВАКАНСИЯ:\n[описание]"
    },
    {
      "role": "assistant",
      "content": "{\"role_score\": 30, \"skills_score\": 33, ...}"
    }
  ]
}
```

### Формат выхода (JSON)

```json
{
  "role_score": 8,
  "skills_score": 7,
  "experience_score": 6,
  "conditions_score": 9,
  "total_score": 7.5,
  "decision": "MATCH",
  "reasoning": "Strong technical skills match requirements..."
}
```

### Рубрика оценивания

Каждая оценка: шкала 1-10 (или по критериям)

| Оценка | Интерпретация |
|--------|---------------|
| 1-3 | Плохое соответствие |
| 4-6 | Умеренное соответствие |
| 7-9 | Хорошее соответствие |
| 10 | Идеальное соответствие |

**Total Score:** Взвешенное среднее или простое среднее (TBD в конфиге эксперимента)

**Decision:** `MATCH` | `NO_MATCH` | `NEED_MORE_INFO`

## Метрики

### Метрики обучения
- Loss (cross-entropy)
- Perplexity

### Метрики валидации
- Loss (primary для выбора чекпоинта)
- Token accuracy (опционально)
- JSON validity rate

### Метрики теста
- Exact match accuracy
- Score correlation (Pearson/Spearman)
- Decision accuracy
- Reasoning quality (human evaluation или GPT-judge)

### Точки сравнения

Сравниваем три модели:
1. **Base Qwen:** Zero-shot baseline
2. **Qwen + LoRA:** Finetuned адаптер
3. **GPT Baseline:** Эталонное качество (например, GPT-4o-mini)

## Файлы для исключения из Git

Согласно `.gitignore`:

```
data/              # Содержит реальные HRA кейсы (могут содержать PII)
runs/              # Артефакты обучения (большие файлы)
models/            # Загруженные/адаптированные модели (большие файлы)
.venv/             # Виртуальное окружение
__pycache__/       # Python кэш
*.safetensors      # Веса моделей
*.pt               # PyTorch чекпоинты
*.bin              # Бинарные веса
.env               # Переменные окружения (ключи)
.cache/            # HF кэш
```

## Зависимости

Основные требования (будут уточняться):

```
torch>=2.0
transformers>=4.36
peft>=0.7
datasets>=2.14
accelerate>=0.24
bitsandbytes>=0.41  # Для QLoRA
trl>=0.7
wandb>=0.16         # Опционально: трекинг экспериментов
```

## Безопасность и приватность

**Обработка данных:**
- Анонимизация имён кандидатов и контактной информации
- Удаление идентифицирующей информации о компаниях
- Хранение реальных данных только в `data/` (gitignored)

**API ключи:**
- Никогда не коммитить `.env` файлы
- Использовать переменные окружения для HuggingFace токенов
- Продакшен API (`/workspace/hra_qwen_api.py`) не затрагивается

## Следующие технические решения

1. **Learning Rate:** Требует тюнинга (предлагаю начать с 1e-4)
2. **Batch Size:** Зависит от памяти (попробовать 4-8 с gradient accumulation)
3. **Epochs:** 3-5 типично для LoRA, валидация early stopping
4. **Prompt Template:** Финализировать system prompt для HRA задачи
5. **JSON Schema:** Валидация выходного JSON во время inference

## Ссылки

- PEFT документация: https://huggingface.co/docs/peft
- LoRA paper: https://arxiv.org/abs/2106.09685
- QLoRA paper: https://arxiv.org/abs/2305.14314