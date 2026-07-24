#!/usr/bin/env python3
"""
Генератор G-026: сцена 11 «Smoke repeatability».
Матрица runtime smoke: 6 строк × 3 столбца.
Столбцы: Exp 003, Exp 004, rerun.
Все ячейки — PASS.
"""

from pathlib import Path
import xml.etree.ElementTree as ET


ROOT = Path("/opt/ai-automation-portfolio-lab/cases/hr-assistant")
OUT_SVG_LANDING = ROOT / "landing/assets/visuals/G-026-smoke-repeatability-matrix.svg"
OUT_SVG_PORTFOLIO = ROOT / "portfolio_visuals/svg/G-026-smoke-repeatability-matrix.svg"


BG = "#0d1117"
PANEL_BG = "#161b22"
GRID = "#30363d"
TEXT = "#e6edf3"
MUTED = "#8b949e"
PASS_COLOR = "#238636"

WIDTH = 676
HEIGHT = 832


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


def main():
    experiments = ["Exp 003", "Exp 004", "rerun"]
    categories = [
        "positive",
        "obvious_negative",
        "hard_negative",
        "edge_case",
        "invalid_input",
        "stability_repeat",
    ]
    category_labels = [
        "Positive",
        "Obvious Negative",
        "Hard Negative",
        "Edge Case",
        "Invalid Input",
        "Stability Repeat",
    ]

    svg = ET.Element("svg", {
        "xmlns": "http://www.w3.org/2000/svg",
        "width": str(WIDTH), "height": str(HEIGHT),
        "viewBox": f"0 0 {WIDTH} {HEIGHT}",
        "role": "img",
        "aria-label": "Runtime smoke repeatability matrix"
    })

    add_rect(svg, 0, 0, WIDTH, HEIGHT, BG)

    # Title
    add_text(svg, WIDTH / 2, 46, "Runtime smoke repeatability", fill=TEXT, font_size=23, anchor="middle", weight="bold")
    add_text(svg, WIDTH / 2, 76, "7/7 passed across three production runs", fill=MUTED, font_size=15, anchor="middle")

    # Matrix geometry
    margin_left = 180
    margin_top = 120
    cell_w = 142
    cell_h = 90
    gap_x = 10
    gap_y = 8

    # Column headers (experiments)
    for i, exp in enumerate(experiments):
        x = margin_left + i * (cell_w + gap_x) + cell_w / 2
        add_text(svg, x, margin_top - 20, exp, fill=TEXT, font_size=18, anchor="middle", weight="bold")

    # Row headers (categories) + cells
    for row, (cat, label) in enumerate(zip(categories, category_labels)):
        y = margin_top + row * (cell_h + gap_y)

        # Row label
        add_text(svg, margin_left - 16, y + cell_h / 2 + 6, label, fill=MUTED, font_size=15, anchor="end")

        # Cells
        for col in range(len(experiments)):
            x = margin_left + col * (cell_w + gap_x)
            add_rect(svg, x, y, cell_w, cell_h, PASS_COLOR, stroke=GRID, stroke_width=1, rx=5)
            add_text(svg, x + cell_w / 2, y + cell_h / 2 + 7, "PASS", fill=BG, font_size=20, anchor="middle", weight="bold")

    tree = ET.ElementTree(svg)
    OUT_SVG_LANDING.parent.mkdir(parents=True, exist_ok=True)
    OUT_SVG_PORTFOLIO.parent.mkdir(parents=True, exist_ok=True)

    tree.write(OUT_SVG_LANDING, encoding="utf-8", xml_declaration=True)
    tree.write(OUT_SVG_PORTFOLIO, encoding="utf-8", xml_declaration=True)

    print(f"Saved:\n  {OUT_SVG_LANDING}\n  {OUT_SVG_PORTFOLIO}")


if __name__ == "__main__":
    main()
