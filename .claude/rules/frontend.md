# Frontend Rules

## TypeScript
- strict mode 필수
- `any` 타입 사용 금지, 공유 타입은 `src/types/index.ts`에 정의
- 서버/클라이언트 컴포넌트 구분 명확히 ("use client" 필요 시에만)

## Next.js
- App Router 사용 (pages router 금지)
- 서버 컴포넌트 우선, 클라이언트 컴포넌트는 인터랙션 필요 시에만
- 데이터 페칭은 서버 컴포넌트에서 fetch() 사용
- API 클라이언트는 `src/lib/api.ts`에 중앙화

## UI/Styling
- shadcn/ui 컴포넌트 우선 사용
- Tailwind CSS만 사용 (인라인 스타일, CSS 모듈 금지)
- Dark Mode 기본 (bg-slate-900 계열)
- 색상: 상승 green-500, 하락 red-500, 배경 slate-900

## Charts
- Recharts 사용 (Treemap, BarChart, AreaChart 등)
- 반응형 컨테이너(ResponsiveContainer) 필수

## Design Tokens
- 국면 색상: Goldilocks green-500, Reflation amber-500, Stagflation red-500, Deflation blue-500
