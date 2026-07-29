import type { DashboardOverviewResponse } from "@/types/dashboard";
import type {
  CompanyFilingsResponse,
  CompanyProfileResponse,
  CompanySearchResponse,
} from "@/types/company";

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

interface ApiErrorPayload {
  error?: {
    code?: string;
    message?: string;
  };
}

async function requestJson<T>(
  path: string,
  resourceName: string,
  signal?: AbortSignal,
): Promise<T> {
  let response: Response;

  try {
    response = await fetch(`${apiBaseUrl}${path}`, {
      method: "GET",
      headers: { Accept: "application/json" },
      cache: "no-store",
      signal,
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
    let payload: ApiErrorPayload | undefined;
    try {
      payload = (await response.json()) as ApiErrorPayload;
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
    signal,
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
    signal,
  );
}

export function getCompanyProfile(
  ticker: string,
  signal?: AbortSignal,
): Promise<CompanyProfileResponse> {
  return requestJson<CompanyProfileResponse>(
    `/api/v1/companies/${encodeURIComponent(ticker)}`,
    `${ticker} company data`,
    signal,
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
    signal,
  );
}
