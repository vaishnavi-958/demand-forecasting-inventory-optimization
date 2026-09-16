# SQL documentation

Scripts in `sql/` are **PostgreSQL-first**. The local pipeline loads tables with SQLAlchemy (SQLite by default). Use these files in interviews to show analyst-level SQL: CTEs, window functions, CASE, and star-schema joins.

| File | Purpose |
| --- | --- |
| 01_create_schema.sql | `supply_chain` schema |
| 02_create_tables.sql | Star schema DDL + PKs |
| 03_load_dimensions.sql | Dimension load pattern |
| 04_load_fact_sales.sql | Fact reconciliation query |
| 05_demand_analysis.sql | Top/bottom SKUs, CV, store rolling demand, category, seasonality |
| 06_inventory_analysis.sql | Turns proxy, reorder queue, coverage |
| 07_forecast_metrics.sql | Accuracy by model/dept, bias, poor performers |
| 08_abc_analysis.sql | A-class list and value vs count mix |
| 09_stockout_risk.sql | Risk queue and excess exposure |
| 10_powerbi_views.sql | Executive KPI and planner views |

## SQL Server notes

- `SERIAL` / `DOUBLE PRECISION` → `INT IDENTITY` / `FLOAT`
- `CREATE SCHEMA` is supported
- `strftime` in the SQLite comment on dim_date week → `DATEPART(week, date)`
- `COUNT(*) FILTER (WHERE ...)` → `SUM(CASE WHEN ... THEN 1 ELSE 0 END)`
- `BOOLEAN` → `BIT`

## Relationships

```
dim_date[date_key]          1 --- * fact_daily_sales
dim_product[product_key]    1 --- * fact_daily_sales
dim_store[store_key]        1 --- * fact_daily_sales
dim_department[department_key] 1 --- * fact_daily_sales

dim_product.item_id         1 --- * fact_forecast
dim_store.store_id          1 --- * fact_forecast
dim_product.item_id         1 --- * fact_inventory_optimization
dim_product.item_id         1 --- * fact_abc_classification
dim_product.item_id         1 --- * fact_model_metrics
```

Avoid many-to-many. Bridge tables are unnecessary at this grain.
