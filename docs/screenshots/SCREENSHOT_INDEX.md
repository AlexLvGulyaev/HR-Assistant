# Screenshot Index: HR Assistant

**Last Updated:** 2026-06-23
**Source:** PEm05 HR-ассистент V2 (полный отчет по проекту).pdf

---

## Extracted Images

### Appendix 1 — Архитектурная схема системы

| ID | File | Page | Caption | Purpose |
|----|------|------|---------|---------|
| IMG-001 | `raw/report_v2_-000.png` | 49 | Архитектурная схема системы | ARCHITECTURE — общая архитектура HR-ассистента |

---

### Appendix 2 — Структура базы данных

| ID | File | Page | Caption | Purpose |
|----|------|------|---------|---------|
| IMG-002 | `raw/report_v2_-001.png` | 52 | ER-диаграмма базы данных HR-ассистента | DATABASE — структура таблиц |
| IMG-003 | `raw/report_v2_-002.png` | 54 | Таблица intake_events | DATABASE — схема intake_events |
| IMG-004 | `raw/report_v2_-003.png` | 55 | Таблицы candidate_inputs/candidates | DATABASE — схема таблиц кандидатов |
| IMG-005 | `raw/report_v2_-004.png` | 55 | Связи между таблицами | DATABASE — ER-диаграмма связей |

---

### Appendix 3 — Примеры входных данных

| ID | File | Page | Caption | Purpose |
|----|------|------|---------|---------|
| IMG-006 | `raw/report_v2_-005.png` | 56 | Рисунок 3.1 — Пример текстового входящего сообщения | USER_GUIDE — текстовый ввод |
| IMG-007 | `raw/report_v2_-006.png` | 56 | Рисунок 3.2 — Пример голосового входящего сообщения | USER_GUIDE — голосовой ввод |
| IMG-008 | `raw/report_v2_-007.png` | 57 | Рисунок 3.3 — Пример входящего сообщения в формате фотографии резюме | USER_GUIDE — изображение |
| IMG-009 | `raw/report_v2_-008.png` | 58 | Рисунок 3.4 — Пример входящего сообщения в формате pdf-файла | USER_GUIDE — документ |
| IMG-010 | `raw/report_v2_-009.png` | 59 | Рисунок 3.4 — Нормализованный текст (JSON) | ARCHITECTURE — формат данных |

---

### Appendix 4 — Примеры результатов обработки

| ID | File | Page | Caption | Purpose |
|----|------|------|---------|---------|
| IMG-011 | `raw/report_v2_-010.png` | 59 | Рисунок 4.1 — Карточка результата при успешном сопоставлении (match) | USER_GUIDE — результат match |
| IMG-012 | `raw/report_v2_-011.png` | 60 | Рисунок 4.2 — Карточка результата при неуспешном сопоставлении (no_match) | USER_GUIDE — результат no_match |
| IMG-013 | `raw/report_v2_-012.png` | 60 | Рисунок 4.3 — Голосовая версия результата | USER_GUIDE — TTS |
| IMG-014 | `raw/report_v2_-013.png` | 61 | Рисунок 4.4 — Визуальная карточка кандидата | USER_GUIDE — visual card |
| IMG-015 | `raw/report_v2_-014.png` | 61 | Рисунок 4.5 — Пример видео-результата | USER_GUIDE — video |

---

### Appendix 5 — Логи обработки

| ID | File | Page | Caption | Purpose |
|----|------|------|---------|---------|
| IMG-016 | `raw/report_v2_-015.png` | 62 | Структура логирования | ARCHITECTURE — логи |
| IMG-017 | `raw/report_v2_-016.png` | 62 | Пример логов обработки | ARCHITECTURE — пример логов |

---

### Appendix 7 — Сценарии тестирования

| ID | File | Page | Caption | Purpose |
|----|------|------|---------|---------|
| IMG-018 | `raw/report_v2_-017.png` | 68 | Рисунок 7.1 — Workflow HR Intake, успешное выполнение сценария с match | WORKFLOWS — тестирование |

---

### Appendix 8 — Примеры workflow (n8n)

| ID | File | Page | Caption | Purpose |
|----|------|------|---------|---------|
| IMG-019 | `raw/report_v2_-018.png` | 69 | Рисунок 8.1 — Workflow приёма входных данных (HR Intake) | WORKFLOWS — HR Intake |
| IMG-020 | `raw/report_v2_-019.png` | 70 | Рисунок 8.2 — Workflow обработки кандидата (Processing Worker) | WORKFLOWS — Processing Worker |

**Примечание:** Изображения Workflow Delivery Worker и Video Worker отсутствуют в исходном PDF.

---

## Image Usage Matrix

### By APL Document

| Document | Images | Coverage |
|----------|--------|----------|
| **README.md** | IMG-001 | Архитектура |
| **ARCHITECTURE.md** | IMG-001, IMG-002, IMG-016, IMG-017 | Схема, БД, логи |
| **USER_GUIDE.md** | IMG-006–IMG-015 | Все примеры ввода/вывода |
| **DATABASE.md** | IMG-002–IMG-005, IMG-010 | ER-диаграмма, схемы таблиц |
| **WORKFLOWS.md** | IMG-018–IMG-020 | Workflow-схемы |
| **SPEC.md** | IMG-001, IMG-010 | Общая архитектура, формат данных |

### By Category

| Category | Images | Count |
|----------|--------|-------|
| ARCHITECTURE | IMG-001, IMG-002, IMG-016, IMG-017 | 4 |
| DATABASE | IMG-002–IMG-005, IMG-010 | 4 |
| USER_GUIDE | IMG-006–IMG-015 | 10 |
| WORKFLOWS | IMG-018–IMG-020 | 3 |

---

## Source Documents

| Document | Type | Pages | Images | Content |
|----------|------|-------|--------|---------|
| PEm05 HR-ассистент V2 (полный отчет).pdf | Full Report | 75 | 20 | Полная проектная документация |
| PEm05 HR-ассистент V2 vs V1 и зоны роста.pdf | Comparison | 5 | 0 | Сравнительный анализ V1/V2 |

---

## Notes

1. **Извлечение изображений:** Выполнено с помощью `pdfimages -png`
2. **Нумерация:** Соответствует порядку появления в PDF (000–019)
3. **Страницы:** Указаны по PDF-нумерации (начиная с 1)
4. **Назначение:** Определено по смыслу иллюстрации и контексту в документе

---

## Recommendations

### Для README.md
- IMG-001 (архитектура) — основной продающий элемент

### Для USER_GUIDE.md
- IMG-006–IMG-009 — все примеры ввода
- IMG-011–IMG-015 — все примеры вывода

### Для ARCHITECTURE.md
- IMG-001 — общая схема
- IMG-002–IMG-005 — структура БД
- IMG-016–IMG-017 — логирование

### Для INTEGRATION_DIAGRAM.md
- IMG-019–IMG-020 — workflow-схемы

### Для SUPPORT_RUNBOOK.md
- IMG-016–IMG-017 — логи (при наличии)