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

