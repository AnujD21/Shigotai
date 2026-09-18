export function BarList({ items }: { items: { label: string; value: number }[] }) {
  const max = Math.max(...items.map((item) => item.value), 1);

  return (
    <ul className="space-y-3.5">
      {items.map((item) => (
        <li key={item.label} className="flex items-center gap-3">
          <span className="w-36 shrink-0 truncate text-[13px] text-[var(--color-text-secondary)]" title={item.label}>
            {item.label}
          </span>
          <div className="h-2 flex-1 overflow-hidden rounded-full bg-[var(--color-accent-subtle)]">
            <div
              className="h-full rounded-full bg-[var(--color-accent)]"
              style={{ width: `${item.value > 0 ? Math.max(4, (item.value / max) * 100) : 0}%` }}
            />
          </div>
          <span className="w-6 shrink-0 text-right text-[13px] font-medium tabular-nums text-[var(--color-text-primary)]">
            {item.value}
          </span>
        </li>
      ))}
    </ul>
  );
}
