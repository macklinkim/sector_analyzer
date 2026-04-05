# Sector Rotation Strategy Guide

본 문서는 AI 에이전트(Analyst Agent)가 시스템 프롬프트 및 RAG 데이터베이스로 활용하기 위한 섹터 순환매 전략 참조 자료입니다.

---

## 1. 거시 경제 2D 매트릭스 (Macro Regime Matrix)

기존의 '경기(Growth)' 축에 '물가/금리(Inflation/Rates)' 축을 추가하여 4가지 핵심 시장 국면(Regime)으로 분류합니다. AI는 수집한 뉴스를 바탕으로 현재 시장이 어느 사분면에 위치하는지 먼저 파악합니다.

| 국면 (Regime) | 경제 성장 (Growth) | 물가/금리 (Inflation) | 시장 특징 | 주도 섹터 (수혜주) |
| :--- | :---: | :---: | :--- | :--- |
| **골디락스 (Goldilocks)** | 상승 (High) | 하락/안정 (Low) | 완벽한 강세장, 위험자산 선호 | 기술주, 임의소비재, 통신(미디어) |
| **리플레이션 (Reflation)** | 상승 (High) | 상승 (High) | 경기 과열, 원자재 수요 급증 | 산업재, 소재, 금융 |
| **스태그플레이션 (Stagflation)** | 하락 (Low) | 상승 (High) | 비용 상승, 이익 둔화, 최악의 장 | **에너지**, 필수소비재 |
| **디플레이션 (Deflation)** | 하락 (Low) | 하락 (Low) | 경기 침체, 안전자산 선호 | **헬스케어**, 유틸리티, 통신(인프라) |

### 국면 전환 패턴 (Typical Regime Transitions)

```
Goldilocks ──(물가 상승)──▶ Reflation
     ▲                          │
     │                    (성장 둔화)
 (금리 인하,                     ▼
  경기 회복)              Stagflation
     │                          │
Deflation ◀──(물가 안정)───────┘
```

---

## 2. 고도화된 섹터 매핑 테이블 (Advanced Sector Mapping)

단순한 1대1 매핑을 넘어, 세부 그룹(Sub-industry) 분리와 예외 상황(Override)을 추가한 데이터 구조입니다.

| ID | 대분류 섹터 | 세부 분류 (필요시) | 유리한 국면 (강세) | 불리한 국면 (약세) | AI 분석 시 특별 예외/가중치 규칙 (Override Rules) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | Financials | - | Reflation | Deflation | 금리 인상기(금리 스프레드 확대)에 가중치 부여 |
| 2 | Real Estate | - | Goldilocks | Stagflation | 금리 하락 뉴스 발생 시 강한 매수 시그널로 인식 |
| 3 | Technology | - | Goldilocks | Stagflation | **[예외]** 디플레이션 국면이더라도 '실질 금리 하락' 및 '잉여현금흐름(FCF) 우수' 뉴스가 감지되면 방어주로 인식하여 점수 상향 |
| 4 | Consumer Discretionary | - | Goldilocks | Deflation, Stagflation | 고용 지표 및 소비 심리 데이터에 가장 민감하게 반응 |
| 5 | Industrials | - | Reflation | Deflation | 정부 인프라 투자 및 공급망 관련 뉴스에 가중치 |
| 6 | Materials | - | Reflation | Deflation | 글로벌 원자재 가격(구리, 철광석 등) 지표와 연동 |
| 7 | Energy | - | **Stagflation**, Reflation | Goldilocks, Deflation | **[예외]** 성장이 둔화되어도 '지정학적 리스크'나 '인플레이션 고착화' 뉴스 발생 시 최우선 방어주로 격상 |
| 8 | Utilities | - | Deflation | Reflation, Goldilocks | 배당 수익률 대비 채권 금리가 매력적일 때 불리함 |
| 9 | Healthcare | - | Deflation | **Goldilocks, Reflation** | **[수정]** 강세장(성장 가속, 위험 선호)에서는 상대적 수익률 저조(Underperform) 반영 |
| 10 | Consumer Staples | - | Deflation, Stagflation | Goldilocks, Reflation | 가격 전가력(Pricing Power) 관련 긍정 뉴스 시 가중치 |
| 11-A | **Communication** | **Media/Platform** (성장) | Goldilocks | Stagflation, Deflation | **[분리]** 메타, 알파벳 등은 기술주(임의소비재)와 동일한 논리로 분석 |
| 11-B | **Communication** | **Telecom** (방어/인프라) | Deflation | Goldilocks | **[분리]** AT&T, 버라이즌 등은 유틸리티와 동일한 논리로 분석 |

### 대표 ETF 매핑

| 섹터 | ETF Symbol | 비고 |
| :--- | :--- | :--- |
| Financials | XLF | |
| Real Estate | XLRE | |
| Technology | XLK | |
| Consumer Discretionary | XLY | |
| Industrials | XLI | |
| Materials | XLB | |
| Energy | XLE | |
| Utilities | XLU | |
| Healthcare | XLV | |
| Consumer Staples | XLP | |
| Communication (Media) | META, GOOGL | 개별 종목 추적 |
| Communication (Telecom) | VOX 또는 T, VZ | 개별 종목 추적 |

---

## 3. AI 에이전트(Analyst Agent) 판단 로직 플로우

위의 데이터를 기반으로 Analyst Agent가 작동하는 4단계 판단 프로세스입니다.

### Step 1: 매크로 환경 설정 (Macro Regime Detection)

News Agent가 가져온 거시 경제 뉴스(CPI, FED 금리 결정, GDP 성장률 등)를 분석하여 현재 매트릭스 상의 위치를 확률(%)로 추론합니다.

**입력:** 경제 지표 데이터 + 거시 경제 뉴스
**출력:** 4개 국면별 확률 분포 + 전환기 판단

```
예시 출력:
{
  "current_regime": "goldilocks",
  "probabilities": {
    "goldilocks": 0.60,
    "reflation": 0.25,
    "stagflation": 0.10,
    "deflation": 0.05
  },
  "transition": "goldilocks → reflation 전환 가능성 25%",
  "key_signals": ["CPI 상승세 지속", "PMI 확장 유지", "연준 매파적 발언"]
}
```

### Step 2: 기본 점수 할당 (Base Score Calculation)

매핑 테이블의 '유리/불리 국면'을 바탕으로 12개 섹터(11-A, 11-B 분리)의 기본 모멘텀 점수(Base Score)를 계산합니다.

**로직:**
- favorable_regimes 매칭 → 양(+)의 기본 점수
- unfavorable_regimes 매칭 → 음(-)의 기본 점수
- 전환 확률에 따라 다음 국면의 유/불리도 가중 반영

### Step 3: 가중치 보정 (Override Adjustment)

개별 섹터나 기업 뉴스를 분석하여 '특별 예외 규칙'이 발동하는지 확인합니다.

**예시:**
- "물가는 오르는데 애플이 자사주 매입을 발표했다" → Technology 점수 보정
- "중동 지정학 긴장 고조" + Stagflation 국면 → Energy 최우선 방어주 격상
- "연준 금리 인하 시사" → Real Estate 강한 매수 시그널

### Step 4: 최종 리포팅 (Scoring & Reporting)

점수가 가장 높은 섹터와 가장 낮은 섹터를 선정하고, 논리적 근거를 텍스트로 요약합니다.

**출력:**
- **Top 3 Overweight 섹터** + 투자 근거
- **Bottom 3 Underweight 섹터** + 회피 근거
- **로테이션 방향 시그널** (자금 이동 방향)
- **종합 시장 브리핑** (전체 요약)

---

## 4. 점수 산출 공식 (Scoring Formula)

```
Final Score = (Base Score × Regime Confidence)
            + (Override Adjustment)
            + (News Sentiment Score × 0.2)
            + (Technical Momentum Score × 0.15)

여기서:
- Base Score: 국면 매핑 기반 (-1.0 ~ +1.0)
- Regime Confidence: 현재 국면 확률 (0 ~ 1.0)
- Override Adjustment: 예외 규칙 보정 (-0.5 ~ +0.5)
- News Sentiment: 해당 섹터 관련 뉴스 감성 (-1.0 ~ +1.0)
- Technical Momentum: 상대강도 + 거래량 변화 기반 (-1.0 ~ +1.0)
```

### Recommendation 기준

| Final Score 범위 | 추천 등급 |
| :--- | :--- |
| +0.5 이상 | **Overweight** (비중 확대) |
| -0.2 ~ +0.5 | **Neutral** (중립) |
| -0.2 미만 | **Underweight** (비중 축소) |
