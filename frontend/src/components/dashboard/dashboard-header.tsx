import { Icon } from "./icons";

export function DashboardHeader() {
  return (
    <header className="border-b border-border bg-background/95 px-4 py-4 sm:px-6 lg:px-8">
      <div className="mx-auto flex max-w-[1500px] flex-col gap-4 xl:flex-row xl:items-center xl:justify-between">
        <div>
          <p className="font-mono text-[10px] uppercase tracking-[0.2em] text-secondary">
            Portfolio intelligence
          </p>
          <h1 className="mt-1 text-2xl font-semibold tracking-tight text-foreground">
            Dashboard
          </h1>
        </div>

        <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
          <div className="relative min-w-0 sm:w-80">
            <label htmlFor="ticker-search" className="sr-only">
              Search by ticker or company
            </label>
            <Icon
              name="search"
              className="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-secondary"
            />
            <input
              id="ticker-search"
              type="search"
              placeholder="Search ticker or company"
              className="h-10 w-full border border-border bg-panel pl-10 pr-3 text-sm text-foreground outline-none placeholder:text-secondary/70 focus:border-positive focus:ring-1 focus:ring-positive"
            />
          </div>

          <div className="flex items-center justify-between gap-4 sm:justify-start">
            <div className="border-l border-border pl-4">
              <div className="flex items-center gap-2 font-mono text-[10px] font-semibold uppercase tracking-wider text-positive">
                <span className="size-1.5 bg-positive" aria-hidden="true" />
                Market open
              </div>
              <p className="mt-1 font-mono text-[10px] text-secondary">
                Closes 3:00 PM CT
              </p>
            </div>

            <div
              className="flex size-9 items-center justify-center border border-border bg-panel font-mono text-xs font-semibold text-foreground"
              role="img"
              aria-label="User avatar placeholder"
            >
              AI
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}

