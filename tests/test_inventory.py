"""Safety stock, reorder point, and stockout-risk tests."""

import math

from src.inventory.reorder_point import reorder_point
from src.inventory.safety_stock import safety_stock, z_from_service_level
from src.inventory.stockout_risk import classify_stockout_risk, recommended_action


def test_safety_stock_known_value():
    ss = safety_stock(demand_std=10, lead_time_days=4, z_value=1.65)
    assert abs(ss - 33.0) < 1e-9


def test_safety_stock_zero_variance_or_lead_time():
    assert safety_stock(0, 7, z_value=1.65) == 0.0
    assert safety_stock(10, 0, z_value=1.65) == 0.0


def test_z_from_service_level_95():
    z = z_from_service_level(0.95)
    assert abs(z - 1.64485) < 1e-4


def test_reorder_point():
    rop = reorder_point(avg_daily_demand=20, lead_time_days=5, safety_stock_units=15)
    assert rop == 115


def test_stockout_critical_when_dos_below_lead_time():
    # 10 units, demand 10/day, LT 5 -> DOS=1 < LT
    assert classify_stockout_risk(10, reorder_point_units=50, avg_daily_demand=10, lead_time_days=5) == "CRITICAL"


def test_stockout_high_below_rop():
    assert classify_stockout_risk(80, reorder_point_units=100, avg_daily_demand=5, lead_time_days=5) == "HIGH"


def test_stockout_medium_near_rop():
    assert classify_stockout_risk(108, reorder_point_units=100, avg_daily_demand=5, lead_time_days=5) == "MEDIUM"


def test_stockout_low():
    assert classify_stockout_risk(200, reorder_point_units=100, avg_daily_demand=5, lead_time_days=5) == "LOW"


def test_recommended_actions():
    assert recommended_action("CRITICAL", False) == "EXPEDITE"
    assert recommended_action("HIGH", False) == "REORDER"
    assert recommended_action("LOW", True) == "REDUCE INVENTORY"
    assert recommended_action("MEDIUM", False) == "MONITOR"
    assert recommended_action("LOW", False) == "NO ACTION"


def test_rejects_negative_demand_std():
    try:
        safety_stock(-1, 4, z_value=1.6)
        assert False, "expected ValueError"
    except ValueError:
        pass
