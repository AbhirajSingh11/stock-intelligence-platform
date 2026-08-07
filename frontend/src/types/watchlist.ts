export interface WatchlistEntry {
  id: number;
  ticker: string;
  cik: string;
  company_name: string;
  added_at: string;
  updated_at: string;
}

export interface WatchlistResponse {
  entries: WatchlistEntry[];
}

export interface WatchlistDeleteResponse {
  ticker: string;
  deleted: boolean;
}
