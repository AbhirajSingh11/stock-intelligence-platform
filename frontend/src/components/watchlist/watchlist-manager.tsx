"use client";

import Link from "next/link";

import { useWatchlist } from "@/hooks/use-watchlist";
import { formatSecDate } from "@/lib/formatters";

export function WatchlistManager() {
  const watchlist = useWatchlist();

  if (watchlist.status === "loading") {
    return (
      <div className="space-y-3" role="status" aria-label="Loading watchlist">
        {Array.from({ length: 3 }, (_, index) => (
          <div
            key={index}
            className="h-24 animate-pulse border border-border bg-panel motion-reduce:animate-none"
          />
        ))}
      </div>
    );
  }

  if (watchlist.status === "error") {
    return (
      <section className="border border-warning/50 bg-panel p-6" role="alert">
        <h2 className="text-lg font-semibold text-foreground">Watchlist unavailable</h2>
        <p className="mt-2 max-w-2xl text-sm leading-6 text-secondary">
          {watchlist.message}
        </p>
        <button
          type="button"
          onClick={watchlist.retryLoad}
          className="mt-5 border border-warning bg-warning px-4 py-2.5 font-mono text-xs font-semibold uppercase tracking-wider text-[#171006] outline-none hover:bg-[#F0B75F] focus-visible:ring-2 focus-visible:ring-warning focus-visible:ring-offset-2 focus-visible:ring-offset-background"
        >
          Retry
        </button>
      </section>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex flex-col gap-3 border border-border bg-panel p-5 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <p className="font-mono text-[10px] uppercase tracking-[0.18em] text-positive">
            Persistent local research set
          </p>
          <h2 className="mt-2 text-xl font-semibold text-foreground">Your watchlist</h2>
          <p className="mt-2 text-sm text-secondary">
            {`${watchlist.entries.length} ${watchlist.entries.length === 1 ? "company" : "companies"} stored in SQLite`}
          </p>
        </div>
        <p className="max-w-md text-xs leading-5 text-secondary sm:text-right">
          Add companies from their research profiles. Price data is intentionally unavailable in this milestone.
        </p>
      </div>

      {watchlist.mutation.status === "error" ? (
        <div className="flex flex-col gap-3 border border-warning/50 bg-warning/5 p-4 sm:flex-row sm:items-center sm:justify-between" role="alert">
          <p className="text-sm text-warning">{watchlist.mutation.message}</p>
          <button
            type="button"
            onClick={watchlist.retryMutation}
            className="self-start border border-warning px-3 py-2 font-mono text-[10px] font-semibold uppercase tracking-wider text-warning outline-none hover:bg-warning/10 focus-visible:ring-2 focus-visible:ring-warning sm:self-auto"
          >
            Retry removal
          </button>
        </div>
      ) : null}

      <div className="sr-only" aria-live="polite">
        {watchlist.mutation.status === "success"
          ? `${watchlist.mutation.action.ticker} ${watchlist.mutation.action.kind === "add" ? "added to" : "removed from"} watchlist.`
          : ""}
      </div>

      {watchlist.entries.length === 0 ? (
        <section className="border border-border bg-panel p-8 text-center">
          <h2 className="text-lg font-semibold text-foreground">Your watchlist is empty</h2>
          <p className="mx-auto mt-3 max-w-xl text-sm leading-6 text-secondary">
            Use the ticker or company search above, open a research profile, and add the company from there.
          </p>
          <Link
            href="/"
            className="mt-5 inline-block border border-positive px-4 py-2.5 font-mono text-xs font-semibold uppercase tracking-wider text-positive outline-none hover:bg-positive/10 focus-visible:ring-2 focus-visible:ring-positive"
          >
            Return to dashboard
          </Link>
        </section>
      ) : (
        <ul className="divide-y divide-border border border-border bg-panel">
          {watchlist.entries.map((entry) => {
            const isRemoving =
              watchlist.mutation.status === "pending" &&
              watchlist.mutation.action.kind === "remove" &&
              watchlist.mutation.action.ticker === entry.ticker;

            return (
              <li key={entry.id} className="flex flex-col gap-4 p-4 sm:flex-row sm:items-center sm:justify-between sm:p-5">
                <Link
                  href={`/companies/${encodeURIComponent(entry.ticker)}`}
                  className="min-w-0 outline-none focus-visible:ring-2 focus-visible:ring-positive"
                >
                  <span className="font-mono text-base font-semibold text-positive">{entry.ticker}</span>
                  <span className="ml-3 text-sm text-foreground">{entry.company_name}</span>
                  <span className="mt-1 block font-mono text-[10px] text-secondary">
                    {`CIK ${entry.cik} · Added ${formatSecDate(entry.added_at.slice(0, 10))}`}
                  </span>
                </Link>
                <button
                  type="button"
                  onClick={() => watchlist.remove(entry.ticker)}
                  disabled={watchlist.mutation.status === "pending"}
                  aria-label={`Remove ${entry.ticker} from watchlist`}
                  className="self-start border border-warning/60 px-3 py-2 font-mono text-[10px] font-semibold uppercase tracking-wider text-warning outline-none hover:bg-warning/10 focus-visible:ring-2 focus-visible:ring-warning disabled:cursor-wait disabled:opacity-50 sm:self-auto"
                >
                  {isRemoving ? "Removing…" : "Remove"}
                </button>
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
}
