import pandas as pd

from logic.data_validation import validate_inventory_df
from logic.data_cleaning import clean_inventory_df


def load_inventory(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)

    validate_inventory_df(df)
    df = clean_inventory_df(df)

    return df


if __name__ == "__main__":
    df = load_inventory("data/raw/synthetic_retail_sales_inventory.csv")
   
    print(df.head())


# Optional but VERY useful for testing this file alone
if __name__ == "__main__":
    df = load_inventory("data/raw/synthetic_retail_sales_inventory.csv")
    print(df.head())