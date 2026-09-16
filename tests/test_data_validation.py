"""Raw and fact-table validation gates."""

from pathlib import Path

import pandas as pd
import pytest

from src.data.validation import DataQualityError, validate_fact_sales, validate_raw_files


def test_missing_sales_columns():
    files = {
        "calendar": Path("/tmp/does-not-need-to-exist-for-this-assert"),
    }
    # File existence is checked first.
    with pytest.raises(FileNotFoundError):
        validate_raw_files(
            {"calendar": Path("/tmp/missing-calendar-xyz.csv")},
            {"calendar": pd.DataFrame(), "sales": pd.DataFrame(), "prices": pd.DataFrame()},
        )


def test_fact_rejects_negative_sales(tmp_path):
    fact = pd.DataFrame(
        {
            "date": pd.to_datetime(["2024-01-01", "2024-01-02"]),
            "item_id": ["A", "A"],
            "store_id": ["S1", "S1"],
            "dept_id": ["D", "D"],
            "cat_id": ["C", "C"],
            "sales_units": [1, -4],
            "price": [2.0, 2.0],
            "revenue": [2.0, -8.0],
        }
    )
    with pytest.raises(DataQualityError):
        validate_fact_sales(fact)


def test_fact_rejects_duplicates():
    fact = pd.DataFrame(
        {
            "date": pd.to_datetime(["2024-01-01", "2024-01-01"]),
            "item_id": ["A", "A"],
            "store_id": ["S1", "S1"],
            "dept_id": ["D", "D"],
            "cat_id": ["C", "C"],
            "sales_units": [1, 2],
            "price": [2.0, 2.0],
            "revenue": [2.0, 4.0],
        }
    )
    with pytest.raises(DataQualityError):
        validate_fact_sales(fact)


def test_fact_passes_clean_panel():
    fact = pd.DataFrame(
        {
            "date": pd.to_datetime(["2024-01-01", "2024-01-02"]),
            "item_id": ["A", "A"],
            "store_id": ["S1", "S1"],
            "dept_id": ["D", "D"],
            "cat_id": ["C", "C"],
            "sales_units": [1, 2],
            "price": [2.0, 2.0],
            "revenue": [2.0, 4.0],
        }
    )
    report = validate_fact_sales(fact)
    assert report["row_count"] == 2


def test_missing_product_ids_fail():
    fact = pd.DataFrame(
        {
            "date": pd.to_datetime(["2024-01-01"]),
            "item_id": [None],
            "store_id": ["S1"],
            "dept_id": ["D"],
            "cat_id": ["C"],
            "sales_units": [1],
            "price": [2.0],
            "revenue": [2.0],
        }
    )
    with pytest.raises(DataQualityError):
        validate_fact_sales(fact)
