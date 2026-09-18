import { forwardRef, type InputHTMLAttributes } from "react";
import { Check } from "lucide-react";
import { cn } from "@/lib/utils";

export interface CheckboxProps extends Omit<InputHTMLAttributes<HTMLInputElement>, "type"> {
  label?: React.ReactNode;
  description?: string;
}

export const Checkbox = forwardRef<HTMLInputElement, CheckboxProps>(
  ({ className, label, description, id, ...props }, ref) => {
    const inputId = id ?? `checkbox-${label ?? Math.random().toString(36).slice(2)}`;
    return (
      <label htmlFor={inputId} className={cn("flex cursor-pointer items-start gap-2.5", className)}>
        <span className="relative mt-0.5 flex size-[18px] shrink-0 items-center justify-center">
          <input ref={ref} id={inputId} type="checkbox" className="peer sr-only" {...props} />
          <span className="absolute inset-0 rounded-[4px] border border-[var(--color-border-strong)] bg-[var(--color-surface)] transition-colors peer-checked:border-[var(--color-accent)] peer-checked:bg-[var(--color-accent)] peer-focus-visible:ring-2 peer-focus-visible:ring-[var(--color-accent)]/30" />
          <Check className="relative size-3 text-[var(--color-text-on-accent)] opacity-0 peer-checked:opacity-100" aria-hidden />
        </span>
        {(label || description) && (
          <span>
            {label && <span className="block text-[13.5px] font-medium text-[var(--color-text-primary)]">{label}</span>}
            {description && <span className="block text-[12.5px] text-[var(--color-text-tertiary)]">{description}</span>}
          </span>
        )}
      </label>
    );
  }
);
Checkbox.displayName = "Checkbox";
