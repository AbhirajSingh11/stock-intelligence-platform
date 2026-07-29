"use client";

import { useEffect, useState } from "react";

import { CompanyError, CompanyLoading } from "./company-states";
import { getCompanyFilings, getCompanyProfile } from "@/lib/api/client";
import { formatFiscalYearEnd, formatSecDate } from "@/lib/formatters";
import type {
  CompanyAddress,
  CompanyFilingsResponse,
  CompanyProfileResponse,
  FilingRecord,
} from "@/types/company";

interface CompanyData {
  profile: CompanyProfileResponse;
  filings: CompanyFilingsResponse;
}

type CompanyState =
  | { status: "loading" }
  | { status: "success"; data: CompanyData }
  | { status: "error"; message: string };

const initialCompanyState: CompanyState = { status: "loading" };

function ExternalSecLink({
  href,
  children,
}: {
  href: string;
  children: React.ReactNode;
}) {
  return (
    <a
      href={href}
      target="_blank"
      rel="noopener noreferrer"
      className="font-mono text-[10px] font-semibold uppercase tracking-wider text-positive underline decoration-positive/40 underline-offset-4 outline-none hover:decoration-positive focus-visible:ring-2 focus-visible:ring-positive"
    >
      {children}
      <span className="sr-only"> (opens SEC.gov in a new tab)</span>
    </a>
  );
}

function MetadataCell({
  label,
  value,
}: {
  label: string;
  value: string;
}) {
  return (
    <div className="border-b border-r border-border bg-panel p-4">
      <p className="font-mono text-[9px] uppercase tracking-[0.16em] text-secondary">
        {label}
      </p>
      <p className="financial-figure mt-2 text-sm font-medium text-foreground">
        {value}
      </p>
    </div>
  );
}

function AddressPanel({
  title,
  address,
}: {
  title: string;
  address: CompanyAddress | null;
}) {
  const stateAndPostalCode = address
    ? [address.state_or_country, address.postal_code].filter(Boolean).join(" ")
    : "";
  const region = address
    ? [address.city, stateAndPostalCode].filter(Boolean).join(", ")
    : "";

  return (
    <section className="border border-border bg-panel p-5">
      <p className="font-mono text-[10px] uppercase tracking-[0.18em] text-secondary">
        {title}
      </p>
      {address ? (
        <address className="mt-3 text-sm not-italic leading-6 text-foreground">
          {address.street1 ? <span className="block">{address.street1}</span> : null}
          {address.street2 ? <span className="block">{address.street2}</span> : null}
          {region ? <span className="block">{region}</span> : null}
          {address.state_or_country_description &&
          address.state_or_country_description !== address.state_or_country ? (
            <span className="block text-secondary">
              {address.state_or_country_description}
            </span>
          ) : null}
        </address>
      ) : (
        <p className="mt-3 text-sm text-secondary">Not reported by the SEC.</p>
      )}
    </section>
  );
}

function FilingRow({ filing }: { filing: FilingRecord }) {
  return (
    <tr className="border-b border-border last:border-0">
      <td className="whitespace-nowrap px-4 py-4 align-top font-mono text-xs font-semibold text-foreground">
        {filing.form}
      </td>
      <td className="whitespace-nowrap px-4 py-4 align-top font-mono text-xs text-foreground">
        {formatSecDate(filing.filing_date)}
      </td>
      <td className="whitespace-nowrap px-4 py-4 align-top font-mono text-xs text-secondary">
        {filing.report_date ? formatSecDate(filing.report_date) : "Not reported"}
      </td>
      <td className="min-w-56 px-4 py-4 align-top">
        <p className="text-xs leading-5 text-foreground">
          {filing.description || filing.primary_document}
        </p>
        {filing.items ? (
          <p className="mt-1 font-mono text-[9px] text-secondary">
            {`Items ${filing.items}`}
          </p>
        ) : null}
      </td>
      <td className="min-w-52 px-4 py-4 align-top">
        <div className="flex flex-col items-start gap-2">
          <ExternalSecLink href={filing.filing_detail_url}>
            Filing details ↗
          </ExternalSecLink>
          <ExternalSecLink href={filing.primary_document_url}>
            Primary document ↗
          </ExternalSecLink>
        </div>
      </td>
    </tr>
  );
}

function CompanyContent({ data }: { data: CompanyData }) {
  const { profile, filings } = data;

  return (
    <div className="space-y-5">
      <section className="border border-border bg-panel p-5 sm:p-6">
        <div className="flex flex-col gap-5 sm:flex-row sm:items-start sm:justify-between">
          <div>
            <p className="font-mono text-[10px] uppercase tracking-[0.18em] text-positive">
              {profile.ticker}
            </p>
            <h2 className="mt-2 text-2xl font-semibold tracking-tight text-foreground sm:text-3xl">
              {profile.company_name}
            </h2>
            <p className="mt-3 font-mono text-xs text-secondary">
              {`CIK ${profile.cik}`}
            </p>
          </div>
          <ExternalSecLink href={profile.sec_company_url}>
            View company on SEC.gov ↗
          </ExternalSecLink>
        </div>
      </section>

      <section
        className="grid border-l border-t border-border sm:grid-cols-2 xl:grid-cols-5"
        aria-label="Company metadata"
      >
        <MetadataCell
          label="SIC"
          value={
            profile.sic_code
              ? `${profile.sic_code}${
                  profile.sic_description
                    ? ` · ${profile.sic_description}`
                    : ""
                }`
              : "Not reported"
          }
        />
        <MetadataCell
          label="Exchange"
          value={profile.exchanges.join(", ") || "Not reported"}
        />
        <MetadataCell
          label="Fiscal year end"
          value={formatFiscalYearEnd(profile.fiscal_year_end)}
        />
        <MetadataCell
          label="Incorporated"
          value={profile.state_of_incorporation || "Not reported"}
        />
        <MetadataCell label="CIK" value={profile.cik} />
      </section>

      <div className="grid gap-4 xl:grid-cols-2">
        <AddressPanel title="Business address" address={profile.business_address} />
        <AddressPanel title="Mailing address" address={profile.mailing_address} />
      </div>

      {profile.former_names.length > 0 ? (
        <section className="border border-border bg-panel p-5">
          <p className="font-mono text-[10px] uppercase tracking-[0.18em] text-secondary">
            Former names
          </p>
          <ul className="mt-3 space-y-2">
            {profile.former_names.map((formerName) => (
              <li
                key={`${formerName.name}-${formerName.from_date}`}
                className="flex flex-col gap-1 text-sm sm:flex-row sm:items-baseline sm:justify-between"
              >
                <span className="text-foreground">{formerName.name}</span>
                <span className="font-mono text-[10px] text-secondary">
                  {formerName.from_date && formerName.to_date
                    ? `${formatSecDate(formerName.from_date)} – ${formatSecDate(
                        formerName.to_date,
                      )}`
                    : "Dates not reported"}
                </span>
              </li>
            ))}
          </ul>
        </section>
      ) : null}

      <section className="border border-border bg-panel">
        <div className="flex flex-col gap-2 border-b border-border p-5 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <p className="font-mono text-[10px] uppercase tracking-[0.18em] text-secondary">
              SEC submissions
            </p>
            <h3 className="mt-2 text-lg font-semibold text-foreground">
              Recent material filings
            </h3>
          </div>
          <p className="font-mono text-[9px] uppercase tracking-wider text-secondary">
            {`Forms ${filings.forms.join(" · ")}`}
          </p>
        </div>

        {filings.filings.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full border-collapse text-left">
              <thead>
                <tr className="border-b border-border bg-sidebar">
                  {["Form", "Filed", "Report date", "Description", "SEC links"].map(
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
                {filings.filings.map((filing) => (
                  <FilingRow
                    key={filing.accession_number}
                    filing={filing}
                  />
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="p-6 text-sm text-secondary" role="status">
            No recent 10-K, 10-Q, or 8-K filings were returned by SEC EDGAR.
          </div>
        )}
      </section>

      <p className="text-right font-mono text-[9px] uppercase tracking-wider text-secondary">
        Company metadata and filing history sourced from SEC EDGAR
      </p>
    </div>
  );
}

export function CompanyResearch({ ticker }: { ticker: string }) {
  const [state, setState] = useState<CompanyState>(initialCompanyState);
  const [requestVersion, setRequestVersion] = useState(0);

  useEffect(() => {
    const controller = new AbortController();

    Promise.all([
      getCompanyProfile(ticker, controller.signal),
      getCompanyFilings(ticker, controller.signal),
    ])
      .then(([profile, filings]) => {
        setState({ status: "success", data: { profile, filings } });
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
              : "An unexpected error occurred while loading SEC company data.",
        });
      });

    return () => controller.abort();
  }, [requestVersion, ticker]);

  function retry() {
    setState({ status: "loading" });
    setRequestVersion((version) => version + 1);
  }

  if (state.status === "loading") {
    return <CompanyLoading ticker={ticker} />;
  }

  if (state.status === "error") {
    return (
      <CompanyError ticker={ticker} message={state.message} onRetry={retry} />
    );
  }

  return <CompanyContent data={state.data} />;
}
