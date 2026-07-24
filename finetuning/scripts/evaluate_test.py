import argparse
import json
from pathlib import Path

import torch
from datasets import Dataset
from transformers import AutoModelForCausalLM, AutoTokenizer, Trainer, TrainingArguments
from peft import PeftModel


def load_config(config_path: str) -> dict:
    import yaml
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def parse_args():
    parser = argparse.ArgumentParser(description="Eval loss for HRA LoRA")
    parser.add_argument("--config", type=str, default="configs/experiment_003.yaml")
    return parser.parse_args()


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


def tokenize(example, tokenizer, max_length: int = 2048):
    tokens = tokenizer(example["text"], truncation=True, max_length=max_length, padding="max_length")
    tokens["labels"] = tokens["input_ids"].copy()
    return tokens


def build_dataset(tokenizer, test_path: Path, max_length: int = 2048):
    ds = Dataset.from_list(load_rows(test_path))
    ds = ds.map(lambda x: to_text(x, tokenizer), remove_columns=["messages"])
    ds = ds.map(lambda x: tokenize(x, tokenizer, max_length), remove_columns=["text"])
    return ds


def evaluate(model, tokenizer, dataset, name, out_dir: Path, fp16: bool = True):
    args = TrainingArguments(
        output_dir=str(out_dir / name),
        per_device_eval_batch_size=1,
        report_to="none",
        fp16=fp16,
    )
    trainer = Trainer(model=model, args=args, eval_dataset=dataset)
    metrics = trainer.evaluate()
    metrics["model_name"] = name
    return metrics


def load_base(model_id: str, torch_dtype="float16", device_map="auto"):
    dtype = torch.float16 if torch_dtype == "float16" else torch.float32
    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        dtype=dtype,
        device_map=device_map,
        trust_remote_code=True,
    )
    model.eval()
    return model


def main():
    args = parse_args()
    config = load_config(args.config)

    base_dir = Path(config["workspace"]["base_dir"])
    run_dir = base_dir / config["output"]["run_dir"]
    best_adapter = run_dir / "best_adapter"
    test_path = base_dir / config["dataset"]["files"]["test"]
    out_dir = run_dir / "test_evaluation"
    out_dir.mkdir(parents=True, exist_ok=True)

    model_id = config["model"]["id"]
    torch_dtype = config["model"].get("torch_dtype", "float16")
    device_map = config["model"].get("device_map", "auto")
    max_length = config["training"].get("max_length", 2048)
    fp16 = config["training"].get("fp16", True)

    tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    dataset = build_dataset(tokenizer, test_path, max_length)

    print("Evaluating Base Qwen...")
    base_model = load_base(model_id, torch_dtype, device_map)
    base_metrics = evaluate(base_model, tokenizer, dataset, "base_qwen", out_dir, fp16)
    del base_model
    torch.cuda.empty_cache()

    print("Evaluating Best LoRA Adapter...")
    lora_base = load_base(model_id, torch_dtype, device_map)
    lora_model = PeftModel.from_pretrained(lora_base, best_adapter)
    lora_model.eval()
    lora_metrics = evaluate(lora_model, tokenizer, dataset, "best_lora", out_dir, fp16)
    del lora_model, lora_base
    torch.cuda.empty_cache()

    result = {
        "test_file": str(test_path),
        "adapter": str(best_adapter),
        "base_qwen": base_metrics,
        "best_lora": lora_metrics,
    }

    out_json = out_dir / "test_metrics.json"
    out_json.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps(result, ensure_ascii=False, indent=2))
    print(f"Saved: {out_json}")


if __name__ == "__main__":
    main()
