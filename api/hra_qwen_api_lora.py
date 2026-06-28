from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel
import torch
import json

MODEL_ID = "Qwen/Qwen2.5-1.5B-Instruct"
ADAPTER_DIR = "/workspace/adapters/hra_exp002"

app = FastAPI()

tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
base_model = AutoModelForCausalLM.from_pretrained(
    MODEL_ID,
    torch_dtype="auto",
    device_map="auto",
)

model = PeftModel.from_pretrained(
    base_model,
    ADAPTER_DIR,
)
model.eval()


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    model: str = "hra-qwen"
    messages: list[ChatMessage]
    max_tokens: int = 300
    temperature: float = 0.2
    response_format: dict | None = None


def extract_json_object(text: str) -> str:
    text = text.strip()

    if text.startswith("```json"):
        text = text.removeprefix("```json").strip()
    if text.startswith("```"):
        text = text.removeprefix("```").strip()
    if text.endswith("```"):
        text = text[:-3].strip()

    decoder = json.JSONDecoder()

    for i, ch in enumerate(text):
        if ch == "{":
            try:
                obj, _ = decoder.raw_decode(text[i:])
                return json.dumps(obj, ensure_ascii=False)
            except json.JSONDecodeError:
                continue

    raise HTTPException(
        status_code=422,
        detail={
            "error": "Model did not return valid JSON object",
            "raw_response": text,
        },
    )


def apply_response_format(messages: list[ChatMessage], response_format: dict | None) -> list[ChatMessage]:
    if not response_format or response_format.get("type") != "json_schema":
        return messages

    schema = response_format.get("json_schema", {}).get("schema", {})

    schema_instruction = (
        "\n\nВАЖНО. Ты работаешь как JSON API.\n"
        "Верни ТОЛЬКО валидный JSON-объект.\n"
        "Без markdown.\n"
        "Без пояснений.\n"
        "Без текста до JSON.\n"
        "Без текста после JSON.\n"
        "Без списков вне JSON.\n"
        "JSON должен соответствовать этой схеме:\n"
        + json.dumps(schema, ensure_ascii=False)
    )

    patched = [ChatMessage(role=m.role, content=m.content) for m in messages]

    if patched and patched[0].role == "system":
        patched[0].content = patched[0].content + schema_instruction
    else:
        patched.insert(0, ChatMessage(role="system", content=schema_instruction))

    return patched


@app.post("/v1/chat/completions")
def chat(req: ChatRequest):
    messages = apply_response_format(req.messages, req.response_format)

    prompt = tokenizer.apply_chat_template(
        [m.model_dump() for m in messages],
        tokenize=False,
        add_generation_prompt=True,
    )

    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)

    generation_kwargs = {
        "max_new_tokens": req.max_tokens,
        "do_sample": req.temperature > 0,
    }

    if req.temperature > 0:
        generation_kwargs["temperature"] = req.temperature

    outputs = model.generate(
        **inputs,
        **generation_kwargs,
    )

    text = tokenizer.decode(
        outputs[0][inputs["input_ids"].shape[-1]:],
        skip_special_tokens=True,
    ).strip()

    if req.response_format and req.response_format.get("type") == "json_schema":
        text = extract_json_object(text)

    return {
        "id": "chatcmpl-hra-qwen",
        "object": "chat.completion",
        "model": req.model,
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": text,
                },
                "finish_reason": "stop",
            }
        ],
    }


@app.get("/v1/models")
def models():
    return {"data": [{"id": "hra-qwen"}]}
