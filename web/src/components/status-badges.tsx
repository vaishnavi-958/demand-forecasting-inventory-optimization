const RISK: Record<string, string> = {
  CRITICAL: "border-[#c0504d] bg-[#f8d7da] text-[#9b1c1c]",
  HIGH: "border-[#ed7d31] bg-[#fce4d6] text-[#9a3412]",
  MEDIUM: "border-[#ffc000] bg-[#fff2cc] text-[#7c5800]",
  LOW: "border-[#70ad47] bg-[#e2efda] text-[#375623]",
};

const ACTION: Record<string, string> = {
  EXPEDITE: "border-[#c0504d] bg-[#c0504d] text-white",
  REORDER: "border-[#4472C4] bg-[#4472C4] text-white",
  MONITOR: "border-[#ed7d31] bg-[#ed7d31] text-white",
  "REDUCE INVENTORY": "border-[#595959] bg-[#595959] text-white",
  "NO ACTION": "border-[#cfcfcf] bg-[#f3f3f3] text-[#444]",
};

export function RiskBadge({ value }: { value: string }) {
  return (
    <span className={`inline-block border px-1.5 py-0.5 text-[10px] font-semibold ${RISK[value] ?? "border-[#cfcfcf]"}`}>
      {value}
    </span>
  );
}

export function ActionBadge({ value }: { value: string }) {
  return (
    <span className={`inline-block border px-1.5 py-0.5 text-[10px] font-semibold ${ACTION[value] ?? "border-[#cfcfcf]"}`}>
      {value}
    </span>
  );
}
