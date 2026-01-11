import pandas as pd
import numpy as np


def get_redistribution_recommendations(df: pd.DataFrame) -> pd.DataFrame:
    """
    Generates redistribution recommendations by matching
    high-deadstock stores with higher-demand stores for the same SKU.

    Parameters:
        df (pd.DataFrame): Output of compute_deadstock_score()

    Returns:
        pd.DataFrame: Ranked redistribution recommendations with:
            - SKU
            - store_from
            - store_to
            - transfer_score
    """

    # ---------------------------------------------------------
    # 0️⃣ Required column check
    # ---------------------------------------------------------
    required_columns = {
        'SKU',
        'Store',
        'current_stock',
        'avg_daily_sales',
        'deadstock_score'
    }

    if not required_columns.issubset(df.columns):
        raise ValueError(
            f"Input DataFrame must contain columns: {required_columns}"
        )

    if df.empty:
        return pd.DataFrame(
            columns=['SKU', 'store_from', 'store_to', 'transfer_score']
        )

    # ---------------------------------------------------------
    # 1️⃣ Identify source stores (high deadstock risk)
    # ---------------------------------------------------------
    source = df[
        (df['deadstock_score'] >= 0.6) &
        (df['current_stock'] > 0)
    ].rename(columns={'Store': 'store_from'})

    # ---------------------------------------------------------
    # 2️⃣ Identify destination stores (higher sales velocity)
    # ---------------------------------------------------------
    dest = df[
        df['avg_daily_sales'] > 0
    ].rename(columns={'Store': 'store_to'})

    if source.empty or dest.empty:
        return pd.DataFrame(
            columns=['SKU', 'store_from', 'store_to', 'transfer_score']
        )

    # ---------------------------------------------------------
    # 3️⃣ Match source → destination by SKU
    # ---------------------------------------------------------
    recs = pd.merge(
        source,
        dest,
        on='SKU',
        suffixes=('_source', '_dest')
    )

    # Exclude same-store transfers
    recs = recs[
        recs['store_from'] != recs['store_to']
    ]

    if recs.empty:
        return pd.DataFrame(
            columns=['SKU', 'store_from', 'store_to', 'transfer_score']
        )

    # ---------------------------------------------------------
    # 4️⃣ Normalize components for scoring
    # ---------------------------------------------------------
    recs['norm_stock'] = (
        recs['current_stock_source'] /
        recs['current_stock_source'].max()
        if recs['current_stock_source'].max() > 0
        else 0
    )

    recs['norm_demand'] = (
        recs['avg_daily_sales_dest'] /
        recs['avg_daily_sales_dest'].max()
        if recs['avg_daily_sales_dest'].max() > 0
        else 0
    )

    # ---------------------------------------------------------
    # 5️⃣ Transfer score (0–1, interpretable)
    # ---------------------------------------------------------
    recs['transfer_score'] = (
        0.5 * recs['deadstock_score_source'] +
        0.3 * recs['norm_stock'] +
        0.2 * recs['norm_demand']
    )

    # ---------------------------------------------------------
    # 6️⃣ Final output
    # ---------------------------------------------------------
    result = (
        recs[['SKU', 'store_from', 'store_to', 'transfer_score']]
        .sort_values('transfer_score', ascending=False)
        .reset_index(drop=True)
    )

    return result
