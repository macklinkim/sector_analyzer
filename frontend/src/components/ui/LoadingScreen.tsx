export function LoadingScreen() {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm">
      <div className="rounded-xl bg-card px-10 py-8 shadow-2xl border border-border text-center">
        <div className="mx-auto mb-4 h-10 w-10 animate-spin rounded-full border-4 border-muted-foreground/30 border-t-emerald-500" />
        <p className="text-base font-medium text-foreground">AI · 차트 정보 로딩중</p>
      </div>
    </div>
  );
}
