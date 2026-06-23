-- ==============================================================================
-- APEXPLANET DATA ANALYTICS INTERNSHIP
-- TASK 2: SQL FOR DATA EXTRACTION & ANALYSIS
-- Standard SQL Queries and Analytical Views
-- ==============================================================================

-- ==============================================================================
-- PART 1: ANALYTICAL VIEWS
-- ==============================================================================

-- VIEW 1: Customer lifetime sales and order count
DROP VIEW IF EXISTS vw_customer_summary;
CREATE VIEW vw_customer_summary AS
SELECT 
    customer_id, 
    customer_name, 
    segment, 
    ROUND(SUM(sales), 2) AS total_sales, 
    COUNT(DISTINCT order_id) AS order_count
FROM orders
GROUP BY customer_id, customer_name, segment;


-- VIEW 2: Product lifetime sales and order count
DROP VIEW IF EXISTS vw_product_summary;
CREATE VIEW vw_product_summary AS
SELECT 
    product_id, 
    product_name, 
    category, 
    sub_category, 
    ROUND(SUM(sales), 2) AS total_sales, 
    COUNT(*) AS order_line_count
FROM orders
GROUP BY product_id, product_name, category, sub_category;


-- VIEW 3: Monthly sales trends
DROP VIEW IF EXISTS vw_monthly_sales;
CREATE VIEW vw_monthly_sales AS
SELECT 
    order_year_month AS year_month, 
    ROUND(SUM(sales), 2) AS total_sales, 
    COUNT(DISTINCT order_id) AS order_count
FROM orders
GROUP BY order_year_month;


-- VIEW 4: Sales performance by category and subcategory
DROP VIEW IF EXISTS vw_category_sales;
CREATE VIEW vw_category_sales AS
SELECT 
    category, 
    sub_category, 
    ROUND(SUM(sales), 2) AS total_sales, 
    COUNT(DISTINCT order_id) AS order_count
FROM orders
GROUP BY category, sub_category;


-- VIEW 5: Order-level aggregated metrics (AOV, shipping days)
DROP VIEW IF EXISTS vw_order_summary;
CREATE VIEW vw_order_summary AS
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


-- ==============================================================================
-- PART 2: BUSINESS QUESTIONS (BQ-1 TO BQ-12)
-- ==============================================================================

-- BQ-1: Top 5 Products by Total Sales
SELECT product_name, ROUND(SUM(sales), 2) AS total_sales 
FROM orders 
GROUP BY product_name 
ORDER BY total_sales DESC 
LIMIT 5;


-- BQ-2: Top 10 Customers by Lifetime Revenue
SELECT customer_name, segment, ROUND(SUM(sales), 2) AS total_sales 
FROM orders 
GROUP BY customer_name, segment 
ORDER BY total_sales DESC 
LIMIT 10;


-- BQ-3: Monthly Sales Trend (2015-2018)
SELECT order_year_month AS year_month, ROUND(SUM(sales), 2) AS total_sales 
FROM orders 
GROUP BY order_year_month 
ORDER BY order_year_month;


-- BQ-4: Sales by Region with Revenue Share
WITH total AS (SELECT SUM(sales) AS grand_total FROM orders)
SELECT region, ROUND(SUM(sales), 2) AS total_sales,
       ROUND((SUM(sales) / (SELECT grand_total FROM total)) * 100, 2) AS revenue_share_pct
FROM orders
GROUP BY region
ORDER BY total_sales DESC;


-- BQ-5: Sales Performance by Category
SELECT category, ROUND(SUM(sales), 2) AS total_sales, ROUND(AVG(sales), 2) AS avg_sale, COUNT(DISTINCT order_id) AS unique_orders 
FROM orders 
GROUP BY category;


-- BQ-6: Most Valuable Products by Average Sale
SELECT product_name, ROUND(AVG(sales), 2) AS avg_sale, COUNT(*) AS order_count 
FROM orders 
GROUP BY product_name 
ORDER BY avg_sale DESC 
LIMIT 10;


-- BQ-7: Customer Segmentation by Spend Tier
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


-- BQ-8: Average Order Value by Year & Segment
WITH order_totals AS (
    SELECT order_id, order_year, segment, SUM(sales) AS order_total
    FROM orders
    GROUP BY order_id, order_year, segment
)
SELECT order_year, segment, ROUND(AVG(order_total), 2) AS avg_order_value
FROM order_totals
GROUP BY order_year, segment
ORDER BY order_year, segment;


-- BQ-9: Top 10 States by Sales (with Cumulative Contribution)
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
LIMIT 10;


-- BQ-10: Revenue Share by Sub-Category Within Category
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


-- BQ-11: Ship Mode Performance Analysis
SELECT ship_mode, COUNT(DISTINCT order_id) AS order_count, ROUND(AVG(shipping_days), 2) AS avg_shipping_days, ROUND(SUM(sales), 2) AS total_sales 
FROM orders 
GROUP BY ship_mode 
ORDER BY total_sales DESC;


-- BQ-12: Year-over-Year Sales Growth
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
