# Implementation Plan — HR Assistant LoRA Storytelling Landing v2

**Кейс:** `hr-assistant`  
**Целевая страница:** `https://hra-lora.alex-n8n.site`  
**Дата:** 2026-07-23  
**Статус:** Phase 8 выполнена — landing v2 реализован, локальный preview пройден, готов к production deploy по `DEPLOYMENT_GUIDE.md`.  
**Source of Truth:** настоящий документ фиксирует обязательную последовательность от Meta Artifact Registry до реализации landing. Internal predecessor materials are archived in `task_history/attachments/landing_internal/`.

---

## 1. Назначение документа

Этот документ — единый проектный план переработки demo-landing HR Assistant LoRA. Он не заменяет [`DEPLOYMENT_GUIDE.md`](../DEPLOYMENT_GUIDE.md) (Source of Truth развёртывания), а дополняет его: описывает, **какие документы и артефакты должны быть подготовлены и согласованы до начала разработки**, и в каком порядке.

План построен по восьми обязательным этапам. Каждый следующий этап зависит от выходных документов предыдущего. Нельзя начинать этап 8 (реализацию landing) до утверждения `Narrative Blueprint v2` и `Visual Assets Registry v2`.

---

## 2. Текущее состояние

### Что уже существует и служит входом для плана

| Документ / артефакт | Назначение | Статус |
|---------------------|------------|--------|
| `finetuning/reports/experiment_001_artifact_inventory.md` | Полная инвентаризация Experiment 001 | ✅ Готово |
| `finetuning/reports/experiment_002_artifact_inventory.md` | Полная инвентаризация Experiment 002 | ✅ Готово |
| `finetuning/reports/experiment_003_artifact_inventory.md` | Полная инвентаризация Experiment 003 | ✅ Готово |
| `finetuning/reports/experiment_004_artifact_inventory.md` | Полная инвентаризация Experiment 004 | ✅ Готово |
| `task_history/attachments/landing_internal/experiment_story_analysis.md` | Сводный анализ переходов между экспериментами | ✅ Готово |
| `task_history/attachments/landing_internal/hra_lora_narrative_blueprint.md` | Narrative Blueprint v1.0 (научно-популярный фильм, модель-герой) | ✅ Готово |
| `VISUAL_ASSETS_REGISTRY.md` | Visual Assets Registry v1 (46 элементов: G/T/D/C) | ✅ Готово |
| `task_history/attachments/landing_internal/portfolio_case_visual_concept.md` | Визуальная концепция и драматургия | ✅ Готово |
| `task_history/attachments/landing_internal/hra_lora_storytelling_landing_concept.md` | Режиссёрская концепция и Sound-Off Test | ✅ Готово |
| `task_history/attachments/landing_internal/hra_lora_narrative_blueprint_assessment.md` | Оценка Blueprint v1, рекомендация четырёх спринтов инвентаризации | ✅ Готово |
| `README.md` | Описание landing и quick start | ✅ Готово |
| `DEPLOYMENT_GUIDE.md` | Source of Truth развёртывания | ✅ Готово |

### Чего ещё нет

| Документ | Этап | Статус |
|----------|------|--------|
| `task_history/attachments/landing_internal/meta_artifact_registry.md` | 1 | ❌ Не создан |
| `task_history/attachments/landing_internal/engineering_knowledge_graph.md` | 2 | ❌ Не создан |
| `task_history/attachments/landing_internal/story_mining.md` | 3 | ❌ Не создан |
| `task_history/attachments/landing_internal/narrative_gap_analysis.md` | 4 | ❌ Не создан |
| `task_history/attachments/landing_internal/narrative_extension_proposal.md` | 5 | ❌ Не создан |
| `NARRATIVE_BLUEPRINT.md` | 6 | ✅ Готово |
| `VISUAL_ASSETS_REGISTRY.md` v2 | 7 | ✅ Готово |
| [`IMPLEMENTATION_PLAN.md`](IMPLEMENTATION_PLAN.md) | 8 (план) | ✅ Готово |
| `index.html` v2 | 8 (код) | ✅ Реализовано |
| `css/main.css` v2 | 8 (код) | ✅ Реализовано |
| `js/app.js` v2 | 8 (код) | ✅ Реализовано |

---

## 3. Обязательная последовательность этапов

### Этап 1. Meta Artifact Registry

**Документ:** `task_history/attachments/landing_internal/meta_artifact_registry.md`  
**Входные документы:**
- `finetuning/reports/experiment_001_artifact_inventory.md`
- `finetuning/reports/experiment_002_artifact_inventory.md`
- `finetuning/reports/experiment_003_artifact_inventory.md`
- `finetuning/reports/experiment_004_artifact_inventory.md`
- `task_history/attachments/landing_internal/experiment_story_analysis.md`
- Исходные JSON- и MD-файлы в `finetuning/runs/experiment_00*/`

**Задача:**
Создать полный инженерный каталог всех артефактов без редакторского отбора под landing. Для каждого артефакта зафиксировать:
- ID;
- название;
- тип (model, checkpoint, log, report, evaluation, smoke, latency, config, manifest, operation_log и др.);
- эксперимент-источник (001–004, shared, external);
- исходные файлы с точными путями;
- используемые данные;
- первичный или производный характер;
- инженерные вопросы, на которые он отвечает;
- выводы, которые он подтверждает;
- связи с другими артефактами;
- уникальность, частный случай или обобщённая версия;
- возможность автоматического построения из других данных.

**Acceptance criteria:**
1. Каталог покрывает все артефакты, упомянутые в четырёх inventory reports, плюс дополнительные файлы, обнаруженные в `finetuning/runs/`.
2. Каждый артефакт содержит все обязательные поля.
3. Нет ранжирования, минимизации или решения о включении в landing.
4. Документ можно использовать как инженерный Source of Truth для всех последующих этапов.

---

### Этап 2. Engineering Knowledge Graph

**Документ:** `task_history/attachments/landing_internal/engineering_knowledge_graph.md`  
**Входные документы:**
- `task_history/attachments/landing_internal/meta_artifact_registry.md`
- 4 inventory reports
- `task_history/attachments/landing_internal/experiment_story_analysis.md`

**Задача:**
Превратить каталог артефактов в карту причинно-следственных связей. Показать:
- какая гипотеза привела к каждому эксперименту;
- какие изменения были внесены в данные, обучение или runtime;
- какие артефакты подтверждают результат изменения;
- какие проблемы выявились;
- какие решения были приняты после этого;
- как один эксперимент логически породил следующий.

Отразить параллельные инженерные линии:
- развитие датасета;
- динамика обучения;
- checkpoint selection;
- business evaluation;
- борьба с false positives и false negatives;
- production smoke validation;
- external validation;
- сравнение с GPT;
- исправление production bug;
- latency optimization.

**Acceptance criteria:**
1. Для каждого эксперимента 001–004 описана входная гипотеза, внесённое изменение и исход.
2. Между экспериментами прослеживаются логические переходы.
3. Все перечисленные параллельные линии присутствуют и связаны с артефактами.
4. Документ читается как единая история развития модели, а не как список независимых фактов.

---

### Этап 3. Story Mining

**Документ:** `task_history/attachments/landing_internal/story_mining.md`  
**Входные документы:**
- `task_history/attachments/landing_internal/engineering_knowledge_graph.md`
- `task_history/attachments/landing_internal/hra_lora_narrative_blueprint.md` (для понимания сохраняемых сильных идей)

**Задача:**
Извлечь из Engineering Knowledge Graph все самостоятельные потенциальные сюжетные линии. Для каждой линии зафиксировать:
- центральный вопрос;
- исходную проблему;
- последовательность инженерных событий;
- ключевые повороты;
- подтверждающие артефакты;
- итоговый вывод;
- связь с основным образом развивающейся языковой модели.

Линии не ограничивать заранее. Проверить и зафиксировать, в том числе, истории вида:
- модель научилась форме, но ещё не смыслу;
- рост ёмкости LoRA улучшил решение задачи;
- улучшение одной метрики не гарантирует эксплуатационной надёжности;
- hard negatives уменьшили ложные срабатывания, но снизили recall;
- балансировка датасета восстановила равновесие;
- лучшая эпоха — не последняя;
- train loss и eval loss не равны business quality;
- небольшой тест может вводить в заблуждение;
- production smoke выявляет проблемы, которых не видно в training metrics;
- внешняя выборка проверяет способность к обобщению;
- сравнительная модель может быть сильнее в score calibration;
- production bug меняет интерпретацию результатов;
- latency становится отдельной инженерной задачей после достижения качества.

**Acceptance criteria:**
1. Список сюжетных линий полный и не ограничен только приведёнными примерами.
2. Каждая линия обоснована конкретными артефактами.
3. Для каждой линии описана связь с образом модели-героя.
4. Линии не ранжируются по пригодности для landing.

---

### Этап 4. Narrative Gap Analysis

**Документ:** `task_history/attachments/landing_internal/narrative_gap_analysis.md`  
**Входные документы:**
- `task_history/attachments/landing_internal/hra_lora_narrative_blueprint.md` (v1)
- `task_history/attachments/landing_internal/story_mining.md`
- `task_history/attachments/landing_internal/engineering_knowledge_graph.md`
- `task_history/attachments/landing_internal/meta_artifact_registry.md`
- `VISUAL_ASSETS_REGISTRY.md` (v1)

**Задача:**
Сравнить существующий Blueprint v1 с результатами Story Mining, Engineering Knowledge Graph и Meta Artifact Registry. Для каждой существующей главы Blueprint v1 определить:
- что раскрыто полно;
- что раскрыто частично;
- какие инженерные события отсутствуют;
- где результат показан без объяснения процесса;
- где не показаны гипотеза, эксперимент, ошибка или решение;
- где отсутствуют переходы между экспериментами;
- какие новые артефакты позволяют расширить сцену;
- требуется ли усиление, разделение или добавление новой главы.

**Acceptance criteria:**
1. Проведён анализ всех глав Blueprint v1.
2. Для каждой главы указаны полнота, пробелы и точки расширения.
3. Нет предложений удалить сильные старые сцены только из-за появления новых.
4. Документ не заменяет Blueprint v1, а готовит материал для Extension Proposal.

---

### Этап 5. Narrative Extension Proposal

**Документ:** `task_history/attachments/landing_internal/narrative_extension_proposal.md`  
**Входные документы:**
- `task_history/attachments/landing_internal/narrative_gap_analysis.md`
- `task_history/attachments/landing_internal/story_mining.md`

**Задача:**
Подготовить план эволюции существующего Blueprint v1, а не новый Blueprint. Для каждой существующей главы указать:
- исходную идею;
- что сохраняется без изменений;
- что необходимо усилить;
- какие новые инженерные сцены добавляются;
- какие новые сюжетные линии интегрируются;
- какие визуальные артефакты подтверждают каждую сцену;
- какие переходы связывают старый и новый материал.

Отдельно перечислить новые главы, которых раньше не было, но которые необходимы для отражения полного инженерного процесса.

**Acceptance criteria:**
1. Для каждой главы Blueprint v1 зафиксированы сохраняемое, усиливаемое и добавляемое.
2. Новые сцены привязаны к визуальным артефактам из Meta Artifact Registry / Visual Assets Registry.
3. Перечислены все новые главы с обоснованием.
4. Переходы между старым и новым материалом описаны явно.

---

### Этап 6. Narrative Blueprint v2

**Документ:** `NARRATIVE_BLUEPRINT.md`  
**Входные документы:**
- `task_history/attachments/landing_internal/narrative_extension_proposal.md`
- `task_history/attachments/landing_internal/hra_lora_narrative_blueprint.md` (v1)
- `task_history/attachments/landing_internal/engineering_knowledge_graph.md`
- `task_history/attachments/landing_internal/story_mining.md`

**Задача:**
Создать расширенный Narrative Blueprint v2. Требования:
- сохранить утверждённую концепцию научно-популярного фильма;
- сохранить языковую модель как главного героя;
- сохранить сильные идеи и удачные сцены предыдущего Blueprint;
- расширить повествование инженерным процессом;
- показать не только четыре результата экспериментов, но и логику их появления;
- показать обучение внутри каждого эксперимента, а не только сравнение финальных моделей;
- явно отразить гипотезы, ошибки, противоречия метрик, checkpoint selection и production validation;
- связать Experiment 001–004 в единую историю развития модели;
- завершить историю переходом от качества к эксплуатационной пригодности и latency optimization.

Для каждой главы определить:
- narrative purpose;
- главный инженерный вопрос;
- события;
- ключевые артефакты;
- вывод;
- переход к следующей главе.

**Acceptance criteria:**
1. Сохранены концепция фильма, модель-герой и сильные сцены v1.
2. Показан инженерный процесс внутри каждого эксперимента.
3. Отражены гипотезы, ошибки, противоречия метрик, выбор чекпоинтов и production validation.
4. Experiment 001–004 связаны в единую историю развития модели.
5. История завершается latency optimization и переходом к эксплуатационной пригодности.
6. Документ готов к согласованию и использованию как основа Visual Assets Registry v2.

---

### Этап 7. Visual Assets Registry v2

**Документ:** `VISUAL_ASSETS_REGISTRY.md` (обновление до v2)  
**Входные документы:**
- `NARRATIVE_BLUEPRINT.md`
- `task_history/attachments/landing_internal/meta_artifact_registry.md`
- `VISUAL_ASSETS_REGISTRY.md` (v1)

**Задача:**
Обновить Visual Assets Registry на основе финальной истории Blueprint v2. Требования:
- сохранить полный Meta Artifact Registry как инженерный Source of Truth;
- в Visual Assets Registry указать, какие артефакты участвуют в конкретных сценах Blueprint v2;
- устранить только фактические дубли визуального представления;
- не удалять инженерные сущности из Meta Artifact Registry;
- добавить новые графики, таблицы, карточки и диаграммы, необходимые для расширенного процесса.

**Acceptance criteria:**
1. Registry v2 покрывает все сцены Blueprint v2.
2. Каждый визуальный элемент связан с исходным JSON-файлом или артефактом.
3. Фактические дубли визуального представления устранены.
4. Meta Artifact Registry не изменён и не удалён.
5. Добавлены новые элементы, необходимые для отражения инженерного процесса (training dynamics, checkpoint selection, per-example диагностика и др.).

---

### Этап 8. Landing Implementation Plan v2 + реализация landing

**Документ:** [`IMPLEMENTATION_PLAN.md`](IMPLEMENTATION_PLAN.md) (детализация до production-ready плана)  
**Входные документы:**
- `NARRATIVE_BLUEPRINT.md`
- `VISUAL_ASSETS_REGISTRY.md` (v2)
- `DEPLOYMENT_GUIDE.md`

**Задача:**
Подготовить конкретный план реализации demo-landing, привязанный к сценам Blueprint v2. Для каждой страницы или сцены определить:
- её место в Narrative Blueprint v2;
- существующий или новый статус;
- необходимые данные;
- визуальные артефакты;
- интерактивные элементы;
- тексты и подписи;
- изменения HTML;
- изменения CSS;
- изменения JavaScript;
- зависимости от новых графиков и таблиц;
- acceptance criteria;
- порядок реализации;
- проверку на сохранение существующих сильных частей landing.

**Acceptance criteria:**
1. План привязан к сценам Blueprint v2, а не представляет общий список UI-задач.
2. Для каждой сцены заданы данные, артефакты, тексты, HTML/CSS/JS-изменения и acceptance criteria.
3. Порядок реализации определён и учитывает зависимости от графиков и таблиц.
4. Учтено сохранение существующих сильных частей landing.
5. Масштаб изменений определяется полнотой новой истории, а не принципом минимальной переработки.
6. После завершения плана landing может быть развёрнут по `DEPLOYMENT_GUIDE.md`.

---

## 4. Зависимости между этапами

```
Этап 1 ──→ Этап 2 ──→ Этап 3 ──→ Этап 4 ──→ Этап 5 ──→ Этап 6 ──→ Этап 7 ──→ Этап 8
Meta      Eng.        Story        Gap          Extension    Blueprint    Visual       Landing
Artifact    Knowledge   Mining       Analysis     Proposal     v2           Assets       impl.
Registry    Graph                                             (согласование) Registry v2  + code
```

- Этап 2 зависит от Meta Artifact Registry.
- Этап 3 зависит от Engineering Knowledge Graph.
- Этап 4 зависит от Story Mining, Blueprint v1, Visual Assets Registry v1 и Meta Artifact Registry.
- Этап 5 зависит от Narrative Gap Analysis.
- Этап 6 зависит от Narrative Extension Proposal.
- Этап 7 зависит от Blueprint v2 и Meta Artifact Registry.
- Этап 8 зависит от Blueprint v2 и Visual Assets Registry v2.

Пропускать или объединять этапы запрещено. Каждый документ является обязательным входом для следующего.

---

## 5. Рекомендуемый порядок следующих спринтов

| # | Спринт | Этап | Выходной документ | Входные документы | Оценочная длительность |
|---|--------|------|-------------------|-------------------|------------------------|
| 1 | Meta Artifact Registry | 1 | `task_history/attachments/landing_internal/meta_artifact_registry.md` | 4 inventory reports, исходные JSON/MD экспериментов | 1 спринт |
| 2 | Engineering Knowledge Graph | 2 | `task_history/attachments/landing_internal/engineering_knowledge_graph.md` | Meta Artifact Registry | 1 спринт |
| 3 | Story Mining | 3 | `task_history/attachments/landing_internal/story_mining.md` | Engineering Knowledge Graph | 1 спринт |
| 4 | Narrative Gap Analysis | 4 | `task_history/attachments/landing_internal/narrative_gap_analysis.md` | Story Mining + Blueprint v1 + Registry v1 + Meta Artifact Registry | 1 спринт |
| 5 | Narrative Extension Proposal | 5 | `task_history/attachments/landing_internal/narrative_extension_proposal.md` | Narrative Gap Analysis | 1 спринт |
| 6 | Narrative Blueprint v2 | 6 | `NARRATIVE_BLUEPRINT.md` | Narrative Extension Proposal | 1–2 спринта (включая согласование) |
| 7 | Visual Assets Registry v2 | 7 | `VISUAL_ASSETS_REGISTRY.md` (обновление) | Blueprint v2 + Meta Artifact Registry | 1 спринт |
| 8 | Landing Implementation Plan v2 + разработка | 8 | [`IMPLEMENTATION_PLAN.md`](IMPLEMENTATION_PLAN.md) (детализация) + код landing | Blueprint v2 + Visual Assets Registry v2 | 2–3 спринта |

**Примечание:** сроки оценочные. Длительность зависит от глубины детализации и количества новых визуальных артефактов.

---

## 6. Документы, которые будут созданы или обновлены

### Создаются заново

- `task_history/attachments/landing_internal/meta_artifact_registry.md`
- `task_history/attachments/landing_internal/engineering_knowledge_graph.md`
- `task_history/attachments/landing_internal/story_mining.md`
- `task_history/attachments/landing_internal/narrative_gap_analysis.md`
- `task_history/attachments/landing_internal/narrative_extension_proposal.md`
- `NARRATIVE_BLUEPRINT.md`
- [`IMPLEMENTATION_PLAN.md`](IMPLEMENTATION_PLAN.md) — настоящий документ (будет дополнен детализацией этапа 8 после готовности Blueprint v2 и Registry v2).

### Обновляются

- `VISUAL_ASSETS_REGISTRY.md` — обновление до v2.
- `index.html`, `css/main.css`, `js/app.js` — в рамках этапа 8.
- `data/experimentData.json`, `data/extract_data.py`, `data/generate_graphs.py` — в рамках этапа 8.
- `assets/visuals/*.svg` — в рамках этапа 8.

### Остаются без изменений на время Phase 1

- `task_history/attachments/landing_internal/hra_lora_narrative_blueprint.md` — остаётся Blueprint v1 до утверждения v2.
- `task_history/attachments/landing_internal/hra_lora_storytelling_landing_concept.md` — остаётся режиссёрской концепцией.
- `task_history/attachments/landing_internal/portfolio_case_visual_concept.md` — остаётся визуальной концепцией.
- `DEPLOYMENT_GUIDE.md` — остаётся Source of Truth развёртывания; актуализируется только если меняется инфраструктура landing.

---

## 7. Критерии завершения всего плана

1. Все документы этапов 1–7 созданы, согласованы и связаны между собой.
2. Blueprint v2 одобрен и не противоречит сильным идеям v1.
3. Visual Assets Registry v2 покрывает все сцены Blueprint v2.
4. Implementation Plan этапа 8 детализирован до уровня сцен с acceptance criteria.
5. Landing реализован в соответствии с Blueprint v2 и Registry v2.
6. Развёртывание проверено по `DEPLOYMENT_GUIDE.md`.
7. Все числа и визуальные артефакты на landing прослеживаются к исходным JSON-файлам проекта.

---

## 8. Ограничения и правила, закреплённые в плане

- **Старый Blueprint не заменяется новым без Gap Analysis и Extension Proposal.**
- **История не сокращается ради сохранения текущего количества экранов.**
- **Инженерные события не ранжируются по принципу «помещается / не помещается»; ранжирование возможно только на этапе 7 при устранении фактических дублей.**
- **Новые знания не подгоняются под существующую структуру landing.**
- **Реализация landing не начинается до завершения и согласования Blueprint v2 и Visual Assets Registry v2.**
- **Старые сильные сцены не удаляются только потому, что появились новые.**
- **Не используются слова «минимальный», «достаточный минимум» или аналогичная логика при описании объёма переработки.**

---

## 9. Связанные документы

- [`DEPLOYMENT_GUIDE.md`](../DEPLOYMENT_GUIDE.md) — Source of Truth развёртывания.
- [`README.md`](../README.md) — описание landing и quick start.
- `task_history/attachments/landing_internal/hra_lora_narrative_blueprint.md` — Blueprint v1.
- `VISUAL_ASSETS_REGISTRY.md` — Visual Assets Registry v1.
- `task_history/attachments/landing_internal/experiment_story_analysis.md` — анализ четырёх экспериментов.
- `finetuning/reports/experiment_001_artifact_inventory.md`
- `finetuning/reports/experiment_002_artifact_inventory.md`
- `finetuning/reports/experiment_003_artifact_inventory.md`
- `finetuning/reports/experiment_004_artifact_inventory.md`

---

**Статус документа:** Implementation Plan v1.0 — план этапов зафиксирован.  
**Следующий шаг:** начать спринт 1 — создание `task_history/attachments/landing_internal/meta_artifact_registry.md`.  
**Автор:** AI Automation Portfolio Lab / Claude Code  
**Последнее обновление:** 2026-07-23
