import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config(page_title="Deadstock Redistribution — Demo", layout="wide")
st.title("Deadstock Redistribution — Demo")

data_path = Path("data/raw/synthetic_retail_sales_inventory.csv")

if data_path.exists():
	df = pd.read_csv(data_path)
	st.markdown(f"**Loaded dataset:** {data_path} — {df.shape[0]} rows, {df.shape[1]} columns")
	st.dataframe(df.head(100))
	with st.expander("Columns"):
		st.write(list(df.columns))
else:
	st.warning(f"Sample dataset not found at {data_path}.")
	st.info("Place your CSV at data/raw/synthetic_retail_sales_inventory.csv to view it here.")

