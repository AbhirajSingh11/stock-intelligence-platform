import type { DashboardOverviewResponse } from "@/types/dashboard";
import type { ApiErrorResponse } from "@/types/api";
import type {
  CompanyFilingsResponse,
  CompanyFundamentalsResponse,
  CompanyProfileResponse,
  CompanySearchResponse,
} from "@/types/company";
import type {
  WatchlistDeleteResponse,
  WatchlistEntry,
  WatchlistResponse,
} from "@/types/watchlist";
import type {
  PortfolioDeleteResponse,
  PortfolioOverviewResponse,
  PortfolioPriceMark,
  PortfolioPriceMarkInput,
  PortfolioTransaction,
  PortfolioTransactionInput,
  PortfolioTransactionsResponse,
  PortfolioTransactionUpdate,
} from "@/types/portfolio";

const defaultApiBaseUrl = "http://127.0.0.1:8000";

export const apiBaseUrl = (
  process.env.NEXT_PUBLIC_API_BASE_URL ?? defaultApiBaseUrl
).replace(/\/+$/, "");

export class ApiRequestError extends Error {
  constructor(
    message: string,
    readonly status?: number,
    readonly code?: string,
  ) {
    super(message);
    this.name = "ApiRequestError";
  }
}

async function requestJson<T>(
  path: string,
  resourceName: string,
  options: {
    method?: "GET" | "POST" | "PATCH" | "PUT" | "DELETE";
    body?: object;
    signal?: AbortSignal;
  } = {},
): Promise<T> {
  let response: Response;

  try {
    response = await fetch(`${apiBaseUrl}${path}`, {
      method: options.method ?? "GET",
      headers: {
        Accept: "application/json",
        ...(options.body ? { "Content-Type": "application/json" } : {}),
      },
      body: options.body ? JSON.stringify(options.body) : undefined,
      cache: "no-store",
      signal: options.signal,
    });
  } catch (error) {
    if (error instanceof DOMException && error.name === "AbortError") {
      throw error;
    }
    throw new ApiRequestError(
      `Unable to reach FastAPI at ${apiBaseUrl}. Confirm the backend is running.`,
    );
  }

  if (!response.ok) {
    let payload: Partial<ApiErrorResponse> | undefined;
    try {
      payload = (await response.json()) as Partial<ApiErrorResponse>;
    } catch {
      payload = undefined;
    }

    throw new ApiRequestError(
      payload?.error?.message ??
        `FastAPI returned ${response.status} while loading ${resourceName}.`,
      response.status,
      payload?.error?.code,
    );
  }

  return (await response.json()) as T;
}

export function getDashboardOverview(
  signal?: AbortSignal,
): Promise<DashboardOverviewResponse> {
  return requestJson<DashboardOverviewResponse>(
    "/api/v1/dashboard/overview",
    "the dashboard",
    { signal },
  );
}

export function searchCompanies(
  query: string,
  limit = 8,
  signal?: AbortSignal,
): Promise<CompanySearchResponse> {
  const params = new URLSearchParams({
    query,
    limit: String(limit),
  });
  return requestJson<CompanySearchResponse>(
    `/api/v1/companies/search?${params.toString()}`,
    "company search results",
    { signal },
  );
}

export function getCompanyProfile(
  ticker: string,
  signal?: AbortSignal,
): Promise<CompanyProfileResponse> {
  return requestJson<CompanyProfileResponse>(
    `/api/v1/companies/${encodeURIComponent(ticker)}`,
    `${ticker} company data`,
    { signal },
  );
}

export function getCompanyFilings(
  ticker: string,
  signal?: AbortSignal,
): Promise<CompanyFilingsResponse> {
  const params = new URLSearchParams({
    forms: "10-K,10-Q,8-K",
    limit: "20",
  });
  return requestJson<CompanyFilingsResponse>(
    `/api/v1/companies/${encodeURIComponent(ticker)}/filings?${params.toString()}`,
    `${ticker} filing history`,
    { signal },
  );
}

export function getCompanyFundamentals(
  ticker: string,
  signal?: AbortSignal,
): Promise<CompanyFundamentalsResponse> {
  return requestJson<CompanyFundamentalsResponse>(
    `/api/v1/companies/${encodeURIComponent(ticker)}/fundamentals`,
    `${ticker} fundamentals`,
    { signal },
  );
}

export function getWatchlist(signal?: AbortSignal): Promise<WatchlistResponse> {
  return requestJson<WatchlistResponse>("/api/v1/watchlist", "the watchlist", {
    signal,
  });
}

export function addWatchlistEntry(
  ticker: string,
  signal?: AbortSignal,
): Promise<WatchlistEntry> {
  return requestJson<WatchlistEntry>("/api/v1/watchlist", "the watchlist", {
    method: "POST",
    body: { ticker },
    signal,
  });
}

export function deleteWatchlistEntry(
  ticker: string,
  signal?: AbortSignal,
): Promise<WatchlistDeleteResponse> {
  return requestJson<WatchlistDeleteResponse>(
    `/api/v1/watchlist/${encodeURIComponent(ticker)}`,
    "the watchlist",
    { method: "DELETE", signal },
  );
}

export function getPortfolioOverview(
  signal?: AbortSignal,
): Promise<PortfolioOverviewResponse> {
  return requestJson<PortfolioOverviewResponse>(
    "/api/v1/portfolio/overview",
    "the portfolio overview",
    { signal },
  );
}

export function getPortfolioTransactions(
  ticker?: string,
  signal?: AbortSignal,
): Promise<PortfolioTransactionsResponse> {
  const query = ticker
    ? `?${new URLSearchParams({ ticker }).toString()}`
    : "";
  return requestJson<PortfolioTransactionsResponse>(
    `/api/v1/portfolio/transactions${query}`,
    "portfolio transactions",
    { signal },
  );
}

export function createPortfolioTransaction(
  input: PortfolioTransactionInput,
): Promise<PortfolioTransaction> {
  return requestJson<PortfolioTransaction>(
    "/api/v1/portfolio/transactions",
    "the portfolio transaction",
    { method: "POST", body: input },
  );
}

export function updatePortfolioTransaction(
  transactionId: number,
  input: PortfolioTransactionUpdate,
): Promise<PortfolioTransaction> {
  return requestJson<PortfolioTransaction>(
    `/api/v1/portfolio/transactions/${transactionId}`,
    "the portfolio transaction",
    { method: "PATCH", body: input },
  );
}

export function deletePortfolioTransaction(
  transactionId: number,
): Promise<PortfolioDeleteResponse> {
  return requestJson<PortfolioDeleteResponse>(
    `/api/v1/portfolio/transactions/${transactionId}`,
    "the portfolio transaction",
    { method: "DELETE" },
  );
}

export function setPortfolioPriceMark(
  ticker: string,
  input: PortfolioPriceMarkInput,
): Promise<PortfolioPriceMark> {
  return requestJson<PortfolioPriceMark>(
    `/api/v1/portfolio/marks/${encodeURIComponent(ticker)}`,
    "the manual portfolio price",
    { method: "PUT", body: input },
  );
}
