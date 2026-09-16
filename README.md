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
      │ Forecasting Engine │       │ Inventory Engine   │
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
                    │ Analytics Workbench  │
                    └──────────────────────┘
```

Detailed architecture documentation:

[`docs/architecture.md`](docs/architecture.md)

---

# Technology Stack

## Data & Analytics

- Python
- Pandas
- NumPy
- SciPy
- Statsmodels
- Scikit-learn
- SQL
- SQLite
- PostgreSQL-compatible SQL

## Forecasting

- Naive baseline
- Moving Average
- Holt-Winters / Exponential Smoothing
- ARIMA
- Prophet wrapper (optional)

## Supply Chain Analytics

- Demand forecasting
- WMAPE
- Forecast Accuracy
- Safety Stock
- Reorder Point
- Economic Order Quantity (EOQ)
- ABC Classification
- Stockout Risk
- Excess Inventory
- Days of Supply
- Inventory Turns

## Visualization

- Power BI
- Next.js
- React
- TypeScript
- Recharts

## Development

- Git
- GitHub
- Jupyter Notebook
- pytest

---

# Key Results

The following results were produced by the latest successful pipeline run on the schema-compatible sample dataset.

| Metric | Result |
|---|---:|
| SKU / Store series | **120** |
| Historical days | **730** |
| Daily sales fact rows | **87,600** |
| Naive baseline forecast accuracy | **67.6%** |
| Champion-model mean forecast accuracy | **76.9%** |
| Improvement vs baseline | **+9.3 percentage points** |
| Champion WMAPE | **23.1%** |
| ARIMA mean WMAPE | **18.2%** |
| Holt-Winters mean accuracy | **80.1%** |
| Critical inventory exceptions | **3** |
| High-risk inventory exceptions | **6** |
| Recommended expedite/reorder actions | **9** |
| Excess inventory items | **72** |
| Excess inventory value | **~$64.6K** |
| A-class series | **71** |
| B-class series | **24** |
| C-class series | **25** |
| Inventory turns | **16.3x** |

> These figures are calculated from the project's pipeline output and can change when the pipeline is rerun with different data or parameters.

---

# Forecasting Methodology

Forecasting uses a **chronological 28-day holdout** rather than a random train/test split.

Candidate models include:

1. Naive baseline
2. 7-day Moving Average
3. 14-day Moving Average
4. 28-day Moving Average
5. Holt-Winters
6. ARIMA
7. Prophet when the optional dependency is available

Models are evaluated using:

### WMAPE

```text
WMAPE = Σ|Actual − Forecast| / Σ|Actual|
```

### Forecast Accuracy

```text
Forecast Accuracy = 1 − WMAPE
```

The champion model is selected independently for each SKU/store series using the lowest evaluated WMAPE.

The pipeline therefore does **not** assume that one forecasting model is optimal for every product.

Detailed methodology:

[`docs/forecasting_methodology.md`](docs/forecasting_methodology.md)

---

# Forecast Model Results

| Model | Evaluated Series | MAE | RMSE | WMAPE | Accuracy |
|---|---:|---:|---:|---:|---:|
| ARIMA | 16 | 5.30 | 6.92 | **18.2%** | **81.8%** |
| Holt-Winters | 24 | 4.43 | 5.80 | 19.9% | 80.1% |
| Moving Average 28 | 48 | 3.83 | 4.91 | 23.8% | 76.2% |
| Moving Average 14 | 48 | 3.85 | 4.97 | 23.8% | 76.2% |
| Moving Average 7 | 48 | 3.91 | 4.94 | 24.5% | 75.5% |
| Naive | 48 | 5.04 | 6.12 | 32.4% | 67.6% |

The model table represents evaluated model/series combinations.

The **champion model is selected at the SKU/store level**, so the lowest average WMAPE model is not necessarily the champion for every individual series.

---

# Inventory Optimization

The inventory engine converts forecast demand into planning metrics.

## Safety Stock

```text
Safety Stock = Z × σd × √Lead Time
```

Where:

- `Z` = service-level factor
- `σd` = demand standard deviation
- `Lead Time` = assumed supplier lead time

## Reorder Point

```text
ROP = Average Daily Demand × Lead Time + Safety Stock
```

## Economic Order Quantity

EOQ is calculated using scenario ordering and holding-cost parameters.

```text
EOQ = √(2DS / H)
```

Where:

- `D` = annual demand
- `S` = ordering cost
- `H` = annual holding cost per unit

The inventory engine also calculates:

- Days of Supply
- Stockout risk
- Excess inventory
- Inventory turns
- Recommended action

Detailed methodology:

[`docs/inventory_methodology.md`](docs/inventory_methodology.md)

---

# Planner Recommendations

The platform converts inventory conditions into planner-oriented actions:

| Action | Meaning |
|---|---|
| **EXPEDITE** | Critical inventory position requiring urgent attention |
| **REORDER** | Inventory position indicates replenishment is required |
| **MONITOR** | Continue monitoring demand and inventory |
| **REDUCE INVENTORY** | Excess inventory identified |
| **NO ACTION** | No immediate planning action |

For the current pipeline run:

- **3** items are classified as critical / expedite.
- **6** additional items are classified as high-risk / reorder.
- **9** total expedite/reorder recommendations are generated.

The planner page allows scenario parameters to be adjusted and evaluates how inventory recommendations change.

---

# ABC Inventory Analysis

ABC classification is based on cumulative annual consumption value.

```text
Annual Consumption Value
= Annual Demand × Unit Cost Proxy
```

Current pipeline results:

| Class | SKU / Store Series |
|---|---:|
| A | **71** |
| B | **24** |
| C | **25** |
| **Total** | **120** |

The A-class population represents approximately **79.5% of annual consumption value** in the current run.

The ABC analysis supports prioritization of inventory management effort toward higher-value demand streams.

---

# Dashboard

The project includes an interactive **Next.js supply-chain analytics workbench**.

## Dashboard Pages

### Overview

Executive-level view of:

- Total sales
- Forecast accuracy
- WMAPE
- Inventory turns
- Stockout risk
- Excess inventory
- A-class share
- Recommended orders
- Revenue trends
- Risk and excess-inventory summaries

### Forecast

Provides:

- Forecast performance by model
- SKU/store forecast selection
- Chronological holdout results
- Actual vs forecast analysis
- WMAPE and forecast accuracy

### Inventory

Provides:

- Critical inventory exceptions
- Excess inventory
- Days of Supply
- Inventory risk
- Recommended planning actions

### ABC / EOQ

Provides:

- ABC classification
- Pareto analysis
- EOQ
- Inventory position
- Reorder Point
- Safety Stock

### Stores

Provides:

- Store-level forecast accuracy
- WMAPE
- Critical exceptions
- Excess inventory
- Days of Supply
- Category revenue

### Planner

Provides:

- Recommended action
- Recommended order quantity
- Safety stock
- Reorder point
- Days of Supply
- Scenario planning

---

# Data & Assumptions

The project is based on the public **M5 Forecasting dataset**.

M5 provides historical sales, calendar information, and selling-price information, but it does not provide a complete supplier inventory ledger containing operational on-hand balances and supplier lead times.

Therefore:

> **Lead time, on-hand inventory, ordering cost, and holding cost are analytical assumptions / scenario parameters.**

The inventory position should be interpreted as a **scenario proxy**, not retailer-reported operational inventory.

The project does not claim that its inventory recommendations represent actual Walmart replenishment decisions.

Official M5 dataset:

https://www.kaggle.com/competitions/m5-forecasting-accuracy/data

---

# Quick Start

## 1. Clone the repository

```bash
git clone https://github.com/vaishnavi-958/demand-forecasting-inventory-optimization.git
cd demand-forecasting-inventory-optimization
```

## 2. Create a Python environment

Python **3.12** is recommended.

### Windows

```powershell
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1
```

### Linux / macOS

```bash
python3.12 -m venv .venv
source .venv/bin/activate
```

## 3. Install Python dependencies

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## 4. Run the pipeline

```bash
python scripts/run_pipeline.py
```

If official M5 files are not present, the project can generate a schema-compatible synthetic sample for demonstration.

The synthetic sample is **not Walmart operational data**.

---

# Optional M5 Data

To run against the official M5 files, place the following files inside:

```text
data/raw/
```

```text
calendar.csv
sales_train_validation.csv
sell_prices.csv
```

The raw M5 files are intentionally excluded from GitHub.

Run:

```bash
python scripts/run_pipeline.py
```

The pipeline performs:

```text
Raw Data
   ↓
Validation
   ↓
Cleaning
   ↓
Feature Engineering
   ↓
Daily Sales Fact
   ↓
Forecast Evaluation
   ↓
Inventory Optimization
   ↓
SQL Tables
   ↓
Dashboard Extracts
```

---

# Run Tests

Run:

```bash
python -m pytest tests -q
```

The test suite covers:

- WMAPE
- Forecast accuracy
- Zero-demand edge cases
- Safety stock
- Reorder point
- EOQ
- ABC classification
- Inventory calculations
- Data-quality validation

---

# Run the Next.js Dashboard

Navigate to the web application:

```bash
cd web
```

Install dependencies:

```bash
npm install
```

Start the development server:

```bash
npm run dev
```

Then open:

```text
http://localhost:43125
```

To verify the production build:

```bash
npm run build
```

---

# Power BI

The repository also contains Power BI design and modeling documentation.

See:

[`dashboard/powerbi/`](dashboard/powerbi/)

Documentation includes:

- Data model
- DAX measures
- Dashboard design
- Power BI semantic model
- Analyst views

The pipeline generates Power BI-ready extracts under:

```text
data/processed/powerbi/
```

---

# Repository Structure

```text
demand-forecasting-inventory-optimization/
│
├── config/
│   ├── config.yaml
│   └── model_config.yaml
│
├── dashboard/
│   ├── powerbi/
│   └── screenshots/
│
├── data/
│   ├── raw/
│   ├── processed/
│   └── external/
│
├── docs/
│   ├── architecture.md
│   ├── business_requirements.md
│   ├── data_dictionary.md
│   ├── forecasting_methodology.md
│   ├── inventory_methodology.md
│   ├── interview_guide.md
│   └── sql_documentation.md
│
├── notebooks/
│   ├── 01_data_exploration.ipynb
│   ├── 02_data_cleaning.ipynb
│   ├── 03_demand_analysis.ipynb
│   ├── 04_forecasting_baseline.ipynb
│   ├── 05_holt_winters_forecasting.ipynb
│   ├── 06_prophet_forecasting.ipynb
│   ├── 07_model_comparison.ipynb
│   ├── 08_inventory_optimization.ipynb
│   └── 09_final_analysis.ipynb
│
├── scripts/
│   ├── run_pipeline.py
│   ├── run_forecasts.py
│   ├── generate_dashboard_data.py
│   └── setup_database.py
│
├── sql/
│   ├── 01_create_schema.sql
│   ├── 02_create_tables.sql
│   ├── 03_load_dimensions.sql
│   ├── 04_load_fact_sales.sql
│   ├── 05_demand_analysis.sql
│   ├── 06_inventory_analysis.sql
│   ├── 07_forecast_metrics.sql
│   ├── 08_abc_analysis.sql
│   ├── 09_stockout_risk.sql
│   └── 10_powerbi_views.sql
│
├── src/
│   ├── data/
│   ├── database/
│   ├── features/
│   ├── forecasting/
│   ├── inventory/
│   └── utils/
│
├── tests/
│
├── web/
│   └── Next.js dashboard
│
├── .env.example
├── .gitignore
├── LICENSE
├── Makefile
├── pyproject.toml
├── requirements.txt
└── README.md
```

---

# Data Quality & Reproducibility

The pipeline performs validation checks before downstream analytics.

Examples include:

- Required source-file validation
- Daily-column validation
- Date-range validation
- Duplicate checks
- Missing-value checks
- Fact-table validation
- SKU/store series validation
- Forecast evaluation validation

The project intentionally computes metrics from pipeline outputs instead of hardcoding portfolio numbers.

---

# Forecast Integrity

Accuracy is calculated from evaluated forecasts.

```text
Forecast Accuracy = 1 − WMAPE
```

The pipeline records run-level metrics in:

```text
data/processed/run_insights.json
```

This includes values such as:

```text
baseline_accuracy
best_model_accuracy
improvement_vs_baseline
```

Results can change when:

- The dataset changes
- Forecast horizon changes
- Model parameters change
- Inventory assumptions change
- The number of forecasted series changes

---

# Important Interpretation Notes

### Forecast Accuracy

The reported **76.9%** is the mean champion-model accuracy from the current sample run.

It should not be interpreted as a guaranteed future forecasting accuracy.

### Inventory Turns

The current **16.3x inventory turns** figure is a scenario calculation based on the project's inventory proxy.

### Excess Inventory

The approximately **$64.6K** excess value is based on scenario on-hand inventory and a unit-price/cost proxy.

### Stockout Risk

The **7.5% critical + high share** represents the share of SKU/store series classified as critical or high under the project's scenario rules.

These metrics are analytical outputs, not retailer-reported operational KPIs.

---

# Future Improvements

Potential extensions include:

- Full M5 dataset benchmarking
- Hierarchical forecasting
- Intermittent-demand forecasting
- Promotion and event features
- Gradient boosting models
- LightGBM / XGBoost forecasting
- Automated hyperparameter tuning
- Supplier-specific lead-time distributions
- Service-level optimization
- Multi-echelon inventory optimization
- Real-time ERP integration
- Automated Power BI refresh
- Cloud deployment
- Planner approval workflow
- Scenario comparison and export

---

# Interview Talking Points

This project demonstrates experience with:

## Supply Chain

- Demand planning
- Forecasting
- Inventory optimization
- Replenishment
- Safety stock
- Reorder Point
- EOQ
- ABC analysis
- Stockout risk
- Excess inventory
- S&OP-style planning

## Analytics

- SQL
- Python
- Statistical forecasting
- KPI development
- Data validation
- Business rules
- Scenario analysis
- Power BI

## Software Engineering

- Modular Python architecture
- Automated data pipeline
- Unit testing
- Next.js / React
- TypeScript
- Git / GitHub
- Reproducible analytics workflow

---

# License

MIT.

The M5 dataset remains subject to its own competition and dataset terms.

---

## Author

**Yellasiri Naga Vaishnavi**

Supply Chain Analytics | Demand Planning | Inventory Optimization | Data Analytics

GitHub:

https://github.com/vaishnavi-958
