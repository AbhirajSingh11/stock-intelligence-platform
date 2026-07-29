import type { Metadata } from "next";

import { DashboardHeader } from "@/components/dashboard/dashboard-header";
import { PerformanceChart } from "@/components/dashboard/performance-chart";
import { PortfolioSummary } from "@/components/dashboard/portfolio-summary";
import { Sidebar } from "@/components/dashboard/sidebar";
import { ThesisSignals } from "@/components/dashboard/thesis-signals";
import { WatchlistGrid } from "@/components/dashboard/watchlist-grid";
import {
  portfolioSummary,
  thesisSignals,
  watchlist,
} from "@/data/dashboard";

export const metadata: Metadata = {
  title: "Dashboard | Stock Intelligence",
  description:
    "A static portfolio and research dashboard for the Stock Intelligence Platform.",
};

export default function DashboardPage() {
  return (
    <div className="min-h-screen bg-background text-foreground">
      <Sidebar />

      <div className="min-w-0 lg:pl-60">
        <DashboardHeader />

        <main className="mx-auto max-w-[1500px] space-y-6 px-4 py-5 sm:px-6 sm:py-6 lg:px-8 lg:py-8">
          <PortfolioSummary summary={portfolioSummary} />

          <div
            id="portfolio"
            className="grid items-start gap-4 xl:grid-cols-[minmax(0,2fr)_minmax(300px,0.85fr)]"
          >
            <PerformanceChart />
            <div id="thesis">
              <ThesisSignals signals={thesisSignals} />
            </div>
          </div>

          <WatchlistGrid items={watchlist} />
        </main>

        <footer className="border-t border-border px-4 py-4 sm:px-6 lg:px-8">
          <div className="mx-auto flex max-w-[1500px] flex-col gap-1 font-mono text-[9px] uppercase tracking-wider text-secondary sm:flex-row sm:items-center sm:justify-between">
            <span>Stock Intelligence · Local research environment</span>
            <span>Static mock data · No external services connected</span>
          </div>
        </footer>
      </div>
    </div>
  );
}

