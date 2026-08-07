import type { Metadata } from "next";

import { DashboardHeader } from "@/components/dashboard/dashboard-header";
import { Sidebar } from "@/components/dashboard/sidebar";
import { ThesisDetail } from "@/components/thesis/thesis-detail";

interface ThesisPageProps { params: Promise<{ ticker: string }> }

export async function generateMetadata({ params }: ThesisPageProps): Promise<Metadata> {
  const { ticker } = await params;
  return { title: `${ticker.toUpperCase()} Thesis | Stock Intelligence`, description: `Investment thesis and evidence journal for ${ticker.toUpperCase()}.` };
}

export default async function ThesisPage({ params }: ThesisPageProps) {
  const { ticker } = await params;
  const normalizedTicker = ticker.toUpperCase();
  return <div className="min-h-screen bg-background text-foreground"><Sidebar /><div className="min-w-0 lg:pl-60"><DashboardHeader title={`${normalizedTicker} Thesis`} eyebrow="Evidence journal" /><main className="mx-auto max-w-[1500px] px-4 py-5 sm:px-6 sm:py-6 lg:px-8 lg:py-8"><ThesisDetail ticker={normalizedTicker} /></main><footer className="border-t border-border px-4 py-4 sm:px-6 lg:px-8"><div className="mx-auto flex max-w-[1500px] flex-col gap-1 font-mono text-[9px] uppercase tracking-wider text-secondary sm:flex-row sm:items-center sm:justify-between"><span>Stock Intelligence · Local research environment</span><span>User-authored thesis · Manual evidence</span></div></footer></div></div>;
}
