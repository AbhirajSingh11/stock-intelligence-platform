import type { PortfolioSummary as PortfolioSummaryData } from "@/types/dashboard";
import { Icon } from "./icons";

interface PortfolioSummaryProps {
  summary: PortfolioSummaryData;
}

const currencyFormatter = new Intl.NumberFormat("en-US", {
  style: "currency",
  currency: "USD",
  minimumFractionDigits: 2,
});

function formatSignedCurrency(value: number) {
  return `${value >= 0 ? "+" : "−"}${currencyFormatter.format(
    Math.abs(value),
  )}`;
}

export function PortfolioSummary({ summary }: PortfolioSummaryProps) {
  const metrics = [
    {
      label: "Total portfolio value",
      value: currencyFormatter.format(summary.totalValue),
      detail: "3 active positions",
      featured: true,
    },
    {
      label: "Total gain",
      value: formatSignedCurrency(summary.totalGain),
      detail: "Since inception",
    },
    {
      label: "Total return",
      value: `+${summary.totalReturnPercent.toFixed(1)}%`,
      detail: "Cost-weighted",
    },
    {
      label: "Today’s change",
      value: formatSignedCurrency(summary.todayChange),
      detail: "+0.75% today",
    },
  ];

  return (
    <section aria-labelledby="portfolio-summary-heading">
      <div className="mb-3 flex items-center justify-between">
        <h2
          id="portfolio-summary-heading"
          className="text-xs font-semibold uppercase tracking-[0.14em] text-secondary"
        >
          Portfolio summary
        </h2>
        <p className="font-mono text-[10px] uppercase tracking-wider text-secondary">
          Mock data · USD
        </p>
      </div>

      <div className="grid grid-cols-2 border-l border-t border-border xl:grid-cols-4">
        {metrics.map((metric) => (
          <article
            key={metric.label}
            className="min-w-0 border-b border-r border-border bg-panel p-4 sm:p-5"
          >
            <p className="text-[11px] font-medium uppercase tracking-wider text-secondary">
              {metric.label}
            </p>
            <p
              className={`financial-figure mt-3 truncate font-mono font-semibold tracking-tight ${
                metric.featured
                  ? "text-xl text-foreground sm:text-2xl"
                  : "text-lg text-positive sm:text-xl"
              }`}
            >
              {metric.value}
            </p>
            <div className="mt-3 flex items-center gap-1.5 text-[11px] text-secondary">
              {!metric.featured && (
                <Icon name="trend" className="size-3.5 text-positive" />
              )}
              {metric.detail}
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}

