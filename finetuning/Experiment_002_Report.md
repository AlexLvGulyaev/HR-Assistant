# Experiment 002 Report: Parameter Optimisation and Runtime Negative Failure

**Кейс:** HR Assistant (hr-assistant)  
**Модуль:** Fine-tuning / Experimental ML-контур  
**Дата начала:** 2026-06-28  
**Дата завершения:** 2026-06-28  
**Статус:** Завершён — offline-метрики улучшены; runtime negative smoke test не пройден

---

## 1. Контекст

### 1.1. Что предшествовало

Experiment 001 подтвердил, что технический пайплайн fine-tuning работает: LoRA обучается, чекпоинты сохраняются, JSON генерируется. Однако качество matching на original test set осталось на уровне base Qwen (`decision_accuracy = 0.444`).

### 1.2. Цель Experiment 002

Experiment 002 ставил цель **улучшить качество matching**, сохранив стабильность пайплайна. Для этого проверялась гипотеза: увеличение ёмкости адаптера и изменение гиперпараметров позволит модели лучше усвоить task-специфику HR matching.

Ключевые проверки:

1. Увеличение LoRA rank с 8 до 16 (проверка гипотезы о недостаточной ёмкости адаптера Exp 001).
2. Расширение target modules с attention-only (4) до attention + MLP (7) (проверка гипотезы о необходимости адаптации MLP-слоёв).
3. Увеличение числа эпох и корректировка learning rate.
4. Проверка поведения на runtime negative сценариях.

### 1.3. Почему этот эксперимент важен

Experiment 002 — это **параметрическая оптимизация и обнаружение runtime negative failure**. Он показал, что offline-метрики можно существенно улучшить (`decision_accuracy` 0.444 → 0.778), но при этом модель может давать ложные срабатывания на нерелевантных профилях в production-like условиях. Этот конфликт между offline-метриками и runtime-поведением стал мостом к Experiment 003.

---

## 2. Гипотеза

**H₀ (нулевая гипотеза):**  
Увеличение LoRA rank, расширение target modules и корректировка гиперпараметров не оказывают практически значимого влияния на качество matching в offline evaluation и не влияют на поведение модели в runtime negative сценариях.

**H₁ (альтернативная гипотеза):**  
Увеличение ёмкости адаптера и тонкая настройка гиперпараметров улучшают offline-метрики matching (`decision_accuracy`, `MAE_score`) при сохранении стабильной JSON-генерации.

**Критерий подтверждения:**
- `valid_json_rate` = 1.0;
- `decision_accuracy` > 0.444 на original test set;
- `MAE_score` < 29.78;
- positive smoke test пройден;
- результаты negative smoke test зафиксированы.

---

## 3. Изменения относительно предыдущего эксперимента

| Компонент | Experiment 001 | Experiment 002 |
|-----------|----------------|----------------|
| Teacher dataset | `HRA-EXP-V1`, 90 записей | `HRA-EXP-V2`, 90 записей (пересмотрен split) |
| Train / Validation / Test | 72 / 9 / 9 | 72 / 9 / 9 |
| LoRA rank | 8 | 16 |
| LoRA alpha | 32 | 32 |
| LoRA dropout | 0.1 | 0.05 |
| Target modules | 4 (`q_proj`, `k_proj`, `v_proj`, `o_proj`) | 7 (`q_proj`, `k_proj`, `v_proj`, `o_proj`, `gate_proj`, `up_proj`, `down_proj`) |
| Learning rate | 2e-4 | 2e-4 |
| Epochs (план) | 5 | 5 |
| Epochs (факт) | 5 | 3 (early stopping) |
| Best checkpoint | `checkpoint-72` (эпоха 4) | `checkpoint-54` (эпоха 3) |

Главное отличие Exp 002 от Exp 001 — увеличение ёмкости адаптера: rank 8 → 16 и расширение target modules с attention-only (4) до attention + MLP (7). Остальные гиперпараметры (alpha, learning rate, batch, grad_accum) сохранены для чистоты сравнения.

---

## 4. Неизменяемые параметры

| Группа | Параметр | Значение | Источник |
|--------|----------|----------|----------|
| Модель | Base model ID | `Qwen/Qwen2.5-1.5B-Instruct` | `configs/experiment_002.yaml` (не создан; параметры из артефактов запуска) |
| LoRA | `r` | `16` | `experiment_002/best_adapter/adapter_config.json` |
| LoRA | `lora_alpha` | `32` | `experiment_002/best_adapter/adapter_config.json` |
| LoRA | `lora_dropout` | `0.05` | `experiment_002/best_adapter/adapter_config.json` |
| LoRA | `target_modules` | `q_proj, k_proj, v_proj, o_proj, gate_proj, up_proj, down_proj` | `experiment_002/best_adapter/adapter_config.json` |
| Обучение | `per_device_train_batch_size` | `1` | `experiment_002/trainer_state.json` |
| Обучение | `gradient_accumulation_steps` | `4` | `experiment_002/trainer_state.json` |
| Обучение | `learning_rate` | `2e-4` | `experiment_002/trainer_state.json` |
| Обучение | Best checkpoint metric | `eval_loss` (minimize) | `experiment_002/best_adapter/trainer_state.json` |
| Runtime | API-контур | FastAPI + Transformers + PEFT ([`../api/hra_qwen_api_lora.py`](../api/hra_qwen_api_lora.py)) | [`TECHNICAL_FOUNDATION.md`](TECHNICAL_FOUNDATION.md) |
| Teacher | Judge | GPT-4.1, `temperature = 0` | [`TECHNICAL_FOUNDATION.md`](TECHNICAL_FOUNDATION.md) |

Подробное описание технической основы — в [`TECHNICAL_FOUNDATION.md`](TECHNICAL_FOUNDATION.md).

### 4.1. Experimental validity

Experiment 002 сравнивается с Experiment 001 по качеству matching на одном и том же техническом фундаменте.

| Аспект | Как контролируется |
|--------|-------------------|
| Сравнимость модели | Базовая модель `Qwen/Qwen2.5-1.5B-Instruct` неизменна. |
| Контролируемая переменная | Rank и target modules изменены относительно Exp 001; alpha, learning rate, batch, grad_accum неизменны. |
| Сравнимость обучения | Batch=1, grad_accum=4, lr=2e-4, `eval_loss` для выбора best checkpoint. |
| Сравнимость dataset | 90 записей, стратификация по группам. |
| Изменяемая переменная | Ёмкость адаптера (rank 8 → 16, target modules 4 → 7) и фокус на качестве matching; alpha, lr, batch, grad_accum неизменны. |

**Угрозы валидности и ограничения:**

- **Отсутствие отдельного config:** файл `configs/experiment_002.yaml` не создан; параметры восстановлены из артефактов запуска.
- **Ранняя остановка:** обучение остановлено на эпохе 3 вместо 5, что уменьшает разницу между Exp 001 и Exp 002.
- **Малая выборка:** 9 тестовых записей не позволяют надёжно оценить обобщение.
- **Нет формализованного runtime smoke set:** результаты negative smoke зафиксированы текстово, а не через `runtime_smoke_report.json`.

---

## 5. Датасет

### 5.1. Teacher dataset Experiment 002

| Параметр | Значение |
|----------|----------|
| Эксперимент | `HRA-EXP-V2` |
| Dataset | `HRA-EVAL-V2` |
| Всего записей | 90 (30 кандидатов × 3 вакансии) |
| Train | 72 записи (24 кандидата) |
| Validation | 9 записей (3 кандидата) |
| Test | 9 записей (3 кандидата) |

Dataset пересмотрен относительно V1: сохранена стратификация по группам, уточнён split. Три вакансии:
- Prompt Engineer / AI Automation Specialist;
- Системный аналитик;
- Специалист по разметке данных.

### 5.2. Баланс классов

| Split | Записей | match | no_match | % match |
|-------|---------|-------|----------|---------|
| train | 72 | ~14 | ~58 | ~20% |
| validation | 9 | ~2 | ~7 | ~20% |
| train+val | 81 | ~16 | ~65 | ~20% |
| test | 9 | ~3 | ~6 | ~33% |

> Точное распределение match/no_match в V2 не задокументировано отдельно; ориентировочно train+val match ≈ 20%.

### 5.3. Формат данных

Публичный обезличенный пример формата данных: [`data_sample/example.jsonl`](data_sample/example.jsonl).  
Полное описание схемы и истории версий — в [`reports/teacher_dataset_report.md`](reports/teacher_dataset_report.md).

---

## 6. Выполнение

### 6.1. Участники и роли

| Роль | Ответственность |
|------|-------------------|
| **Пользователь** | Инициатор, владелец решения, утверждение гипотезы и критериев успеха; запуск обучения, runtime smoke и контроль процесса на RunPod. |
| **ChatGPT** | Подготовка кода экспериментального пайплайна, launch contract и документации в диалоге с пользователем. |
| **RunPod** | Вычислительная среда для обучения, offline evaluation и runtime smoke; Claude Code на RunPod **не использовался**. |
| **GPT-4.1 (Teacher / Judge)** | Формирование reference labels для teacher dataset. |
| **LoRA-модель** | Обучаемый адаптер Qwen + LoRA. |
| **Telegram / n8n** | Runtime-контур для smoke validation. |

> **Примечание об авторстве и инструментарии.**
> В Experiment 002 код пайплайна разрабатывался в диалоге с ChatGPT. Непосредственный запуск команд, обучение модели, контроль процесса, runtime smoke и получение артефактов выполнял пользователь вручную на RunPod. RunPod использовался исключительно как GPU-стенд. Claude Code на RunPod не применялся.

### 6.2. Stage-by-stage исполнители

| Этап | Вход | Инструмент | Исполнитель | Выходной артефакт | Критерий завершения |
|------|------|------------|-------------|-------------------|---------------------|
| 1. Параметрический контракт | Результаты Exp 001 | Markdown-шаблон отчёта | Пользователь + ChatGPT | `Experiment_002_Report.md` (Stage 1) | Гипотеза и критерии утверждены |
| 2. Подготовка teacher dataset | Reference dataset V2 | `scripts/extract_teacher_dataset.py` | ChatGPT + Пользователь | `train.jsonl`, `validation.jsonl`, `test.jsonl` | Ожидаемое число записей, отсутствие leakage |
| 3. Launch contract | Dataset + параметры | `configs/experiment_002.yaml` (планировался) | ChatGPT + Пользователь | YAML-файл launch contract или параметры из артефактов | Все неизменяемые параметры зафиксированы |
| 4. Обучение и early stopping | Dataset + launch contract | [`scripts/train_lora.py`](scripts/train_lora.py) | Пользователь вручную на RunPod | Best adapter `checkpoint-54`, `trainer_state.json` | Best checkpoint выбран по eval_loss |
| 5. Offline evaluation | `data/test.jsonl`, best adapter | [`scripts/evaluate_generation_test.py`](scripts/evaluate_generation_test.py) | Пользователь вручную на RunPod | `generation_test_report.json` | valid_json_rate, decision_accuracy, MAE зафиксированы |
| 6. Runtime validation | Нерелевантные профили | [`scripts/runtime_smoke_test.py`](scripts/runtime_smoke_test.py) + [`../api/hra_qwen_api_lora.py`](../api/hra_qwen_api_lora.py) | Пользователь вручную на RunPod | Текстовые наблюдения smoke failures | Positive/negative/edge кейсы зафиксированы |
| 7. Документирование | Все метрики + анализ | Отчёт эксперимента | ChatGPT + Пользователь | `Experiment_002_Report.md` | Вердикт принят и задокументирован |

---

## 7. Результаты обучения

| Метрика | Значение |
|---------|----------|
| Experiment ID | `experiment_002` |
| Лучший чекпоинт | `checkpoint-54` (эпоха 3) |
| Best `eval_loss` | **0.4443** |
| Train epochs (факт) | 3 (early stopping) |
| Peak VRAM | ~8 GB |
| GPU | NVIDIA RTX A5000 (RunPod) |

### 7.1. Динамика обучения

| Эпоха | Global step | Eval loss | Eval token accuracy |
|-------|-------------|-----------|---------------------|
| 1 | 18 | 0.5500 | 0.8562 |
| 2 | 36 | 0.4445 | 0.8760 |
| 3 | 54 | **0.4443** | 0.8798 |
| 4 | 72 | 0.4512 | 0.8823 |
| 5 | 90 | 0.4572 | 0.8876 |

Eval loss достиг плато на эпохах 2–3 и начал расти на эпохах 4–5. Early stopping сработала на `checkpoint-54`.

---

## 8. Offline evaluation

### 8.1. Generation test (original test set, 9 записей)

| Модель | valid_json_rate | decision_accuracy | MAE_score |
|--------|-----------------|-------------------|-----------|
| Base Qwen | 1.000 | 0.444 | 38.78 |
| LoRA Experiment 001 | 1.000 | 0.444 | 29.78 |
| **LoRA Experiment 002** | **1.000** | **0.778** | **21.89** |

### 8.2. Интерпретация offline-метрик

- `decision_accuracy` вырос с 0.444 (Exp 001 / base Qwen) до **0.778** — существенное улучшение matching.
- `MAE_score` снизился с 29.78 (Exp 001) до **21.89** — модель стала ближе к числовым оценкам teacher.
- `valid_json_rate` остался 1.0 — JSON-генерация стабильна.

Эти результаты показали, что параметрическая оптимизация и ранняя остановка работают для offline-качества.

### 8.3. Per-example breakdown (key errors)

| # | Case type | Вакансия | Reference | LoRA Exp 002 | Decision match |
|---|-----------|----------|-----------|--------------|----------------|
| 6 | obvious_no_match | Специалист по разметке данных | no_match (27) | match (72) | ❌ False positive |
| 9 | borderline | Специалист по разметке данных | match (64) | no_match (40) | ❌ False negative |

Центральный false positive — кейс 6: кандидат-врач с 15-летним медицинским опытом получил `match` на вакансию «Специалист по разметке данных». Модель использовала нерелевантные сигналы (опыт, зарплата в бюджете) и проигнорировала отсутствие профильной базы. Этот кейс позже стал частью мотивации Experiment 003.

---

## 9. Runtime validation

### 9.1. Positive smoke test

| Тест | Результат |
|------|-----------|
| Корректные matching-запросы | ✅ Pass |
| JSON-структура | ✅ Pass |
| Reasoning | ✅ Pass |
| Decision | ✅ Pass |

### 9.2. Negative smoke test

| Тест | Результат |
|------|-----------|
| Пустые поля | ❌ Fail |
| Невалидные данные | ❌ Fail |
| Edge cases | ❌ Fail |

### 9.3. Интерпретация runtime-результатов

Positive сценарии прошли, но negative сценарии провалились. Модель не умеет корректно отклонять нерелевантные и edge-case профили. Это ключевое открытие Experiment 002:

> **Offline-метрики не покрывают production-like поведение.** `decision_accuracy = 0.778` на 9 записях test set не гарантирует, что модель не будет давать false positives на реальных нерелевантных анкетах.

---

## 10. Дополнительная валидация: почему negative smoke провален

### 10.1. Проблема false positives

Главная ошибка Experiment 002 — false positive на нерелевантном профиле. Модель придавала вес общим сигналам:

- наличие опыта (любого);
- зарплата в диапазоне бюджета;
- soft skills («внимательность»);

и недостаточно штрафовала за отсутствие профильных hard skills.

### 10.2. Failure modes

| # | case_code | Вакансия | Проблема | Почему это важно |
|---|-----------|----------|----------|------------------|
| 1 | `HRA-EVAL-V2-000020` | Специалист по разметке данных | False positive: врач получил `match` (score 72) | Модель использовала нерелевантные soft skills как обоснование высокого score |
| 2 | `HRA-EVAL-V2-000020` | Prompt Engineer | Завышенный score (57 при reference 19) | Модель придавала вес общим словам без проверки профильной базы |
| 3 | `HRA-EVAL-V2-000020` | Системный аналитик | conditions_score максимален при salary mismatch | Модель игнорировала условия при сильном профиле |

Эти failure modes позже стали категориями HN-1, HN-3, HN-8, EC-4 в Experiment 003.

### 10.3. Почему high offline accuracy не гарантирует runtime-качество

- **Test set мал и не содержит production-like hard negatives:** 9 записей покрывают obvious_match / borderline / obvious_no_match, но не сложные нерелевантные профили.
- **Модель обучена на positive/borderline доминировании:** train+val содержит ~20% match, но hard-negative паттерны не формализованы.
- **Offline-метрики усредняют ошибки:** один false positive на 9 записях даёт `decision_accuracy = 0.778`, но в runtime такой false positive критичен.

Эти ограничения стали инженерным основанием для Experiment 003.

---

## 11. Интерпретация

### 11.1. Что показал эксперимент

1. **Параметрическая оптимизация улучшает offline-метрики.** `decision_accuracy` 0.444 → 0.778, `MAE_score` 29.78 → 21.89.
2. **Offline ≠ runtime.** Высокая decision accuracy на test set не гарантирует прохождение negative smoke test.
3. **Hard negatives необходимы.** Модель не умеет отклонять сложные нерелевантные профили без явных negative примеров.
4. **Нужна типология ошибок.** Для систематического исправления нужно классифицировать failure modes, а не ловить их по одному.

### 11.2. Главный урок

> Параметрическая оптимизация достигает предела на существующем dataset. Следующий прирост качества возможен только через dataset engineering — добавление hard negatives и edge cases.

Этот урок стал основанием для Experiment 003.

---

## 12. Вердикт

> **Гипотеза частично подтверждена.**

| Критерий | Результат |
|----------|-----------|
| JSON-генерация остаётся стабильной | ✅ Подтверждено — valid_json_rate = 1.0 |
| Offline-метрики улучшены | ✅ Подтверждено — decision_accuracy 0.444 → 0.778 |
| Positive smoke test пройден | ✅ Подтверждено |
| Negative smoke test пройден | ❌ Нет — false positives на нерелевантных профилях |
| Модель production-ready | ❌ Нет |

**Практический смысл:** Experiment 002 показал, что offline-метрики можно улучшить параметрической оптимизацией, но это не решает проблему runtime negative quality. Необходим следующий цикл, направленный на состав teacher dataset.

---

## 13. Следующий эксперимент

Выводы Experiment 002 непосредственно ведут к **Experiment 003**. Цель следующего цикла — устранить runtime negative failure, сохранив достижения по offline-метрикам.

### 13.1. Что исправить

1. **Добавить hard-negative примеры** в teacher dataset: нерелевантные профессии, смежные роли без обязательных навыков, word overlap без competency overlap, сильные профили в нерелевантной специализации.
2. **Добавить edge-case примеры** для калибровки порога decision.
3. **Сохранить positive/borderline примеры**, чтобы избежать over-correction.

### 13.2. Что оставить неизменным

- Базовая модель `Qwen/Qwen2.5-1.5B-Instruct`;
- LoRA параметры (`r=16`, `alpha=32`, `target_modules`);
- Параметры обучения (batch=1, grad_accum=4, lr=2e-4);
- Runtime-контур;
- Teacher Judge GPT-4.1, `temperature = 0`.

### 13.3. Критерии следующего цикла

- `valid_json_rate` = 1.0;
- runtime negative smoke test пройден (0 unexpected matches);
- `decision_accuracy` не ухудшается критически;
- hard-negative категории формализованы.

Эти критерии были реализованы в Experiment 003.

---

## 14. Источники и артефакты

### 14.1. Публичные конфигурации и скрипты

- `configs/experiment_002.yaml` — планировался, но не создан; параметры восстановлены из артефактов запуска;
- [`scripts/train_lora.py`](scripts/train_lora.py) — обучение;
- [`scripts/evaluate_generation_test.py`](scripts/evaluate_generation_test.py) — generation test;
- [`scripts/runtime_smoke_test.py`](scripts/runtime_smoke_test.py) — runtime smoke;
- [`../api/hra_qwen_api_lora.py`](../api/hra_qwen_api_lora.py) — runtime API.

### 14.2. Отчёты и данные

- [`TECHNICAL_FOUNDATION.md`](TECHNICAL_FOUNDATION.md) — техническая основа;
- [`Experiment_001_Report.md`](Experiment_001_Report.md) — предыдущий эксперимент;
- [`Experiment_003_Report.md`](Experiment_003_Report.md) — следующий эксперимент, реализующий hard negatives;
- [`Experiment_004_Report.md`](Experiment_004_Report.md) — эксперимент, устраняющий over-correction;
- [`reports/teacher_dataset_report.md`](reports/teacher_dataset_report.md) — анализ teacher dataset;
- [`data_sample/example.jsonl`](data_sample/example.jsonl) — обезличенный пример формата данных.

### 14.3. Идентификаторы запуска

- Experiment ID: `experiment_002`;
- Dataset code: `HRA-EVAL-V2`;
- Experiment code: `HRA-EXP-V2`;
- Best checkpoint: `checkpoint-54` (эпоха 3), выбран по `eval_loss = 0.4443`.

Датасет `HRA-EVAL-V2` включён в репозиторий в каталоге [`data/`](data/). Все профили в нём синтетические: HR Assistant никогда не работал в реальном боевом режиме. Первичные артефакты обучения (weights, raw metrics, evaluation JSON, operation logs) хранятся в закрытом рабочем контуре и не публикуются.
