# Inventory methodology

All policy parameters below are **analytical assumptions / scenario parameters** unless taken from M5 sell-through. They are not Walmart, SAP, or employer master data.

## Safety stock

\[
SS = Z \times \sigma_d \times \sqrt{LT}
\]

- \(Z\): standard normal quantile of the cycle service level (90 / 95 / 97.5 / 99%)
- \(\sigma_d\): sample standard deviation of daily demand
- \(LT\): lead time in days from `lead_time_by_department` (default 7)

Assumption: daily demand deviations are independent. Lead-time variability is not in M5 and is not invented; a two-source SS formula can be added if \(\sigma_{LT}\) is ever supplied.

## Reorder point

\[
ROP = \bar{d} \times LT + SS
\]

`inventory_position` equals scenario on-hand because M5 has no open PO / in-transit file (a DRP-style position would add on-order).

`days_of_supply` = on-hand / average daily demand.

`recommended_order_flag` is true when the action is EXPEDITE or REORDER.

## Lead time

M5 has **no supplier lead-time field**. Department defaults live in `config/config.yaml` and are labeled `lead_time_source = analytical_assumption`. Change them for scenario analysis.

## ABC

Annual consumption value = annual demand × unit-cost proxy (average sell price).

Sort descending, take cumulative value share:

- A: cumulative ≤ 80%
- B: 80% < cumulative ≤ 95%
- C: remainder

SKU counts will **not** be 80/15/5. That is expected with a Pareto distribution.

## EOQ

\[
EOQ = \sqrt{\frac{2DS}{H}}
\]

- \(D\): annual demand
- \(S\): ordering cost (config, default 75)
- \(H\): unit cost × holding-cost rate (default 25%)

These are **not** actual procurement costs.

## Stockout risk

| Class | Rule |
| --- | --- |
| CRITICAL | DOS < lead time (cannot cover replenishment cycle) |
| HIGH | On-hand < ROP |
| MEDIUM | On-hand within `near_rop_tolerance` (default 15%) above ROP |
| LOW | Comfortably above ROP |

## Excess inventory

Excess when days of supply exceed `excess_days_supply_threshold` (default 45) **or** on-hand exceeds recommended position (LT demand + SS) and also exceeds `target_days_supply` (default 21).

`excess_value` = excess units × unit-cost proxy.

## Inventory turns (proxy)

M5 has no inventory valuation or COGS ledger.

\[
Turns_{proxy} = \frac{\text{annual consumption value}}{\text{on-hand} \times \text{unit cost}}
\]

Documented as a proxy in the dashboard assumptions panel. Do not present it as financial inventory turns from a retail GL.

## Planner actions

| Action | When |
| --- | --- |
| EXPEDITE | CRITICAL |
| REORDER | HIGH |
| REDUCE INVENTORY | Excess flag and not expedite/reorder |
| MONITOR | MEDIUM |
| NO ACTION | LOW and not excess |

## Scenario engine

`src/inventory/engine.py` `run_scenario()` and the web workbench recompute SS, ROP, EOQ, risk, and excess when the planner changes service level, lead time, ordering cost, or holding-cost rate.
