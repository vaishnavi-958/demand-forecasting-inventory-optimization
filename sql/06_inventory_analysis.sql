-- Inventory analysis: turns proxy, coverage, reorder recommendations, excess.

-- 13. Inventory turns proxy (COGS proxy / average inventory value proxy)
SELECT
    cat_id,
    SUM(cogs_proxy) AS cogs_proxy,
    SUM(average_inventory_value_proxy) AS avg_inventory_value_proxy,
    CASE
        WHEN SUM(average_inventory_value_proxy) = 0 THEN NULL
        ELSE SUM(cogs_proxy) / SUM(average_inventory_value_proxy)
    END AS inventory_turns_proxy
FROM fact_inventory_optimization
GROUP BY cat_id
ORDER BY inventory_turns_proxy DESC;

-- 14. Reorder recommendations
SELECT
    item_id,
    store_id,
    dept_id,
    abc_class,
    avg_daily_demand,
    safety_stock,
    reorder_point,
    current_inventory,
    days_of_supply,
    recommended_action
FROM fact_inventory_optimization
WHERE recommended_action IN ('EXPEDITE', 'REORDER')
ORDER BY
    CASE recommended_action WHEN 'EXPEDITE' THEN 1 ELSE 2 END,
    reorder_point - current_inventory DESC;

-- Coverage vs target
SELECT
    dept_id,
    COUNT(*) AS sku_store_count,
    AVG(days_of_supply) AS avg_days_of_supply,
    AVG(safety_stock) AS avg_safety_stock,
    AVG(reorder_point) AS avg_reorder_point,
    SUM(CASE WHEN days_of_supply < lead_time_days THEN 1 ELSE 0 END) AS below_lead_time_coverage
FROM fact_inventory_optimization
GROUP BY dept_id
ORDER BY below_lead_time_coverage DESC;
