import { useState, type FormEvent, type ReactNode } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

interface LoginGateProps {
  children: ReactNode;
}

const SESSION_KEY = "economi_auth_token";
const SESSION_NAME_KEY = "economi_auth_name";

async function loginApi(name: string): Promise<{ token: string; name: string }> {
  const resp = await fetch("/api/auth/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name }),
  });
  if (!resp.ok) {
    const err = await resp.json().catch(() => ({}));
    throw new Error(err.detail ?? "로그인 실패");
  }
  return resp.json();
}

async function verifyApi(token: string): Promise<boolean> {
  const resp = await fetch(`/api/auth/verify?token=${token}`);
  return resp.ok;
}

export function useAuth() {
  const token = sessionStorage.getItem(SESSION_KEY);
  const name = sessionStorage.getItem(SESSION_NAME_KEY);
  return { token, name, isLoggedIn: !!token };
}

export function logout() {
  sessionStorage.removeItem(SESSION_KEY);
  sessionStorage.removeItem(SESSION_NAME_KEY);
  window.location.reload();
}

export function LoginGate({ children }: LoginGateProps) {
  const [checking, setChecking] = useState(true);
  const [authenticated, setAuthenticated] = useState(false);
  const [name, setName] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  // Check existing session on mount
  useState(() => {
    const token = sessionStorage.getItem(SESSION_KEY);
    if (token) {
      verifyApi(token).then((valid) => {
        if (valid) setAuthenticated(true);
        else sessionStorage.removeItem(SESSION_KEY);
        setChecking(false);
      });
    } else {
      setChecking(false);
    }
  });

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!name.trim()) return;

    setSubmitting(true);
    setError(null);
    try {
      const result = await loginApi(name.trim());
      sessionStorage.setItem(SESSION_KEY, result.token);
      sessionStorage.setItem(SESSION_NAME_KEY, result.name);
      setAuthenticated(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : "로그인 실패");
    } finally {
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
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="이름을 입력하세요"
                autoFocus
                className="w-full rounded-lg border border-border bg-background px-4 py-2.5 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-bullish/50"
              />
            </div>
            {error && (
              <p className="text-center text-xs text-bearish">{error}</p>
            )}
            <button
              type="submit"
              disabled={submitting || !name.trim()}
              className="w-full rounded-lg bg-bullish px-4 py-2.5 text-sm font-medium text-white transition-colors hover:bg-bullish/80 disabled:opacity-50"
            >
              {submitting ? "확인중..." : "입장"}
            </button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
