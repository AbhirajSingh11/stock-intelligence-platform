import Link from "next/link";

import { Icon, type IconName } from "./icons";

interface NavigationItem {
  label: string;
  icon: IconName;
  selected?: boolean;
}

const navigation: NavigationItem[] = [
  { label: "Dashboard", icon: "dashboard", selected: true },
  { label: "Watchlist", icon: "watchlist" },
  { label: "Portfolio", icon: "portfolio" },
  { label: "Filings", icon: "filings" },
  { label: "Thesis", icon: "thesis" },
];

function Brand() {
  return (
    <div className="flex items-center gap-3">
      <div
        className="flex size-9 shrink-0 items-center justify-center border border-positive/40 bg-positive/10 font-mono text-xs font-bold tracking-wider text-positive"
        aria-hidden="true"
      >
        SI
      </div>
      <div className="min-w-0">
        <p className="truncate text-sm font-semibold tracking-wide text-foreground">
          STOCK INTELLIGENCE
        </p>
        <p className="font-mono text-[9px] uppercase tracking-[0.2em] text-secondary">
          Research terminal
        </p>
      </div>
    </div>
  );
}

function DesktopNavigation() {
  return (
    <nav className="mt-8" aria-label="Primary navigation">
      <ul className="space-y-1">
        {navigation.map((item) => (
          <li key={item.label}>
            {item.selected ? (
              <Link
                href="/"
                aria-current="page"
                className="flex items-center gap-3 border-l-2 border-positive bg-positive/10 px-4 py-2.5 text-sm font-medium text-foreground outline-none focus-visible:ring-2 focus-visible:ring-positive"
              >
                <Icon name={item.icon} className="size-[18px] text-positive" />
                {item.label}
              </Link>
            ) : (
              <span
                className="flex cursor-default items-center gap-3 border-l-2 border-transparent px-4 py-2.5 text-sm text-secondary"
                aria-disabled="true"
              >
                <Icon name={item.icon} className="size-[18px]" />
                {item.label}
              </span>
            )}
          </li>
        ))}
      </ul>
    </nav>
  );
}

function MobileNavigation() {
  return (
    <nav
      className="overflow-x-auto border-t border-border"
      aria-label="Mobile navigation"
    >
      <ul className="flex min-w-max px-3">
        {navigation.map((item) => (
          <li key={item.label}>
            {item.selected ? (
              <Link
                href="/"
                aria-current="page"
                className="flex items-center gap-2 border-b-2 border-positive px-3 py-3 text-xs font-medium text-foreground outline-none focus-visible:ring-2 focus-visible:ring-positive"
              >
                <Icon name={item.icon} className="size-4 text-positive" />
                {item.label}
              </Link>
            ) : (
              <span
                className="flex cursor-default items-center gap-2 border-b-2 border-transparent px-3 py-3 text-xs text-secondary"
                aria-disabled="true"
              >
                <Icon name={item.icon} className="size-4" />
                {item.label}
              </span>
            )}
          </li>
        ))}
      </ul>
    </nav>
  );
}

export function Sidebar() {
  return (
    <>
      <aside className="fixed inset-y-0 left-0 z-30 hidden w-60 border-r border-border bg-sidebar lg:flex lg:flex-col">
        <div className="border-b border-border px-5 py-5">
          <Brand />
        </div>
        <DesktopNavigation />
        <div className="mt-auto border-t border-border px-5 py-4">
          <div className="flex items-center gap-2 font-mono text-[10px] uppercase tracking-wider text-positive">
            <span className="size-1.5 bg-positive" aria-hidden="true" />
            Local system online
          </div>
          <p className="mt-2 text-[11px] leading-4 text-secondary">
            Milestone 03 · Backend mock API
          </p>
        </div>
      </aside>

      <div className="sticky top-0 z-30 border-b border-border bg-sidebar lg:hidden">
        <div className="flex items-center justify-between px-4 py-3">
          <Brand />
          <span className="font-mono text-[10px] uppercase tracking-wider text-positive">
            Online
          </span>
        </div>
        <MobileNavigation />
      </div>
    </>
  );
}
