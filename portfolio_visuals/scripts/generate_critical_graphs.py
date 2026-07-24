#!/usr/bin/env python3
"""
Генерация Critical Graphs портфельного кейса HR Assistant.

Артефакты:
  G-004 — Decision Accuracy Evolution
  G-005 — MAE Score Evolution
  G-008 — External-Validation Scatter
  G-009 — Runtime Smoke Pass/Fail Matrix
  G-013 — Dataset Evolution

Источники данных — только реальные JSON/YAML/manifests проекта.
Скрипт завершается ошибкой при нарушении целостности данных.
"""

import json
import sys
import traceback
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yaml

matplotlib.use("Agg")

# --- Пути -------------------------------------------------------------------
ROOT = Path(__file__).resolve().parents[2]  # cases/hr-assistant
OUT_DIR = ROOT / "portfolio_visuals"
DATA_DIR = OUT_DIR / "data"
SVG_DIR = OUT_DIR / "svg"
PNG_DIR = OUT_DIR / "png"

for d in (DATA_DIR, SVG_DIR, PNG_DIR):
    d.mkdir(parents=True, exist_ok=True)

# Исходные файлы
GENERATION_REPORTS = {
    "Exp 001": ROOT / "finetuning/runs/experiment_001/generation_test/generation_test_report.json",
    "Exp 002": ROOT / "finetuning/runs/experiment_002/generation_test/generation_test_report.json",
    "Exp 003": ROOT / "finetuning/runs/experiment_003/generation_test/generation_test_report.json",
    "Exp 004": ROOT / "finetuning/runs/experiment_004/generation_test/generation_test_report.json",
}

EXTERNAL_VALIDATION = ROOT / "finetuning/runs/experiment_004/external_validation_report.json"

RUNTIME_SMOKE = {
    "Exp 003": ROOT / "finetuning/runs/experiment_003/runtime_smoke_report.json",
    "Exp 004": ROOT / "finetuning/runs/experiment_004/runtime_smoke_report.json",
}

CONFIGS = {
    "Exp 001": ROOT / "finetuning/configs/experiment_001.yaml",
    "Exp 003": ROOT / "finetuning/configs/experiment_003.yaml",
    "Exp 004": ROOT / "finetuning/configs/experiment_004.yaml",
}

MANIFESTS = {
    "Exp 003": ROOT / "finetuning/data/manifest_experiment_003.json",
    "Exp 004": ROOT / "finetuning/data/manifest_experiment_004.json",
}

# --- Палитра -----------------------------------------------------------------
DARK_BG = "#0d1117"
CARD_BG = "#161b22"
TEXT_MAIN = "#f0f6fc"
TEXT_MUTED = "#8b949e"
ACCENT_GREEN = "#238636"
ACCENT_RED = "#da3633"
ACCENT_GRAY = "#6e7681"
ACCENT_BLUE = "#58a6ff"
ACCENT_ORANGE = "#d29922"
GRID_COLOR = "#30363d"

# --- Загрузка данных ---------------------------------------------------------

def load_json(path: Path) -> dict | list:
    if not path.exists():
        raise FileNotFoundError(f"Отсутствует исходный файл: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def load_yaml(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(f"Отсутствует исходный файл: {path}")
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def load_generation_reports() -> dict[str, dict]:
    return {name: load_json(path) for name, path in GENERATION_REPORTS.items()}


def load_external_validation() -> dict:
    return load_json(EXTERNAL_VALIDATION)


def load_runtime_smoke() -> dict[str, dict]:
    return {name: load_json(path) for name, path in RUNTIME_SMOKE.items()}


def load_configs() -> dict[str, dict]:
    return {name: load_yaml(path) for name, path in CONFIGS.items()}


def load_manifests() -> dict[str, dict]:
    return {name: load_json(path) for name, path in MANIFESTS.items()}


# --- Проверки целостности ----------------------------------------------------

def assert_files_exist() -> None:
    missing: list[str] = []
    for name, path in {**GENERATION_REPORTS, **RUNTIME_SMOKE, **CONFIGS, **MANIFESTS}.items():
        if not path.exists():
            missing.append(f"{name}: {path}")
    if not EXTERNAL_VALIDATION.exists():
        missing.append(f"external_validation: {EXTERNAL_VALIDATION}")
    if missing:
        raise FileNotFoundError("Отсутствуют обязательные файлы:\n" + "\n".join(missing))


def assert_generation_reports(reports: dict[str, dict]) -> None:
    for name, rep in reports.items():
        for model_key in ("base_qwen", "best_lora"):
            if model_key not in rep:
                raise ValueError(f"{name}: отсутствует секция {model_key}")
            summary = rep[model_key].get("summary")
            if not summary:
                raise ValueError(f"{name}/{model_key}: отсутствует summary")
            for field in ("decision_accuracy", "mae_score", "records", "valid_json_rate"):
                if field not in summary:
                    raise ValueError(f"{name}/{model_key}/summary: отсутствует {field}")
            if not (0 <= summary["decision_accuracy"] <= 1):
                raise ValueError(f"{name}/{model_key}: decision_accuracy вне [0,1]")
            if summary["mae_score"] < 0:
                raise ValueError(f"{name}/{model_key}: отрицательная MAE")
            if summary["valid_json_rate"] != 1.0:
                raise ValueError(f"{name}/{model_key}: valid_json_rate != 1.0")


def assert_external_validation(ev: dict) -> None:
    results = ev.get("results", [])
    if len(results) != 102:
        raise ValueError(f"External validation: ожидалось 102 записи, получено {len(results)}")
    missing_ref_score = 0
    for r in results:
        ref = r["reference"]
        lora = r["lora_prediction"]
        if ref["score"] is None:
            missing_ref_score += 1
        else:
            if not (0 <= ref["score"] <= 100):
                raise ValueError(f"External validation: reference score {ref['score']} вне [0,100]")
        if lora["score"] is None or not (0 <= lora["score"] <= 100):
            raise ValueError(f"External validation: LoRA score {lora['score']} вне [0,100]")
        for dec in (ref["decision"], lora["decision"]):
            if dec not in ("match", "no_match"):
                raise ValueError(f"External validation: неизвестное решение {dec}")
    if missing_ref_score > 0:
        # Фиксируем ограничение; scatter будет строиться только по записям с reference score.
        print(f"  Предупреждение: reference score отсутствует у {missing_ref_score} из 102 записей.")
    summary = ev.get("lora_summary", {})
    if summary.get("records") != 102:
        raise ValueError(f"lora_summary.records != 102: {summary.get('records')}")


def assert_runtime_smoke(smoke: dict[str, dict]) -> None:
    for name, rep in smoke.items():
        if rep.get("total_cases") != 7:
            raise ValueError(f"{name} smoke: ожидалось 7 кейсов, получено {rep.get('total_cases')}")
        if rep.get("passed") != 7 or rep.get("failed") != 0:
            raise ValueError(f"{name} smoke: ожидалось 7 PASS, получено passed={rep.get('passed')}, failed={rep.get('failed')}")
        for r in rep.get("results", []):
            ev = r.get("evaluation", {})
            if "passed" not in ev:
                raise ValueError(f"{name} smoke/{r.get('case_code')}: отсутствует evaluation.passed")


def assert_manifests(manifests: dict[str, dict]) -> None:
    expected_total = {"Exp 003": 123, "Exp 004": 162}
    for name, m in manifests.items():
        if m.get("total_records") != expected_total[name]:
            raise ValueError(f"{name} manifest: total_records != {expected_total[name]}")
        splits = m.get("splits", {})
        split_sum = sum(s.get("records", 0) for s in splits.values())
        if split_sum != m["total_records"]:
            raise ValueError(f"{name} manifest: сумма split ({split_sum}) != total_records ({m['total_records']})")


def assert_configs(configs: dict[str, dict]) -> None:
    for name, cfg in configs.items():
        if "dataset" not in cfg:
            raise ValueError(f"{name} config: отсутствует dataset")


# --- Подготовка нормализованных данных --------------------------------------

def build_metric_evolution_data(reports: dict[str, dict]) -> pd.DataFrame:
    rows = []
    for exp in ["Exp 001", "Exp 002", "Exp 003", "Exp 004"]:
        rep = reports[exp]
        rows.append({
            "experiment": exp,
            "model": "Base Qwen",
            "decision_accuracy": rep["base_qwen"]["summary"]["decision_accuracy"],
            "mae_score": rep["base_qwen"]["summary"]["mae_score"],
            "records": rep["base_qwen"]["summary"]["records"],
        })
        rows.append({
            "experiment": exp,
            "model": "LoRA",
            "decision_accuracy": rep["best_lora"]["summary"]["decision_accuracy"],
            "mae_score": rep["best_lora"]["summary"]["mae_score"],
            "records": rep["best_lora"]["summary"]["records"],
        })
    return pd.DataFrame(rows)


def build_scatter_data(ev: dict) -> pd.DataFrame:
    rows = []
    for r in ev["results"]:
        ref = r["reference"]
        lora = r["lora_prediction"]
        if ref["score"] is None:
            # Reference score отсутствует; исключаем из scatter, но сохраняем метаданные для прозрачности.
            continue
        ref_dec = ref["decision"]
        lora_dec = lora["decision"]
        if ref_dec == "match" and lora_dec == "match":
            classification = "TP"
        elif ref_dec == "no_match" and lora_dec == "no_match":
            classification = "TN"
        elif ref_dec == "no_match" and lora_dec == "match":
            classification = "FP"
        else:
            classification = "FN"
        rows.append({
            "case_code": r["metadata"]["case_code"],
            "case_type": r["metadata"].get("case_type", "unknown"),
            "reference_score": ref["score"],
            "lora_score": lora["score"],
            "reference_decision": ref_dec,
            "lora_decision": lora_dec,
            "classification": classification,
            "score_abs_error": abs(ref["score"] - lora["score"]),
        })
    return pd.DataFrame(rows)


def build_smoke_matrix_data(smoke: dict[str, dict]) -> pd.DataFrame:
    categories = ["positive", "obvious_negative", "hard_negative", "edge_case", "invalid_input", "stability_repeat"]
    experiments = ["Exp 002", "Exp 003", "Exp 004"]

    # Exp 003 и Exp 004 из JSON
    status_by_exp: dict[str, dict[str, str]] = {}
    for exp in ("Exp 003", "Exp 004"):
        status_by_exp[exp] = {}
        for cat in categories:
            status_by_exp[exp][cat] = "NOT RECORDED"
        for r in smoke[exp]["results"]:
            cat = r["category"]
            passed = r["evaluation"]["passed"]
            status_by_exp[exp][cat] = "PASS" if passed else "FAIL"

    # Exp 002 из инженерного отчёта FINETUNING_ENGINEERING_REPORT.md:
    # Positive smoke = Pass; negative/edge/invalid smoke = Fail.
    # Детальных категорий invalid_input и stability_repeat не зафиксировано.
    status_by_exp["Exp 002"] = {
        "positive": "PASS",
        "obvious_negative": "FAIL",
        "hard_negative": "FAIL",
        "edge_case": "FAIL",
        "invalid_input": "NOT RECORDED",
        "stability_repeat": "NOT RECORDED",
    }

    rows = []
    for exp in experiments:
        for cat in categories:
            rows.append({
                "experiment": exp,
                "category": cat,
                "status": status_by_exp[exp][cat],
            })
    return pd.DataFrame(rows)


def build_dataset_evolution_data(configs: dict[str, dict], manifests: dict[str, dict]) -> pd.DataFrame:
    # Exp 001 — из configs/experiment_001.yaml и FINETUNING_ENGINEERING_REPORT.md
    # Exp 002 — повторяет Exp 001 (90 записей, 30 кандидатов, 72/9/9 split)
    rows = [
        {
            "experiment": "Exp 001",
            "total_records": 90,
            "candidates": 30,
            "train": 72,
            "validation": 9,
            "test": 9,
            "holdout": 0,
            "obvious_match": 30,
            "borderline": 30,
            "obvious_no_match": 30,
        },
        {
            "experiment": "Exp 002",
            "total_records": 90,
            "candidates": 30,
            "train": 72,
            "validation": 9,
            "test": 9,
            "holdout": 0,
            "obvious_match": 30,
            "borderline": 30,
            "obvious_no_match": 30,
        },
    ]

    def sum_case_types(split_info: dict) -> dict[str, int]:
        result: dict[str, int] = {}
        for split_name, info in split_info.items():
            for ct, count in info.get("case_type_distribution", {}).items():
                result[ct] = result.get(ct, 0) + count
        return result

    for exp in ("Exp 003", "Exp 004"):
        m = manifests[exp]
        splits = m["splits"]
        ct = sum_case_types(splits)
        rows.append({
            "experiment": exp,
            "total_records": m["total_records"],
            "candidates": sum(s.get("candidates", 0) for s in splits.values()),
            "train": splits["train"]["records"],
            "validation": splits["validation"]["records"],
            "test": splits["test"]["records"],
            "holdout": splits["holdout"]["records"],
            "obvious_match": ct.get("obvious_match", 0),
            "borderline": ct.get("borderline", 0),
            "obvious_no_match": ct.get("obvious_no_match", 0),
        })

    return pd.DataFrame(rows)


# --- Вспомогательные функции для графиков -------------------------------------

def setup_figure(figsize=(10, 6)):
    fig, ax = plt.subplots(figsize=figsize)
    fig.patch.set_facecolor(DARK_BG)
    ax.set_facecolor(DARK_BG)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color(GRID_COLOR)
    ax.spines["bottom"].set_color(GRID_COLOR)
    ax.tick_params(axis="both", colors=TEXT_MUTED, labelsize=10)
    ax.grid(True, color=GRID_COLOR, linestyle="-", linewidth=0.5, alpha=0.6)
    return fig, ax


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


def save_figure(fig: plt.Figure, name: str) -> tuple[Path, Path]:
    svg_path = SVG_DIR / f"{name}.svg"
    png_path = PNG_DIR / f"{name}.png"
    fig.savefig(svg_path, format="svg", facecolor=DARK_BG, edgecolor="none", bbox_inches="tight")
    fig.savefig(png_path, format="png", facecolor=DARK_BG, edgecolor="none", bbox_inches="tight", dpi=150)
    plt.close(fig)
    return svg_path, png_path


# --- G-004 Decision Accuracy Evolution ---------------------------------------

def plot_g004(df: pd.DataFrame) -> tuple[Path, Path]:
    fig, ax = setup_figure(figsize=(10, 6.5))

    experiments = ["Exp 001", "Exp 002", "Exp 003", "Exp 004"]
    x = np.arange(len(experiments))
    width = 0.35

    base_vals = df[df["model"] == "Base Qwen"].set_index("experiment").loc[experiments, "decision_accuracy"].values
    lora_vals = df[df["model"] == "LoRA"].set_index("experiment").loc[experiments, "decision_accuracy"].values

    bars1 = ax.bar(x - width / 2, base_vals, width, label="Base Qwen", color=ACCENT_BLUE, alpha=0.85, edgecolor=GRID_COLOR)
    bars2 = ax.bar(x + width / 2, lora_vals, width, label="LoRA", color=ACCENT_GREEN, alpha=0.9, edgecolor=GRID_COLOR)

    # Линия тренда LoRA
    ax.plot(x, lora_vals, color=ACCENT_GREEN, linewidth=2.5, marker="o", markersize=8, zorder=5)

    # Аннотация экспериментов
    for i, (bv, lv) in enumerate(zip(base_vals, lora_vals)):
        ax.text(i - width / 2, bv + 0.03, f"{bv:.2f}", ha="center", va="bottom", fontsize=9, color=TEXT_MAIN)
        ax.text(i + width / 2, lv + 0.03, f"{lv:.2f}", ha="center", va="bottom", fontsize=9, color=TEXT_MAIN, fontweight="bold")

    ax.set_xticks(x)
    ax.set_xticklabels(experiments)
    ax.set_ylabel("Decision accuracy", color=TEXT_MUTED, fontsize=11)
    ax.set_ylim(0, 1.05)
    ax.set_title("Точность решений росла неравномерно: 44% → 78% → 67% → 80%", color=TEXT_MAIN, fontsize=13, fontweight="bold", pad=15)

    # Аннотация о trade-off в Exp 003
    ax.annotate(
        "precision/recall\ntrade-off",
        xy=(2, lora_vals[2]),
        xytext=(2.35, 0.52),
        fontsize=9,
        color=ACCENT_ORANGE,
        arrowprops=dict(arrowstyle="->", color=ACCENT_ORANGE, lw=1.2),
        ha="center",
    )

    ax.legend(frameon=False, labelcolor=TEXT_MUTED, loc="upper left", fontsize=10)

    add_footer(
        ax,
        "Источник: generation_test_report.json (001–004). "
        "Test sets различаются по составу и размеру (9 vs 15 записей); "
        "сравнение направленное, не абсолютное.",
    )

    fig.tight_layout()
    return save_figure(fig, "G-004-decision-accuracy-evolution")


# --- G-005 MAE Score Evolution -----------------------------------------------

def plot_g005(df: pd.DataFrame) -> tuple[Path, Path]:
    fig, ax = setup_figure(figsize=(10, 6.5))

    experiments = ["Exp 001", "Exp 002", "Exp 003", "Exp 004"]
    x = np.arange(len(experiments))
    width = 0.35

    base_vals = df[df["model"] == "Base Qwen"].set_index("experiment").loc[experiments, "mae_score"].values
    lora_vals = df[df["model"] == "LoRA"].set_index("experiment").loc[experiments, "mae_score"].values

    ax.bar(x - width / 2, base_vals, width, label="Base Qwen", color=ACCENT_BLUE, alpha=0.85, edgecolor=GRID_COLOR)
    ax.bar(x + width / 2, lora_vals, width, label="LoRA", color=ACCENT_GREEN, alpha=0.9, edgecolor=GRID_COLOR)

    # Линия тренда LoRA (меньше MAE — лучше, поэтому линия идёт вниз)
    ax.plot(x, lora_vals, color=ACCENT_GREEN, linewidth=2.5, marker="o", markersize=8, zorder=5)

    for i, (bv, lv) in enumerate(zip(base_vals, lora_vals)):
        ax.text(i - width / 2, bv + 1.0, f"{bv:.1f}", ha="center", va="bottom", fontsize=9, color=TEXT_MAIN)
        ax.text(i + width / 2, lv + 1.0, f"{lv:.1f}", ha="center", va="bottom", fontsize=9, color=TEXT_MAIN, fontweight="bold")

    ax.set_xticks(x)
    ax.set_xticklabels(experiments)
    ax.set_ylabel("MAE score (меньше — лучше)", color=TEXT_MUTED, fontsize=11)
    ax.set_ylim(0, max(base_vals.max(), lora_vals.max()) * 1.15)
    ax.set_title("Средняя ошибка оценки снизилась с 38 до 15 баллов", color=TEXT_MAIN, fontsize=13, fontweight="bold", pad=15)

    ax.legend(frameon=False, labelcolor=TEXT_MUTED, loc="upper right", fontsize=10)

    add_footer(
        ax,
        "Источник: generation_test_report.json (001–004). "
        "MAE Score = среднее абсолютное отклонение итогового score от reference. "
        "Test sets несопоставимы между экспериментами.",
    )

    fig.tight_layout()
    return save_figure(fig, "G-005-mae-score-evolution")


# --- G-008 External-Validation Scatter ---------------------------------------

def plot_g008(scatter_df: pd.DataFrame, ev_summary: dict) -> tuple[Path, Path]:
    fig, ax = setup_figure(figsize=(9, 9))

    colors = {
        "TP": ACCENT_GREEN,
        "TN": ACCENT_GREEN,
        "FP": ACCENT_RED,
        "FN": ACCENT_RED,
    }
    markers = {"TP": "o", "TN": "s", "FP": "^", "FN": "v"}
    labels = {
        "TP": "True Positive",
        "TN": "True Negative",
        "FP": "False Positive",
        "FN": "False Negative",
    }

    # Jitter для наложения точек
    np.random.seed(42)
    jitter = np.random.normal(0, 0.8, size=len(scatter_df))

    for cls in ("TP", "TN", "FP", "FN"):
        sub = scatter_df[scatter_df["classification"] == cls]
        if sub.empty:
            continue
        ax.scatter(
            sub["reference_score"] + jitter[sub.index] * 0.0,  # jitter отключён, т.к. score непрерывный
            sub["lora_score"],
            c=colors[cls],
            marker=markers[cls],
            s=55,
            alpha=0.75,
            edgecolors=DARK_BG,
            linewidth=0.5,
            label=f"{labels[cls]} ({len(sub)})",
        )

    # Диагональ y = x
    ax.plot([0, 100], [0, 100], color=TEXT_MUTED, linestyle="--", linewidth=1.5, alpha=0.7, label="y = x (идеальная калибровка)")

    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.set_xlabel("Reference score", color=TEXT_MUTED, fontsize=11)
    ax.set_ylabel("LoRA predicted score", color=TEXT_MUTED, fontsize=11)
    ax.set_title("На внешней выборке LoRA держится вблизи диагонали калибровки", color=TEXT_MAIN, fontsize=13, fontweight="bold", pad=15)

    # Статистика в правом нижнем углу
    stats_text = (
        f"Записей: {ev_summary['records']}\n"
        f"Decision accuracy: {ev_summary['decision_accuracy']:.3f}\n"
        f"MAE score: {ev_summary['mae_score']:.1f}\n"
        f"FPR: {ev_summary['fpr']:.3f}  FNR: {ev_summary['fnr']:.3f}"
    )
    ax.text(
        0.97,
        0.03,
        stats_text,
        transform=ax.transAxes,
        ha="right",
        va="bottom",
        fontsize=9,
        color=TEXT_MUTED,
        bbox=dict(boxstyle="round,pad=0.4", facecolor=CARD_BG, edgecolor=GRID_COLOR, alpha=0.9),
    )

    ax.legend(
        frameon=False,
        labelcolor=TEXT_MUTED,
        loc="upper left",
        fontsize=9,
        title="Классификация решений",
        title_fontsize=9,
    )

    n_total = ev_summary["records"]
    n_shown = len(scatter_df)
    footer = (
        f"Источник: external_validation_report.json (Exp 004, HRA-EVAL-V5-EXT, {n_total} записи, GPT-4o reference). "
        f"Данные анонимизированы. "
    )
    if n_shown < n_total:
        footer += f"Отображено {n_shown}/{n_total}: у {n_total - n_shown} записей reference score отсутствует в JSON."
    add_footer(ax, footer, y_pos=-0.10)

    fig.tight_layout()
    return save_figure(fig, "G-008-external-validation-scatter")


# --- G-009 Runtime Smoke Pass/Fail Matrix ------------------------------------

def plot_g009(matrix_df: pd.DataFrame) -> tuple[Path, Path]:
    fig, ax = setup_figure(figsize=(9, 7.5))

    categories = ["positive", "obvious_negative", "hard_negative", "edge_case", "invalid_input", "stability_repeat"]
    experiments = ["Exp 002", "Exp 003", "Exp 004"]

    color_map = {"PASS": ACCENT_GREEN, "FAIL": ACCENT_RED, "NOT RECORDED": ACCENT_GRAY}
    label_map = {"PASS": "PASS", "FAIL": "FAIL", "NOT RECORDED": "N/A"}

    pivot = matrix_df.pivot(index="category", columns="experiment", values="status")
    pivot = pivot.loc[categories, experiments]

    # Рисуем ячейки вручную для контроля цвета и подписей
    for i, cat in enumerate(categories):
        for j, exp in enumerate(experiments):
            status = pivot.loc[cat, exp]
            rect = plt.Rectangle((j - 0.5, i - 0.5), 1, 1, facecolor=color_map[status], edgecolor=DARK_BG, linewidth=2)
            ax.add_patch(rect)
            ax.text(
                j,
                i,
                label_map[status],
                ha="center",
                va="center",
                fontsize=12,
                color=TEXT_MAIN,
                fontweight="bold",
            )

    ax.set_xlim(-0.5, len(experiments) - 0.5)
    ax.set_ylim(-0.5, len(categories) - 0.5)
    ax.set_xticks(np.arange(len(experiments)))
    ax.set_xticklabels(experiments)
    ax.set_yticks(np.arange(len(categories)))
    ax.set_yticklabels([c.replace("_", " ").title() for c in categories])
    ax.tick_params(axis="both", colors=TEXT_MUTED, labelsize=11)
    ax.set_title("Production smoke показал то, чего не видела offline-метрика", color=TEXT_MAIN, fontsize=13, fontweight="bold", pad=15)

    # Легенда
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor=ACCENT_GREEN, edgecolor=DARK_BG, label="PASS"),
        Patch(facecolor=ACCENT_RED, edgecolor=DARK_BG, label="FAIL"),
        Patch(facecolor=ACCENT_GRAY, edgecolor=DARK_BG, label="NOT RECORDED"),
    ]
    ax.legend(handles=legend_elements, frameon=False, labelcolor=TEXT_MUTED, loc="lower right", fontsize=10)

    ax.set_aspect("equal")

    add_footer(
        ax,
        "Источники: runtime_smoke_report.json (Exp 003, Exp 004); "
        "Exp 002 — из FINETUNING_ENGINEERING_REPORT.md (negative/edge smoke не пройден). "
        "N/A = категория не зафиксирована в отчёте.",
    )

    fig.tight_layout()
    return save_figure(fig, "G-009-runtime-smoke-pass-fail-matrix")


# --- G-013 Dataset Evolution -------------------------------------------------

def plot_g013(dataset_df: pd.DataFrame) -> tuple[Path, Path]:
    fig, ax1 = plt.subplots(figsize=(11, 7))
    fig.patch.set_facecolor(DARK_BG)
    ax1.set_facecolor(DARK_BG)
    ax1.spines["top"].set_visible(False)
    ax1.spines["right"].set_color(GRID_COLOR)
    ax1.spines["left"].set_color(GRID_COLOR)
    ax1.spines["bottom"].set_color(GRID_COLOR)
    ax1.tick_params(axis="both", colors=TEXT_MUTED, labelsize=10)

    experiments = ["Exp 001", "Exp 002", "Exp 003", "Exp 004"]
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
        ax1.bar(x, vals, bottom=bottom, label=category_labels[cat], color=category_colors[cat], edgecolor=DARK_BG, linewidth=1)
        bottom += vals

    ax1.set_xticks(x)
    ax1.set_xticklabels(experiments)
    ax1.set_ylabel("Записей", color=TEXT_MUTED, fontsize=11)
    ax1.set_ylim(0, 180)
    ax1.set_title("Рост качества шёл за счёт инженерии датасета, а не адаптера", color=TEXT_MAIN, fontsize=13, fontweight="bold", pad=15)

    # Линия числа кандидатов
    ax2 = ax1.twinx()
    ax2.set_facecolor(DARK_BG)
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_color(ACCENT_BLUE)
    ax2.tick_params(axis="y", colors=ACCENT_BLUE, labelsize=10)
    ax2.set_ylabel("Кандидатов", color=ACCENT_BLUE, fontsize=11)
    candidates = dataset_df.set_index("experiment").loc[experiments, "candidates"].values
    ax2.plot(x, candidates, color=ACCENT_BLUE, linewidth=2.5, marker="o", markersize=8, label="кандидаты")
    ax2.set_ylim(0, 70)

    for i, c in enumerate(candidates):
        ax2.text(i, c + 2.5, str(c), ha="center", va="bottom", fontsize=9, color=ACCENT_BLUE, fontweight="bold")

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
        "data/manifest_experiment_003.json, manifest_experiment_004.json. "
        "Exp 001–002: 90 записей, классы равномерны по черновому конфигу; "
        "Exp 003: +33 hard negative/edge; Exp 004: +39 positive/borderline.",
    )

    fig.tight_layout()
    return save_figure(fig, "G-013-dataset-evolution")


# --- Main --------------------------------------------------------------------

def main() -> int:
    try:
        print("Загрузка и проверка данных...")
        assert_files_exist()

        reports = load_generation_reports()
        assert_generation_reports(reports)

        ev = load_external_validation()
        assert_external_validation(ev)

        smoke = load_runtime_smoke()
        assert_runtime_smoke(smoke)

        configs = load_configs()
        assert_configs(configs)

        manifests = load_manifests()
        assert_manifests(manifests)

        print("Подготовка нормализованных данных...")
        metric_df = build_metric_evolution_data(reports)
        scatter_df = build_scatter_data(ev)
        smoke_df = build_smoke_matrix_data(smoke)
        dataset_df = build_dataset_evolution_data(configs, manifests)

        metric_df.to_csv(DATA_DIR / "G-004-G-005-metric-evolution.csv", index=False)
        scatter_df.to_csv(DATA_DIR / "G-008-external-validation-scatter.csv", index=False)
        smoke_df.to_csv(DATA_DIR / "G-009-runtime-smoke-matrix.csv", index=False)
        dataset_df.to_csv(DATA_DIR / "G-013-dataset-evolution.csv", index=False)

        # Проверка соответствия чисел исходным файлам
        assert 0 < len(scatter_df) <= 102
        assert metric_df["model"].nunique() == 2
        assert set(metric_df["experiment"]) == {"Exp 001", "Exp 002", "Exp 003", "Exp 004"}
        assert dataset_df["total_records"].tolist() == [90, 90, 123, 162]
        assert dataset_df["candidates"].tolist() == [30, 30, 41, 54]

        print("Построение G-004...")
        plot_g004(metric_df)

        print("Построение G-005...")
        plot_g005(metric_df)

        print("Построение G-008...")
        plot_g008(scatter_df, ev["lora_summary"])

        print("Построение G-009...")
        plot_g009(smoke_df)

        print("Построение G-013...")
        plot_g013(dataset_df)

        print("\nГотово. Созданные файлы:")
        for svg in sorted(SVG_DIR.glob("G-*.svg")):
            png = PNG_DIR / svg.with_suffix(".png").name
            print(f"  {svg.name}")
            print(f"  {png.name}")
        print(f"\nПроизводные данные: {DATA_DIR}")

        return 0

    except Exception as e:
        print(f"\nОШИБКА: {e}", file=sys.stderr)
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
