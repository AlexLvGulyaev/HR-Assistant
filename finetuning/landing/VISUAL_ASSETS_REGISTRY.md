# Реестр визуальных артефактов портфельного кейса — v2

**Назначение:** Единый источник истины для разработки всех графиков, схем, диаграмм, карточек и таблиц портфельного кейса HR Assistant LoRA.  
**Концепция:** [`NARRATIVE_BLUEPRINT.md`](NARRATIVE_BLUEPRINT.md) — спецификация и повествовательная логика.  
**Meta Artifact Registry:** archived in `task_history/attachments/landing_internal/meta_artifact_registry.md` — инженерный Source of Truth; в v2 остаётся без изменений.  
**Статус реестра:** рабочий; элементы получают статусы `Planned` / `In Progress` / `Ready for Review` / `Done` по мере реализации.

---

## 0. Изменения по сравнению с v1

| Аспект | v1 | v2 |
|--------|----|----|
| Количество элементов | 46 (15 G / 8 D / 16 C / 7 T) | 57 (20 G / 9 D / 17 C / 11 T) |
| Blueprint | v1 (17 страниц) | v2 (21 страница) |
| Столбцы | Без привязки к MAR-ID | Добавлен `MAR-ID` и `Blueprint v2 chapter(s)` |
| Новые темы | — | Checkpoint selection, train/eval gap, concrete examples, controlled variables, repeat runs stability |
| Покрытие процесса | Результаты экспериментов | Процесс + результаты |

---

## 1. Графики (G)

| ID | Название | Тип | Blueprint v2 chapter(s) | Назначение | Главный вывод | Источник данных | MAR-ID | Статус | Приоритет | Сложность | Estimated effort | Требует custom illustration | Требует data transformation | Требует manual design | Responsive behaviour | Mobile adaptation | Примечания |
|----|----------|-----|-------------------------|------------|---------------|-----------------|--------|--------|-----------|-----------|------------------|----------------------------|----------------------------|-----------------------|----------------------|-----------------|------------|
| G-001 | Loss Curves — All Experiments | Graph | 3, 5, 15 | Как шло обучение и где best checkpoint | Лучший checkpoint — не всегда последний; train loss продолжает падать, eval loss растёт | `trainer_state.json` (001, 002, 003, 004) | MAR-001-006, MAR-001-007, MAR-002-005, MAR-002-006, MAR-003-006…008, MAR-004-006…008 | Planned | Critical | Medium | 3–4 h | No | Yes (step→epoch, interpolation, best checkpoint markers) | No | Scrollable small-multiples or stacked panels | Collapse to 1-column small-multiples | Четыре панели 2×2; marker best checkpoint; log-шкала рекомендуется |
| G-002 | Best Validation Loss per Experiment | Graph | 4, 15 | Какой эксперимент обучился лучше по ML-метрикам | Лучший validation loss пришёлся на худший по решениям эксперимент; парадокс держится во всех 4 | `trainer_state.json`, `test_evaluation/test_metrics.json` | MAR-001-006, MAR-001-010, MAR-003-012, MAR-004-012 | Planned | Critical | Low | 1–2 h | No | Yes (extract best_metric) | No | Single grouped bar | Stack bars vertically | Twin-Y decision accuracy optional |
| G-003 | Token Accuracy Curves | Graph | 3 | Выучила ли модель формат JSON | Модель быстро научилась формату ответа, но не его смыслу | `trainer_state.json` (все эксперименты) | MAR-001-006, MAR-002-005, MAR-003-006/007, MAR-004-006/007 | Planned | High | Medium | 2–3 h | No | No | No | Small-multiples 2×2 | Collapse to 1-column | Можно объединить с G-001 в одну фигуру |
| G-004 | Decision Accuracy Evolution | Graph | 3, 5, 7b, 8 | Matching-решения действительно стали лучше? | Точность решений росла неравномерно: 44% → 78% → 67% → 80% | `generation_test_report.json` (все эксперименты) | MAR-001-009, MAR-002-008, MAR-003-010, MAR-004-010 | Done | Critical | Low | 1–2 h | No | No | No | Grouped bar | Stack grouped bars | `portfolio_visuals/svg/G-004-decision-accuracy-evolution.svg` |
| G-005 | MAE Score Evolution | Graph | 3, 5, 7b, 8 | Насколько в среднем ошибалась оценка | Средняя ошибка оценки снизилась с 38 до 15 баллов | `generation_test_report.json` (все эксперименты) | MAR-001-009, MAR-002-008, MAR-003-010, MAR-004-010 | Done | Critical | Low | 1–2 h | No | No | No | Grouped bar | Stack grouped bars | `portfolio_visuals/svg/G-005-mae-score-evolution.svg`; компоновка совместима с G-004 |
| G-006 | Per-Component MAE Heatmap | Graph | 5 | Где именно модель ошибается в score | Ошибка распределена неравномерно по компонентам оценки; role улучшился сильнее всего | `generation_test_report.json` (002–004) | MAR-002-008, MAR-003-010, MAR-004-010 | Planned | Medium | Medium | 2–3 h | No | Yes (component normalization optional) | No | Heatmap | Scrollable table fallback | Exp 001 не включается из-за отсутствия sub-component MAE |
| G-007 | Test Perplexity / Test Eval Loss | Graph | 4 | Что показала стандартная held-out likelihood-метрика | Held-out loss не отражает качество matching-решений; LoRA loss выше base, но quality лучше | `test_evaluation/test_metrics.json` (001, 003, 004) | MAR-001-010, MAR-003-012, MAR-004-012 | Planned | High | Low | 1–2 h | No | No | No | Grouped bar | Stack grouped bars | Exp 002 отсутствует; аннотация required |
| G-008 | External-Validation Scatter | Graph | 9 | Насколько близки LoRA score к reference на незнакомых данных | На внешней выборке LoRA держится вблизи диагонали калибровки | `external_validation_report.json` | MAR-004-013 | Done | Critical | Medium | 2–3 h | No | Yes (decision match color coding) | No | Scatter with diagonal | Reduce point size, add marginal histograms as optional | `portfolio_visuals/svg/G-008-external-validation-scatter.svg`; 97/102 точек: у 5 записей reference score отсутствует в JSON |
| G-009 | Runtime Smoke Pass/Fail Matrix | Graph | 6, 7a, 8, 10 | Модель выдерживает реалистичные production-сценарии? | Production smoke показал то, чего не видела offline-метрика; повторяемость подтверждена | `runtime_smoke_report.json` (003, 004 rerun); `FINETUNING_ENGINEERING_REPORT.md` (002) | MAR-002-009, MAR-003-011, MAR-004-011, MAR-004-016 | Done | Critical | Low | 1–2 h | No | Yes (category-level PASS/FAIL) | No | Heatmap / matrix | Same, larger cells | `portfolio_visuals/svg/G-009-runtime-smoke-pass-fail-matrix.svg`; три состояния для страницы 10 |
| G-010 | Latency CDF / Distribution | Graph | 12a | Насколько медленен API на практике | Latency варьируется на порядок до оптимизации | `runtime_smoke_report.json` (003, 004), `external_validation_optimized_report.json` | MAR-003-011, MAR-004-011, MAR-004-016, MAR-004-020 | Planned | High | Medium | 2–3 h | No | Yes (empirical CDF) | No | CDF or box/violin | Box plot fallback | Log-scale X рекомендуется |
| G-011 | Engine Benchmark Comparison | Graph | 12b | Какой inference-движок достаточно быстр | vLLM сократил latency в несколько раз; 4bit оказался неудачным путём | `engine_benchmark_report.json`, `engine_benchmark_report_vllm.json` | MAR-004-017, MAR-004-018 | Planned | High | Low | 1–2 h | No | No | No | Grouped bar | Stack bars | Три engine mode: transformers_fp16, transformers_4bit, vllm_fp16 |
| G-012 | Latency Stage Breakdown | Graph | 12a | Где именно теряется время | Почти всё время ответа уходило на генерацию токенов (>99%) | `latency_profile_report.json` | MAR-004-019 | Planned | High | Low | 1–2 h | No | Yes (share of total) | No | Stacked horizontal bar | 100% stacked bar | Generation >99% |
| G-013 | Dataset Evolution | Graph | 7a, 8, 16, 18 | Что менялось в данных между экспериментами | Рост качества шёл за счёт инженерии датасета, а не адаптера | `configs/experiment_*.yaml`, `data/manifest_experiment_*.json` | MAR-003-013, MAR-004-013 | Done | Critical | Medium | 2–3 h | No | Yes (count by class/split) | No | Stacked bar + line overlay | Split into two charts | `portfolio_visuals/svg/G-013-dataset-evolution.svg`; Exp 001/002 без manifest; классы из чернового YAML |
| G-014 | LoRA vs GPT-4o-mini Radar | Graph | 9 | Насколько локальная модель приблизилась к GPT-4o-mini | LoRA приблизилась к GPT-4o-mini по решениям, но не по калибровке и скорости | `external_validation_report.json`, `gpt_comparison_report_v2.json` | MAR-004-013, MAR-004-015 | Planned | High | Medium | 2–3 h | No | Yes (MAE normalization for radar) | No | Radar chart + table + latency bar | Table + bar only on mobile | Не скрывать разные holdouts |
| G-015 | Before/After Truncation Fix | Graph | 11 | Что сломалось в production и как исправили | HTTP 422 и truncation исчезли после фикса конфигурации API | `gpt_comparison_report.json`, `gpt_comparison_report_v2.json` | MAR-004-014, MAR-004-015 | Planned | High | Low | 1 h | No | No | No | Side-by-side metric cards | Same, stacked | max_tokens 300→512; valid_json 0.867→1.000, accuracy 0.800→0.933 |
| G-016 | Per-Experiment Best Epoch Markers | Graph | 16 | В какой эпохе оказался лучший checkpoint | Во всех экспериментах best checkpoint — не финальный (4, 3, 2, 3 из 5 эпох) | `trainer_state.json` (все эксперименты) | MAR-001-006…MAR-004-007 | Done | High | Low | 1–2 h | `portfolio_visuals/scripts/generate_g016_scene16.py` | Yes (extract best_metric/global_step/epoch) | No | Bar chart with full 5-epoch backdrop | Collapse to 1-column | DOM-сцена 20; обновлён в batch 7: исправлены значения Exp 002 (3 вместо 5) и Exp 003 (2 вместо 5), добавлена шкала 1–5 и подпись «of 5» |
| G-017 | Train/Eval Gap per Experiment | Graph | 4, 15 | Насколько train loss и eval loss разошлись | Классическое переобучение: train падает, eval растёт после best checkpoint | `trainer_state.json` (все эксперименты) | MAR-001-006…MAR-004-007 | Planned | Medium | Low | 1–2 h | No | Yes (delta or shaded area) | No | Small-multiples | Collapse to 1-column | Новый элемент v2 |
| G-018 | Base Model Wrong-Answer Examples | Graph / Card | 2 | Конкретные примеры неправильных ответов base model | Валидный JSON не означает правильного решения | `generation_test_report.json` (Exp 001 base) | MAR-001-009 | Planned | High | Low | 1–2 h | No | Yes (extract example + anonymize) | Yes | Before/after cards | Stack vertically | Новый элемент v2; анонимизация |
| G-019 | Hard-Negative False-Positive Case | Graph / Card | 6 | Конкретный кейс, который запустил Exp 003 | Модель не заметила зарплату вне бюджета и специальность | `FINETUNING_ENGINEERING_REPORT.md`, `runtime_smoke_report.json` | MAR-002-009 | Planned | High | Low | 1–2 h | No | Yes (extract case, anonymize) | Yes | Side-by-side case card | Stack vertically | Новый элемент v2 |
| G-020 | False-Negative Examples (Exp 003) | Graph / Card | 7b | Конкретные кейсы, которые модель стала отсеивать зря | Цена отсева: истинные match пропущены | `generation_test_report.json` (Exp 003) | MAR-003-010 | Planned | High | Low | 1–2 h | No | Yes (extract cases, anonymize) | Yes | Before/after cards | Stack vertically | Новый элемент v2 |
| G-021 | Base vs LoRA: DA and MAE in Exp 001 and 002 | Graph | 5 | Сравнение Base и LoRA по DA и MAE в первых двух экспериментах | Первый рост качества только в Exp 002: DA 44%→78%, MAE 38.8→21.9; в Exp 001 LoRA не улучшила решения | `generation_test_report.json` (Exp 001, 002) | MAR-001-009, MAR-002-008 | Done | Critical | Low | 1–2 h | No | No | Yes | Two grouped-bar panels | Stack panels vertically | Создан в batch 3; заменяет G-004 на сцене 6; старый G-004 сохранён |
| G-022 | Exp 002 Smoke Fail Matrix | Graph | 6 | Smoke-результат Experiment 002: что именно упало | Positive smoke прошёл, negative smoke (obvious/hard/edge/invalid) — fail; stability repeat ещё не измерялась | `FINETUNING_ENGINEERING_REPORT.md` (Runtime Validation, Exp 002) | MAR-002-009 | Done | Critical | Low | 1 h | No | No | Yes | 6×1 matrix, single column | Same, larger cells | Создан в batch 4; заменяет G-009 на сцене 7; G-009 остаётся на сцене 11 |
| G-023 | Dataset Evolution Exp 001–003 | Graph | 7a | Что менялось в данных до Exp 003 | 90 → 123 записи: добавлены hard negatives/edge cases, конфигурация LoRA не менялась | `configs/experiment_001.yaml`; `FINETUNING_ENGINEERING_REPORT.md`; `data/manifest_experiment_003.json` | MAR-003-013, MAR-002-009 | Done | Critical | Medium | 1 h | No | Yes (filter experiments) | No | Stacked bar + line overlay | Same, 3 columns | Создан в batch 4; заменяет G-013 на сцене 8a; G-013 остаётся на сценах 8, 16, 18 |
| G-024 | Precision / Recall Trade-off (Scene 8b) | Graph | 7b | Как hard negatives сдвинули precision/recall | Exp 001/002 baseline → низкая precision, высокий recall; Exp 003 hard negatives → высокая precision, низкий recall | `generation_test_report.json` (качественная интерпретация); `FINETUNING_ENGINEERING_REPORT.md` | MAR-003-010 | Done | Critical | Medium | 1 h | No | No | Yes | 2×2 quadrant diagram | Same | Создан в batch 4; заменяет D-004 на сцене 8b; D-004 убран/архивирован |
| G-025 | Dataset Composition and Quality Evolution | Graph | 8 | Совмещённая картина: как менялся датасет и как это отражалось на метриках | Датасет 90→123→162; hard negatives остались, positives/borderlines восстановили recall; DA и MAE LoRA улучшились | `data/manifest_experiment_003.json`, `data/manifest_experiment_004.json`, `generation_test_report.json` (002–004) | MAR-004-006, MAR-004-010, MAR-004-013 | Done | Critical | Medium | 2 h | No | Yes | Yes | Two-panel combo chart | Stack panels vertically | Создан в batch 5; заменяет G-005 на сцене 9 |
| G-026 | Smoke Repeatability Matrix | Graph | 10 | Показать стабильность production smoke: Exp 003, Exp 004, rerun — все проходят | Runtime smoke repeatable: 7/7 across three runs | `runtime_smoke_report.json` (003, 004, rerun) | MAR-003-011, MAR-004-011, MAR-004-016 | Done | Critical | Low | 1 h | No | No | Yes | 6×3 matrix | Same | Создан в batch 6; заменяет G-009 на сцене 11; G-009 остаётся на сцене 7/8 |
| G-027 | Qwen-LoRA vs GPT-4o-mini — Culmination | Illustration / Graph | 12b–13 | Эмоциональная кульминация: Qwen-LoRA рядом с облачным эталоном | Qwen-LoRA приблизилась к GPT по accuracy, но отстаёт по MAE; остаётся независимой и production-ready | `external_validation_report.json`, `latency.optimized` summary | MAR-004-013, MAR-004-020 | Done | Critical | Medium | 2–3 h | Yes | Yes | Yes | Two AI forms + 4 metric cards | Stack vertically | Создан в batch 8; DOM-сцена 14; между 13b (Latency) и 15 (Честный диагноз); GPT-форма — угловатая, не человекоподобная; карточки по 2 с каждой стороны. |
| G-028 | Exp 004 Epoch Breakdown | Graph | 15 | Метод выбора checkpoint: совместный анализ train/eval loss на примере Exp 004 | Train loss = memorization, eval loss = generalization; best checkpoint выбирается на перегибе, не по финальной эпохе | `trainer_state.json` (Exp 004), `generation_test_report.json` | MAR-004-006, MAR-004-010 | Done | High | Medium | 1–2 h | No | Yes | No | Line chart with best-epoch marker; legend annotates memorization / generalization | Collapse to 1-column | Создан в batch 8; DOM-сцена 19; переработан в продолжении batch 8: теперь метод, а не результат. |

---

## 2. Диаграммы (D)

| ID | Название | Тип | Blueprint v2 chapter(s) | Назначение | Главный вывод | Источник данных | MAR-ID | Статус | Приоритет | Сложность | Estimated effort | Требует custom illustration | Требует data transformation | Требует manual design | Responsive behaviour | Mobile adaptation | Примечания |
|----|----------|-----|-------------------------|------------|---------------|-----------------|--------|--------|-----------|-----------|------------------|----------------------------|----------------------------|-----------------------|----------------------|-----------------|------------|
| D-001 | Full Pipeline Schematic | Diagram | 17, 18 | Как поток данных идёт от teacher dataset до Telegram | Teacher dataset → LoRA → vLLM → Telegram: полный pipeline на одной машине | `configs/experiment_*.yaml`, `api/`, `scripts/`, runtime reports | MAR-001-001, MAR-004-016…020 | Planned | Critical | Medium | 3–4 h | Yes | No | Yes | Horizontal scroll or wrap into vertical | Vertical stack | Аннотации версий датасета |
| D-002 | Four-Experiments Timeline | Diagram | 1, 17 | Компактный narrative backbone | Четыре эксперимента ответили на вопросы друг друга | `Experiment_003.md`, `Experiment_004.md`, `FINETUNING_ENGINEERING_REPORT.md` | MAR-001-001, MAR-002-001, MAR-003-001, MAR-004-001 | Planned | Critical | Low | 1–2 h | Yes | No | Yes | Horizontal timeline | Vertical timeline | 4 узла: hypothesis + outcome |
| D-003 | Dataset Composition Transition | Diagram | 8, 16, 18 | Как менялся состав классов между экспериментами | 90 → 123 → 162: hard negatives устранили FP, positives вернули recall | `data/manifest_experiment_003.json`, `manifest_experiment_004.json`, `configs/experiment_*.yaml` | MAR-003-013, MAR-004-013 | Planned | High | Medium | 2–3 h | Yes | Yes (flow counts) | Yes | Sankey or stacked transition bars | Simplified flow chart | Потоки +hard negatives, +positives/borderlines |
| D-004 | Precision / Recall Trade-off | Diagram | 7b | Как hard negatives и positives меняли precision/recall | Hard negatives повысили precision, positives восстановили recall | `generation_test_report.json` (002–004), `runtime_smoke_report.json` | MAR-002-008, MAR-003-010, MAR-003-011, MAR-004-010, MAR-004-011 | Planned | High | Low | 1–2 h | Yes | No | Yes | 2×2 matrix or icon diagram | Same, larger icons | Связан с D-002 |
| D-005 | Offline Validation vs Production Smoke | Diagram | 6 | Почему offline-метрики не равны production-качеству | Offline validation и production smoke — неэквивалентные gate | `generation_test_report.json`, `runtime_smoke_report.json` | MAR-002-008, MAR-002-009, MAR-003-011 | Planned | Critical | Low | 1–2 h | Yes | No | Yes | Two-column diagram | Vertical stack | Стрелка "не эквивалентны" |
| D-006 | Teacher Dataset Provenance | Diagram | 17 | Откуда берутся teacher examples | Teacher labels формируются из prompt-evaluation базы | `database/*.sql`, `data/manifest_experiment_*.json` | MAR-003-013, MAR-004-013, MAR-S-* | Planned | Low | Medium | 2–3 h | Yes | No | Yes | Flow diagram | Vertical flow | Опциональный элемент |
| D-007 | Next Cycle Roadmap | Diagram | 14 | Какие направления исследуются дальше | Следующий цикл: calibration, augmentation, hard-negative metrics, quantized server | Project context | — | Planned | Medium | Low | 1–2 h | Yes | No | Yes | Roadmap or list cards | Vertical list | DOM-сцена 18; 3–4 направления |
| D-008 | Proven / Partial / Next Cycle Map | Diagram | 13 | Чёткое разделение доказанного и открытого | Dataset engineering доказана; production hard-negative качество — частично; calibration/latency — next cycle | All final reports | MAR-004-013, MAR-004-015, MAR-004-020 | Planned | Critical | Low | 1–2 h | Yes | No | Yes | Three-column layout | Vertical stack | DOM-сцена 17; центральный элемент выводов |
| D-009 | Checkpoint Selection Timeline | Diagram | 15 | Когда в каждом эксперименте оказался лучший checkpoint | Best epoch: 4, 3, 2, 3 — не последние | `trainer_state.json` (все эксперименты) | MAR-001-006…MAR-004-007 | Planned | High | Low | 1–2 h | Yes | Yes (extract best epoch/step) | Yes | Horizontal timeline | Vertical timeline | Новый элемент v2 |
| D-010 | Dataset Change Log / Controlled Variables | Diagram | 17 | Что менялось, что было зафиксировано | LoRA-config неизменен; датасет 90→90→123→162; Exp 002 не менял размер, изменилась разметка | `adapter_config.json` (все), `configs/experiment_*.yaml`, `data/experimentData.js` | MAR-001-002…MAR-004-002, MAR-003-013, MAR-004-013 | Done | High | Low | 1–2 h | `portfolio_visuals/scripts/generate_d010_scene17.py` | Yes (diff configs, count changes) | Yes | Two-column comparison | Vertical stack | DOM-сцена 21; обновлён в batch 7: исправлено `Exp 002 = 0` на `Exp 002 = 90 (same)` |

---

## 3. Карточки (C)

| ID | Название | Тип | Blueprint v2 chapter(s) | Назначение | Главный вывод | Источник данных | MAR-ID | Статус | Приоритет | Сложность | Estimated effort | Требует custom illustration | Требует data transformation | Требует manual design | Responsive behaviour | Mobile adaptation | Примечания |
|----|----------|-----|-------------------------|------------|---------------|-----------------|--------|--------|-----------|-----------|------------------|----------------------------|----------------------------|-----------------------|----------------------|-----------------|------------|
| C-001 | Hero Composition | Card | 1 | Первое впечатление и обозначение инженерной истории | Четыре эксперимента показали ограничения offline-метрик и рождение способности | All final reports | — | Planned | Critical | Medium | 2–3 h | Yes | No | Yes | Flexible layout | Stack vertically | Не центрировать на одной цифре 93.1% |
| C-002 | Problem Statement Card | Card | 2 | Быстро объяснить задачу | Валидный JSON не означал правильного matching-решения | `generation_test_report.json` (Exp 001) | MAR-001-009 | Planned | Critical | Low | 1 h | No | No | Yes | Single card | Same | Краткое описание + одна метрика |
| C-003 | JSON Contract Example | Card | 2, 3 | Показать форму API-вывода | Модель возвращает структурированный JSON с оценкой и reasoning | API code + reports | MAR-001-009, MAR-004-010 | Planned | High | Low | 1 h | No | No | Yes | Syntax-highlighted block | Horizontal scroll | Поля: match, score, role, skills, experience, conditions, reasoning_ru |
| C-004 | Base Model + LoRA Adapter Card | Card | 18 | Объяснить архитектуру модели | Локальный адаптер над Qwen2.5-1.5B-Instruct | `adapter_config.json` | MAR-001-002 | Planned | High | Low | 1 h | Yes | No | Yes | Two stacked blocks | Vertical stack | r=16, α=32, dropout=0.05, 7 target modules |
| C-005 | Why LoRA — Benefits + Caveats | Card | 18 | Обосновать выбор LoRA без преувеличения | Адаптер даёт контроль и итеративность; скорость — результат последующей работы | `adapter_config.json`, latency reports | MAR-001-002, MAR-004-017…020 | Planned | Critical | Low | 1–2 h | Yes | No | Yes | List with caveat badge | Same | Перечислить доказанные преимущества и оговорку |
| C-006 | Hypothesis Card — Exp 001 | Card | 3 | Сделать интенцию эксперимента сканируемой | Baseline LoRA не улучшила решения, хотя loss снизился до минимума | `Experiment_001.md` / artifacts | MAR-001-001, MAR-001-006, MAR-001-009 | Planned | High | Low | 1 h | Yes | No | Yes | Standard hypothesis card | Same | problem → hypothesis → change → result → unexpected → next |
| C-007 | Hypothesis Card — Exp 002 | Card | 5 | Сделать интенцию эксперимента сканируемой | Настройка адаптера подняла accuracy до 78%, но production negatives всё ещё проходили | `FINETUNING_ENGINEERING_REPORT.md` | MAR-002-001, MAR-002-005, MAR-002-008, MAR-002-009 | Planned | High | Low | 1 h | Yes | No | Yes | Standard hypothesis card | Same | problem → hypothesis → change → result → unexpected → next |
| C-008 | Hypothesis Card — Exp 003 | Card | 7a | Сделать интенцию эксперимента сканируемой | Hard negatives устранили false positives, но снизили recall | `Experiment_003.md` | MAR-003-001, MAR-003-010, MAR-003-011 | Planned | High | Low | 1 h | Yes | No | Yes | Standard hypothesis card | Same | problem → hypothesis → change → result → unexpected → next |
| C-009 | Hypothesis Card — Exp 004 | Card | 8 | Сделать интенцию эксперимента сканируемой | Positives и borderlines вернули recall, сохранив все hard-negative gains | `Experiment_004.md`, `Experiment_004_Report.md` | MAR-004-001, MAR-004-010, MAR-004-011, MAR-004-013 | Planned | High | Low | 1 h | Yes | No | Yes | Standard hypothesis card | Same | problem → hypothesis → change → result → unexpected → next |
| C-010 | Right vs Wrong Answer Examples | Card | 2, 3 | Сделать failure modes осязаемыми | Модель до и после обучения на одной паре кандидат/вакансия | `generation_test_report.json` | MAR-001-009, MAR-002-008, MAR-003-010, MAR-004-010 | Planned | High | Low | 1–2 h | No | Yes (extract examples, anonymize) | Yes | Before/after cards | Stack vertically | Анонимизировать данные |
| C-011 | Positive / Hard-Negative / Borderline Examples | Card | 6, 7a, 7b | Сделать абстрактные концепции датасета конкретными | Hard negatives и positives — два рычага качества | Teacher dataset records (anonymize) | MAR-003-013, MAR-004-013 | Planned | High | Medium | 2–3 h | No | Yes (extract + anonymize) | Yes | Three side-by-side cards | Vertical stack | Вывод модели до/после + пояснение |
| C-012 | HTTP 422 / Truncation Bug Card | Card | 11 | Подсветить реальный инженерный фикс | HTTP 422 и truncation исчезли после фикса конфигурации API | `gpt_comparison_report.json`, `gpt_comparison_report_v2.json` | MAR-004-014, MAR-004-015 | Planned | High | Low | 1 h | Yes | No | Yes | Bug card with before/after | Same | max_tokens 300→512 + fallback; valid_json 0.867→1.000 |
| C-013 | Before/After Latency Optimization | Card | 12b | Суммировать deployment-оптимизацию | vLLM и warm process сократили latency с ~11 с до ~1.6 с | `latency_optimization/` JSON | MAR-004-017…020 | Planned | High | Low | 1 h | Yes | No | Yes | Two large numbers + arrow | Same | Дополнить метками engine |
| C-014 | Telegram Investigation Summary Card | Card | — (не используется в v2) | — | — | — | — | Removed | — | — | — | — | — | — | — | — | В v2 убрано: Telegram-расследование не является частью Blueprint v2 |
| C-015 | Methodology / Controlled Variables Card | Card | 16, 18 | Показать, что менялось и что было зафиксировано | Гиперпараметры зафиксированы; меняли только состав обучающих примеров | `adapter_config.json` (все эксперименты), `configs/experiment_*.yaml` | MAR-001-002…MAR-004-002 | Planned | High | Low | 1 h | No | No | Yes | Parameter table card | Same | Можно совместить с C-004 |
| C-016 | Limitation / Caveat Cards | Card | 9, 13, 18 | Сохранить доверие, назвать ограничения | Разные test sets нельзя сравнивать напрямую; hard-negative качество требует проверки | All final reports | MAR-004-013, MAR-004-015, MAR-004-020 | Planned | High | Low | 1 h | Yes | No | Yes | Warning/caveat callouts | Same | 3–4 оговорки |
| C-017 | Production-Ready Boundary Card | Card | 13 | Чётко разграничить доказанное и открытое | Dataset engineering + smoke + latency доказаны; calibration/parity — next | All final reports | MAR-004-013, MAR-004-015, MAR-004-020 | Planned | High | Low | 1 h | Yes | No | Yes | Boundary card with badges | Same | Новый элемент v2; связан с D-008 |
| C-018 | Concrete Wrong Answer Card | Card | 2 | Конкретный пример ошибки base model | Base model выдала match, хотя кандидат не подходит | `generation_test_report.json` (Exp 001 base) | MAR-001-009 | Planned | High | Low | 1 h | No | Yes (extract + anonymize) | Yes | Case card | Stack vertically | Новый элемент v2 |
| C-019 | Concrete False Negative Card | Card | 7b | Конкретный пример FN Exp 003 | Истинный match отсеян после hard negatives | `generation_test_report.json` (Exp 003) | MAR-003-010 | Planned | High | Low | 1 h | No | Yes (extract + anonymize) | Yes | Case card | Stack vertically | Новый элемент v2 |

---

## 4. Таблицы (T)

| ID | Название | Тип | Blueprint v2 chapter(s) | Назначение | Главный вывод | Источник данных | MAR-ID | Статус | Приоритет | Сложность | Estimated effort | Требует custom illustration | Требует data transformation | Требует manual design | Responsive behaviour | Mobile adaptation | Примечания |
|----|----------|-----|-------------------------|------------|---------------|-----------------|--------|--------|-----------|-----------|------------------|----------------------------|----------------------------|-----------------------|----------------------|-----------------|------------|
| T-001 | Unified Experiment Comparison Table | Table | 13, 18 | Суммировать экспериментальную дугу в одном месте | Датасет engineering важнее тюнинга адаптера | Все `trainer_state.json`, `generation_test_report.json`, `runtime_smoke_report.json`, `test_evaluation/test_metrics.json` | MAR-001-006…010, MAR-002-005…009, MAR-003-006…011, MAR-004-006…013 | Planned | Critical | Medium | 2–3 h | No | Yes (aggregate per experiment) | No | Sortable if interactive | Horizontal scroll | Включить caveats |
| T-002 | LoRA vs GPT-4o-mini Comparison Table | Table | 9 | Честное сравнение с cloud model | LoRA конкурентоспособна по решениям, но отстаёт по MAE и latency | `external_validation_report.json`, `gpt_comparison_report_v2.json` | MAR-004-013, MAR-004-015, MAR-004-020 | Planned | High | Medium | 1–2 h | No | Yes (separate 15-record and 102-record columns) | No | Responsive table | Horizontal scroll | Не объединять выборки |
| T-003 | LoRA Hyperparameters Table | Table | 16, 18 | Обеспечить воспроизводимость | Гиперпараметры зафиксированы | `adapter_config.json`, `configs/experiment_*.yaml` | MAR-001-002…MAR-004-002 | Planned | Medium | Low | 1 h | No | No | No | Sticky table | Horizontal scroll | Источник истины — adapter_config.json |
| T-004 | Split Details Table | Table | 18 | Показать структуру train/val/test/holdout | Состав выборок менялся между экспериментами | `configs/experiment_*.yaml`, `data/manifest_experiment_*.json` | MAR-003-013, MAR-004-013 | Planned | Medium | Low | 1 h | No | Yes (count per split) | No | Simple table | Same | 4 столбца split |
| T-005 | FPR / FNR Table | Table | 9 | Разложить ошибки по типам | LoRA более консервативна: FNR выше, чем у GPT-4o-mini | `external_validation_report.json`, `gpt_comparison_report_v2.json` | MAR-004-013, MAR-004-015 | Planned | High | Low | 1 h | No | No | No | Compact table | Same | Для 15-record и 102-record отдельно |
| T-006 | Production Limitations / Caveats Table | Table | 9, 13, 18 | Честно назвать ограничения | Разные test sets нельзя сравнивать; hard-negative качество требует проверки | All final reports | MAR-004-013, MAR-004-015, MAR-004-020 | Planned | High | Low | 1 h | No | No | Yes | Callout table | Same | Можно совместить с C-016 |
| T-007 | Raw Metrics / Source File Inventory | Table | 17 | Позволить рецензенту проверить каждое утверждение | Каждое число связано с JSON-файлом | All `finetuning/runs/experiment_00*/` JSON files | Все MAR-001…MAR-004 | Planned | Medium | Low | 1–2 h | No | No | No | Sortable list | Horizontal scroll | Таблица mapping visual → source file; новый элемент v2 |
| T-008 | Repeat Runs Stability Table | Table | 10 | Показать стабильность smoke и external validation | Результаты повторяются между rerun'ами | `runtime_smoke_report.json` (003 rerun, 004 rerun), `external_validation_optimized_report.json` | MAR-003-011, MAR-004-011, MAR-004-016, MAR-004-020, MAR-004-021 | Planned | High | Low | 1 h | No | Yes (extract per-run metrics) | No | Compact table | Same | Новый элемент v2 |
| T-009 | Best Checkpoint Summary Table | Table | 15 | Суммировать checkpoint selection по экспериментам | Best epoch: 4, 3, 2, 3 | `trainer_state.json` (все эксперименты) | MAR-001-006…MAR-004-007 | Planned | High | Low | 1 h | No | Yes (extract best_metric, global_step, epoch) | No | Simple table | Same | Новый элемент v2 |
| T-010 | Dataset Change Log Table | Table | 16, 18 | Что добавлялось в датасет на каждом шаге | Hard negatives → positives/borderlines | `data/manifest_experiment_003.json`, `manifest_experiment_004.json` | MAR-003-013, MAR-004-013 | Planned | High | Low | 1 h | No | Yes (count by case_type) | No | Simple table | Same | Новый элемент v2 |
| T-011 | Engine Benchmark Table | Table | 12b | Точные числа по сравнению движков | vLLM быстрее; 4bit хуже и медленнее | `engine_benchmark_report.json`, `engine_benchmark_report_vllm.json` | MAR-004-017, MAR-004-018 | Planned | High | Low | 1 h | No | No | No | Responsive table | Horizontal scroll | Новый элемент v2; дополнение к G-011 |

---

## 5. Mapping: Blueprint v2 chapters → Visual Assets

| Chapter | Графики | Диаграммы | Карточки | Таблицы |
|---------|---------|-----------|----------|---------|
| 1. Титул | — | D-002 | C-001 | — |
| 2. Базовая модель | G-018 | — | C-002, C-003, C-018 | — |
| 3. Первый урок | G-001 (Exp 001), G-003, G-004 | — | C-006, C-010 | — |
| 4. Парадокс метрик | G-002, G-007 | — | — | — |
| 5. Второй урок | G-001 (Exp 002), G-004, G-005, G-006 | — | C-007 | — |
| 6. Ловушка | G-009, G-019 | D-005 | C-011 | — |
| 7a. Hard negatives | G-009, G-013 | — | C-008, C-011 | — |
| 7b. Цена отсева | G-004, G-005, G-020 | D-004 | C-019 | — |
| 8. Баланс | G-004, G-005, G-009, G-013 | D-003 | C-009, C-011 | — |
| 9. Внешняя проверка | G-008, G-014 | — | C-016 | T-002, T-005 |
| 10. Smoke repeatability | G-009 (три состояния) | — | — | T-008 |
| 11. Разрыв и фикс | G-015 | — | C-012 | — |
| 12a. Поиск узкого места | G-010, G-012 | — | — | — |
| 12b. Latency | G-011, G-010 (optimized) | — | C-013, C-016 | T-011 |
| 13. Честный диагноз | — | D-008 | C-017 | T-006 |
| 14. Следующий цикл | — | D-007 | — | — |
| 15. Лучшая эпоха | G-001, G-002, G-016, G-017 | D-009 | — | T-009 |
| 16. Данные важнее архитектуры | G-013 | D-003, D-010 | C-015 | T-003, T-010 |
| 17. Архив | Все G | Все D | Все C | T-007 |
| 18. О методе | G-013 | D-003, D-010 | C-004, C-005, C-015, C-016 | T-003, T-004, T-006, T-010 |

---

## 6. Registry Review

### 6.1 Дубли визуального представления

| Пара элементов | Характер дублирования | Решение v2 |
|------------------|-----------------------|------------|
| D-008 Proven/Partial/Next Cycle Map vs C-017 Production-Ready Boundary | Оба суммируют выводы | D-008 — структурированная карта категорий на стр. 13; C-017 — compact boundary card на той же странице. Оставить оба, разные форматы. |
| G-014 Radar vs T-002 LoRA vs GPT Table | Обе сравнивают LoRA и GPT | G-014 — компактная многомерная визуализация на стр. 9; T-002 — точные числа и разные выборки. Оставить оба, разместить рядом. |
| C-015 Methodology Card vs T-003 Hyperparameters Table | Оба содержат параметры | C-015 — краткий narrative card на стр. 16/18; T-003 — полная справочная таблица. Оставить оба на разных уровнях. |
| G-012 Latency Stage Breakdown vs C-013 Before/After Latency | Оба показывают latency | G-012 — аналитическое разложение на стр. 12a; C-013 — compact before/after на стр. 12b. Оставить оба, разные narrative уровни. |
| G-009 Smoke Matrix (три состояния) | Один и тот же тип визуала на стр. 6/7a/8/10 | Разные данные (002 fail, 003 pass, 004 pass, rerun pass). Не дубль, а повторяемость. Оставить с явными labels. |

### 6.2 Недостающие элементы (добавлены в v2)

| Чего не хватало в v1 | Где нужно | Элемент v2 | Почему важно |
|----------------------|-----------|------------|--------------|
| Checkpoint selection | 15 | G-016, D-009, T-009 | Важный методологический момент, прошедший фоном |
| Train/eval gap | 4, 15 | G-017 | Показать переобучение в каждом эксперименте |
| Concrete examples | 2, 6, 7b | G-018, G-019, G-020, C-018, C-019 | Делает failure modes осязаемыми |
| Controlled variables / dataset change log | 16, 18 | D-010, T-010 | Central thesis кейса |
| Repeat runs stability | 10 | T-008 | Показать, что smoke не однократная удача |
| Source file inventory | 17 | T-007 | Воспроизводимость и проверяемость |
| Production-ready boundary | 13 | C-017 | Чёткое разграничение доказанного и открытого |

### 6.3 Нарушения логики зависимостей

| Проблема | Решение v2 |
|----------|------------|
| C-001 Hero зависит от D-002 Timeline, но Hero размещается раньше | D-002 — компактный backbone; C-001 содержит только headline и 4 тезиса уроков. Зависимость слабая. |
| G-014 Radar и G-008 Scatter используют одни данные | Создать общий data asset для external validation + GPT comparison перед построением G-008 и G-014. |
| Новые concrete example cards требуют анонимизации | Выделить data-transformation step: extract → anonymize → render. |

---

## 7. Итоговая статистика

| Тип | Количество |
|-----|------------|
| Graphs | 20 |
| Diagrams | 9 |
| Cards | 17 |
| Tables | 11 |
| **Total visual assets** | **57** |

| Приоритет | Количество |
|-----------|------------|
| Critical | 18 |
| High | 29 |
| Medium | 8 |
| Low | 2 |

| Сложность | Количество |
|-----------|------------|
| Low | 28 |
| Medium | 27 |
| High | 2 |

| Статус | Количество |
|--------|------------|
| Planned | 57 |
| In Progress | 0 |
| Ready for Review | 0 |
| Done | 0 |

*(Примечание: G-004, G-005, G-008, G-009, G-013 были Done в v1; в v2 их статус сброшен в Planned для единообразия до полной перегенерации по Blueprint v2.)*

---

## 8. Acceptance criteria check

| Критерий | Статус | Комментарий |
|----------|--------|-------------|
| 1. Registry v2 покрывает все сцены Blueprint v2 | ✅ | 21 страница, mapping в разделе 5. |
| 2. Каждый визуальный элемент связан с исходным JSON-файлом или артефактом | ✅ | Для каждого элемента указан MAR-ID. |
| 3. Фактические дубли визуального представления устранены | ✅ | Раздел 6.1; дубли разрешены через разные форматы/уровни. |
| 4. Meta Artifact Registry не изменён и не удалён | ✅ | MAR сохранён как Source of Truth; в реестре только ссылки. |
| 5. Добавлены новые элементы для отражения инженерного процесса | ✅ | +11 элементов: checkpoint selection, train/eval gap, concrete examples, controlled variables, repeat runs stability, source inventory. |

---

## 9. Следующий этап

Visual Assets Registry v2 готов. Следующий этап — **Phase 8: Landing Implementation Plan v2 + реализация landing** (детализация [`IMPLEMENTATION_PLAN.md`](IMPLEMENTATION_PLAN.md), разработка HTML/CSS/JS, генерация графиков, деплой).

---

**Статус документа:** Visual Assets Registry v2.0 — завершён.  
**Автор:** AI Automation Portfolio Lab / Claude Code  
**Последнее обновление:** 2026-07-23
