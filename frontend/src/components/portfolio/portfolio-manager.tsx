"use client";

import { useEffect, useState } from "react";

import { ApiRequestError } from "@/lib/api/client";
import {
  createPortfolioTransaction,
  deletePortfolioTransaction,
  getPortfolioOverview,
  getPortfolioTransactions,
  setPortfolioPriceMark,
  updatePortfolioTransaction,
} from "@/lib/api/client";
import type {
  PortfolioOverviewResponse,
  PortfolioTransaction,
  PortfolioTransactionInput,
  PortfolioTransactionUpdate,
} from "@/types/portfolio";
import { PortfolioSummary } from "@/components/dashboard/portfolio-summary";
import { ConfirmationDialog } from "@/components/ui/confirmation-dialog";
import { PortfolioPositions } from "./portfolio-positions";
import { PortfolioLoadError, PortfolioLoading } from "./portfolio-states";
import { TransactionForm } from "./transaction-form";
import { TransactionHistory } from "./transaction-history";

interface PortfolioData {
  overview: PortfolioOverviewResponse;
  transactions: PortfolioTransaction[];
}

type LoadState =
  | { status: "loading" }
  | { status: "error"; message: string }
  | { status: "success"; data: PortfolioData };

type MutationState =
  | { status: "idle" }
  | { status: "pending" }
  | { status: "success"; message: string }
  | { status: "error"; message: string };

const initialLoadState: LoadState = { status: "loading" };

function messageFrom(error: unknown): string {
  if (error instanceof ApiRequestError && error.code === "portfolio_ledger_conflict") {
    return "This change would oversell the position at some point in its chronological ledger. Review earlier buys, later sells, quantities, and trade dates.";
  }
  return error instanceof Error
    ? error.message
    : "An unexpected portfolio error occurred.";
}

async function loadPortfolio(signal?: AbortSignal): Promise<PortfolioData> {
  const [overview, history] = await Promise.all([
    getPortfolioOverview(signal),
    getPortfolioTransactions(undefined, signal),
  ]);
  return { overview, transactions: history.transactions };
}

export function PortfolioManager() {
  const [loadState, setLoadState] = useState<LoadState>(initialLoadState);
  const [mutation, setMutation] = useState<MutationState>({ status: "idle" });
  const [requestVersion, setRequestVersion] = useState(0);
  const [editing, setEditing] = useState<PortfolioTransaction | null>(null);
  const [deleteTarget, setDeleteTarget] = useState<PortfolioTransaction | null>(null);

  useEffect(() => {
    const controller = new AbortController();
    loadPortfolio(controller.signal)
      .then((data) => setLoadState({ status: "success", data }))
      .catch((error: unknown) => {
        if (error instanceof DOMException && error.name === "AbortError") return;
        setLoadState({ status: "error", message: messageFrom(error) });
      });
    return () => controller.abort();
  }, [requestVersion]);

  async function mutate(action: () => Promise<unknown>, successMessage: string) {
    if (mutation.status === "pending") return;
    setMutation({ status: "pending" });
    try {
      await action();
      const data = await loadPortfolio();
      setLoadState({ status: "success", data });
      setMutation({ status: "success", message: successMessage });
    } catch (error: unknown) {
      setMutation({ status: "error", message: messageFrom(error) });
      throw error;
    }
  }

  function retryLoad() {
    setLoadState(initialLoadState);
    setRequestVersion((version) => version + 1);
  }

  if (loadState.status === "loading") return <PortfolioLoading />;
  if (loadState.status === "error") return <PortfolioLoadError message={loadState.message} onRetry={retryLoad} />;

  const { overview, transactions } = loadState.data;
  const busy = mutation.status === "pending";

  return (
    <div className="space-y-6">
      <PortfolioSummary totals={overview.totals} currency={overview.currency} />

      {overview.totals.transaction_count === 0 ? (
        <section className="border border-positive/30 bg-positive/5 p-5">
          <p className="font-mono text-[10px] uppercase tracking-[0.18em] text-positive">Start the ledger</p>
          <h2 className="mt-2 text-lg font-semibold text-foreground">Record your first BUY transaction</h2>
          <p className="mt-2 max-w-3xl text-sm leading-6 text-secondary">Positions and gains are calculated only from transactions you enter. Market values appear only after you add manual current-price marks.</p>
        </section>
      ) : null}

      <div aria-live="polite" className="min-h-5">
        {mutation.status === "success" ? <p className="text-sm text-positive">{mutation.message}</p> : null}
        {mutation.status === "error" ? <p className="border border-warning/50 bg-warning/5 p-3 text-sm leading-5 text-warning" role="alert">{mutation.message}</p> : null}
      </div>

      <div className="grid items-start gap-4 xl:grid-cols-[360px_minmax(0,1fr)]">
        <TransactionForm
          key={editing ? `edit-${editing.id}-${editing.updated_at}` : `new-${transactions.length}`}
          transaction={editing}
          busy={busy}
          onSubmit={async (input) => {
            try {
              if (editing) {
                await mutate(
                  () => updatePortfolioTransaction(editing.id, input as PortfolioTransactionUpdate),
                  `${editing.ticker} transaction updated.`,
                );
                setEditing(null);
              } else {
                const createInput = input as PortfolioTransactionInput;
                await mutate(
                  () => createPortfolioTransaction(createInput),
                  `${createInput.ticker} transaction recorded.`,
                );
              }
            } catch {
              // The persistent error message above keeps the form available for correction.
            }
          }}
          onCancel={() => setEditing(null)}
        />
        <PortfolioPositions
          positions={overview.positions}
          currency={overview.currency}
          busy={busy}
          onSetMark={async (ticker, price) => {
            await mutate(
              () => setPortfolioPriceMark(ticker, { price }),
              `${ticker} manual price updated.`,
            );
          }}
        />
      </div>

      <TransactionHistory
        transactions={transactions}
        currency={overview.currency}
        busy={busy}
        onEdit={(transaction) => {
          setMutation({ status: "idle" });
          setEditing(transaction);
          document.getElementById("portfolio-ticker")?.scrollIntoView({ block: "center" });
        }}
        onRequestDelete={setDeleteTarget}
      />

      {deleteTarget ? (
        <ConfirmationDialog
          title={`Delete ${deleteTarget.ticker} transaction?`}
          description={`This permanently removes the ${deleteTarget.side} of ${deleteTarget.quantity} shares on ${deleteTarget.trade_date}. The remaining ledger will be replayed, and deletion will be rejected if it creates an oversell.`}
          confirmLabel="Delete transaction"
          busy={busy}
          onCancel={() => setDeleteTarget(null)}
          onConfirm={async () => {
            try {
              await mutate(
                () => deletePortfolioTransaction(deleteTarget.id),
                `${deleteTarget.ticker} transaction deleted.`,
              );
              setDeleteTarget(null);
              if (editing?.id === deleteTarget.id) setEditing(null);
            } catch {
              setDeleteTarget(null);
            }
          }}
        />
      ) : null}
    </div>
  );
}
