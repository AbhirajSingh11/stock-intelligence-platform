export interface CompanySearchResult {
  ticker: string;
  company_name: string;
  cik: string;
}

export interface CompanySearchResponse {
  query: string;
  results: CompanySearchResult[];
}

export interface CompanyAddress {
  street1: string | null;
  street2: string | null;
  city: string | null;
  state_or_country: string | null;
  state_or_country_description: string | null;
  postal_code: string | null;
}

export interface FormerCompanyName {
  name: string;
  from_date: string | null;
  to_date: string | null;
}

export interface CompanyProfileResponse {
  ticker: string;
  company_name: string;
  cik: string;
  sic_code: string | null;
  sic_description: string | null;
  exchanges: string[];
  fiscal_year_end: string | null;
  state_of_incorporation: string | null;
  business_address: CompanyAddress | null;
  mailing_address: CompanyAddress | null;
  former_names: FormerCompanyName[];
  sec_company_url: string;
}

export interface FilingRecord {
  accession_number: string;
  form: string;
  filing_date: string;
  report_date: string | null;
  acceptance_timestamp: string | null;
  primary_document: string;
  filing_detail_url: string;
  primary_document_url: string;
  description: string | null;
  items: string | null;
}

export interface CompanyFilingsResponse {
  ticker: string;
  cik: string;
  forms: string[];
  filings: FilingRecord[];
}

export type FundamentalMetricKey =
  | "revenue"
  | "operating_income"
  | "net_income"
  | "diluted_eps"
  | "cash"
  | "debt"
  | "operating_margin"
  | "net_margin";

export type FundamentalPeriod = "annual" | "quarterly";

export interface FundamentalComponentSource {
  metric_key: string;
  value: number;
  unit: string;
  taxonomy: string;
  source_tag: string;
  accession_number: string;
  source_filing_url: string;
}

export interface FundamentalFact {
  metric_key: FundamentalMetricKey;
  value: number;
  unit: string;
  period_start: string | null;
  period_end: string;
  fiscal_year: number;
  fiscal_period: string;
  form: string;
  filed_date: string;
  accession_number: string;
  frame: string | null;
  taxonomy: string;
  source_tag: string;
  is_fallback: boolean;
  is_derived: boolean;
  is_restated: boolean;
  source_filing_url: string;
  component_sources: FundamentalComponentSource[];
}

export interface FundamentalMetricSeries {
  metric_key: FundamentalMetricKey;
  label: string;
  unit: string;
  period: FundamentalPeriod;
  facts: FundamentalFact[];
}

export interface LatestFundamentalValue {
  metric_key: FundamentalMetricKey;
  label: string;
  fact: FundamentalFact;
}

export interface DataQualityWarning {
  code: string;
  message: string;
  metric_key: FundamentalMetricKey | null;
}

export interface UnavailableMetric {
  metric_key: FundamentalMetricKey;
  label: string;
  period: FundamentalPeriod;
  reason: string;
}

export interface CompanyFundamentalsResponse {
  company: {
    ticker: string;
    company_name: string;
    cik: string;
  };
  data_as_of: string;
  annual: FundamentalMetricSeries[];
  quarterly: FundamentalMetricSeries[];
  latest_values: LatestFundamentalValue[];
  warnings: DataQualityWarning[];
  unavailable_metrics: UnavailableMetric[];
  provenance: {
    provider: "SEC EDGAR Company Facts";
    company_facts_url: string;
  };
}
