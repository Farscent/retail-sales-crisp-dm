[![Tests](https://github.com/Farscent/retail-sales-crisp-dm/actions/workflows/tests.yml/badge.svg)](https://github.com/Farscent/retail-sales-crisp-dm/actions/workflows/tests.yml)

# Retail Sales Analysis with CRISP-DM

A beginner data analysis project about a fictional shop. The aim is to turn a small, messy CSV file into a clear sales report using Python and pandas.

**Research question:** Which product categories contribute the most revenue, and how does revenue change over time?

## Example results

![Sales overview from the included synthetic data](docs/overview.png)

| Measure | Result |
|---|---:|
| Valid transactions | 176 |
| Revenue after discounts | IDR 7,750,500.00 |
| Average transaction value | IDR 44,036.93 |
| Largest category by revenue | Drinks |

These are verified outputs from the bundled fictional dataset, not real business findings. [Read the generated example report](docs/example-report.md).

## Learning objectives

- Inspect a dataset before calculating results.
- Handle duplicates, missing values, invalid dates, and invalid numbers.
- Use pandas filtering, grouping, and date operations.
- Calculate revenue and average transaction value.
- Explain findings and limitations using the CRISP-DM process.

## Dataset

The included [sales.csv](data/sales.csv) is **synthetic**. It contains 180 fictional transactions from January to June 2025 and one deliberately repeated row. No customer information or real business records are used.

| Column | Meaning |
|---|---|
| transaction_id | Unique identifier; each row represents one complete transaction |
| date | Transaction date, in YYYY-MM-DD format |
| category | Stationery, Drinks, Snacks, or an unknown category |
| branch | Campus or City |
| quantity | Positive whole number of items |
| unit_price | Price per item in Indonesian rupiah (IDR) |
| discount | Fraction between 0 and 1; 0.10 means 10% |

The [generator](make_demo_data.py) deliberately adds one missing category, one missing quantity, one invalid date, one invalid discount, one negative quantity, inconsistent category spacing, and one exact duplicate.

## Method: the six CRISP-DM phases

| Phase | Application in this project |
|---|---|
| 1. Business understanding | Define category revenue and monthly revenue as the questions of interest. |
| 2. Data understanding | Inspect row counts, column types, missing values, and unusual records. |
| 3. Data preparation | Remove exact duplicates; reject invalid transactions; label a missing category as Unknown. |
| 4. Modeling | Use descriptive aggregation rather than a predictive model. A forecasting model is unnecessary for these questions. |
| 5. Evaluation | Check that grouped totals equal overall revenue and review the effect of removed rows. |
| 6. Deployment | Export a reusable report, clean data, tables, and a chart through a command-line script. |

CRISP-DM is iterative: unexpected findings can send the analyst back to the data preparation stage. Here, “deployment” means delivering a repeatable report, not hosting a web application.

## Run the project

Use **Python 3.11, 3.12, or 3.13**. Clone the project and create an environment:

~~~bash
git clone https://github.com/Farscent/retail-sales-crisp-dm.git
cd retail-sales-crisp-dm
python -m venv .venv
~~~

Activate the environment:

~~~powershell
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
~~~

~~~bash
# macOS / Linux
source .venv/bin/activate
~~~

Then run:

~~~bash
python -m pip install -r requirements.txt
python analysis.py
python -m unittest discover -s tests -v
~~~

If PowerShell blocks activation, use <code>.\.venv\Scripts\python.exe</code> instead of <code>python</code> in the commands above. Once dependencies are installed, no internet connection is needed.

For your own file with the same schema:

~~~bash
python analysis.py --input data/sales.csv --output outputs
~~~

## Calculations and outputs

~~~text
revenue = quantity × unit_price × (1 − discount)
average transaction value = total revenue / valid transaction count
~~~

For example, one IDR 12,000 item with a 10% discount contributes **IDR 10,800** in revenue.

The bundled data should produce **176 valid transactions**: 181 input rows, minus one exact duplicate and four invalid rows. The missing category is retained as Unknown.

| Output | Purpose |
|---|---|
| outputs/report.md | Short written findings |
| outputs/summary.json | Cleaning counts and headline measures |
| outputs/clean_sales.csv | Valid transactions and calculated revenue |
| outputs/revenue_by_category.csv | Category totals |
| outputs/monthly_revenue.csv | Monthly totals |
| outputs/sales_overview.png | Two charts for visual interpretation |

Open the generated report and chart after running the script. Generated results are ignored by Git so the source data remains the reference.

## How to interpret the analysis

A category with the highest revenue is the largest contributor to sales value in this dataset. It is not necessarily the most profitable category because costs are unavailable.

The audit makes cleaning decisions visible. Removing an invalid row reduces the reported total; in a real project, the preferred next step would be to correct that row using the original record. Conflicting transaction IDs cause an error rather than being merged silently.

The data is synthetic and the final month is incomplete. Do not interpret its patterns as evidence about a real shop or compare partial and full months without adjusting the question. One row per complete transaction is a deliberate simplification; real item-level order data needs an order-level denominator.

## Read and extend the code

Start with [walkthrough.ipynb](walkthrough.ipynb), then read <code>clean_sales()</code>, <code>summarize_sales()</code>, and <code>run()</code> in [analysis.py](analysis.py).

Try these exercises:

1. Add a revenue summary by branch.
2. Find the median transaction value and explain why it differs from the mean.
3. Report the percentage of rows excluded during cleaning.
4. Add product costs and distinguish revenue from gross profit.

**Questions to be able to answer:** Why keep an Unknown category? Why not replace a missing quantity with zero? Why is a forecasting model unnecessary here?

## References

- [IBM: CRISP-DM overview](https://www.ibm.com/docs/en/spss-modeler/saas?topic=dm-crisp-help-overview)
- [pandas documentation](https://pandas.pydata.org/docs/)

This is a student learning project, with no institutional affiliation or endorsement.


## Optional notebook

From this project folder, install the notebook tools and open the walkthrough:

~~~bash
python -m pip install -r requirements-notebook.txt
python -m notebook walkthrough.ipynb
~~~

Choose the project's Python environment and use **Run All**. The notebook imports the same tested functions as the script and adds explanations and intermediate tables.

## Validation and license

The project has been tested locally on Windows with Python 3.13. GitHub Actions checks Python 3.11 and 3.12; see the status badge at the top for the current result. The analysis notebooks include saved example outputs and can be rerun from top to bottom.

Code and the synthetic demonstration data are available under the [MIT License](LICENSE).
