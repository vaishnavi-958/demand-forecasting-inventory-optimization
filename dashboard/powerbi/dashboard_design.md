# Dashboard design (executive UX)

Canvas: 1280 × 720. Theme: white, navy `#0F3D5E`, teal `#0E7C7B`, alert red `#C0392B`, warning `#D68910`. Font: Segoe UI / DIN. One slicer pane on the left: Date, Store, Department, SKU, Model.

Every visual answers a question. No decorative charts.

## Page 1 — Executive supply chain overview

**Question:** How is the network performing this cycle?

KPI cards: Total Sales, Forecast Accuracy (champion), WMAPE, Inventory Turns (proxy), Stockout Risk %, Excess Inventory Value, A-Class SKU %, Recommended Orders.

Visuals:

- Line: sales trend (Total Sales by date)
- Line: forecast vs actual on holdout (best model)
- Stacked bar: stockout risk counts
- Bar: excess value by category
- Bar: departments with lowest Forecast Accuracy
- Table: stores ranked by CRITICAL SKUs

Tooltip: units, revenue, WMAPE. Bookmark: "Exceptions only".

## Page 2 — Demand forecast

**Question:** Which method should we trust, and where is error?

- Actual vs forecast (holdout) with optional interval from Prophet
- Clustered bar: Forecast Accuracy by model
- Bar: WMAPE by department
- Line: accuracy is a static holdout (do not fake a time trend unless you store rolling-origin folds)
- Matrix drilldown: category → dept → SKU

Filters: Date, Store, Department, SKU, Model.

## Page 3 — Inventory optimization

**Question:** Are we short, long, or in policy?

- Waterfall or clustered bar: on-hand vs SS vs ROP
- Histogram / bar: days of supply vs target
- Map or bar: excess value by store
- Table with conditional formatting on stockout risk

## Page 4 — ABC / EOQ

**Question:** Where is the value, and what is the order cycle suggestion?

- Pareto: cumulative value % vs SKU rank
- Donut: SKU count by ABC
- Bar: inventory value by ABC
- Scatter: EOQ vs recommended order qty
- Table: A-class SKUs (item, store, value, SS, ROP)

## Page 5 — Store / region analysis

Drill path: Region (`state_id`) → Store → Department → SKU.

Visuals: sales, demand trend, forecast accuracy, on-hand, stockout risk, excess.

## Page 6 — Planner action center

Workbench table:

SKU, Store, Department, ABC, Champion forecast accuracy, On-hand, SS, ROP, DOS, Risk, Excess value, Recommended action.

Action values: EXPEDITE, REORDER, MONITOR, REDUCE INVENTORY, NO ACTION.

Drill-through from this table to Page 2 (forecast) and Page 3 (inventory). Report page tooltip: last 28 actual vs forecast sparkline.

## UX rules

- KPI cards on top, exceptions in the middle, action table at the bottom of page 6
- Do not put 12 charts on the executive page
- Slicers persist via sync slicers
- Title each visual as a question, e.g. "Where is excess value concentrated?"
