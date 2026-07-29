import { CompanySearch } from "@/components/company/company-search";

interface DashboardHeaderProps {
  title?: string;
  eyebrow?: string;
}

export function DashboardHeader({
  title = "Dashboard",
  eyebrow = "Portfolio intelligence",
}: DashboardHeaderProps) {
  return (
    <header className="border-b border-border bg-background/95 px-4 py-4 sm:px-6 lg:px-8">
      <div className="mx-auto flex max-w-[1500px] flex-col gap-4 xl:flex-row xl:items-center xl:justify-between">
        <div>
          <p className="font-mono text-[10px] uppercase tracking-[0.2em] text-secondary">
            {eyebrow}
          </p>
          <h1 className="mt-1 text-2xl font-semibold tracking-tight text-foreground">
            {title}
          </h1>
        </div>

        <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
          <CompanySearch />

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
              className="flex h-9 items-center gap-2 border border-border bg-panel px-2.5 font-mono"
              aria-disabled="true"
              aria-label="AI assistant planned"
            >
              <span className="text-xs font-semibold text-secondary">AI</span>
              <span className="border border-warning/30 bg-warning/10 px-1.5 py-0.5 text-[8px] uppercase tracking-wider text-warning">
                Planned
              </span>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}
