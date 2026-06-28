# Мультипровайдерная LLM Архитектура

**Создано:** 2026-06-28
**Статус:** Инженерный стенд для тестирования
**Автор:** AI Automation Portfolio Lab

---

## Обзор

Этот документ описывает архитектуру для тестирования нескольких LLM-провайдеров в HR Assistant.

**⚠️ ВАЖНО: Это НЕ production workflow.**

Workflow `HR Processing Worker - Multi Provider Test` является **инженерным стендом**, созданным исключительно для:
- Тестирования различных LLM-провайдеров (OpenAI, RunPod)
- Валидации LoRA-адаптеров в runtime
- Проведения smoke-тестов перед развёртыванием в production

**Этот workflow НЕ используется в production.** Production workflow — `HR Processing Worker.json`, который использует только OpenAI.

---

## Требования

1. **OpenAI (production)** — используется в production workflow
2. **RunPod (test)** — используется для тестирования LoRA-адаптеров
3. **Отдельные workflow** — production и test изолированы
4. **Модуль конфигурации** — централизованная конфигурация провайдеров
5. **Условный response_format** — зависит от возможностей провайдера

---

## Production vs Test Architecture

### Production Workflow: HR Processing Worker.json

| Аспект | Значение |
|--------|----------|
| **Workflow** | HR Processing Worker.json |
| **LLM Provider** | OpenAI only |
| **Model** | gpt-4o-mini |
| **Structured Output** | ✅ json_schema |
| **Authentication** | n8n credentials |
| **Purpose** | Обработка реальных запросов кандидатов |
| **Status** | ✅ Production-ready |

### Test Workflow: HR Processing Worker - Multi Provider Test.json

| Аспект | Значение |
|--------|----------|
| **Workflow** | HR Processing Worker - Multi Provider Test.json |
| **LLM Provider** | RunPod (hardcoded) |
| **Model** | hra-qwen (Qwen + LoRA adapter) |
| **Structured Output** | ⚠️ Experimental |
| **Authentication** | None (RunPod proxy endpoint) |
| **Purpose** | Инженерный стенд для LoRA smoke validation |
| **Status** | ⚠️ Experimental, NOT production |

**Почему отдельные workflow?**

1. **Изоляция:** Тестирование новых моделей не должно влиять на production
2. **Безопасность:** RunPod endpoint не имеет production-аутентификации
3. **Ясность:** Чёткое разделение между production и экспериментальным кодом
4. **Гибкость:** Test workflow может иметь экспериментальные функции

**Почему hardcoded RunPod в test workflow?**

Test workflow специально создан для тестирования LoRA-адаптеров. Провайдер hardcoded как 'runpod' для упрощения smoke-тестирования. IF-ноды остаются в workflow для будущей расширяемости.

---

## Поддерживаемые провайдеры

### OpenAI (по умолчанию)

| Параметр | Значение |
|----------|----------|
| **URL** | `https://api.openai.com/v1/chat/completions` |
| **Model** | `gpt-4o-mini` |
| **Auth** | OpenAI API credential (`pANFrhR1xZgvvzrJ`) |
| **Structured Output** | ✅ Поддерживается (`json_schema`) |
| **Error Handling** | ✅ Подключено к `Build processing error context` |

### RunPod

| Параметр | Значение |
|----------|----------|
| **URL** | `https://bgi0g1thpts995-8000.proxy.runpod.net/v1/chat/completions` |
| **Model** | `hra-qwen` |
| **Auth** | None (`authentication: none`) |
| **Structured Output** | ❌ Не поддерживается |
| **Error Handling** | ✅ Подключено к `Build processing error context` |

---

## Архитектура

### Паттерн прямого подключения (Production-Ready)

```
Configure LLM Provider
       ↓
Prepare OpenAI Body (conditional response_format)
       ↓
IF: Provider?
       ↓
   OpenAI HTTP Request    ←→    RunPod HTTP Request
   (with credentials)           (no credentials)
   (with response_format)        (no response_format)
       ↓                              ↓
       │    success → Parse          │    success → Parse
       │    error   → Error handler  │    error   → Error handler
       │                              │
       └──────────┬───────────────────┘
                  ↓
           Parse Response (shared)
                  ↓
           Common Processing
```

### Почему прямое подключение (без Merge)?

**Проблема:** Merge-ноды предназначены для объединения нескольких активных входов. Для взаимоисключающих веток (IF node) только одна ветка имеет данные в каждый момент времени. Использование Merge либо:
- Ждёт второй вход (который никогда не придёт) → timeout/зависание
- Теряет данные из активной ветки

**Решение:** Подключить обе ветки напрямую к одному downstream node (Parse). n8n автоматически обрабатывает это — только данные активной ветки передаются дальше.

**Поведение n8n:** Когда IF node направляет в одну из двух веток, только эта ветка выполняется. Другая ветка не produces output. Обе ветки могут безопасно подключаться к одному downstream node без конфликта.

---

## Что дублируется?

**Транспортный слой (6 nodes):**
- 3 OpenAI HTTP Request nodes (с credentials, с response_format)
- 3 RunPod HTTP Request nodes (без credentials, без response_format)

**Вспомогательные nodes (3 nodes):**
- 3 IF nodes для выбора провайдера

**НЕ дублируется:**
- ~~3 Merge nodes~~ (не нужны для взаимоисключающих веток)

---

## Что НЕ дублируется?

**Бизнес-логика (9 nodes):**
- 3 Prepare Body nodes (условный `response_format` на основе `llm_config`)
- 3 Parse nodes (общая обработка ответа для обоих провайдеров)
- 1 Configure LLM Provider node
- Вся последующая обработка (validation, database, Telegram, etc.)

**Обработка ошибок:**
- OpenAI и RunPod используют **общие** обработчики ошибок
- `Build processing error context: Extract` для Extract candidate JSON
- `Build processing error context: Repair` для Repair candidate JSON
- `Build processing error context: Match` для Match candidate vacancy

---

## Детали реализации

### Node: Configure LLM Provider

```javascript
// Configure LLM Provider
// Provider selection: openai (default) | runpod
// Set via environment variable LLM_PROVIDER

const provider = 'runpod';

const configs = {
  openai: {
    llm_provider: 'openai',
    llm_url: 'https://api.openai.com/v1/chat/completions',
    llm_model: 'gpt-4o-mini',
    llm_supports_structured_output: true,
    llm_auth_credential_id: null
  },
  runpod: {
    llm_provider: 'runpod',
    llm_url: 'https://khu0q820y5ssqu-8000.proxy.runpod.net/v1/chat/completions',
    llm_model: 'hra-qwen',
    llm_supports_structured_output: true,
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

### Node: Prepare Body (условный response_format)

```javascript
// Get LLM provider configuration
const llmConfig = $json.llm_config;

// Build request body
const openai_body = {
  model: llmConfig.llm_model,
  temperature: 0,
  messages: [
    { role: 'system', content: '...' },
    { role: 'user', content: '...' }
  ]
};

// Add response_format only if provider supports it
if (llmConfig.llm_supports_structured_output) {
  openai_body.response_format = {
    type: 'json_schema',
    json_schema: { ... }
  };
}

return [{ json: { ...$json, llm_config: llmConfig, openai_body } }];
```

### Node: IF: Provider

```javascript
// Check provider
$json.llm_config.llm_provider === 'openai'
```

- **True** → OpenAI HTTP Request (с credentials, с response_format)
- **False** → RunPod HTTP Request (без credentials, без response_format)

### Обработка ошибок

Обе ветки подключаются к **общему** обработчику ошибок:

```
OpenAI HTTP Request
  success → Parse
  error   → Build processing error context

RunPod HTTP Request
  success → Parse
  error   → Build processing error context
```

---

## Переключение провайдеров

### На RunPod

```javascript
// В Configure LLM Provider node
const provider = 'runpod';
```

### На OpenAI (по умолчанию)

```javascript
// В Configure LLM Provider node
const provider = 'openai';
```

---

## Расширяемость

### Добавление нового провайдера (например, Anthropic Claude)

1. **Добавить конфигурацию** в `Configure LLM Provider`:

```javascript
anthropic: {
  llm_provider: 'anthropic',
  llm_url: 'https://api.anthropic.com/v1/messages',
  llm_model: 'claude-3-5-sonnet-20241022',
  llm_supports_structured_output: true,
  llm_auth_credential_id: 'ANTHROPIC_CREDENTIAL_ID'
}
```

2. **Добавить IF branch** для выбора провайдера
3. **Добавить HTTP Request node** для Anthropic
4. **Подключить Anthropic HTTP Request** к Parse (success) и error handler (error)

**НЕ требуется:**
- ~~Добавить Merge node~~ (не нужно)
- Изменять бизнес-логику
- Изменять database queries
- Изменять Telegram processing

**Требуемые изменения:**
- ✅ Конфигурация (1 node)
- ✅ IF condition (3 nodes)
- ✅ HTTP Request node (3 nodes)
- ✅ Error handling connections (уже общие)

---

## Соответствие принципу Open/Closed

**Открыто для расширения:**
- Добавление новых провайдеров требует только конфигурацию + изменения транспортного слоя

**Закрыто для модификации:**
- Бизнес-логика остаётся без изменений
- Database queries без изменений
- Telegram integration без изменений
- JSON parsing без изменений
- Matching algorithms без изменений

---

## Тестирование

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

## Изменённые файлы

| Файл | Изменение |
|------|-----------|
| `workflows/HR Processing Worker.json` | Production workflow (только OpenAI) |
| `workflows/HR Processing Worker - Multi Provider Test.json` | Test workflow (RunPod hardcoded) |
| `docs/MULTI_PROVIDER_ARCHITECTURE.md` | Этот документ |
| `docs/WORKFLOW_MODIFICATION_GUIDE.md` | Инструкция по модификации |
| `workflows/llm-provider-config.js` | Модуль конфигурации |
| `docs/CHANGE_LOG.md` | Версия 2.2.0 |

---

## Риски и ограничения

### 1. Стабильность RunPod endpoint

**Риск:** RunPod endpoint URL может измениться.

**Митигация:** Перенести в переменную окружения:
```javascript
llm_url: $env.RUNPOD_URL || 'https://...'
```

### 2. Обработка ошибок (РЕШЕНО)

**Статус:** ✅ OpenAI и RunPod error outputs подключены к общим обработчикам ошибок.

### 3. Мониторинг

**Текущее:** Нет логирования выбора провайдера.

**Улучшение:** Добавить логирование:
```javascript
console.log(`LLM Provider: ${provider}`);
```

---

## Ссылки

- [OpenAI Chat Completions API](https://platform.openai.com/docs/api-reference/chat)
- [OpenAI Structured Outputs](https://platform.openai.com/docs/guides/structured-outputs)
- [RunPod Serverless Endpoints](https://docs.runpod.io/serverless-endpoints/)
- [n8n HTTP Request Node](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.httprequest/)
- [n8n IF Node](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.if/)
- [EXPERIMENTAL_ML_PIPELINE.md](EXPERIMENTAL_ML_PIPELINE.md) — Архитектура экспериментального ML-контура