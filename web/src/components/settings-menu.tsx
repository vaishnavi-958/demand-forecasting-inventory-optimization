"use client";

import { useEffect, useRef, useState } from "react";
import { SettingsForm } from "@/components/settings-form";

export function SettingsMenu() {
  const [open, setOpen] = useState(false);
  const root = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function onDoc(event: MouseEvent) {
      if (!root.current?.contains(event.target as Node)) setOpen(false);
    }
    document.addEventListener("mousedown", onDoc);
    return () => document.removeEventListener("mousedown", onDoc);
  }, []);

  return (
    <div className="relative" ref={root}>
      <button
        type="button"
        aria-label="Settings"
        aria-expanded={open}
        onClick={() => setOpen((v) => !v)}
        className="flex h-8 w-8 flex-col items-center justify-center gap-[3px] border border-[#cfcfcf] bg-white hover:bg-[#f7f7f7]"
      >
        <span className="block h-[2px] w-4 bg-[#222]" />
        <span className="block h-[2px] w-4 bg-[#222]" />
        <span className="block h-[2px] w-4 bg-[#222]" />
      </button>
      {open ? (
        <div className="absolute right-0 z-40 mt-1 w-[min(20rem,calc(100vw-1.5rem))] border border-[#cfcfcf] bg-white p-3 shadow">
          <p className="mb-2 text-[13px] font-semibold text-[#222]">Settings</p>
          <SettingsForm />
        </div>
      ) : null}
    </div>
  );
}
