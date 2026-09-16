"use client";

import { createContext, useContext, useMemo, useState } from "react";
import { defaultScenario } from "@/lib/scenario";
import type { DashboardData, Scenario } from "@/lib/types";

type Ctx = {
  data: DashboardData | null;
  error: string | null;
  loading: boolean;
  scenario: Scenario;
  setScenario: (next: Scenario) => void;
};

const DashboardContext = createContext<Ctx | null>(null);

export function DashboardProvider({
  children,
  initialData,
}: {
  children: React.ReactNode;
  initialData: DashboardData | null;
}) {
  const [scenario, setScenario] = useState<Scenario>(defaultScenario);
  const value = useMemo(
    () => ({
      data: initialData,
      error: initialData ? null : "Dashboard extracts not found. Run python scripts/run_pipeline.py",
      loading: false,
      scenario,
      setScenario,
    }),
    [initialData, scenario],
  );

  return <DashboardContext.Provider value={value}>{children}</DashboardContext.Provider>;
}

export function useDashboard() {
  const ctx = useContext(DashboardContext);
  if (!ctx) throw new Error("useDashboard must be used within DashboardProvider");
  return ctx;
}
