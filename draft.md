# Product Requirements Document (PRD): AI-Driven Market Insights Dashboard

## 1. 프로젝트 목적 (Purpose)
- **핵심 목표:** AI Agent 기술의 실전 적용 및 심화 활용 능력 배양
- **비즈니스 목표:** 분산된 금융 데이터(EODHD)와 실시간 뉴스 데이터(NewsAPI)를 AI 에이전트 파이프라인을 통해 분석하고, 인사이트가 담긴 종합 미국 주식 시장 대시보드 구축

## 2. 핵심 주제 및 기능 (Key Features)
1. **섹터별 시장 분석 요약:** EODHD API 데이터를 기반으로 미국 주식 시장의 섹터별 추세, 가격 변동성, 주요 주목 포인트를 자동 요약.
2. **뉴스 기반 섹터 영향 예측:** - 정치, 경제, 사회, 글로벌 4개 분야에서 각 3개의 주요 미국 뉴스를 선정.
   - 해당 뉴스가 특정 주식 섹터에 미칠 잠재적 영향을 AI가 추론하여 리포팅.
3. **금융 데이터 시각화:** 대형 금융/주식 포털의 핵심 차트 및 데이터 표현 방식을 벤치마킹하여 직관적이고 전문적인 웹 대시보드 뷰 제공.

## 3. AI 기술 활용 가이드라인 (AI Technology Utilization Guide)
본 프로젝트는 다음의 AI 기술들을 프로젝트 라이프사이클 전반에 걸쳐 최대한 활용합니다.

| 기술 요소 | 활용 단계 및 가이드라인 |
| :--- | :--- |
| **Claude Excalidraw Diagram generator** | **[기획/설계]** 프로젝트 초기 데이터 플로우, LangGraph/CrewAI의 에이전트 노드 아키텍처, 데이터베이스 ERD 등을 시각화하여 문서화. |
| **Claude Vision** | **[설계/UI]** 모방하고자 하는 거대 주식 사이트의 복잡한 차트나 대시보드 화면을 캡처하여 Vision으로 분석, UI 구조와 핵심 데이터 포인트를 추출. |
| **Claude Artifacts & Frontend design skill** | **[프로토타이핑]** 프론트엔드 개발 전, Artifacts를 활용해 추출된 UI 구조를 기반으로 React(또는 Next.js) + Tailwind CSS 컴포넌트를 빠르게 시뮬레이션 및 검증. |
| **Claude harness** | **[백엔드/테스트]** 에이전트가 뉴스 원문을 분석하고 섹터 영향을 평가할 때, 프롬프트의 일관성과 품질을 평가하고 최적화하는 테스트 베드로 활용. |
| **LangGraph / CrewAI** | **[백엔드/코어]** 다중 에이전트 워크플로우 구축. <br> - *Data Agent:* EODHD API 호출 및 정제 <br> - *News Agent:* NewsAPI를 통한 분야별 뉴스 수집 및 필터링 <br> - *Analyst Agent:* 데이터와 뉴스를 융합하여 영향력 분석 |
| **NewsAPI & Fetch MCP** | **[에이전트 도구]** News Agent의 핵심 도구로 통합. <br> 1. 커스텀 MCP 서버로 래핑한 **NewsAPI.org**를 호출하여 카테고리별 주요 헤드라인과 URL을 수집. <br> 2. Anthropic 공식 **fetch MCP**를 사용해 뉴스 원문 웹페이지를 마크다운으로 변환하여 AI가 깊이 있게 문맥을 분석하도록 지원. |
| **Google Workspace** | **[인프라/알림]** 에이전트가 생성한 최종 리포트를 Google Sheets API를 통해 누적 저장하고, 매일 장 시작 전 요약된 마켓 브리핑을 Gmail API를 통해 자동 발송. |

## 4. 기술 스택 (Tech Stack)
*유지보수성과 빠른 개발을 고려하여 구성된 추천 스택입니다.*

- **Backend & AI Pipeline:** - Python, FastAPI (클라이언트와의 빠르고 비동기적인 통신)
  - LangGraph 또는 CrewAI (에이전트 오케스트레이션 프레임워크)
  - LangChain (프롬프트 체인 및 도구 통합)
- **Frontend:** - Next.js (서버 사이드 렌더링 및 SEO, 빠른 로딩)
  - shadcn/ui & Tailwind CSS (빠르고 유연한 대시보드 UI 구성)
  - Recharts 또는 Chart.js (복잡한 금융 데이터 시각화)
- **Data & API:** - **EODHD API:** 주식 시장 및 섹터 데이터
  - **NewsAPI.org:** 주력 뉴스 데이터 소스 (정치/경제/사회/글로벌 카테고리 필터링 및 주요 매체 통합 조회)
  - **Google News RSS (`feedparser`):** NewsAPI 일일 한도(100 req) 소진 시 대비용 무료 Fallback 플랜
  - Supabase 또는 PostgreSQL (과거 분석 데이터 및 뉴스 히스토리 저장)

## 5. 화면 구성 (Screen Composition)
대시보드는 한눈에 시장 상황을 파악할 수 있는 단일 페이지 애플리케이션(SPA) 구조를 지향합니다.

1. **Global Header (상단):**
   - S&P 500, NASDAQ, DOW 등 주요 지수 실시간 티커.
   - 마지막 데이터 갱신 시간 및 AI 분석 상태 표시.
2. **Sector Heatmap & Trends (좌측 영역):**
   - EODHD 데이터를 활용한 섹터별 등락률 히트맵 (Tree map 또는 Grid 형태).
   - 선택된 섹터의 단기 추세 요약 텍스트 (AI 생성).
3. **News Impact Radar (우측 영역):**
   - 정치/경제/사회/글로벌 탭으로 구성된 주요 뉴스 피드.
   - 각 뉴스 아이템 클릭 시, 하단에 해당 뉴스가 특정 섹터에 미치는 'AI 예측 파급력(Impact Score)'과 근거 표시.
4. **Deep Dive Chart (하단 영역):**
   - 거대 주식 사이트를 모방한 인터랙티브 차트.
   - 가격 차트 위에 AI가 분석한 주요 뉴스 발생 시점을 마커(Marker)로 표시하여 인과관계 시각화.

## 6. 디자인 가이드 (Design Guide)
- **테마 (Theme):** 금융/개발자 친화적인 **Dark Mode** 기본 적용 (장시간 화면을 보는 유저의 피로도 감소).
- **색상 팔레트 (Color Palette):**
  - 상승(Bullish): 선명한 Green (예: `#22c55e`)
  - 하락(Bearish): 선명한 Red (예: `#ef4444`)
  - 배경: 딥 그레이/블랙 계열 (`#0f172a` 등)
  - 텍스트: 가독성이 높은 화이트 및 밝은 그레이.
- **UI/UX 원칙:** - 정보의 위계질서를 명확히 하기 위해 카드(Card) 레이아웃 사용.
  - 데이터 로딩 및 AI 분석 중일 때는 스켈레톤 UI(Skeleton UI)와 함께 'AI가 분석 중입니다...' 와 같은 진행 상태를 직관적으로 표시.

## 7. 제약사항 (Constraints & Limitations)
- **API Rate Limits:** - NewsAPI.org의 개발자 무료 플랜 한도(1일 100회)를 고려하여, 주기적 배치(Batch) 수집 후 DB에 캐싱하는 전략 필수. 장애 시 Google News RSS로 우회 처리.
  - EODHD 및 AI 모델 API의 호출 횟수/토큰 제한 관리.
- **AI Hallucination (환각 현상):** 에이전트가 뉴스와 섹터 간의 연관성을 억지로 지어내거나 잘못된 인과관계를 생성할 위험이 있음. (Harness를 통한 프롬프트 튜닝으로 완화 필요)
- **실시간성 지연 (Latency):** 여러 에이전트가 순차적/병렬적으로 사고하고 도구를 사용하는 과정에서 최종 리포트 생성까지 수 분이 소요될 수 있음. 실시간 렌더링보다는 배치(Batch) 처리 후 결과물 제공 방식 고려.
- **재정적 책임 고지:** 생성된 예측 데이터는 AI의 추론일 뿐, 실제 투자 지표로 사용될 수 없다는 면책 조항(Disclaimer) 명시 필수.