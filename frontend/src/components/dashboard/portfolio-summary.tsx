import type { PortfolioSummary as PortfolioSummaryData } from "@/types/dashboard";
import { formatCurrency } from "@/lib/formatters";
import { Icon } from "./icons";

interface PortfolioSummaryProps {
  summary: PortfolioSummaryData;
  currency: string;
}

function formatSignedCurrency(value: number, currency: string) {
  return `${value >= 0 ? "+" : "−"}${formatCurrency(
    Math.abs(value),
    currency,
  )}`;
}

export function PortfolioSummary({
  summary,
  currency,
}: PortfolioSummaryProps) {
  const metrics = [
    {
      label: "Total portfolio value",
      value: formatCurrency(summary.total_value, currency),
      detail: `${summary.position_count} active positions`,
      featured: true,
    },
    {
      label: "Total gain",
      value: formatSignedCurrency(summary.total_gain, currency),
      detail: "Since inception",
    },
    {
      label: "Total return",
      value: `+${summary.total_return_percent.toFixed(1)}%`,
      detail: "Cost-weighted",
    },
    {
      label: "Today’s change",
      value: formatSignedCurrency(summary.today_change, currency),
      detail: `+${summary.today_change_percent.toFixed(2)}% today`,
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
          {`Backend mock · ${currency}`}
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
