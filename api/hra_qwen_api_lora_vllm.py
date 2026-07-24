#!/usr/bin/env python3
"""
Start vLLM OpenAI-compatible server for LoRA Experiment 004.

This is a thin launcher around `vllm.entrypoints.openai.api_server` that
reads the experiment config and exposes the LoRA adapter as an OpenAI model
named `hra_exp004`.

Usage on RunPod:
    cd /workspace
    .venv/bin/python hra_qwen_api_lora_vllm.py --config /workspace/hra-finetuning/configs/experiment_004.yaml --port 8000

Then call it with the standard OpenAI client:
    model = "hra_exp004"
    curl http://127.0.0.1:8000/v1/models
"""

import argparse
import sys
import subprocess
from pathlib import Path


def load_config(config_path: str):
    import yaml

    path = Path(config_path)
    if not path.is_absolute():
        path = Path("/workspace/hra-finetuning") / path

    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def main():
    parser = argparse.ArgumentParser(description="Start vLLM OpenAI server for LoRA Experiment 004")
    parser.add_argument("--config", type=str, default="/workspace/hra-finetuning/configs/experiment_004.yaml")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--host", type=str, default="0.0.0.0")
    parser.add_argument("--gpu-memory-utilization", type=float, default=0.85)
    parser.add_argument("--max-model-len", type=int, default=2048)
    parser.add_argument("--dtype", type=str, default="half", choices=["half", "float16", "bfloat16", "float32"])
    args = parser.parse_args()

    try:
        import vllm
    except ImportError:
        print("ERROR: vllm is not installed.")
        print("Install with: .venv/bin/pip install vllm")
        sys.exit(1)

    config = load_config(args.config)
    model_id = config["model"]["id"]
    lora_r = config["method"]["lora"]["r"]
    base_dir = Path(config["workspace"]["base_dir"])
    adapter_dir = base_dir / config["output"]["best_adapter_dir"]

    if not adapter_dir.exists():
        print(f"ERROR: LoRA adapter not found at {adapter_dir}")
        sys.exit(1)

    lora_module = f"hra_exp004={adapter_dir}"

    cmd = [
        sys.executable,
        "-m",
        "vllm.entrypoints.openai.api_server",
        "--model",
        model_id,
        "--enable-lora",
        "--max-lora-rank",
        str(lora_r),
        "--lora-modules",
        lora_module,
        "--dtype",
        args.dtype,
        "--max-model-len",
        str(args.max_model_len),
        "--gpu-memory-utilization",
        str(args.gpu_memory_utilization),
        "--host",
        args.host,
        "--port",
        str(args.port),
    ]

    print("Starting vLLM OpenAI server for LoRA Experiment 004...")
    print(f"  Base model: {model_id}")
    print(f"  LoRA adapter: {adapter_dir}")
    print(f"  Listening: http://{args.host}:{args.port}")
    print(f"  Command: {' '.join(cmd)}")
    print("")

    # Pass-through to vLLM server; Ctrl+C terminates it cleanly.
    result = subprocess.run(cmd)
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
