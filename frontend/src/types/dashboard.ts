import type { ThesisSummary } from "./thesis";

export interface DashboardOverviewResponse {
  as_of: string;
  thesis_signals: ThesisSummary[];
}
