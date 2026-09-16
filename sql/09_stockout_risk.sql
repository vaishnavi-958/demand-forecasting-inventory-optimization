-- Stockout risk and excess inventory exposure.

-- 6 / 12. Stockout-risk SKUs
SELECT
    item_id,
    store_id,
    dept_id,
    stockout_risk,
    current_inventory,
    reorder_point,
    safety_stock,
    days_of_supply,
    recommended_action
FROM fact_inventory_optimization
WHERE stockout_risk IN ('CRITICAL', 'HIGH')
ORDER BY
    CASE stockout_risk WHEN 'CRITICAL' THEN 1 WHEN 'HIGH' THEN 2 ELSE 3 END,
    days_of_supply ASC;

-- 11. Excess inventory exposure
SELECT
    cat_id,
    store_id,
    SUM(CASE WHEN excess_inventory_flag THEN excess_units ELSE 0 END) AS excess_units,
    SUM(CASE WHEN excess_inventory_flag THEN excess_value ELSE 0 END) AS excess_value,
    COUNT(*) FILTER (WHERE excess_inventory_flag) AS excess_sku_count
FROM fact_inventory_optimization
GROUP BY cat_id, store_id
ORDER BY excess_value DESC;

SELECT
    stockout_risk,
    COUNT(*) AS sku_store_count,
    AVG(days_of_supply) AS avg_dos,
    SUM(excess_value) AS excess_value
FROM fact_inventory_optimization
GROUP BY stockout_risk
ORDER BY CASE stockout_risk
    WHEN 'CRITICAL' THEN 1
    WHEN 'HIGH' THEN 2
    WHEN 'MEDIUM' THEN 3
    ELSE 4
END;
