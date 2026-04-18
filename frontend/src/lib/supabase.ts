import { createClient, type SupabaseClient } from "@supabase/supabase-js";

const SUPABASE_URL = import.meta.env.VITE_SUPABASE_URL;
const SUPABASE_ANON_KEY = import.meta.env.VITE_SUPABASE_ANON_KEY;

// Auth is optional — if env vars are missing we still run in legacy name-only mode.
export const supabase: SupabaseClient | null =
  SUPABASE_URL && SUPABASE_ANON_KEY
    ? createClient(SUPABASE_URL, SUPABASE_ANON_KEY, {
        auth: {
          persistSession: true,
          autoRefreshToken: true,
          detectSessionInUrl: true,
          flowType: "pkce",
        },
      })
    : null;

export const isSupabaseEnabled = supabase !== null;

// Legacy session token (name-only login). Kept so manually-added users continue to work.
const LEGACY_TOKEN_KEY = "economi_auth_token";
const LEGACY_NAME_KEY = "economi_auth_name";

export function getLegacyToken(): string | null {
  return sessionStorage.getItem(LEGACY_TOKEN_KEY);
}

export function getLegacyName(): string | null {
  return sessionStorage.getItem(LEGACY_NAME_KEY);
}

export function setLegacySession(token: string, name: string): void {
  sessionStorage.setItem(LEGACY_TOKEN_KEY, token);
  sessionStorage.setItem(LEGACY_NAME_KEY, name);
}

export function clearLegacySession(): void {
  sessionStorage.removeItem(LEGACY_TOKEN_KEY);
  sessionStorage.removeItem(LEGACY_NAME_KEY);
}

/**
 * Returns the best available auth token for API calls — Supabase JWT first, legacy fallback.
 * Returns ``null`` when neither is present (caller can still issue public requests).
 */
export async function getAuthToken(): Promise<string | null> {
  if (supabase) {
    const { data } = await supabase.auth.getSession();
    if (data.session?.access_token) return data.session.access_token;
  }
  return getLegacyToken();
}
