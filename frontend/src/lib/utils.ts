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

// --- localStorage cache helpers ---

const DEFAULT_CACHE_TTL_MS = 60 * 60 * 1000; // 1 hour

interface CacheEntry<T> {
  data: T;
  ts: number;
}

export function getCached<T>(key: string, ttlMs: number = DEFAULT_CACHE_TTL_MS): T | null {
  try {
    const raw = localStorage.getItem(key);
    if (!raw) return null;
    const entry: CacheEntry<T> = JSON.parse(raw);
    if (Date.now() - entry.ts < ttlMs) return entry.data;
    localStorage.removeItem(key);
  } catch {
    localStorage.removeItem(key);
  }
  return null;
}

export function setCache<T>(key: string, data: T): void {
  try {
    const entry: CacheEntry<T> = { data, ts: Date.now() };
    localStorage.setItem(key, JSON.stringify(entry));
  } catch {
    // quota exceeded — silently ignore
  }
}
