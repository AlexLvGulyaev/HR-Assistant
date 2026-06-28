import json
from pathlib import Path

import torch
from datasets import Dataset
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    TrainingArguments,
)
from peft import LoraConfig
from trl import SFTTrainer


MODEL_ID = "Qwen/Qwen2.5-1.5B-Instruct"
BASE_DIR = Path("/workspace/hra-finetuning")
TRAIN_PATH = BASE_DIR / "data/train.jsonl"
VAL_PATH = BASE_DIR / "data/validation.jsonl"
OUTPUT_DIR = BASE_DIR / "runs/experiment_001"


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


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    train_ds = Dataset.from_list(load_jsonl(TRAIN_PATH))
    val_ds = Dataset.from_list(load_jsonl(VAL_PATH))

    train_ds = train_ds.map(lambda x: to_text(x, tokenizer), remove_columns=["messages"])
    val_ds = val_ds.map(lambda x: to_text(x, tokenizer), remove_columns=["messages"])

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
    )

    trainer = SFTTrainer(
        model=model,
        args=args,
        train_dataset=train_ds,
        eval_dataset=val_ds,
        peft_config=lora_config,
        processing_class=tokenizer,
    )

    trainer.train()

    best_dir = OUTPUT_DIR / "best_adapter"
    trainer.model.save_pretrained(best_dir)
    tokenizer.save_pretrained(best_dir)

    print(f"Best adapter saved to: {best_dir}")


if __name__ == "__main__":
    main()
