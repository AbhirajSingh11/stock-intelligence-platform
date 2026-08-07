export type PerformancePeriod = "1M" | "3M" | "6M" | "1Y" | "ALL";

export type ThesisState = "Strengthening" | "Review required" | "Stable";

export type SignalTone = "positive" | "warning" | "neutral";

export interface PortfolioSummary {
  total_value: number;
  total_gain: number;
  total_return_percent: number;
  today_change: number;
  today_change_percent: number;
  position_count: number;
}

export interface PerformancePoint {
  date: string;
  value: number;
}

export interface PerformanceSeries {
  period: PerformancePeriod;
  start_date: string;
  end_date: string;
  change_percent: number;
  points: PerformancePoint[];
}

export interface ThesisSignal {
  ticker: string;
  company: string;
  state: ThesisState;
  tone: SignalTone;
  last_reviewed: string;
}

export interface DashboardOverviewResponse {
  as_of: string;
  currency: string;
  portfolio_summary: PortfolioSummary;
  performance: PerformanceSeries[];
  thesis_signals: ThesisSignal[];
}
