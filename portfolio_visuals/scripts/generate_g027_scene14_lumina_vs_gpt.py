#!/usr/bin/env python3
"""
Generate G-027 — Scene 14: Lumina vs GPT-4o-mini.

Visual concept (adapted for blueprint v2):
  - Left: Lumina — large, confident, production-ready AI form (teal, antennas up, steady glow).
  - Right: GPT-4o-mini reference — smaller, muted, angular/brutal cloud-AI form (steel blue-grey).
  - Bottom: comparison metric cards (LoRA vs GPT) from optimized external validation.

Data source: finetuning/landing/data/experimentData.js via the optimized external validation summary
(102 records, vLLM + warm process).
"""

import json
from pathlib import Path
import xml.etree.ElementTree as ET


ROOT = Path("/opt/ai-automation-portfolio-lab/cases/hr-assistant")
EXPERIMENT_DATA = ROOT / "finetuning/landing/data/experimentData.js"
OUT_SVG_LANDING = ROOT / "finetuning/landing/assets/visuals/G-027-lumina-vs-gpt.svg"
OUT_SVG_PORTFOLIO = ROOT / "portfolio_visuals/svg/G-027-lumina-vs-gpt.svg"

# Palette
BG = "#0d0d10"
PANEL_BG = "#16161f"
GRID = "#2a2a36"
TEXT = "#e8e8ec"
MUTED = "#8a8a9a"
TEAL = "#4ECDC4"
STEEL = "#5A7A8C"
STEEL_DIM = "#3A4F5C"
GREEN = "#96CEB4"
WHITE = "#ffffff"

WIDTH, HEIGHT = 1100, 680


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
    # experimentData.js is a JS object literal; extract the JSON body via brace matching.
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


def draw_lumina(parent, cx, cy, scale=1.0):
    """Draw a confident, production-ready Lumina AI form."""
    s = scale
    face_r = 54 * s
    halo_r = 105 * s
    color = TEAL

    # Outer glow
    glow_id = "lumina-glow"
    defs = ET.SubElement(parent, "defs")
    grad = ET.SubElement(defs, "radialGradient", {"id": glow_id, "cx": "50%", "cy": "50%", "r": "50%"})
    ET.SubElement(grad, "stop", {"offset": "0%", "stop-color": color, "stop-opacity": "0.22"})
    ET.SubElement(grad, "stop", {"offset": "60%", "stop-color": color, "stop-opacity": "0.08"})
    ET.SubElement(grad, "stop", {"offset": "100%", "stop-color": color, "stop-opacity": "0"})
    ET.SubElement(parent, "circle", {"cx": str(cx), "cy": str(cy), "r": str(halo_r + 35 * s), "fill": f"url(#{glow_id})"})

    # Halo rings
    for i, r in enumerate([halo_r, halo_r - 18 * s, halo_r - 36 * s]):
        op = 0.45 - i * 0.12
        ET.SubElement(parent, "circle", {
            "cx": str(cx), "cy": str(cy), "r": str(r),
            "fill": "none", "stroke": color, "stroke-width": str(1.2 + i * 0.4), "opacity": str(op)
        })

    # Antennae (5, upright)
    for i in range(5):
        a = -90 + (i - 2) * 18
        arad = a * 3.14159 / 180
        x1 = cx + (face_r - 4 * s) * s * 0  # start at top of face
        y1 = cy - face_r
        x2 = cx + (face_r + 32 * s + i * 5 * s) * 0  # placeholder; computed below
        # Correct antenna line
        x1 = cx + (face_r - 2 * s) * __import__('math').cos(arad)
        y1 = cy + (face_r - 2 * s) * __import__('math').sin(arad)
        x2 = cx + (face_r + 28 * s + i * 4 * s) * __import__('math').cos(arad)
        y2 = cy + (face_r + 28 * s + i * 4 * s) * __import__('math').sin(arad)
        ET.SubElement(parent, "line", {
            "x1": str(x1), "y1": str(y1), "x2": str(x2), "y2": str(y2),
            "stroke": color, "stroke-width": str(2.2 * s), "stroke-linecap": "round", "opacity": "0.85"
        })
        ET.SubElement(parent, "circle", {"cx": str(x2), "cy": str(y2), "r": str(4 * s), "fill": color, "opacity": "0.95"})

    # Halo nodes
    n_nodes = 8
    for i in range(n_nodes):
        a = i * 2 * 3.14159 / n_nodes
        nx = cx + halo_r * __import__('math').cos(a)
        ny = cy + halo_r * __import__('math').sin(a)
        ET.SubElement(parent, "circle", {"cx": str(nx), "cy": str(ny), "r": str(3 * s), "fill": color, "opacity": "0.6"})

    # Face
    ET.SubElement(parent, "circle", {
        "cx": str(cx), "cy": str(cy), "r": str(face_r),
        "fill": "rgba(10,10,12,0.55)", "stroke": color, "stroke-width": str(2 * s), "opacity": "0.95"
    })

    # Eyes (confident, slightly narrowed)
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

    # Slight confident smile
    my = cy + 14 * s
    ET.SubElement(parent, "path", {
        "d": f"M{cx - 10 * s} {my} Q{cx} {my + 7 * s} {cx + 10 * s} {my}",
        "fill": "none", "stroke": WHITE, "stroke-width": str(2.2 * s),
        "stroke-linecap": "round", "opacity": "0.85"
    })


def draw_gpt_form(parent, cx, cy, scale=1.0):
    """Draw a smaller, muted, angular/brutal cloud-AI reference form."""
    s = scale
    size = 65 * s
    color = STEEL
    dim = STEEL_DIM

    # Glow (weaker)
    glow_id = "gpt-glow"
    defs = parent.find("defs")
    if defs is None:
        defs = ET.SubElement(parent, "defs")
    grad = ET.SubElement(defs, "radialGradient", {"id": glow_id, "cx": "50%", "cy": "50%", "r": "50%"})
    ET.SubElement(grad, "stop", {"offset": "0%", "stop-color": color, "stop-opacity": "0.10"})
    ET.SubElement(grad, "stop", {"offset": "60%", "stop-color": color, "stop-opacity": "0.04"})
    ET.SubElement(grad, "stop", {"offset": "100%", "stop-color": color, "stop-opacity": "0"})
    ET.SubElement(parent, "circle", {"cx": str(cx), "cy": str(cy), "r": str(size + 60 * s), "fill": f"url(#{glow_id})"})

    # Angular outer shell (hexagon-ish)
    pts = []
    n = 6
    for i in range(n):
        a = i * 2 * 3.14159 / n - 3.14159 / 2
        r = size + 22 * s
        pts.append(f"{cx + r * __import__('math').cos(a)},{cy + r * __import__('math').sin(a)}")
    ET.SubElement(parent, "polygon", {
        "points": " ".join(pts), "fill": "none", "stroke": dim, "stroke-width": str(1.5 * s), "opacity": "0.5"
    })

    # Inner angular core (octagon)
    pts2 = []
    for i in range(8):
        a = i * 2 * 3.14159 / 8 - 3.14159 / 2
        r = size
        pts2.append(f"{cx + r * __import__('math').cos(a)},{cy + r * __import__('math').sin(a)}")
    ET.SubElement(parent, "polygon", {
        "points": " ".join(pts2), "fill": "rgba(10,10,12,0.55)", "stroke": color, "stroke-width": str(2 * s), "opacity": "0.9"
    })

    # Cross-shaped antenna / grid lines (angular, brutal)
    for angle in (-90, 0, 90, 180):
        arad = angle * 3.14159 / 180
        x2 = cx + (size + 36 * s) * __import__('math').cos(arad)
        y2 = cy + (size + 36 * s) * __import__('math').sin(arad)
        ET.SubElement(parent, "line", {
            "x1": str(cx), "y1": str(cy), "x2": str(x2), "y2": str(y2),
            "stroke": dim, "stroke-width": str(1.5 * s), "opacity": "0.5"
        })
        ET.SubElement(parent, "circle", {"cx": str(x2), "cy": str(y2), "r": str(3.5 * s), "fill": color, "opacity": "0.7"})

    # Eyes (puzzled / neutral)
    eye_y = cy - 4 * s
    eye_size = 5 * s
    eye_xo = 22 * s
    for dx in (-eye_xo, eye_xo):
        ET.SubElement(parent, "circle", {"cx": str(cx + dx), "cy": str(eye_y), "r": str(eye_size), "fill": WHITE, "opacity": "0.85"})

    # Flat/questioning mouth
    my = cy + 16 * s
    ET.SubElement(parent, "line", {
        "x1": str(cx - 10 * s), "y1": str(my), "x2": str(cx + 10 * s), "y2": str(my),
        "stroke": WHITE, "stroke-width": str(2 * s), "stroke-linecap": "round", "opacity": "0.7"
    })



def format_latency(ms):
    return f"{ms / 1000:.1f}s"


def build_svg(lora, gpt):
    svg = ET.Element("svg", {
        "xmlns": "http://www.w3.org/2000/svg",
        "width": str(WIDTH), "height": str(HEIGHT),
        "viewBox": f"0 0 {WIDTH} {HEIGHT}",
        "role": "img",
        "aria-label": "LoRA vs GPT-4o-mini comparison"
    })

    # Background
    add_rect(svg, 0, 0, WIDTH, HEIGHT, BG)

    # Title
    add_text(svg, WIDTH / 2, 46, "LoRA vs GPT-4o-mini", fill=TEXT, font_size=24, anchor="middle", weight="bold")
    add_text(svg, WIDTH / 2, 76, "External validation on 102 unseen records (vLLM + warm process)", fill=MUTED, font_size=14, anchor="middle")

    # Characters
    lumina_cx, lumina_cy = 220, 230
    gpt_cx, gpt_cy = 880, 250
    draw_lumina(svg, lumina_cx, lumina_cy, scale=1.15)
    draw_gpt_form(svg, gpt_cx, gpt_cy, scale=0.95)

    # Labels under characters
    add_text(svg, lumina_cx, lumina_cy + 140, "LoRA", fill=TEAL, font_size=18, anchor="middle", weight="bold")
    add_text(svg, lumina_cx, lumina_cy + 164, "local · fine-tuned", fill=MUTED, font_size=12, anchor="middle")
    add_text(svg, gpt_cx, gpt_cy + 120, "GPT-4o-mini", fill=STEEL, font_size=16, anchor="middle", weight="bold")
    add_text(svg, gpt_cx, gpt_cy + 142, "cloud reference", fill=MUTED, font_size=12, anchor="middle")

    # Metric cards at bottom
    metrics = [
        ("Decision accuracy", f"{lora['decision_accuracy'] * 100:.1f}%", f"{gpt['decision_accuracy'] * 100:.1f}%", "LoRA", "GPT"),
        ("MAE score", f"{lora['mae_score']:.1f}", f"{gpt['mae_score']:.1f}", "lower is better", "lower is better"),
        ("Latency p50", format_latency(lora['latency_p50']), format_latency(gpt['latency_p50']), "local vLLM", "cloud API"),
        ("Runtime cost", "fixed infra", "per-token API", "predictable", "scales with load"),
    ]

    card_w = 220
    card_h = 110
    gap = 24
    total_w = len(metrics) * card_w + (len(metrics) - 1) * gap
    start_x = (WIDTH - total_w) / 2
    card_y = HEIGHT - card_h - 30

    for i, (label, lora_val, gpt_val, lora_note, gpt_note) in enumerate(metrics):
        x = start_x + i * (card_w + gap)
        add_rect(svg, x, card_y, card_w, card_h, PANEL_BG, stroke=GRID, stroke_width=1, rx=8)
        add_text(svg, x + card_w / 2, card_y + 26, label, fill=MUTED, font_size=12, anchor="middle", weight="normal")

        # LoRA value (left half)
        add_text(svg, x + 26, card_y + 58, lora_val, fill=TEAL, font_size=20, anchor="start", weight="bold")
        add_text(svg, x + 26, card_y + 80, "LoRA", fill=MUTED, font_size=11, anchor="start")

        # GPT value (right half)
        add_text(svg, x + card_w - 26, card_y + 58, gpt_val, fill=STEEL, font_size=18, anchor="end", weight="bold")
        add_text(svg, x + card_w - 26, card_y + 80, "GPT", fill=MUTED, font_size=11, anchor="end")

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
