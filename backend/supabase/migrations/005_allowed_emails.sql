-- Whitelist of emails permitted to authenticate via Supabase Auth
-- (Magic Link / Google OAuth). Legacy name-based login uses ALLOWED_USERS env var.
CREATE TABLE IF NOT EXISTS allowed_emails (
    email TEXT PRIMARY KEY,
    note TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Seed example (edit after applying)
-- INSERT INTO allowed_emails (email, note) VALUES ('you@example.com', 'owner');
