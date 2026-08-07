"use client";

import Link from "next/link";
import { useState, type FormEvent } from "react";

import {
  formatAsOf,
  formatExactCurrency,
  formatExactQuantity,
  formatSignedExactCurrency,
} from "@/lib/formatters";
import type { PortfolioPosition } from "@/types/portfolio";

function ManualPriceForm({
  position,
  busy,
  onSave,
  onCancel,
}: {
  position: PortfolioPosition;
  busy: boolean;
  onSave: (ticker: string, price: string) => Promise<void>;
  onCancel: () => void;
}) {
  const [price, setPrice] = useState(position.manual_price ?? "");
  const [message, setMessage] = useState<string | null>(null);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!Number.isFinite(Number(price)) || Number(price) <= 0) {
      setMessage("Manual price must be greater than zero.");
      return;
    }
    setMessage(null);
    await onSave(position.ticker, price);
  }

  return (
    <form onSubmit={submit} className="mt-4 border-t border-border pt-4">
      <label
        htmlFor={`manual-price-${position.ticker}`}
        className="block text-xs font-medium text-secondary"
      >
        Manual current price for {position.ticker}
      </label>
      <input
        id={`manual-price-${position.ticker}`}
        type="number"
        inputMode="decimal"
        min="0.00000001"
        step="0.00000001"
        value={price}
        onChange={(event) => setPrice(event.target.value)}
        disabled={busy}
        autoFocus
        className="mt-2 h-10 w-full min-w-0 border border-border bg-background px-3 font-mono text-sm text-foreground outline-none placeholder:text-secondary/60 focus:border-positive focus:ring-1 focus:ring-positive disabled:opacity-60"
        placeholder="140.00"
        required
      />
      <div className="mt-3 flex flex-col gap-2 min-[420px]:flex-row min-[420px]:items-center">
        <button type="submit" disabled={busy} className="w-full whitespace-nowrap border border-positive bg-positive px-4 py-2 font-mono text-[10px] font-semibold uppercase tracking-wider text-[#07120e] outline-none hover:bg-[#48D29D] focus-visible:ring-2 focus-visible:ring-positive min-[420px]:w-auto disabled:cursor-wait disabled:opacity-50">
          {busy ? "Saving…" : "Save price"}
        </button>
        <button type="button" onClick={onCancel} disabled={busy} className="w-full whitespace-nowrap border border-border px-3 py-2 font-mono text-[10px] uppercase tracking-wider text-secondary outline-none hover:text-foreground focus-visible:ring-2 focus-visible:ring-positive min-[420px]:w-auto disabled:opacity-50">
          Cancel
        </button>
      </div>
      <p className="mt-2 min-h-4 text-xs text-warning" role="alert">{message}</p>
      <p className="text-[10px] leading-4 text-secondary">This is a user-entered mark, not a live market quote.</p>
    </form>
  );
}

export function PortfolioPositions({
  positions,
  currency,
  busy,
  onSetMark,
}: {
  positions: PortfolioPosition[];
  currency: string;
  busy: boolean;
  onSetMark: (ticker: string, price: string) => Promise<void>;
}) {
  const [editingTicker, setEditingTicker] = useState<string | null>(null);

  return (
    <section className="border border-border bg-panel" aria-labelledby="open-positions-heading">
      <div className="border-b border-border p-5">
        <p className="font-mono text-[10px] uppercase tracking-[0.18em] text-secondary">Weighted-average holdings</p>
        <h2 id="open-positions-heading" className="mt-2 text-lg font-semibold text-foreground">Open positions</h2>
      </div>

      {positions.length === 0 ? (
        <div className="p-6">
          <p className="text-sm font-medium text-foreground">No open positions yet</p>
          <p className="mt-2 text-xs leading-5 text-secondary">Record a BUY transaction to create the first position. Closed securities remain in transaction history.</p>
        </div>
      ) : (
        <div
          className={`grid gap-4 p-4 sm:p-5 ${
            positions.length === 1
              ? "grid-cols-1"
              : "grid-cols-1 md:grid-cols-2 2xl:grid-cols-3"
          }`}
        >
          {positions.map((position) => {
            const gain = position.unrealized_gain_loss ? Number(position.unrealized_gain_loss) : null;
            return (
              <article key={position.ticker} className="min-w-0 border border-border bg-background/35 p-4 sm:p-5">
                <div className="flex items-start justify-between gap-4">
                  <div className="min-w-0">
                    <Link href={`/companies/${encodeURIComponent(position.ticker)}`} className="font-mono text-base font-semibold text-positive outline-none hover:underline focus-visible:ring-2 focus-visible:ring-positive">
                      {position.ticker}
                    </Link>
                    <p className="mt-1 truncate text-[11px] text-secondary">{position.company_name}</p>
                  </div>
                  <span className={`border px-2 py-1 font-mono text-[9px] uppercase tracking-wide ${position.manual_price ? "border-positive/30 bg-positive/10 text-positive" : "border-warning/40 bg-warning/10 text-warning"}`}>
                    {position.manual_price ? "Manual mark" : "Price required"}
                  </span>
                </div>

                <dl
                  className={`mt-5 grid grid-cols-2 gap-x-4 gap-y-3 text-xs ${
                    positions.length === 1 ? "md:grid-cols-3" : ""
                  }`}
                >
                  <div><dt className="text-secondary">Quantity</dt><dd className="financial-figure mt-1 font-mono text-foreground">{formatExactQuantity(position.quantity)}</dd></div>
                  <div><dt className="text-secondary">Average cost</dt><dd className="financial-figure mt-1 font-mono text-foreground">{formatExactCurrency(position.average_cost, currency)}</dd></div>
                  <div><dt className="text-secondary">Open cost basis</dt><dd className="financial-figure mt-1 font-mono text-foreground">{formatExactCurrency(position.open_cost_basis, currency)}</dd></div>
                  <div><dt className="text-secondary">Manual price</dt><dd className={`financial-figure mt-1 font-mono ${position.manual_price ? "text-foreground" : "text-warning"}`}>{position.manual_price ? formatExactCurrency(position.manual_price, currency) : "Price required"}</dd></div>
                  <div><dt className="text-secondary">Market value</dt><dd className="financial-figure mt-1 font-mono text-foreground">{position.market_value ? formatExactCurrency(position.market_value, currency) : "Unavailable"}</dd></div>
                  <div><dt className="text-secondary">Unrealized P/L</dt><dd className={`financial-figure mt-1 font-mono ${gain === null ? "text-secondary" : gain >= 0 ? "text-positive" : "text-warning"}`}>{position.unrealized_gain_loss ? `${formatSignedExactCurrency(position.unrealized_gain_loss, currency)} (${Number(position.unrealized_return_percent).toFixed(2)}%)` : "Unavailable"}</dd></div>
                </dl>

                <p className="mt-4 min-h-4 font-mono text-[9px] text-secondary">
                  {position.price_as_of ? `Manual mark as of ${formatAsOf(position.price_as_of)}` : "No market price has been entered."}
                </p>
                <button type="button" onClick={() => setEditingTicker(position.ticker)} disabled={busy} className="mt-3 border border-border px-3 py-2 font-mono text-[10px] font-semibold uppercase tracking-wider text-secondary outline-none hover:border-positive hover:text-positive focus-visible:ring-2 focus-visible:ring-positive disabled:opacity-50">
                  {position.manual_price ? "Update manual price" : "Set manual price"}
                </button>

                {editingTicker === position.ticker ? (
                  <ManualPriceForm
                    key={`${position.ticker}-${position.manual_price ?? "new"}`}
                    position={position}
                    busy={busy}
                    onSave={async (ticker, price) => {
                      try {
                        await onSetMark(ticker, price);
                        setEditingTicker(null);
                      } catch {
                        // The shared mutation alert explains the failure; keep this editor open.
                      }
                    }}
                    onCancel={() => setEditingTicker(null)}
                  />
                ) : null}
              </article>
            );
          })}
        </div>
      )}
    </section>
  );
}
