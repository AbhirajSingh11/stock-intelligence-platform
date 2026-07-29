interface DashboardErrorProps {
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

export function DashboardLoading() {
  return (
    <div
      className="space-y-6"
      role="status"
      aria-live="polite"
      aria-label="Loading dashboard data"
    >
      <section>
        <div className="mb-3 flex items-center justify-between">
          <SkeletonBlock className="h-3 w-32" />
          <SkeletonBlock className="h-3 w-24" />
        </div>
        <div className="grid grid-cols-2 border-l border-t border-border xl:grid-cols-4">
          {Array.from({ length: 4 }, (_, index) => (
            <div
              key={index}
              className="border-b border-r border-border bg-panel p-4 sm:p-5"
            >
              <SkeletonBlock className="h-2.5 w-24" />
              <SkeletonBlock className="mt-4 h-6 w-32" />
              <SkeletonBlock className="mt-4 h-2.5 w-20" />
            </div>
          ))}
        </div>
      </section>

      <div className="grid items-start gap-4 xl:grid-cols-[minmax(0,2fr)_minmax(300px,0.85fr)]">
        <div className="border border-border bg-panel p-5">
          <div className="flex items-start justify-between border-b border-border pb-5">
            <div>
              <SkeletonBlock className="h-2.5 w-36" />
              <SkeletonBlock className="mt-3 h-7 w-44" />
            </div>
            <SkeletonBlock className="h-9 w-52" />
          </div>
          <SkeletonBlock className="mt-6 h-64 w-full" />
        </div>

        <div className="border border-border bg-panel">
          <div className="border-b border-border p-5">
            <SkeletonBlock className="h-2.5 w-28" />
            <SkeletonBlock className="mt-3 h-5 w-32" />
          </div>
          {Array.from({ length: 3 }, (_, index) => (
            <div key={index} className="border-b border-border p-5 last:border-0">
              <SkeletonBlock className="h-4 w-28" />
              <SkeletonBlock className="mt-3 h-3 w-40" />
            </div>
          ))}
        </div>
      </div>

      <section>
        <SkeletonBlock className="mb-3 h-5 w-28" />
        <div className="grid gap-3 md:grid-cols-3">
          {Array.from({ length: 3 }, (_, index) => (
            <div key={index} className="border border-border bg-panel p-5">
              <SkeletonBlock className="h-5 w-16" />
              <SkeletonBlock className="mt-2 h-3 w-36" />
              <SkeletonBlock className="mt-7 h-7 w-28" />
              <SkeletonBlock className="mt-6 h-px w-full" />
              <SkeletonBlock className="mt-4 h-4 w-full" />
            </div>
          ))}
        </div>
      </section>
      <span className="sr-only">Loading dashboard data…</span>
    </div>
  );
}

export function DashboardError({ message, onRetry }: DashboardErrorProps) {
  return (
    <section
      className="border border-warning/50 bg-panel p-6 sm:p-8"
      role="alert"
      aria-labelledby="dashboard-error-heading"
    >
      <p className="font-mono text-[10px] font-semibold uppercase tracking-[0.18em] text-warning">
        Data connection unavailable
      </p>
      <h2
        id="dashboard-error-heading"
        className="mt-3 text-xl font-semibold text-foreground"
      >
        Dashboard data could not be loaded
      </h2>
      <p className="mt-3 max-w-2xl text-sm leading-6 text-secondary">
        {message}
      </p>
      <button
        type="button"
        onClick={onRetry}
        className="mt-6 border border-warning bg-warning px-4 py-2.5 font-mono text-xs font-semibold uppercase tracking-wider text-[#171006] outline-none hover:bg-[#F0B75F] focus-visible:ring-2 focus-visible:ring-warning focus-visible:ring-offset-2 focus-visible:ring-offset-background"
      >
        Retry connection
      </button>
    </section>
  );
}

