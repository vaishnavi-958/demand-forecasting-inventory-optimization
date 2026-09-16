# Forecasting methodology

## Why chronological validation

Random row-level train/test splits are **inappropriate for demand time series**. They leak future promotions, seasonality, and trend into training, and they score the model on dates it would not have known in a live planning cycle.

This project uses a **time-based holdout**:

- Training: all history before the last `VALIDATION_DAYS` (default 28)
- Validation: last 28 days
- Forward forecast: `FORECAST_HORIZON` (default 28) after the last observed date

Rolling-origin evaluation is implemented in `src/forecasting/engine.py` (`rolling_origin_wmape`) for deeper model checks without replacing the primary holdout.

## Models

| Model | Rule | Applied to |
| --- | --- | --- |
| Naive | Last observation carried forward | All eligible series |
| Moving average 7/14/28 | Last in-sample MA carried forward | All eligible series |
| Holt-Winters | Additive trend + weekly seasonality (configurable) | High-value series |
| ARIMA/SARIMA | Configurable order, default (1,1,1)(1,0,1,7) | Expensive-model series |
| Prophet | Weekly seasonality; yearly if ≥ 365 days | Top series, **optional dependency** |

Failed numerical fits fall back to naive and are logged. They are not silently discarded.

## Metrics

- **MAE / RMSE**: scale-dependent; useful within a SKU
- **MAPE**: computed only on strictly positive actuals; NaN if all zeros
- **sMAPE**: bounded denominator `|y| + |ŷ|`
- **WMAPE**: `sum(|y − ŷ|) / sum(|y|)`. If actuals sum to 0: 0 when forecasts are also 0, else 1
- **Forecast Accuracy** = `1 − WMAPE`, clipped to [0, 1], reported as a percentage in the dashboard

WMAPE is the planning-relevant metric: it weights error by volume and remains defined on intermittent demand.

## Selection

Champion model per SKU/store = lowest WMAPE, RMSE as tie-breaker (`config/model_config.yaml`).

Do not quote a global accuracy number that was not produced by `run_insights.json` for that run. The pipeline writes:

- `baseline_accuracy` (mean Naive Forecast Accuracy)
- `best_model_accuracy` (mean champion Forecast Accuracy)
- `improvement_vs_baseline`

## Prophet installation workaround

Prophet depends on `cmdstan` / `cmdstanpy` and frequently fails in constrained environments.

```bash
pip install prophet==1.1.6
```

If that fails on Linux:

```bash
pip install cmdstanpy
python -c "import cmdstanpy; cmdstanpy.install_cmdstan()"
pip install prophet==1.1.6
```

The engine sets `PROPHET_AVAILABLE = False` when import fails and continues with the other models. Do not remove Prophet from the methodology because the optional extra is missing.
