import { ButtonHTMLAttributes } from "react";
import { clsx } from "clsx";

type ButtonProps = ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: "primary" | "secondary";
};

export default function Button({ variant = "primary", className, ...props }: ButtonProps) {
  return (
    <button
      className={clsx(
        "rounded-md px-4 py-2 text-sm font-medium transition-colors",
        variant === "primary" && "bg-[#087f78] text-white shadow-sm hover:bg-[#075d59]",
        variant === "secondary" && "bg-slate-100 text-slate-900 hover:bg-slate-200",
        className
      )}
      {...props}
    />
  );
}
