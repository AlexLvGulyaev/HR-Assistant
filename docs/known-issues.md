# Known Issues: HR Assistant

**Last Updated:** 2026-06-24

---

## Critical Issues

### KP-001: НЕСОВМЕСТИМОСТЬ metadata

**Приоритет:** 🔴 Critical

**Статус:** Open

**Дата выявления:** 2026-06-23

**Описание:**

Поле `metadata` (jsonb) в таблице `outbox` существует в БД и активно используется в `HR Delivery Worker`, но **не заполняется** в `HR Processing Worker` при создании записей в `outbox`.

**Технические детали:**

**БД:**
```sql
ALTER TABLE outbox
ADD COLUMN IF NOT EXISTS metadata jsonb;
```
Файл: `database/schema_hr_assistant.sql`, строка 354

**Delivery Worker (использование):**
```javascript
let metadata = $json.metadata || {};
if (typeof metadata === 'string') {
  try {
    metadata = JSON.parse(metadata);
  } catch (e) {
    metadata = {};
  }
}
// Использование полей:
// - tts_required
// - tts_text
// - visual_required
// - visual_prompt
// - visual_title
// - visual_score
// - visual_candidate_name
// - visual_vacancy_title
```

**Processing Worker (INSERT без metadata):**
```sql
INSERT INTO outbox (
    intake_event_id,
    candidate_id,
    channel,
    recipient,
    message_type,
    subject,
    body,
    reply_markup,
    status
    -- metadata ОТСУТСТВУЕТ!
)
VALUES (...)
```

**Последствия:**

1. **TTS не работает корректно** — `metadata.tts_required` всегда `undefined` → fallback на текст из `body`
2. **Visual generation не работает корректно** — `metadata.visual_required` всегда `undefined` → fallback на default prompt
3. **Потеря функциональности** — система не может передать дополнительные параметры для генерации мультимедиа

**Root Cause:**

Поле `metadata` было добавлено в БД (ALTER TABLE), обработка была добавлена в Delivery Worker, но INSERT-запросы в Processing Worker не были обновлены.

**Решение:**

1. Определить источник данных для metadata полей
2. Добавить заполнение metadata в Processing Worker:
   ```sql
   INSERT INTO outbox (
       ...,
       metadata
   )
   VALUES (
       ...,
       '{{ JSON.stringify($json.metadata).replace(/'/g, "''") }}'::jsonb
   )
   ```
3. Протестировать TTS и visual generation
4. Документировать формат metadata

**Требуется:**

- [ ] Определить источник metadata
- [ ] Обновить INSERT запросы в Processing Worker (5 мест)
- [ ] Протестировать TTS generation
- [ ] Протестировать Visual generation
- [ ] Документировать формат metadata в SPEC.md

---

## Medium Issues

### KP-002: BOT TOKEN В РЕПОЗИТОРИИ

**Приоритет:** ⚠️ Medium

**Статус:** ✅ Fixed

**Дата выявления:** 2026-06-23

**Дата исправления:** 2026-06-24

**Описание:**

Файл `schema_hr_assistant.sql` содержал реальный bot token в INSERT-запросе (строка 288-294).

**Исправление:**

1. ✅ Заменён реальный токен на placeholder: `REPLACE_ME_WITH_YOUR_BOT_TOKEN`
2. ✅ Добавлена документация в `DEPLOYMENT_GUIDE.md` (архитектура хранения токена, инструкция по обновлению)
3. ✅ Добавлено предупреждение в `README.md` о необходимости замены токена перед запуском

**Текущее состояние:**

```sql
INSERT INTO bot_credentials (bot_code, bot_token, description)
VALUES (
    'hr_assistant',
    'REPLACE_ME_WITH_YOUR_BOT_TOKEN',  -- ✅ Placeholder
    'HR assistant Telegram bot'
)
```

**Документация:**
- `README.md` — предупреждение о замене токена
- `DEPLOYMENT_GUIDE.md` — архитектура хранения токена, инструкция по обновлению

**Требуется:**

- [x] Заменить токен на placeholder в SQL-файле
- [x] Документировать процесс обновления токена
- [x] Добавить предупреждение в README.md

---

### KP-003: ОТСУТСТВИЕ ВЕРСИОНИРОВАНИЯ WORKFLOW

**Приоритет:** ⚠️ Medium

**Статус:** Open

**Дата выявления:** 2026-06-23

**Описание:**

Отсутствует версионирование workflow n8n. Нет механизма отката изменений.

**Последствия:**

1. **Сложность отката** — при ошибке сложно восстановить предыдущую версию
2. **Отсутствие истории изменений** — неизвестно, что менялось и когда
3. **Риск потери работы** — при ошибочном импорте можно потерять изменения

**Решение:**

1. Внедрить Git-based версионирование workflow JSON
2. Создать CHANGELOG.md для отслеживания изменений
3. Добавить теги версий в README.md

**Требуется:**

- [ ] Создать Git-репозиторий для workflow
- [ ] Добавить CHANGELOG.md
- [ ] Документировать процесс версионирования

---

## Low Issues

### KP-004: МАТЕРИАЛЫ УРОКОВ В КОРНЕ ПРОЕКТА

**Приоритет:** ℹ️ Low

**Статус:** Fixed

**Дата выявления:** 2026-06-23

**Описание:**

Материалы уроков PEd03-PEd05 находились в корне проекта.

**Последствия:**

1. Загрязнение структуры проекта
2. Смешение входных материалов и артефактов проекта

**Решение:**

Переместить в `attachments/input/`.

**Статус:** Исправлено (2026-06-23).

---

## Tracking

| ID | Приоритет | Статус | Дата |
|----|-----------|--------|------|
| KP-001 | 🔴 Critical | Open | 2026-06-23 |
| KP-002 | ⚠️ Medium | Fixed | 2026-06-24 |
| KP-003 | ⚠️ Medium | Open | 2026-06-23 |
| KP-004 | ℹ️ Low | Fixed | 2026-06-23 |

---

## References

- [PROJECT_STATE.md](PROJECT_STATE.md)
- [SPEC.md](SPEC.md)
- [README.md](../README.md)