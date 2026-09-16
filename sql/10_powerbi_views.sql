-- Power BI-oriented views. PostgreSQL CREATE VIEW syntax; SQL Server equivalent is the same
-- aside from FILTER (WHERE ...) which becomes CASE SUM.

CREATE VIEW IF NOT EXISTS vw_exec_kpis AS
SELECT
    (SELECT SUM(revenue) FROM fact_daily_sales) AS total_sales,
    (SELECT AVG(Forecast_Accuracy) FROM fact_model_metrics WHERE rank = 1) AS forecast_accuracy,
    (SELECT AVG(WMAPE) FROM fact_model_metrics WHERE rank = 1) AS wmape,
    (SELECT AVG(inventory_turns_proxy) FROM fact_inventory_optimization) AS inventory_turns,
    (SELECT AVG(CASE WHEN stockout_risk IN ('CRITICAL', 'HIGH') THEN 1.0 ELSE 0.0 END)
        FROM fact_inventory_optimization) AS stockout_risk_pct,
    (SELECT SUM(excess_value) FROM fact_inventory_optimization) AS excess_inventory_value,
    (SELECT AVG(CASE WHEN abc_class = 'A' THEN 1.0 ELSE 0.0 END)
        FROM fact_inventory_optimization) AS a_class_sku_pct,
    (SELECT SUM(CASE WHEN recommended_action IN ('EXPEDITE', 'REORDER') THEN 1 ELSE 0 END)
        FROM fact_inventory_optimization) AS recommended_orders;

CREATE VIEW IF NOT EXISTS vw_planner_action_center AS
SELECT
    i.item_id,
    i.store_id,
    i.dept_id,
    i.abc_class,
    m.model AS best_model,
    m.Forecast_Accuracy,
    i.current_inventory,
    i.safety_stock,
    i.reorder_point,
    i.days_of_supply,
    i.stockout_risk,
    i.excess_value,
    i.recommended_action
FROM fact_inventory_optimization i
LEFT JOIN fact_model_metrics m
  ON i.item_id = m.item_id
 AND i.store_id = m.store_id
 AND m.rank = 1;

CREATE VIEW IF NOT EXISTS vw_store_scorecard AS
SELECT
    store_id,
    COUNT(*) AS sku_count,
    AVG(Forecast_Accuracy) AS forecast_accuracy,
    SUM(CASE WHEN stockout_risk = 'CRITICAL' THEN 1 ELSE 0 END) AS critical_skus,
    SUM(excess_value) AS excess_value,
    AVG(days_of_supply) AS avg_days_of_supply
FROM fact_inventory_optimization
GROUP BY store_id;
