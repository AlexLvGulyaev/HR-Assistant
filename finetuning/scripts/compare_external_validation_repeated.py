#!/usr/bin/env python3
"""
Compare LoRA Experiment 004 and GPT-4o-mini on external validation set,
running multiple repetitions and aggregating statistics.

This is a thin wrapper around compare_external_validation.py:
- runs N repetitions against the same LoRA API and GPT-4o-mini;
- aggregates latency percentiles and quality metrics across all repetitions;
- produces a single report with per-run details and summary statistics.

Usage on RunPod with live vLLM API:
    cd /workspace/hra-finetuning
    set -a; source .env; set +a
    PATH="/workspace/hra-finetuning/.venv/bin:$PATH" \
    .venv/bin/python scripts/compare_external_validation_repeated.py \
        --lora-api-url http://127.0.0.1:8000/v1/chat/completions \
        --input data/external_validation.jsonl \
        --repetitions 3 \
        --max-tokens 512 \
        --gpt-model gpt-4o-mini \
        --output runs/experiment_004/latency_optimization/external_validation_repeated_report.json
"""

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path
from collections import defaultdict


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run multiple repetitions of LoRA vs GPT-4o-mini comparison"
    )
    parser.add_argument(
        "--input",
        type=str,
        default="data/external_validation.jsonl",
        help="External validation JSONL with reference annotations",
    )
    parser.add_argument(
        "--lora-api-url",
        type=str,
        default="http://127.0.0.1:8000/v1/chat/completions",
        help="LoRA API URL",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="runs/experiment_004/latency_optimization/external_validation_repeated_report.json",
        help="Output report path",
    )
    parser.add_argument(
        "--repetitions",
        type=int,
        default=3,
        help="Number of repetitions (default: 3)",
    )
    parser.add_argument(
        "--max-tokens",
        type=int,
        default=512,
        help="Max tokens per response (default: 512)",
    )
    parser.add_argument(
        "--gpt-model",
        type=str,
        default="gpt-4o-mini",
        help="OpenAI model for comparison (default: gpt-4o-mini)",
    )
    parser.add_argument(
        "--compare-script",
        type=str,
        default="scripts/compare_external_validation.py",
        help="Path to base compare script",
    )
    return parser.parse_args()


def percentile(values, q):
    if not values:
        return None
    s = sorted(values)
    idx = int(len(s) * q)
    idx = min(idx, len(s) - 1)
    return s[idx]


def run_once(args, run_idx: int, output_dir: Path) -> dict:
    run_output = output_dir / f"external_validation_run_{run_idx:02d}.json"
    cmd = [
        sys.executable,
        args.compare_script,
        "--input", args.input,
        "--lora-api-url", args.lora_api_url,
        "--output", str(run_output),
        "--max-tokens", str(args.max_tokens),
        "--gpt-model", args.gpt_model,
    ]
    print(f"\n[Run {run_idx}/{args.repetitions}] Starting...")
    t0 = time.time()
    result = subprocess.run(cmd, capture_output=True, text=True, env={**dict(__import__('os').environ)})
    elapsed = time.time() - t0
    if result.returncode != 0:
        print(f"[Run {run_idx}] FAILED: {result.stderr}")
        raise RuntimeError(f"Run {run_idx} failed with exit code {result.returncode}")
    print(f"[Run {run_idx}] Completed in {elapsed:.1f}s")
    report = json.loads(run_output.read_text(encoding="utf-8"))
    report["_run_meta"] = {
        "run_index": run_idx,
        "elapsed_seconds": elapsed,
        "output_file": str(run_output),
    }
    return report


def aggregate(runs, model_name):
    n = len(runs)
    accuracies = [r[f"{model_name}_summary"]["decision_accuracy"] for r in runs]
    maes = [r[f"{model_name}_summary"]["mae_score"] for r in runs if r[f"{model_name}_summary"]["mae_score"] is not None]
    fprs = [r[f"{model_name}_summary"]["fpr"] for r in runs]
    fnrs = [r[f"{model_name}_summary"]["fnr"] for r in runs]
    p95s = [r[f"{model_name}_summary"]["latency_p95"] for r in runs if r[f"{model_name}_summary"]["latency_p95"] is not None]
    p50s = [r[f"{model_name}_summary"]["latency_p50"] for r in runs if r[f"{model_name}_summary"]["latency_p50"] is not None]
    avgs = [r[f"{model_name}_summary"]["latency_avg"] for r in runs if r[f"{model_name}_summary"]["latency_avg"] is not None]

    return {
        "model": model_name,
        "runs": n,
        "decision_accuracy": {
            "min": min(accuracies),
            "max": max(accuracies),
            "avg": sum(accuracies) / len(accuracies),
        },
        "mae_score": {
            "min": min(maes) if maes else None,
            "max": max(maes) if maes else None,
            "avg": sum(maes) / len(maes) if maes else None,
        },
        "fpr": {
            "min": min(fprs),
            "max": max(fprs),
            "avg": sum(fprs) / len(fprs),
        },
        "fnr": {
            "min": min(fnrs),
            "max": max(fnrs),
            "avg": sum(fnrs) / len(fnrs),
        },
        "latency_p50_ms": {
            "min": min(p50s) if p50s else None,
            "max": max(p50s) if p50s else None,
            "avg": sum(p50s) / len(p50s) if p50s else None,
            "best_run": min(p50s) if p50s else None,
        },
        "latency_p95_ms": {
            "min": min(p95s) if p95s else None,
            "max": max(p95s) if p95s else None,
            "avg": sum(p95s) / len(p95s) if p95s else None,
            "best_run": min(p95s) if p95s else None,
        },
        "latency_avg_ms": {
            "min": min(avgs) if avgs else None,
            "max": max(avgs) if avgs else None,
            "avg": sum(avgs) / len(avgs) if avgs else None,
        },
    }


def determine_winner(lora_agg, gpt_agg):
    """Winner is determined by decision accuracy first, then latency p95, then MAE."""
    lora_acc = lora_agg["decision_accuracy"]["avg"]
    gpt_acc = gpt_agg["decision_accuracy"]["avg"]
    lora_p95 = lora_agg["latency_p95_ms"]["avg"]
    gpt_p95 = gpt_agg["latency_p95_ms"]["avg"]
    lora_mae = lora_agg["mae_score"]["avg"]
    gpt_mae = gpt_agg["mae_score"]["avg"]

    if abs(lora_acc - gpt_acc) > 0.005:
        return "lora" if lora_acc > gpt_acc else "gpt"

    if lora_p95 is not None and gpt_p95 is not None:
        if abs(lora_p95 - gpt_p95) > 100:
            return "lora" if lora_p95 < gpt_p95 else "gpt"

    if lora_mae is not None and gpt_mae is not None:
        return "lora" if lora_mae < gpt_mae else "gpt"

    return "tie"


def main():
    args = parse_args()
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    output_dir = output_path.parent
    runs = []
    for i in range(1, args.repetitions + 1):
        report = run_once(args, i, output_dir)
        runs.append(report)

    lora_agg = aggregate(runs, "lora")
    gpt_agg = aggregate(runs, "gpt")

    final_report = {
        "experiment": "experiment_004",
        "external_validation": {
            "dataset": "HRA-EVAL-V5-EXT",
            "experiment_code": "HRA-EXP-V5-EXT",
            "reference_judge": "gpt-4o",
            "total_records": runs[0]["external_validation"]["total_records"],
        },
        "lora_api_url": args.lora_api_url,
        "gpt_model": args.gpt_model,
        "repetitions": args.repetitions,
        "lora_summary": lora_agg,
        "gpt_summary": gpt_agg,
        "winner": determine_winner(lora_agg, gpt_agg),
        "runs": [
            {
                "run_index": r["_run_meta"]["run_index"],
                "elapsed_seconds": r["_run_meta"]["elapsed_seconds"],
                "output_file": r["_run_meta"]["output_file"],
                "lora_summary": r["lora_summary"],
                "gpt_summary": r["gpt_summary"],
            }
            for r in runs
        ],
    }

    output_path.write_text(json.dumps(final_report, ensure_ascii=False, indent=2), encoding="utf-8")

    print("\n=== AGGREGATED SUMMARY ===")
    print(json.dumps({
        "lora": lora_agg,
        "gpt": gpt_agg,
        "winner": final_report["winner"],
    }, ensure_ascii=False, indent=2))
    print(f"\nReport saved: {output_path}")


if __name__ == "__main__":
    main()
