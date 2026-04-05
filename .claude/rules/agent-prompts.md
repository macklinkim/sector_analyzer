# Agent Prompt Rules

## Analyst Agent System Prompt 작성 시 준수사항

1. `docs/sector-rotation-strategy.md`의 Macro Regime Matrix를 시스템 프롬프트에 반드시 포함
2. sector_regime_mapping 테이블의 override_rules를 참조 가능하도록 RAG 또는 직접 삽입
3. 4단계 판단 프로세스(Regime Detection → Base Score → Override → Reporting)를 프롬프트에 명시

## 출력 형식 강제
- Analyst Agent의 출력은 반드시 structured output (JSON)
- 점수는 -1.0 ~ +1.0 범위
- reasoning 필드에 판단 근거 반드시 포함
- 면책 조항: "본 분석은 AI의 추론이며, 실제 투자 판단의 근거로 사용할 수 없습니다"를 리포트 말미에 항상 포함

## Hallucination 방지
- 뉴스 원문에 명시되지 않은 사실을 추론하지 않도록 프롬프트에 제약 조건 추가
- "확인되지 않은 정보는 '불확실' 표기" 규칙 프롬프트에 포함
- Impact Score 산출 시 근거 뉴스 ID를 반드시 참조하도록 강제
