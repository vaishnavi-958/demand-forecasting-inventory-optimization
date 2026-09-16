# Demand Forecasting & Inventory Optimization

> End-to-end supply chain analytics platform for demand forecasting, inventory optimization, ABC/EOQ analysis, inventory risk detection, and supply planning.

## 🚀 Live Dashboard

**[Open the Live Dashboard](https://demand-forecasting-inventory-optimization-magxi2nwr-vyshu5.vercel.app/)**

The interactive dashboard provides:

- Executive supply chain overview
- Demand forecast analysis
- Forecast model comparison
- Inventory optimization
- Reorder and expedite recommendations
- ABC classification and EOQ analysis
- Store-level performance
- Inventory risk and excess-stock analysis

## 📂 Source Code

**[View the GitHub Repository](https://github.com/vaishnavi-958/demand-forecasting-inventory-optimization)**

---

## 📌 Project Overview

This project demonstrates an end-to-end supply chain analytics workflow that transforms daily sales data into actionable demand forecasting and inventory planning insights.

The solution combines:

- Python data engineering
- SQL analytics
- Statistical forecasting
- Time-series model evaluation
- Inventory optimization
- Safety stock and reorder point calculations
- ABC classification
- Economic Order Quantity (EOQ)
- Power BI analytics
- Next.js interactive dashboard

The project connects **demand signals, forecasting accuracy, inventory risk, and replenishment decisions** in one analytics workflow.

---

## 🎯 Business Problem

Supply chain organizations need to balance product availability with inventory investment.

Poor demand forecasts can lead to:

- Stockouts
- Excess inventory
- Emergency replenishment
- Higher carrying costs
- Poor service levels
- Inefficient purchasing decisions

This project addresses those challenges by building a pipeline that:

1. Processes historical daily sales data.
2. Evaluates multiple forecasting methods.
3. Selects a champion model based on WMAPE.
4. Calculates safety stock and reorder points.
5. Identifies inventory risk.
6. Classifies SKU/store combinations using ABC analysis.
7. Calculates EOQ using scenario parameters.
8. Generates replenishment recommendations.
9. Presents the results through an interactive dashboard.

---

## 🏗️ Architecture

```text
                    ┌──────────────────────┐
                    │   Historical Sales   │
                    │   Calendar / Prices  │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │   Python ETL /       │
                    │   Data Validation    │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │   Daily Sales Fact  │
                    │   SKU / Store / Date│
                    └──────────┬───────────┘
                               │
                ┌──────────────┴──────────────┐
                │                             │
                ▼                             ▼
       ┌─────────────────┐          ┌──────────────────┐
       │ Forecast Models │          │ Inventory Engine │
       │                 │          │                  │
       │ Naive           │          │ Safety Stock     │
       │ Moving Average  │          │ ROP              │
       │ Holt-Winters    │          │ Risk             │
       │ ARIMA           │          │ Excess Inventory │
       └────────┬────────┘          └─────────┬────────┘
                │                             │
                ▼                             ▼
       ┌─────────────────┐          ┌──────────────────┐
       │ WMAPE / Accuracy│          │ ABC / EOQ        │
       │ Model Selection │          │ Replenishment    │
       └────────┬────────┘          └─────────┬────────┘
                │                             │
                └──────────────┬──────────────┘
                               ▼
                    ┌──────────────────────┐
                    │    SQL Analytics     │
                    │   & Data Extracts    │
                    └──────────┬───────────┘
                               │
                               ▼
                ┌─────────────────────────────┐
                │      Analytics Layer        │
                │                             │
                │ Power BI + Next.js          │
                │ Interactive Dashboard       │
                └─────────────────────────────┘
