# Визуализации

**Диаграммы и схемы Prompt Evaluation**

---

## Диаграмма архитектуры подсистемы

```mermaid
graph TB
    subgraph Production["Production HR Assistant"]
        C[Candidates] --> M[Matching]
        V[Vacancies] --> M
        M --> Out[Matches]
        M -->|"Prompt A"| PA[Prompt A<br/>gpt-4o-mini]
    end

    subgraph Evaluation["Prompt Evaluation Subsystem"]
        DS[Dataset<br/>HRA-EVAL-V1]
        DS --> Cases[30 Cases<br/>× 3 Vacancies]
        
        Cases --> Judge[Judge Run<br/>gpt-4.1]
        Cases --> A[Prompt A Run<br/>gpt-4o-mini]
        Cases --> B[Prompt B Run<br/>gpt-4o-mini]
        
        Judge --> Ref[Reference Scores]
        A --> ResA[Results A]
        B --> ResB[Results B]
        
        Ref --> Metrics[Metrics Calculation]
        ResA --> Metrics
        ResB --> Metrics
        
        Metrics --> Decision{ACCEPT/REJECT}
    end
    
    Decision -.->|"Decision"| PA
    
    style Production fill:#e1f5fe
    style Evaluation fill:#fff3e0
```

---

## Модель данных

```mermaid
erDiagram
    eval_prompt_datasets ||--o{ eval_prompt_cases : contains
    eval_prompt_datasets ||--o{ eval_prompt_experiments : has
    eval_prompt_cases ||--o{ eval_prompt_case_vacancies : includes
    eval_prompt_experiments ||--o{ eval_prompt_runs : executes
    eval_prompt_runs ||--o{ eval_prompt_results : generates
    eval_prompt_case_vacancies ||--o{ eval_prompt_results : evaluated_in

    eval_prompt_datasets {
        uuid id PK
        string dataset_code UK
        string name
        string description
        string status
    }

    eval_prompt_cases {
        uuid id PK
        uuid dataset_id FK
        string case_code UK
        string case_type
        jsonb candidate_json
    }

    eval_prompt_case_vacancies {
        uuid id PK
        uuid case_id FK
        jsonb vacancy_json
        numeric reference_score
        string reference_decision
    }

    eval_prompt_experiments {
        uuid id PK
        uuid dataset_id FK
        string experiment_code UK
        text prompt_a_text
        text prompt_b_text
        text judge_prompt_text
    }

    eval_prompt_runs {
        uuid id PK
        uuid experiment_id FK
        string run_type
        string status
    }

    eval_prompt_results {
        uuid id PK
        uuid run_id FK
        uuid case_vacancy_id FK
        numeric score
        string decision
        integer latency_ms
    }
```

---

## Жизненный цикл эксперимента

```mermaid
sequenceDiagram
    participant E as Engineer
    participant DB as Database
    participant WF as Workflow
    participant Judge as Judge Model
    participant A as Prompt A
    participant B as Prompt B

    E->>DB: Create Dataset
    E->>DB: Create Experiment
    E->>WF: Start Workflow
    
    WF->>DB: Validate (90 pairs?)
    DB-->>WF: OK
    
    Note over WF, Judge: Phase 1: Judge Run
    loop 90 pairs
        WF->>Judge: Score candidate-vacancy
        Judge-->>WF: reference_score, reference_decision
        WF->>DB: Save reference
    end
    
    Note over WF, A: Phase 2: Prompt A Run
    loop 90 pairs
        WF->>A: Score candidate-vacancy
        A-->>WF: score, decision, latency
        WF->>DB: Save result A
    end
    
    Note over WF, B: Phase 3: Prompt B Run
    loop 90 pairs
        WF->>B: Score candidate-vacancy
        B-->>WF: score, decision, latency
        WF->>DB: Save result B
    end
    
    Note over WF: Phase 4: Metrics
    WF->>DB: Calculate MAE, Latency, Accuracy
    DB-->>WF: Metrics
    
    Note over WF: Phase 5: Decision
    WF->>WF: Check Acceptance Criteria
    WF-->>E: ACCEPT or REJECT
```

---

## Workflow последовательность

```mermaid
flowchart TD
    Start([Start]) --> Config[Run Config]
    Config --> Check{Experiment<br/>Ready?}
    
    Check -->|No| Error[Error: Not Ready]
    Check -->|Yes| Judge[Create Judge Run]
    
    Judge --> JudgeLoop{More<br/>pairs?}
    JudgeLoop -->|Yes| JudgeCall[Call gpt-4.1]
    JudgeCall --> JudgeSave[Save reference_score]
    JudgeSave --> JudgeLoop
    JudgeLoop -->|No| JudgeDone[Complete Judge Run]
    
    JudgeDone --> A[Create Prompt A Run]
    A --> ALoop{More<br/>pairs?}
    ALoop -->|Yes| ACall[Call gpt-4o-mini]
    ACall --> ASave[Save result A]
    ASave --> ALoop
    ALoop -->|No| ADone[Complete Prompt A Run]
    
    ADone --> B[Create Prompt B Run]
    B --> BLoop{More<br/>pairs?}
    BLoop -->|Yes| BCall[Call gpt-4o-mini]
    BCall --> BSave[Save result B]
    BSave --> BLoop
    BLoop -->|No| BDone[Complete Prompt B Run]
    
    BDone --> Metrics[Calculate Metrics]
    Metrics --> Report[Generate Report]
    Report --> Decision{MAE ≥ 20%<br/>AND<br/>Lat ≤ 30%?}
    
    Decision -->|Yes| Accept[ACCEPT Prompt B]
    Decision -->|No| Reject[REJECT Prompt B]
    
    Accept --> End([End])
    Reject --> End
```

---

## Сравнение MAE по сегментам

```mermaid
xychart-beta
    title "MAE по сегментам: Prompt A vs Prompt B"
    x-axis ["obvious_match", "obvious_no_match", "borderline"]
    y-axis "MAE" 0 --> 20
    bar [9.50, 11.97, 9.43]
    bar [13.90, 15.57, 17.77]
```

**Интерпретация:**
- Prompt B показывает **худшие** результаты на всех сегментах
- Наибольшая деградация — на `borderline` кейсах (+88.3%)
- Наилучшая производительность Prompt A — на `borderline` (MAE = 9.43)

---

## Сравнение Accuracy по сегментам

```mermaid
xychart-beta
    title "Accuracy по сегментам: Prompt A vs Prompt B"
    x-axis ["obvious_match", "obvious_no_match", "borderline"]
    y-axis "Accuracy %" 85 --> 101
    bar [93.33, 100.00, 93.33]
    bar [93.33, 100.00, 90.00]
```

**Интерпретация:**
- На `obvious_match` и `obvious_no_match` Accuracy идентична
- На `borderline` Prompt B теряет **3.3 п.п.** accuracy
- Оба промпта корректно распознают очевидные кейсы

---

## Сравнение Latency по сегментам

```mermaid
xychart-beta
    title "Latency по сегментам: Prompt A vs Prompt B"
    x-axis ["obvious_match", "obvious_no_match", "borderline"]
    y-axis "Latency (ms)" 1500 --> 2600
    bar [2029, 2139, 1981]
    bar [2126, 2182, 2415]
```

**Интерпретация:**
- Prompt B медленнее на всех сегментах
- Наибольшая разница — на `borderline` кейсах (+21.9%)
- В среднем latency увеличилась на **9.3%**

---

## Критерии принятия

```mermaid
flowchart TD
    Start([Результат эксперимента])
    
    Start --> MAE{MAE Improvement<br/>≥ 20%?}
    
    MAE -->|Да| Lat{Latency Growth<br/>≤ 30%?}
    MAE -->|Нет| Fail[❌ REJECT]
    
    Lat -->|Да| Success[✅ ACCEPT Prompt B]
    Lat -->|Нет| Fail
    
    Success --> End([Миграция на Prompt B])
    Fail --> End2([Остаться на Prompt A])
    
    style Success fill:#c8e6c9
    style Fail fill:#ffcdd2
    style MAE fill:#fff9c4
    style Lat fill:#fff9c4
```

**Результат HRA-EXP-V1:**
- MAE Improvement: **-52.86%** ❌
- Latency Growth: **+9.34%** ✅
- Финальное решение: **REJECT** (один критерий не выполнен)

---

## Распределение кейсов по типам

```mermaid
pie title "Датасет HRA-EVAL-V1"
    "obvious_match" : 30
    "obvious_no_match" : 30
    "borderline" : 30
```

---

## Принцип изоляции подсистем

```mermaid
graph LR
    subgraph Production["Production"]
        P[Production<br/>Matching]
        PD[(Production<br/>Database)]
        P --> PD
    end
    
    subgraph Evaluation["Prompt Evaluation"]
        E[Experiment<br/>Workflow]
        ED[(Evaluation<br/>Database)]
        E --> ED
    end
    
    E -.->|"Decision"| P
    
    style Production fill:#e3f2fd
    style Evaluation fill:#fff8e1
```

**Правило:** Данные не переходят из Evaluation в Production. Только решение инженера влияет на смену промпта.

---

## Стоимость эксперимента

```mermaid
pie title "Распределение API вызовов"
    "Judge (gpt-4.1)" : 90
    "Prompt A (gpt-4o-mini)" : 90
    "Prompt B (gpt-4o-mini)" : 90
```

| Компонент | Модель | Вызовы | Стоимость |
|-----------|--------|--------|-----------|
| Judge | gpt-4.1 | 90 | ~$2.70 |
| Prompt A | gpt-4o-mini | 90 | ~$0.90 |
| Prompt B | gpt-4o-mini | 90 | ~$0.90 |
| **Итого** | — | **270** | **~$4.50** |

---

*Визуализации Prompt Evaluation*