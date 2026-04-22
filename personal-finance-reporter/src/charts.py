"""
charts.py
---------
Generates matplotlib chart images that are embedded in the PDF report.

Responsible for:
- Monthly income vs expenses bar chart
- Category expense pie chart
- Monthly balance line chart

All charts are saved to a temporary directory and returned as file paths.
"""

import matplotlib
matplotlib.use("Agg")  # Non-interactive backend for file output

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import pandas as pd
from pathlib import Path


# ── Colour palette ────────────────────────────────────────────────────────────
PALETTE = {
    "income": "#2ECC71",
    "expense": "#E74C3C",
    "balance_pos": "#3498DB",
    "balance_neg": "#E67E22",
    "bg": "#FAFAFA",
    "grid": "#E0E0E0",
    "text": "#2C3E50",
}

CATEGORY_COLORS = [
    "#3498DB", "#E74C3C", "#2ECC71", "#F39C12",
    "#9B59B6", "#1ABC9C", "#E67E22", "#34495E",
    "#E91E63", "#00BCD4",
]


def _apply_base_style(ax: plt.Axes, title: str) -> None:
    """Apply consistent styling to an Axes object."""
    ax.set_facecolor(PALETTE["bg"])
    ax.set_title(title, fontsize=13, fontweight="bold", color=PALETTE["text"], pad=12)
    ax.tick_params(colors=PALETTE["text"], labelsize=9)
    ax.spines[["top", "right"]].set_visible(False)
    ax.spines[["left", "bottom"]].set_color(PALETTE["grid"])
    ax.yaxis.grid(True, color=PALETTE["grid"], linewidth=0.8, linestyle="--")
    ax.set_axisbelow(True)


def chart_income_vs_expenses(summary: pd.DataFrame, output_dir: Path) -> Path:
    """
    Bar chart comparing monthly income and expenses.

    Parameters
    ----------
    summary : pd.DataFrame
        Output of analytics.monthly_summary().
    output_dir : Path
        Directory where the PNG will be saved.

    Returns
    -------
    Path
        Path to the saved PNG file.
    """
    fig, ax = plt.subplots(figsize=(8, 4))
    fig.patch.set_facecolor(PALETTE["bg"])

    x = range(len(summary))
    width = 0.38

    bars_income = ax.bar(
        [i - width / 2 for i in x],
        summary["income"],
        width=width,
        color=PALETTE["income"],
        label="Income",
        zorder=3,
    )
    bars_expense = ax.bar(
        [i + width / 2 for i in x],
        summary["expenses"],
        width=width,
        color=PALETTE["expense"],
        label="Expenses",
        zorder=3,
    )

    ax.set_xticks(list(x))
    ax.set_xticklabels(summary["month_str"], rotation=30, ha="right")
    ax.yaxis.set_major_formatter(mticker.FormatStrFormatter("€%.0f"))
    ax.legend(framealpha=0.6, fontsize=9)
    _apply_base_style(ax, "Monthly Income vs Expenses")

    fig.tight_layout()
    out = output_dir / "chart_income_expenses.png"
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return out


def chart_category_pie(category_df: pd.DataFrame, output_dir: Path) -> Path:
    """
    Pie chart of expense breakdown by category.

    Parameters
    ----------
    category_df : pd.DataFrame
        Output of analytics.category_breakdown().
    output_dir : Path
        Directory where the PNG will be saved.

    Returns
    -------
    Path
        Path to the saved PNG file.
    """
    fig, ax = plt.subplots(figsize=(7, 5))
    fig.patch.set_facecolor(PALETTE["bg"])

    colors = CATEGORY_COLORS[: len(category_df)]
    wedges, texts, autotexts = ax.pie(
        category_df["total"],
        labels=category_df["category"],
        autopct="%1.1f%%",
        startangle=140,
        colors=colors,
        pctdistance=0.82,
        wedgeprops={"linewidth": 1.5, "edgecolor": "white"},
    )
    for t in texts:
        t.set_fontsize(9)
        t.set_color(PALETTE["text"])
    for at in autotexts:
        at.set_fontsize(8)
        at.set_color("white")
        at.set_fontweight("bold")

    ax.set_title("Expense Breakdown by Category", fontsize=13, fontweight="bold",
                 color=PALETTE["text"], pad=14)
    fig.tight_layout()
    out = output_dir / "chart_category_pie.png"
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return out


def chart_monthly_balance(summary: pd.DataFrame, output_dir: Path) -> Path:
    """
    Line chart of monthly net balance.

    Parameters
    ----------
    summary : pd.DataFrame
        Output of analytics.monthly_summary().
    output_dir : Path
        Directory where the PNG will be saved.

    Returns
    -------
    Path
        Path to the saved PNG file.
    """
    fig, ax = plt.subplots(figsize=(8, 3.5))
    fig.patch.set_facecolor(PALETTE["bg"])

    x = range(len(summary))
    balances = summary["balance"]

    colors = [
        PALETTE["balance_pos"] if b >= 0 else PALETTE["balance_neg"] for b in balances
    ]
    ax.bar(list(x), balances, color=colors, zorder=3, width=0.55)
    ax.axhline(0, color=PALETTE["text"], linewidth=0.8, linestyle="--")
    ax.set_xticks(list(x))
    ax.set_xticklabels(summary["month_str"], rotation=30, ha="right")
    ax.yaxis.set_major_formatter(mticker.FormatStrFormatter("€%.0f"))
    _apply_base_style(ax, "Monthly Net Balance")

    fig.tight_layout()
    out = output_dir / "chart_balance.png"
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return out
