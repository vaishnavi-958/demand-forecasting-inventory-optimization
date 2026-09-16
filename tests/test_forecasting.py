"""Forecast metric edge cases, including zero demand."""

from src.forecasting.evaluation import forecast_accuracy, mae, mape, rmse, smape, wmape


def test_mae_rmse_basic():
    y = [10, 12, 8]
    yhat = [11, 10, 8]
    assert abs(mae(y, yhat) - (1 + 2 + 0) / 3) < 1e-9
    assert abs(rmse(y, yhat) - ((1 + 4 + 0) / 3) ** 0.5) < 1e-9


def test_wmape_and_accuracy_definition():
    y = [10, 0, 10]
    yhat = [8, 1, 12]
    assert abs(wmape(y, yhat) - 0.25) < 1e-9
    assert abs(forecast_accuracy(y, yhat) - 0.75) < 1e-9


def test_mape_skips_zeros():
    y = [0, 10]
    yhat = [5, 12]
    assert abs(mape(y, yhat) - 0.2) < 1e-9


def test_mape_all_zero_is_nan():
    import math

    assert math.isnan(mape([0, 0], [1, 2]))


def test_zero_demand_perfect_forecast():
    assert wmape([0, 0, 0], [0, 0, 0]) == 0.0
    assert forecast_accuracy([0, 0, 0], [0, 0, 0]) == 1.0


def test_zero_demand_nonzero_forecast():
    assert wmape([0, 0], [1, 1]) == 1.0
    assert forecast_accuracy([0, 0], [1, 1]) == 0.0


def test_smape_symmetric():
    assert abs(smape([10], [0]) - 2.0) < 1e-9 or abs(smape([10], [0]) - 2 * 10 / 10) < 1e-6
    # 2*|10-0|/(|10|+|0|) = 2


def test_constant_demand_naive_is_perfect():
    y = [5, 5, 5, 5]
    yhat = [5, 5, 5, 5]
    assert mae(y, yhat) == 0
    assert forecast_accuracy(y, yhat) == 1.0


def test_wmape_all_nan_actuals_is_nan():
    import math

    assert math.isnan(wmape([float("nan"), float("nan")], [1, 2]))
