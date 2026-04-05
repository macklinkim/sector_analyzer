-- Add momentum_1y column to sectors table
ALTER TABLE sectors ADD COLUMN IF NOT EXISTS momentum_1y DECIMAL;
