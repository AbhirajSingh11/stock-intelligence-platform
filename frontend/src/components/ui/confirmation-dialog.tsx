"use client";

import { useEffect, useId, useRef } from "react";

export function ConfirmationDialog({
  title,
  description,
  confirmLabel,
  busy,
  onConfirm,
  onCancel,
}: {
  title: string;
  description: string;
  confirmLabel: string;
  busy: boolean;
  onConfirm: () => void;
  onCancel: () => void;
}) {
  const dialogRef = useRef<HTMLDivElement>(null);
  const cancelRef = useRef<HTMLButtonElement>(null);
  const titleId = useId();
  const descriptionId = useId();

  useEffect(() => {
    const previouslyFocused = document.activeElement;
    cancelRef.current?.focus();
    return () => {
      if (previouslyFocused instanceof HTMLElement) previouslyFocused.focus();
    };
  }, []);

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 p-4"
      role="alertdialog"
      aria-modal="true"
      aria-labelledby={titleId}
      aria-describedby={descriptionId}
      onKeyDown={(event) => {
        if (event.key === "Escape" && !busy) onCancel();
        if (event.key !== "Tab") return;
        const focusable = Array.from(
          dialogRef.current?.querySelectorAll<HTMLElement>(
            "button:not([disabled]), input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [href], [tabindex]:not([tabindex='-1'])",
          ) ?? [],
        );
        if (focusable.length === 0) return;
        const first = focusable[0];
        const last = focusable[focusable.length - 1];
        if (event.shiftKey && document.activeElement === first) {
          event.preventDefault();
          last.focus();
        } else if (!event.shiftKey && document.activeElement === last) {
          event.preventDefault();
          first.focus();
        }
      }}
    >
      <div ref={dialogRef} className="w-full max-w-md border border-warning/50 bg-panel p-6">
        <h2 id={titleId} className="text-lg font-semibold text-foreground">{title}</h2>
        <p id={descriptionId} className="mt-3 text-sm leading-6 text-secondary">{description}</p>
        <div className="mt-6 flex justify-end gap-3">
          <button ref={cancelRef} type="button" onClick={onCancel} disabled={busy} className="border border-border px-4 py-2 font-mono text-xs uppercase tracking-wider text-secondary outline-none hover:text-foreground focus-visible:ring-2 focus-visible:ring-positive disabled:opacity-50">Cancel</button>
          <button type="button" onClick={onConfirm} disabled={busy} className="border border-warning bg-warning px-4 py-2 font-mono text-xs font-semibold uppercase tracking-wider text-[#171006] outline-none hover:bg-[#F0B75F] focus-visible:ring-2 focus-visible:ring-warning disabled:cursor-wait disabled:opacity-50">
            {busy ? "Deleting…" : confirmLabel}
          </button>
        </div>
      </div>
    </div>
  );
}
