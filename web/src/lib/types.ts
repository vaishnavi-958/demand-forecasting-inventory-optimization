export type StockoutRisk = "CRITICAL" | "HIGH" | "MEDIUM" | "LOW";
export type PlannerAction =
  | "EXPEDITE"
  | "REORDER"
  | "MONITOR"
  | "REDUCE INVENTORY"
  | "NO ACTION";

export type PlannerRow = {
  item_id: string;
  store_id: string;
  dept_id: string;
  cat_id: string;
  abc_class: string;
  demand_segment: string;
  best_model: string;
  Forecast_Accuracy: number | string;
  WMAPE: number | string;
  avg_daily_demand: number;
  current_inventory: number;
  safety_stock: number;
  reorder_point: number;
  days_of_supply: number;
  stockout_risk: StockoutRisk | string;
  excess_units: number;
  excess_value: number;
  eoq: number;
  recommended_order_qty: number;
  recommended_action: PlannerAction | string;
  lead_time_days: number;
  service_level: number;
  demand_std: number;
  annual_demand: number;
  unit_cost: number;
  ordering_cost: number;
  holding_cost_rate: number;
};

export type DashboardData = {
  kpis: {
    total_sales: number;
    total_units: number;
    forecast_accuracy: number;
    baseline_accuracy: number;
    improvement_vs_baseline: number;
    wmape: number;
    inventory_turns: number;
    stockout_risk_pct: number;
    excess_inventory_value: number;
    a_class_sku_pct: number;
    recommended_orders: number;
    sku_store_count: number;
    as_of: string;
  };
  insights: Record<string, unknown>;
  sales_trend: { date: string; sales_units: number; revenue: number }[];
  forecast_vs_actual: { date: string; actual: number; forecast: number }[];
  model_summary: {
    model: string;
    MAE: number;
    RMSE: number;
    MAPE: number | null;
    sMAPE: number;
    WMAPE: number;
    Forecast_Accuracy: number;
    series: number;
  }[];
  dept_accuracy: { dept_id: string; WMAPE: number; Forecast_Accuracy: number }[];
  risk_summary: { stockout_risk: string; sku_count: number; excess_value: number; on_hand: number }[];
  excess_by_category: { cat_id: string; excess_value: number; excess_units: number; sku_count: number }[];
  store_performance: {
    state_id: string;
    store_id: string;
    revenue_proxy: number;
    avg_accuracy: number;
    avg_wmape: number;
    critical: number;
    high: number;
    excess_value: number;
    avg_dos: number;
  }[];
  abc_summary: {
    abc_class: string;
    sku_count: number;
    annual_value: number;
    inventory_value: number;
    avg_eoq: number;
  }[];
  pareto: {
    rank: number;
    item_id: string;
    store_id: string;
    annual_consumption_value: number;
    cumulative_value_pct: number;
    abc_class: string;
  }[];
  planner: PlannerRow[];
  sku_forecasts: { item_id: string; store_id: string; date: string; actual: number; forecast: number }[];
  category_weekly: { week: string; cat_id: string; sales_units: number; revenue: number }[];
  assumptions: Record<string, string>;
};

export type Scenario = {
  serviceLevel: number;
  leadTimeDays: number;
  orderingCost: number;
  holdingCostRate: number;
};
