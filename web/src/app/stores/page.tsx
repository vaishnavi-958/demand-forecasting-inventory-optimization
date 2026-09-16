"use client";

import { useMemo, useState } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { Guard } from "@/components/guard";
import { ChartBox } from "@/components/chart-box";
import { useDashboard } from "@/components/dashboard-provider";
import { money, num, pct } from "@/lib/format";

function StoresInner() {
  const { data } = useDashboard();
  const [store, setStore] = useState("");

  const stores = useMemo(
    () => data?.store_performance.map((s) => s.store_id) ?? [],
    [data]
  );

  const weekly = useMemo(() => {
    if (!data) return [];

    const byWeek = new Map<string, Record<string, string | number>>();

    for (const row of data.category_weekly) {
      const current = byWeek.get(row.week) ?? { week: row.week };
      current[row.cat_id] = row.revenue;
      byWeek.set(row.week, current);
    }

    return Array.from(byWeek.values());
  }, [data]);

  if (!data) return null;

  const selected = store || stores[0] || "";

  const row = data.store_performance.find(
    (s) => s.store_id === selected
  );

  return (
    <div className="space-y-3">
      {/* Page header */}
      <div>
        <h2 className="text-[20px] font-normal text-[#222]">
          Store / region analysis
        </h2>

        <p className="text-[13px] text-[#666]">
          Select a store from the table to review forecast accuracy,
          inventory risk, and weekly category revenue.
        </p>
      </div>

      {/* Charts */}
      <div className="grid gap-4 xl:grid-cols-2">
        {/* Store exceptions */}
        <section className="border border-[#cfcfcf] bg-white p-3">
          <div className="mb-2">
            <h3 className="text-[13px] font-semibold text-[#222]">
              Inventory exceptions by store
            </h3>

            <p className="text-[11px] text-[#888]">
              Critical and high-risk SKU counts by store.
            </p>
          </div>

          <ChartBox className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={data.store_performance}
                margin={{
                  top: 8,
                  right: 10,
                  left: 0,
                  bottom: 4,
                }}
              >
                <CartesianGrid
                  strokeDasharray="3 3"
                  stroke="#e6e6e6"
                />

                <XAxis
                  dataKey="store_id"
                  tick={{ fontSize: 11 }}
                />

                <YAxis
                  allowDecimals={false}
                  tick={{ fontSize: 11 }}
                  label={{
                    value: "SKU count",
                    angle: -90,
                    position: "insideLeft",
                    style: {
                      textAnchor: "middle",
                      fontSize: 10,
                      fill: "#777",
                    },
                  }}
                />

                <Tooltip
                  formatter={(value, name) => [
                    Number(value),
                    String(name),
                  ]}
                />

                <Legend />

                <Bar
                  dataKey="critical"
                  fill="#C0504D"
                  name="Critical"
                />

                <Bar
                  dataKey="high"
                  fill="#ED7D31"
                  name="High"
                />
              </BarChart>
            </ResponsiveContainer>
          </ChartBox>
        </section>

        {/* Category revenue */}
        <section className="border border-[#cfcfcf] bg-white p-3">
          <div className="mb-2">
            <h3 className="text-[13px] font-semibold text-[#222]">
              Category weekly revenue
            </h3>

            <p className="text-[11px] text-[#888]">
              Weekly revenue trend across the three product categories.
            </p>
          </div>

          <ChartBox className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart
                data={weekly}
                margin={{
                  top: 8,
                  right: 10,
                  left: 0,
                  bottom: 4,
                }}
              >
                <CartesianGrid
                  strokeDasharray="3 3"
                  stroke="#e6e6e6"
                />

                <XAxis
                  dataKey="week"
                  hide
                />

                <YAxis
                  tick={{ fontSize: 11 }}
                  tickFormatter={(value) =>
                    `$${Number(value).toLocaleString()}`
                  }
                  width={65}
                />

                <Tooltip
                  formatter={(value, name) => [
                    `$${Number(value).toLocaleString()}`,
                    String(name),
                  ]}
                />

                <Legend />

                <Line
                  dataKey="FOODS"
                  stroke="#4472C4"
                  name="FOODS"
                  dot={false}
                  type="monotone"
                  strokeWidth={2}
                />

                <Line
                  dataKey="HOBBIES"
                  stroke="#ED7D31"
                  name="HOBBIES"
                  dot={false}
                  type="monotone"
                  strokeWidth={2}
                />

                <Line
                  dataKey="HOUSEHOLD"
                  stroke="#70AD47"
                  name="HOUSEHOLD"
                  dot={false}
                  type="monotone"
                  strokeWidth={2}
                />
              </LineChart>
            </ResponsiveContainer>
          </ChartBox>
        </section>
      </div>

      {/* Store performance table */}
      <section className="border border-[#cfcfcf] bg-white">
        <div className="border-b border-[#e5e5e5] px-3 py-2">
          <h3 className="text-[13px] font-semibold text-[#222]">
            Store performance
          </h3>

          <p className="text-[11px] text-[#888]">
            Select a row to review the store-level summary below.
          </p>
        </div>

        <div className="overflow-x-auto">
          <table className="min-w-full text-left text-sm">
            <thead className="bg-[#f3f3f3] text-[11px] font-semibold text-[#444]">
              <tr>
                <th className="px-3 py-2">Region</th>
                <th className="px-3 py-2">Store</th>
                <th className="px-3 py-2">Accuracy</th>
                <th className="px-3 py-2">WMAPE</th>
                <th className="px-3 py-2">Critical</th>
                <th className="px-3 py-2">Excess $</th>
                <th className="px-3 py-2">Median DOS</th>
              </tr>
            </thead>

            <tbody>
              {data.store_performance.map((s) => {
                const isSelected = s.store_id === selected;

                return (
                  <tr
                    key={s.store_id}
                    className={`cursor-pointer border-t border-[#ececec] ${
                      isSelected ? "bg-[#fff2cc]" : "hover:bg-[#fafafa]"
                    }`}
                    onClick={() => setStore(s.store_id)}
                  >
                    <td className="px-3 py-2">
                      {s.state_id}
                    </td>

                    <td className="px-3 py-2 font-medium">
                      {s.store_id}
                    </td>

                    <td className="px-3 py-2">
                      {pct(Number(s.avg_accuracy))}
                    </td>

                    <td className="px-3 py-2">
                      {pct(Number(s.avg_wmape))}
                    </td>

                    <td className="px-3 py-2">
                      {s.critical}
                    </td>

                    <td className="px-3 py-2">
                      {money(Number(s.excess_value))}
                    </td>

                    <td className="px-3 py-2">
                      {num(Number(s.avg_dos), 1)}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </section>

      {/* Selected store summary */}
      {row ? (
        <section className="border border-[#cfcfcf] bg-[#fafafa] p-3">
          <h3 className="mb-1 text-[13px] font-semibold text-[#222]">
            Selected store
          </h3>

          <p className="text-[12px] leading-5 text-[#555]">
            <b>{row.store_id}</b> ({row.state_id}) has{" "}
            <b>{row.critical}</b> critical SKUs,{" "}
            <b>{money(Number(row.excess_value))}</b> in excess inventory
            value, and champion forecast accuracy of{" "}
            <b>{pct(Number(row.avg_accuracy))}</b>.
          </p>
        </section>
      ) : null}

      {/* Interpretation */}
      <section className="border border-[#cfcfcf] bg-[#fafafa] p-3">
        <h3 className="mb-1 text-[13px] font-semibold text-[#222]">
          Planning interpretation
        </h3>

        <p className="text-[12px] leading-5 text-[#555]">
          Store-level performance combines forecast accuracy with inventory
          risk. Critical and high-risk exceptions identify locations that may
          need replenishment attention, while excess inventory value and
          median days of supply help identify locations where inventory
          coverage may warrant review.
        </p>
      </section>
    </div>
  );
}

export default function StoresPage() {
  return (
    <Guard>
      <StoresInner />
    </Guard>
  );
}