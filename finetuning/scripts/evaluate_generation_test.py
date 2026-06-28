import json
import re
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel


MODEL_ID = "Qwen/Qwen2.5-1.5B-Instruct"
BASE_DIR = Path("/workspace/hra-finetuning")
TEST_PATH = BASE_DIR / "data/test.jsonl"
RUN_DIR = BASE_DIR / "runs/experiment_002"
BEST_ADAPTER = RUN_DIR / "best_adapter"
OUT_DIR = RUN_DIR / "generation_test"


def load_jsonl(path: Path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def extract_json(text: str):
    text = text.strip()
    m = re.search(r"\{.*\}", text, re.S)
    if not m:
        return None
    try:
        return json.loads(m.group(0))
    except Exception:
        return None


def get_teacher(row):
    content = row["messages"][2]["content"]
    return json.loads(content)


def build_prompt(row, tokenizer):
    messages = row["messages"][:2]
    return tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)


def load_base():
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_ID,
        dtype=torch.float16,
        device_map="auto",
        trust_remote_code=True,
    )
    model.eval()
    return model


def generate(model, tokenizer, row):
    prompt = build_prompt(row, tokenizer)
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)

    with torch.no_grad():
        out = model.generate(
            **inputs,
            max_new_tokens=768,
            do_sample=False,
            temperature=None,
            top_p=None,
            pad_token_id=tokenizer.eos_token_id,
        )

    generated = out[0][inputs["input_ids"].shape[1]:]
    return tokenizer.decode(generated, skip_special_tokens=True).strip()


def score_one(pred, teacher):
    if pred is None:
        return {
            "valid_json": False,
            "decision_match": False,
            "score_abs_error": None,
            "role_abs_error": None,
            "skills_abs_error": None,
            "experience_abs_error": None,
            "conditions_abs_error": None,
        }

    def ae(field):
        try:
            return abs(float(pred[field]) - float(teacher[field]))
        except Exception:
            return None

    return {
        "valid_json": True,
        "decision_match": pred.get("decision") == teacher.get("decision"),
        "score_abs_error": ae("score"),
        "role_abs_error": ae("role_score"),
        "skills_abs_error": ae("skills_score"),
        "experience_abs_error": ae("experience_score"),
        "conditions_abs_error": ae("conditions_score"),
    }


def mean(values):
    values = [v for v in values if v is not None]
    return sum(values) / len(values) if values else None


def summarize(results):
    n = len(results)
    return {
        "records": n,
        "valid_json_rate": sum(r["metrics"]["valid_json"] for r in results) / n,
        "decision_accuracy": sum(r["metrics"]["decision_match"] for r in results) / n,
        "mae_score": mean([r["metrics"]["score_abs_error"] for r in results]),
        "mae_role": mean([r["metrics"]["role_abs_error"] for r in results]),
        "mae_skills": mean([r["metrics"]["skills_abs_error"] for r in results]),
        "mae_experience": mean([r["metrics"]["experience_abs_error"] for r in results]),
        "mae_conditions": mean([r["metrics"]["conditions_abs_error"] for r in results]),
    }


def evaluate_model(name, model, tokenizer, rows):
    results = []

    for i, row in enumerate(rows, start=1):
        teacher = get_teacher(row)
        raw = generate(model, tokenizer, row)
        pred = extract_json(raw)
        metrics = score_one(pred, teacher)

        results.append({
            "index": i,
            "metadata": row.get("metadata", {}),
            "teacher": teacher,
            "raw_output": raw,
            "parsed_output": pred,
            "metrics": metrics,
        })

        print(f"{name} {i}/{len(rows)} valid={metrics['valid_json']} decision={metrics['decision_match']} score_err={metrics['score_abs_error']}")

    return {
        "summary": summarize(results),
        "results": results,
    }


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    rows = load_jsonl(TEST_PATH)

    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    print("Evaluating Base Qwen generation...")
    base_model = load_base()
    base_eval = evaluate_model("base_qwen", base_model, tokenizer, rows)
    del base_model
    torch.cuda.empty_cache()

    print("Evaluating LoRA checkpoint-72 generation...")
    lora_base = load_base()
    lora_model = PeftModel.from_pretrained(lora_base, BEST_ADAPTER)
    lora_model.eval()
    lora_eval = evaluate_model("best_lora", lora_model, tokenizer, rows)
    del lora_model, lora_base
    torch.cuda.empty_cache()

    report = {
        "test_file": str(TEST_PATH),
        "adapter": str(BEST_ADAPTER),
        "base_qwen": base_eval,
        "best_lora": lora_eval,
    }

    out_json = OUT_DIR / "generation_test_report.json"
    out_json.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    print("\nSUMMARY")
    print(json.dumps({
        "base_qwen": base_eval["summary"],
        "best_lora": lora_eval["summary"],
    }, ensure_ascii=False, indent=2))
    print(f"Saved: {out_json}")


if __name__ == "__main__":
    main()
