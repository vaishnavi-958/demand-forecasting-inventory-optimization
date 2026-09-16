"""Create schema / SQLite file and optionally apply PostgreSQL DDL."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.database.connection import execute_sql_script, get_engine
from src.utils.helpers import load_config, project_root
from src.utils.logging_config import get_logger, setup_logging


def main() -> None:
    setup_logging()
    logger = get_logger("setup_database")
    config = load_config()
    engine = get_engine(config)
    sql_dir = project_root() / "sql"
    execute_sql_script(engine, sql_dir / "01_create_schema.sql")
    execute_sql_script(engine, sql_dir / "02_create_tables.sql")
    logger.info("Database setup complete using %s", engine.url.render_as_string(hide_password=True))


if __name__ == "__main__":
    main()
