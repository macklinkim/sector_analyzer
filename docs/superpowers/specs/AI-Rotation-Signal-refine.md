# [Logic Refactoring] AI Rotation Signal 고도화 — v2

## 1. 현재 문제점 종합 (2026-04-07 기준)

### 1.1 신호 과잉 (Signal Noise)
- **증상:** 하루에 10건의 "Regime Shift" 동시 발생, 거의 모든 섹터 대상
- **원인:** Claude AI에게 엄격한 필터링을 요구하지만, 사전 필터(Step 2)의 임계값이 낮아(score ≥ 0.2) 대부분의 섹터가 후보로 올라감
- **해결:** 사전 필터 임계값 상향 + AI 후처리에서 최대 3개 시그널로 제한 + regime_shift는 confidence ≥ 0.7만 허용

### 1.2 확신도(Confidence Score) 고착화 (50%)
- **증상:** DB에 confidence_score 컬럼이 없어 기본값 0.5로 저장됨
- **근본 원인:** DB 스키마 불일치 (signal_grade, macro_environment, confidence_score 컬럼 누락)
- **해결:** DB 컬럼 추가 완료 (2026-04-07). 다음 배치부터 AI가 산출한 실제 확신도 저장

### 1.3 매크로 논리 부재 & 자금 흐름 비일관성
- **증상:** XLK underweight인데 동시에 산업재, 필수소비재에도 Watch 신호 → "돈이 어디서 어디로 가는지" 불명확
- **원인:** 각 섹터를 독립적으로 평가할 뿐, 섹터 간 자금 이동 방향성(Flow of Funds)을 추론하지 않음
- **해결:** 프롬프트에 "자금 유입 vs 유출 섹터를 명시하라" 강제 + rotate_in/rotate_out 쌍으로만 시그널 생성

### 1.4 인과관계 단순화
- **증상:** "지정학적 리스크 → 에너지" 수준의 1차원 매핑
- **원인:** 뉴스 텍스트만으로 섹터를 매핑하며, 금리/환율/유가 등 수치 지표와의 교차 검증 없음
- **해결:** Step 3 프롬프트에 경제 지표 수치를 명시적으로 전달 + "지표값이 뒷받침하지 않으면 뉴스 기반 신호 제외" 규칙

### 1.5 데이터 중복 (Scoreboard)
- **증상:** 동일 섹터(XLU, XLV)가 랭킹에 2번 노출
- **원인:** `get_latest_scoreboards`가 batch_type 없이 최근 12건 가져오면서 이전 배치 데이터와 혼재
- **해결:** 프론트엔드에서 etf_symbol 기준 dedup 또는 API에서 가장 최근 batch만 반환

---

## 2. 개선 설계

### 2.1 사전 필터 강화 (analyst_agent.py — Step 2)

```
현재: score ≥ 0.2 → 후보 통과
개선: score ≥ 0.4 → 후보 통과 (top_candidates 임계값 상향)
```

**추가 필터:**
- regime_shift 타입: RS Golden Cross + 매크로 일치 + score ≥ 0.5 필수
- 동일 signal_type으로 3개 이상 섹터가 동시 통과 시 → 상위 2개만 유지

### 2.2 교차 검증 (Cross-Validation) 도입

뉴스 센티먼트 vs 가격 모멘텀 불일치 감지:

| 뉴스 센티먼트 | 모멘텀 방향 | 판정 |
|---|---|---|
| 긍정 | 상승 | 정상 — 시그널 유지 |
| 긍정 | 하락 | **Divergence** — 시그널 억제, "센티먼트-가격 괴리" 경고 |
| 부정 | 상승 | **Contrarian** — 시그널 유지, 단 confidence 0.1 감점 |
| 부정 | 하락 | 정상 — rotate_out 시그널 |

→ 이 로직을 Step 2.5로 추가 (rule-based, AI 호출 전)

### 2.3 자금 흐름 일관성 강제 (프롬프트 개선)

AI 프롬프트에 추가할 규칙:
```
## 자금 흐름 일관성 규칙
- rotate_in 시그널을 생성할 때, 반드시 대응하는 rotate_out 섹터를 명시하라
- "어디서 빠져서 어디로 들어가는가"를 한 문장으로 요약하라
- 3개 이상 섹터가 동시에 rotate_in이면 → 가장 강한 2개만 남기고 나머지 제거
- regime_shift는 배치당 최대 1건만 허용
```

### 2.4 다변수 분석 컨텍스트 (프롬프트 개선)

현재: "Gold: up, US10Y: down" (방향만)
개선: "Gold: $3,320 (+1.2% 1W), US10Y: 4.05% (-15bp 1W)" (수치 포함)

→ `classify_macro_environment()`에서 수치값도 반환하도록 수정
→ 프롬프트에 "이 수치가 해당 섹터 밸류에이션에 미치는 영향을 정량적으로 설명하라" 추가

### 2.5 Scoreboard 중복 제거

**백엔드:**
```python
# get_latest_scoreboards — 가장 최근 batch의 scored_at 기준으로만 조회
def get_latest_scoreboards(self) -> list[dict]:
    latest = self.client.table("sector_scoreboards") \
        .select("scored_at").order("scored_at", desc=True).limit(1).execute()
    if not latest.data:
        return []
    latest_ts = latest.data[0]["scored_at"]
    return self.client.table("sector_scoreboards") \
        .select("*").eq("scored_at", latest_ts) \
        .order("rank").execute().data
```

**프론트엔드 fallback:**
- `etf_symbol` 기준 dedup (같은 ETF가 2번 나오면 최신만 유지)

---

## 3. 후처리 강화 (analyst_agent.py — Step 3 이후)

```python
# 현재
signals = [s for s in signals if float(s.get("confidence_score", 0)) >= 0.3]
signals = signals[:5]

# 개선
signals = [s for s in signals if float(s.get("confidence_score", 0)) >= 0.3]

# regime_shift는 confidence ≥ 0.7만 허용
signals = [
    s for s in signals
    if s.get("signal_type") != "regime_shift" or float(s.get("confidence_score", 0)) >= 0.7
]

# 최대 3개로 제한 (5 → 3)
signals = signals[:3]

# regime_shift는 배치당 1건만
regime_shifts = [s for s in signals if s.get("signal_type") == "regime_shift"]
if len(regime_shifts) > 1:
    signals = [s for s in signals if s.get("signal_type") != "regime_shift"]
    signals.insert(0, regime_shifts[0])
    signals = signals[:3]
```

---

## 4. 구현 우선순위

| # | 작업 | 난이도 | 영향도 | 비고 |
|---|---|---|---|---|
| 1 | DB 스키마 수정 (signal_grade, confidence_score 등) | ✅ 완료 | 높음 | 2026-04-07 적용 |
| 2 | 후처리 강화 (시그널 3개 제한, regime_shift 1건 제한) | 낮음 | 높음 | 코드 10줄 |
| 3 | Scoreboard 중복 제거 | 낮음 | 중간 | API 쿼리 수정 |
| 4 | 사전 필터 임계값 상향 (0.2 → 0.4) | 낮음 | 중간 | 상수 1개 변경 |
| 5 | 교차 검증 (센티먼트-모멘텀 괴리 감지) | 중간 | 높음 | Step 2.5 신규 |
| 6 | 프롬프트 개선 (자금 흐름 일관성, 다변수 분석) | 중간 | 높음 | 프롬프트 텍스트 |
| 7 | 매크로 지표 수치 전달 | 낮음 | 중간 | classify_macro 수정 |

---

## 5. 참고: 이전 3-Step Validation 설계 (유지)

### Step 1: Macro Environment Check
- 금리(US10Y), 달러(DXY), 유가(WTI), 금(Gold) 방향성 → Risk-On/Off/Inflationary/Deflationary 분류
- **개선:** 방향성뿐 아니라 수치와 변화폭도 전달

### Step 2: RS & Momentum Pre-filter
- RS > 2% 또는 Golden Cross + 모멘텀 정렬
- **개선:** 임계값 상향 + 교차 검증 추가

### Step 3: Claude AI Final Analysis
- 모든 컨텍스트를 종합하여 시그널 생성
- **개선:** 자금 흐름 일관성 강제 + 다변수 분석 요구 + regime_shift 엄격 제한
