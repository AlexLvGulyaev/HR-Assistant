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

### Experiment 002 (лучший результат)

**Статус:** Завершён, не production-ready

**Результаты:**

| Метрика | Base Qwen | Qwen + LoRA | GPT-4o-mini (baseline) |
|---------|-----------|-------------|------------------------|
| Offline Validation | ✅ Базовый | ✅ **Улучшение** | Reference |
| Runtime Positive Test | ✅ Pass | ✅ Pass | N/A |
| Runtime Negative Test | ✅ Pass | ❌ **Failed** | N/A |

**Ключевой вывод:**
- LoRA значительно улучшает offline качество
- Модель **не прошла runtime negative smoke test**
- Модель **не является production-ready**

**Причина:** Teacher dataset не содержит достаточное количество hard negative примеров.

### Следующий цикл (Cycle 3)

**Приоритет:** Расширение teacher dataset

**Задачи:**
1. Добавить hard negative примеры в teacher dataset
2. Провести experiment_003
3. Пройти runtime smoke validation
4. Документировать результаты

**НЕ приоритет:** Изменение архитектуры модели

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

**Фаза:** Experiment 002 завершён, не production-ready

**Выполнено:**
- [x] Структура каталогов
- [x] Техническая документация
- [x] Шаблон конфигурации эксперимента
- [x] Каркас скрипта подготовки датасета
- [x] Experiment 001 (базовый)
- [x] Experiment 002 (лучший результат)
- [x] Offline validation
- [x] Runtime smoke validation

**Результаты Experiment 002:**
- ✅ Offline validation: значительное улучшение качества
- ✅ Runtime positive test: pass
- ❌ Runtime negative test: **failed**
- ❌ Production readiness: **не готова**

**Следующие шаги:**
- [ ] Расширить teacher dataset (hard negative примеры)
- [ ] Провести experiment_003
- [ ] Пройти runtime smoke validation
- [ ] Документировать результаты
- [ ] Повторить цикл до production-readiness

## Ссылки

- Основной проект HRA: `/cases/hr-assistant/`
- Инструкции проекта: `/CLAUDE.md`
- Окружение RunPod: `/workspace/hra-finetuning/`