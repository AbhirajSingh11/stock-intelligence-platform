import type { Metadata } from "next";

import { DashboardHeader } from "@/components/dashboard/dashboard-header";
import { Sidebar } from "@/components/dashboard/sidebar";
import { PortfolioManager } from "@/components/portfolio/portfolio-manager";

export const metadata: Metadata = {
  title: "Portfolio | Stock Intelligence",
  description: "Persistent transactions, positions, and manual market marks.",
};

export default function PortfolioPage() {
  return (
    <div className="min-h-screen bg-background text-foreground">
      <Sidebar />
      <div className="min-w-0 lg:pl-60">
        <DashboardHeader title="Portfolio" eyebrow="Weighted-average ledger" />
        <main className="mx-auto max-w-[1500px] px-4 py-5 sm:px-6 sm:py-6 lg:px-8 lg:py-8">
          <PortfolioManager />
        </main>
        <footer className="border-t border-border px-4 py-4 sm:px-6 lg:px-8">
          <div className="mx-auto flex max-w-[1500px] flex-col gap-1 font-mono text-[9px] uppercase tracking-wider text-secondary sm:flex-row sm:items-center sm:justify-between">
            <span>Stock Intelligence · Local research environment</span>
            <span>Manual prices · Not live market data</span>
          </div>
        </footer>
      </div>
    </div>
  );
}
