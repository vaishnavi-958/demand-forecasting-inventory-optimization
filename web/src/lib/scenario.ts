import type { PlannerAction, PlannerRow, Scenario, StockoutRisk } from "./types";

const Z: Record<number, number> = {
  0.9: 1.2815515655446004,
  0.95: 1.6448536269514722,
  0.975: 1.959963984540054,
  0.99: 2.3263478740408408,
};

export function zFor(serviceLevel: number): number {
  const exact = Z[serviceLevel];
  if (exact) return exact;
  // Abramowitz approximation is unnecessary; snap to nearest configured level.
  const keys = Object.keys(Z).map(Number);
  const nearest = keys.reduce((a, b) =>
    Math.abs(b - serviceLevel) < Math.abs(a - serviceLevel) ? b : a,
  );
  return Z[nearest];
}

export function safetyStock(std: number, leadTime: number, z: number): number {
  if (std <= 0 || leadTime <= 0) return 0;
  return z * std * Math.sqrt(leadTime);
}

export function eoq(annualDemand: number, orderingCost: number, holdingCost: number): number {
  if (annualDemand <= 0 || orderingCost <= 0 || holdingCost <= 0) return 0;
  return Math.sqrt((2 * annualDemand * orderingCost) / holdingCost);
}

export function classifyRisk(
  onHand: number,
  rop: number,
  avgDaily: number,
  leadTime: number,
): StockoutRisk {
  const dos = avgDaily > 0 ? onHand / avgDaily : Number.POSITIVE_INFINITY;
  if (avgDaily > 0 && dos < leadTime) return "CRITICAL";
  if (onHand < rop) return "HIGH";
  if (onHand <= rop * 1.15) return "MEDIUM";
  return "LOW";
}

export function actionFor(risk: StockoutRisk, excess: boolean): PlannerAction {
  if (risk === "CRITICAL") return "EXPEDITE";
  if (risk === "HIGH") return "REORDER";
  if (excess) return "REDUCE INVENTORY";
  if (risk === "MEDIUM") return "MONITOR";
  return "NO ACTION";
}

export function applyScenario(rows: PlannerRow[], scenario: Scenario): PlannerRow[] {
  const z = zFor(scenario.serviceLevel);
  return rows.map((row) => {
    const add = Number(row.avg_daily_demand) || 0;
    const std = Number(row.demand_std) || 0;
    const onHand = Number(row.current_inventory) || 0;
    const unitCost = Number(row.unit_cost) || 0;
    const annual = Number(row.annual_demand) || 0;
    const ss = safetyStock(std, scenario.leadTimeDays, z);
    const rop = add * scenario.leadTimeDays + ss;
    const dos = add > 0 ? onHand / add : 0;
    const recommendedPosition = add * scenario.leadTimeDays + ss;
    const excessFlag = dos > 45 || (onHand > recommendedPosition && dos > 21);
    const excessUnits = excessFlag ? Math.max(onHand - recommendedPosition, 0) : 0;
    const risk = classifyRisk(onHand, rop, add, scenario.leadTimeDays);
    const rec = actionFor(risk, excessFlag);
    const holding = unitCost * scenario.holdingCostRate;
    return {
      ...row,
      lead_time_days: scenario.leadTimeDays,
      service_level: scenario.serviceLevel,
      safety_stock: ss,
      reorder_point: rop,
      days_of_supply: dos,
      stockout_risk: risk,
      excess_units: excessUnits,
      excess_value: excessUnits * unitCost,
      eoq: eoq(annual, scenario.orderingCost, holding),
      recommended_action: rec,
      recommended_order_qty: rec === "EXPEDITE" || rec === "REORDER" ? Math.max(eoq(annual, scenario.orderingCost, holding), rop - onHand) : 0,
    };
  });
}

export const defaultScenario: Scenario = {
  serviceLevel: 0.95,
  leadTimeDays: 7,
  orderingCost: 75,
  holdingCostRate: 0.25,
};
