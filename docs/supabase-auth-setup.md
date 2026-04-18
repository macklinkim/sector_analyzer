# Supabase Auth 설정 가이드

> Magic Link + Google OAuth 동시 지원. 허가제 유지 (`allowed_emails` 테이블 기반).
> Legacy 이름-only 로그인(ALLOWED_USERS env var)은 그대로 유지 — 관리자가 수동 등록한 사용자용.

## 1. Supabase 대시보드 설정

### 1-1. Email (Magic Link) 활성화
1. Supabase Dashboard → **Authentication → Providers → Email**
2. **Enable Email Provider** ✅
3. **Confirm email** 옵션 ON (권장)
4. **Secure email change** ON (권장)
5. Magic Link 템플릿은 기본값 사용 가능 (한글 커스터마이징은 **Email Templates** 에서)

### 1-2. Google OAuth 활성화
1. [Google Cloud Console](https://console.cloud.google.com/) → 새 프로젝트
2. **APIs & Services → Credentials** → Create OAuth 2.0 Client ID
   - Application type: **Web application**
   - Authorized redirect URI:
     ```
     https://<YOUR-SUPABASE-PROJECT-REF>.supabase.co/auth/v1/callback
     ```
3. Client ID + Client Secret 복사
4. Supabase Dashboard → **Authentication → Providers → Google** → 붙여넣고 **Enable**

### 1-3. Redirect URLs (Site URL)
- **Authentication → URL Configuration**
- **Site URL:** `https://sectoranalyzerfrontend2026.kopserf.workers.dev`
- **Redirect URLs (additional):**
  - `https://sectoranalyzerfrontend2026.kopserf.workers.dev/**`
  - `http://localhost:5173/**` (로컬 개발)

### 1-4. JWT Secret 확인
- **Project Settings → API → JWT Secret** 복사 (백엔드 env로)
- **anon public** 키도 복사 (프론트엔드 env로)

## 2. 환경변수

### Backend (`.env` / Render / Railway)
```
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_SERVICE_KEY=...   # 기존, 그대로
SUPABASE_JWT_SECRET=...    # 신규: Authentication JWT Secret
ALLOWED_USERS=admin,mack   # 기존 legacy 이름 목록 유지
```

### Frontend (`frontend/.env` 또는 빌드 시 주입)
```
VITE_API_URL=https://sector-analyzer.onrender.com/api
VITE_SUPABASE_URL=https://xxx.supabase.co
VITE_SUPABASE_ANON_KEY=eyJ...  # anon public 키
```

## 3. DB 마이그레이션
```bash
# SQL Editor에서 실행
\i backend/supabase/migrations/005_allowed_emails.sql

# 허용할 이메일 등록
INSERT INTO allowed_emails (email, note) VALUES
  ('ehrd@malgnsoft.com', 'owner');
```

## 4. Cloudflare Workers 배포 시
```bash
cd frontend
VITE_API_URL=https://sector-analyzer.onrender.com/api \
VITE_SUPABASE_URL=https://xxx.supabase.co \
VITE_SUPABASE_ANON_KEY=eyJ... \
npm run build

npx wrangler deploy
```

## 5. 로그인 동작 요약

| 경로 | 입력 | 검증 | 세션 저장 |
|------|------|------|------|
| 이름 (legacy) | 이름 | ALLOWED_USERS 매칭 | sessionStorage (기존) |
| Magic Link | 이메일 | `allowed_emails` 테이블 + 이메일 링크 | localStorage (Supabase) |
| Google OAuth | Google 계정 | `allowed_emails`에 Google 이메일 등록 필요 | localStorage (Supabase) |

Supabase 세션은 **localStorage에 영구 저장** — 한 번 로그인하면 계속 유지. 토큰은 자동 refresh.
