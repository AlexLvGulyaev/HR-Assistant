# Screenshot Index: HR Assistant

**Last Updated:** 2026-06-24
**Source:** PEm05 HR-ассистент V2 (полный отчет по проекту).pdf

---

## Extracted Images

### Appendix 1 — Архитектура системы

| ID | File | Page | Caption |
|----|------|------|---------|
| IMG-000 | `raw/report_v2_-000.png` | - | Рисунок 1 — Архитектура HR-ассистента с разделением на intake, processing, delivery и on-demand video workflow |
| IMG-001 | `raw/report_v2_-001.png` | - | ER-диаграмма базы данных HR-ассистента |

---

### Appendix 2 — Структура базы данных

*Примечание: Изображения таблиц БД и связей не были извлечены из PDF.*

---

### Appendix 3 — Примеры входных данных

| ID | File | Page | Caption |
|----|------|------|---------|
| IMG-002 | `raw/report_v2_-002.png` | - | Рисунок 3.1 — Пример текстового входящего сообщения. Мария Аверкиева |
| IMG-003 | `raw/report_v2_-003.png` | - | Рисунок 3.2 — Пример голосового входящего сообщения |
| IMG-004 | `raw/report_v2_-004.png` | - | Рисунок 3.3 — Пример входящего сообщения в формате фотографии резюме. Сергей Ковалев |
| IMG-005 | `raw/report_v2_-005.png` | - | Рисунок 3.4 — Пример входящего сообщения в формате pdf-файла (часть 1: текст из PDF). Екатерина Смирнова |
| IMG-006 | `raw/report_v2_-006.png` | - | Рисунок 3.4 — Пример входящего сообщения в формате pdf-файла (часть 2: изображение загруженного файла в Telegram). Екатерина Смирнова |
| IMG-007 | `raw/report_v2_-007.png` | - | Рисунок 3.5 — Пример нормализованного текста (JSON), извлеченного из изображения рис. 3.3 |

---

### Appendix 4 — Примеры результатов обработки

| ID | File | Page | Caption |
|----|------|------|---------|
| IMG-008 | `raw/report_v2_-008.png` | - | Рисунок 4.1 — Карточка результата при успешном сопоставлении (match) |
| IMG-009 | `raw/report_v2_-009.png` | - | Рисунок 4.2 — Карточка результата при неуспешном сопоставлении (no_match) |
| IMG-010 | `raw/report_v2_-010.png` | - | Рисунок 4.3 — Голосовая версия результата |
| IMG-011 | `raw/report_v2_-011.png` | - | Рисунок 4.4 — Визуальная карточка кандидата |
| IMG-012 | `raw/report_v2_-012.png` | - | Рисунок 4.5 — Пример видео-результата (по запросу) |

---

### Appendix 5 — Логирование

| ID | File | Page | Caption |
|----|------|------|---------|
| IMG-013 | `raw/report_v2_-013.png` | - | Рисунок 5.1 — Пример логирования обработки резюме с успешным сопоставлением |
| IMG-014 | `raw/report_v2_-014.png` | - | Рисунок 5.2 — Пример логирования ошибок |

---

### Appendix 7 — Сценарии тестирования

| ID | File | Page | Caption |
|----|------|------|---------|
| IMG-015 | `raw/report_v2_-015.png` | - | Рисунок 7.1 — Workflow HR Intake, успешное выполнение сценария с match анкеты |

---

### Appendix 8 — Примеры workflow (n8n)

| ID | File | Page | Caption |
|----|------|------|---------|
| IMG-016 | `raw/report_v2_-016.png` | - | Рисунок 8.1 — Workflow приёма входных данных (HR Intake) |
| IMG-017 | `raw/report_v2_-017.png` | - | Рисунок 8.2 — Workflow обработки кандидата (Processing Worker) |
| IMG-018 | `raw/report_v2_-018.png` | - | Рисунок 8.3 — Workflow доставки результата (Delivery Worker) |
| IMG-019 | `raw/report_v2_-019.png` | - | Рисунок 8.4 — Workflow генерации видео (on-demand) |

---

## Image Usage Matrix

### By APL Document

| Document | Images | Purpose |
|----------|--------|---------|
| **README.md** | IMG-000 | Архитектура системы |
| **ARCHITECTURE.md** | IMG-000, IMG-001 | Архитектура, ER-диаграмма |
| **USER_GUIDE.md** | IMG-002–IMG-012 | Примеры ввода/вывода |
| **E2E_SCENARIOS.md** | IMG-002, IMG-007, IMG-008 | Примеры сценариев |
| **WORKFLOWS.md** | IMG-016–IMG-019 | Workflow-схемы |

### By Category

| Category | Images | Count |
|----------|--------|-------|
| ARCHITECTURE | IMG-000, IMG-001 | 2 |
| USER_GUIDE (input) | IMG-002–IMG-007 | 6 |
| USER_GUIDE (output) | IMG-008–IMG-012 | 5 |
| LOGS | IMG-013, IMG-014 | 2 |
| TESTING | IMG-015 | 1 |
| WORKFLOWS | IMG-016–IMG-019 | 4 |

---

## Notes

1. **Извлечение изображений:** Выполнено с помощью `pdfimages -png`
2. **Нумерация:** Соответствует порядку появления в PDF (000–019)
3. **Страницы:** Не указаны из-за отсутствия исходного PDF
4. **Назначение:** Определено по смысловому содержанию изображений
5. **Имена:** Добавлены для персонифицированных примеров (Мария Аверкиева, Сергей Ковалев, Екатерина Смирнова)

---

---

## Prompt Evaluation Screenshots

| ID | File | Caption |
|----|------|---------|
| IMG-020 | `prompt_evaluation/screenshots/workflow.png` | Workflow HRA Prompt Evaluation Experiment |

**Usage:**
- [docs/prompt_evaluation/WORKFLOW_IMPLEMENTATION.md](../prompt_evaluation/WORKFLOW_IMPLEMENTATION.md)

---

## Corrections History

**2026-06-25:**
- Добавлена секция Prompt Evaluation Screenshots
- IMG-020: Workflow HRA Prompt Evaluation Experiment

**2026-06-24:**
- Исправлена полная таблица соответствия после проверки всех изображений
- IMG-002: Текстовое сообщение (Мария Аверкиева), было "Таблица intake_events"
- IMG-003: Голосовое сообщение, было "Таблицы candidates"
- IMG-004: Фото резюме (Сергей Ковалев), было "Связи БД"
- IMG-005: PDF часть 1 (Екатерина Смирнова), было "Текстовый ввод"
- IMG-006: PDF часть 2 (Екатерина Смирнова), было "Голосовой ввод"
- IMG-007: Нормализованный JSON, было "Фото резюме"
- IMG-008: Результат match, было "PDF-файл"
- IMG-009: Результат no_match, было "Нормализованный JSON"
- IMG-010: Голосовая версия, было "Результат match"
- IMG-011: Визуальная карточка, было "Результат no_match"
- IMG-012: Видео-результат, было "Голосовая версия"
- IMG-013: Логи обработки (match), было "Визуальная карточка"
- IMG-014: Логи ошибок, было "Видео-результат"
- IMG-015: Workflow тестирование, было "Структура логирования"
- IMG-016: Workflow HR Intake, было "Пример логов"
- IMG-017: Workflow Processing, было "Workflow HR Intake"
- IMG-018: Workflow Delivery, было "Workflow Processing"
- IMG-019: Workflow Video, было "Workflow Delivery"