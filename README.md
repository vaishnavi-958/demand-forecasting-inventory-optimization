# Demand Forecasting & Inventory Optimization Platform

Independent Supply Chain Analytics Project using the public M5 Forecasting dataset.

This repository is a production-style **demand planning + inventory optimization** workbench for a Supply Chain Analyst, Demand Planner, Inventory Analyst, or Supply Chain Data Analyst interview. It is **not** a generic machine-learning portfolio, and it is **not** work performed for AdventHealth, Capgemini, SAP, Walmart, or any employer.

It answers the questions a replenishment / S&OP team actually asks:

- How much will each SKU sell over the next 7 / 14 / 28 days?
- Which statistical forecast beats a naive baseline on a chronological holdout?
- What safety stock and reorder point follow from a stated service level and lead-time assumption?
- Which SKUs are A/B/C, what is EOQ, who is at stockout risk, and where is excess sitting?
- What should the planner do this cycle: expedite, reorder, monitor, or reduce inventory?

## Architecture

See [`docs/architecture.md`](docs/architecture.md) for the mermaid diagram.

Raw M5 (or schema-compatible sample) → Python DQ & feature engineering → star schema → forecast engine (Naive, MA, Holt-Winters, ARIMA, optional Prophet) → inventory engine (SS, ROP, EOQ, ABC, risk) → Power BI semantic model + executive web workbench.

## Quick start

```bash
python -m pip install -r requirements.txt
python scripts/run_pipeline.py
```

If `data/raw/` does not contain the official M5 files, the pipeline generates a **synthetic M5-schema sample**. That sample is for demonstration. It is not Walmart operational data.

Official M5 download (Kaggle account required):  
https://www.kaggle.com/competitions/m5-forecasting-accuracy/data  

Place `calendar.csv`, `sales_train_validation.csv`, and `sell_prices.csv` in `data/raw/`. Do not commit them.

```bash
python -m pytest tests -q
cd web && npm install && npm run dev
```

Power BI Desktop: import CSVs from `data/processed/powerbi/` and follow [`dashboard/powerbi/`](dashboard/powerbi/).

## Configuration

Business parameters live in [`config/config.yaml`](config/config.yaml) and [`config/model_config.yaml`](config/model_config.yaml):

- `FORECAST_HORIZON`, `MAX_FORECAST_SKUS`, `MIN_HISTORY_DAYS`
- Service level, department lead times, ordering cost, holding-cost rate
- ABC cutoffs and stockout / excess thresholds

Lead time, on-hand inventory, ordering cost, and holding cost are **analytical assumptions / scenario parameters**. M5 does not contain supplier lead time or a stock ledger.

## Forecast integrity

Accuracy is **computed**, never hardcoded.

- Forecast Accuracy = 1 − WMAPE
- Pipeline writes `data/processed/run_insights.json` with `baseline_accuracy`, `best_model_accuracy`, and `improvement_vs_baseline`
- Do not quote “87% accuracy” or “15% excess reduction” unless that file (or a scenario run) produced the number

## Repository map

| Path | Contents |
| --- | --- |
| `src/data` | Ingestion, cleaning, validation, wide-to-long fact build |
| `src/forecasting` | Naive, MA, Holt-Winters, ARIMA, Prophet wrapper, WMAPE |
| `src/inventory` | Safety stock, ROP, EOQ, ABC, stockout, excess |
| `sql/` | PostgreSQL-first star schema and analyst SQL |
| `notebooks/` | Exploration through final planner analysis |
| `dashboard/powerbi/` | Semantic model, DAX, six-page UX spec |
| `web/` | Interactive executive / planner workbench |
| `docs/interview_guide.md` | Demo script for hiring managers |

## Measured results (this sample run)

These numbers come from `data/processed/run_insights.json` after `python scripts/run_pipeline.py` on the schema-compatible sample (120 SKU/store series, 730 days, 48 series forecasted). They will change if you run on full M5.

| Metric | Value |
| --- | --- |
| Naive baseline Forecast Accuracy | **67.6%** |
| Champion-model mean Forecast Accuracy | **76.9%** |
| Improvement vs baseline | **+9.3 pp** |
| Lowest mean WMAPE among fitted models | ARIMA on the 16 high-value series it was assigned (WMAPE 18.2%) |
| Holt-Winters mean accuracy (24 series) | 80.1% |
| CRITICAL + HIGH stockout share | 7.5% of SKU/stores (3 critical, 6 high) |
| Recommended expedite/reorder actions | 9 |
| Excess inventory value (scenario on-hand × price proxy) | ~$64.6k |
| Prophet | skipped — `prophet` is not installed in this environment |

Do not quote 87% accuracy or a 15% excess reduction. Those figures were not produced by this run.

## Tests

```bash
python -m pytest tests -q
```

Covers WMAPE / accuracy zero-demand cases, SS, ROP, EOQ, ABC, and data-quality gates.

## License

MIT. M5 remains subject to its own competition / dataset terms.
