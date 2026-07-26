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

Production and staging are two independent Docker Compose stacks — same repository, same code, no duplication — living side by side on one shared host that also runs several unrelated projects (Odoo, n8n, etc.). See [Deployment](#deployment) for the full picture: how the two environments stay isolated, how the shared nginx routes to them, and how releases actually ship.

## Local setup

Prerequisites: Node 20+, Python 3.12+, and either Docker (recommended) or a local Postgres instance.

### Backend

Easiest path — the whole backend plus Postgres via Docker Compose, from the repo root (this reuses the production compose file; see [Deployment](#deployment) for why there are two — for local dev either works identically, `prod` is just the default):

```bash
cp .env.production.example .env.production   # fill in a local password, doesn't need to be real
docker compose -f docker/compose.prod.yml --env-file .env.production up -d --build
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

1. `docker compose -f docker/compose.prod.yml --env-file .env.production up -d --build` (backend + db)
2. `cd frontend && npm install && npm run dev`
3. Visit `http://localhost:3000` — splash → language → login (the OTP code is shown directly in the UI, since there's no real SMS gateway) → home

## Deployment

Production and staging run as two independent Docker Compose stacks on one shared host, from the **same git repository** — no duplicated code, no separate checkouts fighting over branches.

| | Production | Staging |
|---|---|---|
| Branch | `main` | `develop` |
| Frontend | https://app.bueza.in (host port 3010) | https://staging.app.bueza.in (host port 3011) |
| Backend | https://api.bueza.in (host port 8000) | https://staging.api.bueza.in (host port 8001) |
| Postgres | internal only, not published | internal only, not published |
| Containers | `bueza-pets-{frontend,backend,db}-prod` | `bueza-pets-{frontend,backend,db}-staging` |
| Docker network | `bueza-pets-prod-network` | `bueza-pets-staging-network` |
| Volume | `bueza_pets_prod_postgres_data` | `bueza_pets_staging_postgres_data` |
| Env file | `/root/bueza-pets/.env.production` | `/root/bueza-pets-staging/.env.staging` |

### Why git worktree, not two clones or a shared checkout with branch-switching

Both environments need their own on-disk build context (Docker builds `COPY` from a real directory) and their own git branch checked out *simultaneously* — production can't be mid-deploy on `main` while staging is switching to `develop` in the same working directory. The options were:

1. **Two full clones** — works, but two independent `.git` histories to keep in sync is exactly the "duplicated repository" this setup is meant to avoid.
2. **One checkout, `git checkout <branch>` before each deploy** — the working directory can only ever be on one branch at a time, so a staging deploy and a production deploy can never safely overlap, and it's easy to forget which branch is currently checked out mid-incident.
3. **`git worktree`** — one `.git` object database, two real, independent working directories, each permanently on its own branch. This is what's actually in place:

```
/root/bueza-pets           main branch    (production — the original checkout)
/root/bueza-pets-staging   develop branch (staging — added via `git worktree add`)
```

Both directories can be built, deployed, and rolled back independently, with zero risk of one stepping on the other, while still being one repository with one history.

### Docker Compose

`docker/compose.prod.yml` and `docker/compose.staging.yml` are near-identical, differing only in names/ports/volumes so the two can never collide even while running on the same Docker host. Notable choices, explained once here rather than repeated in both files:

- **Postgres is never published to the host** in either environment — nothing outside the compose network needs to reach it directly.
- **No Redis.** The codebase doesn't use it anywhere (no caching, queues, or pub/sub) — provisioning idle Redis containers on a host that already runs two other Redis instances for unrelated projects would be pure YAGNI.
- **`backend`/`frontend` also join the pre-existing external `odoo-network`**, in addition to their own private per-environment network. This is how the host's shared nginx (see below) reaches them by container name — Postgres is deliberately *not* on this shared network, so nothing outside this project's own containers can ever reach the database.
- **Per-container log rotation** (`max-size: 10m`, `max-file: 3`) via a shared `x-logging` anchor. Deliberately not a `/etc/docker/daemon.json` change — that's daemon-wide and requires restarting the Docker daemon, which would restart *every* container on this shared host at once.
- **Memory limits** (`mem_limit`) on every service so a runaway container in one stack can't starve the other stack or the other projects on this host.

### Nginx: sharing the host's existing reverse proxy

Port 80/443 on this host are already owned by another project's nginx container (`odoo16-nginx`), which fronts several unrelated domains via sibling files in its `/etc/nginx/conf.d/` (its own `default.conf`, plus an existing `n8n.conf`). Rather than run a second, competing nginx — which isn't possible, only one process can bind a given port — `nginx/z-bueza-pets.conf` is deployed as one more sibling file in that same directory. It's pure addition: no existing file is modified, and it reaches this project's containers by name over the shared `odoo-network`.

The `z-` filename prefix is deliberate, not cosmetic: nginx picks its `default_server` (used for any request with no matching `Host` header) from whichever `conf.d` file loads first alphabetically when none is explicitly marked. Without the prefix, this file would have silently become the new default for the whole host, changing pre-existing fallback behavior. Real traffic (which always sends a proper `Host` header) is unaffected either way, but `z-` guarantees zero behavioral change to anything already running here.

Deploy or update it with:

```bash
docker cp nginx/z-bueza-pets.conf odoo16-nginx:/etc/nginx/conf.d/z-bueza-pets.conf
docker exec odoo16-nginx nginx -t && docker exec odoo16-nginx nginx -s reload
```

### SSL (Let's Encrypt via Certbot)

One certificate, four names as SANs (`app.bueza.in`, `api.bueza.in`, `staging.app.bueza.in`, `staging.api.bueza.in`) — simpler to manage than four separate certs for a single developer, and certbot's own systemd timer renews it automatically going forward.

**Prerequisite**: DNS for all four hostnames must already resolve to this server — see [DNS requirements](#dns-requirements-hostinger) below. Certbot's webroot validation will fail otherwise.

```bash
CERTBOT_EMAIL=you@example.com scripts/setup-ssl.sh
```

This is a one-time bootstrap, safe to re-run. It exists because deploying the full nginx config before a certificate exists would fail nginx's config test (referencing cert files that don't exist yet) — so it sequences things safely: deploy a minimal HTTP-only placeholder first, verify all four domains actually resolve here (refusing to continue otherwise), request the certificate via certbot's webroot mode (reusing the ACME webroot already configured on this nginx), then swap in the full HTTPS config from `nginx/z-bueza-pets.conf`.

Once SSL is confirmed working, flip `COOKIE_SECURE=true` in both `.env.production` and `.env.staging` and redeploy — until then it's deliberately `false`, since a `Secure` cookie set over plain HTTP is silently dropped by real browsers, which would break login.

### DNS requirements (Hostinger)

Four A records, all pointing at this server's IP:

| Host | Type | Value |
|---|---|---|
| `app` | A | `<server IP>` |
| `api` | A | `<server IP>` |
| `staging.app` | A | `<server IP>` |
| `staging.api` | A | `<server IP>` |

(`app.bueza.in` currently points elsewhere and needs repointing; `api.bueza.in` already resolves here; the two `staging.*` records don't exist yet and need creating.) Note `bueza.in`'s nameservers were observed pointing at a DNS-parking service rather than Hostinger's own DNS at the time this was set up — if that's still the case, these records need to be added wherever DNS is actually being managed for the domain, not necessarily Hostinger's panel specifically.

Propagation is usually minutes, occasionally longer. Confirm with `dig +short app.bueza.in` (and the other three) before running `scripts/setup-ssl.sh`.

### Manual deploy

```bash
scripts/deploy-production.sh   # main branch only, restarts only the prod stack
scripts/deploy-staging.sh      # develop branch only, restarts only the staging stack
```

Each: fetches its own branch (fast-forward only), rebuilds and restarts only its own stack, then polls the backend `/health` endpoint before declaring success.

### CI/CD (GitHub Actions)

`.github/workflows/deploy-production.yml` runs `scripts/deploy-production.sh` on every push to `main`; `deploy-staging.yml` runs `deploy-staging.sh` on every push to `develop`. Both also support manual triggering from the Actions tab.

Requires two repository secrets (Settings → Secrets and variables → Actions):

| Secret | Value |
|---|---|
| `DEPLOY_HOST` | The server's IP |
| `DEPLOY_SSH_KEY` | Private half of a dedicated deploy keypair (`github_actions_deploy` on the server) generated specifically for this — it can't do anything the deploy scripts themselves don't already do, and is separate from every other key already authorized on the server. |

### Rollback

```bash
scripts/rollback.sh production          # rolls back to the previous commit
scripts/rollback.sh staging abc1234      # or to a specific commit
```

Checks out the target commit **detached** in that environment's worktree and redeploys from it. The next regular deploy re-attaches to the branch and moves forward normally — rollback doesn't rewrite history, it just temporarily runs older code.

### Backups

`scripts/backup.sh` runs nightly via cron (`/root/bueza-pets/scripts/backup.sh`, root's crontab, `3:15 AM` — offset from the existing Odoo backup jobs on this host at 2 AM/2 PM), `pg_dump`-ing both databases to `/root/bueza-pets-backups/{production,staging}/`, gzipped, keeping the last **14** per environment by count.

### Firewall (UFW)

Active, default-deny on incoming. Allowed: `22` (SSH), `80`/`443` (the shared nginx), plus every port already in use by other projects on this host at the time UFW was enabled (`3000`, `3001`, `5000`, `5433`, `5678`, `6380`, `8080`) so nothing else already running here lost reachability. This project's own container ports (`3010`, `3011`, `8000`, `8001`) are **deliberately not** in the allow list — nginx reaches them over the internal Docker network, not via these host-published ports, so they have no reason to be reachable from the public internet. They're still reachable from the server itself (e.g. `curl localhost:8000/health` over SSH) since UFW only governs the external interface.

## Technical debt & known limitations

Things that work today but carry a known, conscious tradeoff:

- **No automated tests.** Neither backend (pytest) nor frontend (Vitest/Playwright) has a test suite yet. Verification so far has been manual — curl scripts, Lighthouse, and direct browser checks against scratch environments. Fine at the current pace; a real gap as surface area grows.
- **No database migrations.** `Base.metadata.create_all()` only creates missing tables — it cannot alter an existing one. The first schema change to a table holding real data needs Alembic (or equivalent) introduced *before* it's safe to deploy.
- **Mock OTP returns the code directly in the API response.** Necessary today since there's no SMS gateway. This must be gated behind an environment check (or removed outright) before any real SMS integration — otherwise it's an authentication bypass.
- **No rate limiting** on `/auth/otp/request`. Harmless today since nothing is actually sent, but would need addressing before real SMS delivery (cost and abuse).
- **`otp_codes` and `sessions` rows are never cleaned up.** Expired/consumed rows accumulate forever. Not urgent at current scale; needs a scheduled cleanup eventually.
- **Repository interfaces have exactly one implementation each** (e.g. `UserRepository` → `SqlAlchemyUserRepository`). This is a conscious tradeoff from the decision to use Clean Architecture, not an oversight — the seam exists for future flexibility (swapping persistence, substituting fakes once a test suite exists), but nothing exercises the swap today. One instance of this pattern *was* pure ceremony with zero business logic behind it — the health-check feature (`HealthRepository` interface + use case wrapping a single `SELECT 1`) — and was collapsed into the endpoint directly as part of this review. The auth/analytics repositories were kept as-is since they hold real domain logic (OTP validation, session expiry, user get-or-create).
- **No CORS configuration on the backend** — not currently needed since the frontend's BFF routes proxy server-side, but relevant if anything ever needs the browser to call the backend directly.
- **This project's nginx config lives inside another project's container** (`odoo16-nginx`), because that container already owns the host's only 80/443. It's deployed as an isolated, clearly-namespaced file (`z-bueza-pets.conf`) that touches nothing else in there, but it does mean this project's public routing has an operational dependency on a container it doesn't own or control the lifecycle of.
- **UFW was enabled for the first time as part of this work**, on a host that previously had no firewall at all and runs several unrelated projects. The allow-list was built from an audit of ports in use *at that moment* — if any of those other projects starts listening on a new port later, it'll need its own UFW rule added, since default-deny won't know about it.

## Roadmap

Roughly in the order they'd likely become necessary:

1. Real SMS gateway (Twilio, MSG91, etc.) to replace mock OTP, gated per environment
2. Automated tests — pytest for backend use cases/repositories, Vitest/Playwright for the frontend
3. Alembic migrations, replacing `create_all()`
4. Rate limiting on OTP request/verify
5. Scheduled cleanup of expired sessions/OTP codes
6. Build out `describe-problem` — currently a placeholder, but the actual core teleconsultation feature
7. A way to read analytics back out (currently write-only via the API; reads are direct SQL against Postgres) — a query endpoint or small internal dashboard
8. Additional locales beyond the current five, if demand warrants it
9. A lint/typecheck/test gate in the GitHub Actions workflows before they deploy — right now they deploy unconditionally on push, since there's no test suite yet for them to run (see item 2)
