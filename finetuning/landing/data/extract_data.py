#!/usr/bin/env python3
"""Extract normalized experiment data for the HR Assistant LoRA landing page."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3] / "finetuning" / "runs"
DATA_ROOT = Path(__file__).resolve().parents[3] / "finetuning" / "data"
CONFIGS_ROOT = Path(__file__).resolve().parents[3] / "finetuning" / "configs"


def load(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def safe(d, *keys, default=None):
    for k in keys:
        if isinstance(d, dict) and k in d:
            d = d[k]
        else:
            return default
    return d


def best_eval_loss(trainer_state):
    logs = trainer_state.get("log_history", [])
    losses = [(i, l) for i, l in enumerate(logs) if l.get("eval_loss") is not None]
    if not losses:
        return None, None
    best = min(losses, key=lambda x: x[1]["eval_loss"])
    return best[1]["eval_loss"], best[0]


def final_train_loss(trainer_state):
    logs = trainer_state.get("log_history", [])
    losses = [l.get("loss") for l in logs if l.get("loss") is not None]
    return losses[-1] if losses else None


def extract_generation_report(path):
    data = load(path)
    lora_data = data.get("best_lora", data.get("lora", {}))
    summary = lora_data.get("summary", data.get("lora_summary", {}))
    base_summary = data.get("base_qwen", {}).get("summary", {})
    return {
        "records": summary.get("records"),
        "valid_json_rate": summary.get("valid_json_rate"),
        "decision_accuracy": summary.get("decision_accuracy"),
        "mae_score": summary.get("mae_score"),
        "mae_role": summary.get("mae_role"),
        "mae_skills": summary.get("mae_skills"),
        "mae_experience": summary.get("mae_experience"),
        "mae_conditions": summary.get("mae_conditions"),
        "base": {
            "records": base_summary.get("records"),
            "valid_json_rate": base_summary.get("valid_json_rate"),
            "decision_accuracy": base_summary.get("decision_accuracy"),
            "mae_score": base_summary.get("mae_score"),
        },
        "results": lora_data.get("results", []),
        "base_results": data.get("base_qwen", {}).get("results", []),
    }


def find_trainer_state(exp_dir):
    # Prefer top-level trainer_state.json if it exists (003/004 have it)
    top = exp_dir / "trainer_state.json"
    if top.exists():
        return top
    files = sorted(exp_dir.rglob("trainer_state.json"))
    # Return the one with highest step count (final checkpoint)
    if not files:
        return None
    candidates = []
    for f in files:
        try:
            state = load(f)
            logs = state.get("log_history", [])
            steps = [l.get("step", 0) for l in logs if l.get("step") is not None]
            candidates.append((max(steps) if steps else 0, f))
        except Exception:
            continue
    return max(candidates, key=lambda x: x[0])[1] if candidates else files[-1]


def training_curves(trainer_state):
    logs = trainer_state.get("log_history", [])
    train_steps = []
    train_loss = []
    eval_steps = []
    eval_loss = []
    token_accuracy = []
    lr = []
    for l in logs:
        if l.get("loss") is not None:
            train_steps.append(l.get("step", len(train_steps)))
            train_loss.append(l["loss"])
            lr.append(l.get("learning_rate"))
        if l.get("eval_loss") is not None:
            eval_steps.append(l.get("step"))
            eval_loss.append(l["eval_loss"])
            token_accuracy.append(l.get("eval_token_accuracy", l.get("token_accuracy")))
    return {
        "train_steps": train_steps,
        "train_loss": train_loss,
        "eval_steps": eval_steps,
        "eval_loss": eval_loss,
        "token_accuracy": token_accuracy,
        "learning_rate": lr,
    }


def best_checkpoint_info(exp_dir, trainer_state, adapter_config):
    """Extract best checkpoint epoch/step from trainer_state and training_report."""
    info = {"path": None, "step": None, "epoch": None}
    training_report_path = exp_dir / "training_report.json"
    if training_report_path.exists():
        try:
            tr = load(training_report_path)
            info["path"] = safe(tr, "best_checkpoint")
        except Exception:
            pass
    logs = trainer_state.get("log_history", [])
    eval_logs = [(i, l) for i, l in enumerate(logs) if l.get("eval_loss") is not None]
    if not eval_logs:
        return info
    best_idx, best_log = min(eval_logs, key=lambda x: x[1]["eval_loss"])
    info["step"] = best_log.get("step")
    # Prefer the epoch field from the eval log; fall back to step inference
    if "epoch" in best_log:
        info["epoch"] = int(best_log["epoch"])
    else:
        # infer epoch: total planned epochs = 5 for all experiments
        num_epochs = 5
        max_step = max((l.get("step", 0) for l in logs if l.get("step") is not None), default=0)
        if max_step and info["step"] is not None:
            steps_per_epoch = max_step / num_epochs
            if steps_per_epoch:
                info["epoch"] = max(1, int(round(info["step"] / steps_per_epoch)))
    return info


def concrete_example(result, kind):
    """Build an anonymized concrete example card from a generation-test result."""
    meta = result.get("metadata", {})
    teacher = result.get("teacher", {})
    pred = result.get("parsed_output", result.get("lora_prediction", {}))
    return {
        "kind": kind,
        "case_code": meta.get("case_code"),
        "case_type": meta.get("case_type"),
        "vacancy_title": meta.get("vacancy_title"),
        "reference_decision": teacher.get("decision"),
        "reference_score": teacher.get("score"),
        "predicted_decision": pred.get("decision"),
        "predicted_score": pred.get("score"),
        "predicted_reason": pred.get("reason", "")[:200],
        "source": "generation_test_report.json",
    }


def extract_concrete_examples(exp_data, gen_report):
    examples = {}
    base_results = gen_report.get("base_results", [])
    lora_results = gen_report.get("results", [])
    # Base wrong answer: reference no_match, base predicted match
    for r in base_results:
        teacher = r.get("teacher", {})
        pred = r.get("parsed_output", {})
        if teacher.get("decision") == "no_match" and pred.get("decision") == "match":
            examples["base_wrong"] = concrete_example(r, "base_wrong")
            break
    # Hard-negative false positive: reference no_match, lora predicted match
    for r in lora_results:
        teacher = r.get("teacher", {})
        pred = r.get("parsed_output", {})
        if teacher.get("decision") == "no_match" and pred.get("decision") == "match":
            examples["hard_negative_fp"] = concrete_example(r, "hard_negative_fp")
            break
    # False negatives: reference match, lora predicted no_match
    fn_examples = []
    for r in lora_results:
        teacher = r.get("teacher", {})
        pred = r.get("parsed_output", {})
        if teacher.get("decision") == "match" and pred.get("decision") == "no_match":
            fn_examples.append(concrete_example(r, "false_negative"))
    if fn_examples:
        examples["false_negatives"] = fn_examples[:3]
    return examples


def load_manifest(exp):
    manifest_path = DATA_ROOT / f"manifest_experiment_{exp}.json"
    if manifest_path.exists():
        return load(manifest_path)
    return None


def dataset_change_log():
    """Build dataset change log from manifests and configs.

    Experiment 002 reused the same 90 records as Exp 001 (only judge labels / split
    strategy changed). When a manifest is missing, carry forward the previous
    experiment's record count rather than leaving a misleading null/0.
    """
    log = []
    previous_total = None
    for exp in ["001", "002", "003", "004"]:
        manifest_path = DATA_ROOT / f"manifest_experiment_{exp}.json"
        manifest = load(manifest_path) if manifest_path.exists() else None
        cfg_path = CONFIGS_ROOT / f"experiment_{exp}.yaml"
        total = None
        if manifest:
            total = manifest.get("total_records")
        elif cfg_path.exists():
            # rough fallback: read yaml split numbers
            import yaml
            try:
                cfg = yaml.safe_load(cfg_path.read_text())
                total = sum(cfg.get("dataset", {}).get("split", {}).values())
            except Exception:
                pass
        if total is None and previous_total is not None:
            total = previous_total
        previous_total = total
        entry = {"experiment": exp, "total_records": total, "manifest": str(manifest_path) if manifest else None}
        if manifest and "splits" in manifest:
            entry["splits"] = {
                k: {"records": v.get("records"), "case_type_distribution": v.get("case_type_distribution", {})}
                for k, v in manifest["splits"].items()
            }
        log.append(entry)
    return log


def source_file_inventory():
    """Map visual asset IDs to source files and MAR-ID."""
    inventory = []
    # per-experiment source files
    for exp in ["001", "002", "003", "004"]:
        exp_dir = ROOT / f"experiment_{exp}"
        base = f"finetuning/runs/experiment_{exp}"
        inventory.extend([
            {"visual": f"G-001 / Exp {exp}", "mar": f"MAR-{exp}-006", "files": [f"{base}/trainer_state.json"]},
            {"visual": f"G-002 / Exp {exp}", "mar": f"MAR-{exp}-006", "files": [f"{base}/trainer_state.json"]},
            {"visual": f"G-004 / Exp {exp}", "mar": f"MAR-{exp}-009", "files": [f"{base}/generation_test/generation_test_report.json"]},
        ])
    inventory.extend([
        {"visual": "G-008", "mar": "MAR-004-013", "files": ["finetuning/runs/experiment_004/external_validation_report.json"]},
        {"visual": "G-009", "mar": "MAR-003-011 / MAR-004-011", "files": [
            "finetuning/runs/experiment_003/runtime_smoke_report.json",
            "finetuning/runs/experiment_004/runtime_smoke_report.json",
        ]},
        {"visual": "G-010 / G-012", "mar": "MAR-004-019", "files": ["finetuning/runs/experiment_004/latency_optimization/latency_profile_report.json"]},
        {"visual": "G-011", "mar": "MAR-004-017 / MAR-004-018", "files": [
            "finetuning/runs/experiment_004/latency_optimization/engine_benchmark_report.json",
            "finetuning/runs/experiment_004/latency_optimization/engine_benchmark_report_vllm.json",
        ]},
        {"visual": "G-014", "mar": "MAR-004-013 / MAR-004-015", "files": [
            "finetuning/runs/experiment_004/external_validation_report.json",
            "finetuning/runs/experiment_004/gpt_comparison_report_v2.json",
        ]},
        {"visual": "G-015", "mar": "MAR-004-014 / MAR-004-015", "files": [
            "finetuning/runs/experiment_004/gpt_comparison_report.json",
            "finetuning/runs/experiment_004/gpt_comparison_report_v2.json",
        ]},
        {"visual": "G-013", "mar": "MAR-003-013 / MAR-004-013", "files": [
            "finetuning/data/manifest_experiment_003.json",
            "finetuning/data/manifest_experiment_004.json",
        ]},
    ])
    return inventory


def main():
    data = {
        "experiments": {},
        "external_validation": None,
        "gpt_comparison": None,
        "smoke": {},
        "smoke_rerun": {},
        "latency": {},
        "engine_benchmark": {},
        "dataset_change_log": dataset_change_log(),
        "source_inventory": source_file_inventory(),
        "concrete_examples": {},
    }

    for exp in ["001", "002", "003", "004"]:
        exp_dir = ROOT / f"experiment_{exp}"
        if not exp_dir.exists():
            continue

        trainer_path = find_trainer_state(exp_dir)
        if not trainer_path:
            continue
        trainer = load(trainer_path)
        adapter_path = next((exp_dir / "best_adapter").glob("adapter_config.json"), None)
        adapter = load(adapter_path) if adapter_path else {}

        curves = training_curves(trainer)
        best_loss, _ = best_eval_loss(trainer)
        bc_info = best_checkpoint_info(exp_dir, trainer, adapter)

        exp_data = {
            "id": f"experiment_{exp}",
            "best_eval_loss": best_loss,
            "final_train_loss": final_train_loss(trainer),
            "best_checkpoint": bc_info,
            "adapter": {
                "r": adapter.get("r"),
                "lora_alpha": adapter.get("lora_alpha"),
                "lora_dropout": adapter.get("lora_dropout"),
                "target_modules": adapter.get("target_modules", []),
                "base_model": adapter.get("base_model_name_or_path"),
            },
        }

        gen_path = exp_dir / "generation_test" / "generation_test_report.json"
        if gen_path.exists():
            gen = extract_generation_report(gen_path)
            exp_data["generation_test"] = gen
            # extract concrete examples per experiment
            examples = extract_concrete_examples(exp_data, gen)
            if examples:
                data["concrete_examples"][exp] = examples

        test_path = exp_dir / "test_evaluation" / "test_metrics.json"
        if test_path.exists():
            test = load(test_path)
            exp_data["test_eval_loss"] = {
                "base": safe(test, "base_qwen", "eval_loss"),
                "lora": safe(test, "best_lora", "eval_loss", default=safe(test, "lora", "eval_loss")),
            }

        smoke_path = exp_dir / "runtime_smoke_report.json"
        if smoke_path.exists():
            smoke = load(smoke_path)
            data["smoke"][exp] = {
                "total": smoke.get("total_cases"),
                "passed": smoke.get("passed"),
                "failed": smoke.get("failed"),
                "pass_rate": smoke.get("pass_rate"),
                "latency_range": smoke.get("latency_range"),
                "categories": smoke.get("categories", []),
            }

        training_report_path = exp_dir / "training_report.json"
        if training_report_path.exists():
            tr = load(training_report_path)
            exp_data["training"] = {
                "peak_vram_mb": safe(tr, "peak_vram_mb"),
                "training_time_s": safe(tr, "training_time_s"),
                "best_checkpoint": safe(tr, "best_checkpoint"),
                "final_checkpoint": safe(tr, "final_checkpoint"),
            }

        # keep per-experiment curves separately
        data.setdefault("curves", {})[exp] = curves
        data["experiments"][exp] = exp_data

    # External validation (Exp 004)
    ext_path = ROOT / "experiment_004" / "external_validation_report.json"
    if ext_path.exists():
        ev = load(ext_path)
        data["external_validation"] = {
            "lora": ev.get("lora_summary", {}),
            "gpt": ev.get("gpt_summary", {}),
            "scatter": [
                {
                    "ref_score": r["reference"]["score"],
                    "lora_score": r["lora_prediction"]["score"],
                    "decision_match": r["lora_metrics"]["decision_match"],
                    "case_type": r["metadata"].get("case_type"),
                    "vacancy": r["metadata"].get("vacancy_title"),
                }
                for r in ev.get("results", [])
                if "reference" in r and "lora_prediction" in r
            ],
        }

    # GPT comparison (Exp 004)
    gpt_path = ROOT / "experiment_004" / "gpt_comparison_report_v2.json"
    if gpt_path.exists():
        gc = load(gpt_path)
        data["gpt_comparison"] = {
            "lora": gc.get("lora_summary", {}),
            "gpt": gc.get("gpt_summary", {}),
        }

    # Latency profile (Exp 004)
    prof_path = ROOT / "experiment_004" / "latency_optimization" / "latency_profile_report.json"
    if prof_path.exists():
        prof = load(prof_path)
        data["latency"]["stage_profile"] = prof.get("stage_summary", prof)

    # Engine benchmark
    def summarize_engine(report):
        summary = {}
        for e in report.get("engines", []):
            name = e.get("engine")
            if not name:
                continue
            summary[name] = {
                "mean_latency_ms": e.get("latency_avg_ms"),
                "p50_latency_ms": e.get("latency_p50_ms"),
                "p95_latency_ms": e.get("latency_p95_ms"),
                "p99_latency_ms": e.get("latency_p99_ms"),
                "decision_accuracy": e.get("decision_accuracy"),
                "mae_score": e.get("mae_score"),
                "valid_json_rate": e.get("valid_json_rate"),
                "n": e.get("records"),
            }
        return summary

    eng_path = ROOT / "experiment_004" / "latency_optimization" / "engine_benchmark_report.json"
    vllm_path = ROOT / "experiment_004" / "latency_optimization" / "engine_benchmark_report_vllm.json"
    if eng_path.exists():
        eng = load(eng_path)
        data["engine_benchmark"].update(summarize_engine(eng))
    if vllm_path.exists():
        vllm = load(vllm_path)
        data["engine_benchmark"].update(summarize_engine(vllm))

    # Optimized external validation latency
    opt_path = ROOT / "experiment_004" / "latency_optimization" / "external_validation_optimized_report.json"
    if opt_path.exists():
        opt = load(opt_path)
        data["latency"]["optimized"] = opt.get("summary", opt)

    # Smoke rerun (Exp 004 latency optimization)
    rerun_smoke_path = ROOT / "experiment_004" / "latency_optimization" / "runtime_smoke_report.json"
    if rerun_smoke_path.exists():
        smoke = load(rerun_smoke_path)
        data["smoke_rerun"]["004_optimized"] = {
            "total": smoke.get("total_cases"),
            "passed": smoke.get("passed"),
            "failed": smoke.get("failed"),
            "pass_rate": smoke.get("pass_rate"),
            "categories": smoke.get("categories", []),
        }

    out_path = Path(__file__).resolve().parent / "experimentData.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Wrote {out_path}")

    js_path = Path(__file__).resolve().parent / "experimentData.js"
    with open(js_path, "w", encoding="utf-8") as f:
        f.write("/* Auto-generated by extract_data.py — DO NOT EDIT MANUALLY */\n")
        f.write("const experimentData = ")
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write(";\n")
        f.write("if (typeof module !== 'undefined' && module.exports) { module.exports = experimentData; }\n")
    print(f"Wrote {js_path}")


if __name__ == "__main__":
    main()
