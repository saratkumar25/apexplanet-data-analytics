import pandas as pd
from db_utils import run_query, get_engine

# --- Demo Query Functions ---

def demo_select(engine=None):
    query = """
        SELECT order_id, customer_name, segment, category, sub_category, ROUND(sales, 2) AS sales 
        FROM orders 
        LIMIT 10;
    """
    return run_query(query, engine)

def demo_where(region="West", engine=None):
    query = """
        SELECT order_id, customer_name, segment, category, sub_category, ROUND(sales, 2) AS sales 
        FROM orders 
        WHERE region = :region 
        ORDER BY sales DESC 
        LIMIT 10;
    """
    return run_query(query, engine, params={"region": region})

def demo_order_by(engine=None):
    query = """
        SELECT order_id, customer_name, product_name, ROUND(sales, 2) AS sales 
        FROM orders 
        ORDER BY sales DESC 
        LIMIT 10;
    """
    return run_query(query, engine)

def demo_limit(n=5, engine=None):
    query = """
        SELECT order_id, customer_name, product_name, ROUND(sales, 2) AS sales 
        FROM orders 
        LIMIT :n;
    """
    return run_query(query, engine, params={"n": n})

def demo_group_by(engine=None):
    query = """
        SELECT category, ROUND(SUM(sales), 2) AS total_sales, ROUND(AVG(sales), 2) AS avg_sale 
        FROM orders 
        GROUP BY category;
    """
    return run_query(query, engine)

def demo_having(min_sales=50000, engine=None):
    query = """
        SELECT state, ROUND(SUM(sales), 2) AS total_sales 
        FROM orders 
        GROUP BY state 
        HAVING SUM(sales) > :min_sales
        ORDER BY total_sales DESC;
    """
    return run_query(query, engine, params={"min_sales": min_sales})

def demo_join(engine=None):
    query = """
        SELECT 
            o.order_id, 
            o.order_date, 
            c.customer_name, 
            c.segment, 
            p.product_name, 
            p.sub_category, 
            ROUND(o.sales, 2) AS sales 
        FROM orders o 
        JOIN customers c ON o.customer_id = c.customer_id 
        JOIN products p ON o.product_id = p.product_id 
        LIMIT 10;
    """
    return run_query(query, engine)

def demo_subquery(engine=None):
    query = """
        SELECT customer_id, customer_name, total_sales 
        FROM vw_customer_summary 
        WHERE total_sales > (SELECT AVG(total_sales) FROM vw_customer_summary) 
        ORDER BY total_sales DESC 
        LIMIT 10;
    """
    return run_query(query, engine)

def demo_cte_category_rank(engine=None):
    query = """
        WITH sub_cat_sales AS (
            SELECT category, sub_category, SUM(sales) AS total_sales
            FROM orders
            GROUP BY category, sub_category
        )
        SELECT category, sub_category, ROUND(total_sales, 2) AS total_sales,
               RANK() OVER (PARTITION BY category ORDER BY total_sales DESC) AS sales_rank,
               ROW_NUMBER() OVER (PARTITION BY category ORDER BY total_sales DESC) AS row_num
        FROM sub_cat_sales;
    """
    return run_query(query, engine)

def demo_cte_monthly_growth(engine=None):
    query = """
        WITH monthly_sales AS (
            SELECT order_year_month AS year_month, SUM(sales) AS total_sales
            FROM orders
            GROUP BY order_year_month
        ),
        sales_lead_lag AS (
            SELECT year_month, total_sales,
                   LAG(total_sales, 1) OVER (ORDER BY year_month) AS prior_sales
            FROM monthly_sales
        )
        SELECT year_month, ROUND(total_sales, 2) AS total_sales, ROUND(prior_sales, 2) AS prior_sales,
               ROUND(((total_sales - prior_sales) / prior_sales) * 100, 2) AS mom_growth_pct
        FROM sales_lead_lag;
    """
    return run_query(query, engine)

def demo_window_row_number(engine=None):
    query = """
        WITH top_customers AS (
            SELECT customer_id FROM vw_customer_summary ORDER BY total_sales DESC LIMIT 5
        )
        SELECT customer_id, order_id, order_date, ROUND(sales, 2) AS sales,
               ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY order_date) AS order_seq
        FROM orders
        WHERE customer_id IN (SELECT customer_id FROM top_customers)
        ORDER BY customer_id, order_date;
    """
    return run_query(query, engine)

def demo_window_rank(engine=None):
    query = """
        SELECT customer_id, customer_name, segment, total_sales,
               RANK() OVER (PARTITION BY segment ORDER BY total_sales DESC) AS spend_rank,
               DENSE_RANK() OVER (PARTITION BY segment ORDER BY total_sales DESC) AS spend_dense_rank
        FROM vw_customer_summary
        ORDER BY segment, spend_rank
        LIMIT 20;
    """
    return run_query(query, engine)

def demo_window_lag_lead(engine=None):
    query = """
        WITH monthly_sales AS (
            SELECT order_year_month AS year_month, SUM(sales) AS total_sales
            FROM orders
            GROUP BY order_year_month
        )
        SELECT year_month, ROUND(total_sales, 2) AS total_sales,
               ROUND(LAG(total_sales, 1) OVER (ORDER BY year_month), 2) AS prev_month_sales,
               ROUND(LEAD(total_sales, 1) OVER (ORDER BY year_month), 2) AS next_month_sales
        FROM monthly_sales
        ORDER BY year_month
        LIMIT 15;
    """
    return run_query(query, engine)


# --- Business Question Query Functions ---

def bq1_top_products_by_sales(n=5, engine=None):
    query = """
        SELECT product_name, ROUND(SUM(sales), 2) AS total_sales 
        FROM orders 
        GROUP BY product_name 
        ORDER BY total_sales DESC 
        LIMIT :n;
    """
    return run_query(query, engine, params={"n": n})

def bq2_top_customers_by_revenue(n=10, engine=None):
    query = """
        SELECT customer_name, segment, ROUND(SUM(sales), 2) AS total_sales 
        FROM orders 
        GROUP BY customer_name, segment 
        ORDER BY total_sales DESC 
        LIMIT :n;
    """
    return run_query(query, engine, params={"n": n})

def bq3_monthly_sales_trend(engine=None):
    query = """
        SELECT order_year_month AS year_month, ROUND(SUM(sales), 2) AS total_sales 
        FROM orders 
        GROUP BY order_year_month 
        ORDER BY order_year_month;
    """
    return run_query(query, engine)

def bq4_sales_by_region(engine=None):
    query = """
        WITH total AS (SELECT SUM(sales) AS grand_total FROM orders)
        SELECT region, ROUND(SUM(sales), 2) AS total_sales,
               ROUND((SUM(sales) / (SELECT grand_total FROM total)) * 100, 2) AS revenue_share_pct
        FROM orders
        GROUP BY region
        ORDER BY total_sales DESC;
    """
    return run_query(query, engine)

def bq5_avg_sale_by_category(engine=None):
    query = """
        SELECT category, ROUND(SUM(sales), 2) AS total_sales, ROUND(AVG(sales), 2) AS avg_sale, COUNT(DISTINCT order_id) AS unique_orders 
        FROM orders 
        GROUP BY category;
    """
    return run_query(query, engine)

def bq6_top_products_by_avg_sale(n=10, engine=None):
    query = """
        SELECT product_name, ROUND(AVG(sales), 2) AS avg_sale, COUNT(*) AS order_count 
        FROM orders 
        GROUP BY product_name 
        ORDER BY avg_sale DESC 
        LIMIT :n;
    """
    return run_query(query, engine, params={"n": n})

def bq7_customer_segmentation_by_spend(engine=None):
    query = """
        WITH customer_spend AS (
            SELECT customer_id, customer_name, segment, SUM(sales) AS total_spend
            FROM orders
            GROUP BY customer_id, customer_name, segment
        ),
        spend_tiers AS (
            SELECT customer_id, customer_name, segment, total_spend,
                   CASE
                       WHEN total_spend >= 5000 THEN 'High Value'
                       WHEN total_spend >= 1000 THEN 'Medium Value'
                       ELSE 'Low Value'
                   END AS spend_tier
            FROM customer_spend
        )
        SELECT segment, spend_tier, COUNT(*) AS customer_count, ROUND(SUM(total_spend), 2) AS total_segment_spend
        FROM spend_tiers
        GROUP BY segment, spend_tier
        ORDER BY segment, spend_tier;
    """
    return run_query(query, engine)

def bq8_average_order_value(engine=None):
    query = """
        WITH order_totals AS (
            SELECT order_id, order_year, segment, SUM(sales) AS order_total
            FROM orders
            GROUP BY order_id, order_year, segment
        )
        SELECT order_year, segment, ROUND(AVG(order_total), 2) AS avg_order_value
        FROM order_totals
        GROUP BY order_year, segment
        ORDER BY order_year, segment;
    """
    return run_query(query, engine)

def bq9_best_performing_states(n=10, engine=None):
    query = """
        WITH state_sales AS (
            SELECT state, SUM(sales) AS total_sales
            FROM orders
            GROUP BY state
        ),
        total AS (SELECT SUM(sales) AS grand_total FROM orders),
        state_shares AS (
            SELECT state, total_sales,
                   ROUND((total_sales / (SELECT grand_total FROM total)) * 100, 2) AS share_pct
            FROM state_sales
        ),
        ranked_states AS (
            SELECT state, total_sales, share_pct,
                   SUM(share_pct) OVER (ORDER BY total_sales DESC) AS cumulative_share_pct
            FROM state_shares
        )
        SELECT state, ROUND(total_sales, 2) AS total_sales, share_pct, ROUND(cumulative_share_pct, 2) AS cumulative_share_pct
        FROM ranked_states
        ORDER BY total_sales DESC
        LIMIT :n;
    """
    return run_query(query, engine, params={"n": n})

def bq10_revenue_contribution_by_subcategory(engine=None):
    query = """
        WITH cat_totals AS (
            SELECT category, SUM(sales) AS cat_total
            FROM orders
            GROUP BY category
        ),
        subcat_totals AS (
            SELECT category, sub_category, SUM(sales) AS total_sales
            FROM orders
            GROUP BY category, sub_category
        )
        SELECT s.category, s.sub_category, ROUND(s.total_sales, 2) AS total_sales,
               ROUND((s.total_sales / c.cat_total) * 100, 2) AS revenue_share_pct
        FROM subcat_totals s
        JOIN cat_totals c ON s.category = c.category
        ORDER BY s.category, s.total_sales DESC;
    """
    return run_query(query, engine)

def bq11_ship_mode_analysis(engine=None):
    query = """
        SELECT ship_mode, COUNT(DISTINCT order_id) AS order_count, ROUND(AVG(shipping_days), 2) AS avg_shipping_days, ROUND(SUM(sales), 2) AS total_sales 
        FROM orders 
        GROUP BY ship_mode 
        ORDER BY total_sales DESC;
    """
    return run_query(query, engine)

def bq12_yoy_sales_growth(engine=None):
    query = """
        WITH yearly_sales AS (
            SELECT order_year, SUM(sales) AS total_sales
            FROM orders
            GROUP BY order_year
        )
        SELECT order_year, ROUND(total_sales, 2) AS total_sales,
               ROUND(LAG(total_sales, 1) OVER (ORDER BY order_year), 2) AS prior_year_sales,
               ROUND(((total_sales - LAG(total_sales, 1) OVER (ORDER BY order_year)) / LAG(total_sales, 1) OVER (ORDER BY order_year)) * 100, 2) AS yoy_growth_pct
        FROM yearly_sales
        ORDER BY order_year;
    """
    return run_query(query, engine)


def run_all(engine=None):
    if engine is None:
        engine = get_engine()
        
    print("Executing all SQL business questions...")
    print("========================================")
    
    questions = [
        ("BQ-1: Top 5 Products by Total Sales", bq1_top_products_by_sales, {"n": 5}),
        ("BQ-2: Top 10 Customers by Lifetime Revenue", bq2_top_customers_by_revenue, {"n": 10}),
        ("BQ-3: Monthly Sales Trend (2015-2018)", bq3_monthly_sales_trend, {}),
        ("BQ-4: Sales by Region", bq4_sales_by_region, {}),
        ("BQ-5: Sales Performance by Category", bq5_avg_sale_by_category, {}),
        ("BQ-6: Most Valuable Products by Average Sale", bq6_top_products_by_avg_sale, {"n": 10}),
        ("BQ-7: Customer Spend Tiers", bq7_customer_segmentation_by_spend, {}),
        ("BQ-8: Average Order Value by Year & Segment", bq8_average_order_value, {}),
        ("BQ-9: Top 10 States by Sales", bq9_best_performing_states, {"n": 10}),
        ("BQ-10: Revenue Share by Sub-Category Within Category", bq10_revenue_contribution_by_subcategory, {}),
        ("BQ-11: Ship Mode Performance Analysis", bq11_ship_mode_analysis, {}),
        ("BQ-12: Year-over-Year Sales Growth", bq12_yoy_sales_growth, {})
    ]
    
    for title, func, kwargs in questions:
        print(f"\n--- {title} ---")
        df = func(engine=engine, **kwargs)
        # Use simple print format
        print(df.to_string(index=False))
        print("----------------------------------------")

if __name__ == "__main__":
    run_all()
