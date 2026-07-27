#!/usr/bin/env python3
"""
Generate G-016-best-epoch-markers.svg for landing scene 16.

Facts (source: trainer_state.json in each experiment run):
  Exp 001: 5 epochs, best checkpoint-72 -> epoch 4
  Exp 002: 5 epochs, best checkpoint-54 -> epoch 3
  Exp 003: 5 epochs, best checkpoint-48 -> epoch 2
  Exp 004: 5 epochs, best checkpoint-87 -> epoch 3
"""

import os

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "finetuning", "landing", "assets", "visuals")
OUTPUT_PATH = os.path.join(OUTPUT_DIR, "G-016-best-epoch-markers.svg")

VIEWBOX_W, VIEWBOX_H = 800, 420

# Chart area
MARGIN_LEFT = 90
MARGIN_RIGHT = 90
MARGIN_TOP = 90
MARGIN_BOTTOM = 70

CHART_LEFT = MARGIN_LEFT
CHART_RIGHT = VIEWBOX_W - MARGIN_RIGHT
CHART_TOP = MARGIN_TOP
CHART_BOTTOM = VIEWBOX_H - MARGIN_BOTTOM
CHART_W = CHART_RIGHT - CHART_LEFT
CHART_H = CHART_BOTTOM - CHART_TOP

MAX_EPOCH = 5
BAR_COUNT = 4
BAR_WIDTH = 86
BAR_GAP = (CHART_W - BAR_COUNT * BAR_WIDTH) / (BAR_COUNT - 1)

COLORS = ["#4ECDC4", "#FFB347", "#FF6B6B", "#96CEB4"]
EXPERIMENTS = ["Exp 001", "Exp 002", "Exp 003", "Exp 004"]
BEST_EPOCHS = [4, 3, 2, 3]


def y_for_epoch(epoch: int) -> float:
    """Bottom of a bar for the given epoch count (from bottom axis)."""
    return CHART_BOTTOM - (epoch / MAX_EPOCH) * CHART_H


def build_svg() -> str:
    parts = []
    parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {VIEWBOX_W} {VIEWBOX_H}" '
        f'width="{VIEWBOX_W}" height="{VIEWBOX_H}" role="img" aria-label="Best epoch per experiment">'
    )
    parts.append('<defs>')
    parts.append('  <marker id="arrow" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto" markerUnits="strokeWidth">')
    parts.append('    <path d="M0,0 L0,6 L9,3 z" fill="#ffffff"/>')
    parts.append('  </marker>')
    parts.append('</defs>')

    # Background
    parts.append(f'<rect width="{VIEWBOX_W}" height="{VIEWBOX_H}" fill="#0d0d10" rx="8"/>')

    # Title & subtitle
    parts.append(f'<text x="40" y="42" fill="#e8e8ec" font-size="20" font-family="Inter, sans-serif" text-anchor="start" font-weight="600">Best epoch per experiment</text>')
    parts.append(f'<text x="40" y="66" fill="#8a8a9a" font-size="13" font-family="Inter, sans-serif" text-anchor="start" font-weight="normal">Best checkpoint was never the final epoch (trained for 5 epochs each)</text>')

    # Y-axis grid lines and labels (epochs 1..5)
    for epoch in range(1, MAX_EPOCH + 1):
        y = y_for_epoch(epoch)
        parts.append(f'<line x1="{CHART_LEFT}" y1="{y}" x2="{CHART_RIGHT}" y2="{y}" stroke="#2a2a35" stroke-width="1"/>')
        parts.append(f'<text x="{CHART_LEFT - 12}" y="{y + 4}" fill="#8a8a9a" font-size="12" font-family="Inter, sans-serif" text-anchor="end" font-weight="normal">{epoch}</text>')

    # Y-axis label
    parts.append(f'<text x="30" y="{CHART_TOP + CHART_H / 2}" fill="#8a8a9a" font-size="12" font-family="Inter, sans-serif" text-anchor="middle" font-weight="normal" transform="rotate(-90, 30, {CHART_TOP + CHART_H / 2})">epoch</text>')

    # Final epoch reference line & label
    final_y = y_for_epoch(MAX_EPOCH)
    parts.append(f'<line x1="{CHART_LEFT}" y1="{final_y}" x2="{CHART_RIGHT}" y2="{final_y}" stroke="#8a8a9a" stroke-width="1.5" stroke-dasharray="5,5"/>')
    parts.append(f'<text x="{CHART_RIGHT + 8}" y="{final_y + 4}" fill="#8a8a9a" font-size="11" font-family="Inter, sans-serif" text-anchor="start" font-weight="normal">final epoch = 5</text>')

    # Bars
    for i, (exp, best_epoch, color) in enumerate(zip(EXPERIMENTS, BEST_EPOCHS, COLORS)):
        x = CHART_LEFT + i * (BAR_WIDTH + BAR_GAP)
        bar_top = y_for_epoch(best_epoch)
        bar_bottom = y_for_epoch(0)
        bar_h = bar_bottom - bar_top

        # Ghost bar showing full 5-epoch height (subtle)
        full_top = y_for_epoch(MAX_EPOCH)
        full_h = bar_bottom - full_top
        parts.append(f'<rect x="{x}" y="{full_top}" width="{BAR_WIDTH}" height="{full_h}" fill="{color}" opacity="0.10" rx="4"/>')

        # Real best-epoch bar
        parts.append(f'<rect x="{x}" y="{bar_top}" width="{BAR_WIDTH}" height="{bar_h}" fill="{color}" rx="4"/>')

        # Epoch label above bar
        parts.append(f'<text x="{x + BAR_WIDTH / 2}" y="{bar_top - 12}" fill="{color}" font-size="16" font-family="Inter, sans-serif" text-anchor="middle" font-weight="700">ep {best_epoch}</text>')

        # "of 5" label inside top of ghost bar
        parts.append(f'<text x="{x + BAR_WIDTH / 2}" y="{full_top + 16}" fill="{color}" font-size="10" font-family="Inter, sans-serif" text-anchor="middle" font-weight="500" opacity="0.7">of 5</text>')

        # X-axis label
        parts.append(f'<text x="{x + BAR_WIDTH / 2}" y="{CHART_BOTTOM + 22}" fill="#e8e8ec" font-size="13" font-family="Inter, sans-serif" text-anchor="middle" font-weight="normal">{exp}</text>')

    # Bottom axis line
    parts.append(f'<line x1="{CHART_LEFT}" y1="{CHART_BOTTOM}" x2="{CHART_RIGHT}" y2="{CHART_BOTTOM}" stroke="#8a8a9a" stroke-width="2"/>')

    parts.append('</svg>')
    return "\n".join(parts)


def main() -> None:
    svg = build_svg()
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"Written {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
