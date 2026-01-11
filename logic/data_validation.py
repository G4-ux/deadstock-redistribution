import pandas as pd


def validate_inventory_df(df: pd.DataFrame) -> None:
    """
    Validates the retail inventory DataFrame for schema, data quality,
    and logical consistency.

    Raises:
        ValueError: If critical validation checks fail.
    """

    # ---------------------------------------------------------
    # CHECK 0: Required Columns
    # ---------------------------------------------------------
    required_columns = {
        'Date',
        'Store',
        'SKU',
        'Opening_Stock',
        'Replenishment',
        'Sales',
        'Closing_Stock'
    }

    missing_cols = required_columns - set(df.columns)
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")

    # ---------------------------------------------------------
    # CHECK 1: Missing Values
    # ---------------------------------------------------------
    missing_counts = df.isnull().sum()
    if missing_counts.sum() > 0:
        raise ValueError(
            f"Missing values detected:\n{missing_counts[missing_counts > 0]}"
        )

    # ---------------------------------------------------------
    # CHECK 2: Duplicate Records
    # (Uniqueness: Date + Store + SKU)
    # ---------------------------------------------------------
    duplicate_mask = df.duplicated(subset=['Date', 'Store', 'SKU'], keep=False)
    if duplicate_mask.any():
        num_duplicates = duplicate_mask.sum()
        raise ValueError(
            f"Duplicate records detected for Date + Store + SKU. "
            f"Count: {num_duplicates}"
        )

    # ---------------------------------------------------------
    # CHECK 3: Negative Values
    # ---------------------------------------------------------
    numeric_cols = [
        'Opening_Stock',
        'Replenishment',
        'Sales',
        'Closing_Stock'
    ]

    if (df[numeric_cols] < 0).any(axis=1).any():
        raise ValueError(
            "Negative values detected in stock or sales columns."
        )

    # ---------------------------------------------------------
    # CHECK 4: Inventory Balance Logic
    # Opening + Replenishment - Sales = Closing
    # ---------------------------------------------------------
    calculated_closing = (
        df['Opening_Stock'] +
        df['Replenishment'] -
        df['Sales']
    )

    mismatches = df[calculated_closing != df['Closing_Stock']]

    # Allow mismatches but flag them
    df['inventory_mismatch'] = calculated_closing != df['Closing_Stock']


    # ---------------------------------------------------------
    # CHECK 5: Date Format Validation
    # ---------------------------------------------------------
    try:
        pd.to_datetime(df['Date'], format='%Y-%m-%d', errors='raise')
    except Exception as e:
        raise ValueError(
            f"Invalid date format detected in 'Date' column. "
            f"Expected YYYY-MM-DD. Error: {e}"
        )

    # If all checks pass, function exits silently


def load_inventory(path: str):
    df = pd.read_csv(path)

    validate_inventory_df(df)

    # cleaning / feature engineering here

    return df