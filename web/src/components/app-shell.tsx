"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Logo } from "@/components/logo";
import { SettingsMenu } from "@/components/settings-menu";
import { cn } from "@/lib/utils";

const NAV = [
  { href: "/", label: "Overview" },
  { href: "/forecast", label: "Forecast" },
  { href: "/inventory", label: "Inventory" },
  { href: "/abc", label: "ABC / EOQ" },
  { href: "/stores", label: "Stores" },
  { href: "/planner", label: "Planner" },
];

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  return (
    <div className="min-h-screen bg-white text-[#222]">
      <header className="border-b border-[#cfcfcf] bg-[#f3f3f3]">
        <div className="flex items-center justify-between gap-3 px-3 py-2 sm:px-4">
          <div className="flex min-w-0 items-center gap-2">
            <Logo className="h-8 w-8 shrink-0" />
            <div className="min-w-0">
              <p className="truncate text-[16px] font-semibold text-[#222]">
                Demand and inventory workbench
              </p>
              <p className="truncate text-[12px] text-[#666]">
                Independent M5-schema project · 28-day holdout · Accuracy = 1 − WMAPE
              </p>
            </div>
          </div>
          <SettingsMenu />
        </div>
        <nav className="flex gap-0 overflow-x-auto border-t border-[#cfcfcf] bg-white px-1">
          {NAV.map((item) => {
            const active = pathname === item.href;
            return (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  "shrink-0 border-b-2 px-3 py-2 text-[13px]",
                  active
                    ? "border-[#4472C4] font-semibold text-[#4472C4]"
                    : "border-transparent text-[#444] hover:bg-[#f7f7f7]",
                )}
              >
                {item.label}
              </Link>
            );
          })}
        </nav>
      </header>
      <main className="px-3 py-4 sm:px-4">{children}</main>
    </div>
  );
}
