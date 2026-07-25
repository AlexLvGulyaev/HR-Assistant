# Fine-tuning в HR Assistant

## Назначение

Подсистема fine-tuning в HR Assistant исследует возможность замены или дополнения production-модели OpenAI GPT-4o-mini лёгкой LoRA-адаптерной моделью на базе Qwen/Qwen2.5-1.5B-Instruct. Цель — повысить автономность, снизить зависимость от внешних API и сохранить качество matching резюме с вакансиями.

**Статус:** экспериментальный ML-контур, изолированный от production.

**Производственный контур по-прежнему использует OpenAI GPT-4o-mini.** LoRA-модель проходит те же проверки качества, но не заменяет production без дополнительного цикла валидации.

---

## Архитектура контура

Fine-tuning — уровень 2 в экспериментальном ML-контуре HR Assistant:

```
Prompt Engineering
      ↓
Prompt A/B Evaluation (уровень 1)
      ↓
Reference Dataset (Judge оценки)
      ↓
Teacher Dataset
      ↓
LoRA Fine-tuning (уровень 2)
      ↓
Offline Evaluation
      ↓
Runtime Smoke Validation (уровень 3)
      ↓
External / Real-world Validation
      ↓
Production Verdict
```

**Связь с production:**

| Аспект | Production | Experimental (этот модуль) |
|--------|------------|----------------------------|
| Workflow | HR Processing Worker | HR Processing Worker — Multi Provider Test |
| LLM | OpenAI GPT-4o-mini | RunPod (Qwen + LoRA) |
| База данных | Production tables | Изолированный teacher dataset |
| Назначение | Обработка реальных запросов | Исследование и тестирование |

Уровень 1 (Prompt Evaluation) формирует reference dataset из 90 кейсов. Подсистема fine-tuning превращает reference dataset в teacher dataset, обучает на нём LoRA-адаптер и проводит многоуровневую валидацию.

---

## Участники и роли

| Роль | Ответственность | Участие в экспериментах |
|------|-------------------|--------------------------|
| **Пользователь / Владелец решения** | Инициирует цикл, утверждает гипотезу, split-стратегию, критерии успеха и остановки; в Experiments 001–002 запускает команды и контролирует процесс на RunPod вручную; принимает вердикт | Все эксперименты |
| **ChatGPT** | Подготовка кода экспериментального пайплайна, launch contract, документации в диалоге с пользователем | Experiments 001–002 |
| **VPS Claude Code** | Подготовка кода, конфигураций, SQL, launch contract, структурная preflight, offline evaluation на VPS | Experiments 003–004 |
| **RunPod Claude Code** | GPU-preflight, запуск обучения, выбор checkpoint, runtime smoke, baseline comparison, external validation на GPU-среде | Experiments 003–004 |
| **Judge (GPT-4.1)** | Teacher: генерация reference labels для teacher dataset | Все эксперименты |
| **Baseline (GPT-4o-mini)** | Production baseline для сравнения с LoRA | Experiment 004 |
| **LoRA-модель** | Обучаемый адаптер Qwen + LoRA | Все эксперименты |
| **Telegram Bot / n8n** | Runtime-контур для real-world smoke test | Experiment 004 |

Стабильные роли описаны здесь. В отчётах по экспериментам остаются только отклонения и конкретные исполнители этапов.

### Эволюция инженерного процесса

Эксперименты проходили в два принципиально разных режима работы:

- **Experiments 001–002** — исходный рабочий пайплайн. Код разрабатывался в диалоге с ChatGPT. Запуск команд, обучение модели, контроль процесса и получение артефактов выполнял пользователь вручную на RunPod. RunPod использовался только как вычислительная среда; Claude Code на RunPod не применялся.
- **Experiments 003–004** — следующий этап развития процесса. Claude Code был запущен непосредственно в среде RunPod и участвовал не только в подготовке кода на VPS, но и в работе с экспериментальным пайплайном внутри GPU-среды: GPU-preflight, обучение, выбор checkpoint, runtime smoke, baseline comparison, external validation.

При этом Experiments 001–002 не обесцениваются: именно они сформировали исходный воспроизводимый пайплайн (dataset → launch contract → GPU preflight → обучение → checkpoint → offline evaluation), который затем был развит в Experiments 003–004.

---

## История экспериментов

| Эксперимент | Что проверяли | Ключевой результат | Вердикт | Следующий инженерный вопрос |
|-------------|---------------|-------------------|---------|------------------------------|
| **001** | Базовый LoRA baseline | Обучение стабильно, чекпоинты сохраняются, JSON генерируется | ✅ Базовый запуск успешен | Какие параметры LoRA улучшат качество? |
| **002** | Увеличение rank, target modules, epochs | `eval_loss=0.44`, offline `decision_accuracy=0.778` | ✅ Offline-качество высокое, ❌ runtime negative smoke failed | Почему модель пропускает сложные negative кейсы? |
| **003** | Добавление hard negatives в teacher dataset | `eval_loss=0.31`, runtime negative smoke **7/7 pass**, offline accuracy снизилась до 0.667 | ⚠️ Частично подтверждено | Как восстановить recall на genuine match без потери negative smoke? |
| **004** | Добавление positive/borderline примеров и сравнение с GPT-4o-mini | Internal test: 0.933 accuracy, 5.80 MAE; External validation (n=102): 0.931 vs GPT-4o-mini 0.941 | ⚠️ Частично подтверждено, рабочий on-premise / edge кандидат | Как устранить hard-negative failures в real-world условиях? |

Эта таблица — сводка. Подробные протоколы, метрики и интерпретации находятся в отчётах по экспериментам.

---

## Текущий статус

**Experiment 004 завершён 2026-07-22.**

- LoRA обучена на сбалансированном teacher dataset из 162 записей (54 кандидата).
- Offline evaluation на тестовом наборе Experiment 004 (n=15): `decision_accuracy=0.933`, `MAE_score=5.80`, `valid_json_rate=1.0`.
- Runtime smoke test: **7/7 passed**, 0 unexpected matches.
- External validation HRA-EVAL-V5-EXT (n=102, GPT-4o reference): LoRA `decision_accuracy=0.931` vs GPT-4o-mini `0.941`.
- Real-world Telegram smoke test (23 hard-negative/edge анкеты): LoRA 35 % корректных vs GPT-4o-mini 43 %. Выявлены failure modes: галлюцинации навыков у junior/стажёрских профилей, путаница BA/DA/процессного аналитика с системным аналитиком, игнорирование salary mismatch.
- Анализ teacher dataset V4 показал, что 9 из 36 hard-negative-like записей размечены reference-teacher как `match`. Это объясняет, почему LoRA копирует поведение teacher на hard negatives.

**Вердикт:** гипотеза Experiment 004 частично подтверждена. LoRA обобщается на внешних данных, но не обгоняет GPT-4o-mini. Модель является рабочим on-premise / edge кандидатом; production остаётся за GPT-4o-mini.

**Открытые вопросы для следующего цикла:**
- Ре-разметка hard negatives с жёстким критерием (BA/DA/process analyst → `no_match` без прямых ключевых навыков).
- Добавление extreme sparse profiles и salary mismatch в teacher dataset.
- Score calibration (снизить MAE score до уровня GPT-4o-mini).
- Введение stratified metrics и production smoke set для оценки production-качества.

---

## Навигация по документации

| Документ | Назначение |
|----------|-----------|
| [TECHNICAL_FOUNDATION.md](TECHNICAL_FOUNDATION.md) | Базовая модель, LoRA, инфраструктура, метрики, общий воспроизводимый пайплайн |
| [Experiment_001_Report.md](Experiment_001_Report.md) | Базовый LoRA baseline, проверка технического пайплайна |
| [Experiment_002_Report.md](Experiment_002_Report.md) | Улучшение параметров LoRA, runtime negative failure |
| [Experiment_003_Report.md](Experiment_003_Report.md) | Hard negative teacher dataset, offline audit, precision/recall trade-off |
| [Experiment_004_Report.md](Experiment_004_Report.md) | Сбалансированный dataset, GPT-4o-mini comparison, external validation, real-world Telegram smoke test |
| [reports/teacher_dataset_report.md](reports/teacher_dataset_report.md) | Состав и структура teacher dataset |
| [reports/external_validation_report.md](reports/external_validation_report.md) | Состав внешнего датасета HRA-EVAL-V5-EXT |

---

## Структура каталога

```
finetuning/
├── README.md                    # Этот файл
├── TECHNICAL_FOUNDATION.md      # Технический фундамент и пайплайн
├── Experiment_001_Report.md     # Отчёт Experiment 001
├── Experiment_002_Report.md     # Отчёт Experiment 002
├── Experiment_003_Report.md     # Отчёт Experiment 003
├── Experiment_004_Report.md     # Отчёт Experiment 004
├── requirements.txt             # Зависимости Python
├── configs/                     # Конфигурации экспериментов (launch contracts)
├── scripts/                     # Скрипты пайплайна
├── data_sample/                 # Анонимизированный пример формата данных
│   └── example.jsonl
├── data/                        # Синтетические датасеты для воспроизведения экспериментов
│   ├── train.jsonl
│   ├── validation.jsonl
│   ├── test.jsonl
│   ├── holdout.jsonl
│   ├── smoke_set.jsonl
│   ├── external_validation.jsonl
│   ├── external_validation_subset_20.jsonl
│   ├── external_validation_subset_21.jsonl
│   ├── manifest_experiment_003.json
│   └── manifest_experiment_004.json
├── data_sample/                 # Обезличенный пример формата данных
│   └── example.jsonl
└── reports/                     # Вспомогательные отчёты
    ├── teacher_dataset_report.md
    └── external_validation_report.md
```

### Данные

Каталог [`data/`](data/) содержит **синтетические** датасеты, использованные в экспериментах. HR Assistant никогда не запускался в реальном боевом режиме, поэтому все профили кандидатов, вакансии и reference-оценки были созданы искусственно для целей исследования. Включение `data/` в репозиторий позволяет воспроизвести каждое решение, принятое в отчётах, на конкретных `case_code`.

Каталоги `runs/` и `models/` по-прежнему исключены через [`.gitignore`](.gitignore): они содержат журналы обучения, чекпоинты и веса моделей.

---

## Основной проект

- [README.md](../README.md) — корневая точка входа в HR Assistant.
- [docs/prompt_evaluation/](../docs/prompt_evaluation/) — уровень 1 ML-контура: Prompt Evaluation.
