import pandas as pd
import numpy as np


def compute_deadstock_score(df: pd.DataFrame) -> pd.DataFrame:
    """
    Computes a deadstock score per SKU per Store based on
    inventory levels and sales velocity.

    Expects cleaned daily ERP data.
    """

    # Required columns from preprocessing
    required_columns = {
        'SKU',
        'Store',
        'Sales',
        'Closing_Stock'
    }

    if not required_columns.issubset(df.columns):
        raise ValueError(f"Missing required columns: {required_columns}")

    # ---------------------------------------------------------
    # 1️⃣ Aggregate to SKU–Store level
    # ---------------------------------------------------------
    agg = (
        df.groupby(['SKU', 'Store'], as_index=False)
        .agg(
            total_sales=('Sales', 'sum'),
            avg_daily_sales=('Sales', 'mean'),
            current_stock=('Closing_Stock', 'last')
        )
    )

    # ---------------------------------------------------------
    # 2️⃣ Compute sell-through proxy
    # ---------------------------------------------------------
    agg['sell_through_rate'] = np.where(
        agg['current_stock'] > 0,
        agg['total_sales'] / agg['current_stock'],
        0
    )

    # ---------------------------------------------------------
    # 3️⃣ Deadstock score (normalized 0–1)
    # High stock + low sales velocity = higher risk
    # ---------------------------------------------------------
    raw_score = (
        (agg['current_stock'] / agg['current_stock'].max()) * 0.6 +
        (1 - agg['sell_through_rate'].clip(0, 1)) * 0.4
    )

    agg['deadstock_score'] = (
        (raw_score - raw_score.min()) /
        (raw_score.max() - raw_score.min())
        if raw_score.max() > raw_score.min()
        else 0
    )

    return agg
