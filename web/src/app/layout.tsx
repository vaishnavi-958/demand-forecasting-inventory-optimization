import type { Metadata } from "next";
import { readFile } from "node:fs/promises";
import path from "node:path";
import { TooltipProvider } from "@/components/ui/tooltip";
import { AppShell } from "@/components/app-shell";
import { DashboardProvider } from "@/components/dashboard-provider";
import type { DashboardData } from "@/lib/types";
import "./globals.css";

export const metadata: Metadata = {
  title: "Demand and inventory workbench",
  description:
    "Independent supply chain analytics project using the public M5 forecasting schema.",
  icons: {
    icon: [{ url: "/icon.svg", type: "image/svg+xml" }],
  },
};

async function loadDashboard(): Promise<DashboardData | null> {
  try {
    const file = path.join(process.cwd(), "public", "data", "dashboard.json");
    const raw = await readFile(file, "utf8");
    return JSON.parse(raw) as DashboardData;
  } catch {
    return null;
  }
}

export default async function RootLayout({ children }: LayoutProps<"/">) {
  const data = await loadDashboard();
  return (
    <html lang="en" className="h-full">
      <body className="min-h-full bg-white text-[#222]">
        <TooltipProvider>
          <DashboardProvider initialData={data}>
            <AppShell>{children}</AppShell>
          </DashboardProvider>
        </TooltipProvider>
      </body>
    </html>
  );
}
