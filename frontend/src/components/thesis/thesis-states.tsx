export function ThesisLoading({ label = "Loading thesis journal" }: { label?: string }) {
  return <div className="space-y-4" role="status" aria-label={label}>{Array.from({ length: 3 }, (_, index) => <div key={index} className="h-36 animate-pulse border border-border bg-panel motion-reduce:animate-none" />)}</div>;
}

export function ThesisError({ message, onRetry }: { message: string; onRetry: () => void }) {
  return <section className="border border-warning/50 bg-panel p-6" role="alert"><h2 className="text-lg font-semibold text-foreground">Thesis journal unavailable</h2><p className="mt-2 max-w-2xl text-sm leading-6 text-secondary">{message}</p><button type="button" onClick={onRetry} className="mt-5 border border-warning bg-warning px-4 py-2.5 font-mono text-xs font-semibold uppercase tracking-wider text-[#171006] outline-none hover:bg-[#F0B75F] focus-visible:ring-2 focus-visible:ring-warning">Retry</button></section>;
}
