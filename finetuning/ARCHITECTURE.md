# Архитектура экспериментального fine-tuning-контура

Этот документ показывает высокоуровневую архитектуру серии экспериментов по fine-tuning в HR Assistant и причинно-следственную связь между Experiment 001 и Experiment 004. Конкретные параметры, метрики и протоколы запусков находятся в [`TECHNICAL_FOUNDATION.md`](TECHNICAL_FOUNDATION.md) и отчётах `Experiment_00N_Report.md`.

---

## 1. Общая архитектура контура

```mermaid
flowchart TD
    subgraph "Production HR Assistant"
        P1["HR Processing Worker"]
        P2["OpenAI GPT-4o-mini"]
        P3["Production PostgreSQL"]
        P4["Telegram Bot / n8n"]
    end

    subgraph "Experimental Fine-tuning Contour"
        E1["Prompt Evaluation"]
        E2["GPT-4.1 Judge"]
        E3["Reference Dataset"]
        E4["Teacher Dataset"]
        E5["LoRA Training<br/>Qwen/Qwen2.5-1.5B-Instruct"]
        E6["Offline Evaluation"]
        E7["Runtime Smoke Validation"]
        E8["External / Real-world Validation"]
    end

    P1 --> P2
    P2 --> P3
    P3 --> P4

    E1 --> E2
    E2 --> E3
    E3 --> E4
    E4 --> E5
    E5 --> E6
    E6 --> E7
    E7 --> E8
    E8 --> V["Engineering Decision"]

    V -.->|"Пока не production-ready"| P2
    V -.->|"Будущий on-premise / edge кандидат"| E5
```

**Пояснение.** Уровень 1 (`Prompt Evaluation`) формирует размеченный `Reference Dataset`. Подсистема fine-tuning превращает его в `Teacher Dataset`, обучает на нём LoRA-адаптер поверх Qwen и проводит три уровня валидации: offline, runtime smoke, external / real-world. Результатом контура является **инженерное решение** (engineering decision): перейти к следующему эксперименту, изменить гипотезу или рекомендовать модель для production. По состоянию на Experiment 004 production-контур остаётся за GPT-4o-mini; LoRA позиционируется как рабочий on-premise / edge-кандидат.

---

## 2. Инфраструктура исполнения

```mermaid
flowchart LR
    subgraph "VPS (Control Plane)"
        VPS["VPS Claude Code"]
        SQL[("PostgreSQL<br/>Reference Dataset")]
        CFG["Launch Contract<br/>configs/experiment_*.yaml"]
    end

    subgraph "RunPod GPU Pod"
        RP["RunPod RTX A5000"]
        GCC["RunPod Claude Code<br/>Exp 003–004"]
        USER["Пользователь вручную<br/>Exp 001–002"]
        QL["Qwen + LoRA"]
        API["FastAPI Runtime<br/>hra_qwen_api_lora.py"]
    end

    subgraph "External Services"
        TEACHER["GPT-4.1 Teacher / Judge"]
        BASELINE["GPT-4o-mini<br/>Production Baseline"]
        TGN["Telegram Bot / n8n"]
    end

    SQL --> VPS
    VPS --> CFG
    VPS -->|"dataset + launch contract"| RP
    CFG --> RP

    USER -->|"train / eval / smoke<br/>(Exp 001–002)"| QL
    GCC -->|"GPU-preflight → train → eval → smoke<br/>(Exp 003–004)"| QL
    QL --> API
    API --> TGN

    TEACHER -->|"reference labels"| SQL
    BASELINE -->|"comparison"| RP
    TGN -->|"real-world smoke"| RP
```

**Пояснение.** VPS Claude Code готовит датасет, SQL-разметку и launch contract. В Experiments 001–002 на RunPod команды запускал пользователь вручную; в Experiments 003–004 GPU-этапы выполнял Claude Code, развёрнутый непосредственно на RunPod. RunPod хостит обучение, offline/runtime evaluation и FastAPI-сервер с LoRA-адаптером. GPT-4.1 выступает Teacher / Judge, GPT-4o-mini — production baseline для сравнения, Telegram / n8n — контур real-world smoke test.

---

## 3. Жизненный цикл одного эксперимента

```mermaid
flowchart TD
    H["Гипотеза и критерии успеха"] --> D["Подготовка Teacher Dataset"]
    D --> C["Launch Contract<br/>configs/experiment_*.yaml"]
    C --> G["GPU Preflight"]
    G --> T["LoRA Training"]
    T --> B["Выбор Best Checkpoint<br/>min eval_loss"]
    B --> O["Offline Evaluation"]
    O --> R["Runtime Smoke Test"]
    R --> BC["Baseline Comparison<br/>(optional)"]
    R --> EV["External / Real-world Validation<br/>(optional)"]
    BC --> V["Engineering Decision"]
    EV --> V
    R --> V
    V --> N["Следующий эксперимент"]
    N --> H
```

**Пояснение.** Каждый эксперимент начинается с гипотезы и закрепляется launch contract. После GPU-preflight запускается обучение, выбирается best checkpoint по минимальному `eval_loss`, затем выполняются обязательные offline и runtime проверки. `Baseline Comparison` и `External / Real-world Validation` выполняются только тогда, когда гипотеза требует сравнения с production baseline или проверки обобщения на независимой выборке. Все ветки сходятся в **Engineering Decision**, которая задаёт вопрос следующему циклу (подробнее — в [`TECHNICAL_FOUNDATION.md`](TECHNICAL_FOUNDATION.md), раздел 3).

---

## 4. Эволюция Experiments 001–004

```mermaid
flowchart LR
    E001["Exp 001<br/>Pipeline Check"] -->|"Pipeline works"| E002["Exp 002<br/>Capacity Tuning"]
    E002 -->|"Negative failures"| E003["Exp 003<br/>Hard Negatives"]
    E003 -->|"Recall loss"| E004["Exp 004<br/>Balanced Dataset"]
    E004 -->|"Real-world gap"| E005["Exp 005 (proposed)<br/>Re-label + Smoke Set"]

    E001 -.->|"Как улучшить matching?"| E002
    E002 -.->|"Почему negative smoke failed?"| E003
    E003 -.->|"Как восстановить recall?"| E004
    E004 -.->|"Как закрыть real-world gap?"| E005
```

| Эксперимент | Что изменялось | Что оставалось неизменным | Ключевой результат | Вопрос к следующему циклу |
|-------------|----------------|---------------------------|--------------------|---------------------------|
| **Exp 001** | Первый LoRA-контур: `r=8`, 4 target modules, `HRA-EXP-V1`, 90 записей | — | Пайплайн работает: обучение стабильно, `valid_json_rate=1.0`, JSON-контракт выполняется; качество matching не проверялось | Какие параметры LoRA улучшат качество? |
| **Exp 002** | Ёмкость адаптера: `r=16`, 7 target modules, пересмотренный split `HRA-EXP-V2` | Базовая модель, runtime-контур, Judge GPT-4.1 | Offline-метрики выросли: `decision_accuracy` 0.444 → 0.778, `MAE_score` 29.78 → 21.89; positive smoke passed, **negative smoke failed** | Почему модель пропускает сложные negative кейсы? |
| **Exp 003** | Состав teacher dataset: добавлены 11 hard-negative/edge-case кандидатов (`HRA-EXP-V3`, 123 записи), формализованы HN1–HN8 / EC1/EC3/EC4 | Модель, LoRA, обучение, runtime | Runtime negative smoke **7/7 passed**, 0 unexpected matches; offline `decision_accuracy` упала до 0.667 — появился over-correction | Как восстановить recall на genuine match, не потеряв hard negatives? |
| **Exp 004** | Пересбалансирование dataset: добавлены 13 positive/borderline кандидатов (`HRA-EXP-V4`, 162 записи), расширен test set до 15 записей, введено сравнение с GPT-4o-mini и external validation | Модель, LoRA, обучение, runtime, все hard-negative записи Exp 003 | Offline `decision_accuracy=0.800`, runtime smoke 7/7 passed, external validation 0.931 vs GPT-4o-mini 0.941; Telegram smoke 35 % vs 43 % у GPT-4o-mini | Как устранить hard-negative failures в real-world условиях? |

**Пояснение.** Все четыре эксперимента используют одну и ту же базовую модель, runtime-контракт и Teacher Judge. Рост качества достигнут не тюнингом адаптера, а последовательным dataset engineering: Exp 002 — ёмкость, Exp 003 — hard negatives, Exp 004 — positive/borderline баланс. Exp 004 показал, что LoRA обобщается на внешних данных, но real-world hard-negative/edge сценарии всё ещё отстают от GPT-4o-mini.

---

## 5. Эволюция Teacher Dataset

```mermaid
flowchart LR
    subgraph "Teacher Dataset"
        V1["V1<br/>90 записей<br/>30 кандидатов"] --> V2["V2<br/>90 записей<br/>30 кандидатов"]
        V2 --> V3["V3<br/>123 записи<br/>41 кандидат<br/>+ Hard Negatives"]
        V3 --> V4["V4<br/>162 записи<br/>54 кандидата<br/>+ Positive / Borderline"]
    end

    subgraph "Independent Validation"
        EV["HRA-EVAL-V5-EXT<br/>102 записи, 34 кандидата<br/>Judge: GPT-4o"]
    end

    V4 -.->|"Проверка обобщения,<br/>no leakage"| EV
```

**Пояснение.** Teacher dataset развивался от V1 к V4: V2 пересмотрел split, V3 добавил hard-negative и edge-case примеры, V4 добавил positive/borderline кандидатов для восстановления recall. `HRA-EVAL-V5-EXT` — **независимая выборка**, а не следующая версия teacher dataset: она не пересекается с train/validation/test по `case_code`, reference labels генерирует GPT-4o вместо GPT-4.1 и служит для cross-check обобщения модели. Подробнее — в [`reports/teacher_dataset_report.md`](reports/teacher_dataset_report.md) и [`reports/external_validation_report.md`](reports/external_validation_report.md).

---

## Связанные документы

| Документ | Назначение |
|----------|-----------|
| [`README.md`](README.md) | Точка входа в подсистему fine-tuning и сводка по экспериментам |
| [`TECHNICAL_FOUNDATION.md`](TECHNICAL_FOUNDATION.md) | Базовая модель, LoRA-конфигурация, инфраструктура, метрики, общий пайплайн |
| [`Experiment_001_Report.md`](Experiment_001_Report.md) | Технический baseline и проверка пайплайна |
| [`Experiment_002_Report.md`](Experiment_002_Report.md) | Параметрическая оптимизация и runtime negative failure |
| [`Experiment_003_Report.md`](Experiment_003_Report.md) | Hard negatives, over-correction и каталог ошибок |
| [`Experiment_004_Report.md`](Experiment_004_Report.md) | Сбалансированный dataset, GPT-4o-mini comparison, external validation, Telegram smoke |
