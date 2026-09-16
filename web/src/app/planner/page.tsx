"use client";

import { useMemo, useState } from "react";
import { Guard } from "@/components/guard";
import { ActionBadge, RiskBadge } from "@/components/status-badges";
import { useDashboard } from "@/components/dashboard-provider";
import { applyScenario } from "@/lib/scenario";
import { money, num, pct } from "@/lib/format";

function PlannerInner() {
  const { data, scenario } = useDashboard();

  const [action, setAction] = useState("ALL");
  const [risk, setRisk] = useState("ALL");

  const rows = useMemo(() => {
    if (!data) return [];

    const isDefaultScenario =
      scenario.serviceLevel === 0.95 &&
      scenario.leadTimeDays === 7 &&
      scenario.orderingCost === 75 &&
      scenario.holdingCostRate === 0.25;

    return isDefaultScenario
      ? data.planner
      : applyScenario(data.planner, scenario);
  }, [data, scenario]);

  if (!data) return null;

  const filtered = rows.filter((r) => {
    if (action !== "ALL" && r.recommended_action !== action) {
      return false;
    }

    if (risk !== "ALL" && r.stockout_risk !== risk) {
      return false;
    }

    return true;
  });

  const counts = rows.reduce<Record<string, number>>((acc, r) => {
    const key = String(r.recommended_action);
    acc[key] = (acc[key] ?? 0) + 1;
    return acc;
  }, {});

  return (
    <div className="space-y-3">
      {/* Page Header */}
      <div>
        <h2 className="text-[20px] font-normal text-[#222]">
          Planner action center
        </h2>

        <p className="text-[13px] text-[#666]">
          Exception workbench: expedite coverage gaps, reorder below ROP,
          destock excess, otherwise monitor. Open the three-line menu in the
          header to change service level and lead time.
        </p>
      </div>

      {/* Action Summary */}
      <div className="grid gap-3 sm:grid-cols-5">
        {[
          "EXPEDITE",
          "REORDER",
          "MONITOR",
          "REDUCE INVENTORY",
          "NO ACTION",
        ].map((key) => (
          <button
            key={key}
            onClick={() =>
              setAction(action === key ? "ALL" : key)
            }
            className={`border bg-white px-2 py-2 text-left text-[13px] ${
              action === key
                ? "border-[#4472C4]"
                : "border-[#cfcfcf]"
            }`}
          >
            <p className="text-[11px] text-[#666]">{key}</p>

            <p className="text-[18px] font-semibold text-[#222]">
              {counts[key] ?? 0}
            </p>
          </button>
        ))}
      </div>

      {/* Risk Filters */}
      <div className="flex flex-wrap gap-2">
        {["ALL", "CRITICAL", "HIGH", "MEDIUM", "LOW"].map((key) => (
          <button
            key={key}
            onClick={() => setRisk(key)}
            className={`border px-2 py-1 text-[12px] ${
              risk === key
                ? "border-[#4472C4] bg-[#4472C4] text-white"
                : "border-[#cfcfcf] bg-white"
            }`}
          >
            {key}
          </button>
        ))}
      </div>

      {/* Planner Table */}
      <div className="overflow-x-auto border border-[#cfcfcf] bg-white">
        <table className="min-w-full text-left text-xs md:text-sm">
          <thead className="bg-[#f3f3f3] text-[11px] font-semibold text-[#444]">
            <tr>
              <th className="px-3 py-2">SKU</th>
              <th className="px-3 py-2">Store</th>
              <th className="px-3 py-2">Dept</th>
              <th className="px-3 py-2">ABC</th>
              <th className="px-3 py-2">Accuracy</th>
              <th className="px-3 py-2">On-hand</th>
              <th className="px-3 py-2">SS</th>
              <th className="px-3 py-2">ROP</th>
              <th className="px-3 py-2">DOS</th>
              <th className="px-3 py-2">Risk</th>
              <th className="px-3 py-2">Excess $</th>
              <th className="px-3 py-2">Action</th>
            </tr>
          </thead>

          <tbody>
            {filtered.map((r) => {
              const accuracy = Number(r.Forecast_Accuracy);

              return (
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
                    {r.dept_id}
                  </td>

                  <td className="px-3 py-2">
                    {r.abc_class}
                  </td>

                  {/* Forecast Accuracy */}
                  <td className="px-3 py-2">
                    {Number.isFinite(accuracy) && accuracy > 0
                      ? pct(accuracy)
                      : "N/A"}
                  </td>

                  {/* Inventory Metrics */}
                  <td className="px-3 py-2">
                    {num(Number(r.current_inventory), 1)}
                  </td>

                  <td className="px-3 py-2">
                    {num(Number(r.safety_stock), 1)}
                  </td>

                  <td className="px-3 py-2">
                    {num(Number(r.reorder_point), 1)}
                  </td>

                  <td className="px-3 py-2">
                    {num(Number(r.days_of_supply), 1)}
                  </td>

                  {/* Risk */}
                  <td className="px-3 py-2">
                    <RiskBadge
                      value={String(r.stockout_risk)}
                    />
                  </td>

                  {/* Excess Inventory */}
                  <td className="px-3 py-2">
                    {money(Number(r.excess_value))}
                  </td>

                  {/* Recommended Action */}
                  <td className="px-3 py-2">
                    <ActionBadge
                      value={String(r.recommended_action)}
                    />
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* Empty State */}
      {filtered.length === 0 && (
        <div className="border border-[#cfcfcf] bg-white px-4 py-6 text-center text-[13px] text-[#666]">
          No planner records match the selected action and risk filters.
        </div>
      )}

      {/* Interpretation */}
      <div className="border border-[#cfcfcf] bg-white p-3">
        <h3 className="mb-1 text-[13px] font-semibold text-[#222]">
          Planning interpretation
        </h3>

        <p className="text-[12px] leading-5 text-[#666]">
          EXPEDITE identifies critical coverage gaps, REORDER identifies
          inventory below the reorder point, REDUCE INVENTORY identifies
          excess positions, and MONITOR highlights medium-risk positions.
          Forecast accuracy is shown only when an evaluated forecast result
          is available; otherwise the dashboard displays N/A.
        </p>
      </div>

      {/* Data Note */}
      <p className="text-[11px] text-[#888]">
        Inventory position is a scenario proxy generated by the project
        pipeline, not retailer-reported on-hand inventory.
      </p>
    </div>
  );
}

export default function PlannerPage() {
  return (
    <Guard>
      <PlannerInner />
    </Guard>
  );
}