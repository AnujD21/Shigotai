import { Card, CardContent } from "@/components/ui/card";

export function AuthCard({
  title,
  description,
  children,
}: {
  title: string;
  description?: string;
  children: React.ReactNode;
}) {
  return (
    <Card className="shadow-[var(--shadow-md)]">
      <CardContent className="p-7">
        <h1 className="text-[20px] font-semibold tracking-tight text-[var(--color-text-primary)]">{title}</h1>
        {description && <p className="mt-1.5 text-[13.5px] text-[var(--color-text-secondary)]">{description}</p>}
        <div className="mt-6">{children}</div>
      </CardContent>
    </Card>
  );
}
