# ShadowByte Cyber Operations Platform — Starter

A runnable local-development foundation for ShadowByte. Includes a FastAPI API, persistent SQLite development database (PostgreSQL-ready configuration), asset authorization records, explicit scope checks, a safe DNS/TLS assessment job, audit events, a Next.js frontend starter, Docker Compose for PostgreSQL/Redis, and tests.

## Prerequisites
- Windows 10/11
- Python 3.11+
- Node.js 20+
- Docker Desktop (optional; for PostgreSQL/Redis)

## Quick start — API (PowerShell)
```powershell
cd shadowbyte-starter
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r backend/requirements.txt
Copy-Item backend/.env.example backend/.env
uvicorn app.main:app --app-dir backend --reload --host 127.0.0.1 --port 8000
```
Open http://127.0.0.1:8000/docs and http://127.0.0.1:8000/health.

The API binds to localhost by default. Do not expose it to the internet as-is.

## Run tests
```powershell
 $env:PYTHONPATH="backend"; pytest backend/tests -q
```

## Frontend
```powershell
cd frontend
npm install
npm run dev
```
Open http://localhost:3000. The dashboard fetches real API health and assets from `http://127.0.0.1:8000`. This is a starter UI, not a complete production frontend.

## Optional PostgreSQL and Redis
```powershell
docker compose up -d postgres redis
```
Set `DATABASE_URL=postgresql+psycopg://shadowbyte:change-this-local-password@localhost:5432/shadowbyte` in `backend/.env`, then restart the API. Install the optional driver:
```powershell
pip install "psycopg[binary]>=3.2,<4"
```
For a real deployment, use a long random password in an untracked `.env` file and do not publish database or Redis ports.

## What is implemented
- Health/readiness endpoints.
- SQLite persistence by default, PostgreSQL URL support.
- Asset registration and authorization metadata.
- Assessment job creation only for assets explicitly marked authorized.
- Safe DNS resolution and TLS certificate-expiry inspection for registered DNS names.
- Job state and findings persisted in the database.
- Audit events for asset/job operations.
- Basic frontend with actual backend status and asset list.
- Tests for scope enforcement and safe assessment behavior.

## Important boundaries
This starter does **not** provide a remote shell, unrestricted Kali terminal, arbitrary command execution, or internet-wide scanning. The first assessment profile performs DNS/TLS checks only against an explicitly registered hostname. Add a Linux worker only after implementing isolation, egress controls, target allowlists, quotas, and authorization review. Do not use it against systems without permission.

## Production gaps to complete before public launch
- Real authentication and RBAC; current API is a local-development scaffold and does not authenticate users.
- Alembic migrations and managed secrets.
- WebAuthn/passkeys, TOTP MFA, email verification, recovery workflows.
- Rate limiting, CSRF strategy, CORS allowlist, reverse proxy and TLS.
- Dedicated worker service with sandboxing and network policy.
- Real event source and licensed map/terrain provider.
- Email provider integration, delivery webhooks, backups and monitoring.
