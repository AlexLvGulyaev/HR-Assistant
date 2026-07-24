from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel
import torch
import json
import argparse
from pathlib import Path


app = FastAPI()


def load_config(config_path: str):
    import yaml

    path = Path(config_path)
    if not path.is_absolute():
        path = Path("/workspace/hra-finetuning") / path

    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


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
    """Extract the first valid JSON object/array from model output.

    Graceful fallback: if no JSON can be extracted, wrap the raw text in a
    JSON envelope so the HTTP response stays 200 and downstream clients can
    decide how to handle the malformed output.
    """
    raw_original = text
    text = text.strip()

    # Strip markdown code fences (handles ```json ... ``` and ``` ... ```)
    if text.startswith("```json"):
        text = text.removeprefix("```json").strip()
    elif text.startswith("```"):
        text = text.removeprefix("```").strip()
    if text.endswith("```"):
        text = text[:-3].strip()

    # Direct parse first
    try:
        obj = json.loads(text)
        return json.dumps(obj, ensure_ascii=False)
    except Exception:
        pass

    # Scan for the first well-formed JSON object or array, ignoring any text
    # before or after it.
    decoder = json.JSONDecoder()
    for i, ch in enumerate(text):
        if ch in ("{", "["):
            try:
                obj, _ = decoder.raw_decode(text, i)
                return json.dumps(obj, ensure_ascii=False)
            except json.JSONDecodeError:
                continue

    # Graceful fallback: never raise HTTP 422. Return the raw response wrapped
    # in a JSON object so the API remains usable.
    return json.dumps(
        {"error": "invalid_json", "raw_response": raw_original},
        ensure_ascii=False,
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


def create_app(config_path: str = "configs/experiment_003.yaml"):
    config = load_config(config_path)
    model_id = config["model"]["id"]
    torch_dtype_str = config["model"].get("torch_dtype", "auto")
    device_map = config["model"].get("device_map", "auto")
    base_dir = Path(config["workspace"]["base_dir"])
    adapter_dir = base_dir / config["output"]["best_adapter_dir"]

    tokenizer = AutoTokenizer.from_pretrained(model_id)
    base_model = AutoModelForCausalLM.from_pretrained(
        model_id,
        torch_dtype=torch_dtype_str if torch_dtype_str != "auto" else "auto",
        device_map=device_map,
    )
    model = PeftModel.from_pretrained(base_model, adapter_dir)
    model.eval()

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

    return app


def main():
    parser = argparse.ArgumentParser(description="LoRA Qwen API for HRA")
    parser.add_argument("--config", type=str, default="configs/experiment_003.yaml", help="Path to config YAML")
    parser.add_argument("--host", type=str, default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()

    import uvicorn
    create_app(args.config)
    uvicorn.run(app, host=args.host, port=args.port)


if __name__ == "__main__":
    main()
