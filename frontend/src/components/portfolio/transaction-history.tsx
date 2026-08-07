import {
  formatExactCurrency,
  formatExactQuantity,
  formatSecDate,
} from "@/lib/formatters";
import type { PortfolioTransaction } from "@/types/portfolio";

export function TransactionHistory({
  transactions,
  currency,
  busy,
  onEdit,
  onRequestDelete,
}: {
  transactions: PortfolioTransaction[];
  currency: string;
  busy: boolean;
  onEdit: (transaction: PortfolioTransaction) => void;
  onRequestDelete: (transaction: PortfolioTransaction) => void;
}) {
  return (
    <section className="border border-border bg-panel" aria-labelledby="transaction-history-heading">
      <div className="flex items-end justify-between gap-4 border-b border-border p-5">
        <div>
          <p className="font-mono text-[10px] uppercase tracking-[0.18em] text-secondary">Newest first</p>
          <h2 id="transaction-history-heading" className="mt-2 text-lg font-semibold text-foreground">Transaction history</h2>
        </div>
        <p className="font-mono text-[10px] text-secondary">{`${transactions.length} ${transactions.length === 1 ? "entry" : "entries"}`}</p>
      </div>

      {transactions.length === 0 ? (
        <div className="p-6 text-sm text-secondary">No transactions recorded. Use the ledger form to add the first BUY.</div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full min-w-[980px] border-collapse text-left">
            <thead className="border-b border-border bg-background/50 font-mono text-[9px] uppercase tracking-wider text-secondary">
              <tr>
                <th className="px-4 py-3 font-medium" scope="col">Date</th>
                <th className="px-4 py-3 font-medium" scope="col">Side</th>
                <th className="px-4 py-3 font-medium" scope="col">Security</th>
                <th className="px-4 py-3 text-right font-medium" scope="col">Quantity</th>
                <th className="px-4 py-3 text-right font-medium" scope="col">Price</th>
                <th className="px-4 py-3 text-right font-medium" scope="col">Gross</th>
                <th className="px-4 py-3 text-right font-medium" scope="col">Fees</th>
                <th className="px-4 py-3 font-medium" scope="col">Notes</th>
                <th className="px-4 py-3 font-medium" scope="col">Actions</th>
              </tr>
            </thead>
            <tbody>
              {transactions.map((transaction) => (
                <tr key={transaction.id} className="border-b border-border last:border-0">
                  <td className="whitespace-nowrap px-4 py-4 font-mono text-xs text-foreground">{formatSecDate(transaction.trade_date)}</td>
                  <td className="px-4 py-4"><span className={`border px-2 py-1 font-mono text-[9px] font-semibold ${transaction.side === "BUY" ? "border-positive/30 bg-positive/10 text-positive" : "border-warning/40 bg-warning/10 text-warning"}`}>{transaction.side}</span></td>
                  <td className="px-4 py-4"><p className="font-mono text-xs font-semibold text-foreground">{transaction.ticker}</p><p className="mt-1 max-w-48 truncate text-[10px] text-secondary">{transaction.company_name}</p></td>
                  <td className="financial-figure whitespace-nowrap px-4 py-4 text-right font-mono text-xs text-foreground">{formatExactQuantity(transaction.quantity)}</td>
                  <td className="financial-figure whitespace-nowrap px-4 py-4 text-right font-mono text-xs text-foreground">{formatExactCurrency(transaction.price_per_share, currency)}</td>
                  <td className="financial-figure whitespace-nowrap px-4 py-4 text-right font-mono text-xs text-foreground">{formatExactCurrency(transaction.gross_amount, currency)}</td>
                  <td className="financial-figure whitespace-nowrap px-4 py-4 text-right font-mono text-xs text-secondary">{formatExactCurrency(transaction.fees, currency)}</td>
                  <td className="max-w-56 px-4 py-4 text-xs leading-5 text-secondary">{transaction.notes ?? "—"}</td>
                  <td className="px-4 py-4"><div className="flex gap-2"><button type="button" onClick={() => onEdit(transaction)} disabled={busy} aria-label={`Edit ${transaction.ticker} transaction from ${transaction.trade_date}`} className="border border-border px-2.5 py-1.5 font-mono text-[9px] uppercase tracking-wider text-secondary outline-none hover:text-foreground focus-visible:ring-2 focus-visible:ring-positive disabled:opacity-50">Edit</button><button type="button" onClick={() => onRequestDelete(transaction)} disabled={busy} aria-label={`Delete ${transaction.ticker} transaction from ${transaction.trade_date}`} className="border border-warning/50 px-2.5 py-1.5 font-mono text-[9px] uppercase tracking-wider text-warning outline-none hover:bg-warning/10 focus-visible:ring-2 focus-visible:ring-warning disabled:opacity-50">Delete</button></div></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}
