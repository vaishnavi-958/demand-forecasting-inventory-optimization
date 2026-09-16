"use client";

import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
  BarChart,
  Bar,
} from "recharts";
import { Guard } from "@/components/guard";
import { ChartBox } from "@/components/chart-box";
import { KpiCard } from "@/components/kpi-card";
import { useDashboard } from "@/components/dashboard-provider";
import { compact, money, pct } from "@/lib/format";

function ExecutiveInner() {
  const { data } = useDashboard();
  if (!data) return null;
  const k = data.kpis;
  const insights = data.insights as {
    best_model_by_mean_wmape?: string;
    lowest_accuracy_department?: string;
    highest_risk_store?: string;
    improvement_vs_baseline?: number;
    baseline_accuracy?: number;
    best_model_accuracy?: number;
  };
  const trend = data.sales_trend.map((d) => ({
    date: d.date.slice(5),
    revenue: d.revenue,
  }));
  const fcst = data.forecast_vs_actual.map((d) => ({
    date: d.date.slice(5),
    actual: d.actual,
    forecast: d.forecast,
  }));

  return (
    <div className="space-y-3">
      <div>
        <h2 className="text-[20px] font-normal text-[#222]">Executive supply chain overview</h2>
        <p className="text-[13px] text-[#666]">
          What happened, what is likely to happen, and where planners should intervene. Figures are
          computed from this pipeline run — not hardcoded.
        </p>
      </div>
      <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
        <KpiCard label="Total sales" value={money(k.total_sales)} hint={`Through ${k.as_of}`} />
        <KpiCard
          label="Forecast accuracy"
          value={pct(k.forecast_accuracy)}
          hint={`Champion mean · baseline ${pct(k.baseline_accuracy)}`}
        />
        <KpiCard label="WMAPE" value={pct(k.wmape)} hint="Champion models, 28-day holdout" />
        <KpiCard
          label="Inventory turns"
          value={k.inventory_turns.toFixed(1)}
          hint="Proxy: annual value / scenario on-hand"
        />
        <KpiCard
          label="Stockout risk"
          value={pct(k.stockout_risk_pct)}
          hint="CRITICAL + HIGH share of SKU/store"
          alert={k.stockout_risk_pct > 0.2}
        />
        <KpiCard label="Excess inventory value" value={money(k.excess_inventory_value)} />
        <KpiCard label="A-class SKU share" value={pct(k.a_class_sku_pct)} hint="By series count" />
        <KpiCard label="Recommended orders" value={String(k.recommended_orders)} hint="Expedite + reorder" />
      </div>

      <div className="grid gap-4 xl:grid-cols-2">
        <section className="border border-[#cfcfcf] bg-white p-3">
          <h3 className="mb-1 text-[13px] font-semibold text-[#222]">How is sell-through trending?</h3>
          <p className="mb-2 text-[11px] text-[#888]">Daily revenue, last 180 days</p>
          <ChartBox className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={trend}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e6e6e6" />
                <XAxis dataKey="date" tick={{ fontSize: 11 }} minTickGap={24} />
                <YAxis tick={{ fontSize: 11 }} tickFormatter={(v) => compact(Number(v))} />
                <Tooltip formatter={(v) => money(Number(v))} />
                <Line type="monotone" dataKey="revenue" stroke="#4472C4" dot={false} strokeWidth={2} isAnimationActive={false} />
              </LineChart>
            </ResponsiveContainer>
          </ChartBox>
        </section>
        <section className="border border-[#cfcfcf] bg-white p-3">
          <h3 className="mb-1 text-[13px] font-semibold text-[#222]">Did the champion forecast track actuals?</h3>
          <p className="mb-2 text-[11px] text-[#888]">Holdout window, best model per series</p>
          <ChartBox className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={fcst}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e6e6e6" />
                <XAxis dataKey="date" tick={{ fontSize: 11 }} />
                <YAxis tick={{ fontSize: 11 }} />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="actual" stroke="#4472C4" strokeWidth={2} dot={false} isAnimationActive={false} />
                <Line type="monotone" dataKey="forecast" stroke="#ED7D31" strokeWidth={2} dot={false} isAnimationActive={false} />
              </LineChart>
            </ResponsiveContainer>
          </ChartBox>
        </section>
      </div>

      <div className="grid gap-4 xl:grid-cols-2">
        <section className="border border-[#cfcfcf] bg-white p-3">
          <h3 className="mb-1 text-[13px] font-semibold text-[#222]">Where is stockout risk?</h3>
          <ChartBox className="h-56">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data.risk_summary}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e6e6e6" />
                <XAxis dataKey="stockout_risk" tick={{ fontSize: 11 }} />
                <YAxis tick={{ fontSize: 11 }} />
                <Tooltip />
                <Bar dataKey="sku_count" fill="#4472C4" radius={0} isAnimationActive={false} />
              </BarChart>
            </ResponsiveContainer>
          </ChartBox>
        </section>
        <section className="border border-[#cfcfcf] bg-white p-3">
          <h3 className="mb-1 text-[13px] font-semibold text-[#222]">Where is excess value concentrated?</h3>
          <ChartBox className="h-56">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data.excess_by_category}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e6e6e6" />
                <XAxis dataKey="cat_id" tick={{ fontSize: 11 }} />
                <YAxis tick={{ fontSize: 11 }} tickFormatter={(v) => compact(Number(v))} />
                <Tooltip formatter={(v) => money(Number(v))} />
                <Bar dataKey="excess_value" fill="#ED7D31" radius={0} isAnimationActive={false} />
              </BarChart>
            </ResponsiveContainer>
          </ChartBox>
        </section>
      </div>

      <section className="border border-[#cfcfcf] bg-white p-3 text-[13px]">
        <h3 className="mb-2 text-[13px] font-semibold text-[#222]">Notes from this run</h3>
        <ul className="list-disc space-y-1 pl-5 text-[13px] text-[#444]">
          <li>
            Champion mean accuracy {pct(Number(insights.best_model_accuracy))} vs naive baseline{" "}
            {pct(Number(insights.baseline_accuracy))} (
            {pct(Number(insights.improvement_vs_baseline))} improvement).
          </li>
          <li>
            Lowest mean WMAPE model: {String(insights.best_model_by_mean_wmape ?? "n/a")}.
          </li>
          <li>
            Weakest department on champion accuracy:{" "}
            {String(insights.lowest_accuracy_department ?? "n/a")}.
          </li>
          <li>
            Store with the most CRITICAL exceptions: {String(insights.highest_risk_store ?? "n/a")}.
          </li>
        </ul>
      </section>
    </div>
  );
}

export default function Page() {
  return (
    <Guard>
      <ExecutiveInner />
    </Guard>
  );
}
