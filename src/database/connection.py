"""SQLAlchemy connection helpers. PostgreSQL is the documented production target; SQLite is the local default."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from src.utils.helpers import resolve_path
from src.utils.logging_config import get_logger

LOGGER = get_logger(__name__)


def get_engine(config: dict[str, Any]) -> Engine:
    url = config.get("database", {}).get("url", "sqlite:///data/processed/supply_chain.db")
    if url.startswith("sqlite:///"):
        db_path = url.replace("sqlite:///", "", 1)
        resolved = resolve_path(db_path)
        resolved.parent.mkdir(parents=True, exist_ok=True)
        url = f"sqlite:///{resolved}"
    LOGGER.info("Opening database engine (%s)", url.split("://")[0])
    return create_engine(url, future=True)


def execute_sql_script(engine: Engine, sql_path: str | Path) -> None:
    script = Path(sql_path).read_text(encoding="utf-8")
    dialect = engine.dialect.name
    statements = [s.strip() for s in script.split(";") if s.strip() and not s.strip().startswith("--")]
    with engine.begin() as conn:
        for stmt in statements:
            upper = stmt.upper()
            if dialect == "sqlite" and any(
                token in upper for token in ("CREATE SCHEMA", "SET SEARCH_PATH", "COMMENT ON")
            ):
                continue
            conn.execute(text(stmt))
