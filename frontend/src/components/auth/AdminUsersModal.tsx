import { useEffect, useRef, useState, type ChangeEvent, type FormEvent } from "react";

import { api } from "@/lib/api";
import { cn } from "@/lib/utils";
import type { AllowedUser } from "@/types";

interface AdminUsersModalProps {
  open: boolean;
  onClose: () => void;
  currentIdentity: string;
}

export function AdminUsersModal({ open, onClose, currentIdentity }: AdminUsersModalProps) {
  const [users, setUsers] = useState<AllowedUser[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [newName, setNewName] = useState("");
  const [busyFor, setBusyFor] = useState<string | null>(null);
  const fileInputRefs = useRef<Record<string, HTMLInputElement | null>>({});

  const load = async () => {
    setLoading(true);
    setError(null);
    try {
      setUsers(await api.listAllowedUsers());
    } catch (err) {
      setError(err instanceof Error ? err.message : "목록을 불러올 수 없습니다");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (open) void load();
  }, [open]);

  useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open, onClose]);

  if (!open) return null;

  const handleAdd = async (e: FormEvent) => {
    e.preventDefault();
    const trimmed = newName.trim().toLowerCase();
    if (!trimmed) return;
    setBusyFor("__add__");
    setError(null);
    try {
      await api.addAllowedUser(trimmed);
      setNewName("");
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "추가 실패");
    } finally {
      setBusyFor(null);
    }
  };

  const handleDelete = async (name: string) => {
    if (!confirm(`${name} 사용자를 삭제하시겠습니까?`)) return;
    setBusyFor(name);
    setError(null);
    try {
      await api.deleteAllowedUser(name);
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "삭제 실패");
    } finally {
      setBusyFor(null);
    }
  };

  const handlePhotoChange = async (name: string, e: ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    e.target.value = "";
    if (!file) return;
    if (file.size > 2 * 1024 * 1024) {
      setError("파일이 2MB를 초과합니다");
      return;
    }
    setBusyFor(name);
    setError(null);
    try {
      await api.uploadAvatar(name, file);
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "업로드 실패");
    } finally {
      setBusyFor(null);
    }
  };

  const backdropClick = (e: React.MouseEvent<HTMLDivElement>) => {
    if (e.target === e.currentTarget) onClose();
  };

  return (
    <div
      onClick={backdropClick}
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4 backdrop-blur-sm"
    >
      <div className="w-full max-w-md overflow-hidden rounded-xl border border-border bg-card shadow-2xl">
        <div className="flex items-center justify-between border-b border-border px-5 py-3">
          <h2 className="text-sm font-semibold text-foreground">사용자 관리</h2>
          <button
            type="button"
            onClick={onClose}
            aria-label="닫기"
            className="text-muted-foreground hover:text-foreground"
          >
            ✕
          </button>
        </div>

        <div className="max-h-[70vh] space-y-4 overflow-y-auto p-5">
          <form onSubmit={handleAdd} className="flex gap-2">
            <input
              type="text"
              value={newName}
              onChange={(e) => setNewName(e.target.value)}
              placeholder="새 사용자 이름"
              className="flex-1 rounded-lg border border-border bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-bullish/50"
            />
            <button
              type="submit"
              disabled={busyFor === "__add__" || !newName.trim()}
              className="rounded-lg bg-bullish px-3 py-2 text-sm font-medium text-white transition-colors hover:bg-bullish/80 disabled:opacity-50"
            >
              {busyFor === "__add__" ? "추가중..." : "추가"}
            </button>
          </form>

          {error && <p className="text-xs text-bearish">{error}</p>}

          <div className="space-y-2">
            {loading && users.length === 0 ? (
              <p className="text-center text-xs text-muted-foreground">불러오는 중...</p>
            ) : users.length === 0 ? (
              <p className="text-center text-xs text-muted-foreground">등록된 사용자가 없습니다</p>
            ) : (
              users.map((u) => {
                const isSelf = u.name === currentIdentity.toLowerCase();
                const isBusy = busyFor === u.name;
                return (
                  <div
                    key={u.name}
                    className="flex items-center gap-3 rounded-lg border border-border/50 bg-background/40 p-2"
                  >
                    <Avatar photoUrl={u.photo_url} name={u.name} />
                    <div className="min-w-0 flex-1">
                      <p className="truncate text-sm font-medium text-foreground">
                        {u.name}
                        {isSelf && (
                          <span className="ml-1 text-[10px] text-muted-foreground">(나)</span>
                        )}
                      </p>
                      {u.added_by && (
                        <p className="truncate text-[10px] text-muted-foreground">
                          등록: {u.added_by}
                        </p>
                      )}
                    </div>
                    <input
                      ref={(el) => {
                        fileInputRefs.current[u.name] = el;
                      }}
                      type="file"
                      accept="image/jpeg,image/png,image/webp"
                      className="hidden"
                      onChange={(e) => handlePhotoChange(u.name, e)}
                    />
                    <button
                      type="button"
                      disabled={isBusy}
                      onClick={() => fileInputRefs.current[u.name]?.click()}
                      className={cn(
                        "rounded-md border border-border px-2 py-1 text-[11px] text-muted-foreground transition-colors hover:bg-muted",
                        isBusy && "opacity-50",
                      )}
                    >
                      사진
                    </button>
                    <button
                      type="button"
                      disabled={isSelf || isBusy}
                      onClick={() => handleDelete(u.name)}
                      className={cn(
                        "rounded-md border border-border px-2 py-1 text-[11px] transition-colors",
                        isSelf || isBusy
                          ? "cursor-not-allowed text-muted-foreground/50"
                          : "text-bearish hover:bg-bearish/10",
                      )}
                    >
                      삭제
                    </button>
                  </div>
                );
              })
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

function Avatar({ photoUrl, name }: { photoUrl: string | null; name: string }) {
  if (photoUrl) {
    return (
      <img
        src={photoUrl}
        alt={name}
        className="h-10 w-10 shrink-0 rounded-full object-cover"
      />
    );
  }
  return (
    <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-muted text-sm font-semibold text-muted-foreground">
      {name.slice(0, 1).toUpperCase()}
    </div>
  );
}
