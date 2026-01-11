import argparse
import subprocess
import sys
from pathlib import Path

from fastapi import FastAPI
import pandas as pd

app = FastAPI()


@app.get("/")
def read_root():
	return {"message": "Deadstock Redistribution API — use /data to preview dataset"}


@app.get("/data")
def get_data_preview(n: int = 10):
	data_path = Path("data/raw/synthetic_retail_sales_inventory.csv")
	if not data_path.exists():
		return {"error": f"Dataset not found at {data_path}."}
	df = pd.read_csv(data_path)
	return {"rows": len(df), "columns": list(df.columns), "preview": df.head(n).to_dict(orient="records")}


def run_streamlit(python_exec: str):
	cmd = [python_exec, "-m", "streamlit", "run", "dashboard/dashboard.py"]
	return subprocess.Popen(cmd)


def run_uvicorn(python_exec: str):
	cmd = [python_exec, "-m", "uvicorn", "app.main:app", "--reload", "--port", "8000"]
	return subprocess.Popen(cmd)


def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("--mode", choices=["streamlit", "api"], default="streamlit")
	parser.add_argument("--python", default=sys.executable)
	args = parser.parse_args()

	if args.mode == "streamlit":
		print("Starting Streamlit dashboard...")
		proc = run_streamlit(args.python)
	else:
		print("Starting FastAPI (uvicorn) server on http://localhost:8000 ...")
		proc = run_uvicorn(args.python)

	try:
		proc.wait()
	except KeyboardInterrupt:
		proc.terminate()


if __name__ == "__main__":
	main()

