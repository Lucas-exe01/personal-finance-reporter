"""
report.py
---------
Assembles the final PDF report using ReportLab.

Responsible for:
- Cover page with overall stats
- Monthly summary table
- Embedded charts
- Category breakdown table
- Professional layout and typography
"""

from pathlib import Path
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image,
    HRFlowable,
    PageBreak,
)

import pandas as pd


# ── Colour constants ──────────────────────────────────────────────────────────
PRIMARY = colors.HexColor("#2C3E50")
ACCENT = colors.HexColor("#3498DB")
GREEN = colors.HexColor("#2ECC71")
RED = colors.HexColor("#E74C3C")
LIGHT_GRAY = colors.HexColor("#F4F6F8")
MID_GRAY = colors.HexColor("#BDC3C7")
WHITE = colors.white


def _build_styles() -> dict:
    """Return a dict of custom ParagraphStyles."""
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "ReportTitle",
            fontSize=26,
            textColor=WHITE,
            alignment=TA_CENTER,
            fontName="Helvetica-Bold",
            spaceAfter=6,
        ),
        "subtitle": ParagraphStyle(
            "ReportSubtitle",
            fontSize=11,
            textColor=colors.HexColor("#BDC3C7"),
            alignment=TA_CENTER,
            fontName="Helvetica",
        ),
        "section": ParagraphStyle(
            "SectionHeading",
            fontSize=13,
            textColor=PRIMARY,
            fontName="Helvetica-Bold",
            spaceBefore=14,
            spaceAfter=6,
        ),
        "body": ParagraphStyle(
            "Body",
            fontSize=9,
            textColor=PRIMARY,
            fontName="Helvetica",
            leading=14,
        ),
        "stat_label": ParagraphStyle(
            "StatLabel",
            fontSize=8,
            textColor=colors.HexColor("#7F8C8D"),
            fontName="Helvetica",
            alignment=TA_CENTER,
        ),
        "stat_value": ParagraphStyle(
            "StatValue",
            fontSize=16,
            textColor=PRIMARY,
            fontName="Helvetica-Bold",
            alignment=TA_CENTER,
        ),
    }


def _stat_card(label: str, value: str, styles: dict) -> Table:
    """Render a small stat card as a single-cell Table."""
    cell = [
        Paragraph(value, styles["stat_value"]),
        Spacer(1, 2),
        Paragraph(label, styles["stat_label"]),
    ]
    t = Table([[cell]], colWidths=[4 * cm])
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), LIGHT_GRAY),
                ("ROUNDEDCORNERS", [6]),
                ("BOX", (0, 0), (-1, -1), 0.5, MID_GRAY),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 10),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
            ]
        )
    )
    return t


def generate_pdf(
    stats: dict,
    monthly_summary: pd.DataFrame,
    category_df: pd.DataFrame,
    chart_paths: dict[str, Path],
    output_path: Path,
) -> Path:
    """
    Build and save the complete PDF financial report.

    Parameters
    ----------
    stats : dict
        Overall statistics from analytics.overall_stats().
    monthly_summary : pd.DataFrame
        Month-by-month data from analytics.monthly_summary().
    category_df : pd.DataFrame
        Category breakdown from analytics.category_breakdown().
    chart_paths : dict[str, Path]
        Paths to the generated chart PNGs.
    output_path : Path
        Destination path for the PDF file.

    Returns
    -------
    Path
        Path to the written PDF.
    """
    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        topMargin=1.5 * cm,
        bottomMargin=2 * cm,
        title="Personal Finance Report",
        author="Personal Finance Reporter",
    )

    styles = _build_styles()
    W = A4[0] - 4 * cm  # usable width
    story = []

    # ── Cover banner ─────────────────────────────────────────────────────────
    banner = Table(
        [
            [Paragraph("Personal Finance Report", styles["title"])],
            [Paragraph(f"Generated on {datetime.today().strftime('%B %d, %Y')}", styles["subtitle"])],
        ],
        colWidths=[W],
    )
    banner.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), PRIMARY),
                ("ROUNDEDCORNERS", [8]),
                ("TOPPADDING", (0, 0), (-1, -1), 22),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 22),
            ]
        )
    )
    story.append(banner)
    story.append(Spacer(1, 0.5 * cm))

    # ── Stat cards row ────────────────────────────────────────────────────────
    cards = Table(
        [[
            _stat_card("Total Income", f"€{stats['total_income']:,.2f}", styles),
            _stat_card("Total Expenses", f"€{stats['total_expenses']:,.2f}", styles),
            _stat_card("Net Balance", f"€{stats['net_balance']:,.2f}", styles),
            _stat_card("Savings Rate", f"{stats['savings_rate_pct']}%", styles),
        ]],
        colWidths=[W / 4] * 4,
        hAlign="CENTER",
    )
    cards.setStyle(TableStyle([("ALIGN", (0, 0), (-1, -1), "CENTER")]))
    story.append(cards)
    story.append(Spacer(1, 0.3 * cm))

    extra_info = Table(
        [[
            _stat_card("Months Analysed", str(stats["num_months"]), styles),
            _stat_card("Transactions", str(stats["num_transactions"]), styles),
            _stat_card("Avg Monthly Expense", f"€{stats['avg_monthly_expense']:,.2f}", styles),
            _stat_card("Top Category", stats["top_category"], styles),
        ]],
        colWidths=[W / 4] * 4,
        hAlign="CENTER",
    )
    extra_info.setStyle(TableStyle([("ALIGN", (0, 0), (-1, -1), "CENTER")]))
    story.append(extra_info)
    story.append(Spacer(1, 0.4 * cm))
    story.append(HRFlowable(width=W, color=MID_GRAY, thickness=0.5))

    # ── Income vs Expenses chart ──────────────────────────────────────────────
    story.append(Paragraph("Monthly Overview", styles["section"]))
    if "income_expenses" in chart_paths:
        story.append(Image(str(chart_paths["income_expenses"]), width=W, height=W * 0.45))

    # ── Balance chart ─────────────────────────────────────────────────────────
    story.append(Spacer(1, 0.3 * cm))
    if "balance" in chart_paths:
        story.append(Image(str(chart_paths["balance"]), width=W, height=W * 0.38))

    story.append(PageBreak())

    # ── Monthly summary table ─────────────────────────────────────────────────
    story.append(Paragraph("Monthly Summary", styles["section"]))

    headers = ["Month", "Income (€)", "Expenses (€)", "Balance (€)", "Savings Rate"]
    table_data = [headers]
    for _, row in monthly_summary.iterrows():
        bal = row["balance"]
        bal_str = f"€{bal:,.2f}"
        table_data.append([
            row["month_str"],
            f"€{row['income']:,.2f}",
            f"€{row['expenses']:,.2f}",
            bal_str,
            f"{row['savings_rate_pct']}%",
        ])

    col_w = [W * p for p in [0.22, 0.20, 0.20, 0.20, 0.18]]
    tbl = Table(table_data, colWidths=col_w, repeatRows=1)

    row_styles = [
        ("BACKGROUND", (0, 0), (-1, 0), PRIMARY),
        ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
        ("ALIGN", (0, 0), (0, -1), "LEFT"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, LIGHT_GRAY]),
        ("GRID", (0, 0), (-1, -1), 0.3, MID_GRAY),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
    ]
    # Colour negative balance cells red
    for i, (_, row) in enumerate(monthly_summary.iterrows(), start=1):
        if row["balance"] < 0:
            row_styles.append(("TEXTCOLOR", (3, i), (3, i), RED))

    tbl.setStyle(TableStyle(row_styles))
    story.append(tbl)
    story.append(Spacer(1, 0.4 * cm))
    story.append(HRFlowable(width=W, color=MID_GRAY, thickness=0.5))

    # ── Category breakdown ────────────────────────────────────────────────────
    story.append(Paragraph("Expense Breakdown by Category", styles["section"]))

    if "category_pie" in chart_paths:
        story.append(Image(str(chart_paths["category_pie"]), width=W * 0.65, height=W * 0.55,
                           hAlign="CENTER"))

    cat_headers = ["Category", "Total (€)", "Share (%)"]
    cat_data = [cat_headers]
    for _, row in category_df.iterrows():
        cat_data.append([
            row["category"],
            f"€{row['total']:,.2f}",
            f"{row['percentage']}%",
        ])

    cat_col_w = [W * p for p in [0.50, 0.25, 0.25]]
    cat_tbl = Table(cat_data, colWidths=cat_col_w, repeatRows=1)
    cat_tbl.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), ACCENT),
            ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, LIGHT_GRAY]),
            ("GRID", (0, 0), (-1, -1), 0.3, MID_GRAY),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ])
    )
    story.append(cat_tbl)

    # ── Footer note ───────────────────────────────────────────────────────────
    story.append(Spacer(1, 0.6 * cm))
    story.append(HRFlowable(width=W, color=MID_GRAY, thickness=0.5))
    story.append(Spacer(1, 0.2 * cm))
    story.append(
        Paragraph(
            "Generated by Personal Finance Reporter · github.com/your-username/personal-finance-reporter",
            ParagraphStyle("footer", fontSize=7, textColor=MID_GRAY, alignment=TA_CENTER),
        )
    )

    doc.build(story)
    return output_path
