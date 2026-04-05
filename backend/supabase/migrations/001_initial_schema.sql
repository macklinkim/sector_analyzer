-- market_indices
CREATE TABLE IF NOT EXISTS market_indices (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    symbol TEXT NOT NULL,
    name TEXT NOT NULL,
    price DECIMAL NOT NULL,
    change_percent DECIMAL NOT NULL,
    collected_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- sectors
CREATE TABLE IF NOT EXISTS sectors (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    etf_symbol TEXT NOT NULL,
    price DECIMAL NOT NULL,
    change_percent DECIMAL NOT NULL,
    volume BIGINT NOT NULL,
    avg_volume_20d BIGINT,
    volume_change_percent DECIMAL,
    relative_strength DECIMAL,
    momentum_1w DECIMAL,
    momentum_1m DECIMAL,
    momentum_3m DECIMAL,
    momentum_6m DECIMAL,
    rs_rank INTEGER,
    collected_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- economic_indicators
CREATE TABLE IF NOT EXISTS economic_indicators (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    indicator_name TEXT NOT NULL,
    value DECIMAL NOT NULL,
    previous_value DECIMAL,
    change_direction TEXT NOT NULL,
    source TEXT NOT NULL,
    reported_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- macro_regimes
CREATE TABLE IF NOT EXISTS macro_regimes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    regime TEXT NOT NULL,
    growth_direction TEXT NOT NULL,
    inflation_direction TEXT NOT NULL,
    transition_from TEXT,
    transition_probability DECIMAL,
    regime_probabilities JSONB NOT NULL,
    indicators_snapshot JSONB,
    reasoning TEXT NOT NULL,
    batch_type TEXT NOT NULL,
    analyzed_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- sector_regime_mapping (reference table)
CREATE TABLE IF NOT EXISTS sector_regime_mapping (
    id SERIAL PRIMARY KEY,
    sector_name TEXT NOT NULL,
    sub_classification TEXT,
    etf_symbols TEXT[] NOT NULL,
    favorable_regimes TEXT[] NOT NULL,
    unfavorable_regimes TEXT[] NOT NULL,
    override_rules JSONB,
    sensitivity_factors TEXT[],
    analysis_note TEXT,
    display_order INTEGER NOT NULL
);

-- news_articles
CREATE TABLE IF NOT EXISTS news_articles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    category TEXT NOT NULL,
    title TEXT NOT NULL,
    source TEXT NOT NULL,
    url TEXT NOT NULL UNIQUE,
    summary TEXT,
    published_at TIMESTAMPTZ NOT NULL,
    collected_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- news_impact_analyses
CREATE TABLE IF NOT EXISTS news_impact_analyses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    news_id UUID REFERENCES news_articles(id),
    sector_name TEXT NOT NULL,
    impact_score DECIMAL NOT NULL,
    impact_direction TEXT NOT NULL,
    reasoning TEXT NOT NULL,
    rotation_relevance DECIMAL DEFAULT 0,
    batch_type TEXT NOT NULL,
    analyzed_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- rotation_signals
CREATE TABLE IF NOT EXISTS rotation_signals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    regime_id UUID REFERENCES macro_regimes(id),
    signal_type TEXT NOT NULL,
    from_sector TEXT,
    to_sector TEXT,
    strength DECIMAL NOT NULL,
    base_score DECIMAL,
    override_adjustment DECIMAL,
    final_score DECIMAL NOT NULL,
    reasoning TEXT NOT NULL,
    supporting_news UUID[],
    batch_type TEXT NOT NULL,
    detected_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- sector_scoreboards
CREATE TABLE IF NOT EXISTS sector_scoreboards (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    regime_id UUID REFERENCES macro_regimes(id),
    sector_name TEXT NOT NULL,
    etf_symbol TEXT NOT NULL,
    base_score DECIMAL NOT NULL,
    override_score DECIMAL NOT NULL,
    news_sentiment_score DECIMAL NOT NULL,
    momentum_score DECIMAL NOT NULL,
    final_score DECIMAL NOT NULL,
    rank INTEGER NOT NULL,
    recommendation TEXT NOT NULL,
    reasoning TEXT NOT NULL,
    batch_type TEXT NOT NULL,
    scored_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- market_reports
CREATE TABLE IF NOT EXISTS market_reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    batch_type TEXT NOT NULL,
    summary TEXT NOT NULL,
    key_highlights JSONB NOT NULL,
    report_date DATE NOT NULL,
    analyzed_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Seed data: sector_regime_mapping (12 rows)
INSERT INTO sector_regime_mapping (sector_name, sub_classification, etf_symbols, favorable_regimes, unfavorable_regimes, override_rules, sensitivity_factors, analysis_note, display_order)
VALUES
('Financials', NULL, '{XLF}', '{reflation}', '{deflation}', '{"trigger":"rate_spread_widening","action":"boost_score","description":"금리 스프레드 확대 시 가중치 부여"}', '{interest_rate,yield_spread}', '금리 인상기에 가중치 부여', 1),
('Real Estate', NULL, '{XLRE}', '{goldilocks}', '{stagflation}', '{"trigger":"rate_cut_news","action":"strong_buy_signal","description":"금리 하락 뉴스 발생 시 강한 매수 시그널"}', '{interest_rate,housing}', '금리 하락 뉴스 → 강한 매수 시그널', 2),
('Technology', NULL, '{XLK}', '{goldilocks}', '{stagflation}', '{"trigger":"real_rate_decline AND high_fcf","condition_regime":"deflation","action":"upgrade_to_defensive","description":"디플레이션이더라도 실질금리 하락 + FCF 우수 시 방어주 인식"}', '{real_rate,fcf}', '디플레이션+실질금리하락+FCF우수 → 방어주 격상', 3),
('Consumer Discretionary', NULL, '{XLY}', '{goldilocks}', '{deflation,stagflation}', NULL, '{employment,consumer_sentiment}', '고용/소비심리 지표 최민감', 4),
('Industrials', NULL, '{XLI}', '{reflation}', '{deflation}', '{"trigger":"infrastructure_spending_news","action":"boost_score","description":"인프라 투자/공급망 뉴스 가중치"}', '{infrastructure,supply_chain}', '인프라 투자 뉴스 가중치', 5),
('Materials', NULL, '{XLB}', '{reflation}', '{deflation}', '{"trigger":"commodity_price_surge","action":"boost_score","description":"원자재 가격 급등 시 가중치"}', '{copper,iron_ore,commodities}', '원자재 가격 연동', 6),
('Energy', NULL, '{XLE}', '{stagflation,reflation}', '{goldilocks,deflation}', '{"trigger":"geopolitical_risk OR inflation_sticky","action":"upgrade_to_top_defensive","description":"지정학 리스크나 인플레 고착화 시 최우선 방어주 격상"}', '{geopolitical,oil_price,inflation}', '지정학 리스크/인플레 고착화 → 최우선 방어주', 7),
('Utilities', NULL, '{XLU}', '{deflation}', '{reflation,goldilocks}', NULL, '{bond_yield,dividend_yield}', '배당수익률 vs 채권금리 비교', 8),
('Healthcare', NULL, '{XLV}', '{deflation}', '{goldilocks,reflation}', NULL, '{drug_approval,regulation}', '강세장에서 상대적 underperform', 9),
('Consumer Staples', NULL, '{XLP}', '{deflation,stagflation}', '{goldilocks,reflation}', '{"trigger":"pricing_power_positive_news","action":"boost_score","description":"가격전가력 관련 긍정 뉴스 시 가중치"}', '{pricing_power,food_prices}', '가격전가력 뉴스 가중치', 10),
('Communication', 'Media/Platform', '{META,GOOGL}', '{goldilocks}', '{stagflation,deflation}', NULL, '{ad_revenue,digital_spending}', '기술주 동일 논리 (메타, 알파벳)', 11),
('Communication', 'Telecom', '{VOX,T,VZ}', '{deflation}', '{goldilocks}', NULL, '{subscriber_growth,dividend_yield}', '유틸리티 동일 논리 (AT&T, 버라이즌)', 12);
