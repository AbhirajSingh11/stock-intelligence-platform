import type { SignalTone, WatchlistItem } from "@/types/dashboard";

interface WatchlistGridProps {
  items: WatchlistItem[];
}

const currencyFormatter = new Intl.NumberFormat("en-US", {
  style: "currency",
  currency: "USD",
  minimumFractionDigits: 2,
});

const toneStyles: Record<SignalTone, string> = {
  positive: "border-positive/30 bg-positive/10 text-positive",
  warning: "border-warning/30 bg-warning/10 text-warning",
  neutral: "border-secondary/30 bg-secondary/10 text-secondary",
};

function formatSignedCurrency(value: number) {
  return `${value >= 0 ? "+" : "−"}${currencyFormatter.format(
    Math.abs(value),
  )}`;
}

export function WatchlistGrid({ items }: WatchlistGridProps) {
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
          const isPositive = item.dailyChange >= 0;
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
                  className={`shrink-0 border px-2 py-1 font-mono text-[9px] font-semibold uppercase tracking-wide ${toneStyles[item.thesisTone]}`}
                >
                  {item.thesisState}
                </span>
              </div>

              <div className="mt-6 flex items-end justify-between gap-4">
                <div>
                  <p className="text-[10px] uppercase tracking-wider text-secondary">
                    Last price
                  </p>
                  <p className="financial-figure mt-1 font-mono text-xl font-semibold text-foreground">
                    {currencyFormatter.format(item.price)}
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
                    {formatSignedCurrency(item.dailyChange)}{" "}
                    <span>
                      ({isPositive ? "+" : "−"}
                      {Math.abs(item.dailyChangePercent).toFixed(2)}%)
                    </span>
                  </p>
                </div>
              </div>

              <dl className="mt-5 border-t border-border pt-4">
                <div className="flex items-center justify-between gap-4">
                  <dt className="text-[11px] text-secondary">Position value</dt>
                  <dd className="financial-figure font-mono text-sm font-medium text-foreground">
                    {currencyFormatter.format(item.positionValue)}
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

