# Demand Forecasting & Inventory Optimization Platform

An end-to-end **Supply Chain Analytics and Demand Planning platform** built with Python, SQL, statistical forecasting, inventory optimization, Power BI, and Next.js.

This independent portfolio project demonstrates how a supply chain analyst can move from raw transactional demand data to:

- Demand forecasting
- Forecast model evaluation
- Safety stock calculation
- Reorder point planning
- Economic Order Quantity (EOQ)
- ABC inventory classification
- Stockout-risk identification
- Excess-inventory analysis
- Store and department performance analysis
- Planner-oriented replenishment recommendations
- Executive dashboards

> **Project Type:** Independent Supply Chain Analytics Portfolio Project  
> **Dataset:** Public M5 Forecasting Dataset / Schema-Compatible Sample  
> **Industry Context:** Retail Supply Chain and Demand Planning  
> **Purpose:** Analytics Portfolio, Demonstration, and Interview Project

This repository is **not** work performed for AdventHealth, Capgemini, SAP, Walmart, or any other employer.

---

## Business Problem

Supply chain teams need to balance product availability against excess inventory.

This platform addresses five practical demand-planning and inventory questions:

1. **How much demand should we expect?**
2. **Which forecasting approach performs best on historical holdout data?**
3. **How much safety stock is required for a target service level?**
4. **When should inventory be reordered?**
5. **Which products require planner attention because of stockout risk or excess inventory?**

The project combines statistical forecasting with inventory planning rather than treating forecasting as an isolated machine-learning problem.

---

# Architecture

```text
                    ┌──────────────────────┐
                    │   M5 Raw Dataset     │
                    │ Calendar / Sales /   │
                    │ Sell Prices          │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │ Python Data Pipeline  │
                    │ Ingestion / Cleaning  │
                    │ Validation / Features │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │   SQL Star Schema    │
                    │ Dimensions + Facts   │
                    └──────────┬───────────┘
                               │
                ┌──────────────┴──────────────┐
                ▼                             ▼
      ┌────────────────────┐       ┌────────────────────┐
      │ Forecasting Engine  │       │ Inventory Engine   │
      │                    │       │                    │
      │ Naive              │       │ Safety Stock       │
      │ Moving Average     │       │ Reorder Point      │
      │ Holt-Winters       │       │ EOQ                │
      │ ARIMA              │       │ ABC Classification │
      │ Prophet (optional) │       │ Stockout Risk      │
      └──────────┬─────────┘       │ Excess Inventory   │
                 │                 └──────────┬─────────┘
                 └────────────┬───────────────┘
                              ▼
                    ┌──────────────────────┐
                    │ Power BI + Next.js   │
                    │ Analytics Workbench   │
                    └──────────────────────┘
