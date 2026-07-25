# Experiment 001 Report: Technical Baseline

**Кейс:** HR Assistant (hr-assistant)  
**Модуль:** Fine-tuning / Experimental ML-контур  
**Дата начала:** 2026-06-28  
**Дата завершения:** 2026-06-28  
**Статус:** Завершён — пайплайн подтверждён; качество matching не проверялось

---

## 1. Контекст

### 1.1. Что предшествовало

До Experiment 001 в кейсе HR Assistant не проводилось fine-tuning на собственном teacher dataset. Prompt Evaluation уже сформировал reference dataset из 90 кейсов candidate-vacancy matching, но было неизвестно:

- влезет ли LoRA-адаптер в память RunPod RTX A5000;
- сохранятся ли чекпоинты корректно;
- сможет ли модель генерировать валидный JSON в требуемой схеме.

### 1.2. Цель Experiment 001

Experiment 001 ставил цель не получить production-ready модель, а **проверить работоспособность всего технического пайплайна**:

1. LoRA обучается стабильно на Qwen/Qwen2.5-1.5B-Instruct.
2. Чекпоинты сохраняются и могут быть перезагружены.
3. Модель генерирует валидный JSON с полями `role_score`, `skills_score`, `experience_score`, `conditions_score`, `score`, `decision`, `reason`.

Качество matching, production readiness и runtime negative behaviour намеренно не проверялись.

### 1.3. Почему этот эксперимент важен

Experiment 001 — это **технический baseline**. Он доказывает, что инфраструктура fine-tuning в принципе работает в кейсе HR Assistant: dataset → launch contract → GPU preflight → обучение → checkpoint → offline evaluation. Без этого доказательства Experiment 002 не мог бы сосредоточиться на качестве matching.

---

## 2. Гипотеза

**H₀ (нулевая гипотеза):**  
Fine-tuning Qwen/Qwen2.5-1.5B-Instruct с LoRA на teacher dataset HR Assistant не может быть выполнен воспроизводимо: либо обучение падает с ошибкой, либо чекпоинты не сохраняются, либо модель не генерирует валидный JSON.

**H₁ (альтернативная гипотеза):**  
Fine-tuning LoRA на RTX A5000 завершается без ошибок, чекпоинты сохраняются, best checkpoint выбирается по `eval_loss`, и модель возвращает валидный JSON для всех записей тестовой выборки.

**Критерий подтверждения:**
- обучение завершено без ошибок;
- `best_adapter/` создан;
- `valid_json_rate` = 1.0 на generation test.

---

## 3. Изменения относительно предыдущего эксперимента

Experiment 001 — первый цикл fine-tuning в кейсе. Изменений относительно предыдущего эксперимента нет.

| Компонент | Experiment 001 |
|-----------|----------------|
| Teacher dataset | `HRA-EXP-V1`, 90 записей (30 кандидатов) |
| Train / Validation / Test | 72 / 9 / 9 |
| Stratification | obvious_match / borderline / obvious_no_match, 30 записей каждая |
| Hard-negative категории | не формализованы |
| Base model | `Qwen/Qwen2.5-1.5B-Instruct` |
| LoRA rank | 16 |
| LoRA alpha | 32 |
| LoRA dropout | 0.05 |
| Target modules | 7: `q_proj`, `k_proj`, `v_proj`, `o_proj`, `gate_proj`, `up_proj`, `down_proj` |
| Epochs | 5 |
| Batch size | 1, gradient accumulation 4 |
| Learning rate | 2e-4 |

---

## 4. Неизменяемые параметры

| Группа | Параметр | Значение | Источник |
|--------|----------|----------|----------|
| Модель | Base model ID | `Qwen/Qwen2.5-1.5B-Instruct` | [`configs/experiment_001.yaml`](configs/experiment_001.yaml) |
| Runtime | API-контур | FastAPI + Transformers + PEFT ([`../api/hra_qwen_api_lora.py`](../api/hra_qwen_api_lora.py)) | [`configs/experiment_001.yaml`](configs/experiment_001.yaml) |
| Teacher | Judge | GPT-4.1, `temperature = 0` | [`configs/experiment_001.yaml`](configs/experiment_001.yaml) |

Подробное описание технической основы — в [`TECHNICAL_FOUNDATION.md`](TECHNICAL_FOUNDATION.md).

### 4.1. Experimental validity

Experiment 001 не является контролируемым сравнением: у него нет предыдущего эксперимента. Валидность ограничивается технической воспроизводимостью:

| Аспект | Как контролируется |
|--------|-------------------|
| Единственная цель | Проверка пайплайна, а не качества matching. |
| Неизменность модели | `Qwen/Qwen2.5-1.5B-Instruct` для всей серии. |
| Фиксация параметров | Launch contract [`configs/experiment_001.yaml`](configs/experiment_001.yaml). |
| Артефакты запуска | `trainer_state.json`, `adapter_config.json`, `generation_test_report.json`. |

**Угрозы валидности и ограничения:**

- **Нет сравнения с baseline:** не проводилось систематическое сравнение с base Qwen.
- **Нет runtime smoke test:** формализованный smoke set отсутствовал.
- **Качество matching не измерялось:** `decision_accuracy` фиксировался, но не был критерием успеха.
- **Малая выборка:** 9 тестовых записей не позволяют оценить обобщение.

---

## 5. Датасет

### 5.1. Teacher dataset Experiment 001

| Параметр | Значение |
|----------|----------|
| Эксперимент | `HRA-EXP-V1` |
| Dataset | `HRA-EVAL-V1` |
| Всего записей | 90 (30 кандидатов × 3 вакансии) |
| Train | 72 записи (24 кандидата) |
| Validation | 9 записей (3 кандидата) |
| Test | 9 записей (3 кандидата) |

Dataset сформирован из reference dataset Prompt Evaluation. Каждый кандидат оценивается по трём вакансиям:
- Prompt Engineer / AI Automation Specialist;
- Системный аналитик;
- Специалист по разметке данных.

### 5.2. Баланс классов

| Split | Записей | match | no_match | % match |
|-------|---------|-------|----------|---------|
| train | 72 | — | — | — |
| validation | 9 | — | — | — |
| test | 9 | — | — | — |

> Точное распределение match/no_match в V1 не задокументировано отдельно; ориентировочно dataset был сбалансирован по группам obvious_match / borderline / obvious_no_match.

### 5.3. Формат данных

Публичный обезличенный пример формата данных: [`data_sample/example.jsonl`](data_sample/example.jsonl).  
Полное описание схемы и истории версий — в [`reports/teacher_dataset_report.md`](reports/teacher_dataset_report.md).

---

## 6. Выполнение

### 6.1. Участники и роли

| Роль | Ответственность |
|------|-----------------|
| **Пользователь** | Инициатор, владелец решения, утверждение гипотезы и критериев успеха. |
| **VPS Claude Code** | Подготовка кода, датасетов, launch contract, документации. |
| **RunPod Claude Code** | GPU-preflight, обучение, выбор checkpoint, возврат артефактов. |
| **GPT-4.1 (Teacher / Judge)** | Формирование reference labels для teacher dataset. |
| **LoRA-модель** | Обучаемый адаптер Qwen + LoRA. |

### 6.2. Stage-by-stage исполнители

| Этап | Вход | Инструмент | Исполнитель | Выходной артефакт | Критерий завершения |
|------|------|------------|-------------|-------------------|---------------------|
| 1. Пайплайн-контракт | Гипотеза | Markdown-шаблон отчёта | Пользователь + VPS Claude Code | `Experiment_001_Report.md` (Stage 1) | Гипотеза и критерии утверждены |
| 2. Формирование teacher dataset | Reference dataset из Prompt Evaluation | `scripts/extract_teacher_dataset.py` | VPS Claude Code | `train.jsonl`, `validation.jsonl`, `test.jsonl` | Ожидаемое число записей, отсутствие leakage |
| 3. Launch contract | Dataset + параметры | [`configs/experiment_001.yaml`](configs/experiment_001.yaml) | VPS Claude Code | YAML-файл launch contract | Все пути и параметры зафиксированы |
| 4. Обучение | Dataset + launch contract | [`scripts/train_lora.py`](scripts/train_lora.py) | RunPod Claude Code | Чекпоинты, best adapter, `trainer_state.json` | Обучение завершилось без ошибок |
| 5. Offline evaluation | `data/test.jsonl`, best adapter | [`scripts/evaluate_generation_test.py`](scripts/evaluate_generation_test.py) | RunPod Claude Code | `generation_test_report.json` | `valid_json_rate` = 1.0 |
| 6. Документирование | Все метрики | Отчёт эксперимента | VPS Claude Code + Пользователь | `Experiment_001_Report.md` | Вердикт принят и задокументирован |

---

## 7. Результаты обучения

| Метрика | Значение |
|---------|----------|
| Experiment ID | `experiment_001` |
| Лучший чекпоинт | `checkpoint-72` (конец эпохи 4) |
| Best `eval_loss` | **0.2348** |
| Train epochs | 5 |
| Peak VRAM | ~8 GB |
| GPU | NVIDIA RTX A5000 (RunPod) |

### 7.1. Динамика обучения

| Эпоха | Global step | Eval loss | Eval token accuracy |
|-------|-------------|-----------|---------------------|
| 1 | 18 | 0.3444 | 0.9156 |
| 2 | 36 | 0.2457 | 0.9369 |
| 3 | 54 | 0.2351 | 0.9412 |
| 4 | 72 | **0.2348** | 0.9430 |
| 5 | 90 | 0.2391 | 0.9426 |

Eval loss достиг минимума на эпохе 4 и слегка вырос на эпохе 5 — ранняя остановка по `eval_loss` сработала бы на `checkpoint-72`.

---

## 8. Offline evaluation

### 8.1. Generation test (original test set, 9 записей)

| Модель | valid_json_rate | decision_accuracy | MAE_score |
|--------|-----------------|-------------------|-----------|
| Base Qwen | 1.000 | 0.444 | 38.78 |
| **LoRA Experiment 001** | **1.000** | **0.444** | **29.78** |

### 8.2. Интерпретация offline-метрик

- **Главный критерий выполнен:** `valid_json_rate` = 1.0. Модель генерирует валидный JSON.
- `decision_accuracy` совпадает с base Qwen (0.444) — это ожидаемо, потому что целью Exp 001 не было улучшение matching.
- MAE score снизился с 38.78 до 29.78 — LoRA стала ближе к числовым оценкам teacher, но не к принятию решений.

Эти результаты показали, что пайплайн работает, и позволили перейти к параметрической оптимизации в Experiment 002.

---

## 9. Runtime validation

Формализованный runtime smoke test в Experiment 001 не проводился. Runtime API `hra_qwen_api_lora.py` был развёрнут и проверен информально, но не с фиксированным набором кейсов.

| Категория | Статус |
|-----------|--------|
| positive | не проверялся системно |
| obvious_negative | не проверялся системно |
| hard_negative | не формализован |
| edge_case | не формализован |
| invalid_input | не формализован |

---

## 10. Дополнительная валидация

Experiment 001 не включал дополнительную валидацию: ни baseline comparison, ни external validation, ни Telegram smoke test. Целью было подтверждение технического пайплайна, а не оценка качества в production-условиях.

---

## 11. Интерпретация

### 11.1. Что показал эксперимент

1. **Fine-tuning LoRA работает в HR Assistant.** Обучение завершилось стабильно, чекпоинты сохранены, best checkpoint выбран.
2. **JSON-генерация стабильна.** Все тестовые записи вернули валидный JSON.
3. **Пайплайн воспроизводим.** Launch contract, скрипты обучения и evaluation функционируют как единый контур.
4. **Качество matching требует отдельной работы.** Совпадение с base Qwen по decision accuracy показывает, что улучшение matching — не побочный эффект простого обучения.

### 11.2. Главный урок

> Технический baseline необходим, но недостаточен. Пайплайн работает, но для улучшения matching нужна параметрическая оптимизация.

Этот урок стал основанием для Experiment 002.

---

## 12. Вердикт

> **Гипотеза подтверждена.**

| Критерий | Результат |
|----------|-----------|
| LoRA обучается стабильно | ✅ Подтверждено |
| Чекпоинты сохраняются | ✅ Подтверждено |
| JSON-генерация стабильна | ✅ Подтверждено — valid_json_rate = 1.0 |
| Качество matching улучшено | ⚠️ Не проверялось — decision_accuracy совпадает с base Qwen |
| Модель production-ready | ❌ Нет |

**Практический смысл:** Experiment 001 доказал, что fine-tuning-контур HR Assistant функционирует технически. Это позволило в Experiment 002 сосредоточиться на параметрической оптимизации и качестве matching.

---

## 13. Следующий эксперимент

Выводы Experiment 001 непосредственно ведут к **Experiment 002**. Цель следующего цикла — улучшить качество matching, сохранив стабильность пайплайна.

### 13.1. Что исправить

1. **Увеличить ёмкость адаптера** для лучшего усвоения task-специфики.
2. **Систематизировать offline-метрики** как критерий качества.
3. **Добавить runtime smoke validation** для проверки поведения на нерелевантных профилях.

### 13.2. Что оставить неизменным

- Базовая модель `Qwen/Qwen2.5-1.5B-Instruct`;
- Runtime-контур;
- Teacher Judge GPT-4.1, `temperature = 0`;
- Общий экспериментальный пайплайн.

### 13.3. Критерии следующего цикла

- `valid_json_rate` = 1.0;
- `decision_accuracy` > 0.444 на original test set;
- прохождение positive smoke test;
- фиксация результатов negative smoke test (даже если провален).

Эти критерии были реализованы в Experiment 002.

---

## 14. Источники и артефакты

### 14.1. Публичные конфигурации и скрипты

- [`configs/experiment_001.yaml`](configs/experiment_001.yaml) — launch contract;
- [`scripts/train_lora.py`](scripts/train_lora.py) — обучение;
- [`scripts/evaluate_generation_test.py`](scripts/evaluate_generation_test.py) — generation test;
- [`../api/hra_qwen_api_lora.py`](../api/hra_qwen_api_lora.py) — runtime API.

### 14.2. Отчёты и данные

- [`TECHNICAL_FOUNDATION.md`](TECHNICAL_FOUNDATION.md) — техническая основа;
- [`Experiment_002_Report.md`](Experiment_002_Report.md) — следующий эксперимент;
- [`Experiment_003_Report.md`](Experiment_003_Report.md) — отчёт о природе ошибок модели;
- [`Experiment_004_Report.md`](Experiment_004_Report.md) — следующий эксперимент, реализующий баланс precision/recall;
- [`reports/teacher_dataset_report.md`](reports/teacher_dataset_report.md) — анализ teacher dataset;
- [`data_sample/example.jsonl`](data_sample/example.jsonl) — обезличенный пример формата данных.

### 14.3. Идентификаторы запуска

- Experiment ID: `experiment_001`;
- Dataset code: `HRA-EVAL-V1`;
- Experiment code: `HRA-EXP-V1`;
- Best checkpoint: `checkpoint-72` (эпоха 4), выбран по `eval_loss = 0.2348`.

Первичные артефакты запусков (weights, raw metrics, evaluation JSON, operation logs) хранятся в закрытом рабочем контуре и не публикуются в репозитории. В публичной документации представлены агрегированные метрики, конфигурации и код.
