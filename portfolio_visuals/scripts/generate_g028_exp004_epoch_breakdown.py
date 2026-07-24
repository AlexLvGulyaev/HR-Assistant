#!/usr/bin/env python3
"""
Generate G-028 — Exp 004 epoch breakdown.

Shows per-epoch train loss and eval loss for Experiment 004,
with a vertical marker at the best checkpoint (epoch 3).
Quality metrics at best checkpoint are shown as annotations.

Data sources:
  - finetuning/runs/experiment_004/trainer_state.json
  - finetuning/runs/experiment_004/generation_test/generation_test_report.json
"""

import json
from pathlib import Path
import xml.etree.ElementTree as ET


ROOT = Path("/opt/ai-automation-portfolio-lab/cases/hr-assistant")
TRAINER_STATE = ROOT / "finetuning/runs/experiment_004/trainer_state.json"
GEN_TEST = ROOT / "finetuning/runs/experiment_004/generation_test/generation_test_report.json"

OUT_SVG_LANDING = ROOT / "landing/assets/visuals/G-028-exp004-epoch-breakdown.svg"
OUT_SVG_PORTFOLIO = ROOT / "portfolio_visuals/svg/G-028-exp004-epoch-breakdown.svg"

# Palette (matches landing dark theme)
BG = "#0d0d10"
PANEL_BG = "#16161f"
GRID = "#2a2a36"
TEXT = "#e8e8ec"
MUTED = "#8a8a9a"
TRAIN_COLOR = "#4ECDC4"
EVAL_COLOR = "#FFB347"
BEST_COLOR = "#96CEB4"

WIDTH, HEIGHT = 1100, 820


def add_text(parent, x, y, text, fill=MUTED, font_size=12, anchor="start", weight="normal"):
    el = ET.SubElement(parent, "text", {
        "x": str(x), "y": str(y), "fill": fill,
        "font-size": str(font_size), "font-family": "Inter, sans-serif",
        "text-anchor": anchor, "font-weight": weight
    })
    el.text = text
    return el


def add_rect(parent, x, y, width, height, fill, stroke=None, stroke_width=None, rx=0):
    att = {
        "x": str(x), "y": str(y), "width": str(width), "height": str(height),
        "fill": fill
    }
    if rx:
        att["rx"] = str(rx)
    if stroke:
        att["stroke"] = stroke
        att["stroke-width"] = str(stroke_width or 1)
    return ET.SubElement(parent, "rect", att)


def add_line(parent, x1, y1, x2, y2, stroke, stroke_width=1, dash=None):
    att = {
        "x1": str(x1), "y1": str(y1), "x2": str(x2), "y2": str(y2),
        "stroke": stroke, "stroke-width": str(stroke_width)
    }
    if dash:
        att["stroke-dasharray"] = dash
    return ET.SubElement(parent, "line", att)


def load_epoch_losses(trainer_path: Path) -> tuple[list[int], list[float], list[float], int]:
    with open(trainer_path) as f:
        data = json.load(f)

    logs = data.get("log_history", [])

    # Group train entries by epoch number (1..5)
    train_by_epoch: dict[int, list[float]] = {}
    eval_by_epoch: dict[int, float] = {}

    for entry in logs:
        epoch = entry.get("epoch")
        if epoch is None:
            continue
        ep = int(round(epoch))
        if ep < 1:
            continue
        if "loss" in entry:
            train_by_epoch.setdefault(ep, []).append(entry["loss"])
        if "eval_loss" in entry:
            eval_by_epoch[ep] = entry["eval_loss"]

    epochs = sorted(set(train_by_epoch.keys()) | set(eval_by_epoch.keys()))
    train_loss = [sum(train_by_epoch.get(ep, [])) / len(train_by_epoch.get(ep, [0])) for ep in epochs]
    eval_loss = [eval_by_epoch.get(ep, None) for ep in epochs]

    best_epoch = int(round(data.get("best_global_step", 0) / (max(epochs) if epochs else 1)))
    # Derive best epoch from checkpoint path as fallback
    ckpt = data.get("best_model_checkpoint", "")
    if "checkpoint-" in ckpt:
        best_step = int(ckpt.split("checkpoint-")[-1])
        # map step to epoch via eval entry
        for entry in logs:
            if entry.get("step") == best_step and "eval_loss" in entry:
                best_epoch = int(round(entry["epoch"]))
                break

    return epochs, train_loss, eval_loss, best_epoch


def load_best_quality(gen_test_path: Path) -> dict:
    with open(gen_test_path) as f:
        data = json.load(f)
    summary = data.get("best_lora", {}).get("summary", {})
    return {
        "decision_accuracy": summary.get("decision_accuracy", 0.0) * 100,
        "mae_score": summary.get("mae_score", 0.0),
        "valid_json_rate": summary.get("valid_json_rate", 0.0) * 100,
    }


def value_to_y(value: float, y_min: float, y_max: float, y_bottom: float, y_top: float) -> float:
    if y_max == y_min:
        return y_bottom
    return y_bottom - (value - y_min) / (y_max - y_min) * (y_bottom - y_top)


def build_svg(epochs, train_loss, eval_loss, best_epoch, quality):
    svg = ET.Element("svg", {
        "xmlns": "http://www.w3.org/2000/svg",
        "width": str(WIDTH), "height": str(HEIGHT),
        "viewBox": f"0 0 {WIDTH} {HEIGHT}",
        "role": "img",
        "aria-label": "Exp 004 train and eval loss per epoch"
    })

    # Background
    add_rect(svg, 0, 0, WIDTH, HEIGHT, BG)

    # Title / subtitle
    add_text(svg, WIDTH / 2, 50, "Experiment 004 — Train / Eval Loss per Epoch", fill=TEXT, font_size=26, anchor="middle", weight="bold")
    add_text(svg, WIDTH / 2, 86, "Checkpoint selection: train loss shows memorization, eval loss shows generalization", fill=MUTED, font_size=16, anchor="middle")

    # Chart area
    margin_left, margin_right, margin_top, margin_bottom = 90, 270, 130, 110
    chart_x0 = margin_left
    chart_y0 = margin_top
    chart_w = WIDTH - margin_left - margin_right
    chart_h = HEIGHT - margin_top - margin_bottom
    chart_x1 = chart_x0 + chart_w
    chart_y1 = chart_y0 + chart_h

    # Value range
    all_values = [v for v in train_loss + eval_loss if v is not None]
    y_max = max(0.8, max(all_values) * 1.05)
    y_min = 0.0

    # Panel background
    add_rect(svg, chart_x0 - 10, chart_y0 - 10, chart_w + 20, chart_h + 20, PANEL_BG, stroke=GRID, stroke_width=1, rx=8)

    # Grid lines
    for v in [0.0, 0.2, 0.4, 0.6, 0.8]:
        y = value_to_y(v, y_min, y_max, chart_y1, chart_y0)
        if y < chart_y0 or y > chart_y1:
            continue
        add_line(svg, chart_x0, y, chart_x1, y, GRID, stroke_width=0.5)
        add_text(svg, chart_x0 - 14, y + 6, f"{v:.1f}", fill=MUTED, font_size=14, anchor="end")

    # X-axis labels
    n = len(epochs)
    gap = chart_w / (n - 1) if n > 1 else chart_w
    x_positions = [chart_x0 + i * gap for i in range(n)]
    for i, ep in enumerate(epochs):
        add_text(svg, x_positions[i], chart_y1 + 30, f"ep {ep}", fill=MUTED, font_size=16, anchor="middle")

    # Axes
    add_line(svg, chart_x0, chart_y1, chart_x1, chart_y1, MUTED, stroke_width=2)
    add_line(svg, chart_x0, chart_y0, chart_x0, chart_y1, MUTED, stroke_width=2)

    def make_points(values, valid_mask):
        pts = []
        for i, (x, val) in enumerate(zip(x_positions, values)):
            if valid_mask[i] and val is not None:
                y = value_to_y(val, y_min, y_max, chart_y1, chart_y0)
                pts.append((x, y, val))
        return pts

    train_valid = [True] * n
    eval_valid = [v is not None for v in eval_loss]

    train_pts = make_points(train_loss, train_valid)
    eval_pts = make_points(eval_loss, eval_valid)

    # Draw lines
    def draw_polyline(points, color, dash=False, stroke_width=3):
        pts = " ".join(f"{x},{y}" for x, y, _ in points)
        att = {"points": pts, "fill": "none", "stroke": color, "stroke-width": str(stroke_width), "stroke-linecap": "round", "stroke-linejoin": "round"}
        if dash:
            att["stroke-dasharray"] = "6,4"
        ET.SubElement(svg, "polyline", att)

    draw_polyline(train_pts, TRAIN_COLOR, dash=True, stroke_width=3)
    draw_polyline(eval_pts, EVAL_COLOR, stroke_width=4)

    # Markers
    for x, y, val in train_pts:
        ET.SubElement(svg, "circle", {"cx": str(x), "cy": str(y), "r": "7", "fill": BG, "stroke": TRAIN_COLOR, "stroke-width": "3"})
        add_text(svg, x, y + 24, f"{val:.3f}", fill=TRAIN_COLOR, font_size=15, anchor="middle", weight="bold")

    for x, y, val in eval_pts:
        ET.SubElement(svg, "circle", {"cx": str(x), "cy": str(y), "r": "8", "fill": EVAL_COLOR, "stroke": BG, "stroke-width": "2"})
        add_text(svg, x, y - 18, f"{val:.3f}", fill=EVAL_COLOR, font_size=15, anchor="middle", weight="bold")

    # Best epoch marker
    best_idx = epochs.index(best_epoch) if best_epoch in epochs else 2
    best_x = x_positions[best_idx]
    add_line(svg, best_x, chart_y0, best_x, chart_y1, BEST_COLOR, stroke_width=2, dash="8,4")
    add_text(svg, best_x, chart_y0 - 22, f"best checkpoint = ep {best_epoch}", fill=BEST_COLOR, font_size=16, anchor="middle", weight="bold")
    # arrow pointing down to the eval point
    add_line(svg, best_x, chart_y0 - 10, best_x, chart_y0 + 10, BEST_COLOR, stroke_width=2)

    # Legend
    lx, ly = chart_x1 + 30, chart_y0 + 30
    ET.SubElement(svg, "circle", {"cx": str(lx + 7), "cy": str(ly + 7), "r": "6", "fill": BG, "stroke": TRAIN_COLOR, "stroke-width": "3"})
    add_text(svg, lx + 22, ly + 12, "train loss", fill=TEXT, font_size=15)
    ly += 32
    ET.SubElement(svg, "circle", {"cx": str(lx + 7), "cy": str(ly + 7), "r": "7", "fill": EVAL_COLOR, "stroke": BG, "stroke-width": "2"})
    add_text(svg, lx + 22, ly + 12, "eval loss", fill=TEXT, font_size=15)
    ly += 32
    add_line(svg, lx, ly + 7, lx + 14, ly + 7, BEST_COLOR, stroke_width=2, dash="8,4")
    add_text(svg, lx + 22, ly + 12, "best epoch", fill=TEXT, font_size=15)

    # Quality annotation card
    card_x = chart_x1 + 20
    card_y = chart_y1 - 160
    card_w = 230
    card_h = 145
    add_rect(svg, card_x, card_y, card_w, card_h, PANEL_BG, stroke=GRID, stroke_width=1, rx=8)
    add_text(svg, card_x + 14, card_y + 32, "Best checkpoint quality", fill=TEXT, font_size=15, weight="bold")
    add_text(svg, card_x + 14, card_y + 62, f"decision accuracy: {quality['decision_accuracy']:.1f}%", fill=BEST_COLOR, font_size=14, weight="bold")
    add_text(svg, card_x + 14, card_y + 88, f"MAE score: {quality['mae_score']:.1f}", fill=MUTED, font_size=14)
    add_text(svg, card_x + 14, card_y + 114, f"valid JSON: {quality['valid_json_rate']:.0f}%", fill=MUTED, font_size=14)

    tree = ET.ElementTree(svg)
    OUT_SVG_LANDING.parent.mkdir(parents=True, exist_ok=True)
    OUT_SVG_PORTFOLIO.parent.mkdir(parents=True, exist_ok=True)
    tree.write(OUT_SVG_LANDING, encoding="utf-8", xml_declaration=True)
    tree.write(OUT_SVG_PORTFOLIO, encoding="utf-8", xml_declaration=True)



def main():
    epochs, train_loss, eval_loss, best_epoch = load_epoch_losses(TRAINER_STATE)
    quality = load_best_quality(GEN_TEST)
    build_svg(epochs, train_loss, eval_loss, best_epoch, quality)
    print(f"Saved:\n  {OUT_SVG_LANDING}\n  {OUT_SVG_PORTFOLIO}")


if __name__ == "__main__":
    main()
