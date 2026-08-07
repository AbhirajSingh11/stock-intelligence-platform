"use client";

import { useEffect, useState } from "react";

import { getDashboardOverview, getPortfolioOverview } from "@/lib/api/client";
import { formatAsOf } from "@/lib/formatters";
import type { DashboardOverviewResponse } from "@/types/dashboard";
import type { PortfolioOverviewResponse } from "@/types/portfolio";
import { DashboardError, DashboardLoading } from "./dashboard-states";
import { PortfolioPositionsOverview } from "./portfolio-positions-overview";
import { PortfolioSummary } from "./portfolio-summary";
import { ThesisSignals } from "./thesis-signals";
import { WatchlistGrid } from "./watchlist-grid";

type DashboardState =
  | { status: "loading" }
  | {
      status: "success";
      data: DashboardOverviewResponse;
      portfolio: PortfolioOverviewResponse;
    }
  | { status: "error"; message: string };

const initialDashboardState: DashboardState = { status: "loading" };
const dashboardSectionIds = new Set(["portfolio", "watchlist", "thesis"]);

export function DashboardOverview() {
  const [state, setState] = useState<DashboardState>(initialDashboardState);
  const [requestVersion, setRequestVersion] = useState(0);

  useEffect(() => {
    const controller = new AbortController();

    Promise.all([
      getDashboardOverview(controller.signal),
      getPortfolioOverview(controller.signal),
    ])
      .then(([data, portfolio]) => {
        setState({ status: "success", data, portfolio });
      })
      .catch((error: unknown) => {
        if (error instanceof DOMException && error.name === "AbortError") {
          return;
        }
        setState({
          status: "error",
          message:
            error instanceof Error
              ? error.message
              : "An unexpected error occurred while loading dashboard data.",
        });
      });

    return () => controller.abort();
  }, [requestVersion]);

  useEffect(() => {
    if (state.status !== "success") {
      return;
    }

    const sectionId = window.location.hash.slice(1);
    if (!dashboardSectionIds.has(sectionId)) {
      return;
    }

    const animationFrame = window.requestAnimationFrame(() => {
      document.getElementById(sectionId)?.scrollIntoView({ block: "start" });
    });

    return () => window.cancelAnimationFrame(animationFrame);
  }, [state.status]);

  function retry() {
    setState({ status: "loading" });
    setRequestVersion((version) => version + 1);
  }

  if (state.status === "loading") {
    return <DashboardLoading />;
  }

  if (state.status === "error") {
    return <DashboardError message={state.message} onRetry={retry} />;
  }

  const { data, portfolio } = state;

  return (
    <div className="space-y-6">
      <PortfolioSummary totals={portfolio.totals} currency={portfolio.currency} />

      <div
        id="portfolio"
        className="grid scroll-mt-36 items-start gap-4 lg:scroll-mt-8 xl:grid-cols-[minmax(0,2fr)_minmax(300px,0.85fr)]"
      >
        <PortfolioPositionsOverview portfolio={portfolio} />
        <div id="thesis" className="scroll-mt-36 lg:scroll-mt-8">
          <ThesisSignals signals={data.thesis_signals} />
        </div>
      </div>

      <WatchlistGrid />

      <p className="text-right font-mono text-[9px] uppercase tracking-wider text-secondary">
        {`Portfolio and theses persisted locally · Snapshot as of ${formatAsOf(data.as_of)}`}
      </p>
    </div>
  );
}
