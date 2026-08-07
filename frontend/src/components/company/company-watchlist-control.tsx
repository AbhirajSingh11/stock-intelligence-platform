"use client";

import { useWatchlist } from "@/hooks/use-watchlist";

export function CompanyWatchlistControl({ ticker }: { ticker: string }) {
  const watchlist = useWatchlist();

  if (watchlist.status === "loading") {
    return (
      <button
        type="button"
        disabled
        className="cursor-wait border border-border px-3 py-2 font-mono text-[10px] uppercase tracking-wider text-secondary"
      >
        Checking watchlist…
      </button>
    );
  }

  if (watchlist.status === "error") {
    return (
      <div className="text-right" role="alert">
        <p className="max-w-xs text-xs text-warning">Watchlist status unavailable.</p>
        <button
          type="button"
          onClick={watchlist.retryLoad}
          className="mt-2 border border-warning px-3 py-2 font-mono text-[10px] font-semibold uppercase tracking-wider text-warning outline-none hover:bg-warning/10 focus-visible:ring-2 focus-visible:ring-warning"
        >
          Retry status
        </button>
      </div>
    );
  }

  const isFollowing = watchlist.entries.some((entry) => entry.ticker === ticker);
  const isPending = watchlist.mutation.status === "pending";
  const actionLabel = isFollowing ? "Remove from watchlist" : "Add to watchlist";

  return (
    <div className="text-right">
      <button
        type="button"
        onClick={() =>
          isFollowing ? watchlist.remove(ticker) : watchlist.add(ticker)
        }
        disabled={isPending}
        aria-pressed={isFollowing}
        className={`border px-3 py-2 font-mono text-[10px] font-semibold uppercase tracking-wider outline-none focus-visible:ring-2 disabled:cursor-wait disabled:opacity-50 ${
          isFollowing
            ? "border-warning/60 text-warning hover:bg-warning/10 focus-visible:ring-warning"
            : "border-positive text-positive hover:bg-positive/10 focus-visible:ring-positive"
        }`}
      >
        {isPending ? "Updating…" : actionLabel}
      </button>

      <div className="mt-2 min-h-4" aria-live="polite">
        {watchlist.mutation.status === "success" ? (
          <p className="text-[10px] text-positive">
            {watchlist.mutation.action.kind === "add"
              ? "Added to your watchlist."
              : "Removed from your watchlist."}
          </p>
        ) : null}
        {watchlist.mutation.status === "error" ? (
          <div role="alert">
            <p className="max-w-xs text-xs leading-5 text-warning">
              {watchlist.mutation.message}
            </p>
            <button
              type="button"
              onClick={watchlist.retryMutation}
              className="mt-2 font-mono text-[10px] font-semibold uppercase tracking-wider text-warning underline outline-none focus-visible:ring-2 focus-visible:ring-warning"
            >
              Retry update
            </button>
          </div>
        ) : null}
      </div>
    </div>
  );
}
