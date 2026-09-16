-- Star schema for demand, forecast, and inventory analytics.
-- PostgreSQL-first; types are reasonably portable to SQL Server
-- (SERIAL -> INT IDENTITY, TEXT -> NVARCHAR(n), BOOLEAN -> BIT).

CREATE TABLE IF NOT EXISTS dim_date (
    date_key        INTEGER PRIMARY KEY,
    date            DATE NOT NULL,
    year            INTEGER NOT NULL,
    quarter         INTEGER,
    month           INTEGER NOT NULL,
    week            INTEGER,
    weekday         TEXT
);

CREATE TABLE IF NOT EXISTS dim_product (
    product_key     INTEGER PRIMARY KEY,
    item_id         TEXT NOT NULL UNIQUE,
    dept_id         TEXT NOT NULL,
    cat_id          TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS dim_store (
    store_key       INTEGER PRIMARY KEY,
    store_id        TEXT NOT NULL UNIQUE,
    state_id        TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS dim_department (
    department_key  INTEGER PRIMARY KEY,
    dept_id         TEXT NOT NULL UNIQUE,
    cat_id          TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS fact_daily_sales (
    date_key        INTEGER NOT NULL,
    product_key     INTEGER NOT NULL,
    store_key       INTEGER NOT NULL,
    department_key  INTEGER NOT NULL,
    item_id         TEXT NOT NULL,
    store_id        TEXT NOT NULL,
    dept_id         TEXT NOT NULL,
    sales_units     INTEGER NOT NULL,
    price           DOUBLE PRECISION NOT NULL,
    revenue         DOUBLE PRECISION NOT NULL,
    promotion_flag  INTEGER NOT NULL,
    snap_flag       INTEGER,
    PRIMARY KEY (date_key, product_key, store_key)
);

CREATE TABLE IF NOT EXISTS fact_forecast (
    date            DATE NOT NULL,
    item_id         TEXT NOT NULL,
    store_id        TEXT NOT NULL,
    dept_id         TEXT,
    cat_id          TEXT,
    model           TEXT NOT NULL,
    forecast        DOUBLE PRECISION NOT NULL,
    forecast_lower  DOUBLE PRECISION,
    forecast_upper  DOUBLE PRECISION,
    actual          DOUBLE PRECISION,
    best_model      TEXT,
    is_selected_model INTEGER
);

CREATE TABLE IF NOT EXISTS fact_model_metrics (
    item_id             TEXT NOT NULL,
    store_id            TEXT NOT NULL,
    dept_id             TEXT,
    model               TEXT NOT NULL,
    MAE                 DOUBLE PRECISION,
    RMSE                DOUBLE PRECISION,
    MAPE                DOUBLE PRECISION,
    sMAPE               DOUBLE PRECISION,
    WMAPE               DOUBLE PRECISION,
    Forecast_Accuracy   DOUBLE PRECISION,
    n_points            INTEGER,
    rank                INTEGER,
    PRIMARY KEY (item_id, store_id, model)
);

CREATE TABLE IF NOT EXISTS fact_inventory_optimization (
    item_id                         TEXT NOT NULL,
    store_id                        TEXT NOT NULL,
    dept_id                         TEXT,
    cat_id                          TEXT,
    avg_daily_demand                DOUBLE PRECISION,
    demand_std                      DOUBLE PRECISION,
    lead_time_days                  DOUBLE PRECISION,
    service_level                   DOUBLE PRECISION,
    safety_stock                    DOUBLE PRECISION,
    reorder_point                   DOUBLE PRECISION,
    current_inventory               DOUBLE PRECISION,
    days_of_supply                  DOUBLE PRECISION,
    stockout_risk                   TEXT,
    excess_units                    DOUBLE PRECISION,
    excess_value                    DOUBLE PRECISION,
    eoq                             DOUBLE PRECISION,
    abc_class                       TEXT,
    recommended_action              TEXT,
    inventory_turns_proxy           DOUBLE PRECISION,
    PRIMARY KEY (item_id, store_id)
);

CREATE TABLE IF NOT EXISTS fact_abc_classification (
    item_id                     TEXT NOT NULL,
    store_id                    TEXT NOT NULL,
    dept_id                     TEXT,
    annual_demand               DOUBLE PRECISION,
    unit_cost                   DOUBLE PRECISION,
    annual_consumption_value    DOUBLE PRECISION,
    cumulative_value_pct        DOUBLE PRECISION,
    abc_class                   TEXT,
    PRIMARY KEY (item_id, store_id)
);
