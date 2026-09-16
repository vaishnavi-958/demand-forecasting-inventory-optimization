export function KpiCard({
  label,
  value,
  hint,
  alert,
}: {
  label: string;
  value: string;
  hint?: string;
  alert?: boolean;
}) {
  return (
    <div className={`border bg-white p-2.5 ${alert ? "border-[#c0504d]" : "border-[#cfcfcf]"}`}>
      <p className="text-[11px] text-[#666]">{label}</p>
      <p className={`text-[22px] font-semibold tabular-nums ${alert ? "text-[#c0504d]" : "text-[#222]"}`}>
        {value}
      </p>
      {hint ? <p className="text-[11px] text-[#888]">{hint}</p> : null}
    </div>
  );
}
