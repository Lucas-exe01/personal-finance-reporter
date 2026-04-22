"""
analytics.py
------------
Computes financial summaries and statistics from the cleaned DataFrame.

Responsible for:
- Monthly income / expense / balance breakdowns
- Category-level expense aggregation
- Savings rate calculation
- Top spending categories
"""

import pandas as pd


def monthly_summary(df: pd.DataFrame) -> pd.DataFrame:
    """
    Build a month-by-month summary of income, expenses and balance.

    Parameters
    ----------
    df : pd.DataFrame
        Validated financial DataFrame with 'date', 'amount', 'type' columns.

    Returns
    -------
    pd.DataFrame
        Columns: month (Period), income, expenses, balance, savings_rate_pct
    """
    df = df.copy()
    df["month"] = df["date"].dt.to_period("M")

    income = (
        df[df["type"] == "income"]
        .groupby("month")["amount"]
        .sum()
        .rename("income")
    )
    expenses = (
        df[df["type"] == "expense"]
        .groupby("month")["amount"]
        .sum()
        .rename("expenses")
    )

    summary = pd.concat([income, expenses], axis=1).fillna(0)
    summary["balance"] = summary["income"] - summary["expenses"]
    summary["savings_rate_pct"] = (
        (summary["balance"] / summary["income"].replace(0, pd.NA)) * 100
    ).round(1)
    summary = summary.reset_index()
    summary["month_str"] = summary["month"].astype(str)

    return summary


def category_breakdown(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate total expenses by category, sorted descending.

    Parameters
    ----------
    df : pd.DataFrame
        Validated financial DataFrame.

    Returns
    -------
    pd.DataFrame
        Columns: category, total, percentage
    """
    expenses = df[df["type"] == "expense"]
    breakdown = (
        expenses.groupby("category")["amount"]
        .sum()
        .reset_index()
        .rename(columns={"amount": "total"})
        .sort_values("total", ascending=False)
        .reset_index(drop=True)
    )
    grand_total = breakdown["total"].sum()
    breakdown["percentage"] = ((breakdown["total"] / grand_total) * 100).round(1)
    return breakdown


def overall_stats(df: pd.DataFrame) -> dict:
    """
    Compute top-level statistics for the full reporting period.

    Parameters
    ----------
    df : pd.DataFrame
        Validated financial DataFrame.

    Returns
    -------
    dict
        Keys: total_income, total_expenses, net_balance,
              savings_rate_pct, num_months, num_transactions,
              avg_monthly_expense, top_category
    """
    income_df = df[df["type"] == "income"]
    expense_df = df[df["type"] == "expense"]

    total_income = income_df["amount"].sum()
    total_expenses = expense_df["amount"].sum()
    net_balance = total_income - total_expenses
    num_months = df["date"].dt.to_period("M").nunique()
    savings_rate = (net_balance / total_income * 100) if total_income > 0 else 0.0

    cat = category_breakdown(df)
    top_category = cat.iloc[0]["category"] if not cat.empty else "N/A"

    return {
        "total_income": round(total_income, 2),
        "total_expenses": round(total_expenses, 2),
        "net_balance": round(net_balance, 2),
        "savings_rate_pct": round(savings_rate, 1),
        "num_months": num_months,
        "num_transactions": len(df),
        "avg_monthly_expense": round(total_expenses / num_months, 2) if num_months else 0,
        "top_category": top_category,
    }
