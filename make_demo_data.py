"""Create deterministic fictional sales, including documented data-quality problems."""
import csv
from datetime import date, timedelta
from pathlib import Path

def generate():
    rows = []
    categories = ["Stationery", "Drinks", "Snacks"]
    prices = [12000, 18000, 15000]
    for i in range(180):
        rows.append([f"TX{i + 1:04d}", str(date(2025, 1, 1) + timedelta(days=i)),
                     categories[i % 3], ["Campus", "City"][i % 2],
                     (i * 7) % 5 + 1, prices[i % 3], "0.1" if i % 4 == 0 else "0.0"])
    rows[7][2] = ""
    rows[15][4] = ""
    rows[41][1] = "not-a-date"
    rows[70][6] = "1.5"
    rows[94][4] = -1
    rows[130][2] = "  drinks  "
    rows.append(rows[5].copy())
    return rows

if __name__ == "__main__":
    path = Path(__file__).resolve().parent / "data/sales.csv"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(["transaction_id", "date", "category", "branch", "quantity", "unit_price", "discount"])
        writer.writerows(generate())
    print(f"Wrote {path}")
