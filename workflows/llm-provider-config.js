/**
 * Configure LLM Provider
 *
 * This module provides centralized LLM provider configuration for HR Assistant.
 * Supports multiple providers: OpenAI (default), RunPod, and extensibility for future providers.
 *
 * Usage in n8n Code node:
 *   const { configureLLMProvider, buildLLMRequestBody } = require('./llm-provider-config.js');
 *   const config = configureLLMProvider($env);
 *   const body = buildLLMRequestBody(config, systemPrompt, userContent, schema);
 */

/**
 * Provider configurations
 *
 * Each provider has:
 * - llm_provider: identifier
 * - llm_url: API endpoint
 * - llm_model: default model
 * - llm_supports_structured_output: whether provider supports json_schema response_format
 * - llm_auth_credential_id: n8n credential ID (null for no auth)
 * - llm_auth_type: authentication type (none, header, etc.)
 */
const PROVIDERS = {
  openai: {
    llm_provider: 'openai',
    llm_url: 'https://api.openai.com/v1/chat/completions',
    llm_model: 'gpt-4o-mini',
    llm_supports_structured_output: true,
    llm_auth_credential_id: 'pANFrhR1xZgvvzrJ',
    llm_auth_type: 'header'
  },
  runpod: {
    llm_provider: 'runpod',
    llm_url: 'https://bgi0g1thpts995-8000.proxy.runpod.net/v1/chat/completions',
    llm_model: 'hra-qwen',
    llm_supports_structured_output: false,
    llm_auth_credential_id: null,
    llm_auth_type: 'none'
  }
};

/**
 * Configure LLM provider based on environment variable
 *
 * @param {Object} env - Environment variables ($env in n8n)
 * @param {string} env.LLM_PROVIDER - Provider name: 'openai' (default) or 'runpod'
 * @returns {Object} Provider configuration object
 */
function configureLLMProvider(env) {
  const providerName = (env?.LLM_PROVIDER || 'openai').toLowerCase();
  const config = PROVIDERS[providerName];

  if (!config) {
    throw new Error(`Unknown LLM provider: ${providerName}. Supported: ${Object.keys(PROVIDERS).join(', ')}`);
  }

  return config;
}

/**
 * Build LLM request body with conditional structured output
 *
 * @param {Object} config - Provider configuration from configureLLMProvider()
 * @param {string} systemPrompt - System message content
 * @param {string|Array} userContent - User message content (string or content array)
 * @param {Object} schema - JSON schema for structured output (optional)
 * @param {string} schemaName - Name for the schema (default: 'response')
 * @param {number} temperature - Temperature setting (default: 0)
 * @returns {Object} Request body for LLM API
 */
function buildLLMRequestBody(config, systemPrompt, userContent, schema, schemaName = 'response', temperature = 0) {
  const body = {
    model: config.llm_model,
    temperature: temperature,
    messages: [
      {
        role: 'system',
        content: systemPrompt
      },
      {
        role: 'user',
        content: userContent
      }
    ]
  };

  // Add structured output only if provider supports it
  if (config.llm_supports_structured_output && schema) {
    body.response_format = {
      type: 'json_schema',
      json_schema: {
        name: schemaName,
        strict: true,
        schema: schema
      }
    };
  }

  return body;
}

/**
 * Get HTTP request options for LLM call
 *
 * @param {Object} config - Provider configuration from configureLLMProvider()
 * @returns {Object} HTTP request options for n8n
 */
function getLLMHttpOptions(config) {
  const options = {
    method: 'POST',
    url: config.llm_url,
    sendHeaders: true,
    headerParameters: {
      parameters: [
        {
          name: 'Content-Type',
          value: 'application/json'
        }
      ]
    },
    sendBody: true,
    specifyBody: 'json'
  };

  // Add authentication if required
  if (config.llm_auth_type === 'header' && config.llm_auth_credential_id) {
    options.authentication = 'genericCredentialType';
    options.genericAuthType = 'httpHeaderAuth';
  }

  return options;
}

/**
 * Get n8n credential ID for HTTP request
 *
 * @param {Object} config - Provider configuration
 * @returns {string|null} Credential ID or null for no auth
 */
function getLLMCredentialId(config) {
  return config.llm_auth_credential_id;
}

/**
 * Extract provider name from config for logging/tracking
 *
 * @param {Object} config - Provider configuration
 * @returns {string} Provider name
 */
function getProviderName(config) {
  return config?.llm_provider || 'unknown';
}

/**
 * Check if provider supports structured output
 *
 * @param {Object} config - Provider configuration
 * @returns {boolean} True if structured output is supported
 */
function supportsStructuredOutput(config) {
  return config?.llm_supports_structured_output === true;
}

/**
 * n8n Code node wrapper for configureLLMProvider
 *
 * Use this in n8n Code node:
 *   return configureLLMProviderNode($env, $json);
 */
function configureLLMProviderNode(env, inputData) {
  const config = configureLLMProvider(env);

  return [{
    json: {
      ...inputData,
      llm_config: config
    }
  }];
}

/**
 * n8n Code node wrapper for buildLLMRequestBody
 *
 * Use this in n8n Code node:
 *   const config = $json.llm_config;
 *   const body = buildLLMRequestBodyNode(config, systemPrompt, userContent, schema);
 */
function buildLLMRequestBodyNode(config, systemPrompt, userContent, schema, schemaName, temperature) {
  return buildLLMRequestBody(config, systemPrompt, userContent, schema, schemaName, temperature);
}

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    PROVIDERS,
    configureLLMProvider,
    buildLLMRequestBody,
    getLLMHttpOptions,
    getLLMCredentialId,
    getProviderName,
    supportsStructuredOutput,
    configureLLMProviderNode,
    buildLLMRequestBodyNode
  };
}