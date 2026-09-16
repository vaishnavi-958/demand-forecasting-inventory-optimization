# Data directory

This project uses the **public M5 Forecasting Accuracy** dataset (Walmart, via the M5 competition).

## Independent project statement

This is an **independent supply chain analytics project using the public M5 Forecasting dataset**.
It is not affiliated with Walmart, AdventHealth, Capgemini, SAP, or any employer.

Lead times, ordering costs, holding costs, and on-hand inventory **do not exist** in M5.
They are labeled throughout the code as **analytical assumptions / scenario parameters**.

## Expected raw files (`data/raw/`)

Download from the official Kaggle competition (requires a Kaggle account):

https://www.kaggle.com/competitions/m5-forecasting-accuracy/data

Place these files in `data/raw/`:

- `calendar.csv`
- `sales_train_validation.csv`
- `sell_prices.csv`

If filenames differ, set them in `config/config.yaml` under `paths`.

**Do not commit the raw M5 dataset.** `.gitignore` blocks it.

## Sample data (schema-compatible)

If the raw files are missing, `python scripts/run_pipeline.py` generates a **synthetic M5-schema sample**:

```bash
python scripts/generate_sample_data.py
```

The sample is for demonstration and testing. It is **not** Walmart operational data.

## Processed outputs (`data/processed/`)

Created by the pipeline:

- `fact_daily_sales.parquet`
- `demand_profile.parquet`
- `forecast_evaluation.parquet`
- `fact_forecast.parquet`
- `model_metrics.csv`
- `fact_inventory_optimization.csv`
- `run_insights.json`
- `powerbi/*.csv`
- `supply_chain.db` (SQLite default)
