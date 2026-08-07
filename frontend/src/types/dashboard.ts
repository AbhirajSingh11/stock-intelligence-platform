export type ThesisState = "Strengthening" | "Review required" | "Stable";

export type SignalTone = "positive" | "warning" | "neutral";

export interface ThesisSignal {
  ticker: string;
  company: string;
  state: ThesisState;
  tone: SignalTone;
  last_reviewed: string;
}

export interface DashboardOverviewResponse {
  as_of: string;
  thesis_signals: ThesisSignal[];
}
