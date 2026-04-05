import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatPercent(value: number): string {
  const sign = value >= 0 ? "+" : "";
  return `${sign}${value.toFixed(2)}%`;
}

export function formatPrice(value: number): string {
  return value.toLocaleString("en-US", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });
}

export function formatCompactNumber(value: number): string {
  return Intl.NumberFormat("en-US", { notation: "compact" }).format(value);
}

export function getChangeColor(value: number): string {
  if (value > 0) return "text-bullish";
  if (value < 0) return "text-bearish";
  return "text-muted-foreground";
}

export function getImpactColor(score: number): string {
  if (score >= 7) return "bg-impact-high text-white";
  if (score >= 4) return "bg-impact-medium text-black";
  return "bg-impact-low text-white";
}
