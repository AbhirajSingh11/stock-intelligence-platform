import type { Metadata } from "next";

import { CompanyResearch } from "@/components/company/company-research";
import { DashboardHeader } from "@/components/dashboard/dashboard-header";
import { Sidebar } from "@/components/dashboard/sidebar";

interface CompanyPageProps {
  params: Promise<{ ticker: string }>;
}

export async function generateMetadata({
  params,
}: CompanyPageProps): Promise<Metadata> {
  const { ticker } = await params;
  const normalizedTicker = ticker.toUpperCase();
  return {
    title: `${normalizedTicker} Research | Stock Intelligence`,
    description: `SEC EDGAR company profile and recent filings for ${normalizedTicker}.`,
  };
}

export default async function CompanyPage({ params }: CompanyPageProps) {
  const { ticker } = await params;
  const normalizedTicker = ticker.toUpperCase();

  return (
    <div className="min-h-screen bg-background text-foreground">
      <Sidebar />

      <div className="min-w-0 lg:pl-60">
        <DashboardHeader
          title="Company Research"
          eyebrow="SEC EDGAR intelligence"
        />

        <main className="mx-auto max-w-[1500px] px-4 py-5 sm:px-6 sm:py-6 lg:px-8 lg:py-8">
          <CompanyResearch ticker={normalizedTicker} />
        </main>

        <footer className="border-t border-border px-4 py-4 sm:px-6 lg:px-8">
          <div className="mx-auto flex max-w-[1500px] flex-col gap-1 font-mono text-[9px] uppercase tracking-wider text-secondary sm:flex-row sm:items-center sm:justify-between">
            <span>Stock Intelligence · Local research environment</span>
            <span>Official company data · SEC EDGAR</span>
          </div>
        </footer>
      </div>
    </div>
  );
}
