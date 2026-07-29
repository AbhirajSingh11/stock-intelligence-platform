"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import { Icon, type IconName } from "./icons";

interface NavigationItem {
  label: string;
  icon: IconName;
  href: string | null;
}

const navigation: NavigationItem[] = [
  { label: "Dashboard", icon: "dashboard", href: "/" },
  { label: "Watchlist", icon: "watchlist", href: "/#watchlist" },
  { label: "Portfolio", icon: "portfolio", href: "/#portfolio" },
  { label: "Filings", icon: "filings", href: null },
  { label: "Thesis", icon: "thesis", href: "/#thesis" },
];

function Brand() {
  return (
    <Link
      href="/"
      aria-label="Stock Intelligence dashboard"
      className="flex items-center gap-3 outline-none hover:text-foreground focus-visible:ring-2 focus-visible:ring-positive focus-visible:ring-offset-2 focus-visible:ring-offset-sidebar"
    >
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
    </Link>
  );
}

interface NavigationProps {
  pathname: string;
}

function DesktopNavigation({ pathname }: NavigationProps) {
  return (
    <nav className="mt-8" aria-label="Primary navigation">
      <ul className="space-y-1">
        {navigation.map((item) => {
          const isActive = item.href === "/" && pathname === "/";

          return (
            <li key={item.label}>
              {item.href ? (
                <Link
                  href={item.href}
                  aria-current={isActive ? "page" : undefined}
                  className={`flex items-center gap-3 border-l-2 px-4 py-2.5 text-sm outline-none focus-visible:ring-2 focus-visible:ring-inset focus-visible:ring-positive ${
                    isActive
                      ? "border-positive bg-positive/10 font-medium text-foreground"
                      : "border-transparent text-secondary hover:border-border hover:bg-white/[0.03] hover:text-foreground"
                  }`}
                >
                  <Icon
                    name={item.icon}
                    className={`size-[18px] ${
                      isActive ? "text-positive" : ""
                    }`}
                  />
                  {item.label}
                </Link>
              ) : (
                <span
                  className="flex cursor-not-allowed items-center gap-3 border-l-2 border-transparent px-4 py-2.5 text-sm text-secondary/60"
                  aria-disabled="true"
                >
                  <Icon name={item.icon} className="size-[18px]" />
                  <span>{item.label}</span>
                  <span className="ml-auto border border-warning/30 bg-warning/10 px-1.5 py-0.5 font-mono text-[8px] uppercase tracking-wider text-warning">
                    Planned
                  </span>
                </span>
              )}
            </li>
          );
        })}
      </ul>
    </nav>
  );
}

function MobileNavigation({ pathname }: NavigationProps) {
  return (
    <nav
      className="overflow-x-auto border-t border-border"
      aria-label="Mobile navigation"
    >
      <ul className="flex min-w-max px-3">
        {navigation.map((item) => {
          const isActive = item.href === "/" && pathname === "/";

          return (
            <li key={item.label}>
              {item.href ? (
                <Link
                  href={item.href}
                  aria-current={isActive ? "page" : undefined}
                  className={`flex items-center gap-2 border-b-2 px-3 py-3 text-xs outline-none focus-visible:ring-2 focus-visible:ring-inset focus-visible:ring-positive ${
                    isActive
                      ? "border-positive font-medium text-foreground"
                      : "border-transparent text-secondary hover:border-border hover:text-foreground"
                  }`}
                >
                  <Icon
                    name={item.icon}
                    className={`size-4 ${isActive ? "text-positive" : ""}`}
                  />
                  {item.label}
                </Link>
              ) : (
                <span
                  className="flex cursor-not-allowed items-center gap-1.5 border-b-2 border-transparent px-3 py-3 text-xs text-secondary/60"
                  aria-disabled="true"
                >
                  <Icon name={item.icon} className="size-4" />
                  {item.label}
                  <span className="border border-warning/30 bg-warning/10 px-1 py-0.5 font-mono text-[7px] uppercase tracking-wide text-warning">
                    Planned
                  </span>
                </span>
              )}
            </li>
          );
        })}
      </ul>
    </nav>
  );
}

export function Sidebar() {
  const pathname = usePathname();

  return (
    <>
      <aside className="fixed inset-y-0 left-0 z-30 hidden w-60 border-r border-border bg-sidebar lg:flex lg:flex-col">
        <div className="border-b border-border px-5 py-5">
          <Brand />
        </div>
        <DesktopNavigation pathname={pathname} />
        <div className="mt-auto border-t border-border px-5 py-4">
          <div className="flex items-center gap-2 font-mono text-[10px] uppercase tracking-wider text-positive">
            <span className="size-1.5 bg-positive" aria-hidden="true" />
            Local system online
          </div>
          <p className="mt-2 text-[11px] leading-4 text-secondary">
            Milestone 04 · SEC EDGAR
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
        <MobileNavigation pathname={pathname} />
      </div>
    </>
  );
}
