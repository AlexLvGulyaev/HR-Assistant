# Critical Graphs — Портфельный кейс HR Assistant

Реализация первой партии визуальных артефактов для портфельного кейса. Все графики построены из реальных JSON/YAML-артефактов проекта.

## Быстрое воспроизведение

```bash
# Из корня кейса (cases/hr-assistant)
portfolio_visuals/.venv/bin/python portfolio_visuals/scripts/generate_critical_graphs.py
```

При первом запуске виртуальное окружение должно быть создано и содержать `matplotlib`, `pandas`, `pyyaml`:

```bash
python3 -m venv portfolio_visuals/.venv
portfolio_visuals/.venv/bin/pip install matplotlib pandas pyyaml
```

## Структура

```
portfolio_visuals/
├── scripts/generate_critical_graphs.py   # единый скрипт генерации + проверки
├── data/                                 # нормализованные производные данные
├── svg/                                  # основной формат для сайта
├── png/                                  # превью для репозитория / документации
└── README.md                             # эта инструкция
```

## G-004 — Decision Accuracy Evolution

**Файлы:**
- SVG: `svg/G-004-decision-accuracy-evolution.svg`
- PNG: `png/G-004-decision-accuracy-evolution.png`
- Данные: `data/G-004-G-005-metric-evolution.csv`

**Источники:**
- `finetuning/runs/experiment_001/generation_test/generation_test_report.json`
- `finetuning/runs/experiment_002/generation_test/generation_test_report.json`
- `finetuning/runs/experiment_003/generation_test/generation_test_report.json`
- `finetuning/runs/experiment_004/generation_test/generation_test_report.json`

**Вывод:**
Точность matching-решений LoRA прошла неравномерную дугу: 44% (Exp 001) → 78% (Exp 002) → 67% (Exp 003) → 80% (Exp 004).

**Преобразования:**
- Извлечены `summary.decision_accuracy` для `base_qwen` и `best_lora` каждого эксперимента.
- Столбцы сгруппированы по эксперименту; LoRA соединена линией тренда.

**Известные ограничения:**
- Test sets различаются между экспериментами (9 записей в 001–003, 15 в 004; разные case_codes).
- Сравнение направленное, не абсолютное.
- В Exp 003 наблюдается precision/recall trade-off: модель стала консервативнее после добавления hard negatives.

## G-005 — MAE Score Evolution

**Файлы:**
- SVG: `svg/G-005-mae-score-evolution.svg`
- PNG: `png/G-005-mae-score-evolution.png`
- Данные: `data/G-004-G-005-metric-evolution.csv`

**Источники:** те же `generation_test_report.json`.

**Вывод:**
Средняя абсолютная ошибка итогового score у LoRA снизилась с ~30 (Exp 001) до 15.1 (Exp 004). Меньшее значение визуально обозначено как лучшее.

**Преобразования:**
- Извлечены `summary.mae_score`.
- Компоновка, типографика и отступы совпадают с G-004; без dual-axis.

**Известные ограничения:**
- Test sets несопоставимы между экспериментами; тренд, а не строгое сравнение.

## G-008 — External-Validation Scatter

**Файлы:**
- SVG: `svg/G-008-external-validation-scatter.svg`
- PNG: `png/G-008-external-validation-scatter.png`
- Данные: `data/G-008-external-validation-scatter.csv`

**Источник:**
- `finetuning/runs/experiment_004/external_validation_report.json`

**Вывод:**
На независимой выборке HRA-EVAL-V5-EXT LoRA предсказания группируются вблизи диагонали reference score. Решения совпадают в 93.1% случаев (по summary по 102 записям).

**Преобразования:**
- Каждая точка: X = `reference.score`, Y = `lora_prediction.score`.
- Классификация TP/TN/FP/FN на основе `reference.decision` и `lora_prediction.decision`.
- Добавлена диагональ y = x.
- Личные данные кандидатов не отображаются.

**Известные ограничения:**
- У 5 из 102 записей `reference.score` отсутствует в JSON (sub-scores тоже None). Scatter отображает 97 точек с известным reference score.
- Decision accuracy в summary рассчитана по всем 102 записям, включая 5 без score.

## G-009 — Runtime Smoke Pass/Fail Matrix

**Файлы:**
- SVG: `svg/G-009-runtime-smoke-pass-fail-matrix.svg`
- PNG: `png/G-009-runtime-smoke-pass-fail-matrix.png`
- Данные: `data/G-009-runtime-smoke-matrix.csv`

**Источники:**
- `finetuning/runs/experiment_003/runtime_smoke_report.json`
- `finetuning/runs/experiment_004/runtime_smoke_report.json`
- `finetuning/FINETUNING_ENGINEERING_REPORT.md` (Exp 002)

**Вывод:**
Production smoke выявил failure modes, которые не видела offline-метрика: Exp 002 не прошёл negative/edge-кейсы; Exp 003 и Exp 004 прошли все 7 категорий.

**Преобразования:**
- Для Exp 003/004 статус категории определён по `evaluation.passed` в `runtime_smoke_report.json`.
- Для Exp 002 использованы категориальные итоги из инженерного отчёта: Positive = PASS; obvious_negative/hard_negative/edge_case = FAIL; invalid_input/stability_repeat = NOT RECORDED, т.к. в отчёте не разделялись.

**Известные ограничения:**
- Exp 002 не имеет структурированного runtime_smoke_report.json; две категории отмечены как NOT RECORDED.
- Детальные reasoning и тексты кейсов не выводятся на график.

## G-013 — Dataset Evolution

**Файлы:**
- SVG: `svg/G-013-dataset-evolution.svg`
- PNG: `png/G-013-dataset-evolution.png`
- Данные: `data/G-013-dataset-evolution.csv`

**Источники:**
- `finetuning/configs/experiment_001.yaml`
- `finetuning/FINETUNING_ENGINEERING_REPORT.md` (Exp 002: те же 90 записей)
- `finetuning/data/manifest_experiment_003.json`
- `finetuning/data/manifest_experiment_004.json`
- `finetuning/configs/experiment_003.yaml`
- `finetuning/configs/experiment_004.yaml`

**Вывод:**
Датасет рос за счёт целенаправленной инженерии: 90 → 123 → 162 записей. Exp 003 добавил hard negatives/edge cases; Exp 004 добавил positives/borderlines, сохранив все hard negatives.

**Преобразования:**
- Для Exp 001: total/split/classes из `experiment_001.yaml`.
- Для Exp 002: повторяет Exp 001 согласно `FINETUNING_ENGINEERING_REPORT.md`.
- Для Exp 003/004: total_records, split sizes, число кандидатов и суммы `case_type_distribution` взяты из `manifest_*.json`.
- Stacked bar по классам obvious_match / borderline / obvious_no_match.
- Line overlay по числу кандидатов (сумма `candidates` по split).

**Известные ограничения:**
- Для Exp 001/002 нет структурированного manifest; категории взяты из чернового YAML.
- Число кандидатов для Exp 003/004 — сумма по split, что совпадает с концепцией (41 и 54).

## Проверки целостности

Скрипт `generate_critical_graphs.py` перед построением выполняет:

1. Проверку наличия всех исходных файлов.
2. Проверку полей `summary` в generation reports.
3. Проверку диапазона `decision_accuracy` ∈ [0, 1].
4. Проверку неотрицательности MAE и диапазона score ∈ [0, 100].
5. Проверку числа записей external validation (102) и runtime smoke (7/7).
6. Проверку суммы split records в manifest против `total_records`.
7. Проверку, что итоговые числа в CSV соответствуют исходным файлам.

При любом нарушении скрипт завершается с ошибкой и не строит неполный график.
