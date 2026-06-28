# Инструкция по модификации Workflow

**Создано:** 2026-06-28
**Workflow:** HR Processing Worker - Multi Provider Test.json
**Назначение:** Финальная архитектура для поддержки мультипровайдерного LLM в тестовом контуре

**⚠️ ВАЖНО:** Это руководство относится к экспериментальному workflow, НЕ к production.

---

## Обзор изменений

| Изменение | Количество | Детали |
|-----------|------------|--------|
| **Новые nodes** | +7 | 1 Configure LLM Provider + 3 IF Provider + 3 RunPod HTTP |
| **Изменённые nodes** | 6 | 3 Prepare Body + 3 Parse |
| **Переименованные nodes** | 3 | OpenAI HTTP nodes переименованы с суффиксом `(OpenAI)` |
| **Удалённые nodes** | -3 | Merge nodes (не нужны) |

**Итого:** 47 → 54 nodes (+7)

---

## Архитектура (Финальная)

```
Configure LLM Provider (устанавливает llm_config)
       ↓
Prepare OpenAI Body (условный response_format)
       ↓
IF: Provider? (проверяет llm_config.llm_provider)
       ↓
   OpenAI HTTP Request    ←→    RunPod HTTP Request
   (с credentials)           (без credentials)
   (с response_format)        (без response_format)
       ↓                              ↓
       │    success → Parse          │    success → Parse
       │    error   → Error handler  │    error   → Error handler
       │                              │
       └──────────┬───────────────────┘
                  ↓
           Parse Response (общий)
                  ↓
           Продолжение обработки
```

---

## Изменения в Nodes

### Новые Nodes (7 total)

| Node | Type | Count | Назначение |
|------|------|-------|------------|
| Configure LLM Provider | Code | 1 | Установка llm_config на основе провайдера |
| IF: Provider for... | IF | 3 | Выбор провайдера для каждого LLM вызова |
| LLM: ... (RunPod) | HTTP Request | 3 | RunPod API вызовы |

### Изменённые Nodes (6 total)

| Node | Изменение |
|------|-----------|
| Prepare OpenAI Body: Extract candidate JSON | Условный response_format |
| Prepare OpenAI Body: Repair candidate JSON | Условный response_format |
| Prepare OpenAI Body: Match candidate vacancy | Условный response_format |
| Parse OpenAI Candidate JSON | Использование llm_provider из config |
| Parse OpenAI Repair Candidate JSON | Использование llm_provider из config |
| Parse match JSON | Использование llm_provider из config |

### Переименованные Nodes (3 total)

| Старое имя | Новое имя |
|------------|-----------|
| LLM: Extract candidate JSON | LLM: Extract candidate JSON (OpenAI) |
| LLM: Repair candidate JSON | LLM: Repair candidate JSON (OpenAI) |
| LLM: Match candidate vacancy | LLM: Match candidate vacancy (OpenAI) |

---

## Пошаговая модификация

### Шаг 1: Добавить Node Configure LLM Provider

**Позиция:** После `IF: has pending input?`

```javascript
// Configure LLM Provider
// Provider selection: openai (default) | runpod
// Set via environment variable LLM_PROVIDER

const provider = 'runpod';  // Hardcoded для тестового workflow

const configs = {
  openai: {
    llm_provider: 'openai',
    llm_url: 'https://api.openai.com/v1/chat/completions',
    llm_model: 'gpt-4o-mini',
    llm_supports_structured_output: true,
    llm_auth_credential_id: 'pANFrhR1xZgvvzrJ'
  },
  runpod: {
    llm_provider: 'runpod',
    llm_url: 'https://bgi0g1thpts995-8000.proxy.runpod.net/v1/chat/completions',
    llm_model: 'hra-qwen',
    llm_supports_structured_output: false,
    llm_auth_credential_id: null
  }
};

const config = configs[provider];

if (!config) {
  throw new Error(`Unknown LLM provider: ${provider}. Supported: openai, runpod`);
}

return [{
  json: {
    ...$json,
    llm_config: config
  }
}];
```

**Обновить подключения:**
- `IF: has pending input?` → `Configure LLM Provider`
- `Configure LLM Provider` → `Prepare OpenAI Body: Extract candidate JSON`

---

### Шаг 2: Добавить IF, RunPod Nodes для каждого LLM вызова

Для каждого из 3 LLM вызовов (Extract, Repair, Match) добавить:

1. **IF node** перед HTTP Request
2. **RunPod HTTP Request node** (копия OpenAI, без credentials)
3. **Подключить обе ветки к Parse и error handler**

#### Паттерн подключения

```
Prepare OpenAI Body → IF: Provider?
                          ↓
              OpenAI HTTP (true)  ←→  RunPod HTTP (false)
                          ↓                    ↓
                   Parse (shared)      Parse (shared)
                          ↓                    ↓
                   Error handler        Error handler
```

**НЕ использовать Merge — обе ветки подключаются напрямую к Parse**

---

### Шаг 3: Изменить Prepare Body Nodes

Добавить условный `response_format`:

```javascript
const llmConfig = $json.llm_config;

const openai_body = {
  model: llmConfig.llm_model,
  temperature: 0,
  messages: [/* ... */]
};

// Добавить response_format только если провайдер поддерживает
if (llmConfig.llm_supports_structured_output) {
  openai_body.response_format = {
    type: 'json_schema',
    json_schema: { /* ... */ }
  };
}

return [{ json: { ...$json, llm_config: llmConfig, openai_body } }];
```

---

### Шаг 4: Создать RunPod HTTP Request Nodes

Скопировать OpenAI nodes, но:

1. Удалить `credentials`
2. Установить `authentication: none`
3. Добавить суффикс `(RunPod)` к имени

---

### Шаг 5: Обновить подключения

**Для каждого LLM вызова:**

```
Prepare Body → IF: Provider
IF: Provider (true) → OpenAI HTTP
IF: Provider (false) → RunPod HTTP
OpenAI HTTP (success) → Parse
OpenAI HTTP (error) → Build processing error context
RunPod HTTP (success) → Parse
RunPod HTTP (error) → Build processing error context
```

---

## Чек-лист тестирования

### OpenAI (по умолчанию)

1. Установить `provider = 'openai'` в Configure LLM Provider node
2. Запустить workflow с candidate input
3. Проверить:
   - LLM request отправлен на `https://api.openai.com/v1/chat/completions`
   - Model: `gpt-4o-mini`
   - `response_format` включён в request
   - Response корректно распарсен
   - Error handling работает

### RunPod

1. Установить `provider = 'runpod'` в Configure LLM Provider node
2. Запустить workflow с candidate input
3. Проверить:
   - LLM request отправлен на RunPod URL
   - Model: `hra-qwen`
   - `response_format` **НЕ** включён в request
   - Credentials не отправляются
   - Response корректно распарсен
   - Error handling работает

---

## Почему не нужен Merge?

**Проблема:** Merge nodes ожидают данные из обоих входов одновременно. Для взаимоисключающих веток (IF node) только одна ветка имеет данные в каждый момент времени.

**Решение:** Подключить обе ветки напрямую к одному downstream node (Parse). n8n обрабатывает это корректно — только данные активной ветки передаются дальше.

**Преимущества:**
- Проще архитектура
- Нет ожидания отсутствующего входа
- Нет потери данных
- Чище обработка ошибок

---

## Изменённые файлы

| Файл | Изменение |
|------|-----------|
| `workflows/HR Processing Worker.json` | Production workflow (только OpenAI) |
| `workflows/HR Processing Worker - Multi Provider Test.json` | Test workflow (RunPod hardcoded) |
| `docs/MULTI_PROVIDER_ARCHITECTURE.md` | Этот документ |
| `docs/WORKFLOW_MODIFICATION_GUIDE.md` | Этот документ |
| `workflows/llm-provider-config.js` | Модуль конфигурации |
| `docs/CHANGE_LOG.md` | Версия 2.2.0 |

---

## Инструкции по откату

Если возникнут проблемы:

1. Установить `provider = 'openai'` в Configure LLM Provider node (default)
2. Импортировать предыдущую версию workflow
3. Нет изменений в БД для отката

---

## Ссылки

- [MULTI_PROVIDER_ARCHITECTURE.md](MULTI_PROVIDER_ARCHITECTURE.md) — Обзор архитектуры
- [llm-provider-config.js](../workflows/llm-provider-config.js) — Модуль конфигурации
- [n8n IF Node](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.if/)
- [EXPERIMENTAL_ML_PIPELINE.md](EXPERIMENTAL_ML_PIPELINE.md) — Архитектура экспериментального ML-контура