export function PageHeader({
  title,
  description,
  action,
}: {
  title: string;
  description?: string;
  action?: React.ReactNode;
}) {
  return (
    <div className="mb-8 flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
      <div>
        <h1 className="text-[24px] font-semibold tracking-tight text-[var(--color-text-primary)]">{title}</h1>
        {description && <p className="mt-1.5 text-[14px] text-[var(--color-text-secondary)]">{description}</p>}
      </div>
      {action}
    </div>
  );
}
