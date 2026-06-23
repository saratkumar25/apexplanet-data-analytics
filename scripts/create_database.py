import pandas as pd
from pathlib import Path
from sqlalchemy import create_engine, text

def main():
    # Resolve paths relative to this script
    script_dir = Path(__file__).resolve().parent
    project_root = script_dir.parent
    csv_path = project_root / "data" / "processed" / "superstore_cleaned.csv"
    db_path = project_root / "data" / "superstore.db"

    print(f"Reading cleaned dataset from {csv_path}...")
    if not csv_path.exists():
        raise FileNotFoundError(f"Cleaned dataset not found at {csv_path}")

    df = pd.read_csv(csv_path)

    # Convert headers to snake_case
    df.columns = df.columns.str.lower().str.replace(' ', '_').str.replace('-', '_')

    # Create database engine
    db_path.parent.mkdir(parents=True, exist_ok=True)
    engine = create_engine(f"sqlite:///{db_path}")

    print("Populating orders table...")
    # orders table has all 27 columns
    df.to_sql("orders", con=engine, if_exists="replace", index=False)

    print("Populating customers table (dimension)...")
    # customers dimension table
    customers_df = df[['customer_id', 'customer_name', 'segment']].drop_duplicates(subset=['customer_id']).reset_index(drop=True)
    customers_df.to_sql("customers", con=engine, if_exists="replace", index=False)
    
    print("Populating products table (dimension)...")
    # products dimension table
    products_df = df[['product_id', 'category', 'sub_category', 'product_name']].drop_duplicates(subset=['product_id']).reset_index(drop=True)
    products_df.to_sql("products", con=engine, if_exists="replace", index=False)

    print("Creating primary keys and indexes...")
    # Add indexes for performance since SQLite 'replace' doesn't preserve constraints
    with engine.begin() as conn:
        # Create indexes
        conn.execute(text("CREATE UNIQUE INDEX IF NOT EXISTS idx_customers_id ON customers(customer_id);"))
        conn.execute(text("CREATE UNIQUE INDEX IF NOT EXISTS idx_products_id ON products(product_id);"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_orders_customer ON orders(customer_id);"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_orders_product ON orders(product_id);"))

    print("Creating views...")
    views = {
        "vw_customer_summary": """
            CREATE VIEW IF NOT EXISTS vw_customer_summary AS
            SELECT 
                customer_id, 
                customer_name, 
                segment, 
                ROUND(SUM(sales), 2) AS total_sales, 
                COUNT(DISTINCT order_id) AS order_count
            FROM orders
            GROUP BY customer_id, customer_name, segment;
        """,
        "vw_product_summary": """
            CREATE VIEW IF NOT EXISTS vw_product_summary AS
            SELECT 
                product_id, 
                product_name, 
                category, 
                sub_category, 
                ROUND(SUM(sales), 2) AS total_sales, 
                COUNT(*) AS order_line_count
            FROM orders
            GROUP BY product_id, product_name, category, sub_category;
        """,
        "vw_monthly_sales": """
            CREATE VIEW IF NOT EXISTS vw_monthly_sales AS
            SELECT 
                order_year_month AS year_month, 
                ROUND(SUM(sales), 2) AS total_sales, 
                COUNT(DISTINCT order_id) AS order_count
            FROM orders
            GROUP BY order_year_month;
        """,
        "vw_category_sales": """
            CREATE VIEW IF NOT EXISTS vw_category_sales AS
            SELECT 
                category, 
                sub_category, 
                ROUND(SUM(sales), 2) AS total_sales, 
                COUNT(DISTINCT order_id) AS order_count
            FROM orders
            GROUP BY category, sub_category;
        """,
        "vw_order_summary": """
            CREATE VIEW IF NOT EXISTS vw_order_summary AS
            SELECT 
                order_id, 
                customer_id, 
                order_date, 
                segment, 
                region, 
                ROUND(SUM(sales), 2) AS total_sales, 
                AVG(shipping_days) AS avg_shipping_days
            FROM orders
            GROUP BY order_id, customer_id, order_date, segment, region;
        """
    }

    with engine.begin() as conn:
        for view_name, view_sql in views.items():
            print(f"Creating view {view_name}...")
            conn.execute(text(f"DROP VIEW IF EXISTS {view_name};"))
            conn.execute(text(view_sql))

    print(f"Database successfully created at {db_path}!")
    
if __name__ == "__main__":
    main()
