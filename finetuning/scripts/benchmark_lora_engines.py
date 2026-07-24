#!/usr/bin/env python3
"""
Benchmark LoRA inference with multiple engines / quantization strategies.

Engines:
- transformers_fp16    : baseline (transformers + peft, float16)
- transformers_4bit    : transformers + peft + bitsandbytes 4-bit NF4
- vllm_fp16            : vLLM offline inference with LoRA (if installed)
- vllm_awq             : vLLM with pre-quantized AWQ base + LoRA (if available)

Usage on RunPod:
    cd /workspace/hra-finetuning
    .venv/bin/python scripts/benchmark_lora_engines.py \
        --config configs/experiment_004.yaml \
        --input data/external_validation.jsonl \
        --engines transformers_fp16 transformers_4bit vllm_fp16 \
        --output runs/experiment_004/latency_optimization/engine_benchmark_report.json

Output:
    runs/experiment_004/latency_optimization/engine_benchmark_report.json
"""

import argparse
import json
import time
from pathlib import Path
from collections import defaultdict

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from peft import PeftModel


def parse_args():
    parser = argparse.ArgumentParser(description="Benchmark LoRA inference engines")
    parser.add_argument("--config", type=str, default="configs/experiment_004.yaml")
    parser.add_argument("--input", type=str, default="data/external_validation.jsonl")
    parser.add_argument(
        "--engines",
        nargs="+",
        default=["transformers_fp16", "transformers_4bit"],
        help="Engines to benchmark",
    )
    parser.add_argument("--warmup", type=int, default=3)
    parser.add_argument("--max-tokens", type=int, default=512)
    parser.add_argument(
        "--output",
        type=str,
        default="runs/experiment_004/latency_optimization/engine_benchmark_report.json",
    )
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


def apply_response_format(messages: list) -> list:
    schema = {
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
    }
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


def extract_json_object(text: str) -> dict | None:
    text = text.strip()
    if text.startswith("```json"):
        text = text.removeprefix("```json").strip()
    elif text.startswith("```"):
        text = text.removeprefix("```").strip()
    if text.endswith("```"):
        text = text[:-3].strip()
    try:
        return json.loads(text)
    except Exception:
        decoder = json.JSONDecoder()
        for i, ch in enumerate(text):
            if ch in ("{", "["):
                try:
                    obj, _ = decoder.raw_decode(text, i)
                    return obj
                except json.JSONDecodeError:
                    continue
    return None


def score_one(pred, reference):
    if pred is None:
        return {"valid_json": False, "decision_match": False, "score_abs_error": None}
    def get(key):
        return pred.get(key) if isinstance(pred, dict) else None
    return {
        "valid_json": True,
        "decision_match": get("decision") == reference.get("decision"),
        "score_abs_error": abs(float(get("score") or 0) - float(reference.get("score") or 0)),
    }


def percentile(values, q):
    if not values:
        return None
    s = sorted(values)
    idx = int(len(s) * q)
    idx = min(idx, len(s) - 1)
    return s[idx]


class EngineTransformersFP16:
    name = "transformers_fp16"

    def __init__(self, config):
        self.config = config
        self.model_id = config["model"]["id"]
        self.adapter_dir = Path(config["workspace"]["base_dir"]) / config["output"]["best_adapter_dir"]

    def load(self):
        print(f"[{self.name}] Loading tokenizer + base model (fp16) + LoRA adapter...")
        t0 = time.time()
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_id)
        base_model = AutoModelForCausalLM.from_pretrained(
            self.model_id,
            torch_dtype=self.config["model"].get("torch_dtype", "auto"),
            device_map=self.config["model"].get("device_map", "auto"),
        )
        self.model = PeftModel.from_pretrained(base_model, self.adapter_dir)
        self.model.eval()
        self.device = self.model.device
        return time.time() - t0

    def predict(self, messages, max_tokens):
        prompt = self.tokenizer.apply_chat_template(
            apply_response_format(messages),
            tokenize=False,
            add_generation_prompt=True,
        )
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
        t0 = time.time()
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=max_tokens,
                do_sample=False,
                use_cache=True,
            )
        gen_time = time.time() - t0
        new_tokens = outputs[0][inputs["input_ids"].shape[-1]:]
        text = self.tokenizer.decode(new_tokens, skip_special_tokens=True).strip()
        pred = extract_json_object(text)
        return pred, gen_time


class EngineTransformers4Bit:
    name = "transformers_4bit"

    def __init__(self, config):
        self.config = config
        self.model_id = config["model"]["id"]
        self.adapter_dir = Path(config["workspace"]["base_dir"]) / config["output"]["best_adapter_dir"]

    def load(self):
        print(f"[{self.name}] Loading tokenizer + base model (4-bit NF4) + LoRA adapter...")
        t0 = time.time()
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_id)
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_use_double_quant=True,
        )
        base_model = AutoModelForCausalLM.from_pretrained(
            self.model_id,
            quantization_config=bnb_config,
            device_map="auto",
            torch_dtype="auto",
        )
        self.model = PeftModel.from_pretrained(base_model, self.adapter_dir)
        self.model.eval()
        self.device = self.model.device
        return time.time() - t0

    def predict(self, messages, max_tokens):
        prompt = self.tokenizer.apply_chat_template(
            apply_response_format(messages),
            tokenize=False,
            add_generation_prompt=True,
        )
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
        t0 = time.time()
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=max_tokens,
                do_sample=False,
                use_cache=True,
            )
        gen_time = time.time() - t0
        new_tokens = outputs[0][inputs["input_ids"].shape[-1]:]
        text = self.tokenizer.decode(new_tokens, skip_special_tokens=True).strip()
        pred = extract_json_object(text)
        return pred, gen_time


class EngineVLLM:
    name = "vllm_fp16"

    def __init__(self, config, vllm_kwargs=None):
        self.config = config
        self.model_id = config["model"]["id"]
        self.adapter_dir = str(Path(config["workspace"]["base_dir"]) / config["output"]["best_adapter_dir"])
        self.vllm_kwargs = vllm_kwargs or {}

    def load(self):
        try:
            from vllm import LLM
            from vllm.lora.request import LoRARequest
        except ImportError as e:
            raise RuntimeError("vllm is not installed") from e

        print(f"[{self.name}] Loading vLLM model + LoRA adapter...")
        t0 = time.time()
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_id)
        llm_kwargs = {
            "model": self.model_id,
            "enable_lora": True,
            "max_lora_rank": self.config["method"]["lora"]["r"],
            "gpu_memory_utilization": 0.85,
            "dtype": "half",
        }
        llm_kwargs.update(self.vllm_kwargs)
        self.llm = LLM(**llm_kwargs)
        # vLLM LoRARequest signature varies by version; handle gracefully
        try:
            self.lora_request = LoRARequest("hra_exp004", 1, self.adapter_dir)
        except TypeError:
            # newer vLLM uses (lora_name, lora_path)
            self.lora_request = LoRARequest("hra_exp004", self.adapter_dir)
        return time.time() - t0

    def predict(self, messages, max_tokens):
        from vllm import SamplingParams

        prompt = self.tokenizer.apply_chat_template(
            apply_response_format(messages),
            tokenize=False,
            add_generation_prompt=True,
        )
        sampling_params = SamplingParams(
            temperature=0,
            max_tokens=max_tokens,
        )
        t0 = time.time()
        outputs = self.llm.generate(
            prompt,
            sampling_params,
            lora_request=self.lora_request,
        )
        gen_time = time.time() - t0
        text = outputs[0].outputs[0].text.strip()
        pred = extract_json_object(text)
        return pred, gen_time


class EngineVLLMEager(EngineVLLM):
    name = "vllm_fp16_enforce_eager"

    def __init__(self, config):
        super().__init__(config, vllm_kwargs={"enforce_eager": True})


class EngineVLLMMaxLen2048(EngineVLLM):
    name = "vllm_fp16_maxlen_2048"

    def __init__(self, config):
        super().__init__(config, vllm_kwargs={"max_model_len": 2048})


class EngineVLLMGPUUtil07(EngineVLLM):
    name = "vllm_fp16_gpu_util_0_7"

    def __init__(self, config):
        super().__init__(config, vllm_kwargs={"gpu_memory_utilization": 0.7})


ENGINE_REGISTRY = {
    "transformers_fp16": EngineTransformersFP16,
    "transformers_4bit": EngineTransformers4Bit,
    "vllm_fp16": EngineVLLM,
    "vllm_fp16_enforce_eager": EngineVLLMEager,
    "vllm_fp16_maxlen_2048": EngineVLLMMaxLen2048,
    "vllm_fp16_gpu_util_0_7": EngineVLLMGPUUtil07,
}


def build_reference(row):
    meta = row.get("metadata", {})
    return {
        "role_score": meta.get("reference_role_score"),
        "skills_score": meta.get("reference_skills_score"),
        "experience_score": meta.get("reference_experience_score"),
        "conditions_score": meta.get("reference_conditions_score"),
        "score": meta.get("reference_score"),
        "decision": meta.get("reference_decision"),
        "reason": meta.get("reference_reason"),
    }


def benchmark_engine(engine_cls, config, records, warmup, max_tokens):
    engine = engine_cls(config)
    load_time = engine.load()

    # Warmup
    print(f"[{engine.name}] Warming up {warmup} requests...")
    for i in range(warmup):
        engine.predict(records[i % len(records)]["messages"], max_tokens)

    # Measure
    print(f"[{engine.name}] Benchmarking {len(records)} records...")
    results = []
    latencies = []
    errors = 0

    for i, row in enumerate(records, 1):
        reference = build_reference(row)
        pred, latency = engine.predict(row["messages"], max_tokens)
        metrics = score_one(pred, reference)
        results.append({
            "metadata": row.get("metadata", {}),
            "reference": reference,
            "prediction": pred,
            "metrics": metrics,
            "latency_ms": int(latency * 1000),
        })
        latencies.append(latency)
        if not metrics["valid_json"]:
            errors += 1
        if i % 20 == 0:
            print(f"  {i}/{len(records)} done")

    n = len(records)
    valid = sum(1 for r in results if r["metrics"]["valid_json"])
    decision_match = sum(1 for r in results if r["metrics"]["decision_match"])
    score_errors = [r["metrics"]["score_abs_error"] for r in results if r["metrics"]["score_abs_error"] is not None]

    fp = sum(1 for r in results if r["reference"].get("decision") == "no_match" and r["prediction"] and r["prediction"].get("decision") == "match")
    fn = sum(1 for r in results if r["reference"].get("decision") == "match" and r["prediction"] and r["prediction"].get("decision") == "no_match")
    total_neg = sum(1 for r in results if r["reference"].get("decision") == "no_match")
    total_pos = sum(1 for r in results if r["reference"].get("decision") == "match")

    return {
        "engine": engine.name,
        "load_time_s": load_time,
        "records": n,
        "valid_json_rate": valid / n if n else 0,
        "decision_accuracy": decision_match / n if n else 0,
        "mae_score": sum(score_errors) / len(score_errors) if score_errors else None,
        "fpr": fp / total_neg if total_neg else 0,
        "fnr": fn / total_pos if total_pos else 0,
        "latency_p50_ms": percentile(latencies, 0.50) * 1000,
        "latency_p95_ms": percentile(latencies, 0.95) * 1000,
        "latency_p99_ms": percentile(latencies, 0.99) * 1000,
        "latency_avg_ms": sum(latencies) / len(latencies) * 1000,
        "invalid_json_count": errors,
        "results": results,
    }


def main():
    args = parse_args()
    config = load_config(args.config)
    records = load_jsonl(args.input)
    if not records:
        raise RuntimeError(f"No records found in {args.input}")

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"Benchmarking engines: {args.engines}")
    print(f"Records: {len(records)}")

    engine_reports = []
    for engine_name in args.engines:
        if engine_name not in ENGINE_REGISTRY:
            print(f"[WARN] Unknown engine: {engine_name}, skipping")
            continue
        try:
            report = benchmark_engine(ENGINE_REGISTRY[engine_name], config, records, args.warmup, args.max_tokens)
            engine_reports.append(report)
            print(f"\n[{engine_name}] summary:")
            print(json.dumps({k: v for k, v in report.items() if k != "results"}, ensure_ascii=False, indent=2))
        except Exception as e:
            print(f"[ERROR] Engine {engine_name} failed: {e}")
            engine_reports.append({
                "engine": engine_name,
                "error": str(e),
            })

    final_report = {
        "experiment": "experiment_004",
        "task": "engine_benchmark",
        "config": str(args.config),
        "input": str(args.input),
        "engines": engine_reports,
    }

    output_path.write_text(json.dumps(final_report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nBenchmark report saved: {output_path}")


if __name__ == "__main__":
    main()
