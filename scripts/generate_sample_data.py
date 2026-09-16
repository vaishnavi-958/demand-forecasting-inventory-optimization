"""Generate a schema-compatible M5 sample when the public dataset is not downloaded.

This is synthetic demand constructed to look like M5 (item/store/dept/calendar/price).
It is NOT Walmart operational data.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.utils.helpers import load_config, resolve_path
from src.utils.logging_config import get_logger, setup_logging

LOGGER = get_logger("generate_sample_data")

STORES = [
    ("CA_1", "CA"),
    ("CA_2", "CA"),
    ("TX_1", "TX"),
    ("WI_1", "WI"),
]

DEPTS = [
    ("FOODS_1", "FOODS", 6, 18.0, 0.35, 2.49),
    ("FOODS_2", "FOODS", 5, 12.0, 0.55, 3.29),
    ("FOODS_3", "FOODS", 5, 8.0, 0.70, 4.19),
    ("HOUSEHOLD_1", "HOUSEHOLD", 5, 4.5, 0.90, 8.99),
    ("HOUSEHOLD_2", "HOUSEHOLD", 4, 2.8, 1.10, 12.49),
    ("HOBBIES_1", "HOBBIES", 3, 1.4, 1.80, 9.99),
    ("HOBBIES_2", "HOBBIES", 2, 0.6, 2.40, 14.99),
]

EVENTS = {
    "01-01": ("NewYear", "National"),
    "02-14": ("Valentines", "Cultural"),
    "07-04": ("IndependenceDay", "National"),
    "10-31": ("Halloween", "Cultural"),
    "12-25": ("Christmas", "National"),
}


def _wm_yr_wk(date: pd.Timestamp) -> int:
    iso = date.isocalendar()
    return int(f"{iso.year % 100:02d}{iso.week:02d}")


def generate(config: dict, seed: int | None = None) -> dict[str, pd.DataFrame]:
    sample_cfg = config.get("sample", {})
    rng = np.random.default_rng(seed if seed is not None else sample_cfg.get("seed", 42))
    n_days = int(sample_cfg.get("n_days", 730))
    start = pd.Timestamp(sample_cfg.get("start_date", "2023-01-01"))
    dates = pd.date_range(start, periods=n_days, freq="D")

    calendar_rows = []
    for i, date in enumerate(dates, start=1):
        key = date.strftime("%m-%d")
        event_name, event_type = EVENTS.get(key, (None, None))
        # Approximate US Thanksgiving (4th Thursday of November)
        if date.month == 11 and date.weekday() == 3 and 22 <= date.day <= 28:
            event_name, event_type = "Thanksgiving", "National"
        calendar_rows.append(
            {
                "date": date.strftime("%Y-%m-%d"),
                "wm_yr_wk": _wm_yr_wk(date),
                "weekday": date.day_name(),
                "wday": date.weekday() + 1,
                "month": date.month,
                "year": date.year,
                "d": f"d_{i}",
                "event_name_1": event_name,
                "event_type_1": event_type,
                "event_name_2": None,
                "event_type_2": None,
                "snap_CA": int(date.day <= 10),
                "snap_TX": int(date.day <= 15),
                "snap_WI": int(date.day <= 10),
            }
        )
    calendar = pd.DataFrame(calendar_rows)

    items = []
    item_seq = 1
    for dept_id, cat_id, n_items, base, cv, price in DEPTS:
        for _ in range(n_items):
            items.append(
                {
                    "item_id": f"{dept_id}_{item_seq:03d}",
                    "dept_id": dept_id,
                    "cat_id": cat_id,
                    "base_demand": base * rng.uniform(0.6, 1.5),
                    "cv": cv * rng.uniform(0.8, 1.3),
                    "base_price": price * rng.uniform(0.85, 1.15),
                    "weekend_lift": 1.15 if cat_id == "FOODS" else 0.85,
                    "trend": rng.uniform(-0.0004, 0.0008),
                }
            )
            item_seq += 1

    sales_rows = []
    price_rows = []
    store_mult = {"CA_1": 1.15, "CA_2": 0.85, "TX_1": 1.05, "WI_1": 0.95}

    for item in items:
        for store_id, state_id in STORES:
            series_id = f"{item['item_id']}_{store_id}_validation"
            daily = []
            last_price = item["base_price"]
            for i, date in enumerate(dates):
                seasonal = 1.0 + 0.12 * np.sin(2 * np.pi * date.dayofyear / 365.25)
                weekly = item["weekend_lift"] if date.weekday() >= 5 else 1.0
                event_lift = 1.0
                cal_row = calendar.iloc[i]
                if pd.notna(cal_row["event_name_1"]):
                    event_lift = 1.55 if item["cat_id"] == "FOODS" else 1.2
                snap_col = {"CA": "snap_CA", "TX": "snap_TX", "WI": "snap_WI"}[state_id]
                snap_lift = 1.18 if cal_row[snap_col] == 1 and item["cat_id"] == "FOODS" else 1.0
                promo = rng.random() < 0.04
                promo_lift = 1.35 if promo else 1.0
                mean = (
                    item["base_demand"]
                    * store_mult[store_id]
                    * seasonal
                    * weekly
                    * event_lift
                    * snap_lift
                    * promo_lift
                    * (1 + item["trend"] * i)
                )
                # Over-dispersed Poisson-like demand; hobbies more intermittent.
                lam = max(mean, 0.05)
                units = int(rng.poisson(lam))
                if item["cv"] > 1.2:
                    units = int(rng.poisson(lam * rng.uniform(0.2, 1.8)))
                if item["cat_id"] == "HOBBIES" and rng.random() < 0.45:
                    units = 0
                units = max(units, 0)
                daily.append(units)

                if date.weekday() == 0 or i == 0:
                    if promo:
                        last_price = round(item["base_price"] * 0.85, 2)
                    else:
                        last_price = round(item["base_price"] * rng.uniform(0.97, 1.03), 2)
                    price_rows.append(
                        {
                            "store_id": store_id,
                            "item_id": item["item_id"],
                            "wm_yr_wk": int(cal_row["wm_yr_wk"]),
                            "sell_price": last_price,
                        }
                    )

            row = {
                "id": series_id,
                "item_id": item["item_id"],
                "dept_id": item["dept_id"],
                "cat_id": item["cat_id"],
                "store_id": store_id,
                "state_id": state_id,
            }
            for i, units in enumerate(daily, start=1):
                row[f"d_{i}"] = units
            sales_rows.append(row)

    sales = pd.DataFrame(sales_rows)
    prices = pd.DataFrame(price_rows).drop_duplicates(["store_id", "item_id", "wm_yr_wk"])
    LOGGER.info("Generated sample calendar=%s sales=%s prices=%s", calendar.shape, sales.shape, prices.shape)
    return {"calendar": calendar, "sales": sales, "prices": prices}


def write_raw(frames: dict[str, pd.DataFrame], data_dir: Path) -> None:
    data_dir.mkdir(parents=True, exist_ok=True)
    frames["calendar"].to_csv(data_dir / "calendar.csv", index=False)
    frames["sales"].to_csv(data_dir / "sales_train_validation.csv", index=False)
    frames["prices"].to_csv(data_dir / "sell_prices.csv", index=False)
    LOGGER.info("Wrote M5-schema sample files to %s", data_dir)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate schema-compatible M5 sample data")
    parser.add_argument("--force", action="store_true", help="Overwrite existing raw files")
    args = parser.parse_args()
    setup_logging()
    config = load_config()
    data_dir = resolve_path(config["paths"]["data_dir"])
    target = data_dir / "sales_train_validation.csv"
    if target.exists() and not args.force:
        LOGGER.info("Raw sales file already exists at %s; use --force to regenerate", target)
        return
    frames = generate(config)
    write_raw(frames, data_dir)


if __name__ == "__main__":
    main()
