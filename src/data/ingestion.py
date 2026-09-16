"""Load M5-schema files from DATA_DIR."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from src.utils.helpers import resolve_path
from src.utils.logging_config import get_logger

LOGGER = get_logger(__name__)

REQUIRED_FILES = ("calendar_file", "sales_file", "prices_file")


def discover_raw_files(config: dict[str, Any]) -> dict[str, Path]:
    paths = config["paths"]
    data_dir = resolve_path(paths["data_dir"])
    files = {
        "calendar": data_dir / paths.get("calendar_file", "calendar.csv"),
        "sales": data_dir / paths.get("sales_file", "sales_train_validation.csv"),
        "prices": data_dir / paths.get("prices_file", "sell_prices.csv"),
    }
    return files


def load_csv(path: Path, **kwargs: Any) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(
            f"Required M5 file not found: {path}. "
            "Download the public M5 Forecasting dataset from Kaggle into data/raw/ "
            "or run `python scripts/generate_sample_data.py` for a schema-compatible sample."
        )
    LOGGER.info("Loading %s", path)
    return pd.read_csv(path, **kwargs)


def load_raw_m5(config: dict[str, Any]) -> dict[str, pd.DataFrame]:
    files = discover_raw_files(config)
    calendar = load_csv(files["calendar"])
    prices = load_csv(files["prices"])
    sales = load_csv(files["sales"])
    LOGGER.info(
        "Loaded raw M5-schema files: calendar=%s sales=%s prices=%s",
        calendar.shape,
        sales.shape,
        prices.shape,
    )
    return {"calendar": calendar, "sales": sales, "prices": prices}
