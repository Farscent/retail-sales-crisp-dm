"""Explore a fictional shop's sales using a small, reproducible CRISP-DM workflow."""
import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
COLUMNS = ["transaction_id", "date", "category", "branch", "quantity", "unit_price", "discount"]

def clean_sales(raw):
    """Return valid transactions and an audit; never silently invent missing sales."""
    missing = set(COLUMNS) - set(raw.columns)
    if missing:
        raise ValueError(f"Missing columns: {sorted(missing)}")
    data = raw[COLUMNS].copy()
    audit = {"input_rows": len(data)}
    data = data.drop_duplicates()
    audit["exact_duplicates_removed"] = len(raw) - len(data)
    data["date"] = pd.to_datetime(data["date"], format="%Y-%m-%d", errors="coerce")
    for column in ["quantity", "unit_price", "discount"]:
        data[column] = pd.to_numeric(data[column], errors="coerce")
    for column in ["transaction_id", "category", "branch"]:
        data[column] = data[column].astype("string").str.strip().replace("", pd.NA)
    valid = (
        data["date"].notna() & data["transaction_id"].notna()
        & np.isfinite(data[["quantity", "unit_price", "discount"]]).all(axis=1)
        & data["quantity"].gt(0) & data["quantity"].mod(1).eq(0)
        & data["unit_price"].gt(0) & data["discount"].between(0, 1)
    )
    audit["invalid_rows_removed"] = int((~valid).sum())
    data = data.loc[valid].copy()
    if data.empty:
        raise ValueError("No valid transactions remain after cleaning.")
    if data["transaction_id"].duplicated().any():
        raise ValueError("Conflicting transaction IDs: check the source before aggregating.")
    audit["missing_categories_filled"] = int(data["category"].isna().sum())
    data["category"] = data["category"].fillna("Unknown").str.title()
    data["branch"] = data["branch"].fillna("Unknown").str.title()
    data["quantity"] = data["quantity"].astype(int)
    # Discount is a fraction: 0.10 means 10%, not ten currency units.
    data["revenue"] = data["quantity"] * data["unit_price"] * (1 - data["discount"])
    audit["output_rows"] = len(data)
    return data.sort_values(["date", "transaction_id"]).reset_index(drop=True), audit

def summarize_sales(data):
    category = data.groupby("category")["revenue"].sum().sort_values(ascending=False)
    monthly = data.groupby(data["date"].dt.to_period("M"))["revenue"].sum()
    monthly.index = monthly.index.astype(str)
    summary = {
        "transactions": len(data),
        "total_revenue_idr": round(float(data["revenue"].sum()), 2),
        "average_transaction_value_idr": round(float(data["revenue"].mean()), 2),
        "top_category": str(category.index[0]),
    }
    return summary, category, monthly

def run(input_path=ROOT / "data/sales.csv", output_dir=ROOT / "outputs"):
    data, audit = clean_sales(pd.read_csv(input_path))
    summary, category, monthly = summarize_sales(data)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    data.to_csv(output_dir / "clean_sales.csv", index=False)
    category.to_csv(output_dir / "revenue_by_category.csv")
    monthly.to_csv(output_dir / "monthly_revenue.csv")
    (output_dir / "summary.json").write_text(
        json.dumps({"cleaning": audit, "results": summary}, indent=2) + "\n", encoding="utf-8")
    fig, axes = plt.subplots(1, 2, figsize=(11, 4))
    category.plot.bar(ax=axes[0], color="#246b74", rot=15)
    monthly.plot(ax=axes[1], marker="o", color="#d67b36")
    axes[0].set(title="Revenue by category", ylabel="Revenue (IDR)", xlabel="")
    axes[1].set(title="Monthly revenue", ylabel="Revenue (IDR)", xlabel="Month")
    fig.suptitle("Fictional shop · cleaned demonstration data")
    fig.tight_layout()
    fig.savefig(output_dir / "sales_overview.png", dpi=160)
    plt.close(fig)
    report = (
        "# Sales findings\n\n"
        "These results describe the included synthetic data, not a real shop.\n\n"
        f"- Valid transactions: {summary['transactions']}\n"
        f"- Revenue after discounts: IDR {summary['total_revenue_idr']:,.0f}\n"
        f"- Average transaction: IDR {summary['average_transaction_value_idr']:,.0f}\n"
        f"- Largest category by revenue: {summary['top_category']}\n"
        f"- Removed: {audit['exact_duplicates_removed']} exact duplicate and "
        f"{audit['invalid_rows_removed']} invalid rows.\n\n"
        "Revenue does not measure profit: product costs are unavailable. "
        "Check source records for removed transactions before using this process in real reporting.\n")
    (output_dir / "report.md").write_text(report, encoding="utf-8")
    print(json.dumps({"cleaning": audit, "results": summary}, indent=2))
    return data, audit, summary

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=ROOT / "data/sales.csv")
    parser.add_argument("--output", type=Path, default=ROOT / "outputs")
    args = parser.parse_args()
    try:
        run(args.input, args.output)
    except (ValueError, OSError) as error:
        parser.exit(2, f"Error: {error}\n")
