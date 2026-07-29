import type { DashboardOverviewResponse } from "@/types/dashboard";

const defaultApiBaseUrl = "http://127.0.0.1:8000";

export const apiBaseUrl = (
  process.env.NEXT_PUBLIC_API_BASE_URL ?? defaultApiBaseUrl
).replace(/\/+$/, "");

export class ApiRequestError extends Error {
  constructor(
    message: string,
    readonly status?: number,
  ) {
    super(message);
    this.name = "ApiRequestError";
  }
}

async function requestJson<T>(path: string, signal?: AbortSignal): Promise<T> {
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
    throw new ApiRequestError(
      `FastAPI returned ${response.status} while loading the dashboard.`,
      response.status,
    );
  }

  return (await response.json()) as T;
}

export function getDashboardOverview(
  signal?: AbortSignal,
): Promise<DashboardOverviewResponse> {
  return requestJson<DashboardOverviewResponse>(
    "/api/v1/dashboard/overview",
    signal,
  );
}

