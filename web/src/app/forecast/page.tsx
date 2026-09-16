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
import { pct } from "@/lib/format";

function ForecastInner() {
  const { data } = useDashboard();
  const [sku, setSku] = useState("");
  const seriesKeys = useMemo(() => {
    if (!data) return [];
    const set = new Set(data.sku_forecasts.map((r) => `${r.item_id} | ${r.store_id}`));
    return Array.from(set).sort();
  }, [data]);
  if (!data) return null;
  const selected = sku || seriesKeys[0] || "";
  const drill = data.sku_forecasts.filter((r) => `${r.item_id} | ${r.store_id}` === selected);

  return (
    <div className="space-y-3">
      <div>
        <h2 className="text-[20px] font-normal text-[#222]">Demand forecast</h2>
        <p className="text-[13px] text-[#666]">
          Chronological 28-day holdout. Champion model is lowest WMAPE per SKU/store. Random splits are
          not used.
        </p>
      </div>
      <div className="grid gap-4 xl:grid-cols-2">
        <section className="border border-[#cfcfcf] bg-white p-3">
          <h3 className="mb-1 text-[13px] font-semibold text-[#222]">Forecast accuracy by model</h3>
          <p className="mb-2 text-[11px] text-[#888]">Accuracy = 1 − WMAPE; higher is better</p>
          <ChartBox className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data.model_summary}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e6e6e6" />
                <XAxis dataKey="model" tick={{ fontSize: 10 }} interval={0} angle={-20} textAnchor="end" height={60} />
                <YAxis tickFormatter={(v) => pct(Number(v), 0)} />
                <Tooltip formatter={(v) => pct(Number(v))} />
                <Bar dataKey="Forecast_Accuracy" fill="#ED7D31" name="Accuracy" />
              </BarChart>
            </ResponsiveContainer>
          </ChartBox>
        </section>
        <section className="border border-[#cfcfcf] bg-white p-3">
          <h3 className="mb-2 text-[13px] font-semibold text-[#222]">Where is error by department?</h3>
          <ChartBox className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data.dept_accuracy}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e6e6e6" />
                <XAxis dataKey="dept_id" tick={{ fontSize: 10 }} />
                <YAxis tickFormatter={(v) => pct(Number(v), 0)} />
                <Tooltip formatter={(v) => pct(Number(v))} />
                <Bar dataKey="WMAPE" fill="#4472C4" />
              </BarChart>
            </ResponsiveContainer>
          </ChartBox>
        </section>
      </div>
      <section className="border border-[#cfcfcf] bg-white p-3">
        <div className="mb-3 flex flex-wrap items-center justify-between gap-2">
          <h3 className="text-[13px] font-semibold text-[#222]">SKU-level actual vs forecast</h3>
          <select
            className="border border-[#cfcfcf] bg-white px-2 py-1 text-[13px]"
            value={selected}
            onChange={(e) => setSku(e.target.value)}
          >
            {seriesKeys.map((key) => (
              <option key={key}>{key}</option>
            ))}
          </select>
        </div>
        <ChartBox className="h-72">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={drill}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e6e6e6" />
              <XAxis dataKey="date" tick={{ fontSize: 11 }} minTickGap={16} />
              <YAxis />
              <Tooltip
                formatter={(value, name) => [
                  Number(value).toFixed(1),
                  String(name).charAt(0).toUpperCase() + String(name).slice(1),
                 ]}
              />
              <Legend />
              <Line dataKey="actual" stroke="#4472C4" strokeWidth={2} dot={false} isAnimationActive={false} />
              <Line dataKey="forecast" stroke="#ED7D31" strokeWidth={2} dot={false} isAnimationActive={false} />
            </LineChart>
          </ResponsiveContainer>
        </ChartBox>
      </section>
      <div className="overflow-x-auto border border-[#cfcfcf] bg-white">
        <table className="min-w-full text-left text-sm">
          <thead className="bg-[#f3f3f3] text-[11px] font-semibold text-[#444]">
            <tr>
              <th className="px-3 py-2">Model</th>
              <th className="px-3 py-2">Series</th>
              <th className="px-3 py-2">MAE</th>
              <th className="px-3 py-2">RMSE</th>
              <th className="px-3 py-2">WMAPE</th>
              <th className="px-3 py-2">Accuracy</th>
            </tr>
          </thead>
          <tbody>
            {data.model_summary.map((row) => (
              <tr key={row.model} className="border-t border-[#ececec]">
                <td className="px-3 py-2 font-medium">{row.model}</td>
                <td className="px-3 py-2">{row.series}</td>
                <td className="px-3 py-2">{row.MAE.toFixed(2)}</td>
                <td className="px-3 py-2">{row.RMSE.toFixed(2)}</td>
                <td className="px-3 py-2">{pct(row.WMAPE)}</td>
                <td className="px-3 py-2">{pct(row.Forecast_Accuracy)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default function ForecastPage() {
  return (
    <Guard>
      <ForecastInner />
    </Guard>
  );
}
