-- Crypto tab: coin metadata (from CoinGecko, refreshed daily), news (CryptoPanic),
-- and AI-generated scores. Live ticker (price/volume) is streamed to the browser
-- directly from Binance WebSocket, so there is no price cache table.

CREATE TABLE IF NOT EXISTS coin_metadata (
    coin_id TEXT PRIMARY KEY,                -- CoinGecko id (e.g. 'bitcoin', 'ethereum')
    symbol TEXT NOT NULL,                    -- lowercase symbol, feeds Binance stream name (btcusdt)
    name TEXT NOT NULL,
    market_cap NUMERIC,
    market_cap_rank INTEGER,
    image_url TEXT,
    is_ai BOOLEAN NOT NULL DEFAULT FALSE,    -- 'AI 섹터' 그룹 표기 플래그
    collected_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_coin_metadata_rank ON coin_metadata(market_cap_rank);
CREATE INDEX IF NOT EXISTS idx_coin_metadata_is_ai ON coin_metadata(is_ai);

CREATE TABLE IF NOT EXISTS coin_news (
    url TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    source TEXT,
    published_at TIMESTAMPTZ NOT NULL,
    sentiment TEXT,                          -- 'positive' | 'negative' | 'neutral' (CryptoPanic votes)
    related_coins TEXT[],                    -- array of coin_metadata.coin_id
    collected_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_coin_news_published ON coin_news(published_at DESC);

CREATE TABLE IF NOT EXISTS coin_ai_scores (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    coin_id TEXT NOT NULL REFERENCES coin_metadata(coin_id) ON DELETE CASCADE,
    ai_score NUMERIC NOT NULL,               -- -1.0 ~ +1.0
    recommendation TEXT NOT NULL,            -- 'overweight' | 'neutral' | 'underweight'
    reasoning TEXT,
    analyzed_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_coin_scores_analyzed_at ON coin_ai_scores(analyzed_at DESC);
CREATE INDEX IF NOT EXISTS idx_coin_scores_coin ON coin_ai_scores(coin_id, analyzed_at DESC);
