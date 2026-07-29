interface CompanyErrorProps {
  ticker: string;
  message: string;
  onRetry: () => void;
}

function SkeletonBlock({ className }: { className: string }) {
  return (
    <div
      className={`animate-pulse bg-white/[0.06] motion-reduce:animate-none ${className}`}
      aria-hidden="true"
    />
  );
}

export function CompanyLoading({ ticker }: { ticker: string }) {
  return (
    <div
      className="space-y-5"
      role="status"
      aria-live="polite"
      aria-label={`Loading SEC data for ${ticker}`}
    >
      <section className="border border-border bg-panel p-5 sm:p-6">
        <SkeletonBlock className="h-3 w-24" />
        <SkeletonBlock className="mt-3 h-8 w-72 max-w-full" />
        <SkeletonBlock className="mt-4 h-4 w-44" />
      </section>

      <section className="grid border-l border-t border-border sm:grid-cols-2 xl:grid-cols-5">
        {Array.from({ length: 5 }, (_, index) => (
          <div
            key={index}
            className="border-b border-r border-border bg-panel p-4"
          >
            <SkeletonBlock className="h-2.5 w-20" />
            <SkeletonBlock className="mt-3 h-4 w-28" />
          </div>
        ))}
      </section>

      <div className="grid gap-4 xl:grid-cols-2">
        {Array.from({ length: 2 }, (_, index) => (
          <section key={index} className="border border-border bg-panel p-5">
            <SkeletonBlock className="h-3 w-28" />
            <SkeletonBlock className="mt-4 h-4 w-48" />
            <SkeletonBlock className="mt-2 h-4 w-36" />
          </section>
        ))}
      </div>

      <section className="border border-border bg-panel">
        <div className="border-b border-border p-5">
          <SkeletonBlock className="h-3 w-32" />
          <SkeletonBlock className="mt-3 h-5 w-48" />
        </div>
        {Array.from({ length: 4 }, (_, index) => (
          <div key={index} className="border-b border-border p-5 last:border-0">
            <SkeletonBlock className="h-4 w-full" />
          </div>
        ))}
      </section>
      <span className="sr-only">{`Loading SEC company data for ${ticker}…`}</span>
    </div>
  );
}

export function CompanyError({
  ticker,
  message,
  onRetry,
}: CompanyErrorProps) {
  return (
    <section
      className="border border-warning/50 bg-panel p-6 sm:p-8"
      role="alert"
      aria-labelledby="company-error-heading"
    >
      <p className="font-mono text-[10px] font-semibold uppercase tracking-[0.18em] text-warning">
        SEC company data unavailable
      </p>
      <h2
        id="company-error-heading"
        className="mt-3 text-xl font-semibold text-foreground"
      >
        {`Could not load ${ticker}`}
      </h2>
      <p className="mt-3 max-w-2xl text-sm leading-6 text-secondary">
        {message}
      </p>
      <button
        type="button"
        onClick={onRetry}
        className="mt-6 border border-warning bg-warning px-4 py-2.5 font-mono text-xs font-semibold uppercase tracking-wider text-[#171006] outline-none hover:bg-[#F0B75F] focus-visible:ring-2 focus-visible:ring-warning focus-visible:ring-offset-2 focus-visible:ring-offset-background"
      >
        Retry SEC request
      </button>
    </section>
  );
}
