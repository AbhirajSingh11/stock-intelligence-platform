import type { ReactNode } from "react";

export type IconName =
  | "dashboard"
  | "watchlist"
  | "portfolio"
  | "filings"
  | "thesis"
  | "search"
  | "trend";

interface IconProps {
  name: IconName;
  className?: string;
}

const paths: Record<IconName, ReactNode> = {
  dashboard: (
    <>
      <rect x="3" y="3" width="7" height="7" rx="1" />
      <rect x="14" y="3" width="7" height="7" rx="1" />
      <rect x="3" y="14" width="7" height="7" rx="1" />
      <rect x="14" y="14" width="7" height="7" rx="1" />
    </>
  ),
  watchlist: (
    <>
      <path d="M2.5 12s3.5-6 9.5-6 9.5 6 9.5 6-3.5 6-9.5 6-9.5-6-9.5-6Z" />
      <circle cx="12" cy="12" r="2.5" />
    </>
  ),
  portfolio: (
    <>
      <path d="M5 8V6.5A2.5 2.5 0 0 1 7.5 4h9A2.5 2.5 0 0 1 19 6.5V8" />
      <rect x="3" y="8" width="18" height="12" rx="2" />
      <path d="M3 13h18M10 13v2h4v-2" />
    </>
  ),
  filings: (
    <>
      <path d="M6 2.5h8l4 4V21H6z" />
      <path d="M14 2.5V7h4M9 12h6M9 16h6" />
    </>
  ),
  thesis: (
    <>
      <path d="M4 4.5h11a3 3 0 0 1 3 3v12H7a3 3 0 0 1-3-3z" />
      <path d="M7 4.5v15M10 9h5M10 13h5" />
    </>
  ),
  search: (
    <>
      <circle cx="11" cy="11" r="6.5" />
      <path d="m16 16 4.5 4.5" />
    </>
  ),
  trend: <path d="m3 17 6-6 4 4 8-9M15 6h6v6" />,
};

export function Icon({ name, className = "size-5" }: IconProps) {
  return (
    <svg
      aria-hidden="true"
      className={className}
      fill="none"
      viewBox="0 0 24 24"
      stroke="currentColor"
      strokeWidth="1.7"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      {paths[name]}
    </svg>
  );
}

