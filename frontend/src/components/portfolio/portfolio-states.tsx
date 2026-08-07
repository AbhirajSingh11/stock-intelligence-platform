function Skeleton({ className }: { className: string }) {
  return <div className={`animate-pulse bg-white/[0.06] motion-reduce:animate-none ${className}`} aria-hidden="true" />;
}

export function PortfolioLoading() {
  return (
    <div className="space-y-5" role="status" aria-label="Loading portfolio">
      <div className="grid grid-cols-2 gap-px bg-border lg:grid-cols-3 2xl:grid-cols-6">
        {Array.from({ length: 6 }, (_, index) => (
          <div key={index} className="bg-panel p-5">
            <Skeleton className="h-3 w-24" />
            <Skeleton className="mt-4 h-6 w-28" />
          </div>
        ))}
      </div>
      <div className="grid gap-4 xl:grid-cols-[360px_minmax(0,1fr)]">
        <Skeleton className="h-[460px] border border-border" />
        <Skeleton className="h-[460px] border border-border" />
      </div>
      <span className="sr-only">Loading portfolio data…</span>
    </div>
  );
}

export function PortfolioLoadError({ message, onRetry }: { message: string; onRetry: () => void }) {
  return (
    <section className="border border-warning/50 bg-panel p-6 sm:p-8" role="alert">
      <p className="font-mono text-[10px] font-semibold uppercase tracking-[0.18em] text-warning">Portfolio unavailable</p>
      <h2 className="mt-3 text-xl font-semibold text-foreground">The local portfolio could not be loaded</h2>
      <p className="mt-3 max-w-2xl text-sm leading-6 text-secondary">{message}</p>
      <button type="button" onClick={onRetry} className="mt-5 border border-warning bg-warning px-4 py-2.5 font-mono text-xs font-semibold uppercase tracking-wider text-[#171006] outline-none hover:bg-[#F0B75F] focus-visible:ring-2 focus-visible:ring-warning focus-visible:ring-offset-2 focus-visible:ring-offset-background">
        Retry
      </button>
    </section>
  );
}
