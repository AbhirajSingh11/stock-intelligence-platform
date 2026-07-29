const modules = [
  { name: "Watchlist", status: "Planned" },
  { name: "Portfolio", status: "Planned" },
  { name: "Filings", status: "Planned" },
  { name: "Investment theses", status: "Planned" },
] as const;

export default function Home() {
  return (
    <main className="min-h-screen bg-background text-foreground">
      <header className="border-b border-border bg-panel">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4 lg:px-8">
          <div className="flex items-center gap-3">
            <div
              className="flex size-9 items-center justify-center border border-emerald-500/40 bg-emerald-500/10 font-mono text-xs font-bold tracking-wider text-emerald-400"
              aria-hidden="true"
            >
              SI
            </div>
            <div>
              <p className="text-sm font-semibold tracking-wide text-white">
                STOCK INTELLIGENCE
              </p>
              <p className="font-mono text-[10px] uppercase tracking-[0.22em] text-muted">
                Research terminal
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2 font-mono text-xs text-emerald-400">
            <span className="size-2 bg-emerald-400" aria-hidden="true" />
            SYSTEM ONLINE
          </div>
        </div>
      </header>

      <div className="mx-auto max-w-6xl px-6 py-12 lg:px-8 lg:py-16">
        <section className="grid gap-8 border-b border-border pb-12 lg:grid-cols-[1.4fr_0.6fr] lg:items-end">
          <div>
            <p className="mb-4 font-mono text-xs font-medium uppercase tracking-[0.2em] text-emerald-400">
              Milestone 01 / Foundation
            </p>
            <h1 className="max-w-3xl text-4xl font-semibold tracking-tight text-white sm:text-5xl">
              Long-term investing,
              <span className="block text-slate-400">built on evidence.</span>
            </h1>
            <p className="mt-6 max-w-2xl text-base leading-7 text-muted">
              The application foundation is operational. Research, portfolio
              analytics, filings, and thesis tracking will arrive in focused,
              validated milestones.
            </p>
          </div>

          <div className="border border-border bg-panel p-5">
            <div className="flex items-center justify-between border-b border-border pb-4">
              <span className="font-mono text-xs uppercase tracking-wider text-muted">
                Frontend status
              </span>
              <span className="font-mono text-xs font-semibold text-emerald-400">
                HEALTHY
              </span>
            </div>
            <dl className="mt-4 space-y-3 font-mono text-xs">
              <div className="flex justify-between gap-6">
                <dt className="text-muted">Framework</dt>
                <dd className="text-slate-200">Next.js</dd>
              </div>
              <div className="flex justify-between gap-6">
                <dt className="text-muted">Interface</dt>
                <dd className="text-slate-200">App Router</dd>
              </div>
              <div className="flex justify-between gap-6">
                <dt className="text-muted">Health route</dt>
                <dd>
                  <a
                    className="text-emerald-400 underline decoration-emerald-400/30 underline-offset-4 hover:text-emerald-300"
                    href="/api/health"
                  >
                    /api/health
                  </a>
                </dd>
              </div>
            </dl>
          </div>
        </section>

        <section className="py-12" aria-labelledby="module-heading">
          <div className="mb-6 flex items-end justify-between gap-4">
            <div>
              <p className="font-mono text-xs uppercase tracking-[0.18em] text-muted">
                Product modules
              </p>
              <h2
                id="module-heading"
                className="mt-2 text-xl font-semibold text-white"
              >
                Deliberately not started
              </h2>
            </div>
            <p className="hidden font-mono text-xs text-amber-400 sm:block">
              SCOPE LOCKED TO MILESTONE 01
            </p>
          </div>

          <div className="grid border-l border-t border-border sm:grid-cols-2 lg:grid-cols-4">
            {modules.map((module, index) => (
              <article
                key={module.name}
                className="min-h-36 border-b border-r border-border bg-panel p-5"
              >
                <p className="font-mono text-[10px] text-slate-600">
                  {String(index + 1).padStart(2, "0")}
                </p>
                <h3 className="mt-7 text-sm font-medium text-slate-200">
                  {module.name}
                </h3>
                <p className="mt-2 font-mono text-[10px] uppercase tracking-wider text-amber-400">
                  {module.status}
                </p>
              </article>
            ))}
          </div>
        </section>
      </div>

      <footer className="border-t border-border">
        <div className="mx-auto flex max-w-6xl flex-col gap-2 px-6 py-5 font-mono text-[10px] uppercase tracking-wider text-muted sm:flex-row sm:items-center sm:justify-between lg:px-8">
          <span>Local development environment</span>
          <span>No paid services · No external data yet</span>
        </div>
      </footer>
    </main>
  );
}

