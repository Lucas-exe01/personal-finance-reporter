"""
Tests for the Personal Finance Reporter.

Run with:  pytest tests/ -v
"""

import pytest
import pandas as pd
from pathlib import Path
import tempfile

from src.parser import load_csv, split_by_type
from src.analytics import monthly_summary, category_breakdown, overall_stats


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def sample_csv(tmp_path: Path) -> Path:
    """Write a minimal valid CSV to a temp file and return its path."""
    content = (
        "date,category,description,amount,type\n"
        "2024-01-10,Food,Supermarket,50.00,expense\n"
        "2024-01-15,Income,Salary,1500.00,income\n"
        "2024-01-20,Transport,Bus ticket,3.50,expense\n"
        "2024-02-05,Food,Restaurant,25.00,expense\n"
        "2024-02-15,Income,Salary,1500.00,income\n"
    )
    p = tmp_path / "test_data.csv"
    p.write_text(content)
    return p


@pytest.fixture
def sample_df(sample_csv: Path) -> pd.DataFrame:
    return load_csv(sample_csv)


# ── Parser tests ───────────────────────────────────────────────────────────────

class TestParser:

    def test_load_valid_csv(self, sample_csv: Path):
        df = load_csv(sample_csv)
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 5

    def test_required_columns_present(self, sample_df: pd.DataFrame):
        for col in ["date", "category", "description", "amount", "type"]:
            assert col in sample_df.columns

    def test_date_parsed_as_datetime(self, sample_df: pd.DataFrame):
        assert pd.api.types.is_datetime64_any_dtype(sample_df["date"])

    def test_amount_is_numeric(self, sample_df: pd.DataFrame):
        assert pd.api.types.is_float_dtype(sample_df["amount"])

    def test_type_values_normalised(self, sample_df: pd.DataFrame):
        assert set(sample_df["type"].unique()).issubset({"income", "expense"})

    def test_missing_file_raises(self, tmp_path: Path):
        with pytest.raises(FileNotFoundError):
            load_csv(tmp_path / "nonexistent.csv")

    def test_wrong_extension_raises(self, tmp_path: Path):
        p = tmp_path / "data.txt"
        p.write_text("hello")
        with pytest.raises(ValueError, match="Expected a .csv file"):
            load_csv(p)

    def test_missing_column_raises(self, tmp_path: Path):
        p = tmp_path / "bad.csv"
        p.write_text("date,amount\n2024-01-01,10.00\n")
        with pytest.raises(ValueError, match="Missing required columns"):
            load_csv(p)

    def test_invalid_type_raises(self, tmp_path: Path):
        p = tmp_path / "bad_type.csv"
        p.write_text(
            "date,category,description,amount,type\n"
            "2024-01-01,Food,Test,10.00,shopping\n"
        )
        with pytest.raises(ValueError, match="Invalid values in 'type'"):
            load_csv(p)

    def test_split_by_type(self, sample_df: pd.DataFrame):
        income, expenses = split_by_type(sample_df)
        assert len(income) == 2
        assert len(expenses) == 3
        assert all(income["type"] == "income")
        assert all(expenses["type"] == "expense")


# ── Analytics tests ────────────────────────────────────────────────────────────

class TestAnalytics:

    def test_monthly_summary_shape(self, sample_df: pd.DataFrame):
        summary = monthly_summary(sample_df)
        assert "income" in summary.columns
        assert "expenses" in summary.columns
        assert "balance" in summary.columns
        assert len(summary) == 2  # January and February

    def test_monthly_balance_calculation(self, sample_df: pd.DataFrame):
        summary = monthly_summary(sample_df)
        jan = summary[summary["month_str"] == "2024-01"].iloc[0]
        assert jan["income"] == pytest.approx(1500.00)
        assert jan["expenses"] == pytest.approx(53.50)
        assert jan["balance"] == pytest.approx(1446.50)

    def test_category_breakdown_sorted(self, sample_df: pd.DataFrame):
        breakdown = category_breakdown(sample_df)
        totals = breakdown["total"].tolist()
        assert totals == sorted(totals, reverse=True)

    def test_category_percentages_sum_to_100(self, sample_df: pd.DataFrame):
        breakdown = category_breakdown(sample_df)
        assert breakdown["percentage"].sum() == pytest.approx(100.0, abs=0.2)

    def test_overall_stats_keys(self, sample_df: pd.DataFrame):
        stats = overall_stats(sample_df)
        expected_keys = {
            "total_income", "total_expenses", "net_balance",
            "savings_rate_pct", "num_months", "num_transactions",
            "avg_monthly_expense", "top_category",
        }
        assert expected_keys.issubset(stats.keys())

    def test_overall_stats_values(self, sample_df: pd.DataFrame):
        stats = overall_stats(sample_df)
        assert stats["total_income"] == pytest.approx(3000.00)
        assert stats["total_expenses"] == pytest.approx(78.50)
        assert stats["num_months"] == 2
        assert stats["num_transactions"] == 5
