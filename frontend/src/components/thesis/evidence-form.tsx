"use client";

import { useState, type FormEvent } from "react";

import type { EvidenceCategory, EvidenceInput, EvidenceStance, ThesisEvidence } from "@/types/thesis";

const fieldClass = "mt-2 w-full border border-border bg-background px-3 py-2.5 text-sm text-foreground outline-none placeholder:text-secondary/60 focus-visible:border-positive focus-visible:ring-2 focus-visible:ring-positive/40";
const labelClass = "font-mono text-[10px] font-semibold uppercase tracking-[0.14em] text-secondary";

export function EvidenceForm({ evidence, busy, onSubmit, onCancel }: { evidence?: ThesisEvidence; busy: boolean; onSubmit: (input: EvidenceInput) => Promise<void>; onCancel: () => void }) {
  const [stance, setStance] = useState<EvidenceStance>(evidence?.stance ?? "SUPPORTING");
  const [category, setCategory] = useState<EvidenceCategory>(evidence?.category ?? "FINANCIAL");
  const [title, setTitle] = useState(evidence?.title ?? "");
  const [description, setDescription] = useState(evidence?.description ?? "");
  const [sourceUrl, setSourceUrl] = useState(evidence?.source_url ?? "");
  const [observedOn, setObservedOn] = useState(evidence?.observed_on ?? "");

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    await onSubmit({ stance, category, title: title.trim(), description: description.trim(), source_url: sourceUrl.trim() || null, observed_on: observedOn });
  }

  return <form onSubmit={submit} className="border border-border bg-sidebar p-4 sm:p-5" aria-label={evidence ? "Edit evidence" : "Add evidence"}>
    <h3 className="text-base font-semibold text-foreground">{evidence ? "Edit evidence" : "Add evidence"}</h3>
    <p className="mt-1 text-xs text-secondary">Evidence is user-entered. A source link is stored only and is never fetched.</p>
    <div className="mt-4 grid gap-4 sm:grid-cols-2">
      <label className={labelClass}>Stance<select className={fieldClass} value={stance} onChange={(event) => setStance(event.target.value as EvidenceStance)}><option value="SUPPORTING">Supporting</option><option value="CONTRADICTING">Contradicting</option><option value="NEUTRAL">Neutral</option></select></label>
      <label className={labelClass}>Category<select className={fieldClass} value={category} onChange={(event) => setCategory(event.target.value as EvidenceCategory)}>{["FINANCIAL", "COMPETITIVE", "MANAGEMENT", "VALUATION", "CATALYST", "RISK", "FILING", "OTHER"].map((value) => <option key={value} value={value}>{value.toLowerCase()}</option>)}</select></label>
      <label className={`${labelClass} sm:col-span-2`}>Title<input className={fieldClass} required maxLength={200} value={title} onChange={(event) => setTitle(event.target.value)} placeholder="What changed?" /></label>
      <label className={`${labelClass} sm:col-span-2`}>Description<textarea className={fieldClass} required rows={4} value={description} onChange={(event) => setDescription(event.target.value)} placeholder="Describe the observation and why it matters" /></label>
      <label className={labelClass}>Observed on<input className={fieldClass} type="date" required value={observedOn} onChange={(event) => setObservedOn(event.target.value)} /></label>
      <label className={labelClass}>Source URL (optional)<input className={fieldClass} type="url" inputMode="url" value={sourceUrl} onChange={(event) => setSourceUrl(event.target.value)} placeholder="https://www.sec.gov/…" /></label>
    </div>
    <div className="mt-5 flex flex-col gap-3 sm:flex-row"><button type="submit" disabled={busy} className="border border-positive bg-positive px-4 py-2.5 font-mono text-xs font-semibold uppercase tracking-wider text-[#07130f] outline-none hover:bg-[#43d39b] focus-visible:ring-2 focus-visible:ring-positive disabled:opacity-50">{busy ? "Saving…" : evidence ? "Save evidence" : "Add evidence"}</button><button type="button" onClick={onCancel} disabled={busy} className="border border-border px-4 py-2.5 font-mono text-xs uppercase tracking-wider text-secondary outline-none hover:text-foreground focus-visible:ring-2 focus-visible:ring-positive disabled:opacity-50">Cancel</button></div>
  </form>;
}
