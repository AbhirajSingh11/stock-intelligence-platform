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
