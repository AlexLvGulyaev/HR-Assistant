#!/usr/bin/env python3
"""Generate D-010-dataset-change-log.svg for landing scene 17."""
import os

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "landing", "assets", "visuals")
OUTPUT_PATH = os.path.join(OUTPUT_DIR, "D-010-dataset-change-log.svg")

VIEWBOX_W, VIEWBOX_H = 800, 450

# Panel positions
PANEL_W = 360
PANEL_H = 330
PANEL_Y = 90
LEFT_X = 30
RIGHT_X = 410

# Dataset facts
EXP = ["001", "002", "003", "004"]
RECORDS = [90, 90, 123, 162]
DELTAS = ["+90", "same", "+33", "+39"]
DELTA_COLORS = ["#FFB347", "#8a8a9a", "#FFB347", "#96CEB4"]
NOTES = [
    None,
    None,
    "Exp 003: +33 hard negatives",
    "Exp 004: +39 positives/borderlines",
]


def build_svg() -> str:
    parts = []
    parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {VIEWBOX_W} {VIEWBOX_H}" '
        f'width="{VIEWBOX_W}" height="{VIEWBOX_H}" role="img" aria-label="Dataset change log">'
    )
    parts.append('<defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L0,6 L9,3 z" fill="#ffffff"/></marker></defs>')
    parts.append(f'<rect width="{VIEWBOX_W}" height="{VIEWBOX_H}" fill="#0d0d10" rx="8"/>')

    # Title
    parts.append(f'<text x="30" y="38" fill="#e8e8ec" font-size="20" font-family="Inter, sans-serif" text-anchor="start" font-weight="600">Dataset change log &amp; controlled variables</text>')
    parts.append(f'<text x="30" y="66" fill="#8a8a9a" font-size="13" font-family="Inter, sans-serif" text-anchor="start" font-weight="normal">LoRA config unchanged; only dataset composition changed</text>')

    # Left panel: controlled variables
    parts.append(f'<rect x="{LEFT_X}" y="{PANEL_Y}" width="{PANEL_W}" height="{PANEL_H}" fill="#1a1a24" stroke="#2a2a36" stroke-width="1" rx="6"/>')
    parts.append(f'<text x="{LEFT_X + PANEL_W / 2}" y="{PANEL_Y + 32}" fill="#ffffff" font-size="15" font-family="Inter, sans-serif" text-anchor="middle" font-weight="600">Controlled variables</text>')
    vars_ = [
        "Base model: Qwen2.5-1.5B-Instruct",
        "LoRA r: 16",
        "LoRA α: 32",
        "Dropout: 0.05",
        "Target modules: 7",
        "Epochs: 5",
        "LR: 2e-4 linear decay",
    ]
    y = PANEL_Y + 70
    for v in vars_:
        parts.append(f'<text x="{LEFT_X + 16}" y="{y}" fill="#8a8a9a" font-size="13" font-family="Inter, sans-serif" text-anchor="start" font-weight="normal">{v}</text>')
        y += 32

    # Right panel: dataset changes
    parts.append(f'<rect x="{RIGHT_X}" y="{PANEL_Y}" width="{PANEL_W}" height="{PANEL_H}" fill="#1a1a24" stroke="#2a2a36" stroke-width="1" rx="6"/>')
    parts.append(f'<text x="{RIGHT_X + PANEL_W / 2}" y="{PANEL_Y + 32}" fill="#ffffff" font-size="15" font-family="Inter, sans-serif" text-anchor="middle" font-weight="600">Dataset changes</text>')

    # Table header
    header_y = PANEL_Y + 72
    parts.append(f'<text x="{RIGHT_X + 20}" y="{header_y}" fill="#8a8a9a" font-size="13" font-family="Inter, sans-serif" text-anchor="start" font-weight="600">Exp</text>')
    parts.append(f'<text x="{RIGHT_X + 90}" y="{header_y}" fill="#8a8a9a" font-size="13" font-family="Inter, sans-serif" text-anchor="start" font-weight="600">Records</text>')
    parts.append(f'<text x="{RIGHT_X + 200}" y="{header_y}" fill="#8a8a9a" font-size="13" font-family="Inter, sans-serif" text-anchor="start" font-weight="600">Δ</text>')

    # Table rows
    row_y = header_y + 36
    for exp, rec, delta, color in zip(EXP, RECORDS, DELTAS, DELTA_COLORS):
        parts.append(f'<text x="{RIGHT_X + 20}" y="{row_y}" fill="#e8e8ec" font-size="13" font-family="Inter, sans-serif" text-anchor="start" font-weight="normal">{exp}</text>')
        parts.append(f'<text x="{RIGHT_X + 90}" y="{row_y}" fill="#e8e8ec" font-size="13" font-family="Inter, sans-serif" text-anchor="start" font-weight="normal">{rec}</text>')
        parts.append(f'<text x="{RIGHT_X + 200}" y="{row_y}" fill="{color}" font-size="13" font-family="Inter, sans-serif" text-anchor="start" font-weight="normal">{delta}</text>')
        row_y += 36

    # Notes
    note_y = PANEL_Y + PANEL_H - 30
    for note, color in zip(NOTES, DELTA_COLORS):
        if note:
            parts.append(f'<text x="{RIGHT_X + 20}" y="{note_y}" fill="{color}" font-size="12" font-family="Inter, sans-serif" text-anchor="start" font-weight="normal">{note}</text>')
            note_y += 24

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
