#!/usr/bin/env python3
"""
Генерация D-008 — Proven · Partial · Next для сцены 14 (Честный диагноз).

Изменения по сравнению с предыдущей версией:
- увеличен шрифт внутри карточек и заголовков;
- расстояние между строками увеличено, чтобы текст не слипался;
- карточки стали выше, чтобы вместить увеличенный текст.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]  # cases/hr-assistant
OUT_SVG = ROOT / "portfolio_visuals" / "svg" / "D-008-proven-partial-next.svg"
LANDING_SVG = ROOT / "landing" / "assets" / "visuals" / "D-008-proven-partial-next.svg"

# --- Палитра ----------------------------------------------------------------
BG = "#0d0d10"
CARD_BG = "#1a1a24"
CARD_BORDER = "#2a2a36"
TEXT_MAIN = "#e8e8ec"
TEXT_MUTED = "#8a8a9a"
COLOR_PROVEN = "#96CEB4"
COLOR_PARTIAL = "#FFB347"
COLOR_NEXT = "#FF6B6B"

# --- Размеры ----------------------------------------------------------------
WIDTH, HEIGHT = 960, 520
CARD_W = 290
CARD_H = 360
CARD_Y = 125
GAP = 20
MARGIN_LEFT = 36

# --- Данные -----------------------------------------------------------------
SECTIONS = [
    ("Proven", COLOR_PROVEN, [
        "Dataset engineering works",
        "Production smoke gate stable",
        "Latency viable with vLLM",
        "External validation 0.931",
    ]),
    ("Partial", COLOR_PARTIAL, [
        "Near GPT on decisions",
        "Quality holds on rerun",
        "Hard-negative coverage",
    ]),
    ("Next", COLOR_NEXT, [
        "Score calibration parity",
        "Stratified FPR/FNR",
        "Quantized server",
        "Full GPT parity",
    ]),
]

TITLE_FONT = 22
SUBTITLE_FONT = 15
HEADER_FONT = 21
ITEM_FONT = 17


def build_svg():
    elements = []
    elements.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {HEIGHT}" width="{WIDTH}" height="{HEIGHT}" role="img" aria-label="Proven partial next map">\n'
        f'<rect width="{WIDTH}" height="{HEIGHT}" fill="{BG}" rx="8"/>\n'
        f'<text x="{MARGIN_LEFT}" y="50" fill="{TEXT_MAIN}" font-size="{TITLE_FONT}" font-family="Inter, sans-serif" text-anchor="start" font-weight="600">Proven · Partial · Next</text>\n'
        f'<text x="{MARGIN_LEFT}" y="84" fill="{TEXT_MUTED}" font-size="{SUBTITLE_FONT}" font-family="Inter, sans-serif" text-anchor="start">Honest classification of what the experiments established</text>\n'
    )

    total_cards_width = len(SECTIONS) * CARD_W + (len(SECTIONS) - 1) * GAP
    start_x = (WIDTH - total_cards_width) / 2

    for idx, (title, color, items) in enumerate(SECTIONS):
        x = start_x + idx * (CARD_W + GAP)
        cx = x + CARD_W / 2

        # Card background
        elements.append(
            f'<rect x="{x}" y="{CARD_Y}" width="{CARD_W}" height="{CARD_H}" fill="{CARD_BG}" stroke="{CARD_BORDER}" stroke-width="1" rx="8"/>'
        )

        # Header
        elements.append(
            f'<text x="{cx}" y="{CARD_Y + 54}" fill="{color}" font-size="{HEADER_FONT}" font-family="Inter, sans-serif" text-anchor="middle" font-weight="700">{title}</text>'
        )

        # Items
        item_y = CARD_Y + 108
        for item in items:
            elements.append(
                f'<text x="{x + 22}" y="{item_y}" fill="{TEXT_MAIN}" font-size="{ITEM_FONT}" font-family="Inter, sans-serif" text-anchor="start">• {item}</text>'
            )
            item_y += 50

    elements.append("\n</svg>\n")
    return "\n".join(elements)


def main():
    svg = build_svg()
    OUT_SVG.parent.mkdir(parents=True, exist_ok=True)
    OUT_SVG.write_text(svg, encoding="utf-8")
    LANDING_SVG.parent.mkdir(parents=True, exist_ok=True)
    LANDING_SVG.write_text(svg, encoding="utf-8")
    print(f"D-008 written: {OUT_SVG}")
    print(f"D-008 landing: {LANDING_SVG}")


if __name__ == "__main__":
    main()
