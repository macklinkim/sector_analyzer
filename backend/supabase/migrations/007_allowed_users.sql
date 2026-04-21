-- Dynamic whitelist for legacy name-based login. Replaces the static ALLOWED_USERS env var
-- (env is still honored as a seed fallback in app code). Each row optionally carries a
-- public avatar URL — the frontend displays it next to the dashboard tab bar and as a
-- mobile login splash screen.
CREATE TABLE IF NOT EXISTS allowed_users (
    name TEXT PRIMARY KEY,
    photo_url TEXT,
    added_by TEXT,
    added_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Avatars are served through Supabase Storage. Create a public bucket so the frontend can
-- load images via the returned public URL without requiring a signed request.
INSERT INTO storage.buckets (id, name, public)
VALUES ('user-avatars', 'user-avatars', true)
ON CONFLICT (id) DO UPDATE SET public = true;

-- Writes are performed by the backend with the service role key, so we intentionally
-- do not grant anon insert/update. Public read is implied by the bucket being public.
