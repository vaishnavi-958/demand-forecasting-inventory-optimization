-- Dimension loads. The Python loader writes these tables from fact_daily_sales.
-- These statements are the documented pattern for a warehouse refresh.

INSERT INTO dim_date (date_key, date, year, quarter, month, week, weekday)
SELECT DISTINCT
    date_key,
    CAST(date AS DATE) AS date,
    year,
    CAST(((month - 1) / 3) + 1 AS INTEGER) AS quarter,
    month,
    CAST(strftime('%W', date) AS INTEGER) AS week, -- SQLite; replace with DATEPART(week, date) on SQL Server / EXTRACT(WEEK FROM date) on PostgreSQL
    weekday
FROM fact_daily_sales
WHERE date_key NOT IN (SELECT date_key FROM dim_date);

INSERT INTO dim_product (product_key, item_id, dept_id, cat_id)
SELECT DISTINCT product_key, item_id, dept_id, cat_id
FROM fact_daily_sales
WHERE item_id NOT IN (SELECT item_id FROM dim_product);

INSERT INTO dim_store (store_key, store_id, state_id)
SELECT DISTINCT store_key, store_id, state_id
FROM fact_daily_sales
WHERE store_id NOT IN (SELECT store_id FROM dim_store);

INSERT INTO dim_department (department_key, dept_id, cat_id)
SELECT DISTINCT department_key, dept_id, cat_id
FROM fact_daily_sales
WHERE dept_id NOT IN (SELECT dept_id FROM dim_department);
