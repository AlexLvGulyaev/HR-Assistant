# Отчёт о teacher dataset

**Дата:** 2026-07-22
**Эксперимент:** HRA-EXP-V4
**Датасет:** HRA-EVAL-V4

## Summary

- **Всего записей:** 162
- **Train:** 114
- **Validation:** 27
- **Test:** 15
- **Hard Negative Holdout:** 6

## 1. Методология

### 1.1 Как собирается teacher dataset

Teacher dataset формируется из reference-слоя Prompt Evaluation, хранящегося в PostgreSQL. Для каждого эксперимента запись датасета группирует кейсы кандидатов. Каждый кандидат сопоставляется с тремя открытыми вакансиями через CROSS JOIN, что порождает пары кандидат–вакансия. Judge (`gpt-4.1`, `temperature=0`, production Prompt A) генерирует reference-лейблы и сохраняет их в поля `reference_*`:

| Поле | Диапазон |
|------|----------|
| `reference_role_score` | 0–30 |
| `reference_skills_score` | 0–35 |
| `reference_experience_score` | 0–20 |
| `reference_conditions_score` | 0–15 |
| `reference_score` | 0–100 |
| `reference_decision` | `match` / `no_match` |
| `reference_reason` | текст |

Каждый кандидат оценивается по всем трём вакансиям, поэтому каждый кандидат порождает ровно три записи. Скрипт [`scripts/extract_teacher_dataset.py`](../scripts/extract_teacher_dataset.py) читает reference-поля, применяет стратифицированный split и экспортирует `train.jsonl`, `validation.jsonl`, `test.jsonl` и `holdout.jsonl`.

### 1.2 Стратегия split

Датасет использует **вариант B**: исходный test set Experiment 002 сохраняется без изменений, а новые hard-negative / сбалансированные кандидаты добавляются в train, validation и holdout. Это позволяет сохранить оригинальный test set как стабильный baseline для прямого сравнения между экспериментами.

| Split | Назначение | Содержимое |
|-------|------------|------------|
| `train` | Обучение LoRA-адаптера | Исходные train-кандидаты + новые кандидаты, назначенные в train |
| `validation` | Выбор best checkpoint и early stopping | Исходные validation-кандидаты + representative новые кандидаты |
| `test` | Offline-сравнение с предыдущими экспериментами | Оригинальный test set Experiment 002, без изменений |
| `holdout` | Независимая проверка обобщения на незнакомых hard negatives | Новые кандидаты, никогда не виденные в train/validation |
| `smoke set` | Runtime API-валидация после обучения | Фиксированные positive, negative, hard-negative и edge-case запросы |

Стратификация ведётся по `case_type` (`obvious_match`, `borderline`, `obvious_no_match`). Каждый `case_code` (кандидат) целиком сохраняется в одном split; его три vacancy-записи перемещаются вместе.

### 1.3 Правила предотвращения leakage

Чтобы offline-метрики оставались доверительными, при сборе каждой версии датасета действуют следующие правила:

1. Оригинальный `test.jsonl` никогда не изменяется и не сливается в train/validation.
2. Новые `case_code` не пересекаются с существующими test или holdout кандидатами.
3. Holdout-кандидаты полностью исключены из train и validation.
4. Новые примеры не являются лексическими перефразировками существующих test-кейсов.
5. Пара кандидат–вакансия — одна запись; одна и та же пара не может оказаться и в train/validation, и в holdout.
6. Runtime smoke-кейсы не используются во время обучения или выбора checkpoint.

### 1.4 Runtime smoke set не является частью teacher dataset

Runtime smoke set — это фиксированный набор API-level проверок, запускаемых после обучения. Он валидирует генерацию JSON, positive-кейсы, obvious negatives, hard negatives, edge cases, invalid input и repeat stability. Smoke set намеренно хранится вне teacher dataset, чтобы измерять runtime-поведение, а не покрытие обучения. Результаты smoke сообщаются в отчётах по экспериментам, а не в этом датасет-отчёте.

## 2. Методология hard negatives

Hard negatives — это не произвольные сложные кейсы; это повторяемые классы ошибок, наблюдаемые в production-like matching. Experiment 003 ввёл первый систематический каталог, используемый в этом проекте.

### 2.1 Категории hard negatives HN1–HN8

| Категория | Название | Что проверяет | Пример | Урок для модели |
|-----------|----------|---------------|--------|-----------------|
| **HN-1** | Полностью нерелевантная профессия (non-IT в IT) | Снижает ли модель positive-решения на профилях без IT-компетенций? | Врач-терапевт на вакансию Prompt Engineer | Название должности и soft skills не компенсируют отсутствие доменной базы |
| **HN-2** | Смежная роль без обязательных навыков | Различает ли модель идентичные и смежные профессии? | Бизнес-аналитик с BPMN/UML, но без SQL/API, на системного аналитика | Формальная близость названий недостаточна; важны конкретные hard skills |
| **HN-3** | Совпадение по общим словам без совпадения по компетенциям | Снижает ли модель влияние лексических совпадений? | Data analyst на Prompt Engineer («аналитик» в названии) | Содержание компетенций важнее лексического сходства |
| **HN-4** | Сильный профиль в нерелевантной специализации | Не завышает ли общая сила профиля релевантность? | Сильный Python backend-разработчик на Prompt Engineer | Глубокий опыт в смежной области ≠ релевантность для целевой роли |
| **HN-5** | Одиночное совпадение навыка без основного профиля | Требует ли модель комплексного набора компетенций? | Копирайтер с базовым JSON на Prompt Engineer | Один-два совпадающих навыка не делают профиль подходящим |
| **HN-6** | Разница в уровне опыта (junior vs senior) | Учитывает ли модель уровень опыта при прочей релевантности? | Junior разработчик на senior-роль | Релевантность зависит от уровня ответственности, требуемого в вакансии |
| **HN-7** | Разница в функциональной роли (управленческая vs hands-on) | Различает ли модель управленческий и исполнительский опыт? | IT-руководитель / PM на исполнительскую роль | Управленческий опыт не заменяет hands-on навыки |
| **HN-8** | Дисбаланс soft skills и hard skills | Сохраняет ли модель баланс между soft и hard skills? | Коммьюнити-менеджер с сильными коммуникациями на техническую роль | Сильные soft skills не компенсируют отсутствие технической базы |

### 2.2 Обязательные vs желаемые категории

| Приоритет | Категории | Обоснование |
|-----------|-----------|-------------|
| **Обязательные** | HN-1, HN-2, HN-3, HN-4, HN-5, HN-8 | Покрывают failure modes, наблюденные в Experiment 002, и должны присутствовать в train |
| **Желательные** | HN-6, HN-7 | Включаются, когда находятся естественные кейсы, но не требуются для закрытия эксперимента |

### 2.3 Edge-case категории EC1 / EC3 / EC4

Edge cases калибруют границу decision и проверяют стабильность на кейсах, близких к порогу `score >= 60`.

| Категория | Название | Что проверяет | Пример | Урок для модели |
|-----------|----------|---------------|--------|-----------------|
| **EC-1** | Неоднозначные borderline-кейсы (score около 60) | Стабильна ли граница между match и no_match? | Кандидат с частичным соответствием и разными решениями по вакансиям | Порог 60 — не единственный критерий; нужен content-aware анализ |
| **EC-3** | Формально похожее название должности при несовместимом содержании | Оценивает ли модель содержание, а не только название? | «Data analyst» vs «Systems analyst» | Название должности может вводить в заблуждение |
| **EC-4** | Несоответствие по условиям при сильном профиле | Сохраняет ли модель оценку условий при сильном профиле? | Сильный кандидат с зарплатными ожиданиями вне бюджета | `conditions_score` должен работать независимо от силы профиля |

### 2.4 Почему EC-2 исключена

EC-2 «Incorrect / incomplete input» исключена из каталога датасета. Она относится к runtime input validation и API-contract testing, а не к гипотезе о влиянии состава teacher dataset на качество LoRA. Поскольку Experiment 003 варьировал только состав датасета, EC-2 была вне scope.

### 2.5 Принцип достаточности категории

Категория считается достаточно представленной не фиксированным числом примеров, а покрытием исследовательских сценариев: разные профессии, вакансии, причины отклонения и уровни опыта. Ни одна категория не должна доминировать среди новых примеров.

### 2.6 Hard-negative кандидаты, добавленные в Experiment 003

Experiment 003 добавил 11 hard-negative / edge-case кандидатов (`HRA-EVAL-V2-000101`–`HRA-EVAL-V2-000111`). Каждый кандидат порождает три записи (по одной на вакансию), давая 33 новые записи teacher dataset.

| # | case_code | Основная категория | Split | Краткое описание профиля | Должно присутствовать | Должно отсутствовать | Исследовательская цель |
|---|-----------|--------------------|-------|--------------------------|-----------------------|----------------------|------------------------|
| 1 | HRA-EVAL-V2-000101 | HN-1 | train | Врач с 7-летним клиническим опытом | Медицинский профиль, клинический опыт, soft skills | IT-профиль, prompt engineering, n8n, LLM, JSON, BPMN, SQL | Снижать positive-решения на профилях без IT-компетенций |
| 2 | HRA-EVAL-V2-000102 | HN-2 / EC-3 | train | Бизнес-аналитик с 3-летним опытом, знает BPMN/UML | BPMN, UML, требования, бизнес-процессы | Prompt engineering, n8n, LLM, deep REST API, SQL | Различать смежные роли и формальную близость названий |
| 3 | HRA-EVAL-V2-000103 | HN-3 / EC-3 | train | Data analyst со SQL, Python, BI | SQL, Python, BI, визуализация данных | Prompt engineering, n8n, LLM-интеграции, автоматизация, BPMN, UML | Снижать влияние лексических совпадений («аналитик») |
| 4 | HRA-EVAL-V2-000104 | HN-4 | train | Сильный Python backend-разработчик (5 лет), backend/API | Python, backend, API, солидный dev-опыт | Prompt engineering, n8n, LLM-интеграции, автоматизация бизнес-процессов | Сила профиля не должна компенсировать отсутствие специализации |
| 5 | HRA-EVAL-V2-000105 | HN-5 | train | Копирайтер с базовым JSON из курсов | Копирайтинг, базовый JSON | Prompt engineering, n8n, LLM, core AI/IT профиль | Одиночное совпадение навыка не должно завышать score |
| 6 | HRA-EVAL-V2-000106 | HN-8 | train | Коммьюнити-менеджер с сильными коммуникациями, организация мероприятий | Коммуникации, организация мероприятий, soft skills | Prompt engineering, n8n, LLM, JSON, BPMN, SQL, ML | Soft skills не должны компенсировать отсутствие технической базы |
| 7 | HRA-EVAL-V2-000107 | EC-1 / EC-4 | train | Middle-кандидат с частичным соответствием навыков и mismatch условий | Частичные hard skills, релевантный опыт | Полное покрытие требований, соответствие зарплаты/формата | Проверить границу 60 и сохранить scoring условий |
| 8 | HRA-EVAL-V2-000108 | HN-6 | validation | Junior Python-разработчик (1 год), базовые скрипты | Python, базовые скрипты | Senior-level prompt engineering, n8n, LLM-интеграции | Учитывать уровень опыта при прочей релевантности |
| 9 | HRA-EVAL-V2-000109 | EC-1 | validation | Borderline-кандидат с частичным соответствием роли/навыков | Некоторые hard skills, релевантный опыт | Полное покрытие всех требований | Стабилизировать решения около порога 60 |
| 10 | HRA-EVAL-V2-000110 | HN-7 | holdout | IT-менеджер / PM с управленческим опытом | Team/project/stakeholder management | Hands-on prompt engineering, n8n, BPMN/UML | Различать управленческие и hands-on роли |
| 11 | HRA-EVAL-V2-000111 | EC-4 / EC-3 | holdout | Сильный специалист в смежной области с критичным mismatch условий и формально похожим названием | Сильный ролевой/навыковый профиль | Соответствие зарплаты/формата; для EC-3 — отсутствие реальных компетенций за похожим названием | Сохранять scoring условий и оценивать содержание vs название |

Покрытие категорий в Experiment 003:

| Категория | Где представлена | Три вакансии покрыты |
|-----------|------------------|----------------------|
| HN-1 | Train (000101) + вторично в других | Yes, via 000101 |
| HN-2 | Train (000102) | Yes, via 000102 (systems analyst) |
| HN-3 | Train (000103) | Yes, via 000103 (Prompt Engineer, systems analyst) |
| HN-4 | Train (000104) | Yes, via 000104 (Prompt Engineer) |
| HN-5 | Train (000105) | Yes, via 000105 (Prompt Engineer) |
| HN-6 | Validation (000108) | Yes, via 000108 (Prompt Engineer, systems analyst) |
| HN-7 | Holdout (000110) | Yes, via 000110 (Prompt Engineer, systems analyst) |
| HN-8 | Train (000106) | Yes, via 000106 |
| EC-1 | Train (000107) + validation (000109) | Yes, via 000107 and 000109 |
| EC-3 | Train (000102, 000103) + holdout (000111) | Yes |
| EC-4 | Train (000107) + holdout (000111) | Yes |

## 3. История версий

| Версия | Эксперимент | Записей | Кандидатов | Что изменилось |
|--------|-------------|---------|------------|----------------|
| HRA-EVAL-V2 | Experiment 002 | 90 | 30 | Baseline teacher dataset; стратифицированный split 72/9/9 |
| HRA-EVAL-V3 | Experiment 003 | 123 | 41 | Добавлено 11 hard-negative / edge-case кандидатов (33 записи) и hard-negative holdout |
| HRA-EVAL-V4 | Experiment 004 | 162 | 54 | Добавлены positive/borderline кандидаты для исправления over-correction из V3; расширен test set |
| HRA-EVAL-V5-EXT | External validation | 102 | 34 | Независимый validation set, размеченный GPT-4o; нет пересечения с train/validation/test |

HRA-EVAL-V4 — датасет, описанный в этом отчёте.

## 4. Распределение по группам

### Train

- **obvious_match:** 39
- **borderline:** 42
- **obvious_no_match:** 33

### Validation

- **obvious_match:** 9
- **borderline:** 9
- **obvious_no_match:** 9

### Test

- **obvious_match:** 9
- **borderline:** 3
- **obvious_no_match:** 3

### Hard Negative Holdout

- **obvious_match:** 0
- **borderline:** 0
- **obvious_no_match:** 6

## 5. Коды кандидатов по split

### Train

```
HRA-EVAL-V2-000001, HRA-EVAL-V2-000002, HRA-EVAL-V2-000003, HRA-EVAL-V2-000004, HRA-EVAL-V2-000005, HRA-EVAL-V2-000006, HRA-EVAL-V2-000007, HRA-EVAL-V2-000008, HRA-EVAL-V2-000009, HRA-EVAL-V2-000011, HRA-EVAL-V2-000012, HRA-EVAL-V2-000013, HRA-EVAL-V2-000014, HRA-EVAL-V2-000015, HRA-EVAL-V2-000016, HRA-EVAL-V2-000017, HRA-EVAL-V2-000018, HRA-EVAL-V2-000019, HRA-EVAL-V2-000021, HRA-EVAL-V2-000022, HRA-EVAL-V2-000023, HRA-EVAL-V2-000024, HRA-EVAL-V2-000025, HRA-EVAL-V2-000026, HRA-EVAL-V2-000027, HRA-EVAL-V2-000028, HRA-EVAL-V2-000029, HRA-EVAL-V2-000101, HRA-EVAL-V2-000102, HRA-EVAL-V2-000103, HRA-EVAL-V2-000104, HRA-EVAL-V2-000107, HRA-EVAL-V2-000109, HRA-EVAL-V2-000201, HRA-EVAL-V2-000202, HRA-EVAL-V2-000203, HRA-EVAL-V2-000204, HRA-EVAL-V2-000207
```

### Validation

```
HRA-EVAL-V2-000105, HRA-EVAL-V2-000106, HRA-EVAL-V2-000108, HRA-EVAL-V2-000205, HRA-EVAL-V2-000206, HRA-EVAL-V2-000208, HRA-EVAL-V2-000209, HRA-EVAL-V2-000210, HRA-EVAL-V2-000213
```

### Test

```
HRA-EVAL-V2-000010, HRA-EVAL-V2-000020, HRA-EVAL-V2-000030, HRA-EVAL-V2-000211, HRA-EVAL-V2-000212
```

### Hard Negative Holdout

```
HRA-EVAL-V2-000110, HRA-EVAL-V2-000111
```

## 6. Borderline-кейсы (score >= 60, decision = no_match)

| case_code | vacancy_title | reference_score | reference_decision | reason |
|-----------|---------------|-----------------|--------------------|--------|
| HRA-EVAL-V2-000024 | Prompt Engineer / AI Automation Specialist | 64 | no_match | Product Manager со смежным опытом, но без ключевых AI/LLM навыков |
| HRA-EVAL-V2-000026 | Системный аналитик | 62 | no_match | QA Engineer со смежными техническими навыками, но без BPMN/аналитического опыта |
| HRA-EVAL-V2-000202 | Системный аналитик | 67 | no_match | AI Automation Specialist без SQL/BPMN и опыта постановки задач разработчикам |
| HRA-EVAL-V2-000204 | Prompt Engineer / AI Automation Specialist | 64 | no_match | Business analyst с базовым n8n/API, но без prompt engineering/LLM |
| HRA-EVAL-V2-000206 | Специалист по разметке данных | 63 | no_match | Technical writer с опытом инструкций, но без явной разметки данных и зарплата выше бюджета |
| HRA-EVAL-V2-000209 | Системный аналитик | 69 | no_match | Data analyst с prompt engineering, но без BPMN и постановки задач разработчикам |

## 7. Аудит teacher-лейблов

Все reference-лейблы в teacher dataset генерируются одним и тем же Judge workflow, чтобы LoRA-адаптер обучался на единой согласованной scoring policy.

### 7.1 Конфигурация Judge

| Атрибут | Значение |
|-----------|-------|
| Model | `gpt-4.1` |
| `temperature` | `0` |
| Prompt | Production Prompt A (см. раздел 11) |
| Output | Поля `reference_*` в PostgreSQL |

Judge с нулевой temperature снижает стохастическую вариативность: повторные вызовы для одной пары кандидат–вакансия возвращают один и тот же лейбл, что делает teacher signal детерминированным для student-модели.

### 7.2 Распределение reference-лейблов (HRA-EVAL-V4)

| Decision | Записей | Доля |
|----------|---------|------|
| `match` | 39 | 24.1% |
| `no_match` | 123 | 75.9% |
| **Итого** | **162** | **100%** |

| Диапазон score | Записей | Типичная интерпретация |
|----------------|---------|------------------------|
| 0–19 | 10 | Strong no-match |
| 20–39 | 65 | Clear no-match |
| 40–59 | 42 | Soft no-match / low borderline |
| 60–69 | 21 | High borderline или match |
| 70–100 | 24 | Confident match |
| **Итого** | **162** | — |

Статистика датасета: min score **5.0**, max score **100.0**, average **47.3**.

### 7.3 Консистентность score / decision

Каждая запись HRA-EVAL-V4 была проверена на соответствие scoring-правилам:

| Проверка | Результат |
|----------|-----------|
| `score = role_score + skills_score + experience_score + conditions_score` | ✅ 0 нарушений |
| `decision = "match"` только если `score >= 60` | ✅ 0 нарушений |
| Borderline-кейсы (`score >= 60`, `decision = no_match`) задокументированы | ✅ 6 кейсов (см. раздел 6) |
| Компонентные score внутри объявленных диапазонов | ✅ |
| Непустой `reference_reason` | ✅ |

### 7.4 Распределение decision по split

| Split | Записей | match | no_match | % match | Borderline (score ≥ 60, no_match) |
|-------|---------|-------|----------|---------|----------------------------------|
| train | 114 | 26 | 88 | 22.8% | 4 |
| validation | 27 | 6 | 21 | 22.2% | 2 |
| test | 15 | 6 | 9 | 40.0% | 0 |
| holdout | 6 | 1 | 5 | 16.7% | 0 |
| **Итого** | **162** | **39** | **123** | **24.1%** | **6** |

### 7.5 Известные ограничения Judge-лейблов

- **Single Judge.** Все reference-лейблы приходят от одной модели (`gpt-4.1`). Систематические смещения Judge наследуются LoRA-адаптером.
- **Нет inter-Judge agreement.** Нет второго Judge или человеческого аудита для разрешения разногласий.
- **Фиксированный prompt.** Для всех лейблов используется Production Prompt A; альтернативные промпты (Prompt B, Judge Prompt) не смешиваются в teacher dataset.
- **Ограниченный домен.** Лейблы покрывают три вакансии; обобщение на произвольные роли зависит от будущих версий датасета.

---

## 8. Влияние на модель

Состав teacher dataset — сильнейший драйвер поведения модели, наблюдаемый в Experiments 002–004. Гиперпараметры LoRA оставались неизменными с Experiment 002; датасет был единственной намеренно изменяемой переменной.

### 8.1 Эволюция датасета и метрики

| Датасет | Эксперимент | Записей | Ключевое изменение | `decision_accuracy` | `MAE_score` | Runtime negative smoke |
|---------|-------------|---------|--------------------|---------------------|-------------|------------------------|
| HRA-EVAL-V2 | Experiment 002 | 90 | Baseline стратифицированный датасет | 0.778 | 21.89 | ❌ Failed |
| HRA-EVAL-V3 | Experiment 003 | 123 | Добавлено 11 hard-negative / edge-case кандидатов (33 записи) + holdout | 0.667 | 22.22 | ✅ 7/7 passed |
| HRA-EVAL-V4 | Experiment 004 | 162 | Добавлены positive/borderline кандидаты для исправления over-correction из V3; расширен test set | 0.800 | 15.13 | ✅ 7/7 passed |

### 8.2 Интерпретация

- **HRA-EVAL-V2 → V3:** hard negatives решили runtime false positives, но сдвиг в сторону `no_match`-примеров вызвал over-correction: recall на genuine matches упал.
- **HRA-EVAL-V3 → V4:** добавление positive и borderline примеров для смежных ролей восстановило recall, сохранив достижения по hard negatives. Offline `decision_accuracy` выросла с 0.667 до 0.800, runtime smoke остался 7/7.
- **Dataset engineering > adapter tuning.** Поскольку параметры LoRA не менялись между Experiments 002–004, наблюдаемые различия объясняются составом датасета, а не ёмкостью модели.

### 8.3 Precision / recall trade-off

| Версия | Проблема | Evidence |
|--------|----------|----------|
| V2 | Высокая offline accuracy, но низкая runtime precision | False positive: врач → специалист по разметке данных |
| V3 | Лучшая runtime precision, но ниже recall | False negatives: системный аналитик / специалист по разметке данных — genuine matches |
| V4 | Сбалансированная precision и recall | `decision_accuracy` 0.800, runtime smoke 7/7, external validation decision accuracy 0.931 |

Эта траектория показывает, что teacher dataset должен одновременно содержать:
- hard negatives — чтобы учить, что отклонять;
- positive/borderline примеры — чтобы учить, что принимать;
- edge cases — чтобы калибровать границу decision.

### 8.4 Teacher-label mismatch на hard negatives

Не все записи, которые выглядят как hard negatives, размечены teacher как `no_match`. В HRA-EVAL-V4 11 hard-negative / edge-case кандидатов (`HRA-EVAL-V2-000101`–`HRA-EVAL-V2-000111`) дают 33 записи по всем split. Из них **5 записей (15 %)** были размечены teacher GPT-4.1 как `match` — например, business analyst на вакансию системного аналитика или data analyst на вакансию системного аналитика получили `match`, несмотря на отсутствие требуемых hard skills.

Поскольку LoRA обучается на teacher signal, она наследует эти лейблы. Это объясняет, почему LoRA иногда принимает профили, которые внешний наблюдатель классифицировал бы как hard negatives.

> **Доказательство:** список всех 33 hard-negative-like записей и 5 mismatch-записей — в [`../data/evidence/teacher_label_mismatch_v4.json`](../data/evidence/teacher_label_mismatch_v4.json).

#### Representative example: teacher-label mismatch

**Candidate:** Business Analyst, 3 года опыта, BPMN, UML, работа с требованиями и бизнес-процессами; без SQL, REST API и опыта постановки задач разработчикам.

**Vacancy:** Системный аналитик; требуется SQL, BPMN, REST API, аналитика, постановка задач разработчикам.

**Teacher label (GPT-4.1):** `match`, score 70.

**Почему этот пример важен:** Кандидат не обладает обязательными hard skills системного аналитика (SQL, REST API, постановка задач разработчикам), но teacher разметил запись как `match`. LoRA обучается на этих labels, поэтому на production-like hard negatives она наследует ту же логику и принимает смежные роли без ключевых навыков.

**Evidence:** [`../data/evidence/teacher_label_mismatch_v4.json`](../data/evidence/teacher_label_mismatch_v4.json), запись `HRA-EVAL-V2-000102`, vacancy "Системный аналитик".

---

## 9. Требования к следующей версии датасета

На основе уроков Experiments 002–004 следующая версия teacher dataset (предварительно HRA-EVAL-V5) должна решить следующее:

1. **Сохранить баланс V4.** Доля `match`-записей в train+val должна оставаться около 25–35%, чтобы избежать over-correction.
2. **Расширить покрытие hard negatives.** Добавить кейсы для недостаточно представленных failure modes (например, гибридные профили, фейковый опыт, mismatch локации + remote-only роль).
3. **Расширить разнообразие вакансий.** Включить дополнительные роли помимо трёх канонических вакансий для улучшения generalisation.
4. **Добавить human или multi-Judge audit.** Ввести второго Judge или ручную проверку borderline-кейсов для снижения inherited Judge bias.
5. **Формализовать holdout evaluation.** Перейти от holdout, используемого только для качественных runtime-проверок, к scored holdout set с category-level метриками.
6. **Сохранить leakage-правила.** Сохранить split-стратегию и правила предотвращения leakage, описанные в разделе 1.3.

---

## 10. Проверки

- ✅ Все 162 записи присутствуют.
- ✅ Нет NULL-значений.
- ✅ Assistant-сообщения полностью сформированы.
- ✅ System-сообщения заполнены (production Prompt A).
- ✅ User-сообщения заполнены (candidate + vacancy).
- ✅ Все 6 borderline-кейсов (`score >= 60`, `decision = no_match`) присутствуют в датасете.
- ✅ Консистентность score / decision проверена (0 нарушений).
- ✅ Суммы компонентных score проверены (0 нарушений).
- ✅ Используется production Prompt A (не Prompt B, не Judge Prompt).
- ✅ Используется Judge (GPT-4.1) в качестве Teacher.

## 11. System Prompt (Production Prompt A)

```
Ты HR matching assistant.

Сравни кандидата и вакансию по критериям:

1. Должность / роль — 30 баллов
2. Навыки — 35 баллов
3. Опыт — 20 баллов
4. Город / формат / зарплатные ожидания — 15 баллов

Итоговый score должен быть от 0 до 100.

Правила:
- score >= 60 → decision = "match"
- score < 60 → decision = "no_match"
- не выдумывай навыки и опыт
- если данных недостаточно, снижай score
- reason должен кратко объяснять, почему выставлен такой score

Верни строго JSON по схеме.
```

## 12. Формат assistant-сообщения

```json
{
  "role_score": 0-30,
  "skills_score": 0-35,
  "experience_score": 0-20,
  "conditions_score": 0-15,
  "score": 0-100,
  "decision": "match" | "no_match",
  "reason": "..."
}
```
