-- Forecast KPIs: accuracy by model, department, bias, and poor performers.

-- 8. Forecast accuracy by model
SELECT
    model,
    AVG(MAE) AS mae,
    AVG(RMSE) AS rmse,
    AVG(MAPE) AS mape,
    AVG(sMAPE) AS smape,
    AVG(WMAPE) AS wmape,
    AVG(Forecast_Accuracy) AS forecast_accuracy,
    COUNT(*) AS series_count
FROM fact_model_metrics
GROUP BY model
ORDER BY wmape ASC;

-- 9. Forecast accuracy by department (best model per series)
SELECT
    dept_id,
    AVG(WMAPE) AS wmape,
    AVG(Forecast_Accuracy) AS forecast_accuracy,
    COUNT(*) AS series_count
FROM fact_model_metrics
WHERE rank = 1
GROUP BY dept_id
ORDER BY wmape DESC;

-- 10. Forecast bias (from fact_forecast holdout rows where actual is present)
SELECT
    model,
    dept_id,
    AVG(forecast - actual) AS mean_bias,
    SUM(forecast - actual) * 1.0 / NULLIF(SUM(actual), 0) AS pct_bias
FROM fact_forecast
WHERE actual IS NOT NULL
GROUP BY model, dept_id
ORDER BY ABS(SUM(forecast - actual) * 1.0 / NULLIF(SUM(actual), 0)) DESC;

-- 16. Poor forecast performers (best model still weak)
SELECT
    item_id,
    store_id,
    dept_id,
    model,
    WMAPE,
    Forecast_Accuracy,
    MAE
FROM fact_model_metrics
WHERE rank = 1
  AND Forecast_Accuracy < 0.70
ORDER BY Forecast_Accuracy ASC, WMAPE DESC;
