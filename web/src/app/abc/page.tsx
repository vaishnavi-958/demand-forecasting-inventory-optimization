"use client";

import {
  Bar,
  BarChart,
  CartesianGrid,
  ComposedChart,
  Legend,
  Line,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { Guard } from "@/components/guard";
import { ChartBox } from "@/components/chart-box";
import { useDashboard } from "@/components/dashboard-provider";
import { money, num } from "@/lib/format";

function shortSku(itemId: string) {
  const parts = itemId.split("_");

  if (parts.length >= 3) {
    return `${parts[0].charAt(0)}${parts[1]}-${parts[2]}`;
  }

  return itemId;
}

function shortStore(storeId: string) {
  return storeId.replace("_", "");
}

function chartLabel(itemId: string, storeId: string) {
  return `${shortSku(itemId)} / ${shortStore(storeId)}`;
}

function ABCInner() {
  const { data } = useDashboard();

  if (!data) return null;

  /*
   * Annual consumption value:
   * Annual demand × unit-cost proxy
   */
  const valuedRows = data.planner
    .map((r) => ({
      ...r,
      annualValue:
        (Number(r.annual_demand) || 0) *
        (Number(r.unit_cost) || 0),
    }))
    .sort((a, b) => b.annualValue - a.annualValue);

  /*
   * Calculate cumulative annual consumption value
   * across the complete inventory population.
   */
  const totalAnnualValue = valuedRows.reduce(
    (sum, r) => sum + r.annualValue,
    0
  );

  let runningValue = 0;

  const paretoRows = valuedRows.map((r, index) => {
    runningValue += r.annualValue;

    return {
      ...r,
      rank: index + 1,
      cumulativePct:
        totalAnnualValue > 0
          ? runningValue / totalAnnualValue
          : 0,
      label: chartLabel(r.item_id, r.store_id),
      fullName: `${r.item_id} / ${r.store_id}`,
    };
  });

  /*
   * Display top 40 value-driving SKU/store combinations.
   */
  const paretoChart = paretoRows.slice(0, 40);

  /*
   * ABC class summary.
   */
  const classes = ["A", "B", "C"];

  const classSummary = classes.map((abcClass) => {
    const subset = data.planner.filter(
      (r) => String(r.abc_class) === abcClass
    );

    const annualValue = subset.reduce(
      (sum, r) =>
        sum +
        (Number(r.annual_demand) || 0) *
          (Number(r.unit_cost) || 0),
      0
    );

    const avgEoq =
      subset.length > 0
        ? subset.reduce(
            (sum, r) => sum + (Number(r.eoq) || 0),
            0
          ) / subset.length
        : 0;

    return {
      className: abcClass,
      skuCount: subset.length,
      annualValue,
      avgEoq,
      valueShare:
        totalAnnualValue > 0
          ? annualValue / totalAnnualValue
          : 0,
    };
  });

  /*
   * A-class detail rows.
   */
  const aClassRows = valuedRows
    .filter((r) => String(r.abc_class) === "A")
    .slice(0, 20);

  const aClassCount =
    classSummary.find((r) => r.className === "A")?.skuCount ?? 0;

  const bClassCount =
    classSummary.find((r) => r.className === "B")?.skuCount ?? 0;

  const cClassCount =
    classSummary.find((r) => r.className === "C")?.skuCount ?? 0;

  const aClassValueShare =
    classSummary.find((r) => r.className === "A")?.valueShare ?? 0;

  return (
    <div className="space-y-3">

      {/* Header */}
      <div>
        <h2 className="text-[20px] font-normal text-[#222]">
          ABC and EOQ
        </h2>

        <p className="text-[13px] text-[#666]">
          ABC uses cumulative annual consumption value
          (demand × unit-cost proxy). EOQ uses scenario
          ordering and holding costs — not retailer PO actuals.
        </p>
      </div>

      {/* KPI cards */}
      <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-4">

        <section className="border border-[#cfcfcf] bg-white p-3">
          <p className="text-[11px] font-medium uppercase tracking-wide text-[#777]">
            A-class SKU / store
          </p>

          <p className="mt-2 text-[25px] font-normal text-[#222]">
            {aClassCount}
          </p>

          <p className="mt-1 text-[11px] text-[#777]">
            {num(aClassValueShare * 100, 1)}% of annual value
          </p>
        </section>

        <section className="border border-[#cfcfcf] bg-white p-3">
          <p className="text-[11px] font-medium uppercase tracking-wide text-[#777]">
            B-class SKU / store
          </p>

          <p className="mt-2 text-[25px] font-normal text-[#222]">
            {bClassCount}
          </p>

          <p className="mt-1 text-[11px] text-[#777]">
            Moderate value contribution
          </p>
        </section>

        <section className="border border-[#cfcfcf] bg-white p-3">
          <p className="text-[11px] font-medium uppercase tracking-wide text-[#777]">
            C-class SKU / store
          </p>

          <p className="mt-2 text-[25px] font-normal text-[#222]">
            {cClassCount}
          </p>

          <p className="mt-1 text-[11px] text-[#777]">
            Lower value contribution
          </p>
        </section>

        <section className="border border-[#cfcfcf] bg-white p-3">
          <p className="text-[11px] font-medium uppercase tracking-wide text-[#777]">
            Annual consumption value
          </p>

          <p className="mt-2 text-[25px] font-normal text-[#222]">
            {money(totalAnnualValue)}
          </p>

          <p className="mt-1 text-[11px] text-[#777]">
            Demand × unit-cost proxy
          </p>
        </section>

      </div>

      {/* Charts */}
      <div className="grid gap-4 xl:grid-cols-2">

        {/* Pareto chart */}
        <section className="border border-[#cfcfcf] bg-white p-3">

          <div className="mb-2">
            <h3 className="text-[13px] font-semibold text-[#222]">
              Pareto of annual consumption value
            </h3>

            <p className="mt-1 text-[11px] text-[#888]">
              Top 40 SKU/store combinations ranked by annual
              consumption value; cumulative percentage uses the
              full inventory population.
            </p>
          </div>

          <ChartBox className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <ComposedChart
                data={paretoChart}
                margin={{
                  top: 8,
                  right: 12,
                  left: 4,
                  bottom: 70,
                }}
              >

                <CartesianGrid
                  strokeDasharray="3 3"
                  stroke="#e6e6e6"
                />

                <XAxis
                  dataKey="label"
                  tick={{
                    fontSize: 8,
                    fill: "#666",
                  }}
                  interval={2}
                  angle={-30}
                  textAnchor="end"
                  height={70}
                />

                <YAxis
                  yAxisId="value"
                  tick={{
                    fontSize: 10,
                    fill: "#666",
                  }}
                  tickFormatter={(value) =>
                    money(Number(value))
                  }
                />

                <YAxis
                  yAxisId="percent"
                  orientation="right"
                  domain={[0, 1]}
                  tick={{
                    fontSize: 10,
                    fill: "#666",
                  }}
                  tickFormatter={(value) =>
                    `${Math.round(Number(value) * 100)}%`
                  }
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
                          Rank:{" "}
                          <span className="font-medium">
                            {item.rank}
                          </span>
                        </p>

                        <p className="text-[11px] text-[#555]">
                          Annual value:{" "}
                          <span className="font-medium">
                            {money(
                              Number(item.annualValue)
                            )}
                          </span>
                        </p>

                        <p className="text-[11px] text-[#555]">
                          Cumulative value:{" "}
                          <span className="font-medium">
                            {num(
                              Number(item.cumulativePct) * 100,
                              1
                            )}
                            %
                          </span>
                        </p>

                        <p className="text-[11px] text-[#555]">
                          ABC class:{" "}
                          <span className="font-medium">
                            {item.abc_class}
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
                  yAxisId="value"
                  dataKey="annualValue"
                  fill="#4472C4"
                  name="Annual value"
                />

                <Line
                  yAxisId="percent"
                  type="monotone"
                  dataKey="cumulativePct"
                  stroke="#ED7D31"
                  strokeWidth={2}
                  dot={false}
                  name="Cumulative %"
                />

              </ComposedChart>
            </ResponsiveContainer>
          </ChartBox>

        </section>

        {/* EOQ comparison */}
        <section className="border border-[#cfcfcf] bg-white p-3">

          <div className="mb-2">
            <h3 className="text-[13px] font-semibold text-[#222]">
              SKU count and average EOQ by class
            </h3>

            <p className="mt-1 text-[11px] text-[#888]">
              Separate axes keep SKU count and EOQ readable
              despite their different scales.
            </p>
          </div>

          <ChartBox className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <ComposedChart
                data={classSummary}
                margin={{
                  top: 8,
                  right: 12,
                  left: 4,
                  bottom: 25,
                }}
              >

                <CartesianGrid
                  strokeDasharray="3 3"
                  stroke="#e6e6e6"
                />

                <XAxis
                  dataKey="className"
                  tick={{
                    fontSize: 11,
                    fill: "#666",
                  }}
                />

                <YAxis
                  yAxisId="count"
                  tick={{
                    fontSize: 10,
                    fill: "#666",
                  }}
                  label={{
                    value: "SKU/store count",
                    angle: -90,
                    position: "insideLeft",
                    style: {
                      fontSize: 10,
                      fill: "#777",
                    },
                  }}
                />

                <YAxis
                  yAxisId="eoq"
                  orientation="right"
                  tick={{
                    fontSize: 10,
                    fill: "#666",
                  }}
                  label={{
                    value: "Average EOQ",
                    angle: 90,
                    position: "insideRight",
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
                          ABC Class {item.className}
                        </p>

                        <p className="text-[11px] text-[#555]">
                          SKU/store count:{" "}
                          <span className="font-medium">
                            {item.skuCount}
                          </span>
                        </p>

                        <p className="text-[11px] text-[#555]">
                          Average EOQ:{" "}
                          <span className="font-medium">
                            {num(
                              Number(item.avgEoq),
                              0
                            )}
                          </span>
                        </p>

                        <p className="text-[11px] text-[#555]">
                          Annual value:{" "}
                          <span className="font-medium">
                            {money(
                              Number(item.annualValue)
                            )}
                          </span>
                        </p>

                        <p className="text-[11px] text-[#555]">
                          Value share:{" "}
                          <span className="font-medium">
                            {num(
                              Number(item.valueShare) * 100,
                              1
                            )}
                            %
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
                  yAxisId="count"
                  dataKey="skuCount"
                  fill="#4472C4"
                  name="SKU/store count"
                  barSize={55}
                />

                <Line
                  yAxisId="eoq"
                  type="monotone"
                  dataKey="avgEoq"
                  stroke="#ED7D31"
                  strokeWidth={2}
                  dot={{
                    r: 4,
                  }}
                  name="Average EOQ"
                />

              </ComposedChart>
            </ResponsiveContainer>
          </ChartBox>

        </section>

      </div>

      {/* A-class table */}
      <section>

        <div className="mb-2">
          <h3 className="text-[16px] font-semibold text-[#222]">
            A-class inventory
          </h3>

          <p className="text-[11px] text-[#777]">
            Highest-value SKU/store combinations. These items
            receive tighter inventory monitoring because changes
            in demand or supply can have a larger financial impact.
          </p>
        </div>

        <div className="overflow-x-auto border border-[#cfcfcf] bg-white">

          <table className="min-w-full text-left text-sm">

            <thead className="bg-[#f3f3f3] text-[11px] font-semibold text-[#444]">
              <tr>
                <th className="px-3 py-2">A-class SKU</th>
                <th className="px-3 py-2">Store</th>
                <th className="px-3 py-2">EOQ</th>
                <th className="px-3 py-2">On-hand</th>
                <th className="px-3 py-2">ROP</th>
                <th className="px-3 py-2">SS</th>
              </tr>
            </thead>

            <tbody>
              {aClassRows.map((r) => (
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
                    {num(Number(r.eoq), 0)}
                  </td>

                  <td className="px-3 py-2">
                    {num(
                      Number(r.current_inventory),
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
                      Number(r.safety_stock),
                      1
                    )}
                  </td>
                </tr>
              ))}
            </tbody>

          </table>

        </div>
      </section>

            {/* Planning interpretation */}
      <section className="border border-[#cfcfcf] bg-[#fafafa] p-3">
        <h3 className="mb-1 text-[13px] font-semibold text-[#222]">
          Planning interpretation
        </h3>

        <p className="text-[12px] leading-5 text-[#555]">
          ABC classification focuses inventory-control effort on SKU/store
          combinations with greater annual consumption value. EOQ provides a
          scenario-based order quantity that balances ordering and holding
          costs. A-class items can therefore receive tighter review of demand,
          replenishment, and supplier performance.
        </p>
      </section>

      {/* Single project disclaimer */}
      <p className="text-[10px] leading-4 text-[#888]">
        Not affiliated with Walmart, SAP, or any employer. Annual value uses a
        unit-cost proxy, while EOQ, lead time, and on-hand inventory are
        scenario parameters rather than retailer purchase-order or operational data.
      </p>

    </div>
  );
}

export default function ABCPage() {
  return (
    <Guard>
      <ABCInner />
    </Guard>
  );
}