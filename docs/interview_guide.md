# Interview guide

Independent Supply Chain Analytics Project using the public M5 Forecasting dataset.

Use this walkthrough in Supply Chain Analyst, Demand Planner, Inventory Analyst, Supply Chain Data Analyst, or BI interviews. Do **not** attribute the project to AdventHealth, Capgemini, SAP, Walmart, or any employer.

## 60-second pitch

"I built an independent demand-planning and inventory-optimization workbench on the public M5 schema. It takes daily SKU/store sales, runs chronological forecast benchmarks, then converts demand uncertainty into safety stock, reorder point, EOQ, and ABC so a planner can see who to expedite, reorder, or destock. Lead time and cost are explicit scenario parameters because M5 does not contain them."

## What happened / what will happen / why / what to do

| Question | Where to show it |
| --- | --- |
| What happened? | Executive page: sales trend, category mix |
| What is likely to happen? | Forecast vs actual holdout + 28-day forward champion forecast |
| Why? | WMAPE by department, demand segments (intermittent vs smooth), store scorecard |
| What should we do? | Planner action center |

## Talking points that match a planning resume

- **Demand planning:** statistical baseline vs Holt-Winters/ARIMA, WMAPE, bias, intermittent demand (ADI/CV²)
- **Inventory / MRP-DRP thinking:** SS = Zσ√LT, ROP, days of supply, exception messages (expedite/reorder)
- **S&OP:** service-level scenarios, ABC focus for A-class service
- **SQL / Power BI:** star schema, DAX measures, planner workbench
- **Root cause:** forecast error concentrated in high-CV or hobbies/intermittent series — *only say this if `run_insights.json` shows it for your run*

## Questions you should be ready for

**Why not MAPE as the headline KPI?**  
Daily retail demand is often zero. MAPE is undefined. WMAPE weights by volume and is the S&OP-friendly metric. Accuracy = 1 − WMAPE.

**Why not random train/test?**  
It leaks the future. Planners only know history at freeze. We hold out the last 28 days.

**Is lead time in the dataset?**  
No. It is a documented assumption by department, same way an analyst would scenario IBP lead times.

**Did you reduce excess by 15%?**  
No. This sample run reports computed excess exposure (~$64.6k on scenario on-hand), not a claimed savings percentage.

**What accuracy did you achieve?**  
On the sample run: naive baseline **67.6%**, champion mean **76.9%** (Forecast Accuracy = 1 − WMAPE). ARIMA had the lowest mean WMAPE on the high-value subset it was assigned. Re-run the pipeline on full M5 before quoting any other number.

**How would this land next to SAP IBP / S/4?**  
Key figure mapping: consensus demand → forecast; safety stock / ROP → IBP inventory optimization or MRP type; ABC → MRP controller focus; planner actions → exception monitor. This repo does not connect to a live SAP system.

## Demo path (8 minutes)

1. README + architecture mermaid  
2. `config/config.yaml` parameters  
3. `python scripts/run_pipeline.py` log (or processed outputs)  
4. `model_metrics.csv` champion vs naive  
5. Inventory table: pick a CRITICAL SKU and compute ROP on the whiteboard  
6. Power BI spec or web dashboard planner page  
7. Change service level in the scenario panel and watch SS move
