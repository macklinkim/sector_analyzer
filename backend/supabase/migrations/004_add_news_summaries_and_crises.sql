-- News summaries: AI-analyzed news stored during pipeline batch
CREATE TABLE IF NOT EXISTS news_summaries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    article_url TEXT NOT NULL,
    category TEXT,
    title TEXT,
    source TEXT,
    news_category TEXT,
    summary_ko TEXT,
    impact_label TEXT,
    impact_score INT DEFAULT 0,
    related_sector TEXT,
    expert_insight TEXT,
    action_item TEXT,
    batch_type TEXT NOT NULL DEFAULT 'manual',
    analyzed_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_at TIMESTAMPTZ DEFAULT now(),
    UNIQUE(article_url)
);

-- Global crises: AI-filtered crisis headlines stored during pipeline batch
CREATE TABLE IF NOT EXISTS global_crises (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title TEXT NOT NULL,
    source TEXT,
    summary TEXT,
    impact_score INT DEFAULT 0,
    affected_sector TEXT,
    sentiment TEXT DEFAULT 'negative',
    batch_type TEXT NOT NULL DEFAULT 'manual',
    analyzed_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_news_summaries_analyzed_at ON news_summaries(analyzed_at DESC);
CREATE INDEX IF NOT EXISTS idx_global_crises_analyzed_at ON global_crises(analyzed_at DESC);
