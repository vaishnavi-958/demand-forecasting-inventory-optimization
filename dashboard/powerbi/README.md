# Power BI dashboard

Desktop file is not committed (`.pbix` is binary and environment-specific). Build it from `data/processed/powerbi/*.csv` after `python scripts/run_pipeline.py`.

This folder is the **semantic model + UX spec** a BI developer would implement in Power BI Desktop. The interactive `web/` app mirrors the same six pages so the project can be demonstrated without Desktop.

## Pages

1. Executive supply chain overview
2. Demand forecast
3. Inventory optimization
4. ABC / EOQ
5. Store / region analysis
6. Planner action center

See `dashboard_design.md`, `data_model.md`, and `dax_measures.md`.
