-- Demand analysis: volume, volatility, seasonality, and store/category trends.

-- 1. Top 20 SKUs by sales
WITH sku_sales AS (
    SELECT
        item_id,
        dept_id,
        SUM(sales_units) AS units,
        SUM(revenue) AS revenue,
        AVG(sales_units * 1.0) AS avg_daily_demand,
        STDDEV(sales_units * 1.0) AS demand_std
    FROM fact_daily_sales
    GROUP BY item_id, dept_id
)
SELECT
    item_id,
    dept_id,
    units,
    revenue,
    avg_daily_demand,
    demand_std,
    CASE WHEN avg_daily_demand = 0 THEN NULL ELSE demand_std / avg_daily_demand END AS cv,
    RANK() OVER (ORDER BY revenue DESC) AS revenue_rank
FROM sku_sales
ORDER BY revenue DESC
LIMIT 20;

-- 2. Bottom 20 SKUs by sales
WITH sku_sales AS (
    SELECT item_id, dept_id, SUM(revenue) AS revenue, SUM(sales_units) AS units
    FROM fact_daily_sales
    GROUP BY item_id, dept_id
)
SELECT *
FROM sku_sales
ORDER BY revenue ASC, units ASC
LIMIT 20;

-- 3. SKU demand volatility
SELECT
    item_id,
    store_id,
    dept_id,
    AVG(sales_units * 1.0) AS avg_daily_demand,
    STDDEV(sales_units * 1.0) AS demand_std,
    CASE
        WHEN AVG(sales_units * 1.0) = 0 THEN NULL
        ELSE STDDEV(sales_units * 1.0) / AVG(sales_units * 1.0)
    END AS coefficient_of_variation,
    AVG(CASE WHEN sales_units = 0 THEN 1.0 ELSE 0.0 END) AS zero_sales_pct
FROM fact_daily_sales
GROUP BY item_id, store_id, dept_id
HAVING AVG(sales_units * 1.0) > 0
ORDER BY coefficient_of_variation DESC;

-- 4. Store demand trends (28-day rolling via window)
WITH daily_store AS (
    SELECT
        store_id,
        date_key,
        SUM(sales_units) AS units
    FROM fact_daily_sales
    GROUP BY store_id, date_key
)
SELECT
    store_id,
    date_key,
    units,
    AVG(units) OVER (
        PARTITION BY store_id
        ORDER BY date_key
        ROWS BETWEEN 27 PRECEDING AND CURRENT ROW
    ) AS rolling_28_day_demand
FROM daily_store
ORDER BY store_id, date_key;

-- 5. Category performance
SELECT
    d.cat_id,
    SUM(f.sales_units) AS units,
    SUM(f.revenue) AS revenue,
    AVG(f.sales_units * 1.0) AS avg_daily_units,
    SUM(CASE WHEN f.promotion_flag = 1 THEN f.revenue ELSE 0 END) AS promo_revenue
FROM fact_daily_sales f
JOIN dim_department d ON f.department_key = d.department_key
GROUP BY d.cat_id
ORDER BY revenue DESC;

-- 17. Seasonal demand patterns (day of week / month)
SELECT
    dt.month,
    dt.weekday,
    SUM(f.sales_units) AS units,
    AVG(f.sales_units * 1.0) AS avg_units
FROM fact_daily_sales f
JOIN dim_date dt ON f.date_key = dt.date_key
GROUP BY dt.month, dt.weekday
ORDER BY dt.month, dt.weekday;
