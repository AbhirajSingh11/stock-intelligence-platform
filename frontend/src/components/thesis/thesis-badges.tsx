import type { EvidenceStance, ThesisConviction, ThesisSignal, ThesisStatus } from "@/types/thesis";

const signalStyles: Record<ThesisSignal, string> = {
  STRENGTHENING: "border-positive/40 bg-positive/10 text-positive",
  STABLE: "border-secondary/40 bg-secondary/10 text-secondary",
  WEAKENING: "border-warning/50 bg-warning/10 text-warning",
  REVIEW_REQUIRED: "border-warning/60 bg-warning/15 text-warning",
};

const stanceStyles: Record<EvidenceStance, string> = {
  SUPPORTING: "border-positive/40 bg-positive/10 text-positive",
  CONTRADICTING: "border-warning/50 bg-warning/10 text-warning",
  NEUTRAL: "border-secondary/40 bg-secondary/10 text-secondary",
};

function label(value: string): string {
  return value.toLowerCase().replaceAll("_", " ").replace(/^./, (character) => character.toUpperCase());
}

export function SignalBadge({ signal }: { signal: ThesisSignal }) {
  return <span className={`border px-2 py-1 font-mono text-[9px] font-semibold uppercase tracking-wide ${signalStyles[signal]}`}>{label(signal)}</span>;
}

export function StanceBadge({ stance }: { stance: EvidenceStance }) {
  return <span className={`border px-2 py-1 font-mono text-[9px] font-semibold uppercase tracking-wide ${stanceStyles[stance]}`}>{label(stance)}</span>;
}

export function StatusBadge({ status }: { status: ThesisStatus }) {
  return <span className="border border-border bg-sidebar px-2 py-1 font-mono text-[9px] uppercase tracking-wide text-secondary">{label(status)}</span>;
}

export function ConvictionBadge({ conviction }: { conviction: ThesisConviction }) {
  return <span className="font-mono text-[10px] uppercase tracking-wider text-foreground">{`${label(conviction)} conviction`}</span>;
}
