from fastapi import FastAPI
from pydantic import BaseModel
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
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
    model: str = "hra-qwen-4bit"
    messages: list[ChatMessage]
    max_tokens: int = 512
    temperature: float = 0.0
    response_format: dict | None = None


def extract_json_object(text: str) -> str:
    """Extract the first valid JSON object/array from model output."""
    raw_original = text
    text = text.strip()

    if text.startswith("```json"):
        text = text.removeprefix("```json").strip()
    elif text.startswith("```"):
        text = text.removeprefix("```").strip()
    if text.endswith("```"):
        text = text[:-3].strip()

    try:
        obj = json.loads(text)
        return json.dumps(obj, ensure_ascii=False)
    except Exception:
        pass

    decoder = json.JSONDecoder()
    for i, ch in enumerate(text):
        if ch in ("{", "["):
            try:
                obj, _ = decoder.raw_decode(text, i)
                return json.dumps(obj, ensure_ascii=False)
            except json.JSONDecodeError:
                continue

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


def create_app(config_path: str = "configs/experiment_004.yaml"):
    config = load_config(config_path)
    model_id = config["model"]["id"]
    base_dir = Path(config["workspace"]["base_dir"])
    adapter_dir = base_dir / config["output"]["best_adapter_dir"]

    tokenizer = AutoTokenizer.from_pretrained(model_id)

    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_compute_dtype=torch.float16,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_use_double_quant=True,
    )
    base_model = AutoModelForCausalLM.from_pretrained(
        model_id,
        quantization_config=bnb_config,
        device_map="auto",
        torch_dtype="auto",
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
            "use_cache": True,
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
            "id": "chatcmpl-hra-qwen-4bit",
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
        return {"data": [{"id": "hra-qwen-4bit"}]}

    return app


def main():
    parser = argparse.ArgumentParser(description="4-bit Quantized LoRA Qwen API for HRA")
    parser.add_argument("--config", type=str, default="configs/experiment_004.yaml", help="Path to config YAML")
    parser.add_argument("--host", type=str, default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()

    import uvicorn
    create_app(args.config)
    uvicorn.run(app, host=args.host, port=args.port)


if __name__ == "__main__":
    main()
