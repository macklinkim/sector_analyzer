import { useEffect } from "react";

interface AvatarLightboxProps {
  open: boolean;
  onClose: () => void;
  identity: string;
  photoUrl: string | null;
  isAdmin?: boolean;
  onOpenAdmin?: () => void;
}

export function AvatarLightbox({
  open,
  onClose,
  identity,
  photoUrl,
  isAdmin,
  onOpenAdmin,
}: AvatarLightboxProps) {
  useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open, onClose]);

  if (!open) return null;

  const backdropClick = (e: React.MouseEvent<HTMLDivElement>) => {
    if (e.target === e.currentTarget) onClose();
  };

  return (
    <div
      onClick={backdropClick}
      className="fixed inset-0 z-50 flex flex-col items-center justify-center gap-4 bg-black/85 p-6 backdrop-blur-sm"
    >
      <button
        type="button"
        onClick={onClose}
        aria-label="닫기"
        className="absolute right-4 top-4 rounded-full bg-white/10 px-3 py-1 text-sm text-white/80 backdrop-blur hover:bg-white/20"
      >
        ✕
      </button>

      {photoUrl ? (
        <img
          src={photoUrl}
          alt={identity}
          className="max-h-[80vh] max-w-[90vw] rounded-xl object-contain shadow-2xl"
        />
      ) : (
        <div className="flex h-48 w-48 items-center justify-center rounded-full bg-muted text-6xl font-bold text-muted-foreground sm:h-64 sm:w-64 sm:text-8xl">
          {identity.slice(0, 1).toUpperCase()}
        </div>
      )}

      <p className="text-sm font-medium text-white/90">{identity}</p>

      {isAdmin && onOpenAdmin && (
        <button
          type="button"
          onClick={() => {
            onOpenAdmin();
            onClose();
          }}
          className="rounded-lg border border-white/20 bg-white/10 px-4 py-2 text-sm font-medium text-white backdrop-blur transition-colors hover:bg-white/20"
        >
          사용자 관리
        </button>
      )}
    </div>
  );
}
