import argparse
import json
import time
from pathlib import Path

import torch
from datasets import Dataset
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    TrainingArguments,
)
from peft import LoraConfig, get_peft_model
from trl import SFTTrainer


def load_config(config_path: str) -> dict:
    import yaml
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def parse_args():
    parser = argparse.ArgumentParser(description="Train LoRA adapter for HRA matching (assistant-only loss)")
    parser.add_argument("--config", type=str, default="configs/experiment_003.yaml")
    return parser.parse_args()


def load_jsonl(path: Path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def build_prompt_and_answer(row, tokenizer):
    messages = row["messages"]
    prompt_messages = messages[:2]
    assistant_message = messages[2]

    prompt_text = tokenizer.apply_chat_template(
        prompt_messages,
        tokenize=False,
        add_generation_prompt=True,
    )
    full_text = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=False,
    )
    return {
        "prompt_text": prompt_text,
        "full_text": full_text,
        "assistant_text": assistant_message["content"],
    }


def tokenize_assistant_only(example, tokenizer, max_length: int):
    prompt_tokens = tokenizer(
        example["prompt_text"],
        add_special_tokens=False,
        truncation=True,
        max_length=max_length,
    )
    full_tokens = tokenizer(
        example["full_text"],
        add_special_tokens=False,
        truncation=True,
        max_length=max_length,
    )

    input_ids = full_tokens["input_ids"]
    attention_mask = full_tokens["attention_mask"]
    labels = input_ids.copy()
    prompt_len = min(len(prompt_tokens["input_ids"]), len(labels))

    for i in range(prompt_len):
        labels[i] = -100

    return {
        "input_ids": input_ids,
        "attention_mask": attention_mask,
        "labels": labels,
    }


def prepare_dataset(path: Path, tokenizer, max_length: int):
    rows = load_jsonl(path)
    ds = Dataset.from_list(rows)
    ds = ds.map(
        lambda x: build_prompt_and_answer(x, tokenizer),
        remove_columns=ds.column_names,
    )
    ds = ds.map(
        lambda x: tokenize_assistant_only(x, tokenizer, max_length),
        remove_columns=ds.column_names,
    )
    return ds


def main():
    args = parse_args()
    config = load_config(args.config)

    base_dir = Path(config["workspace"]["base_dir"])
    train_path = base_dir / config["dataset"]["files"]["train"]
    val_path = base_dir / config["dataset"]["files"]["validation"]
    output_dir = base_dir / config["output"]["run_dir"]
    output_dir.mkdir(parents=True, exist_ok=True)

    model_id = config["model"]["id"]
    lora_cfg = config["method"]["lora"]
    train_cfg = config["training"]
    max_length = train_cfg.get("max_length", 2048)

    start_time = time.time()

    tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    train_ds = prepare_dataset(train_path, tokenizer, max_length)
    val_ds = prepare_dataset(val_path, tokenizer, max_length)

    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        dtype=torch.float16,
        device_map="auto",
        trust_remote_code=True,
    )
    model.config.use_cache = False

    lora_config = LoraConfig(
        r=lora_cfg["r"],
        lora_alpha=lora_cfg["alpha"],
        lora_dropout=lora_cfg["dropout"],
        bias=lora_cfg["bias"],
        task_type=lora_cfg["task_type"],
        target_modules=lora_cfg["target_modules"],
    )

    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()

    args_train = TrainingArguments(
        output_dir=str(output_dir),
        num_train_epochs=train_cfg["num_train_epochs"],
        per_device_train_batch_size=train_cfg["per_device_train_batch_size"],
        per_device_eval_batch_size=train_cfg["per_device_eval_batch_size"],
        gradient_accumulation_steps=train_cfg["gradient_accumulation_steps"],
        learning_rate=train_cfg["learning_rate"],
        logging_steps=train_cfg["logging_steps"],
        eval_strategy=train_cfg["eval_strategy"],
        save_strategy=train_cfg["save_strategy"],
        save_total_limit=train_cfg["save_total_limit"],
        load_best_model_at_end=train_cfg["load_best_model_at_end"],
        metric_for_best_model=train_cfg["metric_for_best_model"],
        greater_is_better=train_cfg["greater_is_better"],
        report_to=train_cfg["report_to"],
        fp16=train_cfg["fp16"],
        optim=train_cfg["optim"],
        seed=train_cfg.get("seed", 42),
        remove_unused_columns=False,
    )

    trainer = SFTTrainer(
        model=model,
        args=args_train,
        train_dataset=train_ds,
        eval_dataset=val_ds,
        processing_class=tokenizer,
    )

    trainer.train()

    best_dir = output_dir / "best_adapter"
    trainer.model.save_pretrained(best_dir)
    tokenizer.save_pretrained(best_dir)

    elapsed = time.time() - start_time
    peak_vram_mb = torch.cuda.max_memory_allocated() / 1024 / 1024 if torch.cuda.is_available() else 0

    report = {
        "experiment_id": config["experiment"]["id"],
        "model_id": model_id,
        "output_dir": str(output_dir),
        "best_adapter_dir": str(best_dir),
        "best_checkpoint": str(trainer.state.best_model_checkpoint) if trainer.state.best_model_checkpoint else None,
        "best_metric": trainer.state.best_metric,
        "num_epochs": train_cfg["num_train_epochs"],
        "elapsed_seconds": elapsed,
        "peak_vram_mb": peak_vram_mb,
        "completed": True,
    }
    report_path = output_dir / "training_report.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Best adapter saved to: {best_dir}")
    print(f"Training report saved to: {report_path}")


if __name__ == "__main__":
    main()
