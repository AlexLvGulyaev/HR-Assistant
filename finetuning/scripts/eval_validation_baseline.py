import json
from pathlib import Path

import torch
from datasets import Dataset
from transformers import AutoModelForCausalLM, AutoTokenizer, Trainer, TrainingArguments


MODEL_ID = "Qwen/Qwen2.5-1.5B-Instruct"
BASE_DIR = Path("/workspace/hra-finetuning")
VAL_PATH = BASE_DIR / "data/validation.jsonl"
OUTPUT_DIR = BASE_DIR / "runs/experiment_001/baseline_validation"


def load_jsonl(path: Path):
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        item = json.loads(line)
        rows.append({"messages": item["messages"]})
    return rows


def to_text(example, tokenizer):
    return {
        "text": tokenizer.apply_chat_template(
            example["messages"],
            tokenize=False,
            add_generation_prompt=False,
        )
    }


def tokenize(example, tokenizer):
    tokens = tokenizer(
        example["text"],
        truncation=True,
        max_length=2048,
        padding="max_length",
    )
    tokens["labels"] = tokens["input_ids"].copy()
    return tokens


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    rows = Dataset.from_list(load_jsonl(VAL_PATH))
    rows = rows.map(lambda x: to_text(x, tokenizer), remove_columns=["messages"])
    rows = rows.map(lambda x: tokenize(x, tokenizer), remove_columns=["text"])

    model = AutoModelForCausalLM.from_pretrained(
        MODEL_ID,
        dtype=torch.float16,
        device_map="auto",
        trust_remote_code=True,
    )
    model.eval()

    args = TrainingArguments(
        output_dir=str(OUTPUT_DIR),
        per_device_eval_batch_size=1,
        report_to="none",
        fp16=True,
    )

    trainer = Trainer(
        model=model,
        args=args,
        eval_dataset=rows,
    )

    metrics = trainer.evaluate()

    out_path = OUTPUT_DIR / "metrics.json"
    out_path.write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps(metrics, ensure_ascii=False, indent=2))
    print(f"Saved: {out_path}")


if __name__ == "__main__":
    main()
