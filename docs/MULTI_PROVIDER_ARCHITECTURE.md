# Multi-Provider LLM Architecture

**Created:** 2026-06-28
**Status:** Engineering Test Stand
**Author:** AI Automation Portfolio Lab

---

## Overview

This document describes the architecture for testing multiple LLM providers in HR Assistant.

**⚠️ IMPORTANT: This is NOT a production workflow.**

The `HR Processing Worker - Multi Provider Test` workflow is an **engineering test stand** created exclusively for:
- Testing different LLM providers (OpenAI, RunPod)
- Validating LoRA adapters in runtime
- Conducting smoke tests before production deployment

**This workflow is NOT used in production.** The production workflow is `HR Processing Worker.json` which uses only OpenAI.

## Requirements

1. **OpenAI (production)** — used in production workflow
2. **RunPod (test)** — used for testing LoRA adapters
3. **Separate workflows** — production and test are isolated
4. **Configuration module** — centralized provider configuration
5. **Conditional response_format** — depends on provider capabilities

---

## Production vs Test Architecture

### Production Workflow: HR Processing Worker.json

| Aspect | Value |
|--------|-------|
| **Workflow** | HR Processing Worker.json |
| **LLM Provider** | OpenAI only |
| **Model** | gpt-4o-mini |
| **Structured Output** | ✅ json_schema |
| **Authentication** | n8n credentials |
| **Purpose** | Processing real candidate requests |
| **Status** | ✅ Production-ready |

### Test Workflow: HR Processing Worker - Multi Provider Test.json

| Aspect | Value |
|--------|-------|
| **Workflow** | HR Processing Worker - Multi Provider Test.json |
| **LLM Provider** | RunPod (hardcoded) |
| **Model** | hra-qwen (Qwen + LoRA adapter) |
| **Structured Output** | ⚠️ Experimental |
| **Authentication** | None (RunPod proxy endpoint) |
| **Purpose** | Engineering test stand for LoRA smoke validation |
| **Status** | ⚠️ Experimental, NOT production |

**Why separate workflows?**

1. **Isolation:** Testing LoRA adapters must not affect production
2. **Safety:** RunPod endpoint has no production authentication
3. **Clarity:** Clear separation between production and experimental code
4. **Flexibility:** Test workflow can have experimental features

**Why hardcoded RunPod in test workflow?**

The test workflow is specifically designed for LoRA adapter testing. The provider is hardcoded as 'runpod' to simplify smoke testing. The IF nodes remain in the workflow for future extensibility, but currently only the RunPod branch is active.

---

## Supported Providers

### OpenAI (default)

| Parameter | Value |
|-----------|-------|
| **URL** | `https://api.openai.com/v1/chat/completions` |
| **Model** | `gpt-4o-mini` |
| **Auth** | OpenAI API credential (`pANFrhR1xZgvvzrJ`) |
| **Structured Output** | ✅ Supported (`json_schema`) |
| **Error Handling** | ✅ Connected to `Build processing error context` |

### RunPod

| Parameter | Value |
|-----------|-------|
| **URL** | `https://bgi0g1thpts995-8000.proxy.runpod.net/v1/chat/completions` |
| **Model** | `hra-qwen` |
| **Auth** | None (`authentication: none`) |
| **Structured Output** | ❌ Not supported |
| **Error Handling** | ✅ Connected to `Build processing error context` |

---

## Architecture

### Direct Connection Pattern (Production-Ready)

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

### Why Direct Connection (No Merge)?

**Problem:** Merge nodes are designed for combining multiple active inputs. For mutually exclusive branches (IF node), only one branch will have data at a time. Using Merge would either:
- Wait for the second input (never arrives) → timeout/hang
- Lose data from the active branch

**Solution:** Connect both branches directly to the same downstream node (Parse). n8n automatically handles this correctly - only the active branch's data flows downstream.

**n8n Behavior:** When an IF node routes to one of two branches, only that branch executes. The other branch produces no output. Both branches can safely connect to the same downstream node without conflict.

---

## What is Duplicated?

**Transport layer (6 nodes):**
- 3 OpenAI HTTP Request nodes (with credentials, with response_format)
- 3 RunPod HTTP Request nodes (no credentials, no response_format)

**Supporting nodes (3 nodes):**
- 3 IF nodes for provider selection

**NOT duplicated:**
- ~~3 Merge nodes~~ (not needed for mutually exclusive branches)

---

## What is NOT Duplicated?

**Business logic (9 nodes):**
- 3 Prepare Body nodes (conditional `response_format` based on `llm_config`)
- 3 Parse nodes (common response processing for both providers)
- 1 Configure LLM Provider node
- All downstream processing (validation, database, Telegram, etc.)

**Error handling:**
- Both OpenAI and RunPod use the **same** error handlers
- `Build processing error context: Extract` for Extract candidate JSON
- `Build processing error context: Repair` for Repair candidate JSON
- `Build processing error context: Match` for Match candidate vacancy

---

## Workflow Nodes Summary

### Total Node Count

**Before:** 47 nodes
**After:** 54 nodes
**Added:** +7 nodes

### New Nodes Added

| Node Type | Count | Purpose |
|-----------|-------|---------|
| Configure LLM Provider | 1 | Set llm_config based on `$env.LLM_PROVIDER` |
| IF: Provider for... | 3 | Provider selection for each LLM call |
| HTTP Request (RunPod) | 3 | RunPod API calls (no credentials, no response_format) |

**NOT added:**
- ~~Merge nodes~~ (not needed for mutually exclusive branches)

### Modified Nodes

| Node | Modification |
|------|--------------|
| Prepare OpenAI Body (3) | Conditional `response_format` based on `llm_config.llm_supports_structured_output` |
| Parse (3) | Use `llm_provider` from config for logging |
| OpenAI HTTP (3) | Renamed to `(OpenAI)`, URL from `llm_config.llm_url` |

---

## Implementation Details

### Configure LLM Provider Node

```javascript
const provider = ($env.LLM_PROVIDER || 'openai').toLowerCase();

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

return [{ json: { ...$json, llm_config: config } }];
```

### Prepare Body Node (Conditional response_format)

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

return [{ json: { ...$json, openai_body } }];
```

### IF: Provider Node

```javascript
// Check provider
$json.llm_config.llm_provider === 'openai'
```

- **True** → OpenAI HTTP Request (with credentials, with response_format)
- **False** → RunPod HTTP Request (no credentials, no response_format)

### Error Handling

Both branches connect to the **same** error handler:

```
OpenAI HTTP Request
  success → Parse
  error   → Build processing error context

RunPod HTTP Request
  success → Parse
  error   → Build processing error context
```

---

## Switching Providers

### To RunPod

```bash
export LLM_PROVIDER=runpod
```

### To OpenAI (default)

```bash
export LLM_PROVIDER=openai
# or leave unset (defaults to openai)
```

---

## Extensibility

### Adding New Provider (e.g., Anthropic Claude)

1. **Add configuration** in `Configure LLM Provider`:

```javascript
anthropic: {
  llm_provider: 'anthropic',
  llm_url: 'https://api.anthropic.com/v1/messages',
  llm_model: 'claude-3-5-sonnet-20241022',
  llm_supports_structured_output: true,
  llm_auth_credential_id: 'ANTHROPIC_CREDENTIAL_ID'
}
```

2. **Add IF branch** for provider selection (change condition to check for `openai` first)
3. **Add HTTP Request node** for Anthropic
4. **Connect Anthropic HTTP Request** to Parse (success) and error handler (error)

**NOT required:**
- ~~Add Merge node~~ (not needed)
- Change business logic
- Change database
- Change Telegram processing

**Changes required:**
- ✅ Configuration (1 node)
- ✅ IF condition (3 nodes)
- ✅ HTTP Request node (3 nodes)
- ✅ Error handling connections (already shared)

---

## Open/Closed Principle Compliance

**Open for extension:**
- Adding new providers requires only configuration + transport layer changes

**Closed for modification:**
- Business logic remains unchanged
- Database queries unchanged
- Telegram integration unchanged
- JSON parsing unchanged
- Matching algorithms unchanged

---

## Testing Checklist

- [x] JSON validation passed
- [x] All connections reference existing nodes
- [x] OpenAI provider works with default config
- [x] OpenAI structured outputs work correctly
- [x] RunPod provider works without auth
- [x] RunPod requests work without `response_format`
- [x] Provider switch via environment variable works
- [x] Fallback to OpenAI when `LLM_PROVIDER` not set
- [x] Error handling for unknown provider
- [x] Error outputs connected for both providers
- [x] No business logic changes
- [x] No SQL changes
- [x] No Telegram processing changes

---

## Files Modified

| File | Change |
|------|--------|
| `workflows/HR Processing Worker.json` | Added 7 nodes, modified 6 nodes, removed 3 Merge nodes |
| `docs/MULTI_PROVIDER_ARCHITECTURE.md` | This document |
| `docs/WORKFLOW_MODIFICATION_GUIDE.md` | Implementation guide |
| `workflows/llm-provider-config.js` | Configuration module |
| `docs/CHANGE_LOG.md` | Version 2.1.0 |

---

## Risks and Limitations

### 1. RunPod Endpoint Stability

**Risk:** RunPod endpoint URL may change.

**Mitigation:** Move to environment variable:
```javascript
llm_url: $env.RUNPOD_URL || 'https://...'
```

### 2. Error Handling (SOLVED)

**Status:** ✅ Both OpenAI and RunPod error outputs are connected to shared error handlers.

### 3. Monitoring

**Current:** No logging of provider selection.

**Improvement:** Add logging:
```javascript
console.log(`LLM Provider: ${provider}`);
```

---

## References

- [OpenAI Chat Completions API](https://platform.openai.com/docs/api-reference/chat)
- [OpenAI Structured Outputs](https://platform.openai.com/docs/guides/structured-outputs)
- [RunPod Serverless Endpoints](https://docs.runpod.io/serverless-endpoints/)
- [n8n HTTP Request Node](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.httprequest/)
- [n8n IF Node](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.if/)