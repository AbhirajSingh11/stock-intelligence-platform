import { formatCurrency } from "@/lib/formatters";
import type { SignalTone, WatchlistCompany } from "@/types/dashboard";

interface WatchlistGridProps {
  items: WatchlistCompany[];
  currency: string;
}

const toneStyles: Record<SignalTone, string> = {
  positive: "border-positive/30 bg-positive/10 text-positive",
  warning: "border-warning/30 bg-warning/10 text-warning",
  neutral: "border-secondary/30 bg-secondary/10 text-secondary",
};

function formatSignedCurrency(value: number, currency: string) {
  return `${value >= 0 ? "+" : "−"}${formatCurrency(
    Math.abs(value),
    currency,
  )}`;
}

export function WatchlistGrid({ items, currency }: WatchlistGridProps) {
  return (
    <section id="watchlist" aria-labelledby="watchlist-heading">
      <div className="mb-3 flex items-end justify-between gap-4">
        <div>
          <p className="text-[10px] font-semibold uppercase tracking-[0.16em] text-secondary">
            Monitored companies
          </p>
          <h2
            id="watchlist-heading"
            className="mt-1 text-base font-semibold text-foreground"
          >
            Watchlist
          </h2>
        </div>
        <p className="font-mono text-[10px] uppercase tracking-wider text-secondary">
          3 securities · Mock data
        </p>
      </div>

      <div className="grid gap-3 md:grid-cols-3">
        {items.map((item) => {
          const isPositive = item.daily_change >= 0;
          return (
            <article
              key={item.ticker}
              className="border border-border bg-panel p-4 sm:p-5"
            >
              <div className="flex items-start justify-between gap-4">
                <div className="min-w-0">
                  <h3 className="font-mono text-base font-semibold tracking-wide text-foreground">
                    {item.ticker}
                  </h3>
                  <p className="mt-1 truncate text-[11px] text-secondary">
                    {item.company}
                  </p>
                </div>
                <span
                  className={`shrink-0 border px-2 py-1 font-mono text-[9px] font-semibold uppercase tracking-wide ${toneStyles[item.thesis_tone]}`}
                >
                  {item.thesis_state}
                </span>
              </div>

              <div className="mt-6 flex items-end justify-between gap-4">
                <div>
                  <p className="text-[10px] uppercase tracking-wider text-secondary">
                    Last price
                  </p>
                  <p className="financial-figure mt-1 font-mono text-xl font-semibold text-foreground">
                    {formatCurrency(item.price, currency)}
                  </p>
                </div>
                <div className="text-right">
                  <p className="text-[10px] uppercase tracking-wider text-secondary">
                    Daily change
                  </p>
                  <p
                    className={`financial-figure mt-1 font-mono text-xs font-semibold ${
                      isPositive ? "text-positive" : "text-warning"
                    }`}
                  >
                    {formatSignedCurrency(item.daily_change, currency)}{" "}
                    <span>
                      ({isPositive ? "+" : "−"}
                      {Math.abs(item.daily_change_percent).toFixed(2)}%)
                    </span>
                  </p>
                </div>
              </div>

              <dl className="mt-5 border-t border-border pt-4">
                <div className="flex items-center justify-between gap-4">
                  <dt className="text-[11px] text-secondary">Position value</dt>
                  <dd className="financial-figure font-mono text-sm font-medium text-foreground">
                    {formatCurrency(item.position_value, currency)}
                  </dd>
                </div>
              </dl>
            </article>
          );
        })}
      </div>
    </section>
  );
}
