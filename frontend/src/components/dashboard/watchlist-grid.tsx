"use client";

import Link from "next/link";

import { useWatchlist } from "@/hooks/use-watchlist";
import { formatSecDate } from "@/lib/formatters";

function WatchlistSkeleton() {
  return (
    <div className="grid gap-3 md:grid-cols-3" role="status">
      {Array.from({ length: 3 }, (_, index) => (
        <div key={index} className="h-36 animate-pulse border border-border bg-panel motion-reduce:animate-none" />
      ))}
      <span className="sr-only">Loading persisted watchlist…</span>
    </div>
  );
}

export function WatchlistGrid() {
  const watchlist = useWatchlist();

  return (
    <section
      id="watchlist"
      className="scroll-mt-36 lg:scroll-mt-8"
      aria-labelledby="watchlist-heading"
    >
      <div className="mb-3 flex items-end justify-between gap-4">
        <div>
          <p className="text-[10px] font-semibold uppercase tracking-[0.16em] text-secondary">
            Locally persisted companies
          </p>
          <h2 id="watchlist-heading" className="mt-1 text-base font-semibold text-foreground">
            Watchlist
          </h2>
        </div>
        <Link
          href="/watchlist"
          className="font-mono text-[10px] font-semibold uppercase tracking-wider text-positive outline-none hover:underline focus-visible:ring-2 focus-visible:ring-positive"
        >
          Manage watchlist →
        </Link>
      </div>

      {watchlist.status === "loading" ? <WatchlistSkeleton /> : null}

      {watchlist.status === "error" ? (
        <div className="border border-warning/50 bg-panel p-5" role="alert">
          <p className="text-sm text-foreground">Watchlist unavailable</p>
          <p className="mt-2 text-xs leading-5 text-secondary">{watchlist.message}</p>
          <button
            type="button"
            onClick={watchlist.retryLoad}
            className="mt-4 border border-warning px-3 py-2 font-mono text-[10px] font-semibold uppercase tracking-wider text-warning outline-none hover:bg-warning/10 focus-visible:ring-2 focus-visible:ring-warning"
          >
            Retry
          </button>
        </div>
      ) : null}

      {watchlist.status === "success" && watchlist.entries.length === 0 ? (
        <div className="border border-border bg-panel p-6">
          <p className="text-sm font-medium text-foreground">No companies followed yet</p>
          <p className="mt-2 max-w-2xl text-xs leading-5 text-secondary">
            Search for a ticker, open its company research page, and choose Add to watchlist.
          </p>
        </div>
      ) : null}

      {watchlist.status === "success" && watchlist.entries.length > 0 ? (
        <div className="grid gap-3 md:grid-cols-3">
          {watchlist.entries.map((entry) => (
            <Link
              key={entry.id}
              href={`/companies/${encodeURIComponent(entry.ticker)}`}
              className="group border border-border bg-panel p-4 outline-none hover:border-positive/50 focus-visible:ring-2 focus-visible:ring-positive sm:p-5"
            >
              <div className="flex items-start justify-between gap-4">
                <div className="min-w-0">
                  <h3 className="font-mono text-base font-semibold tracking-wide text-foreground group-hover:text-positive">
                    {entry.ticker}
                  </h3>
                  <p className="mt-1 truncate text-[11px] text-secondary">
                    {entry.company_name}
                  </p>
                </div>
                <span className="border border-positive/30 bg-positive/10 px-2 py-1 font-mono text-[9px] uppercase tracking-wide text-positive">
                  Followed
                </span>
              </div>
              <dl className="mt-5 border-t border-border pt-4 text-[11px]">
                <div className="flex items-center justify-between gap-4">
                  <dt className="text-secondary">Added</dt>
                  <dd className="font-mono text-foreground">
                    {formatSecDate(entry.added_at.slice(0, 10))}
                  </dd>
                </div>
              </dl>
            </Link>
          ))}
        </div>
      ) : null}
    </section>
  );
}
