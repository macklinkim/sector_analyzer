-- Add 52-week range columns to sectors table
ALTER TABLE sectors ADD COLUMN IF NOT EXISTS week_52_low DECIMAL;
ALTER TABLE sectors ADD COLUMN IF NOT EXISTS week_52_high DECIMAL;
