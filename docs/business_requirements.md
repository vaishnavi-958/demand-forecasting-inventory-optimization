# Business requirements

**Project:** Demand Forecasting & Inventory Optimization Platform  
**Type:** Independent Supply Chain Analytics Project using the public M5 Forecasting dataset  
**Audience:** Supply Chain Analyst, Demand Planner, Inventory Analyst, Supply Chain Data Analyst, BI Developer

## Problem

A multi-store retailer manages thousands of SKU/store combinations across food, household, and hobbies categories. Planners need a single analytical workbench that answers operational questions used in demand planning, replenishment, and S&OP:

1. How much will each SKU sell over the next 7 / 14 / 28 days?
2. Which forecasting model is the champion for each series?
3. Which SKUs are at stockout risk, and which are sitting in excess?
4. What should safety stock and reorder point be under a stated service level and lead-time assumption?
5. Which SKUs are A / B / C by annual consumption value?
6. What is the economic order quantity under stated ordering and holding-cost assumptions?
7. Where is forecast error concentrated (store, department, demand segment)?
8. What action should the planner take this cycle?

## In scope

- M5-schema ingestion, validation, and long-format fact build
- Chronological forecast validation (no random train/test split)
- Naive, moving average, Holt-Winters, ARIMA, optional Prophet
- Safety stock, ROP, EOQ, ABC, stockout risk, excess inventory, turns proxy
- Star-schema SQL analytics and Power BI semantic model
- Scenario analysis on service level, lead time, and cost parameters
- Executive dashboard (Power BI design + interactive web workbench)

## Out of scope

- Claiming this work was performed for any employer
- Treating lead time, PO cost, or on-hand as M5 actuals
- Training deep learning models on every SKU
- Automated purchase-order execution in SAP S/4HANA (the outputs are **planner decision support**, analogous to IBP/MRP exception monitors)

## Success criteria

- Pipeline runs from raw files to dashboard extracts with logging and quality gates
- Every KPI is computed (not hardcoded)
- Forecast Accuracy = 1 − WMAPE, with zero-demand safeguards
- Unit tests cover metrics, SS, ROP, EOQ, ABC, validation
- A hiring manager can walk the planner action center and explain each column
