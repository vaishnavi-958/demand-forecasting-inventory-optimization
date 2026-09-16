"""ABC cumulative-value classification."""

import pandas as pd

from src.inventory.abc_analysis import abc_classify


def test_classic_80_15_5_split():
    df = pd.DataFrame(
        {
            "item_id": ["A1", "B1", "C1"],
            "store_id": ["S", "S", "S"],
            "annual_consumption_value": [80.0, 15.0, 5.0],
        }
    )
    out = abc_classify(df)
    assert list(out["abc_class"]) == ["A", "B", "C"]
    assert abs(out.loc[0, "cumulative_value_pct"] - 0.80) < 1e-9
    assert abs(out.loc[1, "cumulative_value_pct"] - 0.95) < 1e-9


def test_first_sku_forced_a_when_it_exceeds_cutoff():
    df = pd.DataFrame(
        {
            "item_id": ["X", "Y"],
            "store_id": ["S", "S"],
            "annual_consumption_value": [90.0, 10.0],
        }
    )
    out = abc_classify(df)
    assert out.loc[0, "abc_class"] == "A"
    assert out.loc[1, "abc_class"] == "C"


def test_zero_value_all_c():
    df = pd.DataFrame(
        {
            "item_id": ["Z1", "Z2"],
            "store_id": ["S", "S"],
            "annual_consumption_value": [0.0, 0.0],
        }
    )
    out = abc_classify(df)
    assert set(out["abc_class"]) == {"C"}


def test_empty_frame():
    df = pd.DataFrame(columns=["item_id", "store_id", "annual_consumption_value"])
    out = abc_classify(df)
    assert len(out) == 0
