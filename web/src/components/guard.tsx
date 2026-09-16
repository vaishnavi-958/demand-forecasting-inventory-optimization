"use client";

import { useDashboard } from "@/components/dashboard-provider";

export function Guard({ children }: { children: React.ReactNode }) {
  const { loading, error, data } = useDashboard();
  if (loading) {
    return <p className="text-[13px] text-[#666]">Loading…</p>;
  }
  if (error || !data) {
    return (
      <div className="rounded-lg border border-amber-200 bg-amber-50 p-4 text-sm text-amber-950">
        {error ?? "No dashboard.json yet."} From the repo root run{" "}
        <code className="rounded bg-white px-1">python scripts/run_pipeline.py</code>.
      </div>
    );
  }
  return <>{children}</>;
}
