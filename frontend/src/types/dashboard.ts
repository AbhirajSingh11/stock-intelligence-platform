export type PerformancePeriod = "1M" | "3M" | "6M" | "1Y" | "ALL";

export type ThesisState = "Strengthening" | "Review required" | "Stable";

export type SignalTone = "positive" | "warning" | "neutral";

export interface PortfolioSummary {
  totalValue: number;
  totalGain: number;
  totalReturnPercent: number;
  todayChange: number;
}

export interface PerformancePoint {
  date: string;
  label: string;
  value: number;
}

export interface PerformanceSeries {
  period: PerformancePeriod;
  rangeLabel: string;
  changePercent: number;
  points: PerformancePoint[];
}

export interface ThesisSignal {
  ticker: string;
  company: string;
  state: ThesisState;
  tone: SignalTone;
  lastReviewed: string;
}

export interface WatchlistItem {
  ticker: string;
  company: string;
  price: number;
  dailyChange: number;
  dailyChangePercent: number;
  positionValue: number;
  thesisState: ThesisState;
  thesisTone: SignalTone;
}

