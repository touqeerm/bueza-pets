# Bueza Pets

Livestock teleconsultation for farmers. A Next.js frontend and a FastAPI backend, talking over HTTP, backed by Postgres.

## Contents

- [Architecture](#architecture)
- [Local setup](#local-setup)
- [Deployment](#deployment)
- [Technical debt & known limitations](#technical-debt--known-limitations)
- [Roadmap](#roadmap)

## Architecture

Two independently deployed services:

```
frontend/   Next.js 16 (App Router), TypeScript, Tailwind
backend/    FastAPI, SQLAlchemy (async), Postgres
```

### Frontend

- **Routing & i18n**: pages live under `src/app/[locale]/`. Locale (`en`, `hi`, `kn`, `te`, `ta`) is resolved by `next-intl` via `src/proxy.ts` (Next's routing middleware) and persisted in a `NEXT_LOCALE` cookie. `src/i18n/` holds the routing config, navigation helpers (locale-aware `Link`/`useRouter`), and per-locale display names. Translation strings live in `frontend/messages/<locale>.json`.
- **User flow**: splash (`/`) → language picker → login (phone + mock OTP) → home → describe-problem (placeholder).
- **Backend-for-frontend (BFF)**: the browser never calls the FastAPI backend directly. Route handlers under `src/app/api/*` proxy to it server-side. This does two things: avoids needing CORS on the backend, and lets the session token be set as an `HttpOnly` cookie that client-side JS never touches (`api/auth/otp/verify` sets it; `api/auth/me` and `api/auth/logout` read it).
- **Analytics**: `src/lib/analytics.ts` exports `trackEvent(name, properties?, userId?)`, a fire-and-forget call to `api/analytics/events`, which is itself a thin BFF proxy that also owns a persistent `analytics_id` cookie (created once, reused after) so a user's pre-login and post-login events can be correlated even before they have an account.

### Backend

Clean Architecture, dependencies point inward:

```
domain/          Entities and business rules. No framework imports.
application/     Use cases + repository interfaces (ports). Orchestrates domain
                 logic; knows nothing about FastAPI or SQLAlchemy.
infrastructure/  SQLAlchemy models and concrete repository implementations
                 (the "adapters" for the ports defined in application/).
presentation/    FastAPI routers, Pydantic schemas, dependency-injection wiring.
```

Why: business rules (OTP expiry, session lifetime, user get-or-create) live in `application/use_cases/` and don't import FastAPI or SQLAlchemy at all — they depend only on the `Protocol` interfaces in `application/interfaces/`. The concrete SQLAlchemy implementation is injected at the `presentation/dependencies.py` layer. This means the business logic is independently testable and the persistence layer is swappable in principle (see [Technical debt](#technical-debt--known-limitations) for the honest caveat: nothing currently exercises that swap).

- **Auth**: mock OTP (no SMS gateway — the code is returned directly in the `/auth/otp/request` response so the flow is testable end to end). Sessions are opaque bearer tokens stored server-side in a `sessions` table (not JWT), 30-day expiry.
- **Analytics**: one generic `POST /analytics/events` endpoint. Valid event names are a closed set (`app.domain.events.EventName`), enforced by Pydantic — an unrecognized name gets a `422` listing the valid ones. Adding a new trackable event is one enum line plus one `trackEvent()` call on the frontend; no new endpoint.
- **Database**: tables are created via `Base.metadata.create_all()` on startup (see [Technical debt](#technical-debt--known-limitations) — there's no migration tool yet).

### Deployment topology

- **Backend**: Docker Compose (`docker-compose.yml` at repo root) — `api` + `db` (Postgres 16). Only `api` is published to the host; Postgres is internal-only to the Docker network.
- **Frontend**: runs directly on the host via systemd (`npm run start`), not containerized. This was the pragmatic choice made when it was first deployed, not a deliberate architectural stance — see [Roadmap](#roadmap).

## Local setup

Prerequisites: Node 20+, Python 3.12+, and either Docker (recommended) or a local Postgres instance.

### Backend

Easiest path — the whole backend plus Postgres via Docker Compose, from the repo root:

```bash
docker compose up -d --build
curl http://localhost:8000/health   # {"status":"ok","database_connected":true}
```

Without Docker: `cd backend && pip install -r requirements.txt`, run Postgres yourself, copy `.env.example` to `.env` and point `DATABASE_URL` at it, then `uvicorn app.main:app --reload`.

### Frontend

```bash
cd frontend
cp .env.example .env
npm install
npm run dev
```

Runs on `http://localhost:3000`. `BACKEND_API_URL` in `.env` (defaults to `http://localhost:8000`) needs to point at a running backend for login and analytics to work — language switching and static pages work without it.

### Full local loop

1. `docker compose up -d --build` (backend + db)
2. `cd frontend && npm install && npm run dev`
3. Visit `http://localhost:3000` — splash → language → login (the OTP code is shown directly in the UI, since there's no real SMS gateway) → home

## Deployment

Deployment today is manual, to a single shared host. Described here in reproducible terms rather than host-specific ones — see the operational notes wherever this repo is actually checked out for exact port numbers and shared-host caveats.

### Backend

```bash
git pull
docker compose up -d --build
```

Rebuilds and restarts the `api` container. Postgres data persists in a named volume across restarts.

### Frontend

```bash
cd frontend
git pull   # if not already up to date
npm run build
sudo systemctl restart bueza-pets-frontend
```

The systemd unit runs `npm run start` from `frontend/`, is `enable`d (survives reboots), and restarts automatically on crash (`Restart=always`). Check status with `systemctl status bueza-pets-frontend` / logs with `journalctl -u bueza-pets-frontend -f`.

### Environment variables

| Variable | Service | Purpose |
|---|---|---|
| `DATABASE_URL` | backend | Postgres connection string |
| `BACKEND_API_URL` | frontend | Where the frontend's BFF routes proxy requests to |
| `COOKIE_SECURE` | frontend | Set `true` once HTTPS is in front of the app (see below) |

**No TLS is configured yet.** `COOKIE_SECURE` is deliberately left `false` for this reason — a `Secure` cookie set over plain HTTP is silently dropped by real browsers, which would break login. Put a reverse proxy (nginx/Caddy) with a real certificate in front of both services, then flip `COOKIE_SECURE=true`, before this is exposed beyond internal testing.

## Technical debt & known limitations

Things that work today but carry a known, conscious tradeoff:

- **No automated tests.** Neither backend (pytest) nor frontend (Vitest/Playwright) has a test suite yet. Verification so far has been manual — curl scripts, Lighthouse, and direct browser checks against scratch environments. Fine at the current pace; a real gap as surface area grows.
- **No database migrations.** `Base.metadata.create_all()` only creates missing tables — it cannot alter an existing one. The first schema change to a table holding real data needs Alembic (or equivalent) introduced *before* it's safe to deploy.
- **Mock OTP returns the code directly in the API response.** Necessary today since there's no SMS gateway. This must be gated behind an environment check (or removed outright) before any real SMS integration — otherwise it's an authentication bypass.
- **No rate limiting** on `/auth/otp/request`. Harmless today since nothing is actually sent, but would need addressing before real SMS delivery (cost and abuse).
- **`otp_codes` and `sessions` rows are never cleaned up.** Expired/consumed rows accumulate forever. Not urgent at current scale; needs a scheduled cleanup eventually.
- **Repository interfaces have exactly one implementation each** (e.g. `UserRepository` → `SqlAlchemyUserRepository`). This is a conscious tradeoff from the decision to use Clean Architecture, not an oversight — the seam exists for future flexibility (swapping persistence, substituting fakes once a test suite exists), but nothing exercises the swap today. One instance of this pattern *was* pure ceremony with zero business logic behind it — the health-check feature (`HealthRepository` interface + use case wrapping a single `SELECT 1`) — and was collapsed into the endpoint directly as part of this review. The auth/analytics repositories were kept as-is since they hold real domain logic (OTP validation, session expiry, user get-or-create).
- **Asymmetric deployment.** Backend is containerized, frontend runs directly on the host via systemd. Pragmatic at the time, not a deliberate stance.
- **Fully manual deployment**, no CI/CD. Every release is a hand-run sequence (see [Deployment](#deployment)). Fine solo; a drift risk the moment more than one person deploys.
- **No CORS configuration on the backend** — not currently needed since the frontend's BFF routes proxy server-side, but relevant if anything ever needs the browser to call the backend directly.

## Roadmap

Roughly in the order they'd likely become necessary:

1. Real SMS gateway (Twilio, MSG91, etc.) to replace mock OTP, gated per environment
2. TLS/reverse proxy in front of both services; flip `COOKIE_SECURE=true`
3. Automated tests — pytest for backend use cases/repositories, Vitest/Playwright for the frontend
4. Alembic migrations, replacing `create_all()`
5. Rate limiting on OTP request/verify
6. CI pipeline (lint + typecheck + tests) gating deploys
7. Scheduled cleanup of expired sessions/OTP codes
8. Containerize the frontend for deployment symmetry with the backend
9. Build out `describe-problem` — currently a placeholder, but the actual core teleconsultation feature
10. A way to read analytics back out (currently write-only via the API; reads are direct SQL against Postgres) — a query endpoint or small internal dashboard
11. Additional locales beyond the current five, if demand warrants it
