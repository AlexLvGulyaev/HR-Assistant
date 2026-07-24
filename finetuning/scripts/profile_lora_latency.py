#!/usr/bin/env python3
"""
Profile LoRA inference latency by stage.

Measures:
- model + adapter load time;
- tokenization time;
- model.generate() time;
- decoding / JSON extraction time;
- end-to-end request time.

Usage on RunPod:
    cd /workspace/hra-finetuning
    .venv/bin/python scripts/profile_lora_latency.py --config configs/experiment_004.yaml \
        --input data/external_validation.jsonl --warmup 3 --repeats 5

Output:
    runs/experiment_004/latency_optimization/latency_profile_report.json
"""

import argparse
import json
import time
from pathlib import Path
from collections import defaultdict

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel


def parse_args():
    parser = argparse.ArgumentParser(description="Profile LoRA inference latency by stage")
    parser.add_argument("--config", type=str, default="configs/experiment_004.yaml")
    parser.add_argument("--input", type=str, default="data/external_validation.jsonl")
    parser.add_argument("--warmup", type=int, default=3, help="Warmup requests before measurement")
    parser.add_argument("--repeats", type=int, default=5, help="Number of measured requests per record")
    parser.add_argument("--max-tokens", type=int, default=512)
    parser.add_argument("--output", type=str, default="runs/experiment_004/latency_optimization/latency_profile_report.json")
    return parser.parse_args()


def load_config(path: str):
    import yaml

    p = Path(path)
    if not p.is_absolute():
        p = Path("/workspace/hra-finetuning") / p
    with open(p, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_jsonl(path: str) -> list:
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def extract_json_object(text: str) -> str:
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
        decoder = json.JSONDecoder()
        for i, ch in enumerate(text):
            if ch in ("{", "["):
                try:
                    obj, _ = decoder.raw_decode(text, i)
                    return json.dumps(obj, ensure_ascii=False)
                except json.JSONDecodeError:
                    continue
    return json.dumps({"error": "invalid_json", "raw_response": raw_original}, ensure_ascii=False)


def apply_response_format(messages: list, response_format: dict | None) -> list:
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
    patched = [dict(m) for m in messages]
    if patched and patched[0].get("role") == "system":
        patched[0]["content"] = patched[0]["content"] + schema_instruction
    else:
        patched.insert(0, {"role": "system", "content": schema_instruction})
    return patched


def run_one(model, tokenizer, messages, max_tokens: int, device):
    times = {}

    t0 = time.time()
    patched = apply_response_format(messages, {
        "type": "json_schema",
        "json_schema": {"schema": {
            "type": "object",
            "properties": {
                "role_score": {"type": "number"},
                "skills_score": {"type": "number"},
                "experience_score": {"type": "number"},
                "conditions_score": {"type": "number"},
                "score": {"type": "number"},
                "decision": {"type": "string", "enum": ["match", "no_match"]},
                "reason": {"type": "string"},
            },
            "required": ["role_score", "skills_score", "experience_score", "conditions_score", "score", "decision", "reason"],
            "additionalProperties": False,
        }},
    })
    prompt = tokenizer.apply_chat_template(
        patched,
        tokenize=False,
        add_generation_prompt=True,
    )
    times["apply_chat_template"] = time.time() - t0

    t0 = time.time()
    inputs = tokenizer(prompt, return_tensors="pt").to(device)
    times["tokenize"] = time.time() - t0

    t0 = time.time()
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_tokens,
            do_sample=False,
            use_cache=True,
        )
    times["generate"] = time.time() - t0

    t0 = time.time()
    new_tokens = outputs[0][inputs["input_ids"].shape[-1]:]
    text = tokenizer.decode(new_tokens, skip_special_tokens=True).strip()
    text = extract_json_object(text)
    times["decode_and_extract"] = time.time() - t0

    times["total"] = times["apply_chat_template"] + times["tokenize"] + times["generate"] + times["decode_and_extract"]
    times["generated_tokens"] = len(new_tokens)
    return text, times


def percentile(values: list, q: float) -> float:
    if not values:
        return None
    s = sorted(values)
    idx = int(len(s) * q)
    idx = min(idx, len(s) - 1)
    return s[idx]


def main():
    args = parse_args()
    config = load_config(args.config)
    base_dir = Path(config["workspace"]["base_dir"])
    adapter_dir = base_dir / config["output"]["best_adapter_dir"]
    model_id = config["model"]["id"]

    records = load_jsonl(args.input)
    if not records:
        raise RuntimeError(f"No records found in {args.input}")

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"Profiling {len(records)} records from {args.input}")
    print(f"Model: {model_id}")
    print(f"Adapter: {adapter_dir}")
    print("Loading model + adapter...")

    load_start = time.time()
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    base_model = AutoModelForCausalLM.from_pretrained(
        model_id,
        torch_dtype=config["model"].get("torch_dtype", "auto"),
        device_map=config["model"].get("device_map", "auto"),
    )
    model = PeftModel.from_pretrained(base_model, adapter_dir)
    model.eval()
    load_time = time.time() - load_start
    device = model.device

    print(f"Model loaded in {load_time:.2f}s on {device}")

    # Warmup
    print(f"Running {args.warmup} warmup requests...")
    for i in range(args.warmup):
        run_one(model, tokenizer, records[i % len(records)]["messages"], args.max_tokens, device)

    # Measure
    print(f"Profiling {args.repeats} repeats per record...")
    all_measurements = []
    stage_totals = defaultdict(list)

    for r_idx, record in enumerate(records, 1):
        messages = record["messages"]
        meta = record.get("metadata", {})
        for rep in range(args.repeats):
            _, times = run_one(model, tokenizer, messages, args.max_tokens, device)
            measurement = {
                "record_index": r_idx,
                "repeat": rep,
                "case_code": meta.get("case_code"),
                "vacancy_title": meta.get("vacancy_title"),
                **times,
            }
            all_measurements.append(measurement)
            for k, v in times.items():
                if k != "generated_tokens":
                    stage_totals[k].append(v)
        if r_idx % 10 == 0:
            print(f"  {r_idx}/{len(records)} done")

    stage_summary = {}
    for stage, values in stage_totals.items():
        stage_summary[stage] = {
            "p50_ms": percentile(values, 0.50) * 1000,
            "p95_ms": percentile(values, 0.95) * 1000,
            "p99_ms": percentile(values, 0.99) * 1000,
            "avg_ms": sum(values) / len(values) * 1000,
            "min_ms": min(values) * 1000,
            "max_ms": max(values) * 1000,
            "total_s": sum(values),
        }

    report = {
        "experiment": "experiment_004",
        "task": "latency_profile",
        "config": str(args.config),
        "input": str(args.input),
        "model": model_id,
        "adapter": str(adapter_dir),
        "device": str(device),
        "model_load_time_s": load_time,
        "records": len(records),
        "warmup": args.warmup,
        "repeats": args.repeats,
        "stage_summary": stage_summary,
        "measurements": all_measurements,
    }

    output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    print("\n=== Latency Profile Summary ===")
    print(f"Model load time: {load_time:.2f}s")
    print(json.dumps(stage_summary, ensure_ascii=False, indent=2))
    print(f"\nReport saved: {output_path}")


if __name__ == "__main__":
    main()
