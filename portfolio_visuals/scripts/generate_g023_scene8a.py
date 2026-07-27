#!/usr/bin/env python3
"""
Генерация G-023 — Dataset Evolution для сцены 8a (Hard negatives).

Отличие от G-013: показывает только Exp 001, Exp 002, Exp 003.
Exp 004 ещё не произошёл в момент повествования сцены 8a.
"""

from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

matplotlib.use("Agg")

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "portfolio_visuals" / "data"
SVG_DIR = ROOT / "finetuning" / "landing" / "assets" / "visuals"
PNG_DIR = ROOT / "portfolio_visuals" / "png"

DARK_BG = "#0d1117"
CARD_BG = "#161b22"
TEXT_MAIN = "#f0f6fc"
TEXT_MUTED = "#8b949e"
ACCENT_GREEN = "#238636"
ACCENT_RED = "#da3633"
ACCENT_BLUE = "#58a6ff"
ACCENT_ORANGE = "#d29922"
GRID_COLOR = "#30363d"


def load_dataset_df() -> pd.DataFrame:
    csv_path = DATA_DIR / "G-013-dataset-evolution.csv"
    if not csv_path.exists():
        raise FileNotFoundError(f"Отсутствует CSV: {csv_path}")
    df = pd.read_csv(csv_path)
    return df[df["experiment"].isin(["Exp 001", "Exp 002", "Exp 003"])].copy()


def add_footer(ax: plt.Axes, text: str, y_pos: float = -0.18) -> None:
    ax.text(
        0.5,
        y_pos,
        text,
        transform=ax.transAxes,
        ha="center",
        va="top",
        fontsize=8,
        color=TEXT_MUTED,
        wrap=True,
    )


def plot_g023(dataset_df: pd.DataFrame) -> tuple[Path, Path]:
    fig, ax1 = plt.subplots(figsize=(11, 7))
    fig.patch.set_facecolor(DARK_BG)
    ax1.set_facecolor(DARK_BG)
    ax1.spines["top"].set_visible(False)
    ax1.spines["right"].set_color(GRID_COLOR)
    ax1.spines["left"].set_color(GRID_COLOR)
    ax1.spines["bottom"].set_color(GRID_COLOR)
    ax1.tick_params(axis="both", colors=TEXT_MUTED, labelsize=10)

    experiments = ["Exp 001", "Exp 002", "Exp 003"]
    x = np.arange(len(experiments))

    bottom = np.zeros(len(experiments))
    category_colors = {
        "obvious_match": "#3fb950",
        "borderline": "#d29922",
        "obvious_no_match": "#f85149",
    }
    category_labels = {
        "obvious_match": "obvious match",
        "borderline": "borderline",
        "obvious_no_match": "obvious no match",
    }

    for cat in ("obvious_match", "borderline", "obvious_no_match"):
        vals = dataset_df.set_index("experiment").loc[experiments, cat].values
        ax1.bar(
            x, vals, bottom=bottom,
            label=category_labels[cat],
            color=category_colors[cat],
            edgecolor=DARK_BG,
            linewidth=1,
        )
        bottom += vals

    ax1.set_xticks(x)
    ax1.set_xticklabels(experiments)
    ax1.set_ylabel("Записей", color=TEXT_MUTED, fontsize=11)
    ax1.set_ylim(0, 140)
    ax1.set_title(
        "Рост качества шёл за счёт инженерии датасета, а не адаптера",
        color=TEXT_MAIN,
        fontsize=13,
        fontweight="bold",
        pad=15,
    )

    # Линия числа кандидатов
    ax2 = ax1.twinx()
    ax2.set_facecolor(DARK_BG)
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_color(ACCENT_BLUE)
    ax2.tick_params(axis="y", colors=ACCENT_BLUE, labelsize=10)
    ax2.set_ylabel("Кандидатов", color=ACCENT_BLUE, fontsize=11)
    candidates = dataset_df.set_index("experiment").loc[experiments, "candidates"].values
    ax2.plot(
        x, candidates,
        color=ACCENT_BLUE,
        linewidth=2.5,
        marker="o",
        markersize=8,
        label="кандидаты",
    )
    ax2.set_ylim(0, 55)

    for i, c in enumerate(candidates):
        ax2.text(i, c + 2, str(c), ha="center", va="bottom", fontsize=9, color=ACCENT_BLUE, fontweight="bold")

    # Аннотации роста
    for i, total in enumerate(dataset_df.set_index("experiment").loc[experiments, "total_records"].values):
        ax1.text(i, total + 2, str(total), ha="center", va="bottom", fontsize=10, color=TEXT_MAIN, fontweight="bold")

    # Комбинированная легенда
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, frameon=False, labelcolor=TEXT_MUTED, loc="upper left", fontsize=9)

    add_footer(
        ax1,
        "Источники: configs/experiment_001.yaml; FINETUNING_ENGINEERING_REPORT.md (Exp 002); "
        "data/manifest_experiment_003.json. "
        "Exp 001–002: 90 записей, классы равномерны по черновому конфигу; "
        "Exp 003: +33 hard negative/edge.",
    )

    fig.tight_layout()

    SVG_DIR.mkdir(parents=True, exist_ok=True)
    PNG_DIR.mkdir(parents=True, exist_ok=True)
    svg_path = SVG_DIR / "G-023-dataset-evolution-exp001-003.svg"
    png_path = PNG_DIR / "G-023-dataset-evolution-exp001-003.png"
    fig.savefig(svg_path, format="svg", facecolor=DARK_BG, edgecolor="none", bbox_inches="tight")
    fig.savefig(png_path, format="png", facecolor=DARK_BG, edgecolor="none", bbox_inches="tight", dpi=150)
    plt.close(fig)
    return svg_path, png_path


def main() -> None:
    df = load_dataset_df()
    svg_path, png_path = plot_g023(df)
    print(f"G-023 SVG: {svg_path}")
    print(f"G-023 PNG: {png_path}")


if __name__ == "__main__":
    main()
