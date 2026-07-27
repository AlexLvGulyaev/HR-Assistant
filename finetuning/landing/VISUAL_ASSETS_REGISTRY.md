# Реестр визуальных артефактов лендинга HR Assistant LoRA v3

**Назначение:** единый источник истины для SVG-артефактов storytelling-лендинга `https://hra-lora.alex-n8n.site`.  
**Концепция:** [`NARRATIVE_BLUEPRINT.md`](NARRATIVE_BLUEPRINT.md) — повествовательная спецификация.  
**Source of truth:** текущая реализация landing (`index.html`, `assets/visuals/`).

---

## 0. Категории артефактов

В реестре описаны две независимые категории визуальных артефактов:

| Категория | Где используется | Количество | Раздел |
|-----------|------------------|------------|--------|
| **SVG лендинга** | Непосредственно в `index.html` на сценах | 24 | [§1](#1-сцены-и-артефакты-лендинга) |
| **Иллюстрации Narrative Blueprint** | В [`NARRATIVE_BLUEPRINT.md`](NARRATIVE_BLUEPRINT.md) для визуального усиления повествования | 16 | [§2](#2-иллюстрации-narrative-blueprint) |

Каждый SVG лендинга привязан к конкретной сцене и решает одну повествовательную задачу. Цифры, подписи и цвета в SVG соответствуют данным из [`data/experimentData.js`](data/experimentData.js) и исходным JSON-артефактам в [`../runs/`](../runs/).

Иллюстрации Blueprint — это те же SVG-графики landing и одна дополнительная схема эволюции Люмины, встроенные в документ как акценты повествования.

---

## 1. Сцены и артефакты лендинга

| Интерфейсная сцена | DOM-секция | Основной SVG | Назначение | Источник данных |
|--------------------|------------|--------------|------------|-----------------|
| 1 · Рождение | `scene-1` | — | Титул, появление Люмины | `js/app.js` |
| 2 · Действующие лица | `scene-2` | — | Глоссарий персонажей | `index.html` |
| 3 · Базовая модель | `scene-3` | — | Scorecard базовой модели, case-card | [`data/experimentData.js`](data/experimentData.js) |
| 4 · Первый урок | `scene-4` | [`G-001-loss-curves.svg`](assets/visuals/G-001-loss-curves.svg) | Динамика train/eval loss, best checkpoint | `../runs/experiment_00*/trainer_state.json` |
| 5 · Парадокс метрик | `scene-5` | [`G-002-best-eval-loss.svg`](assets/visuals/G-002-best-eval-loss.svg) | Парадокс: низкий loss ≠ хорошие решения | `trainer_state.json`, `generation_test_report.json` |
| 6 · Второй урок | `scene-6` | [`G-021-base-vs-lora-exp001-exp002.svg`](assets/visuals/G-021-base-vs-lora-exp001-exp002.svg) | Сравнение Base и LoRA по DA/MAE | `../runs/experiment_001/generation_test_report.json`, `../runs/experiment_002/generation_test_report.json` |
| 7 · Ловушка | `scene-7` | [`G-022-exp002-smoke-fail.svg`](assets/visuals/G-022-exp002-smoke-fail.svg) | Smoke Exp 002: positive pass, negative fail | `../runs/experiment_002/runtime_smoke_report.json` |
| 8a · Третий урок | `scene-8` | [`G-023-dataset-evolution-exp001-003.svg`](assets/visuals/G-023-dataset-evolution-exp001-003.svg) | Изменение датасета 90 → 123 | `../data/manifest_experiment_003.json`, `configs/experiment_*.yaml` |
| 8b · Торговля | `scene-9` | [`G-024-precision-recall-tradeoff-scene8b.svg`](assets/visuals/G-024-precision-recall-tradeoff-scene8b.svg) | Precision/recall trade-off | `../runs/experiment_003/generation_test_report.json` |
| 9 · Баланс | `scene-10` | [`G-025-balance-dataset-and-metrics.svg`](assets/visuals/G-025-balance-dataset-and-metrics.svg) | Совмещённая картина датасета и метрик | `../data/manifest_experiment_004.json`, `generation_test_report.json` |
| 10 · Внешняя проверка | `scene-11` | [`G-008-external-validation-scatter.svg`](assets/visuals/G-008-external-validation-scatter.svg) | Близость LoRA score к reference на 102 записях | `../data/external_validation/external_validation_report.json` |
| 11 · Smoke repeatability | `scene-12` | [`G-026-smoke-repeatability-matrix.svg`](assets/visuals/G-026-smoke-repeatability-matrix.svg) | Стабильность smoke на трёх прогонах | `runtime_smoke_report.json` (003, 004, rerun) |
| 12 · Разрыв и фикс | `scene-13` | [`G-015-before-after-truncation.svg`](assets/visuals/G-015-before-after-truncation.svg) | Влияние фикса truncation | `../data/external_validation/gpt_comparison_report.json`, `gpt_comparison_report_v2.json` |
| 13a · Поиск узкого места | `scene-14` | [`G-012-latency-stage-breakdown.svg`](assets/visuals/G-012-latency-stage-breakdown.svg) | Разложение времени ответа по стадиям | `../runs/experiment_004/latency_profile_report.json` |
| 13b · Latency | `scene-15` | [`G-011-engine-benchmark.svg`](assets/visuals/G-011-engine-benchmark.svg) | Сравнение inference-движков | `../runs/experiment_004/engine_benchmark_report.json`, `engine_benchmark_report_vllm.json` |
| 14 · Сильнее ожиданий | `scene-16` | [`G-027-qwen-lora-vs-gpt.svg`](assets/visuals/G-027-qwen-lora-vs-gpt.svg) | Сравнение с GPT-4o-mini | `../data/external_validation/external_validation_report.json`, `latency.optimized` summary |
| 15 · Честный диагноз | `scene-17` | [`D-008-proven-partial-next.svg`](assets/visuals/D-008-proven-partial-next.svg) | Карта: доказано / частично / дальше | Итоговые отчёты экспериментов |
| 16 · Следующий цикл | `scene-18` | [`D-007-next-cycle-roadmap.svg`](assets/visuals/D-007-next-cycle-roadmap.svg) | Дорожная карта | Контекст проекта |
| 17 · Разбор эпох | `scene-19` | [`G-028-exp004-epoch-breakdown.svg`](assets/visuals/G-028-exp004-epoch-breakdown.svg) | Train/eval loss Exp 004 с marker лучшей эпохи | `../runs/experiment_004/trainer_state.json`, `generation_test_report.json` |
| 18 · Лучшая эпоха | `scene-20` | [`G-016-best-epoch-markers.svg`](assets/visuals/G-016-best-epoch-markers.svg) | Best epoch во всех экспериментах | `../runs/experiment_00*/trainer_state.json` |
| 19 · Данные важнее архитектуры | `scene-21` | [`D-010-dataset-change-log.svg`](assets/visuals/D-010-dataset-change-log.svg) | Что менялось, что было зафиксировано | `../runs/experiment_00*/adapter_config.json`, `configs/experiment_*.yaml` |
| 20 · Архив | `scene-22` | [`G-001-loss-curves.svg`](assets/visuals/G-001-loss-curves.svg), [`G-007-test-eval-loss.svg`](assets/visuals/G-007-test-eval-loss.svg), [`G-006-per-component-mae.svg`](assets/visuals/G-006-per-component-mae.svg), [`G-010-latency-cdf.svg`](assets/visuals/G-010-latency-cdf.svg), [`G-014-lora-vs-gpt-radar.svg`](assets/visuals/G-014-lora-vs-gpt-radar.svg), [`D-003-dataset-composition-transition.svg`](assets/visuals/D-003-dataset-composition-transition.svg) | Evidence room: ключевые графики | Соответствующие JSON-источники |
| 21 · О методе | `scene-23` | [`D-001-pipeline-schematic.svg`](assets/visuals/D-001-pipeline-schematic.svg) | Полный pipeline | `configs/experiment_*.yaml`, `api/`, runtime-отчёты |

---

## 2. Иллюстрации Narrative Blueprint

Эти артефакты используются в [`NARRATIVE_BLUEPRINT.md`](NARRATIVE_BLUEPRINT.md) для визуального усиления повествовательных акцентов. Большинство из них — это те же SVG-графики landing, встроенные в текст документа. Дополнительно: одна схема эволюции Люмины.

| Рисунок | SVG | Где в Blueprint | Назначение |
|---------|-----|-----------------|------------|
| 1 | [`lumina-evolution.svg`](assets/visuals/lumina-evolution.svg) | §3.3 | Девять состояний Люмины в прогрессии |
| 2 | [`G-001-loss-curves.svg`](assets/visuals/G-001-loss-curves.svg) | Сцена 4 | Train/eval loss Exp 001 |
| 3 | [`G-002-best-eval-loss.svg`](assets/visuals/G-002-best-eval-loss.svg) | Сцена 5 | Парадокс best eval loss |
| 4 | [`G-021-base-vs-lora-exp001-exp002.svg`](assets/visuals/G-021-base-vs-lora-exp001-exp002.svg) | Сцена 6 | Base vs LoRA |
| 5 | [`G-022-exp002-smoke-fail.svg`](assets/visuals/G-022-exp002-smoke-fail.svg) | Сцена 7 | Smoke Exp 002: negative fail |
| 6 | [`G-023-dataset-evolution-exp001-003.svg`](assets/visuals/G-023-dataset-evolution-exp001-003.svg) | Сцена 8a | Эволюция датасета 90 → 123 |
| 7 | [`G-024-precision-recall-tradeoff-scene8b.svg`](assets/visuals/G-024-precision-recall-tradeoff-scene8b.svg) | Сцена 8b | Precision/recall trade-off |
| 8 | [`G-025-balance-dataset-and-metrics.svg`](assets/visuals/G-025-balance-dataset-and-metrics.svg) | Сцена 9 | Баланс датасета и метрик |
| 9 | [`G-008-external-validation-scatter.svg`](assets/visuals/G-008-external-validation-scatter.svg) | Сцена 10 | External validation scatter |
| 10 | [`G-015-before-after-truncation.svg`](assets/visuals/G-015-before-after-truncation.svg) | Сцена 12 | Before/after truncation fix |
| 11 | [`G-012-latency-stage-breakdown.svg`](assets/visuals/G-012-latency-stage-breakdown.svg) | Сцена 13a | Latency stage breakdown |
| 12 | [`G-011-engine-benchmark.svg`](assets/visuals/G-011-engine-benchmark.svg) | Сцена 13b | Benchmark inference-движков |
| 13 | [`G-027-qwen-lora-vs-gpt.svg`](assets/visuals/G-027-qwen-lora-vs-gpt.svg) | Сцена 14 | Qwen-LoRA vs GPT-4o-mini |
| 14 | [`G-016-best-epoch-markers.svg`](assets/visuals/G-016-best-epoch-markers.svg) | Сцена 18 | Best epoch markers |
| 15 | [`D-010-dataset-change-log.svg`](assets/visuals/D-010-dataset-change-log.svg) | Сцена 19 | Dataset change log |
| 16 | [`D-001-pipeline-schematic.svg`](assets/visuals/D-001-pipeline-schematic.svg) | Сцена 21 | Full pipeline |

---

## 3. Принципы именования и генерации

- Все SVG лежат в [`assets/visuals/`](assets/visuals/).
- Имя файла: `<TYPE>-<NNN>-<kebab-description>.svg`.
- Генерация: [`data/generate_graphs.py`](data/generate_graphs.py) на основе [`data/experimentData.json`](data/experimentData.json), который создаётся [`data/extract_data.py`](data/extract_data.py) из [`../runs/`](../runs/).
- Кеширование: nginx отдаёт SVG с `Cache-Control: public, immutable, max-age=1y`; при изменении данных нужна перегенерация и пересборка образа.

---

**Статус реестра:** синхронизирован с интерфейсной нумерацией landing v3 (21 сцена), все SVG — кликабельные ссылки.  
**Последнее обновление:** 2026-07-27
