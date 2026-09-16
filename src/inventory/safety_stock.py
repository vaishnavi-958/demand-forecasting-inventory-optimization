"""Safety stock using SS = Z × σd × √LT.

Lead time is an analytical assumption / scenario parameter. M5 does not contain supplier lead time.
"""

from __future__ import annotations

import math

from scipy.stats import norm


def z_from_service_level(service_level: float) -> float:
    if not 0 < service_level < 1:
        raise ValueError("service_level must be between 0 and 1 exclusive")
    return float(norm.ppf(service_level))


def safety_stock(
    demand_std: float,
    lead_time_days: float,
    service_level: float | None = None,
    z_value: float | None = None,
) -> float:
    """Cycle-service-level safety stock under independent daily demand.

    SS = Z * sigma_d * sqrt(LT)

    If demand_std or lead_time is 0, safety stock is 0.
    Negative inputs raise ValueError.
    """
    if demand_std < 0:
        raise ValueError("demand_std cannot be negative")
    if lead_time_days < 0:
        raise ValueError("lead_time_days cannot be negative")
    if z_value is None:
        if service_level is None:
            raise ValueError("Provide service_level or z_value")
        z_value = z_from_service_level(service_level)
    if demand_std == 0 or lead_time_days == 0:
        return 0.0
    return float(z_value * demand_std * math.sqrt(lead_time_days))
