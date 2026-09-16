-- Fact sales is populated by src/database/loaders.py.
-- Use this pattern when landing a staged extract into PostgreSQL.

-- COPY supply_chain.fact_daily_sales
-- FROM '/data/processed/powerbi/fact_daily_sales.csv'
-- WITH (FORMAT csv, HEADER true);

SELECT
    COUNT(*) AS fact_rows,
    COUNT(DISTINCT item_id) AS sku_count,
    COUNT(DISTINCT store_id) AS store_count,
    MIN(date_key) AS min_date_key,
    MAX(date_key) AS max_date_key,
    SUM(sales_units) AS total_units,
    SUM(revenue) AS total_revenue
FROM fact_daily_sales;
