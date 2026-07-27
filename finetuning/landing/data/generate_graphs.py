#!/usr/bin/env python3
"""Generate remaining SVG graphs for the HR Assistant LoRA landing page."""
import json
from pathlib import Path
from math import pi, cos, sin

ROOT = Path(__file__).resolve().parents[3] / "finetuning" / "runs"
OUT = Path(__file__).resolve().parents[2] / "assets" / "visuals"
OUT.mkdir(parents=True, exist_ok=True)

# Landing palette
BG = "#0d0d10"
PANEL = "#1a1a24"
TEXT = "#e8e8ec"
MUTED = "#8a8a9a"
TEAL = "#4ECDC4"
AMBER = "#FFB347"
RED = "#FF6B6B"
GREEN = "#96CEB4"
GRID = "#2a2a36"
WHITE = "#ffffff"


def load(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_svg(name, content):
    (OUT / name).write_text(content, encoding="utf-8")
    print(f"Wrote {OUT / name}")


def svg_head(w, h, title=""):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="{title}">\n'
        f'<defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L0,6 L9,3 z" fill="#ffffff"/></marker></defs>\n'
        f'<rect width="{w}" height="{h}" fill="{BG}" rx="8"/>\n'
    )


def svg_foot():
    return "</svg>\n"


def text(x, y, content, fill=TEXT, size=12, anchor="start", weight="normal", transform=None):
    tr = f' transform="{transform}"' if transform else ""
    return f'<text x="{x}" y="{y}" fill="{fill}" font-size="{size}" font-family="Inter, sans-serif" text-anchor="{anchor}" font-weight="{weight}"{tr}>{content}</text>\n'


def line(x1, y1, x2, y2, stroke=MUTED, width=1, dash=None):
    dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{stroke}" stroke-width="{width}"{dash_attr}/>\n'


def rect(x, y, w, h, fill=PANEL, stroke=GRID, radius=0, opacity=1.0):
    r = f' rx="{radius}"' if radius else ""
    op = f' opacity="{opacity}"' if opacity != 1.0 else ""
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" stroke="{stroke}" stroke-width="1"{r}{op}/>\n'


# ---------------------------------------------------------------------------
# G-001 Loss Curves — All Experiments (small multiples with eval + best epoch)
# ---------------------------------------------------------------------------
def generate_g001():
    W, H = 900, 520
    data = load(Path(__file__).resolve().parent / "experimentData.json")
    curves = data.get("curves", {})
    experiments = ["001", "002", "003", "004"]
    colors = [TEAL, AMBER, RED, GREEN]
    svg = svg_head(W, H, "Loss curves for all experiments")
    svg += text(30, 30, "Training & validation loss by experiment", size=16, weight="600")
    svg += text(30, 50, "Best checkpoint is not always the last. Train loss falls, eval loss eventually rises.", fill=MUTED, size=11)

    cols, rows = 2, 2
    panel_w, panel_h = 380, 190
    start_x, start_y = 50, 80
    gap_x, gap_y = 30, 25
    global_max = 1.0

    for idx, exp in enumerate(experiments):
        c = curves.get(exp, {})
        train = c.get("train_loss", [])
        eval_loss = c.get("eval_loss", [])
        eval_steps = c.get("eval_steps", [])
        best = data["experiments"][exp]["best_checkpoint"]
        best_epoch = best.get("epoch")
        best_step = best.get("step")
        col = idx % cols
        row = idx // cols
        px = start_x + col * (panel_w + gap_x)
        py = start_y + row * (panel_h + gap_y)
        svg += rect(px, py, panel_w, panel_h, fill=PANEL, radius=6)
        # grid
        for i in range(5):
            y = py + panel_h - (i / 4) * panel_h
            svg += line(px, y, px + panel_w, y, stroke=GRID)
            svg += text(px - 8, y + 4, f"{i * 0.25:.2f}", fill=MUTED, size=8, anchor="end")
        # train curve
        if train:
            n = len(train)
            pts = " ".join(f"{px + (i / max(n - 1, 1)) * panel_w},{py + panel_h - (v / global_max) * panel_h}" for i, v in enumerate(train))
            svg += f'<polyline points="{pts}" fill="none" stroke="{colors[idx]}" stroke-width="1.5" opacity="0.75"/>\n'
        # eval curve
        if eval_loss and eval_steps:
            max_step = max(train_steps) if (train_steps := c.get("train_steps", [])) else max(eval_steps)
            pts = " ".join(f"{px + (s / max(max_step, 1)) * panel_w},{py + panel_h - (v / global_max) * panel_h}" for s, v in zip(eval_steps, eval_loss))
            svg += f'<polyline points="{pts}" fill="none" stroke="{colors[idx]}" stroke-width="2.5" stroke-dasharray="4,2" opacity="0.95"/>\n'
        # best checkpoint marker
        if best_step is not None and train:
            max_step = max(c.get("train_steps", [])) or 1
            bx = px + (best_step / max_step) * panel_w
            svg += f'<line x1="{bx}" y1="{py}" x2="{bx}" y2="{py + panel_h}" stroke="{WHITE}" stroke-width="1" stroke-dasharray="3,3" opacity="0.8"/>\n'
            svg += text(bx + 4, py + 14, f"best ep{best_epoch}", fill=WHITE, size=8, weight="600")
        # label
        svg += text(px + panel_w / 2, py + panel_h + 16, f"Exp {exp}", fill=colors[idx], size=12, anchor="middle", weight="600")

    # legend
    svg += rect(start_x + 2 * (panel_w + gap_x) - 120, start_y - 10, 12, 12, fill=WHITE, stroke="none", radius=2, opacity=0.6)
    svg += text(start_x + 2 * (panel_w + gap_x) - 100, start_y, "train", fill=MUTED, size=10)
    svg += rect(start_x + 2 * (panel_w + gap_x) - 50, start_y - 10, 12, 12, fill=WHITE, stroke="none", radius=2)
    svg += text(start_x + 2 * (panel_w + gap_x) - 30, start_y, "eval", fill=MUTED, size=10)
    svg += line(start_x + 2 * (panel_w + gap_x) - 120, start_y + 18, start_x + 2 * (panel_w + gap_x) - 120, start_y + 30, stroke=WHITE, width=1, dash="3,3")
    svg += text(start_x + 2 * (panel_w + gap_x) - 100, start_y + 28, "best checkpoint", fill=MUTED, size=10)

    svg += svg_foot()
    save_svg("G-001-loss-curves.svg", svg)


# ---------------------------------------------------------------------------
# G-016 Per-Experiment Best Epoch Markers
# ---------------------------------------------------------------------------
def generate_g016():
    W, H = 640, 320
    data = load(Path(__file__).resolve().parent / "experimentData.json")
    svg = svg_head(W, H, "Best epoch per experiment")
    svg += text(30, 30, "Best epoch per experiment", size=16, weight="600")
    svg += text(30, 50, "Best checkpoint was never the final epoch", fill=MUTED, size=11)

    experiments = ["001", "002", "003", "004"]
    labels = ["Exp 001", "Exp 002", "Exp 003", "Exp 004"]
    colors = [TEAL, AMBER, RED, GREEN]
    epochs = [data["experiments"][e]["best_checkpoint"]["epoch"] for e in experiments]
    max_epoch = 5
    bar_w = 70
    gap = 60
    start_x = 80
    base_y = 260
    for i, (ep, lab, c) in enumerate(zip(epochs, labels, colors)):
        h = (ep / max_epoch) * 160
        svg += rect(start_x + i * (bar_w + gap), base_y - h, bar_w, h, fill=c, stroke="none", radius=4)
        svg += text(start_x + i * (bar_w + gap) + bar_w / 2, base_y - h - 12, f"ep {ep}", fill=c, size=13, anchor="middle", weight="600")
        svg += text(start_x + i * (bar_w + gap) + bar_w / 2, base_y + 20, lab, fill=TEXT, size=12, anchor="middle")
    # planned epochs line
    svg += line(start_x - 10, base_y - 160, start_x + 4 * (bar_w + gap), base_y - 160, stroke=MUTED, width=1, dash="4,4")
    svg += text(start_x + 4 * (bar_w + gap) + 5, base_y - 156, "planned epoch 5", fill=MUTED, size=9, anchor="start")
    svg += line(60, base_y, start_x + 4 * (bar_w + gap) + 20, base_y, stroke=MUTED, width=2)
    svg += svg_foot()
    save_svg("G-016-best-epoch-markers.svg", svg)


# ---------------------------------------------------------------------------
# G-017 Train/Eval Gap per Experiment
# ---------------------------------------------------------------------------
def generate_g017():
    W, H = 900, 420
    data = load(Path(__file__).resolve().parent / "experimentData.json")
    curves = data.get("curves", {})
    experiments = ["001", "002", "003", "004"]
    colors = [TEAL, AMBER, RED, GREEN]
    svg = svg_head(W, H, "Train/eval gap per experiment")
    svg += text(30, 30, "Train/eval gap per experiment", size=16, weight="600")
    svg += text(30, 50, "Classic overfitting: train loss keeps falling, eval loss rises after best checkpoint", fill=MUTED, size=11)

    panel_w, panel_h = 380, 130
    start_x, start_y = 50, 80
    gap_x, gap_y = 30, 25
    for idx, exp in enumerate(experiments):
        c = curves.get(exp, {})
        train = c.get("train_loss", [])
        eval_loss = c.get("eval_loss", [])
        eval_steps = c.get("eval_steps", [])
        col = idx % 2
        row = idx // 2
        px = start_x + col * (panel_w + gap_x)
        py = start_y + row * (panel_h + gap_y)
        svg += rect(px, py, panel_w, panel_h, fill=PANEL, radius=6)
        max_step = max(c.get("train_steps", [])) if c.get("train_steps") else 1
        global_max = 1.0
        if train and c.get("train_steps"):
            pts = " ".join(f"{px + (s / max(max_step, 1)) * panel_w},{py + panel_h - (v / global_max) * panel_h}" for s, v in zip(c["train_steps"], train))
            svg += f'<polyline points="{pts}" fill="none" stroke="{colors[idx]}" stroke-width="1.5" opacity="0.7"/>\n'
        if eval_loss and eval_steps:
            pts = " ".join(f"{px + (s / max(max_step, 1)) * panel_w},{py + panel_h - (v / global_max) * panel_h}" for s, v in zip(eval_steps, eval_loss))
            svg += f'<polyline points="{pts}" fill="none" stroke="{colors[idx]}" stroke-width="2" stroke-dasharray="3,2" opacity="0.9"/>\n'
        svg += text(px + 8, py + 16, f"Exp {exp}", fill=colors[idx], size=11, weight="600")
        svg += text(px + panel_w - 8, py + 16, "train —  eval - -", fill=MUTED, size=8, anchor="end")

    svg += svg_foot()
    save_svg("G-017-train-eval-gap.svg", svg)


# ---------------------------------------------------------------------------
# G-002 Best Validation Loss per Experiment
# ---------------------------------------------------------------------------
def generate_g002():
    W, H = 640, 360
    data = load(Path(__file__).resolve().parent / "experimentData.json")
    svg = svg_head(W, H, "Best validation loss per experiment")
    svg += text(30, 30, "Best validation loss per experiment", size=16, weight="600")
    svg += text(30, 50, "Exp 001 has the lowest loss but the worst decisions", fill=MUTED, size=11)

    values = [data["experiments"][e]["best_eval_loss"] for e in ["001", "002", "003", "004"]]
    labels = ["Exp 001", "Exp 002", "Exp 003", "Exp 004"]
    colors = [TEAL, AMBER, RED, GREEN]
    max_v = max(values) * 1.2
    bar_w = 80
    gap = 60
    start_x = 80
    base_y = 300
    for i, (v, l, c) in enumerate(zip(values, labels, colors)):
        h = (v / max_v) * 200
        svg += rect(start_x + i * (bar_w + gap), base_y - h, bar_w, h, fill=c, stroke="none", radius=4)
        svg += text(start_x + i * (bar_w + gap) + bar_w / 2, base_y - h - 10, f"{v:.3f}", fill=c, size=11, anchor="middle", weight="600")
        svg += text(start_x + i * (bar_w + gap) + bar_w / 2, base_y + 20, l, fill=TEXT, size=12, anchor="middle")
    svg += line(60, base_y, 560, base_y, stroke=MUTED, width=2)
    svg += svg_foot()
    save_svg("G-002-best-eval-loss.svg", svg)


# ---------------------------------------------------------------------------
# G-003 Token Accuracy Curves
# ---------------------------------------------------------------------------
def generate_g003():
    W, H = 900, 420
    data = load(Path(__file__).resolve().parent / "experimentData.json")
    curves = data.get("curves", {})
    svg = svg_head(W, H, "Token accuracy curves")
    svg += text(30, 30, "Token accuracy curves", size=16, weight="600")
    svg += text(30, 50, "Model quickly learned JSON format, not its meaning", fill=MUTED, size=11)

    plot_x, plot_y, plot_w, plot_h = 60, 80, 540, 280
    svg += rect(plot_x, plot_y, plot_w, plot_h, fill=PANEL, radius=6)
    for i in range(6):
        y = plot_y + plot_h - i * (plot_h / 5)
        svg += line(plot_x, y, plot_x + plot_w, y, stroke=GRID)
        svg += text(plot_x - 10, y + 4, f"{i * 20}%", fill=MUTED, size=9, anchor="end")

    colors = [TEAL, AMBER, RED, GREEN]
    for idx, exp in enumerate(["001", "002", "003", "004"]):
        c = curves.get(exp, {})
        acc = [a for a in c.get("token_accuracy", []) if a is not None]
        if not acc:
            continue
        n = len(acc)
        pts = " ".join(f"{plot_x + (i / max(n - 1, 1)) * plot_w},{plot_y + plot_h - (v / 100) * plot_h}" for i, v in enumerate(acc))
        svg += f'<polyline points="{pts}" fill="none" stroke="{colors[idx]}" stroke-width="2"/>\n'
        svg += rect(630, 100 + idx * 34, 14, 14, fill=colors[idx], stroke="none", radius=2)
        svg += text(652, 112 + idx * 34, f"Exp {exp}", fill=TEXT, size=11)
    svg += svg_foot()
    save_svg("G-003-token-accuracy.svg", svg)


# ---------------------------------------------------------------------------
# G-006 Per-Component MAE Heatmap (Exp 004 only)
# ---------------------------------------------------------------------------
def generate_g006():
    W, H = 640, 360
    rep = load(ROOT / "experiment_004" / "generation_test" / "generation_test_report.json")
    results = rep.get("best_lora", {}).get("results", [])
    # Compute per-component MAE for records that have component scores
    diffs = {"role": [], "skills": [], "experience": [], "conditions": []}
    for r in results:
        teacher = r.get("teacher", {})
        pred = r.get("parsed_output", {})
        if not pred:
            pred = r.get("lora_prediction", {})
        for key in diffs:
            t = teacher.get(f"{key}_score")
            p = pred.get(f"{key}_score")
            if t is not None and p is not None:
                diffs[key].append(abs(t - p))
    mae = {k: sum(v) / len(v) if v else 0 for k, v in diffs.items()}

    svg = svg_head(W, H, "Per-component MAE heatmap")
    svg += text(30, 30, "Per-component MAE — Exp 004", size=16, weight="600")
    svg += text(30, 50, "Error is not uniform across scoring components", fill=MUTED, size=11)

    labels = ["Role", "Skills", "Experience", "Conditions"]
    max_mae = max(mae.values()) or 1
    bar_w = 100
    gap = 40
    start_x = 80
    base_y = 280
    for i, (label, key) in enumerate(zip(labels, diffs.keys())):
        v = mae[key]
        color = AMBER if v > 8 else TEAL
        h = (v / max_mae) * 160
        svg += rect(start_x + i * (bar_w + gap), base_y - h, bar_w, h, fill=color, stroke="none", radius=4, opacity=0.85)
        svg += text(start_x + i * (bar_w + gap) + bar_w / 2, base_y - h - 10, f"{v:.1f}", fill=color, size=12, anchor="middle", weight="600")
        svg += text(start_x + i * (bar_w + gap) + bar_w / 2, base_y + 20, label, fill=TEXT, size=11, anchor="middle")
    svg += line(60, base_y, 580, base_y, stroke=MUTED, width=2)
    svg += svg_foot()
    save_svg("G-006-per-component-mae.svg", svg)


# ---------------------------------------------------------------------------
# G-007 Test Eval Loss
# ---------------------------------------------------------------------------
def generate_g007():
    W, H = 640, 360
    data = load(Path(__file__).resolve().parent / "experimentData.json")
    svg = svg_head(W, H, "Test evaluation loss")
    svg += text(30, 30, "Test evaluation loss", size=16, weight="600")
    svg += text(30, 50, "Held-out likelihood does not reflect matching quality", fill=MUTED, size=11)

    experiments = ["001", "003", "004"]
    base_vals = [data["experiments"][e]["test_eval_loss"]["base"] for e in experiments]
    lora_vals = [data["experiments"][e]["test_eval_loss"]["lora"] for e in experiments]

    bar_w = 50
    group_w = 130
    start_x = 80
    base_y = 300
    max_v = max([v for v in base_vals + lora_vals if v is not None]) * 1.15
    for i, exp in enumerate(experiments):
        x = start_x + i * group_w
        bh = (base_vals[i] / max_v) * 200
        lh = (lora_vals[i] / max_v) * 200 if lora_vals[i] else 0
        svg += rect(x, base_y - bh, bar_w, bh, fill=MUTED, stroke="none", radius=3)
        svg += rect(x + bar_w + 6, base_y - lh, bar_w, lh, fill=TEAL, stroke="none", radius=3)
        svg += text(x + bar_w + 3, base_y + 20, f"Exp {exp}", fill=TEXT, size=12, anchor="middle")
    # legend
    svg += rect(400, 110, 14, 14, fill=MUTED, stroke="none", radius=2)
    svg += text(422, 122, "Base Qwen", fill=TEXT, size=11)
    svg += rect(400, 140, 14, 14, fill=TEAL, stroke="none", radius=2)
    svg += text(422, 152, "LoRA", fill=TEXT, size=11)
    svg += line(60, base_y, 560, base_y, stroke=MUTED, width=2)
    svg += svg_foot()
    save_svg("G-007-test-eval-loss.svg", svg)


# ---------------------------------------------------------------------------
# G-010 Latency CDF
# ---------------------------------------------------------------------------
def generate_g010():
    W, H = 640, 360
    ev = load(ROOT / "experiment_004" / "external_validation_report.json")
    latencies = sorted([r["lora_latency_ms"] for r in ev.get("results", []) if r.get("lora_latency_ms")])
    svg = svg_head(W, H, "Latency CDF")
    svg += text(30, 30, "LoRA latency CDF — external validation (102 records)", size=16, weight="600")

    plot_x, plot_y, plot_w, plot_h = 60, 70, 440, 240
    svg += rect(plot_x, plot_y, plot_w, plot_h, fill=PANEL, radius=6)
    n = len(latencies)
    max_l = max(latencies)
    pts = " ".join(
        f"{plot_x + (latencies[i] / max_l) * plot_w},{plot_y + plot_h - ((i + 1) / n) * plot_h}"
        for i in range(n)
    )
    svg += f'<polyline points="{pts}" fill="none" stroke="{AMBER}" stroke-width="2"/>\n'
    svg += text(plot_x + plot_w / 2, plot_y + plot_h + 28, "Latency, ms", fill=MUTED, size=11, anchor="middle")
    svg += text(30, plot_y + plot_h / 2, "Probability", fill=MUTED, size=11, anchor="middle", transform=f"rotate(-90 30 {plot_y + plot_h / 2})")
    svg += text(520, 110, f"p50: {ev['lora_summary']['latency_p50']} ms", fill=TEXT, size=11)
    svg += text(520, 135, f"p95: {ev['lora_summary']['latency_p95']} ms", fill=TEXT, size=11)
    svg += text(520, 160, f"avg: {round(ev['lora_summary']['latency_avg'])} ms", fill=TEXT, size=11)
    svg += svg_foot()
    save_svg("G-010-latency-cdf.svg", svg)


# ---------------------------------------------------------------------------
# G-011 Engine Benchmark
# ---------------------------------------------------------------------------
def generate_g011():
    W, H = 640, 360
    eng = load(ROOT / "experiment_004" / "latency_optimization" / "engine_benchmark_report.json")
    vllm = load(ROOT / "experiment_004" / "latency_optimization" / "engine_benchmark_report_vllm.json")
    svg = svg_head(W, H, "Engine benchmark")
    svg += text(30, 30, "Inference engine benchmark", size=16, weight="600")
    svg += text(30, 50, "vLLM cut latency several-fold", fill=MUTED, size=11)

    def engine_avg(data, name):
        for e in data.get("engines", []):
            if e.get("engine") == name:
                return e.get("latency_avg_ms")
        return None

    engines = [
        ("transformers fp16", engine_avg(eng, "transformers_fp16"), AMBER),
        ("transformers 4-bit", engine_avg(eng, "transformers_4bit"), RED),
        ("vLLM fp16", engine_avg(vllm, "vllm_fp16"), GREEN),
    ]
    bar_w = 120
    gap = 50
    start_x = 80
    base_y = 300
    max_v = max(v for _, v, _ in engines if v) * 1.15
    for i, (name, v, color) in enumerate(engines):
        if not v:
            continue
        h = (v / max_v) * 200
        svg += rect(start_x + i * (bar_w + gap), base_y - h, bar_w, h, fill=color, stroke="none", radius=4)
        svg += text(start_x + i * (bar_w + gap) + bar_w / 2, base_y - h - 10, f"{v:.0f} ms", fill=color, size=11, anchor="middle", weight="600")
        svg += text(start_x + i * (bar_w + gap) + bar_w / 2, base_y + 20, name, fill=TEXT, size=11, anchor="middle")
    svg += line(60, base_y, 560, base_y, stroke=MUTED, width=2)
    svg += svg_foot()
    save_svg("G-011-engine-benchmark.svg", svg)


# ---------------------------------------------------------------------------
# G-012 Latency Stage Breakdown
# ---------------------------------------------------------------------------
def generate_g012():
    W, H = 640, 360
    prof = load(ROOT / "experiment_004" / "latency_optimization" / "latency_profile_report.json")
    summary = prof.get("stage_summary", {})
    stages = ["apply_chat_template", "tokenize", "generate", "decode_and_extract"]
    labels = ["chat template", "tokenize", "generate", "decode"]
    values = [summary.get(s, {}).get("avg_ms", 0) for s in stages]
    total = sum(values)
    svg = svg_head(W, H, "Latency stage breakdown")
    svg += text(30, 30, "Latency stage breakdown", size=16, weight="600")
    svg += text(30, 50, "Generation dominates response time (>99%)", fill=MUTED, size=11)

    bar_h = 34
    gap = 16
    start_y = 100
    max_w = 480
    for i, (label, v) in enumerate(zip(labels, values)):
        w = (v / total) * max_w
        color = RED if label == "generate" else TEAL
        svg += rect(140, start_y + i * (bar_h + gap), w, bar_h, fill=color, stroke="none", radius=3, opacity=0.9)
        svg += text(10, start_y + i * (bar_h + gap) + bar_h / 2 + 4, label, fill=TEXT, size=11, anchor="start")
        pct = v / total * 100
        svg += text(150 + w + 8, start_y + i * (bar_h + gap) + bar_h / 2 + 4, f"{v:.1f} ms ({pct:.1f}%)", fill=TEXT, size=10)
    svg += svg_foot()
    save_svg("G-012-latency-stage-breakdown.svg", svg)


# ---------------------------------------------------------------------------
# G-014 LoRA vs GPT Radar
# ---------------------------------------------------------------------------
def generate_g014():
    W, H = 640, 420
    data = load(Path(__file__).resolve().parent / "experimentData.json")
    ev = data.get("external_validation", {})
    lora = ev.get("lora", {})
    gpt = ev.get("gpt", {})
    # Metrics: accuracy (flip FNR to be good), 1/MAE (higher better), 1/latency (higher better)
    labels = ["Accuracy", "1/MAE", "Precision\n(1-FPR)", "Recall\n(1-FNR)"]
    # Normalize 0-1
    lora_vals = [
        lora.get("decision_accuracy", 0),
        1 / max(lora.get("mae_score", 1), 0.1),
        1 - lora.get("fpr", 0),
        1 - lora.get("fnr", 0),
    ]
    gpt_vals = [
        gpt.get("decision_accuracy", 0),
        1 / max(gpt.get("mae_score", 1), 0.1),
        1 - gpt.get("fpr", 0),
        1 - gpt.get("fnr", 0),
    ]
    # Scale for radar
    max_vals = [max(l, g) for l, g in zip(lora_vals, gpt_vals)]
    lora_vals = [l / max(m, 1e-6) for l, m in zip(lora_vals, max_vals)]
    gpt_vals = [g / max(m, 1e-6) for g, m in zip(gpt_vals, max_vals)]

    svg = svg_head(W, H, "LoRA vs GPT radar")
    svg += text(30, 30, "LoRA vs GPT-4o-mini — external validation", size=16, weight="600")

    cx, cy, r = 320, 220, 120
    n = len(labels)
    for i in range(5):
        rr = r * (i + 1) / 5
        svg += f'<circle cx="{cx}" cy="{cy}" r="{rr}" fill="none" stroke="{GRID}" stroke-width="1"/>\n'
    for i in range(n):
        a = 2 * pi * i / n - pi / 2
        x = cx + r * cos(a)
        y = cy + r * sin(a)
        svg += line(cx, cy, x, y, stroke=GRID)
        lx = cx + (r + 28) * cos(a)
        ly = cy + (r + 28) * sin(a)
        anchor = "middle" if abs(lx - cx) < 20 else ("start" if lx > cx else "end")
        svg += text(lx, ly + 4, labels[i], fill=TEXT, size=10, anchor=anchor)

    def poly(vals, stroke, fill):
        pts = " ".join(
            f"{cx + r * v * cos(2 * pi * i / n - pi / 2)},{cy + r * v * sin(2 * pi * i / n - pi / 2)}"
            for i, v in enumerate(vals)
        )
        return f'<polygon points="{pts}" fill="{fill}" stroke="{stroke}" stroke-width="2" opacity="0.5"/>\n'

    svg += poly(gpt_vals, GREEN, "none")
    svg += poly(lora_vals, TEAL, "none")
    # legend
    svg += rect(480, 90, 14, 14, fill=TEAL, stroke="none", radius=2)
    svg += text(502, 102, "LoRA", fill=TEXT, size=11)
    svg += rect(480, 120, 14, 14, fill=GREEN, stroke="none", radius=2)
    svg += text(502, 132, "GPT-4o-mini", fill=TEXT, size=11)
    svg += text(480, 170, "LoRA competitive on decisions", fill=TEAL, size=10)
    svg += text(480, 188, "but not on MAE or latency", fill=MUTED, size=10)
    svg += svg_foot()
    save_svg("G-014-lora-vs-gpt-radar.svg", svg)


# ---------------------------------------------------------------------------
# G-015 Before/After Truncation Fix
# ---------------------------------------------------------------------------
def generate_g015():
    W, H = 640, 320
    before = load(ROOT / "experiment_004" / "gpt_comparison_report.json")
    after = load(ROOT / "experiment_004" / "gpt_comparison_report_v2.json")
    b_lora = before.get("lora_summary", {})
    a_lora = after.get("lora_summary", {})
    svg = svg_head(W, H, "Before/after truncation fix")
    svg += text(30, 30, "Before / after truncation fix", size=16, weight="600")
    svg += text(30, 50, "max_tokens 300 → 512 + graceful fallback", fill=MUTED, size=11)

    metrics = ["valid JSON", "decision accuracy", "MAE score"]
    before_vals = [b_lora.get("valid_json_rate", 0), b_lora.get("decision_accuracy", 0), b_lora.get("mae_score", 0)]
    after_vals = [a_lora.get("valid_json_rate", 0), a_lora.get("decision_accuracy", 0), a_lora.get("mae_score", 0)]
    # Format
    before_text = [f"{before_vals[0]*100:.0f}%", f"{before_vals[1]*100:.1f}%", f"{before_vals[2]:.1f}"]
    after_text = [f"{after_vals[0]*100:.0f}%", f"{after_vals[1]*100:.1f}%", f"{after_vals[2]:.1f}"]

    for i, (m, bt, at) in enumerate(zip(metrics, before_text, after_text)):
        y = 110 + i * 70
        svg += text(80, y, m, fill=MUTED, size=11, anchor="end")
        svg += rect(100, y - 22, 160, 30, fill=RED, stroke="none", radius=4, opacity=0.8)
        svg += text(180, y - 2, bt, fill="#fff", size=12, anchor="middle", weight="600")
        svg += text(270, y - 2, "→", fill=TEXT, size=14, anchor="middle", weight="700")
        svg += rect(300, y - 22, 160, 30, fill=GREEN, stroke="none", radius=4, opacity=0.8)
        svg += text(380, y - 2, at, fill="#fff", size=12, anchor="middle", weight="600")
    svg += text(180, 80, "Before", fill=RED, size=12, anchor="middle", weight="600")
    svg += text(380, 80, "After", fill=GREEN, size=12, anchor="middle", weight="600")
    svg += svg_foot()
    save_svg("G-015-before-after-truncation.svg", svg)


# ---------------------------------------------------------------------------
# D-009 Checkpoint Selection Timeline
# ---------------------------------------------------------------------------
def generate_d009():
    W, H = 640, 240
    data = load(Path(__file__).resolve().parent / "experimentData.json")
    svg = svg_head(W, H, "Checkpoint selection timeline")
    svg += text(30, 30, "Checkpoint selection timeline", size=16, weight="600")
    svg += text(30, 50, "Best epoch in each experiment was never epoch 5", fill=MUTED, size=11)

    experiments = ["001", "002", "003", "004"]
    colors = [TEAL, AMBER, RED, GREEN]
    y = 130
    svg += line(60, y, 580, y, stroke=MUTED, width=2)
    for i in range(6):
        x = 80 + i * 96
        svg += line(x, y - 5, x, y + 5, stroke=MUTED, width=1)
        svg += text(x, y + 22, f"ep {i + 1}" if i < 5 else "end", fill=MUTED, size=9, anchor="middle")
    for idx, exp in enumerate(experiments):
        ep = data["experiments"][exp]["best_checkpoint"]["epoch"]
        x = 80 + (ep - 1) * 96
        cy = y - 35 - idx * 26
        svg += circle_marker(x, cy, 8, colors[idx])
        svg += text(x + 12, cy + 4, f"Exp {exp} best ep {ep}", fill=colors[idx], size=10, weight="600")
    svg += svg_foot()
    save_svg("D-009-checkpoint-timeline.svg", svg)


def circle_marker(cx, cy, r, fill):
    return f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}" stroke="{WHITE}" stroke-width="1"/>\n'


# ---------------------------------------------------------------------------
# D-010 Dataset Change Log / Controlled Variables
# ---------------------------------------------------------------------------
def generate_d010():
    W, H = 640, 360
    data = load(Path(__file__).resolve().parent / "experimentData.json")
    svg = svg_head(W, H, "Dataset change log")
    svg += text(30, 30, "Dataset change log & controlled variables", size=16, weight="600")
    svg += text(30, 50, "LoRA config unchanged; only dataset composition changed", fill=MUTED, size=11)

    log = data.get("dataset_change_log", [])
    # Controlled variables box
    svg += rect(30, 80, 280, 240, fill=PANEL, radius=6)
    svg += text(170, 105, "Controlled variables", fill=WHITE, size=12, anchor="middle", weight="600")
    rows = [
        "Base model: Qwen2.5-1.5B-Instruct",
        "LoRA r: 16",
        "LoRA α: 32",
        "Dropout: 0.05",
        "Target modules: 7",
        "Epochs: 5",
        "LR: 2e-4 linear decay",
    ]
    for i, r in enumerate(rows):
        svg += text(50, 135 + i * 24, r, fill=MUTED, size=10)

    # Dataset change box
    svg += rect(330, 80, 280, 240, fill=PANEL, radius=6)
    svg += text(470, 105, "Dataset changes", fill=WHITE, size=12, anchor="middle", weight="600")
    svg += text(350, 140, "Exp", fill=MUTED, size=10, weight="600")
    svg += text(410, 140, "Records", fill=MUTED, size=10, weight="600")
    svg += text(500, 140, "Δ", fill=MUTED, size=10, weight="600")
    prev = 0
    for i, entry in enumerate(log):
        total = entry.get("total_records") or 0
        delta = total - prev
        y = 165 + i * 28
        svg += text(350, y, entry["experiment"], fill=TEXT, size=10)
        svg += text(410, y, str(total), fill=TEXT, size=10)
        svg += text(500, y, f"+{delta}" if delta > 0 else "—", fill=AMBER if delta > 0 else MUTED, size=10)
        prev = total
    svg += text(350, 285, "Exp 003: +33 hard negatives", fill=AMBER, size=9)
    svg += text(350, 303, "Exp 004: +39 positives/borderlines", fill=GREEN, size=9)
    svg += svg_foot()
    save_svg("D-010-dataset-change-log.svg", svg)


# ---------------------------------------------------------------------------
# D-001 Full Pipeline Schematic
# ---------------------------------------------------------------------------
def generate_d001():
    W, H = 900, 260
    svg = svg_head(W, H, "Full pipeline schematic")
    svg += text(30, 30, "Full pipeline: teacher dataset → Telegram", size=16, weight="600")
    svg += text(30, 50, "One machine, reproducible stages, versioned artifacts", fill=MUTED, size=11)

    boxes = [
        ("Teacher dataset", "90 → 123 → 162 records", TEAL),
        ("LoRA adapter", "Qwen2.5-1.5B + r=16", AMBER),
        ("vLLM server", "warm persistent process", RED),
        ("Telegram API", "runtime smoke gate", GREEN),
    ]
    x = 50
    y = 110
    w = 180
    h = 90
    gap = 25
    for i, (title, sub, color) in enumerate(boxes):
        bx = x + i * (w + gap)
        svg += rect(bx, y, w, h, fill=PANEL, radius=6)
        svg += text(bx + w / 2, y + 30, title, fill=color, size=12, anchor="middle", weight="600")
        svg += text(bx + w / 2, y + 58, sub, fill=MUTED, size=10, anchor="middle")
        if i < len(boxes) - 1:
            ax = bx + w + 5
            svg += f'<path d="M {ax} {y + h / 2} L {ax + gap - 10} {y + h / 2}" stroke="{WHITE}" stroke-width="2" fill="none" marker-end="url(#arrow)"/>\n'

    svg += svg_foot()
    save_svg("D-001-pipeline-schematic.svg", svg)


# ---------------------------------------------------------------------------
# D-002 Four-Experiments Timeline
# ---------------------------------------------------------------------------
def generate_d002():
    W, H = 900, 280
    data = load(Path(__file__).resolve().parent / "experimentData.json")
    svg = svg_head(W, H, "Four experiments timeline")
    svg += text(30, 30, "Four experiments answered each other's questions", size=16, weight="600")
    svg += text(30, 50, "Each dot is a hypothesis and its unexpected outcome", fill=MUTED, size=11)

    nodes = [
        ("Exp 001", "Baseline LoRA", "Form without meaning", TEAL),
        ("Exp 002", "Tune dynamics", "Better, but misses traps", AMBER),
        ("Exp 003", "Hard negatives", "No FP in smoke", RED),
        ("Exp 004", "Positives", "Balance restored", GREEN),
    ]
    y = 140
    x_start = 90
    gap = 220
    svg += line(x_start, y, x_start + 3 * gap, y, stroke=MUTED, width=2)
    for i, (label, hyp, out, color) in enumerate(nodes):
        x = x_start + i * gap
        svg += circle_marker(x, y, 10, color)
        svg += text(x, y + 28, label, fill=color, size=12, anchor="middle", weight="600")
        svg += text(x, y + 48, hyp, fill=MUTED, size=10, anchor="middle")
        svg += text(x, y + 90, f"→ {out}", fill=TEXT, size=10, anchor="middle")
    svg += svg_foot()
    save_svg("D-002-four-experiments-timeline.svg", svg)


# ---------------------------------------------------------------------------
# D-003 Dataset Composition Transition
# ---------------------------------------------------------------------------
def generate_d003():
    W, H = 720, 320
    data = load(Path(__file__).resolve().parent / "experimentData.json")
    svg = svg_head(W, H, "Dataset composition transition")
    svg += text(30, 30, "Dataset composition transition", size=16, weight="600")
    svg += text(30, 50, "Two levers: hard negatives cut false positives; positives restore recall", fill=MUTED, size=11)

    stages = [
        ("Exp 001/002", 90, "baseline", TEAL),
        ("Exp 003", 123, "+33 hard negatives", RED),
        ("Exp 004", 162, "+39 positives / borderlines", GREEN),
    ]
    x = 60
    y = 110
    w = 180
    h = 140
    gap = 30
    for i, (name, count, note, color) in enumerate(stages):
        bx = x + i * (w + gap)
        svg += rect(bx, y, w, h, fill=PANEL, radius=6)
        svg += text(bx + w / 2, y + 40, name, fill=MUTED, size=11, anchor="middle")
        svg += text(bx + w / 2, y + 85, str(count), fill=color, size=28, anchor="middle", weight="700")
        svg += text(bx + w / 2, y + 118, note, fill=MUTED, size=10, anchor="middle")
        if i < len(stages) - 1:
            ax = bx + w + 5
            svg += f'<path d="M {ax} {y + h / 2} L {ax + gap - 10} {y + h / 2}" stroke="{WHITE}" stroke-width="2" fill="none" marker-end="url(#arrow)"/>\n'

    svg = svg.replace('role="img"', 'role="img"\n  <defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L0,6 L9,3 z" fill="#ffffff"/></marker></defs>', 1)
    svg += svg_foot()
    save_svg("D-003-dataset-composition-transition.svg", svg)


# ---------------------------------------------------------------------------
# D-004 Precision / Recall Trade-off
# ---------------------------------------------------------------------------
def generate_d004():
    W, H = 560, 340
    data = load(Path(__file__).resolve().parent / "experimentData.json")
    svg = svg_head(W, H, "Precision / recall trade-off")
    svg += text(30, 30, "Precision / recall trade-off", size=16, weight="600")
    svg += text(30, 50, "Hard negatives raise precision; positives restore recall", fill=MUTED, size=11)

    # 2x2 matrix: columns precision low/high, rows recall low/high
    rows = ["Low recall", "High recall"]
    cols = ["Low precision", "High precision"]
    cell_w, cell_h = 200, 100
    start_x, start_y = 60, 90
    for r, row in enumerate(rows):
        for c, col in enumerate(cols):
            x = start_x + c * cell_w
            y = start_y + r * cell_h
            svg += rect(x, y, cell_w, cell_h, fill=PANEL, radius=4)
            label = ""
            color = MUTED
            if r == 0 and c == 0:
                label = "Exp 001/002 baseline"
                color = TEAL
            elif r == 0 and c == 1:
                label = "Exp 003\nhard negatives"
                color = RED
            elif r == 1 and c == 0:
                label = "—"
                color = MUTED
            else:
                label = "Exp 004\nbalance"
                color = GREEN
            svg += text(x + cell_w / 2, y + cell_h / 2 + 4, label, fill=color, size=11, anchor="middle", weight="600")

    # axis labels
    svg += text(start_x - 10, start_y + cell_h / 2, "Recall", fill=MUTED, size=10, anchor="end")
    svg += text(start_x - 10, start_y + cell_h * 1.5, "", fill=MUTED, size=10, anchor="end")
    svg += text(start_x + cell_w / 2, start_y - 15, "Precision", fill=MUTED, size=10, anchor="middle")
    svg += svg_foot()
    save_svg("D-004-precision-recall-tradeoff.svg", svg)


# ---------------------------------------------------------------------------
# D-005 Offline Validation vs Production Smoke
# ---------------------------------------------------------------------------
def generate_d005():
    W, H = 720, 260
    svg = svg_head(W, H, "Offline validation vs production smoke")
    svg += text(30, 30, "Offline validation and production smoke are not equivalent gates", size=16, weight="600")
    svg += text(30, 50, "Each catches failure modes the other misses", fill=MUTED, size=11)

    # Two gates
    gates = [
        ("Offline validation", "held-out test\nmetrics: accuracy, MAE", TEAL, 120),
        ("Production smoke", "runtime API\nadversarial cases", GREEN, 420),
    ]
    for title, sub, color, x in gates:
        svg += rect(x, 90, 220, 120, fill=PANEL, radius=6)
        svg += text(x + 110, 125, title, fill=color, size=13, anchor="middle", weight="600")
        svg += text(x + 110, 160, sub, fill=MUTED, size=10, anchor="middle")

    # inequality arrow
    svg += f'<path d="M 360 150 L 400 150" stroke="{AMBER}" stroke-width="2" marker-end="url(#arrow)"/>\n'
    svg += text(380, 140, "≠", fill=AMBER, size=18, anchor="middle", weight="700")
    svg += svg_foot()
    save_svg("D-005-offline-vs-smoke.svg", svg)


# ---------------------------------------------------------------------------
# D-006 Teacher Dataset Provenance
# ---------------------------------------------------------------------------
def generate_d006():
    W, H = 720, 240
    svg = svg_head(W, H, "Teacher dataset provenance")
    svg += text(30, 30, "Teacher dataset provenance", size=16, weight="600")
    svg += text(30, 50, "Labels originate from prompt-evaluation database", fill=MUTED, size=11)

    stages = [
        ("Prompt-eval DB", "PostgreSQL", TEAL),
        ("SQL extraction", "scoring + audit", AMBER),
        ("Manifest", "versioned cases", RED),
        ("Teacher dataset", "train/val/test", GREEN),
    ]
    x = 40
    y = 110
    w = 150
    h = 70
    gap = 20
    for i, (title, sub, color) in enumerate(stages):
        bx = x + i * (w + gap)
        svg += rect(bx, y, w, h, fill=PANEL, radius=4)
        svg += text(bx + w / 2, y + 28, title, fill=color, size=11, anchor="middle", weight="600")
        svg += text(bx + w / 2, y + 52, sub, fill=MUTED, size=9, anchor="middle")
        if i < len(stages) - 1:
            ax = bx + w + 2
            svg += f'<path d="M {ax} {y + h / 2} L {ax + gap - 8} {y + h / 2}" stroke="{WHITE}" stroke-width="2" fill="none" marker-end="url(#arrow)"/>\n'

    svg = svg.replace('role="img"', 'role="img"\n  <defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L0,6 L9,3 z" fill="#ffffff"/></marker></defs>', 1)
    svg += svg_foot()
    save_svg("D-006-teacher-dataset-provenance.svg", svg)


# ---------------------------------------------------------------------------
# D-007 Next Cycle Roadmap
# ---------------------------------------------------------------------------
def generate_d007():
    W, H = 720, 280
    svg = svg_head(W, H, "Next cycle roadmap")
    svg += text(30, 30, "Next cycle roadmap", size=16, weight="600")
    svg += text(30, 50, "Each closed question opens a new one", fill=MUTED, size=11)

    items = [
        ("Calibration", "MAE closer to GPT", AMBER),
        ("Augmentation", "stratified hard negatives", RED),
        ("Metrics", "production FPR/FNR by segment", TEAL),
        ("Server", "quantized persistent vLLM", GREEN),
    ]
    x = 50
    y = 100
    w = 145
    h = 120
    gap = 20
    for i, (title, sub, color) in enumerate(items):
        bx = x + i * (w + gap)
        svg += rect(bx, y, w, h, fill=PANEL, radius=6)
        svg += text(bx + w / 2, y + 35, title, fill=color, size=12, anchor="middle", weight="600")
        svg += text(bx + w / 2, y + 70, sub, fill=MUTED, size=10, anchor="middle")
    svg += svg_foot()
    save_svg("D-007-next-cycle-roadmap.svg", svg)


# ---------------------------------------------------------------------------
# D-008 Proven / Partial / Next Map
# ---------------------------------------------------------------------------
def generate_d008():
    W, H = 900, 300
    svg = svg_head(W, H, "Proven partial next map")
    svg += text(30, 30, "Proven · Partial · Next", size=16, weight="600")
    svg += text(30, 50, "Honest classification of what the experiments established", fill=MUTED, size=11)

    cols = [
        ("Proven", GREEN, [
            "Dataset engineering works",
            "Production smoke gate stable",
            "Latency viable with vLLM",
            "External validation 0.931",
        ]),
        ("Partial", AMBER, [
            "Near GPT on decisions",
            "Quality holds on rerun",
            "Hard-negative coverage",
        ]),
        ("Next", RED, [
            "Score calibration parity",
            "Stratified FPR/FNR",
            "Quantized server",
            "Full GPT parity",
        ]),
    ]
    x = 50
    y = 90
    w = 260
    h = 190
    gap = 25
    for i, (title, color, items) in enumerate(cols):
        bx = x + i * (w + gap)
        svg += rect(bx, y, w, h, fill=PANEL, radius=6)
        svg += text(bx + w / 2, y + 30, title, fill=color, size=14, anchor="middle", weight="700")
        for j, item in enumerate(items):
            svg += text(bx + 20, y + 60 + j * 26, "• " + item, fill=TEXT, size=10)
    svg += svg_foot()
    save_svg("D-008-proven-partial-next.svg", svg)


if __name__ == "__main__":
    generate_g001()
    generate_g002()
    generate_g003()
    generate_g006()
    generate_g007()
    generate_g010()
    generate_g011()
    generate_g012()
    generate_g014()
    generate_g015()
    generate_g016()
    generate_g017()
    generate_d001()
    generate_d002()
    generate_d003()
    generate_d004()
    generate_d005()
    generate_d006()
    generate_d007()
    generate_d008()
    generate_d009()
    generate_d010()
