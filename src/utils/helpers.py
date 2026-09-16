"""Configuration and path helpers."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv


def project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def resolve_path(path_value: str | Path) -> Path:
    path = Path(path_value)
    if path.is_absolute():
        return path
    return project_root() / path


def load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Configuration file not found: {path}")
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    if not isinstance(data, dict):
        raise ValueError(f"YAML at {path} must be a mapping")
    return data


def load_config(path: str | Path | None = None) -> dict[str, Any]:
    load_dotenv(project_root() / ".env")
    config_path = Path(path) if path else project_root() / "config" / "config.yaml"
    config = load_yaml(config_path)

    if os.getenv("DATA_DIR"):
        config.setdefault("paths", {})["data_dir"] = os.getenv("DATA_DIR")
    if os.getenv("PROCESSED_DIR"):
        config.setdefault("paths", {})["processed_dir"] = os.getenv("PROCESSED_DIR")
    if os.getenv("DATABASE_URL"):
        config.setdefault("database", {})["url"] = os.getenv("DATABASE_URL")
    if os.getenv("FORECAST_HORIZON"):
        config.setdefault("forecasting", {})["horizon_days"] = int(os.getenv("FORECAST_HORIZON"))
    if os.getenv("MAX_FORECAST_SKUS"):
        config.setdefault("forecasting", {})["max_forecast_skus"] = int(os.getenv("MAX_FORECAST_SKUS"))
    if os.getenv("MIN_HISTORY_DAYS"):
        config.setdefault("forecasting", {})["min_history_days"] = int(os.getenv("MIN_HISTORY_DAYS"))
    if os.getenv("SERVICE_LEVEL"):
        config.setdefault("inventory", {})["service_level"] = float(os.getenv("SERVICE_LEVEL"))
    if os.getenv("DEFAULT_LEAD_TIME_DAYS"):
        config.setdefault("inventory", {})["default_lead_time_days"] = int(
            os.getenv("DEFAULT_LEAD_TIME_DAYS")
        )
    return config


def load_model_config(path: str | Path | None = None) -> dict[str, Any]:
    config_path = Path(path) if path else project_root() / "config" / "model_config.yaml"
    return load_yaml(config_path)


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def z_for_service_level(config: dict[str, Any], service_level: float | None = None) -> float:
    inventory = config.get("inventory", {})
    level = float(service_level if service_level is not None else inventory.get("service_level", 0.95))
    mapping = config.get("service_level_z", {})
    key = f"{level:.3g}" if level not in mapping else level
    if level in mapping:
        return float(mapping[level])
    for map_key, z_value in mapping.items():
        if abs(float(map_key) - level) < 1e-9:
            return float(z_value)
    from scipy.stats import norm

    return float(norm.ppf(level))
