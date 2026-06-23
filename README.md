# ApexPlanet Data Analytics Internship
**30-Day Data Analytics Internship — Sarat Kumar**

![Python](https://img.shields.io/badge/Python-3.11-blue)
![SQL](https://img.shields.io/badge/SQLite-Database-lightgrey)
![Pandas](https://img.shields.io/badge/Pandas-Data%20Analysis-green)
![Jupyter](https://img.shields.io/badge/Jupyter-Notebook-orange)
![Status](https://img.shields.io/badge/Task%201%20%26%202-Completed-success)

## Repository Structure
```text
APEXPLANET-DATA-ANALYTICS/
│
├── dashboards/
│   └── .gitkeep
│
├── data/
│   ├── processed/
│   │   └── superstore_cleaned.csv  # Cleaned Superstore dataset (Task 1)
│   ├── raw/
│   │   └── superstore.csv          # Raw dataset
│   └── superstore.db              # SQLite Database file (Task 2)
│
├── notebooks/
│   ├── Task1.ipynb                 # EDA & Data Cleaning Notebook (Task 1)
│   └── Task2.ipynb                 # SQL for Data Extraction Notebook (Task 2)
│
├── reports/
│   └── figures/
│       ├── sql_*.png               # Task 2 generated figures
│       └── [00-11]_*.png           # Task 1 generated figures
│
├── scripts/
│   ├── create_database.py          # Database setup and view creation (Task 2)
│   ├── db_utils.py                 # DB connection and helper utilities (Task 2)
│   ├── sql_analysis.py             # CLI runner for the 12 business questions (Task 2)
│   └── queries.sql                 # Standalone SQL query file (Task 2)
│
├── requirements.txt
└── README.md
```

---

## Task 1: Foundational Setup & Exploratory Data Analysis (EDA)
The objective of this task was to clean the raw Superstore sales dataset and perform exploratory data analysis to identify initial trends.

### Data Cleaning Process
The following preprocessing steps were performed:
- Loaded dataset into Pandas DataFrame.
- Handled missing values and removed duplicate records.
- Converted columns to appropriate data types.
- Detected and treated outliers using the Interquartile Range (IQR) method.
- Saved the cleaned dataset to `data/processed/superstore_cleaned.csv`.

---

## Task 2: SQL for Data Extraction & Business Analysis
The objective of this task was to import the cleaned dataset into a relational database, design analytical views, and answer critical business questions using SQLite and Python.

### Database Schema Design
The database `data/superstore.db` contains:
- **`orders` (Fact Table)**: 9,799 rows, matching the cleaned dataset with all 27 attributes.
- **`customers` (Dimension Table)**: 793 unique customer records (`customer_id`, `customer_name`, `segment`).
- **`products` (Dimension Table)**: 1,861 unique product records (`product_id`, `category`, `sub_category`, `product_name`).

### Analytical Views
1. `vw_customer_summary`: Lifetime sales and unique order counts per customer.
2. `vw_product_summary`: Lifetime sales and line item counts per product.
3. `vw_monthly_sales`: Monthly aggregated sales trends and order counts.
4. `vw_category_sales`: Sub-category sales totals partitioned within major categories.
5. `vw_order_summary`: Order-level total sales and average shipping duration.

### 12 Business Questions Solved
* **BQ-1: Top 5 Products by Sales** — Canon imageCLASS 2200 Advanced Copier leads with ~$61.6K.
* **BQ-2: Top 10 Customers by Revenue** — High concentration of VIP customers; top customer Sean Miller has $25K lifetime spend.
* **BQ-3: Monthly Sales Trend (2015-2018)** — Shows repeating Q4 holiday spikes (Sep-Dec) and year-over-year revenue growth.
* **BQ-4: Sales by Region** — West (31.4%) and East (29.6%) are dominant; South (17.2%) lags.
* **BQ-5: Category Performance** — Technology has the highest average sale per line item ($456), while Office Supplies drives the highest transaction volume.
* **BQ-6: Most Valuable Products** — High-ticket copiers and machines dominate the top of the average sale ranking.
* **BQ-7: Customer Spend Tiers** — Categorizes customers into High Value (≥$5K), Medium Value ($1K-$5K), and Low Value (<$1K) spend tiers.
* **BQ-8: Average Order Value by Segment** — Home Office segments show a higher average order value.
* **BQ-9: Top 10 States by Sales** — California represents ~20% of national sales, and the top 3 states represent ~40%.
* **BQ-10: Sub-Category Share** — Shows revenue distribution; Phones represent ~40% of Technology sales.
* **BQ-11: Ship Mode Performance** — Standard Class represents 60% of all orders, demonstrating customer sensitivity to cost over speed.
* **BQ-12: Year-over-Year Sales Growth** — Sustained double-digit sales growth (+29.5%, +30.6%, +20.3%) from 2015 to 2018.

### Python + SQL Integration
We implemented two integration patterns:
1. **Pandas + SQLAlchemy**: Using `pandas.read_sql` combined with SQLAlchemy parameter bindings to run parameterized queries safely.
2. **Raw `sqlite3`**: Standard library cursor operations for lower-level DDL queries.

---

## Deliverables Completed
- [x] **SQLite Database**: `data/superstore.db` populated with tables, primary keys, and indexes.
- [x] **Database Views**: 5 analytical views built for reusable aggregations.
- [x] **Jupyter Notebook**: `notebooks/Task2.ipynb` generated and executed with all outputs embedded.
- [x] **CLI Script**: `scripts/sql_analysis.py` for direct terminal execution.
- [x] **SQL Script**: `scripts/queries.sql` containing all clean query code.

## Learning Outcomes
Through Task 2, I mastered:
- Standard and Advanced DQL (Data Query Language) constructs.
- Writing subqueries, Correlated subqueries, and Common Table Expressions (CTEs).
- Implementing Window Functions (`RANK`, `ROW_NUMBER`, `LAG`, `LEAD`) for time-series and ranking analysis.
- Relational schema normalization and indexing in SQLite.
- Integrating Python with SQL databases securely to automate reporting pipelines.

---

## Author
**Sarat Kumar**  
B.Tech — Artificial Intelligence & Machine Learning  
ApexPlanet Data Analytics Internship
