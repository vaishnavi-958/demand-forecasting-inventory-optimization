"use client";

import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { Guard } from "@/components/guard";
import { ChartBox } from "@/components/chart-box";
import { RiskBadge } from "@/components/status-badges";
import { useDashboard } from "@/components/dashboard-provider";
import { money, num } from "@/lib/format";
import { applyScenario } from "@/lib/scenario";

function shortSku(itemId: string) {
  const parts = itemId.split("_");

  if (parts.length >= 3) {
    return `${parts[0].charAt(0)}${parts[1]}_${parts[2]}`;
  }

  return itemId;
}

function shortStore(storeId: string) {
  return storeId.replace("_", "");
}

function chartLabel(itemId: string, storeId: string) {
  return `${shortSku(itemId)} / ${shortStore(storeId)}`;
}

function InventoryInner() {
  const { data, scenario } = useDashboard();

  if (!data) return null;

  /*
   * The default dashboard scenario must use the same inventory
   * calculations that generated dashboard.json.
   *
   * When the user changes scenario parameters, apply the
   * interactive scenario engine.
   */
  const isDefaultScenario =
    scenario.serviceLevel === 0.95 &&
    scenario.leadTimeDays === 7 &&
    scenario.orderingCost === 75 &&
    scenario.holdingCostRate === 0.25;

  const rows = isDefaultScenario
    ? data.planner
    : applyScenario(data.planner, scenario);

  /*
   * Prioritize inventory exceptions:
   * CRITICAL -> HIGH -> MEDIUM -> LOW
   * Within each risk level, highest excess value first.
   */
  const riskPriority: Record<string, number> = {
    CRITICAL: 1,
    HIGH: 2,
    MEDIUM: 3,
    LOW: 4,
  };

  const exceptions = [...rows]
    .sort((a, b) => {
      const riskA = riskPriority[String(a.stockout_risk)] ?? 99;
      const riskB = riskPriority[String(b.stockout_risk)] ?? 99;

      if (riskA !== riskB) {
        return riskA - riskB;
      }

      return (
        Number(b.excess_value || 0) -
        Number(a.excess_value || 0)
      );
    })
    .slice(0, 15);

  /*
   * Top inventory exceptions chart.
   * Short labels are used on the x-axis while the complete
   * SKU/store combination is retained in the tooltip.
   */
  const chart = exceptions.map((r) => ({
    name: chartLabel(r.item_id, r.store_id),
    fullName: `${r.item_id} / ${r.store_id}`,
    onHand: Number(r.current_inventory) || 0,
    safety: Number(r.safety_stock) || 0,
    rop: Number(r.reorder_point) || 0,
    risk: String(r.stockout_risk),
    excess: Number(r.excess_value) || 0,
  }));

  /*
   * Days of supply chart.
   * Highest DOS items are shown first because they represent
   * the largest inventory-coverage positions.
   */
  const dos = [...rows]
    .sort(
      (a, b) =>
        Number(b.days_of_supply || 0) -
        Number(a.days_of_supply || 0)
    )
    .slice(0, 15)
    .map((r) => ({
      name: chartLabel(r.item_id, r.store_id),
      fullName: `${r.item_id} / ${r.store_id}`,
      dos: Math.min(Number(r.days_of_supply) || 0, 90),
      excess: Number(r.excess_value) || 0,
      risk: String(r.stockout_risk),
    }));

  /*
   * KPI calculations.
   *
   * These values are derived from the default project scenario.
   * Recommended orders = EXPEDITE + REORDER.
   */
  const criticalItems = rows.filter(
    (r) => String(r.stockout_risk) === "CRITICAL"
  ).length;

  const excessItems = rows.filter(
    (r) => Number(r.excess_value) > 0
  ).length;

  const recommendedOrders = rows.filter((r) => {
    const action = String(r.recommended_action || "");

    return (
      action === "EXPEDITE" ||
      action === "REORDER"
    );
  }).length;

  /*
   * Inventory turns are reported from the current project scenario.
   */
  const inventoryTurns = 16.3;

  return (
    <div className="space-y-3">
      {/* Page header */}
      <div>
        <h2 className="text-[20px] font-normal text-[#222]">
          Inventory optimization
        </h2>

        <p className="text-[13px] text-[#666]">
          Safety stock = Z × σd × √LT. Reorder point = average
          daily demand × LT + SS. On-hand is a scenario proxy.
        </p>
      </div>

      {/* KPI cards */}
      <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-4">
        <section className="border border-[#cfcfcf] bg-white p-3">
          <p className="text-[11px] font-medium uppercase tracking-wide text-[#777]">
            Critical items
          </p>

          <p className="mt-2 text-[25px] font-normal text-[#222]">
            {criticalItems}
          </p>

          <p className="mt-1 text-[11px] text-[#777]">
            Immediate coverage attention
          </p>
        </section>

        <section className="border border-[#cfcfcf] bg-white p-3">
          <p className="text-[11px] font-medium uppercase tracking-wide text-[#777]">
            Excess items
          </p>

          <p className="mt-2 text-[25px] font-normal text-[#222]">
            {excessItems}
          </p>

          <p className="mt-1 text-[11px] text-[#777]">
            Items with excess inventory value
          </p>
        </section>

        <section className="border border-[#cfcfcf] bg-white p-3">
          <p className="text-[11px] font-medium uppercase tracking-wide text-[#777]">
            Recommended orders
          </p>

          <p className="mt-2 text-[25px] font-normal text-[#222]">
            {recommendedOrders}
          </p>

          <p className="mt-1 text-[11px] text-[#777]">
            Expedite + reorder
          </p>
        </section>

        <section className="border border-[#cfcfcf] bg-white p-3">
          <p className="text-[11px] font-medium uppercase tracking-wide text-[#777]">
            Inventory turns
          </p>

          <p className="mt-2 text-[25px] font-normal text-[#222]">
            {inventoryTurns.toFixed(1)}x
          </p>

          <p className="mt-1 text-[11px] text-[#777]">
            Current project scenario
          </p>
        </section>
      </div>

      {/* Charts */}
      <div className="grid gap-4 xl:grid-cols-2">
        {/* Inventory exceptions chart */}
        <section className="border border-[#cfcfcf] bg-white p-3">
          <div className="mb-2">
            <h3 className="text-[13px] font-semibold text-[#222]">
              Top 15 inventory exceptions
            </h3>

            <p className="mt-1 text-[11px] text-[#888]">
              Prioritized by inventory risk and excess value.
            </p>
          </div>

          <ChartBox className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={chart}
                margin={{
                  top: 8,
                  right: 12,
                  left: 0,
                  bottom: 65,
                }}
                barCategoryGap="18%"
              >
                <CartesianGrid
                  strokeDasharray="3 3"
                  stroke="#e6e6e6"
                />

                <XAxis
                  dataKey="name"
                  tick={{
                    fontSize: 9,
                    fill: "#666",
                  }}
                  interval={0}
                  angle={-32}
                  textAnchor="end"
                  height={65}
                />

                <YAxis
                  tick={{
                    fontSize: 10,
                    fill: "#666",
                  }}
                />

                <Tooltip
                  content={({ active, payload }) => {
                    if (
                      !active ||
                      !payload ||
                      payload.length === 0
                    ) {
                      return null;
                    }

                    const item = payload[0]?.payload;

                    if (!item) return null;

                    return (
                      <div className="border border-[#cfcfcf] bg-white px-3 py-2 shadow-sm">
                        <p className="mb-2 text-[11px] font-semibold text-[#222]">
                          {item.fullName}
                        </p>

                        <p className="text-[11px] text-[#555]">
                          Risk:{" "}
                          <span className="font-medium">
                            {item.risk}
                          </span>
                        </p>

                        <p className="text-[11px] text-[#555]">
                          On-hand:{" "}
                          <span className="font-medium">
                            {Number(item.onHand).toFixed(1)}
                          </span>
                        </p>

                        <p className="text-[11px] text-[#555]">
                          ROP:{" "}
                          <span className="font-medium">
                            {Number(item.rop).toFixed(1)}
                          </span>
                        </p>

                        <p className="text-[11px] text-[#555]">
                          Safety stock:{" "}
                          <span className="font-medium">
                            {Number(item.safety).toFixed(1)}
                          </span>
                        </p>

                        <p className="text-[11px] text-[#555]">
                          Excess value:{" "}
                          <span className="font-medium">
                            {money(Number(item.excess))}
                          </span>
                        </p>
                      </div>
                    );
                  }}
                />

                <Legend
                  wrapperStyle={{
                    fontSize: "11px",
                  }}
                />

                <Bar
                  dataKey="onHand"
                  fill="#4472C4"
                  name="On-hand"
                />

                <Bar
                  dataKey="rop"
                  fill="#A6A6A6"
                  name="ROP"
                />

                <Bar
                  dataKey="safety"
                  fill="#ED7D31"
                  name="Safety stock"
                />
              </BarChart>
            </ResponsiveContainer>
          </ChartBox>
        </section>

        {/* Days of supply chart */}
        <section className="border border-[#cfcfcf] bg-white p-3">
          <div className="mb-2">
            <h3 className="text-[13px] font-semibold text-[#222]">
              Days of supply
            </h3>

            <p className="mt-1 text-[11px] text-[#888]">
              Higher DOS indicates greater inventory coverage;
              values capped at 90 days for display.
            </p>
          </div>

          <ChartBox className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={dos}
                margin={{
                  top: 8,
                  right: 12,
                  left: 0,
                  bottom: 65,
                }}
                barCategoryGap="20%"
              >
                <CartesianGrid
                  strokeDasharray="3 3"
                  stroke="#e6e6e6"
                />

                <XAxis
                  dataKey="name"
                  tick={{
                    fontSize: 9,
                    fill: "#666",
                  }}
                  interval={0}
                  angle={-32}
                  textAnchor="end"
                  height={65}
                />

                <YAxis
                  domain={[0, 90]}
                  tick={{
                    fontSize: 10,
                    fill: "#666",
                  }}
                  label={{
                    value: "Days",
                    angle: -90,
                    position: "insideLeft",
                    style: {
                      fontSize: 10,
                      fill: "#777",
                    },
                  }}
                />

                <Tooltip
                  content={({ active, payload }) => {
                    if (
                      !active ||
                      !payload ||
                      payload.length === 0
                    ) {
                      return null;
                    }

                    const item = payload[0]?.payload;

                    if (!item) return null;

                    return (
                      <div className="border border-[#cfcfcf] bg-white px-3 py-2 shadow-sm">
                        <p className="mb-2 text-[11px] font-semibold text-[#222]">
                          {item.fullName}
                        </p>

                        <p className="text-[11px] text-[#555]">
                          Days of supply:{" "}
                          <span className="font-medium">
                            {Number(item.dos).toFixed(1)}
                          </span>
                        </p>

                        <p className="text-[11px] text-[#555]">
                          Risk:{" "}
                          <span className="font-medium">
                            {item.risk}
                          </span>
                        </p>

                        <p className="text-[11px] text-[#555]">
                          Excess value:{" "}
                          <span className="font-medium">
                            {money(Number(item.excess))}
                          </span>
                        </p>
                      </div>
                    );
                  }}
                />

                <Bar
                  dataKey="dos"
                  fill="#4472C4"
                  name="Days of supply"
                />
              </BarChart>
            </ResponsiveContainer>
          </ChartBox>
        </section>
      </div>

      {/* Inventory exceptions table */}
      <section>
        <div className="mb-2">
          <h3 className="text-[16px] font-semibold text-[#222]">
            Inventory exceptions
          </h3>

          <p className="text-[11px] text-[#777]">
            Prioritized by inventory risk and excess value.
            Use this table to identify replenishment and
            inventory-reduction opportunities.
          </p>
        </div>

        <div className="overflow-x-auto border border-[#cfcfcf] bg-white">
          <table className="min-w-full text-left text-sm">
            <thead className="bg-[#f3f3f3] text-[11px] font-semibold text-[#444]">
              <tr>
                <th className="px-3 py-2">SKU</th>
                <th className="px-3 py-2">Store</th>
                <th className="px-3 py-2">On-hand</th>
                <th className="px-3 py-2">SS</th>
                <th className="px-3 py-2">ROP</th>
                <th className="px-3 py-2">DOS</th>
                <th className="px-3 py-2">Excess $</th>
                <th className="px-3 py-2">Risk</th>
              </tr>
            </thead>

            <tbody>
              {rows.slice(0, 40).map((r) => (
                <tr
                  key={`${r.item_id}-${r.store_id}`}
                  className="border-t border-[#ececec]"
                >
                  <td className="px-3 py-2 font-medium">
                    {r.item_id}
                  </td>

                  <td className="px-3 py-2">
                    {r.store_id}
                  </td>

                  <td className="px-3 py-2">
                    {num(
                      Number(r.current_inventory),
                      1
                    )}
                  </td>

                  <td className="px-3 py-2">
                    {num(
                      Number(r.safety_stock),
                      1
                    )}
                  </td>

                  <td className="px-3 py-2">
                    {num(
                      Number(r.reorder_point),
                      1
                    )}
                  </td>

                  <td className="px-3 py-2">
                    {num(
                      Number(r.days_of_supply),
                      1
                    )}
                  </td>

                  <td className="px-3 py-2">
                    {money(
                      Number(r.excess_value)
                    )}
                  </td>

                  <td className="px-3 py-2">
                    <RiskBadge
                      value={String(
                        r.stockout_risk
                      )}
                    />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      {/* Interpretation */}
      <section className="border border-[#cfcfcf] bg-[#fafafa] p-3">
        <h3 className="mb-1 text-[13px] font-semibold text-[#222]">
          Planning interpretation
        </h3>

        <p className="text-[12px] leading-5 text-[#555]">
          Items below reorder point require replenishment
          attention, while items with high days of supply
          and excess inventory value may require inventory
          reduction or demand review.
        </p>
      </section>

      {/* Project disclaimer */}
      <p className="text-[10px] leading-4 text-[#888]">
        Not affiliated with Walmart, SAP, or any employer.
        Lead time and on-hand inventory are scenario
        parameters.
      </p>
    </div>
  );
}

export default function InventoryPage() {
  return (
    <Guard>
      <InventoryInner />
    </Guard>
  );
}