"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { SignalBadge, StatusBadge } from "@/components/thesis/thesis-badges";
import { getTheses } from "@/lib/api/client";
import type { ThesisSummary } from "@/types/thesis";

type State = { status: "loading" } | { status: "success"; thesis: ThesisSummary | null } | { status: "error" };

export function CompanyThesisSummary({ ticker }: { ticker: string }) {
  const [state, setState] = useState<State>({ status: "loading" });
  useEffect(() => {
    const controller = new AbortController();
    getTheses({ ticker }, controller.signal).then((response) => setState({ status: "success", thesis: response.theses[0] ?? null })).catch((error: unknown) => {
      if (error instanceof DOMException && error.name === "AbortError") return;
      setState({ status: "error" });
    });
    return () => controller.abort();
  }, [ticker]);

  return <section className="border border-border bg-panel p-5 sm:p-6" aria-labelledby="company-thesis-heading"><div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between"><div><p className="font-mono text-[10px] uppercase tracking-[0.18em] text-secondary">Investment thesis</p><h3 id="company-thesis-heading" className="mt-2 text-lg font-semibold text-foreground">Research case</h3></div>{state.status === "success" ? <Link href={state.thesis ? `/thesis/${encodeURIComponent(ticker)}` : `/thesis?create=${encodeURIComponent(ticker)}`} className="self-start border border-positive px-3 py-2 font-mono text-[10px] font-semibold uppercase tracking-wider text-positive outline-none hover:bg-positive/10 focus-visible:ring-2 focus-visible:ring-positive">{state.thesis ? "Open thesis" : "Create thesis"}</Link> : null}</div>
    {state.status === "loading" ? <div className="mt-4 h-16 animate-pulse bg-sidebar motion-reduce:animate-none" role="status" aria-label="Loading company thesis" /> : null}
    {state.status === "error" ? <p className="mt-4 text-sm text-warning">The thesis journal is currently unavailable.</p> : null}
    {state.status === "success" && !state.thesis ? <p className="mt-4 text-sm leading-6 text-secondary">No thesis exists for {ticker}. Create one to record the original case and compare future evidence.</p> : null}
    {state.status === "success" && state.thesis ? <div className="mt-4"><div className="flex flex-wrap gap-2"><StatusBadge status={state.thesis.status} /><SignalBadge signal={state.thesis.signal} />{state.thesis.is_overdue ? <span className="border border-warning/50 bg-warning/10 px-2 py-1 font-mono text-[9px] uppercase tracking-wide text-warning">Overdue</span> : null}</div><h4 className="mt-3 text-base font-semibold text-foreground">{state.thesis.title}</h4><p className="mt-2 text-sm leading-6 text-secondary">{state.thesis.summary}</p><p className="mt-3 font-mono text-[9px] uppercase tracking-wider text-secondary">{`${state.thesis.evidence_counts.total} evidence items · ${state.thesis.conviction.toLowerCase()} conviction`}</p></div> : null}
  </section>;
}
