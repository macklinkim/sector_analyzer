-- Generalize is_ai into a category column so we can group coins beyond just AI
-- (DeFi, L2 Scaling, Meme, etc.), and add a Korean one-sentence summary column
-- to coin_news so the frontend can render localized context alongside English titles.

ALTER TABLE coin_metadata
    ADD COLUMN IF NOT EXISTS category TEXT NOT NULL DEFAULT 'major';

-- Backfill: existing AI-tagged rows become category='ai', everyone else stays 'major'.
UPDATE coin_metadata SET category = 'ai' WHERE is_ai = TRUE AND category = 'major';

CREATE INDEX IF NOT EXISTS idx_coin_metadata_category ON coin_metadata(category);

ALTER TABLE coin_news
    ADD COLUMN IF NOT EXISTS title_ko TEXT;
