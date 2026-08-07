"use client";

import { useState, type FormEvent } from "react";

import type {
  PortfolioTransaction,
  PortfolioTransactionInput,
  PortfolioTransactionUpdate,
  TransactionSide,
} from "@/types/portfolio";

interface FormValues {
  ticker: string;
  side: TransactionSide;
  tradeDate: string;
  quantity: string;
  pricePerShare: string;
  fees: string;
  notes: string;
}

function initialValues(transaction: PortfolioTransaction | null): FormValues {
  if (!transaction) {
    return {
      ticker: "",
      side: "BUY",
      tradeDate: "",
      quantity: "",
      pricePerShare: "",
      fees: "0",
      notes: "",
    };
  }
  return {
    ticker: transaction.ticker,
    side: transaction.side,
    tradeDate: transaction.trade_date,
    quantity: transaction.quantity,
    pricePerShare: transaction.price_per_share,
    fees: transaction.fees,
    notes: transaction.notes ?? "",
  };
}

function validate(values: FormValues): string | null {
  if (!values.ticker.trim()) return "Ticker is required.";
  if (!values.tradeDate) return "Trade date is required.";
  if (values.tradeDate > new Date().toISOString().slice(0, 10)) {
    return "Trade date cannot be in the future.";
  }
  if (!Number.isFinite(Number(values.quantity)) || Number(values.quantity) <= 0) {
    return "Quantity must be greater than zero.";
  }
  if (!Number.isFinite(Number(values.pricePerShare)) || Number(values.pricePerShare) <= 0) {
    return "Price per share must be greater than zero.";
  }
  if (!Number.isFinite(Number(values.fees)) || Number(values.fees) < 0) {
    return "Fees cannot be negative.";
  }
  return null;
}

const inputClass = "mt-1.5 h-10 w-full border border-border bg-background px-3 font-mono text-sm text-foreground outline-none placeholder:text-secondary/60 focus:border-positive focus:ring-1 focus:ring-positive disabled:opacity-60";

export function TransactionForm({
  transaction,
  busy,
  onSubmit,
  onCancel,
}: {
  transaction: PortfolioTransaction | null;
  busy: boolean;
  onSubmit: (input: PortfolioTransactionInput | PortfolioTransactionUpdate) => Promise<void>;
  onCancel: () => void;
}) {
  const [values, setValues] = useState<FormValues>(() => initialValues(transaction));
  const [validationMessage, setValidationMessage] = useState<string | null>(null);
  const editing = transaction !== null;

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (busy) return;
    const validation = validate(values);
    setValidationMessage(validation);
    if (validation) return;

    const shared = {
      side: values.side,
      trade_date: values.tradeDate,
      quantity: values.quantity,
      price_per_share: values.pricePerShare,
      fees: values.fees || "0",
      notes: values.notes.trim() || null,
    };
    await onSubmit(
      editing
        ? shared
        : { ...shared, ticker: values.ticker.trim().toUpperCase() },
    );
  }

  return (
    <section className="border border-border bg-panel" aria-labelledby="transaction-form-heading">
      <div className="border-b border-border p-5">
        <p className="font-mono text-[10px] uppercase tracking-[0.18em] text-secondary">Portfolio ledger</p>
        <h2 id="transaction-form-heading" className="mt-2 text-lg font-semibold text-foreground">
          {editing ? `Edit ${transaction.ticker} transaction` : "Record transaction"}
        </h2>
      </div>
      <form onSubmit={submit} className="space-y-4 p-5" noValidate>
        <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-1">
          <label className="text-xs font-medium text-secondary" htmlFor="portfolio-ticker">
            Ticker
            <input
              id="portfolio-ticker"
              value={values.ticker}
              onChange={(event) => setValues((current) => ({ ...current, ticker: event.target.value.toUpperCase() }))}
              disabled={editing || busy}
              autoComplete="off"
              maxLength={10}
              placeholder="MSFT"
              className={inputClass}
              required
            />
          </label>
          <label className="text-xs font-medium text-secondary" htmlFor="portfolio-side">
            Side
            <select id="portfolio-side" value={values.side} onChange={(event) => setValues((current) => ({ ...current, side: event.target.value as TransactionSide }))} disabled={busy} className={inputClass}>
              <option value="BUY">BUY</option>
              <option value="SELL">SELL</option>
            </select>
          </label>
        </div>

        <label className="block text-xs font-medium text-secondary" htmlFor="portfolio-trade-date">
          Trade date
          <input id="portfolio-trade-date" type="date" value={values.tradeDate} onChange={(event) => setValues((current) => ({ ...current, tradeDate: event.target.value }))} disabled={busy} className={inputClass} required />
        </label>

        <div className="grid gap-4 sm:grid-cols-3 xl:grid-cols-1">
          <label className="text-xs font-medium text-secondary" htmlFor="portfolio-quantity">
            Quantity
            <input id="portfolio-quantity" type="number" inputMode="decimal" min="0.00000001" step="any" value={values.quantity} onChange={(event) => setValues((current) => ({ ...current, quantity: event.target.value }))} disabled={busy} className={inputClass} placeholder="10" required />
          </label>
          <label className="text-xs font-medium text-secondary" htmlFor="portfolio-price">
            Price per share
            <input id="portfolio-price" type="number" inputMode="decimal" min="0.00000001" step="any" value={values.pricePerShare} onChange={(event) => setValues((current) => ({ ...current, pricePerShare: event.target.value }))} disabled={busy} className={inputClass} placeholder="100.00" required />
          </label>
          <label className="text-xs font-medium text-secondary" htmlFor="portfolio-fees">
            Fees
            <input id="portfolio-fees" type="number" inputMode="decimal" min="0" step="any" value={values.fees} onChange={(event) => setValues((current) => ({ ...current, fees: event.target.value }))} disabled={busy} className={inputClass} placeholder="0.00" required />
          </label>
        </div>

        <label className="block text-xs font-medium text-secondary" htmlFor="portfolio-notes">
          Notes <span className="font-normal text-secondary/70">(optional)</span>
          <textarea id="portfolio-notes" value={values.notes} onChange={(event) => setValues((current) => ({ ...current, notes: event.target.value }))} disabled={busy} maxLength={1000} rows={3} className="mt-1.5 w-full resize-y border border-border bg-background px-3 py-2 text-sm text-foreground outline-none placeholder:text-secondary/60 focus:border-positive focus:ring-1 focus:ring-positive disabled:opacity-60" placeholder="Reason for trade or correction" />
        </label>

        <p className="min-h-5 text-xs text-warning" role="alert" aria-live="polite">
          {validationMessage}
        </p>
        <div className="flex flex-wrap gap-3">
          <button type="submit" disabled={busy} className="border border-positive bg-positive px-4 py-2.5 font-mono text-xs font-semibold uppercase tracking-wider text-[#07120e] outline-none hover:bg-[#48D29D] focus-visible:ring-2 focus-visible:ring-positive focus-visible:ring-offset-2 focus-visible:ring-offset-panel disabled:cursor-wait disabled:opacity-50">
            {busy ? "Saving…" : editing ? "Save correction" : "Record transaction"}
          </button>
          {editing ? (
            <button type="button" onClick={onCancel} disabled={busy} className="border border-border px-4 py-2.5 font-mono text-xs uppercase tracking-wider text-secondary outline-none hover:text-foreground focus-visible:ring-2 focus-visible:ring-positive disabled:opacity-50">
              Cancel edit
            </button>
          ) : null}
        </div>
      </form>
    </section>
  );
}
