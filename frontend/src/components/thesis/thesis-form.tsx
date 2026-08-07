"use client";

import { useState, type FormEvent } from "react";

import type { ThesisCreateInput, ThesisDetail, ThesisFieldsInput } from "@/types/thesis";

const inputClass = "mt-2 w-full border border-border bg-background px-3 py-2.5 text-sm text-foreground outline-none placeholder:text-secondary/60 focus-visible:border-positive focus-visible:ring-2 focus-visible:ring-positive/40";
const labelClass = "font-mono text-[10px] font-semibold uppercase tracking-[0.14em] text-secondary";

interface ThesisFormProps {
  initialTicker?: string;
  thesis?: ThesisDetail;
  busy: boolean;
  onSubmit: (input: ThesisCreateInput | ThesisFieldsInput) => Promise<void>;
  onCancel: () => void;
}

export function ThesisForm({ initialTicker = "", thesis, busy, onSubmit, onCancel }: ThesisFormProps) {
  const [ticker, setTicker] = useState(thesis?.ticker ?? initialTicker);
  const [title, setTitle] = useState(thesis?.title ?? "");
  const [summary, setSummary] = useState(thesis?.summary ?? "");
  const [bullCase, setBullCase] = useState(thesis?.bull_case ?? "");
  const [bearCase, setBearCase] = useState(thesis?.bear_case ?? "");
  const [invalidation, setInvalidation] = useState(thesis?.invalidation_criteria ?? "");
  const [status, setStatus] = useState<ThesisFieldsInput["status"]>(thesis?.status ?? "DRAFT");
  const [conviction, setConviction] = useState<ThesisFieldsInput["conviction"]>(thesis?.conviction ?? "MEDIUM");
  const [signal, setSignal] = useState<ThesisFieldsInput["signal"]>(thesis?.signal ?? "STABLE");
  const [reviewDueDate, setReviewDueDate] = useState(thesis?.review_due_date ?? "");

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const fields: ThesisFieldsInput = {
      title: title.trim(),
      summary: summary.trim(),
      bull_case: bullCase.trim() || null,
      bear_case: bearCase.trim() || null,
      invalidation_criteria: invalidation.trim() || null,
      status,
      conviction,
      signal,
      review_due_date: reviewDueDate || null,
    };
    await onSubmit(thesis ? fields : { ...fields, ticker: ticker.trim().toUpperCase() });
  }

  return (
    <form onSubmit={submit} className="border border-border bg-panel p-5 sm:p-6" aria-label={thesis ? `Edit ${thesis.ticker} thesis` : "Create investment thesis"}>
      <div className="flex flex-col gap-2 border-b border-border pb-4 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className="font-mono text-[10px] uppercase tracking-[0.18em] text-positive">User-authored research</p>
          <h2 className="mt-2 text-lg font-semibold text-foreground">{thesis ? `Edit ${thesis.ticker} thesis` : "Create thesis"}</h2>
        </div>
        <p className="text-xs text-secondary">Signal and conviction are manual judgments.</p>
      </div>

      <div className="mt-5 grid gap-4 lg:grid-cols-2">
        {!thesis ? (
          <label className={labelClass}>Ticker
            <input className={inputClass} value={ticker} onChange={(event) => setTicker(event.target.value)} required maxLength={10} autoComplete="off" placeholder="MSFT" />
          </label>
        ) : null}
        <label className={`${labelClass} ${thesis ? "lg:col-span-2" : ""}`}>Title
          <input className={inputClass} value={title} onChange={(event) => setTitle(event.target.value)} required maxLength={200} placeholder="The core investment proposition" />
        </label>
        <label className={`${labelClass} lg:col-span-2`}>Summary
          <textarea className={inputClass} value={summary} onChange={(event) => setSummary(event.target.value)} required rows={3} placeholder="Why this company can compound value over time" />
        </label>
        <label className={labelClass}>Bull case
          <textarea className={inputClass} value={bullCase} onChange={(event) => setBullCase(event.target.value)} rows={3} placeholder="What must go right" />
        </label>
        <label className={labelClass}>Bear case
          <textarea className={inputClass} value={bearCase} onChange={(event) => setBearCase(event.target.value)} rows={3} placeholder="Material downside risks" />
        </label>
        <label className={`${labelClass} lg:col-span-2`}>Invalidation criteria
          <textarea className={inputClass} value={invalidation} onChange={(event) => setInvalidation(event.target.value)} rows={3} placeholder="Observable conditions that would invalidate the thesis" />
        </label>
        <label className={labelClass}>Status
          <select className={inputClass} value={status} onChange={(event) => setStatus(event.target.value as ThesisFieldsInput["status"])}>
            <option value="DRAFT">Draft</option><option value="ACTIVE">Active</option><option value="INVALIDATED">Invalidated</option><option value="ARCHIVED">Archived</option>
          </select>
        </label>
        <label className={labelClass}>Conviction
          <select className={inputClass} value={conviction} onChange={(event) => setConviction(event.target.value as ThesisFieldsInput["conviction"])}>
            <option value="LOW">Low</option><option value="MEDIUM">Medium</option><option value="HIGH">High</option>
          </select>
        </label>
        <label className={labelClass}>Signal
          <select className={inputClass} value={signal} onChange={(event) => setSignal(event.target.value as ThesisFieldsInput["signal"])}>
            <option value="STRENGTHENING">Strengthening</option><option value="STABLE">Stable</option><option value="WEAKENING">Weakening</option><option value="REVIEW_REQUIRED">Review required</option>
          </select>
        </label>
        <label className={labelClass}>Next review due
          <input type="date" className={inputClass} value={reviewDueDate} onChange={(event) => setReviewDueDate(event.target.value)} />
        </label>
      </div>

      <div className="mt-6 flex flex-col gap-3 sm:flex-row">
        <button type="submit" disabled={busy} className="border border-positive bg-positive px-4 py-2.5 font-mono text-xs font-semibold uppercase tracking-wider text-[#07130f] outline-none hover:bg-[#43d39b] focus-visible:ring-2 focus-visible:ring-positive focus-visible:ring-offset-2 focus-visible:ring-offset-panel disabled:cursor-wait disabled:opacity-50">{busy ? "Saving…" : thesis ? "Save thesis" : "Create thesis"}</button>
        <button type="button" onClick={onCancel} disabled={busy} className="border border-border px-4 py-2.5 font-mono text-xs uppercase tracking-wider text-secondary outline-none hover:text-foreground focus-visible:ring-2 focus-visible:ring-positive disabled:opacity-50">Cancel</button>
      </div>
    </form>
  );
}
