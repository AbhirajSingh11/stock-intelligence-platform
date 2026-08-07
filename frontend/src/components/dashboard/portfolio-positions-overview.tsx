import Link from "next/link";

import { formatCurrency } from "@/lib/formatters";
import type { PortfolioOverviewResponse } from "@/types/portfolio";

export function PortfolioPositionsOverview({ portfolio }: { portfolio: PortfolioOverviewResponse }) {
  const totalCost = Number(portfolio.totals.open_cost_basis);

  return (
    <section className="border border-border bg-panel" aria-labelledby="positions-overview-heading">
      <div className="flex items-start justify-between gap-4 border-b border-border p-5">
        <div>
          <p className="font-mono text-[10px] uppercase tracking-[0.18em] text-secondary">Real portfolio ledger</p>
          <h2 id="positions-overview-heading" className="mt-2 text-lg font-semibold text-foreground">Open positions by cost</h2>
        </div>
        <Link href="/portfolio" className="font-mono text-[10px] font-semibold uppercase tracking-wider text-positive outline-none hover:underline focus-visible:ring-2 focus-visible:ring-positive">
          Manage portfolio →
        </Link>
      </div>

      {portfolio.positions.length === 0 ? (
        <div className="p-6">
          <p className="text-sm font-medium text-foreground">No open positions</p>
          <p className="mt-2 text-xs leading-5 text-secondary">Record a buy transaction to begin building the portfolio ledger.</p>
        </div>
      ) : (
        <ul className="divide-y divide-border">
          {portfolio.positions.map((position) => {
            const allocation = totalCost > 0 ? (Number(position.open_cost_basis) / totalCost) * 100 : 0;
            return (
              <li key={position.ticker} className="p-4 sm:p-5">
                <div className="flex items-end justify-between gap-4">
                  <div className="min-w-0">
                    <p className="font-mono text-sm font-semibold text-foreground">{position.ticker}</p>
                    <p className="mt-1 truncate text-[11px] text-secondary">{position.company_name}</p>
                  </div>
                  <div className="text-right">
                    <p className="financial-figure font-mono text-sm font-semibold text-foreground">
                      {formatCurrency(Number(position.open_cost_basis), portfolio.currency)}
                    </p>
                    <p className="mt-1 font-mono text-[9px] text-secondary">{`${allocation.toFixed(1)}% of open cost`}</p>
                  </div>
                </div>
                <div className="mt-3 h-1.5 bg-background" aria-hidden="true">
                  <div className="h-full bg-positive" style={{ width: `${Math.min(100, allocation)}%` }} />
                </div>
              </li>
            );
          })}
        </ul>
      )}
    </section>
  );
}
