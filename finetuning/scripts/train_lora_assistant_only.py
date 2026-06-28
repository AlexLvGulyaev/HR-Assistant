import json
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


MODEL_ID = "Qwen/Qwen2.5-1.5B-Instruct"
BASE_DIR = Path("/workspace/hra-finetuning")
TRAIN_PATH = BASE_DIR / "data/train.jsonl"
VAL_PATH = BASE_DIR / "data/validation.jsonl"
OUTPUT_DIR = BASE_DIR / "runs/experiment_002"
MAX_LENGTH = 2048


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


def tokenize_assistant_only(example, tokenizer):
    prompt_tokens = tokenizer(
        example["prompt_text"],
        add_special_tokens=False,
        truncation=True,
        max_length=MAX_LENGTH,
    )

    full_tokens = tokenizer(
        example["full_text"],
        add_special_tokens=False,
        truncation=True,
        max_length=MAX_LENGTH,
    )

    input_ids = full_tokens["input_ids"]
    attention_mask = full_tokens["attention_mask"]

    labels = input_ids.copy()
    prompt_len = min(len(prompt_tokens["input_ids"]), len(labels))

    # system + user + assistant header не обучаем;
    # loss считаем только по фактическому assistant JSON.
    for i in range(prompt_len):
        labels[i] = -100

    return {
        "input_ids": input_ids,
        "attention_mask": attention_mask,
        "labels": labels,
    }


def prepare_dataset(path: Path, tokenizer):
    rows = load_jsonl(path)
    ds = Dataset.from_list(rows)

    ds = ds.map(
        lambda x: build_prompt_and_answer(x, tokenizer),
        remove_columns=ds.column_names,
    )

    ds = ds.map(
        lambda x: tokenize_assistant_only(x, tokenizer),
        remove_columns=ds.column_names,
    )

    return ds


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    train_ds = prepare_dataset(TRAIN_PATH, tokenizer)
    val_ds = prepare_dataset(VAL_PATH, tokenizer)

    model = AutoModelForCausalLM.from_pretrained(
        MODEL_ID,
        dtype=torch.float16,
        device_map="auto",
        trust_remote_code=True,
    )
    model.config.use_cache = False

    lora_config = LoraConfig(
        r=16,
        lora_alpha=32,
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM",
        target_modules=[
            "q_proj",
            "k_proj",
            "v_proj",
            "o_proj",
            "gate_proj",
            "up_proj",
            "down_proj",
        ],
    )

    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()

    args = TrainingArguments(
        output_dir=str(OUTPUT_DIR),
        num_train_epochs=5,
        per_device_train_batch_size=1,
        per_device_eval_batch_size=1,
        gradient_accumulation_steps=4,
        learning_rate=2e-4,
        logging_steps=5,
        eval_strategy="epoch",
        save_strategy="epoch",
        save_total_limit=5,
        load_best_model_at_end=True,
        metric_for_best_model="eval_loss",
        greater_is_better=False,
        report_to="none",
        fp16=True,
        optim="adamw_torch",
        remove_unused_columns=False,
    )

    trainer = SFTTrainer(
        model=model,
        args=args,
        train_dataset=train_ds,
        eval_dataset=val_ds,
        processing_class=tokenizer,
    )

    trainer.train()

    best_dir = OUTPUT_DIR / "best_adapter"
    trainer.model.save_pretrained(best_dir)
    tokenizer.save_pretrained(best_dir)

    print(f"Best adapter saved to: {best_dir}")


if __name__ == "__main__":
    main()
