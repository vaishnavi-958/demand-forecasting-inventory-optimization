"""Build interview-ready Jupyter notebooks that call the project package."""

from __future__ import annotations

from pathlib import Path

import nbformat as nbf

ROOT = Path(__file__).resolve().parents[1]
NB = ROOT / "notebooks"


def md(text: str):
    return nbf.v4.new_markdown_cell(text)


def code(text: str):
    return nbf.v4.new_code_cell(text)


def write(name: str, cells: list) -> None:
    nb = nbf.v4.new_notebook()
    nb["cells"] = cells
    nb["metadata"] = {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python"},
    }
    path = NB / name
    path.write_text(nbf.writes(nb), encoding="utf-8")
    print(f"wrote {path}")


BOOT = """from pathlib import Path
import sys
ROOT = Path.cwd().parent if Path.cwd().name == "notebooks" else Path.cwd()
sys.path.insert(0, str(ROOT))
from src.utils.logging_config import setup_logging
from src.utils.helpers import load_config, load_model_config, resolve_path
setup_logging("INFO")
CONFIG = load_config()
print("Independent M5-schema project. DATA_DIR =", resolve_path(CONFIG["paths"]["data_dir"]))
"""


def main() -> None:
    NB.mkdir(exist_ok=True)

    write(
        "01_data_exploration.ipynb",
        [
            md("# 01 — Data exploration\n\nIndependent Supply Chain Analytics Project using the public M5 Forecasting dataset.\n\nInspect calendar, wide sales, and weekly prices. Do not assume files are Walmart confidential extracts — they are the public M5 schema or a synthetic sample."),
            code(BOOT),
            code(
                """from src.data.ingestion import load_raw_m5, discover_raw_files
from src.data.validation import validate_raw_files
from scripts.generate_sample_data import generate, write_raw

raw_dir = resolve_path(CONFIG["paths"]["data_dir"])
if not (raw_dir / "calendar.csv").exists():
    write_raw(generate(CONFIG), raw_dir)

files = discover_raw_files(CONFIG)
raw = load_raw_m5(CONFIG)
validate_raw_files(files, raw)
calendar, sales, prices = raw["calendar"], raw["sales"], raw["prices"]
print(calendar.head())
print("sales shape", sales.shape, "price shape", prices.shape)
print("stores", sales["store_id"].nunique(), "items", sales["item_id"].nunique())
print(sales["cat_id"].value_counts())
"""
            ),
            code(
                """day_cols = [c for c in sales.columns if str(c).startswith("d_")]
print("days", len(day_cols), "series", len(sales))
print(calendar["event_name_1"].value_counts(dropna=True).head())
print(prices["sell_price"].describe())
"""
            ),
        ],
    )

    write(
        "02_data_cleaning.ipynb",
        [
            md("# 02 — Data cleaning and quality gates\n\nNegative sales are clipped, missing prices are flagged, duplicates fail validation. Errors are raised, not swallowed."),
            code(BOOT),
            code(
                """from src.data.ingestion import load_raw_m5
from src.data.cleaning import clean_calendar, clean_prices, clean_sales
from src.data.transformation import build_fact_daily_sales
from src.data.validation import validate_fact_sales

raw = load_raw_m5(CONFIG)
calendar = clean_calendar(raw["calendar"])
sales = clean_sales(raw["sales"])
prices = clean_prices(raw["prices"])
fact = build_fact_daily_sales(sales, calendar, prices, CONFIG)
report = validate_fact_sales(fact)
report
"""
            ),
        ],
    )

    write(
        "03_demand_analysis.ipynb",
        [
            md("# 03 — Demand analysis\n\nVolume/volatility segments, intermittency (ADI / CV²), rolling demand, YoY when history allows. These segments drive later inventory comments."),
            code(BOOT),
            code(
                """import pandas as pd
from src.features.demand_features import build_demand_profile

processed = resolve_path(CONFIG["paths"]["processed_dir"]) / "fact_daily_sales.parquet"
if not processed.exists():
    raise SystemExit("Run python scripts/run_pipeline.py first")
fact = pd.read_parquet(processed)
profile = build_demand_profile(fact)
print(profile["demand_segment"].value_counts())
print(profile["demand_pattern"].value_counts())
profile.sort_values("coefficient_of_variation", ascending=False).head(10)
"""
            ),
            code(
                """import matplotlib.pyplot as plt
fig, ax = plt.subplots(figsize=(7, 4))
profile.boxplot(column="coefficient_of_variation", by="cat_id", ax=ax)
ax.set_title("Demand CV by category")
ax.set_ylabel("CV")
plt.suptitle("")
plt.show()
"""
            ),
        ],
    )

    write(
        "04_forecasting_baseline.ipynb",
        [
            md("# 04 — Naive and moving-average baselines\n\nLast observation carried forward and MA 7/14/28. These are the models a planner should beat before celebrating Holt-Winters or ARIMA."),
            code(BOOT),
            code(
                """import pandas as pd
from src.forecasting.baseline import naive_forecast
from src.forecasting.moving_average import moving_average_forecast
from src.forecasting.evaluation import chronological_split, metrics_dict

fact = pd.read_parquet(resolve_path(CONFIG["paths"]["processed_dir"]) / "fact_daily_sales.parquet")
item, store = fact.groupby(["item_id", "store_id"])["revenue"].sum().idxmax()
series = fact[(fact.item_id == item) & (fact.store_id == store)].sort_values("date")
train, valid = chronological_split(series, "date", 28)
y = valid["sales_units"]
print(item, store)
print("Naive", metrics_dict(y, naive_forecast(train["sales_units"], 28)))
print("MA28", metrics_dict(y, moving_average_forecast(train["sales_units"], 28, 28)))
"""
            ),
        ],
    )

    write(
        "05_holt_winters_forecasting.ipynb",
        [
            md("# 05 — Holt-Winters\n\nWeekly seasonality (period 7) plus optional trend. Falls back to naive if the series is too short or degenerate."),
            code(BOOT),
            code(
                """import pandas as pd
from src.forecasting.exponential_smoothing import holt_winters_forecast
from src.forecasting.evaluation import chronological_split, metrics_dict

fact = pd.read_parquet(resolve_path(CONFIG["paths"]["processed_dir"]) / "fact_daily_sales.parquet")
item, store = fact.groupby(["item_id", "store_id"])["revenue"].sum().idxmax()
series = fact[(fact.item_id == item) & (fact.store_id == store)].sort_values("date")
train, valid = chronological_split(series, "date", 28)
yhat = holt_winters_forecast(train["sales_units"], 28)
metrics_dict(valid["sales_units"], yhat)
"""
            ),
        ],
    )

    write(
        "06_prophet_forecasting.ipynb",
        [
            md("# 06 — Prophet (optional)\n\nIf `prophet` is not installed, the wrapper logs a warning and returns a naive fallback with `status=unavailable`. See `docs/forecasting_methodology.md`."),
            code(BOOT),
            code(
                """import pandas as pd
from src.forecasting.prophet_model import PROPHET_AVAILABLE, fit_predict_prophet
from src.forecasting.evaluation import chronological_split

print("Prophet available:", PROPHET_AVAILABLE)
fact = pd.read_parquet(resolve_path(CONFIG["paths"]["processed_dir"]) / "fact_daily_sales.parquet")
item, store = fact.groupby(["item_id", "store_id"])["revenue"].sum().idxmax()
series = fact[(fact.item_id == item) & (fact.store_id == store)].sort_values("date")
train, valid = chronological_split(series, "date", 28)
pred = fit_predict_prophet(train, pd.to_datetime(valid["date"]), load_model_config())
pred.head()
"""
            ),
        ],
    )

    write(
        "07_model_comparison.ipynb",
        [
            md("# 07 — Model comparison\n\nRead `model_metrics.csv` produced by the pipeline. Champion = lowest WMAPE. Quote only numbers from this file."),
            code(BOOT),
            code(
                """import pandas as pd
metrics = pd.read_csv(resolve_path(CONFIG["paths"]["processed_dir"]) / "model_metrics.csv")
summary = metrics.groupby("model")[["MAE", "RMSE", "WMAPE", "Forecast_Accuracy"]].mean().sort_values("WMAPE")
print(summary)
print("Champion share")
print(metrics.loc[metrics["rank"] == 1, "model"].value_counts(normalize=True))
"""
            ),
        ],
    )

    write(
        "08_inventory_optimization.ipynb",
        [
            md("# 08 — Safety stock, ROP, EOQ, ABC\n\nLead time and costs are scenario parameters. Change `service_level` and recompute."),
            code(BOOT),
            code(
                """import pandas as pd
from src.inventory.engine import run_inventory_engine, run_scenario
from src.features.inventory_features import attach_cost_assumptions, simulate_on_hand_inventory

profile = pd.read_parquet(resolve_path(CONFIG["paths"]["processed_dir"]) / "demand_profile.parquet")
if "lead_time_days" not in profile.columns:
    profile = attach_cost_assumptions(profile, CONFIG)
    profile = simulate_on_hand_inventory(profile)
base = run_inventory_engine(profile, CONFIG)
print(base["stockout_risk"].value_counts())
print(base["abc_class"].value_counts())
base[["item_id", "store_id", "safety_stock", "reorder_point", "eoq", "abc_class", "recommended_action"]].head()
"""
            ),
            code(
                """tight = run_scenario(profile, CONFIG, service_level=0.99, lead_time_days=10, ordering_cost=75, holding_cost_rate=0.25)
compare = base.merge(tight, on=["item_id", "store_id"], suffixes=("_95", "_99"))
print((compare["safety_stock_99"] - compare["safety_stock_95"]).mean(), "mean SS increase at 99% / LT=10")
"""
            ),
        ],
    )

    write(
        "09_final_analysis.ipynb",
        [
            md("# 09 — Final analysis\n\nLoad `run_insights.json`. Do not replace these figures with a memorized 87% accuracy claim."),
            code(BOOT),
            code(
                """import json
from pathlib import Path
p = resolve_path(CONFIG["paths"]["processed_dir"]) / "run_insights.json"
print(p.read_text())
"""
            ),
            code(
                """import pandas as pd
inv = pd.read_csv(resolve_path(CONFIG["paths"]["processed_dir"]) / "fact_inventory_optimization.csv")
print("Planner queue")
print(inv["recommended_action"].value_counts())
print(inv.sort_values(["stockout_risk", "excess_value"]).head(15)[
    ["item_id", "store_id", "abc_class", "stockout_risk", "recommended_action", "days_of_supply"]
])
"""
            ),
        ],
    )


if __name__ == "__main__":
    main()
