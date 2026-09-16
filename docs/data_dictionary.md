# Data dictionary

Grain of `fact_daily_sales`: one row per **item_id × store_id × date**.

## Dimensions

### dim_date

| Column | Type | Definition |
| --- | --- | --- |
| date_key | int YYYYMMDD | Surrogate / degenerate date key |
| date | date | Calendar date |
| year, quarter, month, week, weekday | int / text | Time hierarchy for S&OP views |

### dim_product

| Column | Type | Definition |
| --- | --- | --- |
| product_key | int | Surrogate key |
| item_id | text | SKU (M5 `item_id`) |
| dept_id | text | Department |
| cat_id | text | Category (FOODS / HOUSEHOLD / HOBBIES) |

### dim_store

| Column | Type | Definition |
| --- | --- | --- |
| store_key | int | Surrogate key |
| store_id | text | Store |
| state_id | text | Region (CA / TX / WI in M5) |

### dim_department

| Column | Type | Definition |
| --- | --- | --- |
| department_key | int | Surrogate key |
| dept_id | text | Department |
| cat_id | text | Parent category |

## Facts

### fact_daily_sales

| Column | Definition |
| --- | --- |
| date_key, product_key, store_key, department_key | Star keys |
| sales_units | Daily unit demand |
| price | Sell price (joined from weekly `sell_prices`) |
| revenue | units × price |
| promotion_flag | 1 if calendar event present that day |
| snap_flag | SNAP day for the store's state |

### fact_forecast

| Column | Definition |
| --- | --- |
| date | Forecast or validation date |
| item_id, store_id, model | Series and method |
| forecast, forecast_lower, forecast_upper | Point and optional interval |
| actual | Populated on the holdout window only |
| is_selected_model | Champion model flag |

### fact_model_metrics

| Column | Definition |
| --- | --- |
| MAE, RMSE, MAPE, sMAPE, WMAPE | Holdout error metrics |
| Forecast_Accuracy | 1 − WMAPE, clipped to [0, 1] |
| rank | 1 = best WMAPE for that SKU/store |

### fact_inventory_optimization

See `docs/inventory_methodology.md`. Notable fields: `avg_daily_demand`, `lead_time_days` (assumption), `safety_stock`, `reorder_point`, `current_inventory` (scenario proxy), `days_of_supply`, `stockout_risk`, `excess_*`, `eoq`, `abc_class`, `recommended_action`, `inventory_turns_proxy`.

### fact_abc_classification

Annual consumption value = annual demand × unit-cost proxy; cumulative value %; ABC class.

## Raw M5 files

| File | Grain |
| --- | --- |
| calendar.csv | date / `d` label |
| sales_train_validation.csv | series (wide `d_1..d_n`) |
| sell_prices.csv | store × item × `wm_yr_wk` |
