#!/usr/bin/env python3
"""
Генерация G-012 — Latency stage breakdown для сцены 13a.

Источник данных: latency.stage_profile из JSON-репорта.
Если файл отсутствует, используем fallback-значения из текущего landing.

Дизайн-решение:
- значения размещаются СПРАВА от полосок;
- шкала укорочена до ~70% ширины, чтобы метки точно влезали;
- фон шкалы продолжается серым цветом до 100%, сохраняя визуальную пропорцию;
- generate всё равно занимает почти всю длину, и читатель видит доминирование.
"""

import json
import sys
from pathlib import Path

# --- Пути -------------------------------------------------------------------
ROOT = Path(__file__).resolve().parents[2]  # cases/hr-assistant
OUT_SVG = ROOT / "portfolio_visuals" / "svg" / "G-012-latency-stage-breakdown.svg"
LANDING_SVG = ROOT / "landing" / "assets" / "visuals" / "G-012-latency-stage-breakdown.svg"

DATA_SOURCE = ROOT / "finetuning" / "data" / "latency_stage_profile.json"

# --- Fallback данные (соответствуют текущему landing) -----------------------
FALLBACK_STAGES = [
    ("chat template", 0.2, 0.0),
    ("tokenize", 2.0, 0.0),
    ("generate", 9630.1, 100.0),
    ("decode", 0.5, 0.0),
]

# --- Палитра ----------------------------------------------------------------
BG = "#0d0d10"
CARD_BG = "#16161f"
TEXT_MAIN = "#e8e8ec"
TEXT_MUTED = "#8a8a9a"
ACCENT_MINOR = "#4ECDC4"
ACCENT_MAJOR = "#FF6B6B"
TRACK_BG = "#25252d"

WIDTH, HEIGHT = 640, 360
MARGIN_LEFT = 120
MARGIN_RIGHT = 24
BAR_Y_START = 95
BAR_HEIGHT = 34
BAR_GAP = 32

# Шкала занимает 70% свободной ширины, чтобы справа осталось место для меток
SCALE_WIDTH = int((WIDTH - MARGIN_LEFT - MARGIN_RIGHT) * 0.70)
LABEL_X = MARGIN_LEFT + SCALE_WIDTH + 12


def load_data():
    if DATA_SOURCE.exists():
        data = json.loads(DATA_SOURCE.read_text(encoding="utf-8"))
        stages = data.get("stages", [])
        if stages:
            total_ms = sum(s.get("ms", 0) for s in stages)
            return [
                (s.get("name", "stage"), s.get("ms", 0), round(100 * s.get("ms", 0) / total_ms, 1))
                for s in stages
            ]
    return FALLBACK_STAGES


def format_value(ms: float, pct: float) -> str:
    if pct >= 99.95:
        return f"{ms:,.1f} ms (100.0%)"
    return f"{ms:,.1f} ms ({pct:.1f}%)"


def build_svg(stages):
    total_ms = sum(ms for _, ms, _ in stages)
    max_ms = max(ms for _, ms, _ in stages) if stages else 1

    rows = []
    y = BAR_Y_START
    for name, ms, pct in stages:
        color = ACCENT_MAJOR if pct >= 50 else ACCENT_MINOR
        # Пропорциональная ширина внутри укороченной шкалы
        bar_w = SCALE_WIDTH * (ms / max_ms) if max_ms else 0

        # Фоновая дорожка на всю шкалу
        rows.append(f'<rect x="{MARGIN_LEFT}" y="{y}" width="{SCALE_WIDTH}" height="{BAR_HEIGHT}" fill="{TRACK_BG}" rx="3"/>')
        # Цветная полоска
        rows.append(f'<rect x="{MARGIN_LEFT}" y="{y}" width="{bar_w:.2f}" height="{BAR_HEIGHT}" fill="{color}" rx="3" opacity="0.9"/>')
        # Название этапа слева
        rows.append(f'<text x="10" y="{y + BAR_HEIGHT/2 + 4:.1f}" fill="{TEXT_MAIN}" font-size="13" font-family="Inter, sans-serif" text-anchor="start">{name}</text>')
        # Значение справа от шкалы
        rows.append(f'<text x="{LABEL_X}" y="{y + BAR_HEIGHT/2 + 4:.1f}" fill="{TEXT_MAIN}" font-size="12" font-family="Inter, sans-serif" text-anchor="start">{format_value(ms, pct)}</text>')
        y += BAR_HEIGHT + BAR_GAP

    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {HEIGHT}" width="{WIDTH}" height="{HEIGHT}" role="img" aria-label="Latency stage breakdown">\n'
        f'<rect width="{WIDTH}" height="{HEIGHT}" fill="{BG}" rx="8"/>\n'
        f'<text x="24" y="34" fill="{TEXT_MAIN}" font-size="17" font-family="Inter, sans-serif" text-anchor="start" font-weight="600">Latency stage breakdown</text>\n'
        f'<text x="24" y="56" fill="{TEXT_MUTED}" font-size="12" font-family="Inter, sans-serif" text-anchor="start">Generation dominates response time (>99%)</text>\n'
        + "\n".join(rows)
        + "\n</svg>\n"
    )
    return svg


def main():
    stages = load_data()
    svg = build_svg(stages)

    OUT_SVG.parent.mkdir(parents=True, exist_ok=True)
    OUT_SVG.write_text(svg, encoding="utf-8")
    LANDING_SVG.parent.mkdir(parents=True, exist_ok=True)
    LANDING_SVG.write_text(svg, encoding="utf-8")

    print(f"G-012 written: {OUT_SVG}")
    print(f"G-012 landing: {LANDING_SVG}")


if __name__ == "__main__":
    main()
