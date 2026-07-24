from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
import json
import argparse


app = FastAPI()


def load_config(config_path: str):
    import yaml
    from pathlib import Path

    path = Path(config_path)
    if not path.is_absolute():
        # If relative, assume it's relative to /workspace/hra-finetuning
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


def create_app(config_path: str = "configs/experiment_003.yaml"):
    config = load_config(config_path)
    model_id = config["model"]["id"]
    torch_dtype_str = config["model"].get("torch_dtype", "auto")
    device_map = config["model"].get("device_map", "auto")

    tokenizer = AutoTokenizer.from_pretrained(model_id)
    base_model = AutoModelForCausalLM.from_pretrained(
        model_id,
        torch_dtype=torch_dtype_str if torch_dtype_str != "auto" else "auto",
        device_map=device_map,
    )
    base_model.eval()

    @app.post("/v1/chat/completions")
    def chat(req: ChatRequest):
        messages = apply_response_format(req.messages, req.response_format)

        prompt = tokenizer.apply_chat_template(
            [m.model_dump() for m in messages],
            tokenize=False,
            add_generation_prompt=True,
        )

        inputs = tokenizer(prompt, return_tensors="pt").to(base_model.device)

        generation_kwargs = {
            "max_new_tokens": req.max_tokens,
            "do_sample": req.temperature > 0,
        }

        if req.temperature > 0:
            generation_kwargs["temperature"] = req.temperature

        outputs = base_model.generate(
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
    parser = argparse.ArgumentParser(description="Base Qwen API for HRA")
    parser.add_argument("--config", type=str, default="configs/experiment_003.yaml", help="Path to config YAML")
    parser.add_argument("--host", type=str, default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()

    import uvicorn
    create_app(args.config)
    uvicorn.run(app, host=args.host, port=args.port)


if __name__ == "__main__":
    main()
