import tempfile
import unittest
from pathlib import Path
import pandas as pd
from analysis import ROOT, clean_sales, run, summarize_sales

class SalesTests(unittest.TestCase):
    def setUp(self):
        self.raw = pd.read_csv(ROOT / "data/sales.csv")

    def test_known_dirty_records_and_revenue(self):
        data, audit = clean_sales(self.raw)
        self.assertEqual(audit["input_rows"], 181)
        self.assertEqual(audit["exact_duplicates_removed"], 1)
        self.assertEqual(audit["invalid_rows_removed"], 4)
        self.assertEqual(len(data), 176)
        self.assertEqual(audit["missing_categories_filled"], 1)
        first = data.loc[data.transaction_id == "TX0001"].iloc[0]
        self.assertEqual(first.revenue, 10800)
        summary, categories, monthly = summarize_sales(data)
        self.assertAlmostEqual(categories.sum(), summary["total_revenue_idr"])
        self.assertAlmostEqual(monthly.sum(), summary["total_revenue_idr"])

    def test_nonfinite_or_fractional_quantity_is_rejected(self):
        for value in [float("inf"), 1.5]:
            raw = self.raw.iloc[:2].copy()
            raw.loc[0, "quantity"] = value
            data, audit = clean_sales(raw)
            self.assertEqual(len(data), 1)
            self.assertEqual(audit["invalid_rows_removed"], 1)

    def test_conflicting_ids_are_not_silently_merged(self):
        raw = self.raw.iloc[:2].copy()
        raw.loc[1, "transaction_id"] = raw.loc[0, "transaction_id"]
        with self.assertRaisesRegex(ValueError, "Conflicting"):
            clean_sales(raw)

    def test_schema_and_empty_data_fail_clearly(self):
        with self.assertRaisesRegex(ValueError, "Missing columns"):
            clean_sales(pd.DataFrame({"date": []}))
        with self.assertRaisesRegex(ValueError, "No valid"):
            clean_sales(self.raw.iloc[0:0])

    def test_report_pipeline_writes_artifacts(self):
        with tempfile.TemporaryDirectory() as directory:
            run(output_dir=directory)
            for name in ["summary.json", "report.md", "sales_overview.png", "clean_sales.csv"]:
                self.assertTrue((Path(directory) / name).is_file())

if __name__ == "__main__":
    unittest.main()
