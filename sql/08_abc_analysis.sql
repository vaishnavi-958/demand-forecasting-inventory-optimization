-- ABC classification analytics.

-- 7 / 15. High-value A-class SKUs
SELECT
    item_id,
    store_id,
    dept_id,
    annual_demand,
    unit_cost,
    annual_consumption_value,
    cumulative_value_pct,
    abc_class
FROM fact_abc_classification
WHERE abc_class = 'A'
ORDER BY annual_consumption_value DESC;

SELECT
    abc_class,
    COUNT(*) AS sku_store_count,
    SUM(annual_consumption_value) AS value,
    SUM(annual_consumption_value) * 1.0 / SUM(SUM(annual_consumption_value)) OVER () AS value_share,
    COUNT(*) * 1.0 / SUM(COUNT(*)) OVER () AS sku_share
FROM fact_abc_classification
GROUP BY abc_class
ORDER BY abc_class;
