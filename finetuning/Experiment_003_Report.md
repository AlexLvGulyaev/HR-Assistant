# Experiment 003 Report: Understanding Model Failures Through Hard Negatives

**Кейс:** HR Assistant (hr-assistant)  
**Модуль:** Fine-tuning / Experimental ML-контур  
**Дата начала:** 2026-07-21  
**Дата завершения:** 2026-07-22  
**Статус:** Завершён — гипотеза частично подтверждена; выявлены ограничения модели, требующие следующего цикла

---

## 1. Контекст

### 1.1. Что предшествовало

К моменту начала Experiment 003 в кейсе HR Assistant уже было проведено два цикла fine-tuning:

- **Experiment 001** — технический baseline. Код пайплайна разработан в диалоге с ChatGPT; запуск и управление выполнял пользователь вручную на RunPod. Подтверждено: LoRA обучается стабильно, чекпоинты сохраняются, JSON-формат генерируется.
- **Experiment 002** — параметрическая оптимизация: rank 8 → 16, target modules 4 → 7. Код и launch contract также разработаны в диалоге с ChatGPT; запуск и управление выполнял пользователь вручную на RunPod. Offline-метрики выросли (`eval_loss=0.44`, `decision_accuracy=0.778`), но runtime negative smoke test не пройден — модель давала ложные срабатывания на нерелевантных профилях.

Experiment 003 стал переходом к следующему режиму работы: Claude Code развёрнут непосредственно на RunPod и участвует в GPU-этапах пайплайна вместе с пользователем. Это развитие процесса, а не смена инструмента: исходный пайплайн, сформированный в Experiments 001–002, сохранён и расширен.

Проблема Experiment 002 была не в архитектуре или гиперпараметрах, а в **составе teacher dataset**: в нём не хватало примеров сложных отрицательных сценариев, которые встречаются в реальном matching.

### 1.2. Цель Experiment 003

Experiment 003 поставил цель не просто улучшить метрики, а **понять природу ошибок модели**. Нужно было ответить на вопрос: *какие именно кейсы ломают production-like matching, и как их нужно представить в teacher dataset, чтобы модель научилась их корректно отклонять?*

Этот эксперимент впервые ввёл:

- **hard-negative категории HN1–HN8**;
- **edge-case классификацию EC1 / EC3 / EC4**;
- **системный анализ failure modes**;
- **понимание, чему именно нужно учить модель дальше**.

### 1.3. Почему этот эксперимент важен

Experiment 003 — это не «предыдущая версия» Experiment 004. Это отчёт о том, **как мы поняли, в чём проблема**. Его выводы стали инженерным основанием для Experiment 004. Без Exp 003 Exp 004 выглядел бы как произвольная доводка dataset; благодаря Exp 003 Exp 004 становится проверкой конкретного вывода: «модель нужно научить отличать hard negatives, не теряя recall на genuine match».

---

## 2. Гипотеза

**H₀ (нулевая гипотеза):**  
Изменение состава teacher dataset путём добавления hard-negative и edge-case примеров не оказывает практически значимого влияния на способность модели корректно проходить runtime negative smoke test при неизменных параметрах обучения, архитектуре модели и runtime-контуре.

**H₁ (альтернативная гипотеза):**  
Расширение teacher dataset за счёт hard-negative и edge-case примеров улучшает способность модели корректно обрабатывать сложные отрицательные сценарии в runtime negative smoke test без существенного ухудшения остальных ключевых метрик относительно Experiment 002.

**Критерий подтверждения:**
- runtime negative smoke test проходит без unexpected matches;
- `valid_json_rate` сохраняется равным 1.0;
- offline-метрики не ухудшаются критически (decision_accuracy ≥ 0.60, MAE ≤ 30).

---

## 3. Изменения относительно предыдущего эксперимента

| Компонент | Experiment 002 | Experiment 003 |
|-----------|----------------|----------------|
| Teacher dataset | `HRA-EXP-V2`, 90 записей (30 кандидатов) | `HRA-EXP-V3`, 123 записи (41 кандидат) |
| Hard-negative кандидаты | 0 целенаправленных | 11 (`HRA-EVAL-V2-000101`–`HRA-EVAL-V2-000111`) |
| Hard-negative категории | не формализованы | HN1–HN8, EC1/EC3/EC4 |
| Train+val match % | ~20% | 15.7% |
| Train+val no_match % | ~80% | 84.3% |
| Test set | 9 записей (исходный V2) | 9 записей (без изменений) |
| Hard negative holdout | отсутствовал | 6 записей (2 кандидата) |
| Runtime smoke set | не формализован | `data/smoke_set.jsonl`, 7 кейсов |

Единственная изменяемая переменная — состав teacher dataset. Все параметры модели, LoRA, обучения и runtime-контура остались прежними.

---

## 4. Неизменяемые параметры

| Группа | Параметр | Значение | Источник |
|--------|----------|----------|----------|
| Модель | Base model ID | `Qwen/Qwen2.5-1.5B-Instruct` | [`configs/experiment_003.yaml`](configs/experiment_003.yaml) |
| LoRA | `r` | `16` | [`configs/experiment_003.yaml`](configs/experiment_003.yaml) |
| LoRA | `lora_alpha` | `32` | [`configs/experiment_003.yaml`](configs/experiment_003.yaml) |
| LoRA | `lora_dropout` | `0.05` | [`configs/experiment_003.yaml`](configs/experiment_003.yaml) |
| LoRA | `target_modules` | `q_proj, k_proj, v_proj, o_proj, gate_proj, up_proj, down_proj` | [`configs/experiment_003.yaml`](configs/experiment_003.yaml) |
| LoRA | `bias` | `none` | [`configs/experiment_003.yaml`](configs/experiment_003.yaml) |
| Обучение | `num_train_epochs` | `5` | [`configs/experiment_003.yaml`](configs/experiment_003.yaml) |
| Обучение | `per_device_train_batch_size` | `1` | [`configs/experiment_003.yaml`](configs/experiment_003.yaml) |
| Обучение | `gradient_accumulation_steps` | `4` | [`configs/experiment_003.yaml`](configs/experiment_003.yaml) |
| Обучение | `learning_rate` | `2e-4` | [`configs/experiment_003.yaml`](configs/experiment_003.yaml) |
| Обучение | `optim` | `adamw_torch` | [`configs/experiment_003.yaml`](configs/experiment_003.yaml) |
| Обучение | `fp16` | `True` | [`configs/experiment_003.yaml`](configs/experiment_003.yaml) |
| Обучение | Best checkpoint metric | `eval_loss` (minimize) | [`configs/experiment_003.yaml`](configs/experiment_003.yaml) |
| Обучение | `seed` | `42` | [`configs/experiment_003.yaml`](configs/experiment_003.yaml) |
| Runtime | API-контур | FastAPI + Transformers + PEFT ([`../api/hra_qwen_api_lora.py`](../api/hra_qwen_api_lora.py)) | [`configs/experiment_003.yaml`](configs/experiment_003.yaml) |
| Teacher | Judge | GPT-4.1, `temperature = 0` | [`configs/experiment_003.yaml`](configs/experiment_003.yaml) |

Подробное описание технической основы — в [`TECHNICAL_FOUNDATION.md`](TECHNICAL_FOUNDATION.md).

### 4.1. Experimental validity

Все параметры, кроме состава teacher dataset, зафиксированы. Это позволяет интерпретировать различия в результатах как следствие именно изменения dataset, а не модели, обучения или runtime-контура.

| Аспект | Как контролируется |
|--------|-------------------|
| Единственная изменяемая переменная | Состав teacher dataset: добавлены 11 hard-negative/edge-case кандидатов (`HRA-EVAL-V2-000101`–`HRA-EVAL-V2-000111`) к 30 кандидатам Exp 002. |
| Неизменность модели и LoRA | `Qwen/Qwen2.5-1.5B-Instruct`, `r=16`, `alpha=32`, `target_modules` и прочие параметры совпадают с Exp 002. |
| Неизменность обучения | 5 эпох, batch=1, grad_accum=4, lr=2e-4, `eval_loss` для выбора best checkpoint. |
| Неизменность runtime | FastAPI + Transformers + PEFT, тот же smoke set, та же процедура запуска. |
| Прямое сравнение с Exp 002 | Original test set (`data/test.jsonl`) оставлен без изменений; метрики Exp 002 и Exp 003 измерены на одних и тех же 9 записях. |

**Угрозы валидности и ограничения:**

- **Малый test set:** 9 записей не позволяют надёжно оценить recall и FNR.
- **Ограниченный holdout:** 6 записей (2 кандидата) — только начало обобщения на незнакомые hard negatives.
- **Зависимость от Judge:** все reference labels сгенерированы GPT-4.1 с `temperature=0`; любые систематические ошибки Judge наследуются моделью.
- **Ограничения обобщения:** результаты покрывают три вакансии и восемь hard-negative категорий; они не гарантируют качество на произвольных вакансиях или доменах.
- **Однократная Judge-разметка:** повторные прогоны не проводились; пограничные кейсы с `score >= 60` и `decision=no_match` сохранены как есть.

---

## 5. Датасет

### 5.1. Teacher dataset Experiment 003

| Параметр | Значение |
|----------|----------|
| Эксперимент | `HRA-EXP-V3` |
| Dataset | `HRA-EVAL-V3` |
| Всего записей | 123 (41 кандидат × 3 вакансии) |
| Train | 93 записи (31 кандидат) |
| Validation | 15 записей (5 кандидатов) |
| Test | 9 записей (3 кандидата, исходный V2) |
| Hard negative holdout | 6 записей (2 кандидата) |

Dataset формировался так:
- **30 кандидатов Experiment 002** (90 записей) сохранены без изменений.
- **11 новых hard-negative / edge-case кандидатов** (`HRA-EVAL-V2-000101`–`HRA-EVAL-V2-000111`, 33 записи) добавлены в train/validation/holdout.

### 5.2. Баланс классов

| Split | Записей | match | no_match | % match |
|-------|---------|-------|----------|---------|
| train | 93 | 14 | 79 | 15.1% |
| validation | 15 | 3 | 12 | 20.0% |
| train+val | 108 | 17 | 91 | 15.7% |
| test | 9 | 3 | 6 | 33.3% |
| holdout | 6 | 1 | 5 | 16.7% |

### 5.3. Вакансии

Каждый кандидат оценивается по трём вакансиям:
- Prompt Engineer / AI Automation Specialist;
- Системный аналитик;
- Специалист по разметке данных.

### 5.4. Формат данных

Публичный обезличенный пример формата данных: [`data_sample/example.jsonl`](data_sample/example.jsonl).  
Полное описание схемы и истории версий — в [`reports/teacher_dataset_report.md`](reports/teacher_dataset_report.md).

---

## 6. Выполнение

### 6.1. Участники и роли

| Роль | Ответственность |
|------|-----------------|
| **Пользователь** | Инициатор, владелец решения, утверждение гипотез, критериев успеха, split-стратегии и итогового вердикта. |
| **VPS Claude Code** | Подготовка кода, SQL-скриптов, датасетов, launch contract, структурной preflight, offline evaluation, документации. |
| **RunPod Claude Code** | GPU-preflight, обучение, выбор checkpoint, runtime smoke, возврат артефактов. |
| **GPT-4.1 (Teacher / Judge)** | Формирование reference labels для teacher dataset. |
| **LoRA-модель** | Обучаемый адаптер Qwen + LoRA. |
| **Telegram / n8n** | Runtime-контур для smoke validation. |

### 6.2. Stage-by-stage исполнители

| Этап | Вход | Инструмент | Исполнитель | Выходной артефакт | Критерий завершения |
|------|------|------------|-------------|-------------------|---------------------|
| 1. Исследовательский контракт | Результаты Experiment 002 | Markdown-шаблон отчёта | Пользователь + VPS Claude Code | `Experiment_003_Report.md` (Stage 1) | Гипотеза и критерии утверждены |
| 2. Аудит failure modes Experiment 002 | `generation_test_report.json`, runtime observations | Анализ отчётов | VPS Claude Code | Список ошибок Exp 002, обоснование гипотезы | Идентифицированы наблюдаемые failure modes |
| 3. Каталог hard-negative категорий | Failure modes | Инженерная классификация | VPS Claude Code + Пользователь | Каталог HN1–HN8, EC1/EC3/EC4 | Каждая категория описывает структуру данных, а не ожидаемое поведение модели |
| 4. Спроектировать hard-negative кандидатов | Каталог категорий | Профили кандидатов | VPS Claude Code | 11 новых кандидатов (`000101`–`000111`) | Все обязательные категории покрыты; уникальность `case_code` |
| 5. SQL и Judge-разметка | Спецификация кандидатов | SQL-скрипты + n8n workflow | VPS Claude Code + Пользователь | 123 размеченные пары | Все пары валидированы |
| 6. Формирование teacher dataset | Reference-разметка | [`scripts/extract_teacher_dataset.py`](scripts/extract_teacher_dataset.py) | VPS Claude Code | `train.jsonl`, `validation.jsonl`, `test.jsonl`, `holdout.jsonl` | Стратификация и отсутствие leakage |
| 7. Launch contract и transfer package | Dataset + параметры | [`configs/experiment_003.yaml`](configs/experiment_003.yaml) | VPS Claude Code | Launch contract, transfer list | Все пути и команды зафиксированы |
| 8. Обучение и evaluation на RunPod | Dataset + launch contract | [`scripts/train_lora.py`](scripts/train_lora.py), [`scripts/evaluate_generation_test.py`](scripts/evaluate_generation_test.py) | RunPod Claude Code | Best adapter, offline metrics | Best checkpoint выбран, criteria passed |
| 9. Runtime validation | `data/smoke_set.jsonl` | [`../api/hra_qwen_api_lora.py`](../api/hra_qwen_api_lora.py) + [`scripts/runtime_smoke_test.py`](scripts/runtime_smoke_test.py) | RunPod Claude Code | Runtime smoke report | 7/7 passed, 0 unexpected matches |
| 10. Документирование и вердикт | Все метрики + анализ ошибок | Отчёт эксперимента | VPS Claude Code + Пользователь | `Experiment_003_Report.md` | Вердикт принят и задокументирован; ограничения модели сформулированы |

---

## 7. Результаты обучения

| Метрика | Значение |
|---------|----------|
| Experiment ID | `experiment_003` |
| Лучший чекпоинт | `checkpoint-48` (конец эпохи 2) |
| Best `eval_loss` | **0.3108** |
| Train epochs | 5 |
| Время обучения | ~180 секунд |
| Peak VRAM | ~7.4 GB |
| GPU | NVIDIA RTX A5000 (RunPod) |

Early convergence: лучший чекпоинт достигается на эпохе 2; дальнейшие эпохи не улучшают validation loss.

---

## 8. Offline evaluation

### 8.1. Generation test (original test set, 9 записей)

| Модель | valid_json_rate | decision_accuracy | MAE_score |
|--------|-----------------|-------------------|-----------|
| Base Qwen | 1.000 | 0.222 | 38.33 |
| LoRA Experiment 002 | 1.000 | 0.778 | 21.89 |
| **LoRA Experiment 003** | **1.000** | **0.667** | **22.22** |

> **Доказательство:** summary метрик и примеры Base vs LoRA — в [`data/evidence/experiment_003_generation_test_summary.json`](data/evidence/experiment_003_generation_test_summary.json).

### 8.2. Интерпретация offline-метрик

- LoRA Exp 003 значительно превосходит base Qwen, но уступает Exp 002 по decision accuracy (−11.1 pp).
- Главный эффект виден не в метриках, а в **runtime negative smoke test**: Exp 003 впервые проходит его.
- Появились ложные отрицательные решения на genuine match-кейсах (`HRA-EVAL-V2-000010` системный аналитик, `HRA-EVAL-V2-000030` специалист по разметке). Это не ошибка обучения, а **индикатор дисбаланса dataset**: модель научилась штрафовать за отсутствие ключевых слов, но не сохранила способность признавать наличие соответствия.

---

## 9. Runtime validation

| Категория | Cases | Passed | Failed |
|-----------|-------|--------|--------|
| positive | 1 | 1 | 0 |
| obvious_negative | 1 | 1 | 0 |
| hard_negative | 2 | 2 | 0 |
| edge_case | 1 | 1 | 0 |
| invalid_input | 1 | 1 | 0 |
| stability_repeat | 1 | 1 | 0 |
| **Итого** | **7** | **7** | **0** |

**Ключевой вывод:** все заранее зафиксированные отрицательные и edge-case сценарии корректно отклонены; unexpected matches отсутствуют. Это главное достижение Experiment 003.

> **Доказательство:** полные ответы LoRA по каждому smoke-кейсу — в [`data/evidence/experiment_003_runtime_smoke.json`](data/evidence/experiment_003_runtime_smoke.json).

#### Representative example: устранение false positive

**Candidate:** Врач-терапевт, 7 лет клинического опыта, навыки работы с пациентами и медицинской документацией; нет IT/AI навыков.

**Vacancy:** Prompt Engineer / AI Automation Specialist; требуется prompt engineering, n8n, API, JSON, LLM, автоматизация бизнес-процессов.

**Reference / expected:** `no_match`.

**Model prediction (LoRA Experiment 003):** `no_match`, score 0 — модель отклоняет нерелевантный профиль и не использует медицинский опыт как обоснование соответствия.

**Почему этот пример важен:** Показывает, что добавление hard negatives в teacher dataset научило модель корректно отклонять полностью нерелевантную профессию (HN-1), чего Exp 002 не умел.

**Evidence:** [`data/evidence/experiment_003_runtime_smoke.json`](data/evidence/experiment_003_runtime_smoke.json), кейс `SMOKE-NEGATIVE-001`, category `obvious_negative`.

---

#### Representative example: over-correction

**Candidate:** Системный аналитик, 6 лет опыта, SQL, BPMN, REST API, UML, Agile, документирование, зарплата 190 000 ₽.

**Vacancy:** Системный аналитик; требования совпадают с профилем кандидата.

**Reference:** `match`, score 98.

**Model prediction (LoRA Experiment 003):** `no_match`, score 43, с обоснованием, что у кандидата "не указаны аналитические или технические навыки".

**Почему этот пример важен:** Иллюстрирует цену hard negatives без компенсирующих positive примеров: модель стала слишком консервативной и стала отклонять genuine match.

**Evidence:** [`data/evidence/experiment_003_overcorrection.jsonl`](data/evidence/experiment_003_overcorrection.jsonl), запись `HRA-EVAL-V2-000010`, vacancy "Системный аналитик".

---

## 10. Дополнительная валидация: каталог ошибок

### 10.1. Почему нужен был каталог ошибок

До Experiment 003 runtime negative smoke test в Exp 002 провалился, но не было структурированного понимания, **какие именно типы кейсов ломают модель**. Hard negatives — это не просто «сложные негативы», а классы ошибок, которые повторяются в production matching. Без их формализации невозможно было:

- систематически генерировать teacher dataset;
- измерить, научилась ли модель конкретному паттерну;
- понять, какие паттерны остаются непокрытыми.

### 10.2. Hard-negative категории HN1–HN8

| Категория | Название | Что проверяет | Пример | Урок для модели |
|-----------|----------|---------------|--------|-----------------|
| **HN-1** | Полностью нерелевантная профессия (non-IT в IT) | Снижает ли модель положительные решения на профилях без IT-компетенций | Врач-терапевт для вакансии Prompt Engineer | Название должности и soft skills не компенсируют отсутствие профильной базы |
| **HN-2** | Смежная роль без обязательных навыков | Различает ли модель тождественные и смежные профессии | Бизнес-аналитик с BPMN/UML, но без SQL/API, для системного аналитика | Формальная близость названий недостаточна; нужны конкретные hard skills |
| **HN-3** | Совпадение по общим словам без совпадения по компетенциям | Снижает ли модель влияние лексических совпадений | Data analyst для Prompt Engineer («аналитик» в названии) | Содержание компетенций важнее лексического сходства |
| **HN-4** | Сильный профиль в нерелевантной специализации | Не завышает ли общая сила профиля релевантность | Python backend-разработчик для Prompt Engineer | Глубокий опыт в смежной области ≠ релевантность для целевой роли |
| **HN-5** | Одиночное совпадение навыка без основного профиля | Требует ли модель комплексного набора компетенций | Копирайтер со знанием JSON для Prompt Engineer | Один-два навыка из требований не делают профиль подходящим |
| **HN-6** | Разница в уровне опыта (junior vs senior) | Учитывает ли модель уровень опыта при прочей релевантности | Junior разработчик для senior-роли | Релевантность зависит от уровня ответственности в вакансии |
| **HN-7** | Разница в функциональной роли (управленческая vs исполнительская) | Различает ли модель управленческий и исполнительский опыт | IT-руководитель / PM для исполнительской роли | Управленческий опыт не заменяет hands-on навыки |
| **HN-8** | Дисбаланс soft skills и hard skills | Сохраняет ли модель баланс между soft и hard skills | Коммьюнити-менеджер с сильными коммуникациями для технической роли | Сильные soft skills не компенсируют отсутствие технической базы |

### 10.3. Edge-case категории EC1 / EC3 / EC4

| Категория | Название | Что проверяет | Пример | Урок для модели |
|-----------|----------|---------------|--------|-----------------|
| **EC-1** | Неоднозначные пограничные случаи (score около 60) | Стабильна ли граница между match и no_match | Кандидат с частичным соответствием и разными решениями по вакансиям | Порог 60 — не единственный критерий; нужен content-aware анализ |
| **EC-3** | Формально похожее название должности при несовместимом содержании | Оценивает ли модель содержание, а не только название | «Аналитик данных» vs «Системный аналитик» | Название должности может вводить в заблуждение |
| **EC-4** | Несоответствие по условиям при сильном профиле | Сохраняет ли модель оценку условий при сильном профиле | Сильный кандидат с зарплатными ожиданиями вне бюджета | Conditions_score должен работать независимо от силы профиля |

### 10.4. Failure modes Experiment 002, которые исправил Experiment 003

| # | case_code | Вакансия | Проблема Exp 002 | Почему это важно | Какая категория покрывает |
|---|-----------|----------|------------------|------------------|---------------------------|
| 1 | `HRA-EVAL-V2-000020` | Специалист по разметке данных | False positive: врач получил `match` (score 72) | Модель использовала нерелевантные soft skills («внимательность») как обоснование высокого score | HN-1, HN-8 |
| 2 | `HRA-EVAL-V2-000020` | Prompt Engineer | Завышенный score (57 при reference 19) | Модель придавала вес общим словам без проверки профильной базы | HN-1, HN-3 |
| 3 | `HRA-EVAL-V2-000020` | Системный аналитик | conditions_score максимален при salary mismatch | Модель игнорировала условия при сильном профиле | EC-4 |
| 4 | `HRA-EVAL-V2-000030` | Специалист по разметке данных | Borderline case нестабилен | Пограничные кейсы требуют явного обучения | EC-1 |

### 10.5. Over-correction: новые ошибки, которые выявил Experiment 003

Добавление hard negatives решило старые проблемы, но создало новые. Модель стала слишком консервативной:

| case_code | Вакансия | reference | Exp 003 LoRA | Дельта | Причина over-correction |
|-----------|----------|-----------|--------------|--------|-------------------------|
| `HRA-EVAL-V2-000010` | Prompt Engineer / AI Automation Specialist | match (60) | no_match (54) | −6 | Модель стала штрафовать системного аналитика за отсутствие prompt engineering навыков |
| `HRA-EVAL-V2-000010` | Системный аналитик | match (98) | no_match (43) | −55 | Игнорирование совпадения по названию должности и заявленных навыков |
| `HRA-EVAL-V2-000030` | Специалист по разметке данных | match (64) | no_match (45) | −19 | Content manager не распознаётся как подходящий для разметки данных |

> **Доказательство:** полные `reference`, Base Qwen и LoRA prediction для over-correction кейсов — в [`data/evidence/experiment_003_overcorrection.jsonl`](data/evidence/experiment_003_overcorrection.jsonl).

Эти кейсы показали, что **hard negatives без компенсирующих positive/borderline примеров ведут к over-correction**. Модель научилась искать отсутствие ключевых слов, но потеряла способность признавать наличие соответствия на смежных профилях.

### 10.6. Почему high validation accuracy не гарантирует production-качество

Experiment 003 прошёл runtime smoke test, но не стал production-ready. Почему:

- **Малый test set** (9 записей) не позволяет надёжно измерить recall.
- **Дисбаланс в сторону no_match** (84.3% в train+val) делает модель консервативной.
- **Отсутствие positive/borderline примеров** для смежных ролей не даёт модели научиться распознавать genuine match в сложных случаях.
- **Offline-метрики не покрывают production-like hard-negative сценарии**: runtime smoke test проверяет 7 кейсов, а реальный Telegram-контур содержит десятки граничных профилей.

Эти ограничения стали инженерным основанием для Experiment 004.

---

## 11. Интерпретация

### 11.1. Что показал эксперимент

1. **Hard negatives — рабочий инструмент.** Модель действительно научилась корректно отклонять сложные отрицательные сценарии, которые ломали Exp 002.
2. **Dataset engineering сильнее adapter tuning.** Гиперпараметры LoRA неизменны с Exp 002. Всё изменение качества связано с составом teacher dataset.
3. **Over-correction — реальный риск.** Добавление negative примеров без компенсирующих positive примеров снижает recall на genuine match.
4. **Нужна типология ошибок.** Без категорий HN1–HN8 и EC1/EC3/EC4 невозможно систематически генерировать dataset и измерять прогресс по конкретным failure modes.

### 11.2. Почему offline и runtime результаты расходятся

- Offline test set (9 записей) показывает снижение decision accuracy — это проявление over-correction.
- Runtime smoke test (7 кейсов) показывает успех — hard negatives работают.
- Расхождение объясняется **разным покрытием сценариев**: offline test не содержит production-like hard negatives, а runtime smoke set специально их включает.

### 11.3. Главный урок

> Hard negatives необходимы, но недостаточны. Чтобы получить production-ready модель, нужно одновременно:
> - сохранить hard-negative достижения;
> - добавить positive/borderline примеры для смежных ролей;
> - расширить test set;
> - ввести stratified метрики по категориям ошибок.

Этот урок стал основанием для Experiment 004.

---

## 12. Вердикт

> **Гипотеза частично подтверждена.**

| Критерий | Результат |
|----------|-----------|
| Hard negatives улучшают runtime negative smoke | ✅ Подтверждено — 7/7 passed, 0 unexpected matches |
| JSON-генерация остаётся стабильной | ✅ Подтверждено — valid_json_rate = 1.0 |
| Качество на original test set не ухудшается критически | ⚠️ Частично — decision_accuracy снизилась с 0.778 до 0.667 |
| Модель production-ready | ❌ Нет |

**Практический смысл:** Experiment 003 доказал, что проблема Experiment 002 — в dataset, а не в модели. Он дал первую системную типологию ошибок (HN1–HN8, EC1/EC3/EC4) и показал, что hard negatives работают. Однако он же выявил новое ограничение — over-correction — которое требует следующего цикла.

---

## 13. Следующий эксперимент

Выводы Experiment 003 непосредственно ведут к **Experiment 004**. Цель следующего цикла — устранить over-correction, сохранив достижения по hard negatives.

### 13.1. Что исправить

1. **Пересбалансировать teacher dataset в сторону positive/borderline.** Довести долю match в train+val до 25–30% при сохранении 33 hard-negative записей.
2. **Добавить positive примеры для смежных профилей**, которые ломаются:
   - Системный аналитик с SQL/BPMN/REST API;
   - AI Automation Specialist / Prompt Engineer с релевантным опытом;
   - Специалист по разметке данных с прямым опытом annotation/ML.
3. **Добавить borderline примеры** со score 55–65 и обоими решениями (match/no_match) для калибровки порога.
4. **Расширить test set** до ≥15 записей с сохранением стратификации.

### 13.2. Что оставить неизменным

- Базовая модель `Qwen/Qwen2.5-1.5B-Instruct`;
- LoRA параметры (`r=16`, `alpha=32`, `target_modules`);
- Параметры обучения (5 эпох, batch=1, grad_accum=4, lr=2e-4);
- Runtime-контур;
- Teacher Judge GPT-4.1, `temperature = 0`;
- Все 33 hard-negative записи Experiment 003.

### 13.3. Критерии следующего цикла

- `decision_accuracy` ≥ 0.75 на расширенном test set;
- `MAE_score` ≤ 22;
- `valid_json_rate` = 1.0;
- runtime smoke test 7/7 passed;
- нет false positives на obvious_no_match;
- нет false negatives на obvious_match.

Эти критерии были реализованы в Experiment 004.

---

## 14. Источники и артефакты

### 14.1. Публичные конфигурации и скрипты

- [`configs/experiment_003.yaml`](configs/experiment_003.yaml) — launch contract;
- [`scripts/train_lora.py`](scripts/train_lora.py) — обучение;
- [`scripts/evaluate_generation_test.py`](scripts/evaluate_generation_test.py) — generation test;
- [`scripts/evaluate_test.py`](scripts/evaluate_test.py) — eval loss;
- [`scripts/runtime_smoke_test.py`](scripts/runtime_smoke_test.py) — runtime smoke;
- [`../api/hra_qwen_api_lora.py`](../api/hra_qwen_api_lora.py) — runtime API.

### 14.2. Отчёты и данные

- [`TECHNICAL_FOUNDATION.md`](TECHNICAL_FOUNDATION.md) — техническая основа;
- [`Experiment_002_Report.md`](Experiment_002_Report.md) — предыдущий эксперимент;
- [`Experiment_004_Report.md`](Experiment_004_Report.md) — следующий эксперимент, реализующий выводы Exp 003;
- [`reports/teacher_dataset_report.md`](reports/teacher_dataset_report.md) — анализ teacher dataset;
- [`data_sample/example.jsonl`](data_sample/example.jsonl) — обезличенный пример формата данных.

### 14.3. Идентификаторы запуска

- Experiment ID: `experiment_003`;
- Dataset code: `HRA-EVAL-V3`;
- Experiment code: `HRA-EXP-V3`;
- Best checkpoint: `checkpoint-48` (эпоха 2), выбран по `eval_loss = 0.3108`.

Датасет `HRA-EVAL-V3`, smoke set и манифест включены в репозиторий в каталоге [`data/`](data/). Все профили в них синтетические: HR Assistant никогда не работал в реальном боевом режиме. Первичные артефакты обучения (weights, raw metrics, evaluation JSON, operation logs) хранятся в закрытом рабочем контуре и не публикуются.
