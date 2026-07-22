-- base_score / override_score / news_sentiment_score 필드는
-- f81c797 이후 analyst 프롬프트에서 제거되었음. NOT NULL 제약 해제.

ALTER TABLE sector_scoreboards ALTER COLUMN base_score DROP NOT NULL;
ALTER TABLE sector_scoreboards ALTER COLUMN override_score DROP NOT NULL;
ALTER TABLE sector_scoreboards ALTER COLUMN news_sentiment_score DROP NOT NULL;
