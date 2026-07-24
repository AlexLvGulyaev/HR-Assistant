#!/usr/bin/env python3
"""
Генерация D-007 — Next cycle roadmap для сцены 15.

Изменения:
- увеличен шрифт заголовков и подписей карточек;
- подпись "production FPR/FNR by segment" разбита на две строки;
- карточки стали выше, чтобы вместить увеличенный текст.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]  # cases/hr-assistant
OUT_SVG = ROOT / "portfolio_visuals" / "svg" / "D-007-next-cycle-roadmap.svg"
LANDING_SVG = ROOT / "landing" / "assets" / "visuals" / "D-007-next-cycle-roadmap.svg"

# --- Палитра ----------------------------------------------------------------
BG = "#0d0d10"
CARD_BG = "#1a1a24"
CARD_BORDER = "#2a2a36"
TEXT_MAIN = "#e8e8ec"
TEXT_MUTED = "#8a8a9a"
COLOR_CALIBRATION = "#FFB347"
COLOR_AUGMENTATION = "#FF6B6B"
COLOR_METRICS = "#4ECDC4"
COLOR_SERVER = "#96CEB4"

# --- Размеры ----------------------------------------------------------------
WIDTH, HEIGHT = 820, 340
CARD_W = 175
CARD_H = 185
CARD_Y = 110
GAP = 20
MARGIN_LEFT = 34

TITLE_FONT = 20
SUBTITLE_FONT = 14
HEADER_FONT = 18
ITEM_FONT = 14


def build_svg():
    cards = [
        ("Calibration", COLOR_CALIBRATION, ["MAE closer", "to GPT"]),
        ("Augmentation", COLOR_AUGMENTATION, ["stratified hard", "negatives"]),
        ("Metrics", COLOR_METRICS, ["production FPR/FNR", "by segment"]),
        ("Server", COLOR_SERVER, ["quantized persistent", "vLLM"]),
    ]

    total_cards_width = len(cards) * CARD_W + (len(cards) - 1) * GAP
    start_x = (WIDTH - total_cards_width) / 2

    elements = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {HEIGHT}" width="{WIDTH}" height="{HEIGHT}" role="img" aria-label="Next cycle roadmap">\n',
        f'<rect width="{WIDTH}" height="{HEIGHT}" fill="{BG}" rx="8"/>\n',
        f'<text x="{MARGIN_LEFT}" y="42" fill="{TEXT_MAIN}" font-size="{TITLE_FONT}" font-family="Inter, sans-serif" text-anchor="start" font-weight="600">Next cycle roadmap</text>\n',
        f'<text x="{MARGIN_LEFT}" y="70" fill="{TEXT_MUTED}" font-size="{SUBTITLE_FONT}" font-family="Inter, sans-serif" text-anchor="start">Each closed question opens a new one</text>\n',
    ]

    for idx, (title, color, lines) in enumerate(cards):
        x = start_x + idx * (CARD_W + GAP)
        cx = x + CARD_W / 2

        # Card background
        elements.append(
            f'<rect x="{x}" y="{CARD_Y}" width="{CARD_W}" height="{CARD_H}" fill="{CARD_BG}" stroke="{CARD_BORDER}" stroke-width="1" rx="8"/>'
        )

        # Header
        elements.append(
            f'<text x="{cx}" y="{CARD_Y + 40}" fill="{color}" font-size="{HEADER_FONT}" font-family="Inter, sans-serif" text-anchor="middle" font-weight="700">{title}</text>'
        )

        # Multi-line body text
        line_y = CARD_Y + 85
        for line in lines:
            elements.append(
                f'<text x="{cx}" y="{line_y}" fill="{TEXT_MUTED}" font-size="{ITEM_FONT}" font-family="Inter, sans-serif" text-anchor="middle">{line}</text>'
            )
            line_y += 24

    elements.append("\n</svg>\n")
    return "\n".join(elements)


def main():
    svg = build_svg()
    OUT_SVG.parent.mkdir(parents=True, exist_ok=True)
    OUT_SVG.write_text(svg, encoding="utf-8")
    LANDING_SVG.parent.mkdir(parents=True, exist_ok=True)
    LANDING_SVG.write_text(svg, encoding="utf-8")
    print(f"D-007 written: {OUT_SVG}")
    print(f"D-007 landing: {LANDING_SVG}")


if __name__ == "__main__":
    main()
