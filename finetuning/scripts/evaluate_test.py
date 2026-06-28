import json
from pathlib import Path

import torch
from datasets import Dataset
from transformers import AutoModelForCausalLM, AutoTokenizer, Trainer, TrainingArguments
from peft import PeftModel


MODEL_ID = "Qwen/Qwen2.5-1.5B-Instruct"
BASE_DIR = Path("/workspace/hra-finetuning")
TEST_PATH = BASE_DIR / "data/test.jsonl"
RUN_DIR = BASE_DIR / "runs/experiment_001"
BEST_ADAPTER = RUN_DIR / "best_adapter"
OUT_DIR = RUN_DIR / "test_evaluation"


def load_rows(path: Path):
    return [{"messages": json.loads(line)["messages"]} for line in path.read_text(encoding="utf-8").splitlines()]


def to_text(example, tokenizer):
    return {
        "text": tokenizer.apply_chat_template(
            example["messages"],
            tokenize=False,
            add_generation_prompt=False,
        )
    }


def tokenize(example, tokenizer):
    tokens = tokenizer(example["text"], truncation=True, max_length=2048, padding="max_length")
    tokens["labels"] = tokens["input_ids"].copy()
    return tokens


def build_dataset(tokenizer):
    ds = Dataset.from_list(load_rows(TEST_PATH))
    ds = ds.map(lambda x: to_text(x, tokenizer), remove_columns=["messages"])
    ds = ds.map(lambda x: tokenize(x, tokenizer), remove_columns=["text"])
    return ds


def evaluate(model, tokenizer, dataset, name):
    args = TrainingArguments(
        output_dir=str(OUT_DIR / name),
        per_device_eval_batch_size=1,
        report_to="none",
        fp16=True,
    )
    trainer = Trainer(model=model, args=args, eval_dataset=dataset)
    metrics = trainer.evaluate()
    metrics["model_name"] = name
    return metrics


def load_base(tokenizer):
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_ID,
        dtype=torch.float16,
        device_map="auto",
        trust_remote_code=True,
    )
    model.eval()
    return model


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    dataset = build_dataset(tokenizer)

    print("Evaluating Base Qwen...")
    base_model = load_base(tokenizer)
    base_metrics = evaluate(base_model, tokenizer, dataset, "base_qwen")
    del base_model
    torch.cuda.empty_cache()

    print("Evaluating Best LoRA Adapter...")
    lora_base = load_base(tokenizer)
    lora_model = PeftModel.from_pretrained(lora_base, BEST_ADAPTER)
    lora_model.eval()
    lora_metrics = evaluate(lora_model, tokenizer, dataset, "best_lora")
    del lora_model, lora_base
    torch.cuda.empty_cache()

    result = {
        "test_file": str(TEST_PATH),
        "adapter": str(BEST_ADAPTER),
        "base_qwen": base_metrics,
        "best_lora": lora_metrics,
    }

    out_json = OUT_DIR / "test_metrics.json"
    out_json.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps(result, ensure_ascii=False, indent=2))
    print(f"Saved: {out_json}")


if __name__ == "__main__":
    main()
