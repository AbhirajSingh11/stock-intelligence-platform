export type ExactDecimal = string;
export type TransactionSide = "BUY" | "SELL";
export type PriceMarkSource = "MANUAL";

export interface PortfolioTransactionInput {
  ticker: string;
  side: TransactionSide;
  trade_date: string;
  quantity: ExactDecimal;
  price_per_share: ExactDecimal;
  fees: ExactDecimal;
  notes: string | null;
}

export type PortfolioTransactionUpdate = Partial<
  Omit<PortfolioTransactionInput, "ticker">
>;

export interface PortfolioTransaction {
  id: number;
  ticker: string;
  cik: string;
  company_name: string;
  side: TransactionSide;
  trade_date: string;
  quantity: ExactDecimal;
  price_per_share: ExactDecimal;
  fees: ExactDecimal;
  gross_amount: ExactDecimal;
  notes: string | null;
  created_at: string;
  updated_at: string;
}

export interface PortfolioTransactionsResponse {
  transactions: PortfolioTransaction[];
}

export interface PortfolioPriceMarkInput {
  price: ExactDecimal;
  as_of?: string;
}

export interface PortfolioPriceMark {
  id: number;
  ticker: string;
  price: ExactDecimal;
  as_of: string;
  source: PriceMarkSource;
  created_at: string;
  updated_at: string;
}

export interface PortfolioPosition {
  ticker: string;
  cik: string;
  company_name: string;
  quantity: ExactDecimal;
  average_cost: ExactDecimal;
  open_cost_basis: ExactDecimal;
  realized_gain_loss: ExactDecimal;
  manual_price: ExactDecimal | null;
  price_as_of: string | null;
  price_source: PriceMarkSource | null;
  market_value: ExactDecimal | null;
  unrealized_gain_loss: ExactDecimal | null;
  unrealized_return_percent: ExactDecimal | null;
}

export interface PortfolioTotals {
  open_cost_basis: ExactDecimal;
  realized_gain_loss: ExactDecimal;
  market_value: ExactDecimal | null;
  marked_market_value: ExactDecimal;
  unrealized_gain_loss: ExactDecimal | null;
  marked_unrealized_gain_loss: ExactDecimal;
  open_position_count: number;
  transaction_count: number;
  marked_position_count: number;
  unmarked_position_count: number;
  manual_price_coverage_percent: ExactDecimal | null;
  market_values_complete: boolean;
}

export interface PortfolioOverviewResponse {
  as_of: string;
  currency: "USD";
  totals: PortfolioTotals;
  positions: PortfolioPosition[];
}

export interface PortfolioDeleteResponse {
  transaction_id: number;
  deleted: boolean;
}
