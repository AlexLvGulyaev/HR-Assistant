"""
Runtime Smoke Test for Experiment 003
=====================================

Запускает локальные HTTP-запросы к hra_qwen_api_lora.py по фиксированному
smoke_set.jsonl и формирует runtime_smoke_report.json.

Использование на RunPod:
    /workspace/hra-finetuning/.venv/bin/python scripts/runtime_smoke_test.py \
        --config configs/experiment_003.yaml
"""

import argparse
import json
import time
import urllib.request
from pathlib import Path


def parse_args():
    parser = argparse.ArgumentParser(description="Runtime smoke test for HRA LoRA API")
    parser.add_argument(
        "--config",
        type=str,
        default="configs/experiment_003.yaml",
        help="Path to experiment config YAML",
    )
    parser.add_argument(
        "--api-url",
        type=str,
        default="http://127.0.0.1:8000/v1/chat/completions",
        help="LoRA API URL",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Output report path (default: from config)",
    )
    return parser.parse_args()


def load_config(config_path: str) -> dict:
    try:
        import yaml
        with open(config_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except Exception as e:
        raise RuntimeError(f"Cannot read config {config_path}: {e}")


def load_smoke_set(config: dict) -> list:
    base_dir = Path(config["workspace"]["base_dir"])
    smoke_file = config["runtime_smoke"]["file"]
    path = base_dir / smoke_file
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def send_request(api_url: str, messages: list, schema: dict | None = None) -> dict:
    payload = {
        "model": "hra_exp004",
        "messages": messages,
        "max_tokens": 512,
        "temperature": 0,
    }
    if schema:
        payload["response_format"] = {
            "type": "json_schema",
            "json_schema": {"name": "hra_matching", "schema": schema},
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
            return {"status_code": resp.status, "body": body, "latency_ms": latency_ms}
    except urllib.error.HTTPError as e:
        latency_ms = int((time.time() - start) * 1000)
        return {
            "status_code": e.code,
            "body": e.read().decode("utf-8"),
            "latency_ms": latency_ms,
            "error": True,
        }
    except Exception as e:
        latency_ms = int((time.time() - start) * 1000)
        return {"status_code": None, "body": str(e), "latency_ms": latency_ms, "error": True}


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
        # Try to find first JSON object
        decoder = json.JSONDecoder()
        for i, ch in enumerate(text):
            if ch == "{":
                try:
                    obj, _ = decoder.raw_decode(text[i:])
                    return obj
                except json.JSONDecodeError:
                    continue
        return None


def evaluate_response(response: dict, expected_category: str) -> dict:
    """Simple pass/fail logic per category."""
    result = {
        "valid_json": False,
        "decision": None,
        "score": None,
        "match_unexpected": False,
        "passed": False,
    }

    if response.get("error") or response.get("status_code") != 200:
        return result

    try:
        body = json.loads(response["body"])
        content = body["choices"][0]["message"]["content"]
        parsed = extract_json(content)
    except Exception:
        return result

    if not parsed:
        return result

    result["valid_json"] = True
    result["decision"] = parsed.get("decision")
    result["score"] = parsed.get("score")

    decision = parsed.get("decision")
    score = parsed.get("score")

    if expected_category == "positive":
        result["passed"] = decision == "match" and score is not None and score >= 60
    elif expected_category in ("obvious_negative", "hard_negative"):
        result["passed"] = decision == "no_match"
    elif expected_category == "edge_case":
        result["passed"] = decision in ("match", "no_match") and score is not None
    elif expected_category == "invalid_input":
        result["passed"] = True  # any deterministic response is acceptable
    elif expected_category == "stability_repeat":
        result["passed"] = decision == "match" and score is not None and score >= 60

    if expected_category in ("obvious_negative", "hard_negative") and decision == "match":
        result["match_unexpected"] = True

    return result


def main():
    args = parse_args()
    config = load_config(args.config)
    base_dir = Path(config["workspace"]["base_dir"])
    run_dir = base_dir / config["output"]["run_dir"]
    run_dir.mkdir(parents=True, exist_ok=True)

    smoke_set = load_smoke_set(config)

    output_path = Path(args.output) if args.output else run_dir / "runtime_smoke_report.json"

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
    }

    results = []
    for row in smoke_set:
        meta = row.get("metadata", {})
        case_code = meta.get("case_code", "unknown")
        category = meta.get("category", "unknown")
        messages = row["messages"]

        response = send_request(args.api_url, messages, schema)
        evaluation = evaluate_response(response, category)

        results.append({
            "case_code": case_code,
            "category": category,
            "vacancy_title": meta.get("vacancy_title"),
            "api_response": response,
            "evaluation": evaluation,
        })

        status = "PASS" if evaluation["passed"] else "FAIL"
        print(f"[{status}] {case_code} ({category}) decision={evaluation['decision']} score={evaluation['score']} latency={response['latency_ms']}ms")

    passed = sum(1 for r in results if r["evaluation"]["passed"])
    total = len(results)
    unexpected_matches = sum(1 for r in results if r["evaluation"]["match_unexpected"])

    report = {
        "experiment_id": config["experiment"]["id"],
        "api_url": args.api_url,
        "total_cases": total,
        "passed": passed,
        "failed": total - passed,
        "pass_rate": passed / total if total else 0,
        "unexpected_matches": unexpected_matches,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "results": results,
    }

    output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nSummary: {passed}/{total} passed, {unexpected_matches} unexpected matches")
    print(f"Report saved: {output_path}")


if __name__ == "__main__":
    main()
