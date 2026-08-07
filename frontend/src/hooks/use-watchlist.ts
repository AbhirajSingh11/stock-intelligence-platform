"use client";

import { useEffect, useState } from "react";

import {
  addWatchlistEntry,
  deleteWatchlistEntry,
  getWatchlist,
} from "@/lib/api/client";
import type { WatchlistEntry } from "@/types/watchlist";

type WatchlistState =
  | { status: "loading"; entries: WatchlistEntry[]; message: null }
  | { status: "success"; entries: WatchlistEntry[]; message: null }
  | { status: "error"; entries: WatchlistEntry[]; message: string };

type WatchlistAction = { kind: "add" | "remove"; ticker: string };

type MutationState =
  | { status: "idle" }
  | { status: "pending"; action: WatchlistAction }
  | { status: "success"; action: WatchlistAction }
  | { status: "error"; action: WatchlistAction; message: string };

const initialState: WatchlistState = {
  status: "loading",
  entries: [],
  message: null,
};

function errorMessage(error: unknown): string {
  return error instanceof Error
    ? error.message
    : "An unexpected error occurred while updating the watchlist.";
}

function sortEntries(entries: WatchlistEntry[]): WatchlistEntry[] {
  return [...entries].sort((left, right) =>
    left.ticker < right.ticker ? -1 : left.ticker > right.ticker ? 1 : 0,
  );
}

export function useWatchlist() {
  const [state, setState] = useState<WatchlistState>(initialState);
  const [mutation, setMutation] = useState<MutationState>({ status: "idle" });
  const [requestVersion, setRequestVersion] = useState(0);

  useEffect(() => {
    const controller = new AbortController();

    getWatchlist(controller.signal)
      .then((response) => {
        setState({
          status: "success",
          entries: sortEntries(response.entries),
          message: null,
        });
      })
      .catch((error: unknown) => {
        if (error instanceof DOMException && error.name === "AbortError") {
          return;
        }
        setState({ status: "error", entries: [], message: errorMessage(error) });
      });

    return () => controller.abort();
  }, [requestVersion]);

  async function perform(action: WatchlistAction): Promise<void> {
    setMutation({ status: "pending", action });
    try {
      if (action.kind === "add") {
        const entry = await addWatchlistEntry(action.ticker);
        setState((current) => ({
          status: "success",
          entries: sortEntries([
            ...current.entries.filter((item) => item.ticker !== entry.ticker),
            entry,
          ]),
          message: null,
        }));
      } else {
        await deleteWatchlistEntry(action.ticker);
        setState((current) => ({
          status: "success",
          entries: current.entries.filter(
            (entry) => entry.ticker !== action.ticker,
          ),
          message: null,
        }));
      }
      setMutation({ status: "success", action });
    } catch (error: unknown) {
      setMutation({
        status: "error",
        action,
        message: errorMessage(error),
      });
    }
  }

  return {
    ...state,
    mutation,
    retryLoad: () => {
      setState(initialState);
      setRequestVersion((version) => version + 1);
    },
    add: (ticker: string) => perform({ kind: "add", ticker }),
    remove: (ticker: string) => perform({ kind: "remove", ticker }),
    retryMutation: () =>
      mutation.status === "error" ? perform(mutation.action) : Promise.resolve(),
  };
}
