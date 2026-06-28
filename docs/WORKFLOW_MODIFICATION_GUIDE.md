# Workflow Modification Guide

**Created:** 2026-06-28
**Workflow:** HR Processing Worker.json
**Purpose:** Final architecture for multi-provider LLM support

---

## Summary of Changes

| Change | Count | Details |
|--------|-------|---------|
| **New nodes** | +7 | 1 Configure LLM Provider + 3 IF Provider + 3 RunPod HTTP |
| **Modified nodes** | 6 | 3 Prepare Body + 3 Parse |
| **Renamed nodes** | 3 | OpenAI HTTP nodes renamed with `(OpenAI)` suffix |
| **Removed nodes** | -3 | Merge nodes (not needed) |

**Total:** 47 → 54 nodes (+7)

---

## Architecture (Final)

```
Configure LLM Provider (sets llm_config)
       ↓
Prepare OpenAI Body (conditional response_format)
       ↓
IF: Provider? (checks llm_config.llm_provider)
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
           Continue Processing
```

---

## Node Changes

### New Nodes (7 total)

| Node | Type | Count | Purpose |
|------|------|-------|---------|
| Configure LLM Provider | Code | 1 | Set llm_config based on provider |
| IF: Provider for... | IF | 3 | Provider selection for each LLM call |
| LLM: ... (RunPod) | HTTP Request | 3 | RunPod API calls |

### Modified Nodes (6 total)

| Node | Modification |
|------|--------------|
| Prepare OpenAI Body: Extract candidate JSON | Conditional response_format |
| Prepare OpenAI Body: Repair candidate JSON | Conditional response_format |
| Prepare OpenAI Body: Match candidate vacancy | Conditional response_format |
| Parse OpenAI Candidate JSON | Use llm_provider from config |
| Parse OpenAI Repair Candidate JSON | Use llm_provider from config |
| Parse match JSON | Use llm_provider from config |

### Renamed Nodes (3 total)

| Old Name | New Name |
|----------|-----------|
| LLM: Extract candidate JSON | LLM: Extract candidate JSON (OpenAI) |
| LLM: Repair candidate JSON | LLM: Repair candidate JSON (OpenAI) |
| LLM: Match candidate vacancy | LLM: Match candidate vacancy (OpenAI) |

---

## Step-by-Step Modifications

### Step 1: Add Configure LLM Provider Node

**Position:** After `IF: has pending input?`

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
  throw new Error(`Unknown LLM provider: ${provider}`);
}

return [{ json: { ...$json, llm_config: config } }];
```

**Update connections:**
- `IF: has pending input?` → `Configure LLM Provider`
- `Configure LLM Provider` → `Prepare OpenAI Body: Extract candidate JSON`

---

### Step 2: Add IF, RunPod Nodes for Each LLM Call

For each of the 3 LLM calls (Extract, Repair, Match), add:

1. **IF node** before HTTP Request
2. **RunPod HTTP Request node** (copy of OpenAI, without credentials)
3. **Connect both branches to Parse and error handler**

#### Connection Pattern

```
Prepare OpenAI Body → IF: Provider?
                          ↓
              OpenAI HTTP (true)  ←→  RunPod HTTP (false)
                          ↓                    ↓
                   Parse (shared)      Parse (shared)
                          ↓                    ↓
                   Error handler        Error handler
```

**NOT using Merge - both branches connect directly to Parse**

---

### Step 3: Modify Prepare Body Nodes

Add conditional `response_format`:

```javascript
const llmConfig = $json.llm_config;

const openai_body = {
  model: llmConfig.llm_model,
  temperature: 0,
  messages: [/* ... */]
};

// Add response_format only if provider supports it
if (llmConfig.llm_supports_structured_output) {
  openai_body.response_format = {
    type: 'json_schema',
    json_schema: { /* ... */ }
  };
}

return [{ json: { ...$json, llm_config: llmConfig, openai_body } }];
```

---

### Step 4: Create RunPod HTTP Request Nodes

Copy OpenAI nodes, but:

1. Remove `credentials`
2. Set `authentication: none`
3. Add `(RunPod)` suffix to name

---

### Step 5: Update Connections

**For each LLM call:**

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

## Testing Checklist

### OpenAI (default)

1. Set `LLM_PROVIDER=openai` or leave unset
2. Run workflow with candidate input
3. Verify:
   - LLM request sent to `https://api.openai.com/v1/chat/completions`
   - Model: `gpt-4o-mini`
   - `response_format` included in request
   - Response parsed correctly
   - Error handling works

### RunPod

1. Set `LLM_PROVIDER=runpod`
2. Run workflow with candidate input
3. Verify:
   - LLM request sent to RunPod URL
   - Model: `hra-qwen`
   - `response_format` **NOT** included in request
   - No credentials sent
   - Response parsed correctly
   - Error handling works

---

## Why No Merge?

**Problem:** Merge nodes expect data from both inputs simultaneously. For mutually exclusive branches (IF node), only one branch has data at a time.

**Solution:** Connect both branches directly to the same downstream node (Parse). n8n handles this correctly - only the active branch's data flows downstream.

**Benefits:**
- Simpler architecture
- No waiting for missing input
- No data loss
- Cleaner error handling

---

## Files Modified

| File | Change |
|------|--------|
| `workflows/HR Processing Worker.json` | Added 7 nodes, modified 6 nodes, removed 3 Merge nodes |
| `docs/MULTI_PROVIDER_ARCHITECTURE.md` | Architecture document |
| `docs/WORKFLOW_MODIFICATION_GUIDE.md` | This document |
| `workflows/llm-provider-config.js` | Configuration module |

---

## Rollback Instructions

If issues arise:

1. Set `LLM_PROVIDER=openai` (default)
2. Revert workflow import to previous version
3. No database changes to rollback

---

## References

- [MULTI_PROVIDER_ARCHITECTURE.md](MULTI_PROVIDER_ARCHITECTURE.md) - Architecture overview
- [llm-provider-config.js](../workflows/llm-provider-config.js) - Configuration module
- [n8n IF Node](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.if/)