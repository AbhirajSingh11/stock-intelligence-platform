"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useRef, useState, type FormEvent } from "react";

import { ConfirmationDialog } from "@/components/ui/confirmation-dialog";
import {
  addThesisEvidence,
  deleteThesis,
  deleteThesisEvidence,
  getThesis,
  markThesisReviewed,
  updateThesis,
  updateThesisEvidence,
} from "@/lib/api/client";
import { formatSecDate, formatUtcTimestamp } from "@/lib/formatters";
import type { EvidenceInput, ThesisDetail as ThesisDetailType, ThesisEvidence, ThesisFieldsInput } from "@/types/thesis";
import { EvidenceForm } from "./evidence-form";
import { ConvictionBadge, SignalBadge, StanceBadge, StatusBadge } from "./thesis-badges";
import { ThesisForm } from "./thesis-form";
import { ThesisError, ThesisLoading } from "./thesis-states";

type LoadState = { status: "loading" } | { status: "error"; message: string } | { status: "success"; data: ThesisDetailType };
type DeleteTarget = { kind: "thesis" } | { kind: "evidence"; evidence: ThesisEvidence };
const initialState: LoadState = { status: "loading" };

export function ThesisDetail({ ticker }: { ticker: string }) {
  const router = useRouter();
  const editButtonRef = useRef<HTMLButtonElement>(null);
  const evidenceButtonRef = useRef<HTMLButtonElement>(null);
  const [state, setState] = useState<LoadState>(initialState);
  const [version, setVersion] = useState(0);
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [editingThesis, setEditingThesis] = useState(false);
  const [editingEvidence, setEditingEvidence] = useState<ThesisEvidence | null>(null);
  const [addingEvidence, setAddingEvidence] = useState(false);
  const [reviewDueDate, setReviewDueDate] = useState("");
  const [deleteTarget, setDeleteTarget] = useState<DeleteTarget | null>(null);

  useEffect(() => {
    const controller = new AbortController();
    getThesis(ticker, controller.signal).then((data) => {
      setState({ status: "success", data });
      setReviewDueDate(data.review_due_date ?? "");
    }).catch((caught: unknown) => {
      if (caught instanceof DOMException && caught.name === "AbortError") return;
      setState({ status: "error", message: caught instanceof Error ? caught.message : "An unexpected thesis error occurred." });
    });
    return () => controller.abort();
  }, [ticker, version]);

  function announce(success: string) { setMessage(success); setError(""); }
  function fail(caught: unknown) { setMessage(""); setError(caught instanceof Error ? caught.message : "The thesis change could not be saved."); }

  if (state.status === "loading") return <ThesisLoading label={`Loading ${ticker} thesis`} />;
  if (state.status === "error") return <ThesisError message={state.message} onRetry={() => { setState(initialState); setVersion((value) => value + 1); }} />;

  const thesis = state.data;

  async function save(action: () => Promise<ThesisDetailType>, success: string) {
    if (busy) return;
    setBusy(true);
    try { const data = await action(); setState({ status: "success", data }); setReviewDueDate(data.review_due_date ?? ""); announce(success); }
    catch (caught) { fail(caught); throw caught; }
    finally { setBusy(false); }
  }

  return <div className="space-y-5">
    <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
      <Link href="/thesis" className="font-mono text-[10px] font-semibold uppercase tracking-wider text-positive outline-none hover:underline focus-visible:ring-2 focus-visible:ring-positive">← Thesis journal</Link>
      <p className="font-mono text-[9px] uppercase tracking-wider text-secondary">{`Updated ${formatUtcTimestamp(thesis.updated_at)}`}</p>
    </div>

    <div className="sr-only" aria-live="polite">{message}</div>
    {message ? <p className="border border-positive/40 bg-positive/5 p-3 text-sm text-positive">{message}</p> : null}
    {error ? <p className="border border-warning/50 bg-warning/5 p-3 text-sm text-warning" role="alert">{error}</p> : null}

    {editingThesis ? <ThesisForm thesis={thesis} busy={busy} onCancel={() => { setEditingThesis(false); requestAnimationFrame(() => editButtonRef.current?.focus()); }} onSubmit={async (input) => {
      try { await save(() => updateThesis(thesis.ticker, input as ThesisFieldsInput), "Thesis updated."); setEditingThesis(false); }
      catch { /* Persistent error remains visible. */ }
    }} /> : <>
      <section className="border border-border bg-panel p-5 sm:p-6">
        <div className="flex flex-col gap-5 lg:flex-row lg:items-start lg:justify-between">
          <div className="min-w-0"><p className="font-mono text-sm font-semibold text-positive">{thesis.ticker}</p><p className="mt-1 text-sm text-secondary">{`${thesis.company_name} · CIK ${thesis.cik}`}</p><h1 className="mt-4 text-2xl font-semibold tracking-tight text-foreground sm:text-3xl">{thesis.title}</h1><p className="mt-4 max-w-4xl text-sm leading-7 text-secondary">{thesis.summary}</p></div>
          <div className="flex shrink-0 flex-wrap gap-2"><StatusBadge status={thesis.status} /><SignalBadge signal={thesis.signal} /></div>
        </div>
        <div className="mt-6 flex flex-wrap items-center gap-3 border-t border-border pt-5"><ConvictionBadge conviction={thesis.conviction} />{thesis.is_overdue ? <span className="border border-warning/50 bg-warning/10 px-2 py-1 font-mono text-[9px] uppercase tracking-wider text-warning">Review overdue</span> : null}</div>
        <div className="mt-5 flex flex-wrap gap-3"><button ref={editButtonRef} type="button" onClick={() => { setEditingThesis(true); setError(""); }} className="border border-positive px-3 py-2 font-mono text-[10px] font-semibold uppercase tracking-wider text-positive outline-none hover:bg-positive/10 focus-visible:ring-2 focus-visible:ring-positive">Edit thesis</button><button type="button" onClick={() => setDeleteTarget({ kind: "thesis" })} className="border border-warning/60 px-3 py-2 font-mono text-[10px] font-semibold uppercase tracking-wider text-warning outline-none hover:bg-warning/10 focus-visible:ring-2 focus-visible:ring-warning">Delete thesis</button></div>
      </section>

      <div className="grid gap-4 lg:grid-cols-3">
        <CasePanel eyebrow="Upside case" title="Bull case" value={thesis.bull_case} tone="positive" />
        <CasePanel eyebrow="Downside case" title="Bear case" value={thesis.bear_case} tone="warning" />
        <CasePanel eyebrow="Decision rule" title="Invalidation criteria" value={thesis.invalidation_criteria} tone="warning" />
      </div>
    </>}

    <section className="border border-border bg-panel p-5 sm:p-6">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between"><div><p className="font-mono text-[10px] uppercase tracking-[0.18em] text-secondary">Review discipline</p><h2 className="mt-2 text-lg font-semibold text-foreground">Review record</h2><p className="mt-2 text-sm text-secondary">{thesis.last_reviewed_at ? `Last reviewed ${formatUtcTimestamp(thesis.last_reviewed_at)}` : "This thesis has not been marked reviewed."}</p></div>
        <form className="flex flex-col gap-3 sm:flex-row sm:items-end" onSubmit={async (event: FormEvent<HTMLFormElement>) => { event.preventDefault(); try { await save(() => markThesisReviewed(thesis.ticker, reviewDueDate || null), "Thesis marked reviewed."); } catch { /* Persistent error remains visible. */ } }}>
          <label className="font-mono text-[9px] uppercase tracking-wider text-secondary">New due date (optional)<input type="date" value={reviewDueDate} onChange={(event) => setReviewDueDate(event.target.value)} className="mt-2 block w-full border border-border bg-background px-3 py-2 text-sm text-foreground outline-none focus-visible:ring-2 focus-visible:ring-positive" /></label>
          <button type="submit" disabled={busy} className="whitespace-nowrap border border-positive px-4 py-2.5 font-mono text-[10px] font-semibold uppercase tracking-wider text-positive outline-none hover:bg-positive/10 focus-visible:ring-2 focus-visible:ring-positive disabled:opacity-50">Mark reviewed</button>
        </form>
      </div>
    </section>

    <section className="border border-border bg-panel">
      <div className="flex flex-col gap-4 border-b border-border p-5 sm:flex-row sm:items-end sm:justify-between sm:p-6"><div><p className="font-mono text-[10px] uppercase tracking-[0.18em] text-secondary">Evidence ledger</p><h2 className="mt-2 text-lg font-semibold text-foreground">Evidence</h2><p className="mt-2 font-mono text-[9px] uppercase tracking-wider text-secondary">{`${thesis.evidence_counts.supporting} supporting · ${thesis.evidence_counts.contradicting} contradicting · ${thesis.evidence_counts.neutral} neutral`}</p></div><button ref={evidenceButtonRef} type="button" onClick={() => { setAddingEvidence(true); setEditingEvidence(null); setError(""); }} className="self-start border border-positive px-4 py-2.5 font-mono text-[10px] font-semibold uppercase tracking-wider text-positive outline-none hover:bg-positive/10 focus-visible:ring-2 focus-visible:ring-positive sm:self-auto">Add evidence</button></div>
      <div className="space-y-4 p-4 sm:p-5">
        {addingEvidence ? <EvidenceForm busy={busy} onCancel={() => { setAddingEvidence(false); requestAnimationFrame(() => evidenceButtonRef.current?.focus()); }} onSubmit={async (input) => { try { await save(() => addThesisEvidence(thesis.ticker, input), "Evidence added."); setAddingEvidence(false); } catch { /* Persistent error remains visible. */ } }} /> : null}
        {thesis.evidence.length === 0 && !addingEvidence ? <div className="p-5 text-center"><h3 className="text-base font-semibold text-foreground">No evidence recorded</h3><p className="mt-2 text-sm text-secondary">Add a supporting, contradicting, or neutral observation without changing the thesis automatically.</p></div> : null}
        <ul className="space-y-3">{thesis.evidence.map((item) => <li key={item.id}>{editingEvidence?.id === item.id ? <EvidenceForm evidence={item} busy={busy} onCancel={() => setEditingEvidence(null)} onSubmit={async (input: EvidenceInput) => { try { await save(() => updateThesisEvidence(thesis.ticker, item.id, input), "Evidence updated."); setEditingEvidence(null); } catch { /* Persistent error remains visible. */ } }} /> : <article className="border border-border bg-sidebar p-4 sm:p-5"><div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between"><div className="min-w-0"><div className="flex flex-wrap items-center gap-2"><StanceBadge stance={item.stance} /><span className="font-mono text-[9px] uppercase tracking-wider text-secondary">{item.category.toLowerCase()}</span></div><h3 className="mt-3 text-base font-semibold text-foreground">{item.title}</h3></div><time dateTime={item.observed_on} className="shrink-0 font-mono text-[10px] text-secondary">{formatSecDate(item.observed_on)}</time></div><p className="mt-3 text-sm leading-6 text-secondary">{item.description}</p><div className="mt-4 flex flex-wrap items-center gap-4">{item.source_url ? <a href={item.source_url} target="_blank" rel="noopener noreferrer" className="font-mono text-[10px] font-semibold uppercase tracking-wider text-positive underline decoration-positive/40 underline-offset-4 outline-none hover:decoration-positive focus-visible:ring-2 focus-visible:ring-positive">Open source ↗<span className="sr-only"> (opens in a new tab)</span></a> : <span className="font-mono text-[9px] uppercase tracking-wider text-secondary">No source link</span>}<button type="button" onClick={() => { setEditingEvidence(item); setAddingEvidence(false); }} className="font-mono text-[10px] uppercase tracking-wider text-secondary outline-none hover:text-foreground focus-visible:ring-2 focus-visible:ring-positive">Edit</button><button type="button" onClick={() => setDeleteTarget({ kind: "evidence", evidence: item })} className="font-mono text-[10px] uppercase tracking-wider text-warning outline-none hover:underline focus-visible:ring-2 focus-visible:ring-warning">Delete</button></div></article>}</li>)}</ul>
      </div>
    </section>

    {deleteTarget ? <ConfirmationDialog title={deleteTarget.kind === "thesis" ? `Delete ${thesis.ticker} thesis?` : "Delete evidence?"} description={deleteTarget.kind === "thesis" ? "This permanently deletes the investment thesis and every evidence item attached to it. This cannot be undone." : `This permanently removes “${deleteTarget.evidence.title}” from the evidence ledger.`} confirmLabel={deleteTarget.kind === "thesis" ? "Delete thesis" : "Delete evidence"} busy={busy} onCancel={() => setDeleteTarget(null)} onConfirm={async () => {
      if (deleteTarget.kind === "thesis") { setBusy(true); try { await deleteThesis(thesis.ticker); router.push("/thesis"); } catch (caught) { fail(caught); setDeleteTarget(null); setBusy(false); } return; }
      const evidenceId = deleteTarget.evidence.id; setBusy(true); try { await deleteThesisEvidence(thesis.ticker, evidenceId); const data = await getThesis(thesis.ticker); setState({ status: "success", data }); announce("Evidence deleted."); } catch (caught) { fail(caught); } finally { setBusy(false); setDeleteTarget(null); }
    }} /> : null}
  </div>;
}

function CasePanel({ eyebrow, title, value, tone }: { eyebrow: string; title: string; value: string | null; tone: "positive" | "warning" }) {
  return <section className={`border bg-panel p-5 ${tone === "positive" ? "border-positive/30" : "border-warning/30"}`}><p className={`font-mono text-[9px] uppercase tracking-[0.16em] ${tone === "positive" ? "text-positive" : "text-warning"}`}>{eyebrow}</p><h2 className="mt-2 text-base font-semibold text-foreground">{title}</h2><p className="mt-3 text-sm leading-6 text-secondary">{value || "Not recorded."}</p></section>;
}
