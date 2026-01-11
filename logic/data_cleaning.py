import pandas as pd


def clean_inventory_df(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cleans and standardizes validated retail inventory data.

    Operations performed:
    - Standardizes text columns (SKU, Store, Region, Category)
    - Ensures numeric columns are valid integers
    - Parses Date column
    - Adds basic time-based features for analysis

    Parameters:
        df (pd.DataFrame): Validated inventory DataFrame

    Returns:
        pd.DataFrame: Cleaned and feature-ready DataFrame
    """

    df = df.copy()

    # ---------------------------------------------------------
    # 1️⃣ TEXT STANDARDIZATION
    # ---------------------------------------------------------
    if 'SKU' in df.columns:
        df['SKU'] = df['SKU'].astype(str).str.strip().str.upper()

    if 'Store' in df.columns:
        df['Store'] = df['Store'].astype(str).str.strip().str.title()

    if 'Region' in df.columns:
        df['Region'] = df['Region'].astype(str).str.strip().str.title()

    if 'Category' in df.columns:
        df['Category'] = df['Category'].astype(str).str.strip().str.title()

    # ---------------------------------------------------------
    # 2️⃣ NUMERIC CLEANING
    # ---------------------------------------------------------
    numeric_cols = [
        'Opening_Stock',
        'Replenishment',
        'Sales',
        'Closing_Stock'
    ]

    for col in numeric_cols:
        if col in df.columns:
            df[col] = (
                pd.to_numeric(df[col], errors='coerce')
                .fillna(0)
                .astype(int)
            )

    # ---------------------------------------------------------
    # 3️⃣ DATE PARSING
    # ---------------------------------------------------------
    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'], errors='raise')

        # -----------------------------------------------------
        # 4️⃣ TIME-BASED FEATURES
        # -----------------------------------------------------
        df['Year_Month'] = df['Date'].dt.to_period('M')
        df['Week_Number'] = df['Date'].dt.isocalendar().week.astype(int)
        df['Day_Name'] = df['Date'].dt.day_name()

    return df



from logic.data_validation import validate_inventory_df
from logic.data_cleaning import clean_inventory_df
import pandas as pd


def load_inventory(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)

    validate_inventory_df(df)
    df = clean_inventory_df(df)

    return df