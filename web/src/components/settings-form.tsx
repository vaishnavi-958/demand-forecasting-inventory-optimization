"use client";

import { useDashboard } from "@/components/dashboard-provider";

export function SettingsForm() {
  const { scenario, setScenario } = useDashboard();
  return (
    <div className="grid gap-3">
      <label className="block text-[12px] text-[#444]">
        <span className="flex justify-between">
          Service level <b>{(scenario.serviceLevel * 100).toFixed(1)}%</b>
        </span>
        <input
          type="range"
          min={90}
          max={99}
          step={1}
          value={Math.round(scenario.serviceLevel * 100)}
          className="mt-1 w-full accent-[#4472C4]"
          onChange={(e) => {
            const n = Number(e.target.value);
            const snapped = n >= 99 ? 0.99 : n >= 98 ? 0.975 : n >= 95 ? 0.95 : 0.9;
            setScenario({ ...scenario, serviceLevel: snapped });
          }}
        />
      </label>
      <label className="block text-[12px] text-[#444]">
        <span className="flex justify-between">
          Lead time (days) <b>{scenario.leadTimeDays}</b>
        </span>
        <input
          type="range"
          min={3}
          max={21}
          value={scenario.leadTimeDays}
          className="mt-1 w-full accent-[#4472C4]"
          onChange={(e) => setScenario({ ...scenario, leadTimeDays: Number(e.target.value) })}
        />
      </label>
      <label className="block text-[12px] text-[#444]">
        <span className="flex justify-between">
          Ordering cost <b>${scenario.orderingCost}</b>
        </span>
        <input
          type="range"
          min={25}
          max={200}
          step={5}
          value={scenario.orderingCost}
          className="mt-1 w-full accent-[#4472C4]"
          onChange={(e) => setScenario({ ...scenario, orderingCost: Number(e.target.value) })}
        />
      </label>
      <label className="block text-[12px] text-[#444]">
        <span className="flex justify-between">
          Holding cost rate <b>{Math.round(scenario.holdingCostRate * 100)}%</b>
        </span>
        <input
          type="range"
          min={10}
          max={40}
          value={Math.round(scenario.holdingCostRate * 100)}
          className="mt-1 w-full accent-[#4472C4]"
          onChange={(e) =>
            setScenario({ ...scenario, holdingCostRate: Number(e.target.value) / 100 })
          }
        />
      </label>
      <p className="text-[11px] text-[#888]">
        These are planner assumptions. They are not fields in the M5 dataset.
      </p>
    </div>
  );
}
