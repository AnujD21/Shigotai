# Shigotai

**仕事 (shigoto) + AI.** An AI-powered career intelligence platform for people who want
to work at Japanese companies. Tell Shigotai who you are — your skills, education,
experience, and Japanese ability — and it continuously matches you against currently
active job postings, explaining transparently *why* you match and what's missing,
rather than showing a mystery score.

This repository contains a complete, runnable full-stack implementation: a Next.js
frontend, a FastAPI backend, a hybrid (deterministic + semantic + LLM-explained)
matching engine, a pluggable job-ingestion pipeline, and a notification system —
all runnable locally with zero external API keys. Jobs come live from employers'
public career-board APIs (Greenhouse, Lever, Ashby, SmartRecruiters); a
clearly-labeled demo dataset is available for offline development.

## Product overview

- **Career DNA profile**: skills (technical vs. AI/ML kept separate), education,
  experience, projects, certifications, and a *disaggregated* Japanese-ability
  profile (JLPT level is not assumed to represent speaking/business communication
  ability — those are tracked separately).
- **Resume upload**: PDF/DOCX parsing (DOCX tables, headers, and footers included)
  that *proposes* extracted fields for the user to accept/edit/remove — it never
  silently overwrites the profile. With an LLM configured, education, roles, and
  skills are extracted with a strict schema and each item is checked against the
  resume text, so nothing the model invents reaches the user; without one, a
  conservative keyword parser runs instead.
- **Live job intelligence**: `JobSourceAdapter`s for the public job-board APIs of
  Greenhouse, Lever, Ashby, and SmartRecruiters (`backend/app/ingestion/ats_sources.py`),
  polling a curated list of companies hiring in Japan
  (`backend/app/ingestion/japan_boards.py`). No API keys and no scraping; roles
  removed from an employer's board are marked closed on the next run.
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
pip install -r requirements-dev.txt

# Apply migrations
python -m alembic upgrade head

# Seed demo jobs + a demo account (demo@shigotai.app / ShigotaiDemo123!)
python -m app.seed

# Optional: pull live Japan jobs (and retire the demo ones with DEMO_MODE=false)
python -m app.ingest

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

Covers: JLPT/skill/education/experience deterministic matching, role relevance,
boundary-aware skill detection ("Go" vs. "Google", "Go-to-market"), the rule-based
requirement extractor (never inventing a JLPT level, correct required/preferred
skill splitting, visa/new-grad signal detection), each ATS adapter against
captured payload shapes, job deduplication and closing of removed postings,
resume extraction and its grounding check, and notification decision logic
(first-match, suppression of duplicate alerts, "job just became a match"
detection, daily cap, threshold filtering).

### 5. Database migrations

```bash
cd backend
python -m alembic revision --autogenerate -m "describe your change"
python -m alembic upgrade head
```

## Job sources

`python -m app.ingest` polls every board in `backend/app/ingestion/japan_boards.py`,
keeps roles located in Japan, upserts them, closes the ones no longer listed,
and recomputes every user's matches (sending new-match notifications). In
production it runs every 6 hours from `.github/workflows/ingest-jobs.yml`.

```bash
python -m app.ingest --board lever:woven-by-toyota --dry-run   # inspect one board
python -m app.ingest --skip-matching                            # jobs only
```

To add a company, find its board slug in its careers-page URL
(`boards.greenhouse.io/<slug>`, `jobs.lever.co/<slug>`, `jobs.ashbyhq.com/<slug>`,
`jobs.smartrecruiters.com/<slug>`), add a `BoardConfig`, and dry-run it.

To add a different kind of source, implement `JobSourceAdapter`
(`backend/app/ingestion/base.py`) and pass it to `ingest_source(db, adapter,
close_missing=True)` -- normalization, deduplication, requirement extraction,
and status tracking all happen inside `app/ingestion/pipeline.py` regardless of
source. **Always respect the target site's Terms of Service, robots.txt, and
rate limits. Prefer official APIs/feeds.**

## Adding a notification provider

`EMAIL_PROVIDER=smtp` (Gmail app password or Brevo; no domain needed) or
`EMAIL_PROVIDER=resend` (+ `EMAIL_API_KEY`) switches every outgoing email
(verify-email, password reset, job match alerts) to real delivery. The dev
provider (default) writes emails to `backend/var/outbox/` as inspectable
`.html` files, and only logs them on read-only hosts.

To add a different provider, implement `EmailProvider` or `PushProvider`
(`backend/app/notifications/base.py`) and add it as another branch in
`app/notifications/provider.py`'s `get_email_provider()`.

## AI configuration

By default (`LLM_PROVIDER=dev`), Shigotai uses a conservative, fully-offline
rule-based extractor (`app/ai/dev_provider.py`), so the app works with no API
key. Two kinds of real providers plug in behind the same interface:

- `LLM_PROVIDER=anthropic` -- Claude via the official SDK with structured
  outputs (`app/ai/anthropic_provider.py`). `LLM_MODEL` defaults to
  `claude-opus-5-5`; `claude-haiku-5-5` costs about 1/40th as much.
- `LLM_PROVIDER=groq | gemini | openrouter | openai_compatible` -- any
  OpenAI-compatible endpoint, including free tiers
  (`app/ai/openai_compat_provider.py`). Requires `LLM_MODEL`.

Resumes can use a separate provider (`RESUME_LLM_*`), since they're personal
data and job postings aren't. Every provider falls back to the rule-based one
on any error, refusal, or rate limit, so the pipeline never hard-fails. See
`.env.example` for all settings.

## Demo data

`DEMO_MODE=true` (the default for local development) seeds ~15 fictional
Japan-focused postings, each flagged `is_demo_data: true` end-to-end and shown
with a visible "Demo data" label. With `DEMO_MODE=false`, `app.ingest` closes
them so only live postings are shown.

## Deployment

See **[DEPLOYMENT.md](DEPLOYMENT.md)** for a step-by-step $0 launch: Vercel
(frontend and FastAPI backend) + Neon Postgres + GitHub Actions for
ingestion + Gmail SMTP.

To self-host on one VM instead:

```bash
cp .env.example .env   # fill in AUTH_SECRET at minimum
docker compose up --build
```

### Not built yet

- **Web Push**: `WEB_PUSH_PUBLIC_KEY`/`WEB_PUSH_PRIVATE_KEY` are reserved for a
  real `pywebpush` integration; the settings page tells users it isn't wired
  up rather than pretending it works.
- **Background workers**: match recomputation after a profile save runs
  in-request (bounded: at most `MAX_LLM_EXPLANATIONS_PER_RECOMPUTE` LLM calls).
  Moving `recompute_matches_for_user` / `recompute_matches_for_job` into a
  queue is the next step at larger scale.

## Security notes

- Passwords are hashed with bcrypt (never stored or logged in plaintext).
- JWT access/refresh tokens; no session state stored server-side.
- Resume uploads are validated by extension and size (4MB, under Vercel's 4.5MB
  request limit) before parsing; with `STORAGE_PROVIDER=none` the file is never stored.
- The backend refuses to start with `ENVIRONMENT=production` and the default
  `AUTH_SECRET`.
- `/auth/login`, `/auth/register`, and `/auth/password-reset/request` are
  rate-limited per-IP (`app/core/rate_limit.py`). Uses Redis when `REDIS_URL`
  is set (correct across multiple instances); falls back to an in-process
  limiter otherwise, which only enforces per-process, so it's not effective
  if you scale the backend to multiple instances without also setting
  `REDIS_URL`.
- No secrets are committed; `.env` is gitignored and `.env.example` only holds
  placeholders.
