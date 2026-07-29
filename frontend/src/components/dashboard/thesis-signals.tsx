import type { SignalTone, ThesisSignal } from "@/types/dashboard";

interface ThesisSignalsProps {
  signals: ThesisSignal[];
}

const toneStyles: Record<SignalTone, string> = {
  positive: "border-positive/30 bg-positive/10 text-positive",
  warning: "border-warning/30 bg-warning/10 text-warning",
  neutral: "border-secondary/30 bg-secondary/10 text-secondary",
};

export function ThesisSignals({ signals }: ThesisSignalsProps) {
  return (
    <section
      className="border border-border bg-panel"
      aria-labelledby="thesis-signals-heading"
    >
      <div className="border-b border-border p-4 sm:p-5">
        <p className="text-[10px] font-semibold uppercase tracking-[0.16em] text-secondary">
          Evidence monitor
        </p>
        <h2
          id="thesis-signals-heading"
          className="mt-2 text-base font-semibold text-foreground"
        >
          Thesis signals
        </h2>
      </div>

      <ul className="divide-y divide-border">
        {signals.map((signal) => (
          <li key={signal.ticker} className="p-4 sm:p-5">
            <div className="flex items-start justify-between gap-3">
              <div className="min-w-0">
                <p className="truncate text-sm font-medium text-foreground">
                  {signal.company}
                </p>
                <p className="mt-1 font-mono text-[10px] text-secondary">
                  {signal.ticker}
                </p>
              </div>
              <span
                className={`shrink-0 border px-2 py-1 font-mono text-[9px] font-semibold uppercase tracking-wide ${toneStyles[signal.tone]}`}
              >
                {signal.state}
              </span>
            </div>
            <p className="mt-4 text-[11px] text-secondary">
              Last reviewed{" "}
              <time className="financial-figure font-mono text-foreground/80">
                {signal.lastReviewed}
              </time>
            </p>
          </li>
        ))}
      </ul>
    </section>
  );
}

