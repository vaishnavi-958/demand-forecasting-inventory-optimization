# Power BI data model

Star schema. Hide foreign keys; expose names from dimensions.

## Tables

Import from `data/processed/powerbi/`:

- dim_date (or create a Date table from `fact_daily_sales[date]`)
- dim_product
- dim_store
- dim_department
- fact_daily_sales
- fact_forecast
- fact_inventory_optimization
- fact_model_metrics
- fact_abc_classification

If CSV extracts are denormalized (Python export), still **model** them as a star: split product/store/dept or mark relationships on `item_id` / `store_id` / `date`.

## Relationships (single direction, one-to-many)

| From | To | Key | Cardinality |
| --- | --- | --- | --- |
| dim_date | fact_daily_sales | date_key | 1:* |
| dim_product | fact_daily_sales | item_id | 1:* |
| dim_store | fact_daily_sales | store_id | 1:* |
| dim_department | fact_daily_sales | dept_id | 1:* |
| dim_date | fact_forecast | date | 1:* |
| dim_product | fact_forecast | item_id | 1:* |
| dim_store | fact_forecast | store_id | 1:* |
| dim_product | fact_inventory_optimization | item_id | 1:* |
| dim_store | fact_inventory_optimization | store_id | 1:* |
| dim_product | fact_model_metrics | item_id | 1:* |
| dim_store | fact_model_metrics | store_id | 1:* |
| dim_product | fact_abc_classification | item_id | 1:* |
| dim_store | fact_abc_classification | store_id | 1:* |

Do **not** relate fact_forecast to fact_daily_sales directly (many-to-many at date×SKU). Both filter through dimensions.

Inactive relationship option: a second date role for "forecast date" vs "actual date" if you split the forecast table. Default model uses one date table.

## Cross-filter

Keep `both` off except dim_department → dim_product if you create a snowflake. Prefer flattening cat_id onto dim_product to avoid snowflake complexity.
