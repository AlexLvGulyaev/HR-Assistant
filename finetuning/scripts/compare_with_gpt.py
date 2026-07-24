#!/usr/bin/env python3
"""
Compare LoRA Experiment 004 with OpenAI GPT-4o-mini on the same sample.

Usage on VPS (after RunPod reports copied back):
    .venv/bin/python scripts/compare_with_gpt.py \
        --lora-report runs/experiment_004/generation_test/generation_test_report.json \
        --sample-size 50 \
        --output runs/experiment_004/gpt_comparison_report.json

Or on RunPod with live LoRA API:
    .venv/bin/python scripts/compare_with_gpt.py \
        --config configs/experiment_004.yaml \
        --test-file data/test.jsonl \
        --sample-size 50 \
        --output runs/experiment_004/gpt_comparison_report.json

Environment:
    OPENAI_API_KEY — required for GPT-4o-mini calls.
"""

import argparse
import json
import os
import random
import time
import urllib.request
from pathlib import Path
from collections import Counter

import yaml


def parse_args():
    parser = argparse.ArgumentParser(description="Compare LoRA vs GPT-4o-mini")
    parser.add_argument("--config", type=str, default="configs/experiment_004.yaml")
    parser.add_argument("--test-file", type=str, default=None)
    parser.add_argument("--lora-report", type=str, default=None,
                        help="Path to existing LoRA generation_test_report.json")
    parser.add_argument("--lora-api-url", type=str, default="http://127.0.0.1:8000/v1/chat/completions")
    parser.add_argument("--sample-size", type=int, default=50)
    parser.add_argument("--output", type=str, default="runs/experiment_004/gpt_comparison_report.json")
    parser.add_argument("--seed", type=int, default=42)
    return parser.parse_args()


def load_config(config_path: str) -> dict:
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_jsonl(path: Path) -> list:
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def extract_json(text: str) -> dict | None:
    text = text.strip()
    if text.startswith("```json"):
        text = text[7:]
    if text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    text = text.strip()
    try:
        return json.loads(text)
    except Exception:
        decoder = json.JSONDecoder()
        for i, ch in enumerate(text):
            if ch == "{":
                try:
                    obj, _ = decoder.raw_decode(text[i:])
                    return obj
                except json.JSONDecodeError:
                    continue
        return None


def call_lora_api(api_url: str, messages: list, schema: dict) -> tuple:
    payload = {
        "model": "hra-qwen",
        "messages": messages,
        "max_tokens": 512,
        "temperature": 0,
        "response_format": {
            "type": "json_schema",
            "json_schema": {"schema": schema},
        },
    }
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        api_url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    start = time.time()
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            body = resp.read().decode("utf-8")
            latency_ms = int((time.time() - start) * 1000)
            parsed = json.loads(body)
            content = parsed["choices"][0]["message"]["content"]
            result = extract_json(content)
            return result, latency_ms, None
    except Exception as e:
        latency_ms = int((time.time() - start) * 1000)
        return None, latency_ms, str(e)


def call_gpt4o_mini(messages: list, schema: dict) -> tuple:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY environment variable is not set")

    payload = {
        "model": "gpt-4o-mini",
        "messages": messages,
        "max_tokens": 512,
        "temperature": 0,
        "response_format": {
            "type": "json_schema",
            "json_schema": {
                "name": "hra_matching",
                "strict": True,
                "schema": schema,
            },
        },
    }
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        "https://api.openai.com/v1/chat/completions",
        data=data,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )
    start = time.time()
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            body = resp.read().decode("utf-8")
            latency_ms = int((time.time() - start) * 1000)
            parsed = json.loads(body)
            content = parsed["choices"][0]["message"]["content"]
            result = extract_json(content)
            return result, latency_ms, None
    except Exception as e:
        latency_ms = int((time.time() - start) * 1000)
        return None, latency_ms, str(e)


def score_one(pred, teacher):
    if pred is None:
        return {"valid_json": False, "decision_match": False, "score_abs_error": None}
    def get(key):
        return pred.get(key) if isinstance(pred, dict) else None
    return {
        "valid_json": True,
        "decision_match": get("decision") == teacher.get("decision"),
        "score_abs_error": abs(float(get("score") or 0) - float(teacher.get("score") or 0)),
    }


def summarize(results, model_name):
    n = len(results)
    valid = sum(1 for r in results if r[f"{model_name}_metrics"]["valid_json"])
    decision_match = sum(1 for r in results if r[f"{model_name}_metrics"]["decision_match"])
    score_errors = [r[f"{model_name}_metrics"]["score_abs_error"] for r in results
                    if r[f"{model_name}_metrics"]["score_abs_error"] is not None]
    latencies = [r[f"{model_name}_latency_ms"] for r in results if r[f"{model_name}_latency_ms"] is not None]

    teacher_decisions = Counter(r["teacher"].get("decision") for r in results)
    model_decisions = Counter(r[f"{model_name}_prediction"].get("decision") if r[f"{model_name}_prediction"] else None for r in results)

    # FPR/FNR against teacher
    fp = sum(1 for r in results
             if r["teacher"].get("decision") == "no_match"
             and r[f"{model_name}_prediction"] is not None
             and r[f"{model_name}_prediction"].get("decision") == "match")
    fn = sum(1 for r in results
             if r["teacher"].get("decision") == "match"
             and r[f"{model_name}_prediction"] is not None
             and r[f"{model_name}_prediction"].get("decision") == "no_match")
    total_neg = teacher_decisions.get("no_match", 0)
    total_pos = teacher_decisions.get("match", 0)

    return {
        "model": model_name,
        "records": n,
        "valid_json_rate": valid / n if n else 0,
        "decision_accuracy": decision_match / n if n else 0,
        "mae_score": sum(score_errors) / len(score_errors) if score_errors else None,
        "fpr": fp / total_neg if total_neg else 0,
        "fnr": fn / total_pos if total_pos else 0,
        "latency_p50": sorted(latencies)[len(latencies) // 2] if latencies else None,
        "latency_p95": sorted(latencies)[int(len(latencies) * 0.95)] if latencies else None,
        "latency_avg": sum(latencies) / len(latencies) if latencies else None,
    }


def main():
    args = parse_args()
    config = load_config(args.config)
    base_dir = Path(config["workspace"]["base_dir"])

    test_file = Path(args.test_file) if args.test_file else base_dir / config["dataset"]["files"]["test"]
    rows = load_jsonl(test_file)

    # Sample stratified by case_type to keep representation
    random.seed(args.seed)
    by_type = {}
    for r in rows:
        ct = r.get("metadata", {}).get("case_type", "unknown")
        by_type.setdefault(ct, []).append(r)

    sample = []
    remaining = args.sample_size
    for ct, group in by_type.items():
        k = max(1, round(args.sample_size * len(group) / len(rows)))
        k = min(k, len(group))
        sample.extend(random.sample(group, k))
        remaining -= k

    # Fill remaining randomly
    if remaining > 0:
        leftover = [r for r in rows if r not in sample]
        sample.extend(random.sample(leftover, min(remaining, len(leftover))))

    sample = sample[:args.sample_size]

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

    results = []
    for i, row in enumerate(sample, 1):
        messages = row["messages"]
        teacher = json.loads(messages[2]["content"])

        print(f"[{i}/{len(sample)}] Evaluating...")

        lora_pred, lora_lat, lora_err = call_lora_api(args.lora_api_url, messages, schema)
        gpt_pred, gpt_lat, gpt_err = call_gpt4o_mini(messages, schema)

        results.append({
            "metadata": row.get("metadata", {}),
            "teacher": teacher,
            "lora_prediction": lora_pred,
            "lora_latency_ms": lora_lat,
            "lora_error": lora_err,
            "lora_metrics": score_one(lora_pred, teacher),
            "gpt_prediction": gpt_pred,
            "gpt_latency_ms": gpt_lat,
            "gpt_error": gpt_err,
            "gpt_metrics": score_one(gpt_pred, teacher),
        })

    lora_summary = summarize(results, "lora")
    gpt_summary = summarize(results, "gpt")

    report = {
        "sample_size": len(results),
        "test_file": str(test_file),
        "lora_api_url": args.lora_api_url,
        "gpt_model": "gpt-4o-mini",
        "lora_summary": lora_summary,
        "gpt_summary": gpt_summary,
        "winner": "lora" if lora_summary["decision_accuracy"] >= gpt_summary["decision_accuracy"]
                  and (lora_summary["mae_score"] or 999) <= (gpt_summary["mae_score"] or 999) else "gpt",
        "results": results,
    }

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    print("\nSUMMARY")
    print(json.dumps({
        "lora": lora_summary,
        "gpt": gpt_summary,
        "winner": report["winner"],
    }, ensure_ascii=False, indent=2))
    print(f"Report saved: {out_path}")


if __name__ == "__main__":
    main()
