import Link, { type LinkProps } from "next/link";
import { buttonClasses, BUTTON_SIZES, BUTTON_VARIANTS } from "@/components/ui/button-styles";

export interface LinkButtonProps extends LinkProps {
  variant?: keyof typeof BUTTON_VARIANTS;
  size?: keyof typeof BUTTON_SIZES;
  className?: string;
  children: React.ReactNode;
}

export function LinkButton({ variant, size, className, children, ...props }: LinkButtonProps) {
  return (
    <Link className={buttonClasses(variant, size, className)} {...props}>
      {children}
    </Link>
  );
}
