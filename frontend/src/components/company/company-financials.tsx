"use client";

import { useEffect, useMemo, useState } from "react";

import { FinancialTrendChart } from "./financial-trend-chart";
import { getCompanyFundamentals } from "@/lib/api/client";
import {
  formatAsOf,
  formatFiscalPeriod,
  formatFundamentalValue,
  formatSecDate,
} from "@/lib/formatters";
import type {
  CompanyFundamentalsResponse,
  FundamentalFact,
  FundamentalMetricKey,
  FundamentalMetricSeries,
  FundamentalPeriod,
} from "@/types/company";

type FundamentalsState =
  | { status: "loading" }
  | { status: "success"; data: CompanyFundamentalsResponse }
  | { status: "error"; message: string };

const initialState: FundamentalsState = { status: "loading" };
const defaultMetric: FundamentalMetricKey = "revenue";
const metricKeys: FundamentalMetricKey[] = [
  "revenue",
  "operating_income",
  "net_income",
  "diluted_eps",
  "cash",
  "debt",
  "operating_margin",
  "net_margin",
];
const metricLabels: Record<FundamentalMetricKey, string> = {
  revenue: "Revenue",
  operating_income: "Operating income",
  net_income: "Net income",
  diluted_eps: "Diluted EPS",
  cash: "Cash",
  debt: "Debt",
  operating_margin: "Operating margin",
  net_margin: "Net margin",
};
const summaryKeys: FundamentalMetricKey[] = [
  "revenue",
  "net_income",
  "cash",
  "debt",
];

function StatusBadge({ children }: { children: React.ReactNode }) {
  return (
    <span className="border border-warning/50 px-1.5 py-0.5 font-mono text-[8px] font-semibold uppercase tracking-wider text-warning">
      {children}
    </span>
  );
}

function FactBadges({ fact }: { fact: FundamentalFact }) {
  if (!fact.is_derived && !fact.is_fallback && !fact.is_restated) {
    return <span className="text-secondary">Direct fact</span>;
  }

  return (
    <div className="flex flex-wrap gap-1.5">
      {fact.is_derived ? <StatusBadge>Derived</StatusBadge> : null}
      {fact.is_fallback ? <StatusBadge>Fallback tag</StatusBadge> : null}
      {fact.is_restated ? <StatusBadge>Restated</StatusBadge> : null}
    </div>
  );
}

function FinancialsLoading() {
  return (
    <section
      className="border border-border bg-panel"
      aria-busy="true"
      aria-label="Loading company financials"
    >
      <div className="border-b border-border p-5">
        <div className="h-3 w-24 animate-pulse bg-border" />
        <div className="mt-3 h-6 w-48 animate-pulse bg-border" />
      </div>
      <div className="grid gap-px bg-border sm:grid-cols-2 xl:grid-cols-4">
        {Array.from({ length: 4 }, (_, index) => (
          <div key={index} className="h-24 animate-pulse bg-panel p-4">
            <div className="h-3 w-20 bg-border" />
            <div className="mt-4 h-5 w-28 bg-border" />
          </div>
        ))}
      </div>
      <div className="m-5 h-56 animate-pulse border border-border bg-sidebar" />
    </section>
  );
}

function FinancialsError({
  message,
  onRetry,
}: {
  message: string;
  onRetry: () => void;
}) {
  return (
    <section className="border border-warning/50 bg-panel p-6" role="alert">
      <p className="font-mono text-[10px] uppercase tracking-[0.18em] text-warning">
        Financials unavailable
      </p>
      <h3 className="mt-2 text-lg font-semibold text-foreground">
        SEC Company Facts could not be loaded
      </h3>
      <p className="mt-2 max-w-2xl text-sm leading-6 text-secondary">{message}</p>
      <button
        type="button"
        onClick={onRetry}
        className="mt-4 border border-positive px-4 py-2 font-mono text-[10px] font-semibold uppercase tracking-wider text-positive outline-none hover:bg-positive hover:text-[#07120E] focus-visible:ring-2 focus-visible:ring-positive"
      >
        Retry financials
      </button>
    </section>
  );
}

function SummaryCards({
  series,
}: {
  series: FundamentalMetricSeries[];
}) {
  const byKey = new Map(series.map((item) => [item.metric_key, item]));
  return (
    <div
      className="grid gap-px border-b border-border bg-border sm:grid-cols-2 xl:grid-cols-4"
      aria-label="Latest financial values"
    >
      {summaryKeys.map((metricKey) => {
        const selectedSeries = byKey.get(metricKey);
        const latest = selectedSeries?.facts.at(-1);
        return (
          <div key={metricKey} className="bg-panel p-4">
            <p className="font-mono text-[9px] uppercase tracking-[0.16em] text-secondary">
              {metricLabels[metricKey]}
            </p>
            <p className="financial-figure mt-2 font-mono text-lg font-semibold text-foreground">
              {latest
                ? formatFundamentalValue(latest.value, latest.unit)
                : "Unavailable"}
            </p>
            <p className="mt-1 font-mono text-[9px] text-secondary">
              {latest
                ? formatFiscalPeriod(latest.fiscal_year, latest.fiscal_period)
                : "No qualifying SEC fact"}
            </p>
          </div>
        );
      })}
    </div>
  );
}

function FinancialHistory({ series }: { series: FundamentalMetricSeries }) {
  return (
    <div className="overflow-x-auto border-t border-border">
      <table className="w-full border-collapse text-left">
        <thead>
          <tr className="border-b border-border bg-sidebar">
            {["Fiscal period", "Period end", "Value", "Form / filed", "Quality", "Source"].map(
              (heading) => (
                <th
                  key={heading}
                  scope="col"
                  className="whitespace-nowrap px-4 py-3 font-mono text-[9px] font-semibold uppercase tracking-[0.16em] text-secondary"
                >
                  {heading}
                </th>
              ),
            )}
          </tr>
        </thead>
        <tbody>
          {[...series.facts].reverse().map((fact) => (
            <tr
              key={`${fact.period_end}-${fact.accession_number}`}
              className="border-b border-border last:border-0"
            >
              <td className="whitespace-nowrap px-4 py-4 font-mono text-xs font-semibold text-foreground">
                {formatFiscalPeriod(fact.fiscal_year, fact.fiscal_period)}
              </td>
              <td className="whitespace-nowrap px-4 py-4 font-mono text-xs text-secondary">
                {formatSecDate(fact.period_end)}
              </td>
              <td className="financial-figure whitespace-nowrap px-4 py-4 font-mono text-xs font-semibold text-foreground">
                {formatFundamentalValue(fact.value, fact.unit)}
              </td>
              <td className="whitespace-nowrap px-4 py-4 font-mono text-[10px] text-secondary">
                <span className="block text-foreground">{fact.form}</span>
                <span className="mt-1 block">{formatSecDate(fact.filed_date)}</span>
              </td>
              <td className="min-w-36 px-4 py-4 font-mono text-[9px]">
                <FactBadges fact={fact} />
              </td>
              <td className="min-w-48 px-4 py-4">
                <a
                  href={fact.source_filing_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="font-mono text-[9px] font-semibold uppercase tracking-wider text-positive underline decoration-positive/40 underline-offset-4 outline-none hover:decoration-positive focus-visible:ring-2 focus-visible:ring-positive"
                >
                  Supporting filing ↗
                  <span className="sr-only"> (opens SEC.gov in a new tab)</span>
                </a>
                <p className="mt-2 max-w-56 break-words font-mono text-[8px] text-secondary">
                  {`${fact.taxonomy}:${fact.source_tag}`}
                </p>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function FinancialsContent({ data }: { data: CompanyFundamentalsResponse }) {
  const [period, setPeriod] = useState<FundamentalPeriod>("annual");
  const [metric, setMetric] = useState<FundamentalMetricKey>(defaultMetric);
  const series = period === "annual" ? data.annual : data.quarterly;
  const selectedSeries = useMemo(
    () => series.find((item) => item.metric_key === metric),
    [metric, series],
  );
  const relevantWarnings = data.warnings.filter(
    (warning) => warning.metric_key === null || warning.metric_key === metric,
  );
  const unavailable = data.unavailable_metrics.find(
    (item) => item.metric_key === metric && item.period === period,
  );

  if (!selectedSeries) {
    return (
      <section className="border border-warning/50 bg-panel p-6" role="alert">
        The API response did not include the selected metric contract.
      </section>
    );
  }

  return (
    <section className="border border-border bg-panel" aria-labelledby="financials-heading">
      <div className="flex flex-col gap-4 border-b border-border p-5 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <p className="font-mono text-[10px] uppercase tracking-[0.18em] text-positive">
            SEC Company Facts
          </p>
          <h3 id="financials-heading" className="mt-2 text-lg font-semibold text-foreground">
            Financial performance
          </h3>
          <p className="mt-2 max-w-2xl text-xs leading-5 text-secondary">
            Standardized XBRL facts only. Gaps are retained when the SEC data does not meet the period, unit, or provenance rules.
          </p>
        </div>
        <div
          className="flex w-fit border border-border"
          role="group"
          aria-label="Financial reporting period"
        >
          {(["annual", "quarterly"] as FundamentalPeriod[]).map((option) => (
            <button
              key={option}
              type="button"
              aria-pressed={period === option}
              onClick={() => setPeriod(option)}
              className={`border-r border-border px-3 py-2 font-mono text-[10px] font-semibold uppercase outline-none last:border-0 focus-visible:z-10 focus-visible:ring-2 focus-visible:ring-positive ${
                period === option
                  ? "bg-positive text-[#07120E]"
                  : "text-secondary hover:bg-white/[0.04] hover:text-foreground"
              }`}
            >
              {option}
            </button>
          ))}
        </div>
      </div>

      <SummaryCards series={series} />

      <div className="border-b border-border p-4 sm:p-5">
        <p className="font-mono text-[9px] uppercase tracking-[0.16em] text-secondary">
          Select metric
        </p>
        <div className="mt-3 grid grid-cols-2 gap-2 sm:grid-cols-4 xl:grid-cols-8" role="group" aria-label="Financial metric">
          {metricKeys.map((metricKey) => (
            <button
              key={metricKey}
              type="button"
              aria-pressed={metric === metricKey}
              onClick={() => setMetric(metricKey)}
              className={`min-h-11 border px-2 py-2 font-mono text-[9px] font-semibold uppercase leading-4 outline-none focus-visible:ring-2 focus-visible:ring-positive ${
                metric === metricKey
                  ? "border-positive bg-positive/10 text-positive"
                  : "border-border text-secondary hover:border-secondary hover:text-foreground"
              }`}
            >
              {metricLabels[metricKey]}
            </button>
          ))}
        </div>
      </div>

      <div className="flex flex-col gap-1 border-b border-border px-5 py-4 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className="font-mono text-[9px] uppercase tracking-[0.16em] text-secondary">
            {`${period} trend`}
          </p>
          <h4 className="mt-1 text-base font-semibold text-foreground">{selectedSeries.label}</h4>
        </div>
        <p className="font-mono text-[9px] text-secondary">
          {`${selectedSeries.facts.length} qualifying period${selectedSeries.facts.length === 1 ? "" : "s"}`}
        </p>
      </div>

      {selectedSeries.facts.length > 0 ? (
        <>
          <FinancialTrendChart series={selectedSeries} />
          <FinancialHistory series={selectedSeries} />
        </>
      ) : (
        <div className="border-b border-border p-6" role="status">
          <p className="font-mono text-[10px] uppercase tracking-wider text-warning">
            Metric unavailable
          </p>
          <p className="mt-2 max-w-2xl text-sm leading-6 text-secondary">
            {unavailable?.reason ?? "No qualifying SEC facts were returned for this view."}
          </p>
        </div>
      )}

      {relevantWarnings.length > 0 ? (
        <div className="border-t border-warning/30 bg-warning/[0.04] p-5" role="status">
          <p className="font-mono text-[9px] font-semibold uppercase tracking-[0.16em] text-warning">
            Data quality notes
          </p>
          <ul className="mt-2 space-y-1 text-xs leading-5 text-secondary">
            {relevantWarnings.map((warning) => (
              <li key={`${warning.code}-${warning.message}`}>{`• ${warning.message}`}</li>
            ))}
          </ul>
        </div>
      ) : null}

      <div className="flex flex-col gap-2 border-t border-border p-5 text-[9px] text-secondary sm:flex-row sm:items-center sm:justify-between">
        <p className="font-mono uppercase tracking-wider">
          {`Data retrieved ${formatAsOf(data.data_as_of)} · ${data.provenance.provider}`}
        </p>
        <a
          href={data.provenance.company_facts_url}
          target="_blank"
          rel="noopener noreferrer"
          className="font-mono font-semibold uppercase tracking-wider text-positive underline decoration-positive/40 underline-offset-4 outline-none hover:decoration-positive focus-visible:ring-2 focus-visible:ring-positive"
        >
          Raw Company Facts ↗
          <span className="sr-only"> (opens SEC.gov in a new tab)</span>
        </a>
      </div>
    </section>
  );
}

export function CompanyFinancials({ ticker }: { ticker: string }) {
  const [state, setState] = useState<FundamentalsState>(initialState);
  const [requestVersion, setRequestVersion] = useState(0);

  useEffect(() => {
    const controller = new AbortController();
    getCompanyFundamentals(ticker, controller.signal)
      .then((data) => setState({ status: "success", data }))
      .catch((error: unknown) => {
        if (error instanceof DOMException && error.name === "AbortError") {
          return;
        }
        setState({
          status: "error",
          message:
            error instanceof Error
              ? error.message
              : "An unexpected error occurred while loading company financials.",
        });
      });
    return () => controller.abort();
  }, [requestVersion, ticker]);

  function retry() {
    setState(initialState);
    setRequestVersion((version) => version + 1);
  }

  if (state.status === "loading") {
    return <FinancialsLoading />;
  }
  if (state.status === "error") {
    return <FinancialsError message={state.message} onRetry={retry} />;
  }
  return <FinancialsContent data={state.data} />;
}
