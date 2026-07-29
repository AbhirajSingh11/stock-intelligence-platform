"use client";

import { useRouter } from "next/navigation";
import {
  useEffect,
  useId,
  useRef,
  useState,
  type KeyboardEvent,
} from "react";

import { Icon } from "@/components/dashboard/icons";
import { searchCompanies } from "@/lib/api/client";
import type { CompanySearchResult } from "@/types/company";

type SearchState =
  | { status: "idle"; results: CompanySearchResult[] }
  | { status: "loading"; results: CompanySearchResult[] }
  | { status: "success"; results: CompanySearchResult[] }
  | { status: "error"; results: CompanySearchResult[]; message: string };

const initialState: SearchState = { status: "idle", results: [] };
const minimumQueryLength = 2;
const debounceMilliseconds = 300;

export function CompanySearch() {
  const router = useRouter();
  const listboxId = useId();
  const containerRef = useRef<HTMLDivElement>(null);
  const [query, setQuery] = useState("");
  const [state, setState] = useState<SearchState>(initialState);
  const [isOpen, setIsOpen] = useState(false);
  const [activeIndex, setActiveIndex] = useState(-1);

  useEffect(() => {
    const normalizedQuery = query.trim();
    if (normalizedQuery.length < minimumQueryLength) {
      return;
    }

    const controller = new AbortController();

    const timeoutId = window.setTimeout(() => {
      searchCompanies(normalizedQuery, 8, controller.signal)
        .then((response) => {
          setState({ status: "success", results: response.results });
          setActiveIndex(response.results.length > 0 ? 0 : -1);
        })
        .catch((error: unknown) => {
          if (error instanceof DOMException && error.name === "AbortError") {
            return;
          }
          setState({
            status: "error",
            results: [],
            message:
              error instanceof Error
                ? error.message
                : "Company search is temporarily unavailable.",
          });
        });
    }, debounceMilliseconds);

    return () => {
      window.clearTimeout(timeoutId);
      controller.abort();
    };
  }, [query]);

  useEffect(() => {
    function closeOnOutsidePointer(event: PointerEvent) {
      if (
        containerRef.current &&
        !containerRef.current.contains(event.target as Node)
      ) {
        setIsOpen(false);
      }
    }

    document.addEventListener("pointerdown", closeOnOutsidePointer);
    return () => {
      document.removeEventListener("pointerdown", closeOnOutsidePointer);
    };
  }, []);

  function selectCompany(result: CompanySearchResult) {
    setQuery(result.ticker);
    setIsOpen(false);
    router.push(`/companies/${encodeURIComponent(result.ticker)}`);
  }

  function updateQuery(value: string) {
    setQuery(value);
    setActiveIndex(-1);

    if (value.trim().length < minimumQueryLength) {
      setState(initialState);
      setIsOpen(false);
      return;
    }

    setState({ status: "loading", results: [] });
    setIsOpen(true);
  }

  function handleKeyDown(event: KeyboardEvent<HTMLInputElement>) {
    if (event.key === "Escape") {
      setIsOpen(false);
      setActiveIndex(-1);
      return;
    }

    if (!isOpen || state.results.length === 0) {
      return;
    }

    if (event.key === "ArrowDown") {
      event.preventDefault();
      setActiveIndex((index) => (index + 1) % state.results.length);
    } else if (event.key === "ArrowUp") {
      event.preventDefault();
      setActiveIndex(
        (index) => (index <= 0 ? state.results.length - 1 : index - 1),
      );
    } else if (event.key === "Enter" && activeIndex >= 0) {
      event.preventDefault();
      selectCompany(state.results[activeIndex]);
    }
  }

  const activeResultId =
    activeIndex >= 0 ? `${listboxId}-option-${activeIndex}` : undefined;

  return (
    <div ref={containerRef} className="relative min-w-0 sm:w-80">
      <label htmlFor="ticker-search" className="sr-only">
        Search by ticker or company
      </label>
      <Icon
        name="search"
        className="pointer-events-none absolute left-3 top-1/2 z-10 size-4 -translate-y-1/2 text-secondary"
      />
      <input
        id="ticker-search"
        type="search"
        role="combobox"
        autoComplete="off"
        aria-autocomplete="list"
        aria-controls={listboxId}
        aria-expanded={isOpen}
        aria-activedescendant={activeResultId}
        value={query}
        onChange={(event) => updateQuery(event.target.value)}
        onFocus={() => {
          if (query.trim().length >= minimumQueryLength) {
            setIsOpen(true);
          }
        }}
        onKeyDown={handleKeyDown}
        placeholder="Search ticker or company"
        className="h-10 w-full border border-border bg-panel pl-10 pr-3 text-sm text-foreground outline-none placeholder:text-secondary/70 focus:border-positive focus:ring-1 focus:ring-positive"
      />

      {isOpen ? (
        <div
          id={listboxId}
          role="listbox"
          aria-label="Company search results"
          className="absolute left-0 right-0 top-[calc(100%+0.375rem)] z-50 max-h-80 overflow-y-auto border border-border bg-sidebar"
        >
          {state.status === "loading" ? (
            <p
              className="px-4 py-3 font-mono text-[10px] uppercase tracking-wider text-secondary"
              role="status"
            >
              Searching SEC companies…
            </p>
          ) : null}

          {state.status === "error" ? (
            <div className="px-4 py-3" role="alert">
              <p className="font-mono text-[10px] uppercase tracking-wider text-warning">
                Search unavailable
              </p>
              <p className="mt-1 text-xs leading-5 text-secondary">
                {state.message}
              </p>
            </div>
          ) : null}

          {state.status === "success" && state.results.length === 0 ? (
            <p
              className="px-4 py-3 text-xs text-secondary"
              role="status"
            >
              No SEC companies matched this search.
            </p>
          ) : null}

          {state.results.map((result, index) => (
            <button
              key={`${result.ticker}-${result.cik}`}
              id={`${listboxId}-option-${index}`}
              type="button"
              role="option"
              aria-selected={index === activeIndex}
              onMouseDown={(event) => event.preventDefault()}
              onMouseEnter={() => setActiveIndex(index)}
              onClick={() => selectCompany(result)}
              className={`flex w-full items-center justify-between gap-4 border-t border-border px-4 py-3 text-left outline-none first:border-t-0 focus-visible:ring-2 focus-visible:ring-inset focus-visible:ring-positive ${
                index === activeIndex ? "bg-positive/10" : "bg-sidebar"
              }`}
            >
              <span className="min-w-0">
                <span className="block font-mono text-xs font-semibold text-foreground">
                  {result.ticker}
                </span>
                <span className="mt-0.5 block truncate text-xs text-secondary">
                  {result.company_name}
                </span>
              </span>
              <span className="shrink-0 font-mono text-[9px] text-secondary">
                CIK {result.cik}
              </span>
            </button>
          ))}
        </div>
      ) : null}
    </div>
  );
}
