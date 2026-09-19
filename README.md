# Shigotai

**仕事 (shigoto) + AI.** An AI-powered career intelligence platform for people who want
to work at Japanese companies. Tell Shigotai who you are — your skills, education,
experience, and Japanese ability — and it continuously matches you against currently
active job postings, explaining transparently *why* you match and what's missing,
rather than showing a mystery score.

This repository contains a complete, runnable full-stack implementation: a Next.js
frontend, a FastAPI backend, a hybrid (deterministic + semantic + LLM-explained)
matching engine, a pluggable job-ingestion pipeline, and a notification system —
all runnable locally with zero external API keys, backed by a clearly-labeled demo
dataset.

## Product overview

- **Career DNA profile**: skills (technical vs. AI/ML kept separate), education,
  experience, projects, certifications, and a *disaggregated* Japanese-ability
  profile (JLPT level is not assumed to represent speaking/business communication
  ability — those are tracked separately).
- **Resume upload**: PDF/DOCX parsing that *proposes* extracted fields for the user
  to accept/edit/remove — it never silently overwrites the profile.
- **Job intelligence**: a `JobSourceAdapter` interface (see `backend/app/ingestion/base.py`)
  with a demo dataset implementation today, ready to swap in real sources (company
  career pages, Greenhouse/Lever, authorized feeds) without touching the rest of
  the pipeline.
- **"Hiring now" verification**: every job tracks `first_seen_at` / `last_verified_at`
  / `status` (ACTIVE/CLOSED/STALE/UNKNOWN), re-checked against its source over time
  rather than trusting a stale posting date.
- **Hybrid matching engine**: deterministic requirement checks (JLPT, education,
  experience, skills, visa, new-grad eligibility) → lightweight explainable semantic
  matching (a concept-vector space over a curated skill taxonomy, not an opaque
  embedding) → an LLM-generated plain-language explanation, only for jobs that
  already cleared the cheap stages (cost control).
- **Notifications**: in-app + email, deduplicated so a user isn't renotified about
  an unchanged match, but *is* notified when a job's stated requirements change
  enough that they now qualify ("this job just became a match for you").
- **FACT vs. AI INTERPRETATION vs. UNKNOWN**: the extraction pipeline never invents
  a requirement the source text doesn't support (e.g. it will never turn "business
  Japanese required" into a specific JLPT level).

## Tech stack

| Layer | Choice |
|---|---|
| Frontend | Next.js 16 (App Router), React 19, TypeScript, Tailwind CSS v4, Framer Motion |
| Backend | FastAPI, SQLAlchemy 2.0, Alembic, Pydantic v2 |
| Database | SQLite for local dev (schema is Postgres-portable; see "Going to production") |
| Matching | Rule-based deterministic checks + a hand-built explainable concept-vector "semantic" layer + a pluggable LLM provider |
| Auth | JWT (access + refresh), bcrypt password hashing |
| Background processing | In-process synchronous recompute at demo scale; designed to lift into Celery/RQ workers behind the same function signatures |

## Project structure

```
Shigotai/
  backend/
    app/
      api/            # FastAPI routers (thin -- delegate to services/)
      core/           # config, security, rate limiting
      models/         # SQLAlchemy models
      schemas/        # Pydantic request/response schemas
      services/       # business logic (auth, profile, matching orchestration, notifications, resume parsing)
      matching/        # deterministic + semantic matching engine, skill taxonomy
      ai/              # LLMProvider interface + dev (rule-based) and Anthropic-backed implementations
      ingestion/       # JobSourceAdapter interface + demo dataset + ingestion pipeline
      notifications/   # EmailProvider interface + dev (file outbox) and Resend implementations + templates
      storage/         # FileStorage interface + dev (local disk) and S3-compatible implementations
    alembic/           # migrations
    tests/             # pytest suite for matching/extraction/dedup/notifications
    scripts/start.sh   # container entrypoint: run migrations, seed if DEMO_MODE, start uvicorn
    seed.py            # seeds demo jobs + a demo user
    Dockerfile
  frontend/
    src/
      app/             # Next.js routes: (marketing), (auth), (app) route groups
      components/      # ui/ (design system primitives), layout/, jobs/, marketing/, motion/
      lib/             # api client, auth context, types, utils
    .qa/               # local screenshot tooling used during development (gitignored)
    Dockerfile         # only needed if not deploying the frontend to Vercel
  docker-compose.yml   # full stack incl. Postgres, for local prod-parity or single-VM self-hosting
  README.md
  .env.example
```

## Setup

### Prerequisites

- Node.js 20+
- Python 3.11+ (3.10+ works; developed against 3.12)

### 1. Environment variables

```bash
cp .env.example .env
```

The defaults work out of the box for local development: SQLite database, a
rule-based AI provider (no API key needed), and a file-based email outbox. Fill
in real values only when you're ready to connect a real LLM/email/push provider.

### 2. Backend

```bash
cd backend
python -m venv venv
./venv/Scripts/activate        # Windows; use `source venv/bin/activate` on macOS/Linux
pip install -r requirements.txt

# Apply migrations
python -m alembic upgrade head

# Seed demo jobs + a demo account (demo@shigotai.app / ShigotaiDemo123!)
python -m app.seed

# Run the API
python -m uvicorn app.main:app --reload --port 8000
```

The API is now at `http://localhost:8000` (interactive docs at `/docs`).

### 3. Frontend

```bash
cd frontend
npm install
cp .env.local.example .env.local   # or create .env.local with NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
npm run dev
```

The app is now at `http://localhost:3000`. Log in with the seeded demo account,
or register a new one.

### 4. Running tests

```bash
cd backend
python -m pytest tests/ -v
```

Covers: JLPT/skill/education/experience deterministic matching, the rule-based
requirement extractor (never inventing a JLPT level, correct required/preferred
skill splitting, visa/new-grad signal detection), job deduplication across
sources, and notification decision logic (first-match, suppression of duplicate
alerts, "job just became a match" detection, daily cap, threshold filtering).

### 5. Database migrations

```bash
cd backend
python -m alembic revision --autogenerate -m "describe your change"
python -m alembic upgrade head
```

## Adding a job source

Implement `JobSourceAdapter` (`backend/app/ingestion/base.py`):

```python
class MyAdapter(JobSourceAdapter):
    source_name = "My ATS"
    source_type = "ATS_GREENHOUSE"

    def fetch_jobs(self) -> list[RawJobPosting]: ...
    def check_status(self, source_job_id: str) -> JobStatus: ...
```

Then call `ingest_source(db, MyAdapter())` (see `app/seed.py` for the demo-source
example) — normalization, deduplication, requirement extraction, and job-status
tracking all happen inside `app/ingestion/pipeline.py` regardless of source.
**Always respect the target site's Terms of Service, robots.txt, and rate limits.
Prefer official APIs/feeds.**

## Adding a notification provider

`EMAIL_PROVIDER=resend` (+ `EMAIL_API_KEY`) already switches every outgoing
email (verify-email, password reset, job match alerts) to real delivery via
[Resend](https://resend.com) using `app/notifications/resend_provider.py` --
no code changes needed for that one. The dev provider (default) writes emails
to `backend/var/outbox/` as inspectable `.html` files instead of sending.

To add a different provider, implement `EmailProvider` or `PushProvider`
(`backend/app/notifications/base.py`) and add it as another branch in
`app/notifications/provider.py`'s `get_email_provider()` -- every call site
already goes through that function rather than instantiating a provider
directly.

## AI configuration

By default (`LLM_PROVIDER=dev`), Shigotai uses a conservative, fully-offline
rule-based extractor (`app/ai/dev_provider.py`) for requirement extraction and
match explanations — this is why the app is fully functional with no API key.
Set `LLM_PROVIDER=anthropic` and `LLM_API_KEY` to switch to the Anthropic-backed
provider (`app/ai/anthropic_provider.py`), which falls back to the rule-based
provider on any API error so the pipeline never hard-fails.

## Demo data

`DEMO_MODE=true` (the default) seeds ~15 fictional but realistic Japan-focused
job postings, each flagged `is_demo_data: true` end-to-end and surfaced in the
UI with a visible "Demo data" label — they are never presented as real, currently
hiring postings.

## Deployment

The recommended path is **Vercel (frontend) + Render or Railway (backend) +
Neon or Supabase (Postgres)** — each is a natural fit for its piece, all have
free tiers, and none require you to manage a server. A single-VM
`docker compose up` (see `docker-compose.yml`) is the alternative if you'd
rather own one box than split hosting across three providers.

### 1. Database

Create a Postgres database on [Neon](https://neon.tech) or
[Supabase](https://supabase.com) and copy its connection string. Set it as
`DATABASE_URL`, adding `+psycopg` after `postgresql` if it isn't already
there:

```
DATABASE_URL=postgresql+psycopg://user:password@host/dbname?sslmode=require
```

Nothing else changes — the schema and all queries are already
Postgres-compatible (see `backend/app/database/session.py`).

### 2. Backend (Render / Railway / Fly.io)

`backend/Dockerfile` is ready to deploy as-is: point your host at the
`backend/` directory, it'll detect the Dockerfile, and `scripts/start.sh`
runs migrations (and seeds demo data if `DEMO_MODE=true`) before starting
the server. Set these environment variables on the host:

- `DATABASE_URL` (from step 1)
- `AUTH_SECRET` — generate a real one: `python -c "import secrets; print(secrets.token_urlsafe(48))"`
- `FRONTEND_BASE_URL` and `CORS_ORIGINS` — your Vercel URL (step 3); until
  you have it, deploy once with the Render/Railway default subdomain as a
  placeholder for the frontend, then update these two after step 3
- `EMAIL_PROVIDER=resend` + `EMAIL_API_KEY` (get a free key at
  [resend.com](https://resend.com)) — without this, emails just get logged
  and no one receives them
- `STORAGE_PROVIDER=s3` + `STORAGE_BUCKET`/`STORAGE_ACCESS_KEY_ID`/`STORAGE_SECRET_ACCESS_KEY`
  (a free [Cloudflare R2](https://developers.cloudflare.com/r2/) bucket
  works well; set `STORAGE_ENDPOINT_URL` to its account-specific endpoint) —
  without this, uploaded resumes vanish on every redeploy since most hosts'
  filesystems are ephemeral
- Optionally `REDIS_URL` (a free [Upstash](https://upstash.com) Redis
  instance) so rate limiting is shared correctly if you ever run more than
  one backend instance
- Health check path: `/health`

### 3. Frontend (Vercel)

Import the repo, set the project's root directory to `frontend/`, and set
one environment variable: `NEXT_PUBLIC_API_BASE_URL` to your backend's public
URL from step 2. Deploy. Then go back to step 2's host and update
`FRONTEND_BASE_URL`/`CORS_ORIGINS` to the real `https://your-app.vercel.app`
URL Vercel just gave you, and redeploy the backend so those take effect.

### Self-hosting on one VM instead

```bash
cp .env.example .env   # fill in AUTH_SECRET at minimum
docker compose up --build
```

This runs Postgres, the backend, and the frontend together with sensible
defaults already wired between them (see `docker-compose.yml`).

### What's still a placeholder either way

- **Job sources**: only the demo dataset exists; implement additional
  `JobSourceAdapter`s for real postings (section above).
- **Real LLM**: set `LLM_PROVIDER=anthropic` + `LLM_API_KEY` for
  LLM-generated match explanations; the rule-based provider is honest but
  simple.
- **Web Push**: `WEB_PUSH_PUBLIC_KEY`/`WEB_PUSH_PRIVATE_KEY` are reserved for
  a real `pywebpush` integration; the settings page already tells users this
  isn't wired up yet rather than pretending it works.
- **Background workers**: match recomputation runs synchronously in-request
  today, which is fine at demo scale. Swapping in Celery/RQ using `REDIS_URL`
  means moving the calls in `app/services/match_service.py`
  (`recompute_matches_for_user`, `recompute_matches_for_job`) into tasks —
  the function boundaries are already the right granularity for that.

## Security notes

- Passwords are hashed with bcrypt (never stored or logged in plaintext).
- JWT access/refresh tokens; no session state stored server-side.
- Resume uploads are validated by extension and size (5MB) before parsing.
- `/auth/login`, `/auth/register`, and `/auth/password-reset/request` are
  rate-limited per-IP (`app/core/rate_limit.py`). Uses Redis when `REDIS_URL`
  is set (correct across multiple instances); falls back to an in-process
  limiter otherwise, which only enforces per-process, so it's not effective
  if you scale the backend to multiple instances without also setting
  `REDIS_URL`.
- No secrets are committed; `.env` is gitignored and `.env.example` only holds
  placeholders.
