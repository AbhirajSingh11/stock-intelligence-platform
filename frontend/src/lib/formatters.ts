import type { PerformancePeriod } from "@/types/dashboard";

const reviewedDateFormatter = new Intl.DateTimeFormat("en-US", {
  month: "short",
  day: "numeric",
  year: "numeric",
  timeZone: "UTC",
});

const rangeDateFormatter = new Intl.DateTimeFormat("en-US", {
  month: "short",
  day: "numeric",
  year: "numeric",
  timeZone: "UTC",
});

const shortChartDateFormatter = new Intl.DateTimeFormat("en-US", {
  month: "short",
  day: "2-digit",
  timeZone: "UTC",
});

const longChartDateFormatter = new Intl.DateTimeFormat("en-US", {
  month: "short",
  year: "2-digit",
  timeZone: "UTC",
});

const asOfFormatter = new Intl.DateTimeFormat("en-US", {
  month: "short",
  day: "numeric",
  year: "numeric",
  hour: "numeric",
  minute: "2-digit",
  timeZone: "UTC",
  timeZoneName: "short",
});

const secDateFormatter = new Intl.DateTimeFormat("en-US", {
  month: "short",
  day: "numeric",
  year: "numeric",
  timeZone: "UTC",
});

function parseIsoDate(date: string): Date {
  return new Date(`${date}T00:00:00Z`);
}

export function formatCurrency(value: number, currency: string): string {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency,
    minimumFractionDigits: 2,
  }).format(value);
}

export function formatCompactCurrency(
  value: number,
  currency: string,
): string {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency,
    notation: "compact",
    maximumFractionDigits: 1,
  }).format(value);
}

export function formatReviewedDate(date: string): string {
  return reviewedDateFormatter.format(parseIsoDate(date));
}

export function formatDateRange(startDate: string, endDate: string): string {
  return `${rangeDateFormatter.format(
    parseIsoDate(startDate),
  )} – ${rangeDateFormatter.format(parseIsoDate(endDate))}`;
}

export function formatChartDate(
  date: string,
  period: PerformancePeriod,
): string {
  const formatter =
    period === "1Y" || period === "ALL"
      ? longChartDateFormatter
      : shortChartDateFormatter;
  return formatter.format(parseIsoDate(date));
}

export function formatAsOf(timestamp: string): string {
  return asOfFormatter.format(new Date(timestamp));
}

export function formatSecDate(date: string): string {
  return secDateFormatter.format(parseIsoDate(date));
}

export function formatFiscalYearEnd(value: string | null): string {
  if (!value || !/^\d{4}$/.test(value)) {
    return "Not reported";
  }

  const month = Number(value.slice(0, 2));
  const day = Number(value.slice(2, 4));
  if (month < 1 || month > 12 || day < 1 || day > 31) {
    return value;
  }

  return secDateFormatter.format(
    new Date(Date.UTC(2024, month - 1, day)),
  ).replace(", 2024", "");
}
