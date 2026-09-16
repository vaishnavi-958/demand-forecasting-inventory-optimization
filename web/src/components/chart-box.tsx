"use client";

import { useEffect, useState } from "react";

export function ChartBox({
  children,
  className = "h-64",
}: {
  children: React.ReactNode;
  className?: string;
}) {
  const [ready, setReady] = useState(false);
  useEffect(() => {
    const id = requestAnimationFrame(() => setReady(true));
    return () => cancelAnimationFrame(id);
  }, []);
  return <div className={className}>{ready ? children : null}</div>;
}
