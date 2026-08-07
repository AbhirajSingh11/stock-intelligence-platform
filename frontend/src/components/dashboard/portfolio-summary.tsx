import { formatCurrency } from "@/lib/formatters";
import type { ExactDecimal, PortfolioTotals } from "@/types/portfolio";

interface PortfolioSummaryProps {
  totals: PortfolioTotals;
  currency: string;
}

function currency(value: ExactDecimal, code: string): string {
  return formatCurrency(Number(value), code);
}

function signedCurrency(value: ExactDecimal, code: string): string {
  const numeric = Number(value);
  return `${numeric >= 0 ? "+" : "−"}${formatCurrency(Math.abs(numeric), code)}`;
}

export function PortfolioSummary({ totals, currency: code }: PortfolioSummaryProps) {
  const complete = totals.market_values_complete;
  const metrics = [
    {
      label: "Market value",
      value: totals.market_value ? currency(totals.market_value, code) : "Incomplete",
      detail: complete
        ? "All open positions marked"
        : `${totals.marked_position_count} of ${totals.open_position_count} positions marked`,
      tone: complete ? "text-foreground" : "text-warning",
    },
    {
      label: "Open cost basis",
      value: currency(totals.open_cost_basis, code),
      detail: "Weighted-average cost",
      tone: "text-foreground",
    },
    {
      label: "Unrealized P/L",
      value: totals.unrealized_gain_loss
        ? signedCurrency(totals.unrealized_gain_loss, code)
        : "Unavailable",
      detail: complete ? "Based on manual marks" : "Requires all open prices",
      tone:
        totals.unrealized_gain_loss && Number(totals.unrealized_gain_loss) >= 0
          ? "text-positive"
          : "text-warning",
    },
    {
      label: "Realized P/L",
      value: signedCurrency(totals.realized_gain_loss, code),
      detail: "Closed quantities, after fees",
      tone: Number(totals.realized_gain_loss) >= 0 ? "text-positive" : "text-warning",
    },
    {
      label: "Open positions",
      value: String(totals.open_position_count),
      detail: `${totals.transaction_count} ledger ${totals.transaction_count === 1 ? "entry" : "entries"}`,
      tone: "text-foreground",
    },
    {
      label: "Manual-price coverage",
      value:
        totals.manual_price_coverage_percent === null
          ? "Not applicable"
          : `${Number(totals.manual_price_coverage_percent).toFixed(0)}%`,
      detail: `${totals.marked_position_count} marked · ${totals.unmarked_position_count} awaiting price`,
      tone: complete ? "text-positive" : "text-warning",
    },
  ];

  return (
    <section aria-labelledby="portfolio-summary-heading">
      <div className="mb-3 flex items-center justify-between gap-4">
        <h2 id="portfolio-summary-heading" className="text-xs font-semibold uppercase tracking-[0.14em] text-secondary">
          Portfolio summary
        </h2>
        <p className="font-mono text-[10px] uppercase tracking-wider text-secondary">
          Persisted ledger · Manual prices
        </p>
      </div>
      <div className="grid grid-cols-2 border-l border-t border-border lg:grid-cols-3 2xl:grid-cols-6">
        {metrics.map((metric) => (
          <article key={metric.label} className="min-w-0 border-b border-r border-border bg-panel p-4 sm:p-5">
            <p className="text-[10px] font-medium uppercase tracking-wider text-secondary sm:text-[11px]">
              {metric.label}
            </p>
            <p className={`financial-figure mt-3 truncate font-mono text-lg font-semibold tracking-tight sm:text-xl ${metric.tone}`}>
              {metric.value}
            </p>
            <p className="mt-3 text-[10px] leading-4 text-secondary sm:text-[11px]">
              {metric.detail}
            </p>
          </article>
        ))}
      </div>
      {!complete && totals.open_position_count > 0 ? (
        <p className="border-x border-b border-warning/40 bg-warning/5 px-4 py-3 text-xs leading-5 text-warning">
          Market value and total unrealized gain/loss are unavailable until every open position has a manual price. The marked subtotal is not presented as the complete portfolio.
        </p>
      ) : null}
    </section>
  );
}
