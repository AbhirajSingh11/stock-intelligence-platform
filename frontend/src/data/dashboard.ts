import type {
  PerformancePeriod,
  PerformanceSeries,
  PortfolioSummary,
  ThesisSignal,
  WatchlistItem,
} from "@/types/dashboard";

export const portfolioSummary: PortfolioSummary = {
  totalValue: 24860.42,
  totalGain: 2814.16,
  totalReturnPercent: 12.8,
  todayChange: 184.32,
};

export const performancePeriods: PerformancePeriod[] = [
  "1M",
  "3M",
  "6M",
  "1Y",
  "ALL",
];

export const performanceSeries: Record<
  PerformancePeriod,
  PerformanceSeries
> = {
  "1M": {
    period: "1M",
    rangeLabel: "Jun 29 – Jul 28, 2026",
    changePercent: 3.4,
    points: [
      { date: "2026-06-29", label: "Jun 29", value: 24042.18 },
      { date: "2026-07-02", label: "Jul 02", value: 24186.44 },
      { date: "2026-07-06", label: "Jul 06", value: 24098.72 },
      { date: "2026-07-09", label: "Jul 09", value: 24326.51 },
      { date: "2026-07-13", label: "Jul 13", value: 24472.36 },
      { date: "2026-07-16", label: "Jul 16", value: 24388.19 },
      { date: "2026-07-20", label: "Jul 20", value: 24614.83 },
      { date: "2026-07-23", label: "Jul 23", value: 24728.64 },
      { date: "2026-07-28", label: "Jul 28", value: 24860.42 },
    ],
  },
  "3M": {
    period: "3M",
    rangeLabel: "Apr 28 – Jul 28, 2026",
    changePercent: 6.8,
    points: [
      { date: "2026-04-28", label: "Apr 28", value: 23277.55 },
      { date: "2026-05-08", label: "May 08", value: 23506.11 },
      { date: "2026-05-18", label: "May 18", value: 23418.62 },
      { date: "2026-05-28", label: "May 28", value: 23792.48 },
      { date: "2026-06-08", label: "Jun 08", value: 23956.73 },
      { date: "2026-06-18", label: "Jun 18", value: 23884.25 },
      { date: "2026-06-28", label: "Jun 28", value: 24042.18 },
      { date: "2026-07-08", label: "Jul 08", value: 24282.96 },
      { date: "2026-07-18", label: "Jul 18", value: 24552.14 },
      { date: "2026-07-28", label: "Jul 28", value: 24860.42 },
    ],
  },
  "6M": {
    period: "6M",
    rangeLabel: "Jan 28 – Jul 28, 2026",
    changePercent: 9.7,
    points: [
      { date: "2026-01-28", label: "Jan 28", value: 22662.19 },
      { date: "2026-02-14", label: "Feb 14", value: 22846.38 },
      { date: "2026-03-01", label: "Mar 01", value: 22584.74 },
      { date: "2026-03-18", label: "Mar 18", value: 23096.21 },
      { date: "2026-04-04", label: "Apr 04", value: 22942.87 },
      { date: "2026-04-21", label: "Apr 21", value: 23214.61 },
      { date: "2026-05-08", label: "May 08", value: 23506.11 },
      { date: "2026-05-25", label: "May 25", value: 23698.45 },
      { date: "2026-06-11", label: "Jun 11", value: 23914.32 },
      { date: "2026-06-28", label: "Jun 28", value: 24042.18 },
      { date: "2026-07-11", label: "Jul 11", value: 24362.28 },
      { date: "2026-07-28", label: "Jul 28", value: 24860.42 },
    ],
  },
  "1Y": {
    period: "1Y",
    rangeLabel: "Jul 28, 2025 – Jul 28, 2026",
    changePercent: 12.8,
    points: [
      { date: "2025-07-28", label: "Jul '25", value: 22046.26 },
      { date: "2025-08-28", label: "Aug '25", value: 22284.44 },
      { date: "2025-09-28", label: "Sep '25", value: 21968.17 },
      { date: "2025-10-28", label: "Oct '25", value: 22492.63 },
      { date: "2025-11-28", label: "Nov '25", value: 22618.37 },
      { date: "2025-12-28", label: "Dec '25", value: 22476.82 },
      { date: "2026-01-28", label: "Jan '26", value: 22662.19 },
      { date: "2026-02-28", label: "Feb '26", value: 22794.56 },
      { date: "2026-03-28", label: "Mar '26", value: 23118.72 },
      { date: "2026-04-28", label: "Apr '26", value: 23277.55 },
      { date: "2026-05-28", label: "May '26", value: 23792.48 },
      { date: "2026-06-28", label: "Jun '26", value: 24042.18 },
      { date: "2026-07-28", label: "Jul '26", value: 24860.42 },
    ],
  },
  ALL: {
    period: "ALL",
    rangeLabel: "Jan 2023 – Jul 2026",
    changePercent: 48.6,
    points: [
      { date: "2023-01-03", label: "Jan '23", value: 16734.82 },
      { date: "2023-05-01", label: "May '23", value: 17462.44 },
      { date: "2023-09-01", label: "Sep '23", value: 18296.73 },
      { date: "2024-01-02", label: "Jan '24", value: 19148.55 },
      { date: "2024-05-01", label: "May '24", value: 19884.16 },
      { date: "2024-09-03", label: "Sep '24", value: 20496.38 },
      { date: "2025-01-02", label: "Jan '25", value: 21418.92 },
      { date: "2025-05-01", label: "May '25", value: 21876.44 },
      { date: "2025-09-02", label: "Sep '25", value: 21968.17 },
      { date: "2026-01-02", label: "Jan '26", value: 22554.83 },
      { date: "2026-05-01", label: "May '26", value: 23462.17 },
      { date: "2026-07-28", label: "Jul '26", value: 24860.42 },
    ],
  },
};

export const thesisSignals: ThesisSignal[] = [
  {
    ticker: "MSFT",
    company: "Microsoft",
    state: "Strengthening",
    tone: "positive",
    lastReviewed: "Jul 22, 2026",
  },
  {
    ticker: "UBER",
    company: "Uber",
    state: "Review required",
    tone: "warning",
    lastReviewed: "Jul 12, 2026",
  },
  {
    ticker: "GOOG",
    company: "Alphabet",
    state: "Stable",
    tone: "neutral",
    lastReviewed: "Jul 18, 2026",
  },
];

export const watchlist: WatchlistItem[] = [
  {
    ticker: "MSFT",
    company: "Microsoft Corporation",
    price: 512.34,
    dailyChange: 7.18,
    dailyChangePercent: 1.42,
    positionValue: 10560.4,
    thesisState: "Strengthening",
    thesisTone: "positive",
  },
  {
    ticker: "UBER",
    company: "Uber Technologies",
    price: 92.18,
    dailyChange: -0.69,
    dailyChangePercent: -0.74,
    positionValue: 5527.25,
    thesisState: "Review required",
    thesisTone: "warning",
  },
  {
    ticker: "GOOG",
    company: "Alphabet Class C",
    price: 203.44,
    dailyChange: 1.37,
    dailyChangePercent: 0.68,
    positionValue: 8772.77,
    thesisState: "Stable",
    thesisTone: "neutral",
  },
];

