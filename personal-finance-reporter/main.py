"""
main.py
-------
Entry point for Personal Finance Reporter.

Usage
-----
    python main.py                                  # uses default sample data
    python main.py --input data/my_expenses.csv
    python main.py --input data/my_expenses.csv --output reports/my_report.pdf

Run `python main.py --help` for full options.
"""

import argparse
import sys
import tempfile
from pathlib import Path

from src.parser import load_csv
from src.analytics import monthly_summary, category_breakdown, overall_stats
from src.charts import chart_income_vs_expenses, chart_category_pie, chart_monthly_balance
from src.report import generate_pdf


DEFAULT_INPUT = Path("data/expenses_sample.csv")
DEFAULT_OUTPUT = Path("reports/finance_report.pdf")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="personal-finance-reporter",
        description=(
            "Generate a professional PDF financial report from a CSV file.\n\n"
            "CSV format required:\n"
            "  date, category, description, amount, type\n"
            "  type must be 'income' or 'expense'"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--input", "-i",
        type=Path,
        default=DEFAULT_INPUT,
        help=f"Path to the input CSV file (default: {DEFAULT_INPUT})",
    )
    parser.add_argument(
        "--output", "-o",
        type=Path,
        default=DEFAULT_OUTPUT,
        help=f"Path for the output PDF file (default: {DEFAULT_OUTPUT})",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    print("\n📊 Personal Finance Reporter")
    print("─" * 40)

    # ── Load and validate CSV ─────────────────────────────────────────────────
    print(f"  → Loading data from: {args.input}")
    try:
        df = load_csv(args.input)
    except FileNotFoundError as e:
        print(f"\n  ✗ Error: {e}")
        print("  Tip: run with --input path/to/your/file.csv")
        sys.exit(1)
    except ValueError as e:
        print(f"\n  ✗ Data error: {e}")
        sys.exit(1)

    print(f"  ✓ Loaded {len(df)} transactions spanning {df['date'].dt.to_period('M').nunique()} month(s)")

    # ── Compute analytics ─────────────────────────────────────────────────────
    print("  → Computing analytics ...")
    summary = monthly_summary(df)
    cat_df = category_breakdown(df)
    stats = overall_stats(df)

    print(f"  ✓ Total income:   €{stats['total_income']:,.2f}")
    print(f"  ✓ Total expenses: €{stats['total_expenses']:,.2f}")
    print(f"  ✓ Net balance:    €{stats['net_balance']:,.2f}")
    print(f"  ✓ Savings rate:   {stats['savings_rate_pct']}%")

    # ── Generate charts into a temp directory ─────────────────────────────────
    print("  → Generating charts ...")
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)

        chart_paths = {
            "income_expenses": chart_income_vs_expenses(summary, tmp),
            "category_pie": chart_category_pie(cat_df, tmp),
            "balance": chart_monthly_balance(summary, tmp),
        }
        print("  ✓ Charts created")

        # ── Build PDF ─────────────────────────────────────────────────────────
        args.output.parent.mkdir(parents=True, exist_ok=True)
        print(f"  → Building PDF report: {args.output}")
        generate_pdf(stats, summary, cat_df, chart_paths, args.output)

    print(f"\n  ✅ Report saved to: {args.output.resolve()}")
    print("─" * 40 + "\n")


if __name__ == "__main__":
    main()
