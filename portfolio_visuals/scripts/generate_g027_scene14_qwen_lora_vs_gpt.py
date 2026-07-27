#!/usr/bin/env python3
"""
Generate G-027 — Scene 14: Qwen-LoRA vs GPT-4o-mini.

Layout v4:
  - Bigger SVG, bigger fonts, bigger cards.
  - More vertical space between characters and top labels.
  - More vertical space between characters and metric cards.
  - Runtime cost card as tall as the three top cards combined.
  - Runtime cost label centered vertically inside the card.
"""

import json
import math
from pathlib import Path
import xml.etree.ElementTree as ET


ROOT = Path("/opt/ai-automation-portfolio-lab/cases/hr-assistant")
EXPERIMENT_DATA = ROOT / "finetuning/landing/data/experimentData.js"
OUT_SVG_LANDING = ROOT / "finetuning/landing/assets/visuals/G-027-qwen-lora-vs-gpt.svg"
OUT_SVG_PORTFOLIO = ROOT / "portfolio_visuals/svg/G-027-qwen-lora-vs-gpt.svg"

# Palette
BG = "#0d0d10"
PANEL_BG = "#16161f"
GRID = "#2a2a36"
TEXT = "#e8e8ec"
MUTED = "#8a8a9a"
TEAL = "#4ECDC4"
STEEL = "#6B8FA3"
STEEL_DIM = "#3A4F5C"
STEEL_FILL = "#1A2A35"
AMBER = "#FFB347"
AMBER_DIM = "#4D3A1F"
AMBER_LIGHT = "#E8C080"
WHITE = "#ffffff"

WIDTH, HEIGHT = 1200, 1150


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


def load_optimized_metrics():
    """Read the JS-like experimentData file and return LoRA/GPT optimized metrics."""
    text = EXPERIMENT_DATA.read_text(encoding="utf-8")
    start = text.find("{")
    if start == -1:
        raise ValueError("Could not locate JSON object in experimentData.js")
    depth = 0
    in_str = False
    escape = False
    end = start
    for i, ch in enumerate(text[start:], start=start):
        if in_str:
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == '"':
                in_str = False
            continue
        if ch == '"':
            in_str = True
        elif ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                end = i
                break
    if end == start:
        raise ValueError("Could not find matching closing brace in experimentData.js")
    data = json.loads(text[start:end + 1])
    opt = data.get("latency", {}).get("optimized", {})
    lora = opt.get("lora_summary", {})
    gpt = opt.get("gpt_summary", {})
    return lora, gpt


def draw_qwen_lora(parent, cx, cy, scale=1.0):
    s = scale
    face_r = 54 * s
    halo_r = 105 * s
    color = TEAL

    glow_id = "qwen-glow"
    defs = ET.SubElement(parent, "defs")
    grad = ET.SubElement(defs, "radialGradient", {"id": glow_id, "cx": "50%", "cy": "50%", "r": "50%"})
    ET.SubElement(grad, "stop", {"offset": "0%", "stop-color": color, "stop-opacity": "0.30"})
    ET.SubElement(grad, "stop", {"offset": "60%", "stop-color": color, "stop-opacity": "0.12"})
    ET.SubElement(grad, "stop", {"offset": "100%", "stop-color": color, "stop-opacity": "0"})
    ET.SubElement(parent, "circle", {"cx": str(cx), "cy": str(cy), "r": str(halo_r + 45 * s), "fill": f"url(#{glow_id})"})

    for i, r in enumerate([halo_r, halo_r - 20 * s, halo_r - 40 * s]):
        op = 0.55 - i * 0.14
        ET.SubElement(parent, "circle", {
            "cx": str(cx), "cy": str(cy), "r": str(r),
            "fill": "none", "stroke": color, "stroke-width": str(1.6 + i * 0.5), "opacity": str(op)
        })

    for i in range(5):
        a = -90 + (i - 2) * 18
        arad = a * math.pi / 180
        x1 = cx + (face_r - 2 * s) * math.cos(arad)
        y1 = cy + (face_r - 2 * s) * math.sin(arad)
        x2 = cx + (face_r + 34 * s + i * 6 * s) * math.cos(arad)
        y2 = cy + (face_r + 34 * s + i * 6 * s) * math.sin(arad)
        ET.SubElement(parent, "line", {
            "x1": str(x1), "y1": str(y1), "x2": str(x2), "y2": str(y2),
            "stroke": color, "stroke-width": str(2.8 * s), "stroke-linecap": "round", "opacity": "0.92"
        })
        ET.SubElement(parent, "circle", {"cx": str(x2), "cy": str(y2), "r": str(5 * s), "fill": color, "opacity": "0.95"})

    n_nodes = 8
    for i in range(n_nodes):
        a = i * 2 * math.pi / n_nodes
        nx = cx + halo_r * math.cos(a)
        ny = cy + halo_r * math.sin(a)
        ET.SubElement(parent, "circle", {"cx": str(nx), "cy": str(ny), "r": str(3.5 * s), "fill": color, "opacity": "0.70"})

    ET.SubElement(parent, "circle", {
        "cx": str(cx), "cy": str(cy), "r": str(face_r),
        "fill": "rgba(10,10,12,0.55)", "stroke": color, "stroke-width": str(2.5 * s), "opacity": "0.95"
    })

    eye_y = cy - 6 * s
    eye_rx = 16 * s
    eye_ry = 9 * s
    eye_xo = 24 * s
    for dx in (-eye_xo, eye_xo):
        ET.SubElement(parent, "ellipse", {
            "cx": str(cx + dx), "cy": str(eye_y), "rx": str(eye_rx), "ry": str(eye_ry),
            "fill": WHITE, "opacity": "0.9"
        })
        ET.SubElement(parent, "circle", {"cx": str(cx + dx), "cy": str(eye_y), "r": str(5 * s), "fill": color, "opacity": "0.8"})

    my = cy + 14 * s
    ET.SubElement(parent, "path", {
        "d": f"M{cx - 10 * s} {my} Q{cx} {my + 7 * s} {cx + 10 * s} {my}",
        "fill": "none", "stroke": WHITE, "stroke-width": str(2.4 * s),
        "stroke-linecap": "round", "opacity": "0.85"
    })


def draw_gpt_form(parent, cx, cy, scale=1.0):
    s = scale
    size = 78 * s
    color = STEEL
    dim = STEEL_DIM

    glow_id = "gpt-glow"
    defs = parent.find("defs")
    if defs is None:
        defs = ET.SubElement(parent, "defs")
    grad = ET.SubElement(defs, "radialGradient", {"id": glow_id, "cx": "50%", "cy": "50%", "r": "50%"})
    ET.SubElement(grad, "stop", {"offset": "0%", "stop-color": color, "stop-opacity": "0.26"})
    ET.SubElement(grad, "stop", {"offset": "60%", "stop-color": color, "stop-opacity": "0.10"})
    ET.SubElement(grad, "stop", {"offset": "100%", "stop-color": color, "stop-opacity": "0"})
    ET.SubElement(parent, "circle", {"cx": str(cx), "cy": str(cy), "r": str(size + 75 * s), "fill": f"url(#{glow_id})"})

    pts = []
    n = 6
    for i in range(n):
        a = i * 2 * math.pi / n - math.pi / 2
        r = size + 30 * s
        pts.append(f"{cx + r * math.cos(a)},{cy + r * math.sin(a)}")
    ET.SubElement(parent, "polygon", {
        "points": " ".join(pts), "fill": STEEL_FILL, "stroke": dim, "stroke-width": str(2 * s), "opacity": "0.80"
    })

    pts2 = []
    for i in range(8):
        a = i * 2 * math.pi / 8 - math.pi / 2
        r = size
        pts2.append(f"{cx + r * math.cos(a)},{cy + r * math.sin(a)}")
    ET.SubElement(parent, "polygon", {
        "points": " ".join(pts2), "fill": "rgba(10,10,12,0.60)", "stroke": color, "stroke-width": str(2.6 * s), "opacity": "0.95"
    })

    for angle in (-90, 0, 90, 180):
        arad = angle * math.pi / 180
        x2 = cx + (size + 44 * s) * math.cos(arad)
        y2 = cy + (size + 44 * s) * math.sin(arad)
        ET.SubElement(parent, "line", {
            "x1": str(cx), "y1": str(cy), "x2": str(x2), "y2": str(y2),
            "stroke": color, "stroke-width": str(2.2 * s), "opacity": "0.70"
        })
        ET.SubElement(parent, "circle", {"cx": str(x2), "cy": str(y2), "r": str(4.5 * s), "fill": color, "opacity": "0.85"})

    eye_y = cy - 4 * s
    eye_size = 6 * s
    eye_xo = 26 * s
    for dx in (-eye_xo, eye_xo):
        ET.SubElement(parent, "circle", {"cx": str(cx + dx), "cy": str(eye_y), "r": str(eye_size), "fill": WHITE, "opacity": "0.90"})

    my = cy + 20 * s
    ET.SubElement(parent, "line", {
        "x1": str(cx - 12 * s), "y1": str(my), "x2": str(cx + 12 * s), "y2": str(my),
        "stroke": WHITE, "stroke-width": str(2.4 * s), "stroke-linecap": "round", "opacity": "0.75"
    })


def format_latency(ms):
    return f"{ms / 1000:.1f}s"


def build_svg(lora, gpt):
    svg = ET.Element("svg", {
        "xmlns": "http://www.w3.org/2000/svg",
        "width": str(WIDTH), "height": str(HEIGHT),
        "viewBox": f"0 0 {WIDTH} {HEIGHT}",
        "role": "img",
        "aria-label": "Qwen-LoRA vs GPT-4o-mini comparison"
    })

    add_rect(svg, 0, 0, WIDTH, HEIGHT, BG)

    # Title and subtitle with more top padding
    add_text(svg, WIDTH / 2, 60, "Qwen-LoRA vs GPT-4o-mini", fill=TEXT, font_size=30, anchor="middle", weight="bold")
    add_text(svg, WIDTH / 2, 96, "External validation on 102 unseen records (vLLM + warm process)", fill=MUTED, font_size=16, anchor="middle")

    # Characters further apart and lower, more space from top text
    qwen_cx, qwen_cy = 300, 300
    gpt_cx, gpt_cy = 900, 300
    draw_qwen_lora(svg, qwen_cx, qwen_cy, scale=1.45)
    draw_gpt_form(svg, gpt_cx, gpt_cy, scale=1.30)

    add_text(svg, qwen_cx, qwen_cy + 185, "Qwen-LoRA", fill=TEAL, font_size=26, anchor="middle", weight="bold")
    add_text(svg, qwen_cx, qwen_cy + 220, "local · fine-tuned", fill=MUTED, font_size=18, anchor="middle")
    add_text(svg, gpt_cx, qwen_cy + 185, "GPT-4o-mini", fill=STEEL, font_size=26, anchor="middle", weight="bold")
    add_text(svg, gpt_cx, qwen_cy + 220, "cloud reference", fill=MUTED, font_size=18, anchor="middle")

    # Three parametric metric cards in a row, taller and with larger fonts
    metrics_top = [
        ("Decision accuracy", f"{lora['decision_accuracy'] * 100:.1f}%", f"{gpt['decision_accuracy'] * 100:.1f}%", "Qwen-LoRA", "GPT"),
        ("MAE score", f"{lora['mae_score']:.1f}", f"{gpt['mae_score']:.1f}", "Qwen-LoRA", "GPT"),
        ("Latency p50", format_latency(lora['latency_p50']), format_latency(gpt['latency_p50']), "Qwen-LoRA", "GPT"),
    ]

    n_top = len(metrics_top)
    top_card_w = 350
    top_card_h = 170
    top_gap = 25
    top_total_w = n_top * top_card_w + (n_top - 1) * top_gap
    top_start_x = (WIDTH - top_total_w) / 2
    top_card_y = 580

    for i, (label, qwen_val, gpt_val, qwen_note, gpt_note) in enumerate(metrics_top):
        x = top_start_x + i * (top_card_w + top_gap)
        add_rect(svg, x, top_card_y, top_card_w, top_card_h, PANEL_BG, stroke=GRID, stroke_width=1, rx=12)
        add_text(svg, x + top_card_w / 2, top_card_y + 34, label, fill=MUTED, font_size=18, anchor="middle", weight="normal")

        add_text(svg, x + 28, top_card_y + 100, qwen_val, fill=TEAL, font_size=42, anchor="start", weight="bold")
        add_text(svg, x + 28, top_card_y + 134, qwen_note, fill=MUTED, font_size=15, anchor="start")

        add_text(svg, x + top_card_w - 28, top_card_y + 100, gpt_val, fill=STEEL, font_size=40, anchor="end", weight="bold")
        add_text(svg, x + top_card_w - 28, top_card_y + 134, gpt_note, fill=MUTED, font_size=15, anchor="end")

    # Full-width Runtime cost card, normal height (same as top cards)
    business_y = top_card_y + top_card_h + 35
    business_h = 170
    business_x = 60
    business_w = WIDTH - 120
    add_rect(svg, business_x, business_y, business_w, business_h, AMBER_DIM, stroke=AMBER, stroke_width=2, rx=14)

    # Decorative left amber bar
    add_rect(svg, business_x, business_y, 10, business_h, AMBER, rx=14)

    # Runtime cost content centered vertically in the business card
    card_mid_y = business_y + business_h / 2

    # Title above center
    add_text(svg, WIDTH / 2, card_mid_y - 44, "Runtime cost", fill=AMBER, font_size=24, anchor="middle", weight="bold")

    # Center separator
    ET.SubElement(svg, "line", {
        "x1": str(WIDTH / 2), "y1": str(card_mid_y - 14), "x2": str(WIDTH / 2), "y2": str(card_mid_y + 58),
        "stroke": AMBER, "stroke-width": "2", "opacity": "0.4"
    })

    # Left value
    add_text(svg, WIDTH / 2 - 38, card_mid_y + 26, "fixed infra", fill=AMBER, font_size=42, anchor="end", weight="bold")
    add_text(svg, WIDTH / 2 - 38, card_mid_y + 60, "Qwen-LoRA — predictable", fill=MUTED, font_size=16, anchor="end")

    # Right value
    add_text(svg, WIDTH / 2 + 38, card_mid_y + 26, "per-token API", fill=AMBER_LIGHT, font_size=42, anchor="start", weight="bold")
    add_text(svg, WIDTH / 2 + 38, card_mid_y + 60, "GPT-4o-mini — scales with load", fill=MUTED, font_size=16, anchor="start")

    tree = ET.ElementTree(svg)
    OUT_SVG_LANDING.parent.mkdir(parents=True, exist_ok=True)
    OUT_SVG_PORTFOLIO.parent.mkdir(parents=True, exist_ok=True)
    tree.write(OUT_SVG_LANDING, encoding="utf-8", xml_declaration=True)
    tree.write(OUT_SVG_PORTFOLIO, encoding="utf-8", xml_declaration=True)


def main():
    lora, gpt = load_optimized_metrics()
    build_svg(lora, gpt)
    print(f"Saved:\n  {OUT_SVG_LANDING}\n  {OUT_SVG_PORTFOLIO}")


if __name__ == "__main__":
    main()
