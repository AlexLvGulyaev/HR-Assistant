# 🖼️ MEDIA_INDEX — HR Assistant

**Назначение:** реестр всех изображений кейса — витринные hero, скриншоты продукта, резерв. Фактическое содержимое каталога — 26 файлов (`raw/` — 25, `prompt_evaluation/` — 1), все зарегистрированы.

---

## 👁️ 1. Визуальный контракт

- **Витринные hero — строго по документам:** README подключает **только** `HRA_portfolio_light.png`, ARCHITECTURE — **только** `HRA_portfolio_dark.png`. Без `<picture>` и подмен по `prefers-color-scheme` — вариант закреплён за документом жёстко (решение владельца, 2026-09-15).
- **Скриншоты — UI evidence** (`report_v2_*`, `workflow.png`) показывают фактические экраны продукта и n8n; **не смешиваются с AIP artwork** (витринные hero).
- **Скриншоты подписаны** — заголовок над изображением называет экран; alt-текст описывает содержимое для доступности.
- **Архитектурные связи — Mermaid** в самих документах; PNG используется только для UI/API-свидетельств (скриншоты редактора n8n, экраны Telegram).
- **Light theme — основной evidence** для публичных документов; тёмная тема — только витринный hero.

---

## 🎨 2. Витринные hero (AIP artwork)

| Файл | Назначение |
|------|------------|
| `raw/HRA_portfolio_light.png` | Витринный hero светлой темы — **только README** (единственный документ с этим изображением) |
| `raw/HRA_portfolio_dark.png` | Витринный hero тёмной темы — **только ARCHITECTURE** (единственный документ с этим изображением) |

---

## 🖥️ 3. Скриншоты продукта (используются в документах)

### Ввод кандидата

| ID | Файл | Подпись | Где используется |
|----|------|---------|------------------|
| IMG-002 | `raw/report_v2_-002.png` | Пример текстового входящего сообщения | USER_GUIDE, E2E_SCENARIOS |
| IMG-003 | `raw/report_v2_-003.png` | Пример голосового входящего сообщения | USER_GUIDE, E2E_SCENARIOS |
| IMG-004 | `raw/report_v2_-004.png` | Пример входящего сообщения — фото резюме | USER_GUIDE, E2E_SCENARIOS |
| IMG-005 | `raw/report_v2_-005.png` | Пример входящего сообщения — PDF-файл (часть 1: текст) | USER_GUIDE, E2E_SCENARIOS |
| IMG-006 | `raw/report_v2_-006.png` | Пример входящего сообщения — PDF-файл (часть 2: файл в Telegram) | USER_GUIDE, E2E_SCENARIOS |

### Результаты обработки

| ID | Файл | Подпись | Где используется |
|----|------|---------|------------------|
| IMG-008 | `raw/report_v2_-008.png` | Карточка результата — match | USER_GUIDE |
| IMG-009 | `raw/report_v2_-009.png` | Карточка результата — no_match | USER_GUIDE |
| IMG-010 | `raw/report_v2_-010.png` | Голосовая версия результата | USER_GUIDE |
| IMG-011 | `raw/report_v2_-011.png` | Визуальная карточка кандидата | USER_GUIDE, HR_GUIDE |
| IMG-012 | `raw/report_v2_-012.png` | Пример видео-результата (по запросу) | USER_GUIDE |

### Эксплуатация

| ID | Файл | Подпись | Где используется |
|----|------|---------|------------------|
| IMG-013 | `raw/report_v2_-013.png` | Логирование обработки — успешный matching | (резерв) |
| IMG-014 | `raw/report_v2_-014.png` | Логирование ошибок | (резерв) |
| IMG-015 | `raw/report_v2_-015.png` | Workflow HR Intake — успешное выполнение сценария | SUPPORT_RUNBOOK |

### Workflow n8n (скриншоты редактора)

| ID | Файл | Подпись | Где используется |
|----|------|---------|------------------|
| IMG-016 | `raw/report_v2_-016.png` | Workflow приёма входных данных (HR Intake) | INTEGRATION_DIAGRAM, SUPPORT_RUNBOOK |
| IMG-017 | `raw/report_v2_-017.png` | Workflow обработки кандидата (Processing Worker) | INTEGRATION_DIAGRAM |
| IMG-018 | `raw/report_v2_-018.png` | Workflow доставки результата (Delivery Worker) | INTEGRATION_DIAGRAM |
| IMG-019 | `raw/report_v2_-019.png` | Workflow генерации видео (on-demand) | INTEGRATION_DIAGRAM |

---

## 🧪 4. Prompt Evaluation

| ID | Файл | Подпись | Где используется |
|----|------|---------|------------------|
| IMG-020 | `prompt_evaluation/screenshots/workflow.png` | Workflow HRA Prompt Evaluation Experiment | prompt_evaluation/WORKFLOW_IMPLEMENTATION.md |

---

## 🗃️ 5. Резерв (в документах не используется)

| ID | Файл | Подпись | Примечание |
|----|------|---------|------------|
| IMG-000 | `raw/report_v2_-000.png` | Архитектура HR-ассистента (intake / processing / delivery / video) | Заменён в README на витринный hero; архитектурная схема — Mermaid в ARCHITECTURE |
| IMG-001 | `raw/report_v2_-001.png` | ER-диаграмма базы данных | ER-схема — Mermaid в ARCHITECTURE |
| IMG-007 | `raw/report_v2_-007.png` | Нормализованный текст (JSON) из голосового сообщения | E2E-сценарии описывают нормализацию текстом |
| — | `raw/report_v2_-020.png` | Подпись не установлена | Требуется верификация содержимого человеком |

---

## 🧬 6. Изображения подсистемы finetuning

| ID | Файл | Назначение |
|----|------|------------|
| HRA-LORA-LIGHT | `raw/HRA-Lora_portfolio_light.png` | Витринный hero светлой темы материалов HRA LoRA |
| HRA-LORA-DARK | `raw/HRA-Lora_portfolio_dark.png` | Витринный hero тёмной темы материалов HRA LoRA |

Используются материалами [`finetuning/`](../../finetuning/README.md); в документацию основного контура не входят.

---

## 📊 7. Сводная таблица

| Категория | Используются | Резерв | Итого |
|-----------|--------------|--------|-------|
| Витринные hero (основной контур) | 2 | — | 2 |
| Скриншоты продукта | 11 | 4 | 15 |
| Prompt Evaluation | 1 | — | 1 |
| Витринные hero (finetuning) | 2 | — | 2 |
| **Итого** | **16** | **4** | **26** |

## 📚 8. Использование по документам

| Документ | Изображения |
|----------|-------------|
| [`README.md`](../../README.md) | HRA_portfolio_light (hero) — единственные изображения README; схемы — Mermaid |
| [`ARCHITECTURE.md`](../ARCHITECTURE.md) | HRA_portfolio_dark (hero); архитектурные и ER-схемы — Mermaid |
| [`USER_GUIDE.md`](../USER_GUIDE.md) | report_v2_-002..-006, -008..-012 |
| [`HR_GUIDE.md`](../HR_GUIDE.md) | report_v2_-011 |
| [`E2E_SCENARIOS.md`](../E2E_SCENARIOS.md) | report_v2_-002..-006 |
| [`SUPPORT_RUNBOOK.md`](../SUPPORT_RUNBOOK.md) | report_v2_-015, -016 |
| [`INTEGRATION_DIAGRAM.md`](../INTEGRATION_DIAGRAM.md) | report_v2_-016..-019 |
| [`prompt_evaluation/WORKFLOW_IMPLEMENTATION.md`](../prompt_evaluation/WORKFLOW_IMPLEMENTATION.md) | workflow.png |

## 🔄 9. История реестра

- **2026-09-15** — SCREENSHOT_INDEX.md слит в MEDIA_INDEX.md; введён визуальный контракт (AIP Light → README, Dark → ARCHITECTURE); все 26 файлов зарегистрированы; исправлена матрица использования по фактическим ссылкам в документах.
- **2026-08-22** — добавлены Portfolio-изображения HRA LoRA.
- **2026-06-25** — добавлена секция Prompt Evaluation (IMG-020).
- **2026-06-24** — полная сверка подписей всех изображений (исправлена таблица соответствия).