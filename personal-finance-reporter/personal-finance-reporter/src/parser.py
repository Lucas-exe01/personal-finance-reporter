"""
parser.py
---------
Handles reading and validating the CSV input file.

Responsible for:
- Loading the CSV into a pandas DataFrame
- Validating required columns
- Normalising data types (dates, amounts)
- Separating income from expense rows
"""

import pandas as pd
from pathlib import Path


REQUIRED_COLUMNS = {"date", "category", "description", "amount", "type"}
VALID_TYPES = {"income", "expense"}


def load_csv(filepath: str | Path) -> pd.DataFrame:
    """
    Load a financial CSV file and return a validated, normalised DataFrame.

    Parameters
    ----------
    filepath : str | Path
        Path to the CSV file.

    Returns
    -------
    pd.DataFrame
        Cleaned DataFrame with columns:
        date (datetime), category (str), description (str),
        amount (float), type (str).

    Raises
    ------
    FileNotFoundError
        If the file does not exist.
    ValueError
        If required columns are missing or data is invalid.
    """
    path = Path(filepath)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    if path.suffix.lower() != ".csv":
        raise ValueError(f"Expected a .csv file, got: {path.suffix}")

    df = pd.read_csv(path)

    # Validate columns
    missing = REQUIRED_COLUMNS - set(df.columns.str.strip().str.lower())
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    # Normalise column names
    df.columns = df.columns.str.strip().str.lower()

    # Normalise types
    df["date"] = pd.to_datetime(df["date"], dayfirst=False, errors="coerce")
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
    df["type"] = df["type"].str.strip().str.lower()
    df["category"] = df["category"].str.strip().str.title()
    df["description"] = df["description"].str.strip()

    # Drop rows with critical NaN values
    before = len(df)
    df = df.dropna(subset=["date", "amount", "type"])
    dropped = before - len(df)
    if dropped > 0:
        print(f"  ⚠  {dropped} row(s) skipped due to invalid date or amount.")

    # Validate type values
    invalid_types = set(df["type"].unique()) - VALID_TYPES
    if invalid_types:
        raise ValueError(
            f"Invalid values in 'type' column: {invalid_types}. "
            f"Allowed values: {VALID_TYPES}"
        )

    return df.reset_index(drop=True)


def split_by_type(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Split DataFrame into income and expense subsets.

    Parameters
    ----------
    df : pd.DataFrame
        Validated financial DataFrame.

    Returns
    -------
    tuple[pd.DataFrame, pd.DataFrame]
        (income_df, expense_df)
    """
    income_df = df[df["type"] == "income"].copy()
    expense_df = df[df["type"] == "expense"].copy()
    return income_df, expense_df
