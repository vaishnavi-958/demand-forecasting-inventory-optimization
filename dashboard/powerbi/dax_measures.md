# DAX measures

Create a `_Measures` table. Format Accuracy / WMAPE as %; currency as $; units as #,##0.0.

```dax
Total Sales =
SUM ( fact_daily_sales[revenue] )
```

```dax
Total Units =
SUM ( fact_daily_sales[sales_units] )
```

```dax
Average Daily Demand =
AVERAGE ( fact_inventory_optimization[avg_daily_demand] )
```

```dax
WMAPE =
AVERAGE ( fact_model_metrics[WMAPE] )
```

Use the champion model in report-level visuals:

```dax
WMAPE (Champion) =
CALCULATE (
    AVERAGE ( fact_model_metrics[WMAPE] ),
    fact_model_metrics[rank] = 1
)
```

```dax
Forecast Accuracy =
CALCULATE (
    AVERAGE ( fact_model_metrics[Forecast_Accuracy] ),
    fact_model_metrics[rank] = 1
)
```

```dax
MAPE =
CALCULATE (
    AVERAGE ( fact_model_metrics[MAPE] ),
    fact_model_metrics[rank] = 1
)
```

```dax
Forecast Bias =
VAR Actuals = CALCULATE ( SUM ( fact_forecast[actual] ), NOT ISBLANK ( fact_forecast[actual] ) )
VAR Forecasts = CALCULATE ( SUM ( fact_forecast[forecast] ), NOT ISBLANK ( fact_forecast[actual] ) )
RETURN
IF ( Actuals = 0, BLANK (), ( Forecasts - Actuals ) / Actuals )
```

```dax
Inventory Turns =
AVERAGE ( fact_inventory_optimization[inventory_turns_proxy] )
```

```dax
Stockout Risk % =
AVERAGEX (
    fact_inventory_optimization,
    IF ( fact_inventory_optimization[stockout_risk] IN { "CRITICAL", "HIGH" }, 1, 0 )
)
```

```dax
Excess Inventory Value =
SUM ( fact_inventory_optimization[excess_value] )
```

```dax
A-Class Inventory % =
AVERAGEX (
    fact_inventory_optimization,
    IF ( fact_inventory_optimization[abc_class] = "A", 1, 0 )
)
```

```dax
Days of Supply =
AVERAGE ( fact_inventory_optimization[days_of_supply] )
```

```dax
Recommended Order Count =
CALCULATE (
    COUNTROWS ( fact_inventory_optimization ),
    fact_inventory_optimization[recommended_order_flag] = TRUE ()
)
```

If the flag is stored as 1/0:

```dax
Recommended Order Count =
SUM ( fact_inventory_optimization[recommended_order_flag] )
```

```dax
Average Safety Stock =
AVERAGE ( fact_inventory_optimization[safety_stock] )
```

```dax
Average Reorder Point =
AVERAGE ( fact_inventory_optimization[reorder_point] )
```

```dax
Baseline Accuracy =
CALCULATE (
    AVERAGE ( fact_model_metrics[Forecast_Accuracy] ),
    fact_model_metrics[model] = "Naive"
)
```

```dax
Accuracy Improvement vs Baseline =
[Forecast Accuracy] - [Baseline Accuracy]
```

Conditional formatting rules (not DAX): CRITICAL red, HIGH amber, MEDIUM gold, LOW green on `stockout_risk`.
