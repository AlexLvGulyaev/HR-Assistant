#!/usr/bin/env python3
"""
Генератор G-025: сцена 9 «Баланс».
Комбинированный график без зависимостей (matplotlib не требуется).

Версия v5:
- горизонтальный layout 1800×760, левая панель — состав датасета,
  правая панель — метрики;
- убраны средние подписи экспериментов на оси X;
- легенда левого графика: квадратики по центру столбцов, подписи правее;
- правый график: смещены позиции меток, чтобы избежать наложений.
"""

import json
from pathlib import Path
import xml.etree.ElementTree as ET


ROOT = Path("/opt/ai-automation-portfolio-lab/cases/hr-assistant")
MANIFEST_003 = ROOT / "finetuning/data/manifest_experiment_003.json"
MANIFEST_004 = ROOT / "finetuning/data/manifest_experiment_004.json"
REPORTS = {
    "002": ROOT / "finetuning/runs/experiment_002/generation_test/generation_test_report.json",
    "003": ROOT / "finetuning/runs/experiment_003/generation_test/generation_test_report.json",
    "004": ROOT / "finetuning/runs/experiment_004/generation_test/generation_test_report.json",
}

OUT_SVG_LANDING = ROOT / "finetuning/landing/assets/visuals/G-025-balance-dataset-and-metrics.svg"
OUT_SVG_PORTFOLIO = ROOT / "portfolio_visuals/svg/G-025-balance-dataset-and-metrics.svg"


# Цвета в стиле лендинга
BG = "#0d1117"
PANEL_BG = "#161b22"
GRID = "#30363d"
TEXT = "#e6edf3"
MUTED = "#8b949e"

COLOR_POSITIVES = "#3fb950"
COLOR_BORDERLINES = "#d29922"
COLOR_REJECTS = "#da3633"

COLOR_BASE_DA = "#58a6ff"
COLOR_LORA_DA = "#238636"
COLOR_BASE_MAE = "#f0883e"
COLOR_LORA_MAE = "#a371f7"

WIDTH = 1800
HEIGHT = 760


def load_manifest_counts(path: Path) -> dict:
    with open(path) as f:
        data = json.load(f)
    totals = {"obvious_match": 0, "obvious_no_match": 0, "borderline": 0}
    for split in data.get("splits", {}).values():
        dist = split.get("case_type_distribution", {})
        for k in totals:
            totals[k] += dist.get(k, 0)
    return totals


def load_metrics(exp: str) -> dict:
    path = REPORTS[exp]
    with open(path) as f:
        data = json.load(f)
    out = {}
    for model in ("base_qwen", "best_lora"):
        s = data[model]["summary"]
        out[model] = {
            "da": s["decision_accuracy"] * 100,
            "mae": s["mae_score"],
        }
    return out


def add_text(parent, x, y, text, fill=MUTED, font_size=12, anchor="start", weight="normal"):
    el = ET.SubElement(parent, "text", {
        "x": str(x), "y": str(y), "fill": fill,
        "font-size": str(font_size), "font-family": "Inter, sans-serif",
        "text-anchor": anchor, "font-weight": weight
    })
    el.text = text
    return el


def add_rect(parent, x, y, width, height, fill, stroke=None, stroke_width=None, rx=0):
    att = {"x": str(x), "y": str(y), "width": str(width), "height": str(height), "fill": fill}
    if rx:
        att["rx"] = str(rx)
    if stroke:
        att["stroke"] = stroke
        att["stroke-width"] = str(stroke_width or 1)
    return ET.SubElement(parent, "rect", att)


def add_line(parent, x1, y1, x2, y2, stroke, stroke_width=1, dash=None):
    att = {"x1": str(x1), "y1": str(y1), "x2": str(x2), "y2": str(y2), "stroke": stroke, "stroke-width": str(stroke_width)}
    if dash:
        att["stroke-dasharray"] = dash
    return ET.SubElement(parent, "line", att)


def value_to_y(value, y_min, y_max, y_bottom, y_top):
    return y_bottom - (value - y_min) / (y_max - y_min) * (y_bottom - y_top)


def draw_dataset_panel(root, experiments, dataset_counts, panel):
    x0, y0, w, h = panel["x"], panel["y"], panel["w"], panel["h"]
    add_rect(root, x0, y0, w, h, PANEL_BG, stroke=GRID, stroke_width=1, rx=10)

    margin_left, margin_right, margin_top, margin_bottom = 90, 50, 50, 60
    chart_x0 = x0 + margin_left
    chart_y0 = y0 + margin_top
    chart_w = w - margin_left - margin_right
    chart_h = h - margin_top - margin_bottom
    chart_x1 = chart_x0 + chart_w
    chart_y1 = chart_y0 + chart_h

    y_max = 190
    y_min = 0

    # Grid lines
    for v in [0, 50, 100, 150]:
        y = value_to_y(v, y_min, y_max, chart_y1, chart_y0)
        add_line(root, chart_x0, y, chart_x1, y, GRID, stroke_width=0.5)
        add_text(root, chart_x0 - 12, y + 5, str(v), fill=MUTED, font_size=14, anchor="end")

    # Bars
    cats = ["obvious_match", "obvious_no_match", "borderline"]
    labels = ["positives", "hard negatives / rejects", "borderlines"]
    colors = [COLOR_POSITIVES, COLOR_REJECTS, COLOR_BORDERLINES]
    n = len(experiments)
    gap = chart_w / n
    bar_w = gap * 0.55

    centers = []
    for i, exp in enumerate(experiments):
        cx = chart_x0 + gap * (i + 0.5)
        centers.append(cx)
        bx = cx - bar_w / 2
        bottom_y = chart_y1
        total = sum(dataset_counts[exp].values())

        for cat, color in zip(cats, colors):
            val = dataset_counts[exp][cat]
            bar_h = val / y_max * chart_h
            by = bottom_y - bar_h
            add_rect(root, bx, by, bar_w, bar_h, color, stroke=BG, stroke_width=2)
            if val >= 12:
                add_text(root, cx, by + bar_h / 2 + 6, str(int(val)), fill=BG, font_size=16, anchor="middle", weight="bold")
            bottom_y = by

        # total label
        add_text(root, cx, chart_y0 - 12, str(total), fill=TEXT, font_size=18, anchor="middle", weight="bold")

        # x label only at bottom
        xlabels = ["Exp 001/002\nbaseline", "Exp 003\n+hard negatives", "Exp 004\n+balance"]
        lines = xlabels[i].split("\n")
        for li, line in enumerate(lines):
            add_text(root, cx, chart_y1 + 24 + li * 20, line, fill=MUTED, font_size=14, anchor="middle")

    # Legend: squares centered on bars, labels to the right
    legend_top = chart_y0 + 18
    for label, color, cx in zip(labels, colors, centers):
        add_rect(root, cx - 8, legend_top, 16, 16, color, rx=3)
        add_text(root, cx + 14, legend_top + 13, label, fill=TEXT, font_size=14, anchor="start")


def draw_metrics_panel(root, experiments, metrics, panel):
    x0, y0, w, h = panel["x"], panel["y"], panel["w"], panel["h"]
    add_rect(root, x0, y0, w, h, PANEL_BG, stroke=GRID, stroke_width=1, rx=10)

    margin_left, margin_right, margin_top, margin_bottom = 90, 110, 50, 60
    chart_x0 = x0 + margin_left
    chart_y0 = y0 + margin_top
    chart_w = w - margin_left - margin_right
    chart_h = h - margin_top - margin_bottom
    chart_x1 = chart_x0 + chart_w
    chart_y1 = chart_y0 + chart_h

    y_max_da = 100
    y_min_da = 0
    y_max_mae = 45
    y_min_mae = 0

    n = len(experiments)
    gap = chart_w / n

    # Grid and left Y (DA)
    for v in [0, 25, 50, 75, 100]:
        y = value_to_y(v, y_min_da, y_max_da, chart_y1, chart_y0)
        add_line(root, chart_x0, y, chart_x1, y, GRID, stroke_width=0.5)
        add_text(root, chart_x0 - 12, y + 6, f"{v}%", fill=MUTED, font_size=14, anchor="end")

    # Right Y (MAE)
    for v in [0, 10, 20, 30, 40]:
        y = value_to_y(v, y_min_mae, y_max_mae, chart_y1, chart_y0)
        add_text(root, chart_x1 + 12, y + 6, str(v), fill=MUTED, font_size=14, anchor="start")

    # X labels
    xlabels = ["Exp 001/002", "Exp 003", "Exp 004"]
    for i, label in enumerate(xlabels):
        cx = chart_x0 + gap * (i + 0.5)
        add_text(root, cx, chart_y1 + 26, label, fill=MUTED, font_size=14, anchor="middle")

    # Lines
    def make_points(metrics_key, value_key, y_min, y_max):
        points = []
        for i, exp in enumerate(experiments):
            cx = chart_x0 + gap * (i + 0.5)
            val = metrics[exp][metrics_key][value_key]
            cy = value_to_y(val, y_min, y_max, chart_y1, chart_y0)
            points.append((cx, cy, val))
        return points

    da_base = make_points("base_qwen", "da", y_min_da, y_max_da)
    da_lora = make_points("best_lora", "da", y_min_da, y_max_da)
    mae_base = make_points("base_qwen", "mae", y_min_mae, y_max_mae)
    mae_lora = make_points("best_lora", "mae", y_min_mae, y_max_mae)

    def draw_polyline(points, color, dash=False, stroke_width=3):
        pts = " ".join(f"{x},{y}" for x, y, _ in points)
        att = {"points": pts, "fill": "none", "stroke": color, "stroke-width": str(stroke_width)}
        if dash:
            att["stroke-dasharray"] = "8,6"
        ET.SubElement(root, "polyline", att)

    draw_polyline(da_base, COLOR_BASE_DA, dash=True, stroke_width=2.5)
    draw_polyline(da_lora, COLOR_LORA_DA, stroke_width=4)
    draw_polyline(mae_base, COLOR_BASE_MAE, dash=True, stroke_width=2.5)
    draw_polyline(mae_lora, COLOR_LORA_MAE, stroke_width=4)

    # Markers and labels with adjusted offsets
    for points, color, shape, fmt, offset_y in [
        (da_base, COLOR_BASE_DA, "circle", "{:.0f}%", 22),      # lower, away from LoRA DA
        (da_lora, COLOR_LORA_DA, "circle", "{:.0f}%", -18),     # higher, away from Base MAE
        (mae_base, COLOR_BASE_MAE, "rect", "{:.1f}", -18),       # higher, away from LoRA DA labels 78%, 67%
        (mae_lora, COLOR_LORA_MAE, "rect", "{:.1f}", -18),      # higher
    ]:
        for x, y, val in points:
            if shape == "circle":
                ET.SubElement(root, "circle", {"cx": str(x), "cy": str(y), "r": "7", "fill": BG, "stroke": color, "stroke-width": "3"})
            else:
                add_rect(root, x - 6, y - 6, 12, 12, BG, stroke=color, stroke_width=3)
            add_text(root, x, y + offset_y, fmt.format(val), fill=color, font_size=15, anchor="middle", weight="bold")

    # Legend
    lx, ly = chart_x0 + 18, chart_y0 + 20
    legend_items = [
        ("Base Qwen DA", COLOR_BASE_DA, "circle"),
        ("LoRA DA", COLOR_LORA_DA, "circle"),
        ("Base Qwen MAE", COLOR_BASE_MAE, "rect"),
        ("LoRA MAE", COLOR_LORA_MAE, "rect"),
    ]
    for label, color, shape in legend_items:
        if shape == "circle":
            ET.SubElement(root, "circle", {"cx": str(lx + 7), "cy": str(ly + 7), "r": "6", "fill": color})
        else:
            add_rect(root, lx, ly + 1, 14, 12, color)
        add_text(root, lx + 22, ly + 13, label, fill=TEXT, font_size=14)
        lx += 190


def main():
    experiments = ["002", "003", "004"]

    dataset_counts = {
        "002": {"obvious_match": 30, "obvious_no_match": 30, "borderline": 30},
        "003": load_manifest_counts(MANIFEST_003),
        "004": load_manifest_counts(MANIFEST_004),
    }

    metrics = {exp: load_metrics(exp) for exp in experiments}

    svg = ET.Element("svg", {
        "xmlns": "http://www.w3.org/2000/svg",
        "width": str(WIDTH), "height": str(HEIGHT),
        "viewBox": f"0 0 {WIDTH} {HEIGHT}",
        "role": "img",
        "aria-label": "Dataset composition and quality evolution"
    })

    # Background
    add_rect(svg, 0, 0, WIDTH, HEIGHT, BG)

    # Title
    add_text(svg, WIDTH / 2, 44, "Dataset composition and quality evolution", fill=TEXT, font_size=24, anchor="middle", weight="bold")

    # Panels side by side
    panel_w = (WIDTH - 70) // 2
    top_panel = {"x": 30, "y": 65, "w": panel_w - 15, "h": 670}
    bottom_panel = {"x": 30 + panel_w + 5, "y": 65, "w": panel_w - 15, "h": 670}

    draw_dataset_panel(svg, experiments, dataset_counts, top_panel)
    draw_metrics_panel(svg, experiments, metrics, bottom_panel)

    tree = ET.ElementTree(svg)
    OUT_SVG_LANDING.parent.mkdir(parents=True, exist_ok=True)
    OUT_SVG_PORTFOLIO.parent.mkdir(parents=True, exist_ok=True)

    tree.write(OUT_SVG_LANDING, encoding="utf-8", xml_declaration=True)
    tree.write(OUT_SVG_PORTFOLIO, encoding="utf-8", xml_declaration=True)

    print(f"Saved:\n  {OUT_SVG_LANDING}\n  {OUT_SVG_PORTFOLIO}")


if __name__ == "__main__":
    main()
