# Bueza Pets — Frontend

Next.js 16 (App Router), TypeScript, Tailwind, `next-intl`. See the [repo root README](../README.md) for architecture, local setup, and deployment covering the whole system (this app plus the FastAPI backend).

## Quick reference

```bash
cp .env.example .env
npm install
npm run dev      # http://localhost:3000
```

```bash
npm run build && npm run start   # production build
npm run lint
```

Requires `BACKEND_API_URL` (see `.env.example`) pointing at a running instance of `../backend` for login and analytics to work.
