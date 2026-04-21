import { useEffect, useState, type FormEvent, type ReactNode } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { api } from "@/lib/api";
import {
  clearLegacySession,
  getLegacyName,
  isSupabaseEnabled,
  setLegacySession,
  supabase,
} from "@/lib/supabase";

type AuthMode = "name" | "email" | "oauth";

interface LoginGateProps {
  children: ReactNode;
}

interface AuthState {
  identity: string;
  source: "legacy" | "supabase";
  isAdmin: boolean;
  photoUrl: string | null;
}

const BASE_URL = import.meta.env.VITE_API_URL || "/api";

interface LegacyLoginResult {
  token: string;
  name: string;
  is_admin: boolean;
  photo_url: string | null;
}

async function legacyLogin(name: string): Promise<LegacyLoginResult> {
  let resp: Response;
  try {
    resp = await fetch(`${BASE_URL}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name }),
    });
  } catch {
    throw new Error("서버에 연결할 수 없습니다. 잠시 후 다시 시도해주세요.");
  }
  if (!resp.ok) {
    const err = await resp.json().catch(() => ({}));
    throw new Error(err.detail ?? "로그인 실패");
  }
  return resp.json();
}

export const SPLASH_KEY = "economi_login_splash";
const MOBILE_BREAKPOINT = 1024; // Tailwind lg

function markLoginSplash(photoUrl: string | null): void {
  if (!photoUrl) return;
  sessionStorage.setItem(SPLASH_KEY, photoUrl);
}

/**
 * Renders a full-screen photo overlay for 2s after a successful mobile login.
 * The splash consumes the ``economi_login_splash`` sessionStorage flag so it
 * fires exactly once per login event.
 */
export function LoginSplash() {
  const [photo, setPhoto] = useState<string | null>(null);
  const [fadingOut, setFadingOut] = useState(false);

  useEffect(() => {
    const stored = sessionStorage.getItem(SPLASH_KEY);
    sessionStorage.removeItem(SPLASH_KEY);
    if (!stored) return;
    if (typeof window !== "undefined" && window.innerWidth >= MOBILE_BREAKPOINT) return;

    setPhoto(stored);
    const fadeTimer = window.setTimeout(() => setFadingOut(true), 1600);
    const clearTimer = window.setTimeout(() => setPhoto(null), 2000);
    return () => {
      window.clearTimeout(fadeTimer);
      window.clearTimeout(clearTimer);
    };
  }, []);

  if (!photo) return null;

  return (
    <div
      className={`fixed inset-0 z-[60] flex items-center justify-center bg-black transition-opacity duration-500 ${
        fadingOut ? "opacity-0" : "opacity-100"
      }`}
    >
      <img
        src={photo}
        alt=""
        className="max-h-full max-w-full object-contain"
      />
    </div>
  );
}

async function verifyLegacyToken(token: string): Promise<boolean> {
  try {
    const resp = await fetch(`${BASE_URL}/auth/verify?token=${token}`);
    return resp.ok;
  } catch {
    return false;
  }
}

export function useAuth(): {
  identity: string | null;
  isLoggedIn: boolean;
  isAdmin: boolean;
  photoUrl: string | null;
  source: "legacy" | "supabase" | null;
  refresh: () => Promise<void>;
} {
  const [state, setState] = useState<AuthState | null>(null);

  const hydrateFromServer = async (
    fallback: { identity: string; source: "legacy" | "supabase" },
  ): Promise<void> => {
    try {
      const me = await api.getMe();
      setState({
        identity: me.identity,
        source: me.source,
        isAdmin: me.is_admin,
        photoUrl: me.photo_url,
      });
    } catch {
      // /auth/me unreachable — fall back to local session info with no admin rights.
      setState({ ...fallback, isAdmin: false, photoUrl: null });
    }
  };

  useEffect(() => {
    const legacyName = getLegacyName();
    if (legacyName) {
      void hydrateFromServer({ identity: legacyName, source: "legacy" });
    }

    if (supabase) {
      supabase.auth.getSession().then(({ data }) => {
        const email = data.session?.user?.email;
        if (email) void hydrateFromServer({ identity: email, source: "supabase" });
      });
      const { data: sub } = supabase.auth.onAuthStateChange((_event, session) => {
        const email = session?.user?.email;
        if (email) {
          void hydrateFromServer({ identity: email, source: "supabase" });
        } else if (!getLegacyName()) {
          setState(null);
        }
      });
      return () => sub.subscription.unsubscribe();
    }
  }, []);

  const refresh = async (): Promise<void> => {
    const legacyName = getLegacyName();
    if (legacyName) {
      await hydrateFromServer({ identity: legacyName, source: "legacy" });
      return;
    }
    if (supabase) {
      const { data } = await supabase.auth.getSession();
      const email = data.session?.user?.email;
      if (email) await hydrateFromServer({ identity: email, source: "supabase" });
    }
  };

  return {
    identity: state?.identity ?? null,
    isLoggedIn: state !== null,
    isAdmin: state?.isAdmin ?? false,
    photoUrl: state?.photoUrl ?? null,
    source: state?.source ?? null,
    refresh,
  };
}

export async function logout(): Promise<void> {
  clearLegacySession();
  if (supabase) await supabase.auth.signOut();
  window.location.reload();
}

export function LoginGate({ children }: LoginGateProps) {
  const [checking, setChecking] = useState(true);
  const [authenticated, setAuthenticated] = useState(false);
  const [mode, setMode] = useState<AuthMode>("name");
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [magicSent, setMagicSent] = useState(false);

  useEffect(() => {
    let cancelled = false;

    async function restoreSession() {
      // 1. Supabase session (localStorage persistent)
      if (supabase) {
        const { data } = await supabase.auth.getSession();
        if (data.session?.user?.email) {
          if (!cancelled) {
            setAuthenticated(true);
            setChecking(false);
          }
          return;
        }
      }

      // 2. Legacy session token (sessionStorage)
      const legacyName = getLegacyName();
      if (legacyName) {
        const token = sessionStorage.getItem("economi_auth_token");
        if (token && (await verifyLegacyToken(token))) {
          if (!cancelled) {
            setAuthenticated(true);
            setChecking(false);
          }
          return;
        }
        clearLegacySession();
      }

      if (!cancelled) setChecking(false);
    }

    restoreSession();

    // Listen for Supabase sign-in (OAuth redirect callback)
    if (supabase) {
      const { data: sub } = supabase.auth.onAuthStateChange((_event, session) => {
        if (session?.user?.email && !cancelled) setAuthenticated(true);
      });
      return () => {
        cancelled = true;
        sub.subscription.unsubscribe();
      };
    }

    return () => {
      cancelled = true;
    };
  }, []);

  const submitName = async (e: FormEvent) => {
    e.preventDefault();
    if (!name.trim()) return;
    setSubmitting(true);
    setError(null);
    try {
      const result = await legacyLogin(name.trim());
      setLegacySession(result.token, result.name);
      markLoginSplash(result.photo_url);
      setAuthenticated(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : "로그인 실패");
    } finally {
      setSubmitting(false);
    }
  };

  const submitMagicLink = async (e: FormEvent) => {
    e.preventDefault();
    if (!supabase || !email.trim()) return;
    setSubmitting(true);
    setError(null);
    setMagicSent(false);
    try {
      const { allowed } = await api.checkEmail(email.trim());
      if (!allowed) {
        throw new Error("승인되지 않은 이메일입니다");
      }
      const { error: otpError } = await supabase.auth.signInWithOtp({
        email: email.trim(),
        options: { emailRedirectTo: window.location.origin },
      });
      if (otpError) throw new Error(otpError.message);
      setMagicSent(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Magic Link 전송 실패");
    } finally {
      setSubmitting(false);
    }
  };

  const submitGoogle = async () => {
    if (!supabase) return;
    setSubmitting(true);
    setError(null);
    try {
      const { error: oauthError } = await supabase.auth.signInWithOAuth({
        provider: "google",
        options: { redirectTo: window.location.origin },
      });
      if (oauthError) throw new Error(oauthError.message);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Google 로그인 실패");
      setSubmitting(false);
    }
  };

  if (checking) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-background">
        <p className="text-muted-foreground animate-pulse">인증 확인중...</p>
      </div>
    );
  }

  if (authenticated) {
    return <>{children}</>;
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-background p-4">
      <Card className="w-full max-w-sm">
        <CardHeader className="text-center">
          <CardTitle className="text-lg">Market Insights Dashboard</CardTitle>
          <p className="text-xs text-muted-foreground">승인된 사용자만 접근 가능합니다</p>
        </CardHeader>
        <CardContent className="space-y-4">
          {isSupabaseEnabled && (
            <div className="flex gap-1 rounded-lg bg-muted p-1 text-xs">
              <ModeButton active={mode === "name"} onClick={() => { setMode("name"); setError(null); }}>
                이름
              </ModeButton>
              <ModeButton active={mode === "email"} onClick={() => { setMode("email"); setError(null); }}>
                이메일
              </ModeButton>
              <ModeButton active={mode === "oauth"} onClick={() => { setMode("oauth"); setError(null); }}>
                Google
              </ModeButton>
            </div>
          )}

          {mode === "name" && (
            <form onSubmit={submitName} className="space-y-4">
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="이름을 입력하세요"
                autoFocus
                className="w-full rounded-lg border border-border bg-background px-4 py-2.5 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-bullish/50"
              />
              <SubmitButton disabled={submitting || !name.trim()}>
                {submitting ? "확인중..." : "입장"}
              </SubmitButton>
            </form>
          )}

          {mode === "email" && isSupabaseEnabled && (
            <form onSubmit={submitMagicLink} className="space-y-4">
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="승인된 이메일 주소"
                autoFocus
                className="w-full rounded-lg border border-border bg-background px-4 py-2.5 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-bullish/50"
              />
              <SubmitButton disabled={submitting || !email.trim()}>
                {submitting ? "전송중..." : "Magic Link 받기"}
              </SubmitButton>
              {magicSent && (
                <p className="text-center text-xs text-bullish">
                  이메일로 로그인 링크를 전송했습니다
                </p>
              )}
            </form>
          )}

          {mode === "oauth" && isSupabaseEnabled && (
            <div className="space-y-4">
              <button
                type="button"
                onClick={submitGoogle}
                disabled={submitting}
                className="flex w-full items-center justify-center gap-2 rounded-lg border border-border bg-background px-4 py-2.5 text-sm font-medium text-foreground transition-colors hover:bg-muted disabled:opacity-50"
              >
                <GoogleIcon />
                {submitting ? "이동중..." : "Google로 계속하기"}
              </button>
            </div>
          )}

          {error && (
            <p className="text-center text-xs text-bearish">{error}</p>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

function ModeButton({
  active,
  onClick,
  children,
}: {
  active: boolean;
  onClick: () => void;
  children: ReactNode;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={`flex-1 rounded-md px-2 py-1.5 font-medium transition-colors ${
        active
          ? "bg-background text-foreground shadow-sm"
          : "text-muted-foreground hover:text-foreground"
      }`}
    >
      {children}
    </button>
  );
}

function SubmitButton({
  disabled,
  children,
}: {
  disabled: boolean;
  children: ReactNode;
}) {
  return (
    <button
      type="submit"
      disabled={disabled}
      className="w-full rounded-lg bg-bullish px-4 py-2.5 text-sm font-medium text-white transition-colors hover:bg-bullish/80 disabled:opacity-50"
    >
      {children}
    </button>
  );
}

function GoogleIcon() {
  return (
    <svg className="h-4 w-4" viewBox="0 0 24 24" aria-hidden="true">
      <path fill="#4285F4" d="M22.54 12.27c0-.79-.07-1.54-.2-2.27H12v4.29h5.92c-.26 1.37-1.04 2.54-2.21 3.32v2.77h3.57c2.09-1.93 3.26-4.77 3.26-8.11z" />
      <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.99.66-2.25 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C4 20.53 7.7 23 12 23z" />
      <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" />
      <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 4 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" />
    </svg>
  );
}
