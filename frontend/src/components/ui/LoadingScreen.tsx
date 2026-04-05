export function LoadingScreen() {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-background">
      <div className="flex flex-col items-center gap-8">
        {/* Animated Logo / Icon */}
        <div className="relative">
          {/* Outer ring */}
          <div className="h-28 w-28 animate-spin rounded-full border-4 border-muted-foreground/20 border-t-emerald-500" style={{ animationDuration: "2s" }} />
          {/* Inner pulse */}
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="animate-pulse text-4xl">📊</div>
          </div>
        </div>

        {/* Title */}
        <div className="text-center">
          <h1 className="text-2xl font-bold tracking-tight text-foreground">
            Sector Rotation Analyzer
          </h1>
          <p className="mt-2 text-sm text-muted-foreground">
            AI 분석 · Economy 정보 로딩중
          </p>
        </div>

        {/* Progress dots */}
        <div className="flex items-center gap-2">
          <div className="h-2 w-2 animate-bounce rounded-full bg-emerald-500" style={{ animationDelay: "0ms" }} />
          <div className="h-2 w-2 animate-bounce rounded-full bg-emerald-500" style={{ animationDelay: "150ms" }} />
          <div className="h-2 w-2 animate-bounce rounded-full bg-emerald-500" style={{ animationDelay: "300ms" }} />
        </div>

        {/* Status items */}
        <div className="flex flex-col items-center gap-1 text-xs text-muted-foreground">
          <span>시장 지수 · 섹터 데이터 · 뉴스 · AI 분석</span>
        </div>
      </div>
    </div>
  );
}
