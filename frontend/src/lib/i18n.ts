// frontend/src/lib/i18n.ts
// 한글 라벨 관리 — 섹터, 지수, 카테고리 등

export const SECTOR_LABELS: Record<string, string> = {
  XLF: "금융",
  XLRE: "부동산",
  XLK: "기술",
  XLY: "경기소비재",
  XLI: "산업재",
  XLB: "소재",
  XLE: "에너지",
  XLU: "유틸리티",
  XLV: "헬스케어",
  XLP: "필수소비재",
  XLC: "커뮤니케이션",
  // Communication sub-sectors
  META: "커뮤니케이션",
  GOOGL: "커뮤니케이션",
  VOX: "통신",
  // Full names
  Financials: "금융",
  "Real Estate": "부동산",
  Technology: "기술",
  "Consumer Discretionary": "경기소비재",
  Industrials: "산업재",
  Materials: "소재",
  Energy: "에너지",
  Utilities: "유틸리티",
  Healthcare: "헬스케어",
  "Consumer Staples": "필수소비재",
  Communication: "커뮤니케이션",
  "Communication Services": "커뮤니케이션",
};

export const INDEX_LABELS: Record<string, string> = {
  SPY: "S&P 500",
  QQQ: "나스닥",
  DIA: "다우존스",
  "S&P 500": "S&P 500",
  NASDAQ: "나스닥",
  DOW: "다우존스",
  KOSDAQ: "코스닥",
};

export const NEWS_CATEGORY_LABELS: Record<string, string> = {
  all: "전체",
  business: "경제",
  politics: "정치",
  society: "사회",
  world: "글로벌",
  technology: "기술",
  science: "과학",
  general: "일반",
};

export function getSectorLabel(symbolOrName: string): string {
  return SECTOR_LABELS[symbolOrName] ?? symbolOrName;
}

export function getIndexLabel(symbolOrName: string): string {
  return INDEX_LABELS[symbolOrName] ?? symbolOrName;
}

export function getCategoryLabel(category: string): string {
  return NEWS_CATEGORY_LABELS[category] ?? category;
}
