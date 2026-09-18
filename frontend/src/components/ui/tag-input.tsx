"use client";

import { useMemo, useState } from "react";
import { X } from "lucide-react";
import { cn } from "@/lib/utils";

export function TagInput({
  values,
  onChange,
  suggestions = [],
  placeholder = "Type and press Enter",
  className,
  id,
  "aria-label": ariaLabel,
}: {
  values: string[];
  onChange: (values: string[]) => void;
  suggestions?: string[];
  placeholder?: string;
  className?: string;
  id?: string;
  "aria-label"?: string;
}) {
  const [input, setInput] = useState("");
  const [showSuggestions, setShowSuggestions] = useState(false);

  const filteredSuggestions = useMemo(() => {
    if (!input.trim()) return [];
    const lower = input.toLowerCase();
    return suggestions
      .filter((s) => s.toLowerCase().includes(lower) && !values.some((v) => v.toLowerCase() === s.toLowerCase()))
      .slice(0, 6);
  }, [input, suggestions, values]);

  function addValue(raw: string) {
    const value = raw.trim();
    if (!value) return;
    if (values.some((v) => v.toLowerCase() === value.toLowerCase())) {
      setInput("");
      return;
    }
    onChange([...values, value]);
    setInput("");
    setShowSuggestions(false);
  }

  function removeValue(value: string) {
    onChange(values.filter((v) => v !== value));
  }

  return (
    <div className={cn("relative", className)}>
      <div className="flex min-h-11 flex-wrap items-center gap-1.5 rounded-[var(--radius-sm)] border border-[var(--color-border-strong)] bg-[var(--color-surface)] p-2 focus-within:border-[var(--color-accent)] focus-within:ring-2 focus-within:ring-[var(--color-accent)]/15">
        {values.map((value) => (
          <span
            key={value}
            className="flex items-center gap-1 rounded-full bg-[var(--color-bg-subtle)] px-2.5 py-1 text-[12.5px] font-medium text-[var(--color-text-primary)]"
          >
            {value}
            <button
              type="button"
              onClick={() => removeValue(value)}
              aria-label={`Remove ${value}`}
              className="text-[var(--color-text-tertiary)] hover:text-[var(--color-danger)]"
            >
              <X className="size-3" aria-hidden />
            </button>
          </span>
        ))}
        <input
          id={id}
          aria-label={ariaLabel ?? (id ? undefined : placeholder)}
          value={input}
          onChange={(e) => {
            setInput(e.target.value);
            setShowSuggestions(true);
          }}
          onKeyDown={(e) => {
            if (e.key === "Enter" || e.key === ",") {
              e.preventDefault();
              addValue(input);
            } else if (e.key === "Backspace" && !input && values.length > 0) {
              removeValue(values[values.length - 1]);
            }
          }}
          onFocus={() => setShowSuggestions(true)}
          onBlur={() => setTimeout(() => setShowSuggestions(false), 120)}
          placeholder={values.length === 0 ? placeholder : ""}
          className="min-w-[120px] flex-1 bg-transparent px-1 py-1 text-sm outline-none placeholder:text-[var(--color-text-tertiary)]"
        />
      </div>
      {showSuggestions && filteredSuggestions.length > 0 && (
        <ul className="absolute z-10 mt-1.5 w-full overflow-hidden rounded-[var(--radius-sm)] border border-[var(--color-border)] bg-[var(--color-surface)] py-1 shadow-[var(--shadow-md)]">
          {filteredSuggestions.map((s) => (
            <li key={s}>
              <button
                type="button"
                onMouseDown={(e) => e.preventDefault()}
                onClick={() => addValue(s)}
                className="block w-full px-3 py-2 text-left text-[13.5px] text-[var(--color-text-primary)] hover:bg-[var(--color-bg-subtle)]"
              >
                {s}
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
