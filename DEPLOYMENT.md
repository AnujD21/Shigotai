# Launching Shigotai for $0

Everything below runs on free tiers with no server to manage and no cold
starts long enough for a user to notice. Checked against each provider's
terms in October 2026; free tiers change, so glance at each pricing page
when you sign up.

| Piece | Service | Free tier notes |
|---|---|---|
| Frontend (Next.js) | **Vercel** Hobby | Non-commercial use only. Upgrade to Pro once you charge money. |
| Backend API (FastAPI) | **Vercel** Hobby, second project | Serverless; 300 s max per request, 4.5 MB max request body. |
| Database | **Neon** Postgres | Free plan, sleeps after 5 min idle and wakes in under a second. |
| Job ingestion (cron) | **GitHub Actions** | Unlimited minutes on public repos; 2,000 min/month on private (a run takes ~4 min, 4x/day ≈ 500 min/month). |
| Emails | **Gmail SMTP** (or Brevo) | No domain needed. Gmail: ~500/day with an app password. |
| AI extraction | Rule-based (built in), **Gemini**/**Groq** free tiers, or Claude Haiku at ~$1/month | See step 5. |
| Resume files | Not stored | `STORAGE_PROVIDER=none`: parsed in memory, only approved fields saved. |

Why not Render or Koyeb? Render's free web services sleep after 15 minutes
and take about a minute to wake, which users see as a broken site, and its
free Postgres is deleted after 30 days. Koyeb closed its free plan to new
users in February 2026. Vercel's FastAPI support makes the backend a
serverless function that starts in about a second instead.

---

## 1. Push the repo to GitHub

Public or private both work (see the Actions minutes note above).

## 2. Create the database (Neon)

1. Sign up at [neon.com](https://neon.com) and create a project. Pick the
   **AWS US East (N. Virginia)** region: it's next to Vercel's default
   function region (`iad1`, Washington D.C.), and every API request makes
   several database round trips.
2. On the dashboard, open **Connect**, turn on **Connection pooling**, and
   copy the connection string (the host contains `-pooler`).
3. Change the scheme to use the psycopg driver:
   `postgresql://...` → `postgresql+psycopg://...`. Keep `?sslmode=require`.

That's your `DATABASE_URL`.

## 3. Get an email sender (Gmail app password)

1. On the Google account you'll send from, turn on 2-Step Verification.
2. Go to **Google Account → Security → App passwords**, create one named
   "Shigotai", and copy the 16-character password.

You'll use `smtp.gmail.com`, port `587`, your Gmail address as both
`SMTP_USERNAME` and `EMAIL_FROM`, and the app password as `SMTP_PASSWORD`.
(Brevo works the same way with `smtp-relay.brevo.com` if you'd rather not
use a personal Gmail.)

## 4. Generate a secret

```bash
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

That's `AUTH_SECRET`. The backend refuses to start in production without a
real one.

## 5. Choose how jobs and resumes are read

All options work; they differ in accuracy and cost. You can switch later
by changing environment variables -- no code changes.

| Option | Cost | Set |
|---|---|---|
| **A. Rule-based** (built in) | $0 | `LLM_PROVIDER=dev` |
| **B. Gemini free tier** for job postings | $0 | `LLM_PROVIDER=gemini`, `LLM_API_KEY` from [aistudio.google.com](https://aistudio.google.com), `LLM_MODEL` = a Flash model ID from AI Studio's model list |
| **C. Groq free tier** | $0 | `LLM_PROVIDER=groq`, key and model ID from [console.groq.com](https://console.groq.com) |
| **D. Claude Haiku 5.5** | ~$0.30 for the first full ingest, then cents per day | `LLM_PROVIDER=anthropic`, `LLM_MODEL=claude-haiku-5-5`, key from [platform.claude.com](https://platform.claude.com) |

Rule-based extraction recognizes a fixed skill list and explicit phrases
("JLPT N2", "visa sponsorship available"); an LLM also catches requirements
phrased any other way and structures work history from resumes.

**Resumes are personal data.** Gemini's free tier may use your inputs to
improve Google's products, which is fine for public job postings but not for
users' resumes. If you use option B, send resumes elsewhere with
`RESUME_LLM_PROVIDER` / `RESUME_LLM_API_KEY` / `RESUME_LLM_MODEL` (e.g. Groq
after checking its current data terms, or Claude), or leave
`RESUME_LLM_PROVIDER` empty and set `LLM_PROVIDER=dev` to keep resume
parsing local. Whatever you pick, every LLM-extracted item is checked
against the resume text before the user sees it.

Free tiers are rate-limited. The ingestion workflow already spaces calls
2.5 s apart, only new or changed postings are sent, and match explanations
are capped at 8 LLM calls per recompute. If a limit is hit anyway, that call
falls back to the rule-based result instead of failing.

## 6. Deploy the backend (Vercel project #1)

1. In Vercel: **Add New → Project**, import the repo, and set **Root
   Directory** to `backend`. Vercel detects FastAPI from `app/main.py`.
2. Add these environment variables:

   ```
   ENVIRONMENT=production
   DEMO_MODE=false
   AUTH_SECRET=<step 4>
   DATABASE_URL=<step 2>
   STORAGE_PROVIDER=none
   EMAIL_PROVIDER=smtp
   SMTP_HOST=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USERNAME=<your gmail>
   SMTP_PASSWORD=<step 3>
   EMAIL_FROM=<your gmail>
   LLM_PROVIDER=<step 5>
   LLM_API_KEY=<step 5>
   LLM_MODEL=<step 5>
   FRONTEND_BASE_URL=https://placeholder.vercel.app
   CORS_ORIGINS=https://placeholder.vercel.app
   ```

   The last two get their real values in step 8.
3. Deploy. Copy the URL (e.g. `https://shigotai-api.vercel.app`) and open
   `/health` -- you should see `{"status":"ok"}`.

## 7. Create the tables and load live jobs (GitHub Actions)

1. In GitHub: **Settings → Secrets and variables → Actions → New repository
   secret**. Add the same values as step 6: `DATABASE_URL`, `AUTH_SECRET`,
   `FRONTEND_BASE_URL`, `LLM_PROVIDER`, `LLM_API_KEY`, `LLM_MODEL`,
   `EMAIL_PROVIDER`, `EMAIL_FROM`, `SMTP_HOST`, `SMTP_PORT`,
   `SMTP_USERNAME`, `SMTP_PASSWORD`.
2. **Actions → Ingest live jobs → Run workflow.** This applies the database
   migrations, then pulls every board in
   `backend/app/ingestion/japan_boards.py` (about 550 Japan roles from 34
   companies at last check). It takes 3-5 minutes rule-based, longer the
   first time with an LLM on a free tier.
3. From then on it runs automatically every 6 hours: new roles are added,
   roles taken down by the employer are marked closed, and users get emails
   about new matches.

**Do this before anyone signs up** -- until the migrations run, the
database has no tables and every API call fails.

## 8. Deploy the frontend (Vercel project #2)

1. **Add New → Project**, import the same repo, **Root Directory**
   `frontend`.
2. Environment variables:

   ```
   NEXT_PUBLIC_API_BASE_URL=<backend URL from step 6, no trailing slash>
   NEXT_PUBLIC_SITE_URL=<this project's URL, e.g. https://shigotai.vercel.app>
   ```

   (Deploy once to learn the URL if needed, then set `NEXT_PUBLIC_SITE_URL`
   and redeploy -- `NEXT_PUBLIC_*` values are baked in at build time.)
3. Back in the **backend** project, set `FRONTEND_BASE_URL` and
   `CORS_ORIGINS` to the frontend URL (exact match, no trailing slash) and
   redeploy it. Update the `FRONTEND_BASE_URL` GitHub secret too -- it's
   used for links in match emails.

## 9. Check it end to end

- [ ] Home page shows "N open roles in Japan from M companies" under the buttons.
- [ ] **Explore Jobs** lists real postings; **View job** links reach the employer's page.
- [ ] Register → the verification email arrives (check spam the first time).
- [ ] Upload a resume on **My Profile** → review dialog lists education, roles, and skills.
- [ ] Save the profile → **My Matches** fills in.
- [ ] **Forgot password** email arrives.

---

## Optional upgrades

- **Shared rate limiting.** Login/registration limits are counted per
  serverless instance. For limits that hold across instances, create a free
  [Upstash](https://upstash.com) Redis database and set `REDIS_URL` to its
  `rediss://` URL on the backend.
- **Custom domain** (~$10/year from any registrar): add it to the frontend
  Vercel project, then update `NEXT_PUBLIC_SITE_URL`, `FRONTEND_BASE_URL`,
  and `CORS_ORIGINS`. With your own domain you can also switch email to
  Resend (`EMAIL_PROVIDER=resend`) for better deliverability than Gmail.
- **More companies.** Add boards to `backend/app/ingestion/japan_boards.py`
  (instructions at the top of that file) and check them with
  `python -m app.ingest --board <platform>:<slug> --dry-run`.

## Things to know

- **Scheduled workflows pause on inactive repos.** GitHub disables cron
  workflows in public repos after 60 days without a commit. Re-enable it
  from the Actions tab, or push any commit.
- **First request after idle** wakes the database and the function: about
  a second, once.
- **Vercel Hobby is for non-commercial projects.** Move to Pro before
  charging users or running ads.
- **Web push** notifications aren't implemented; email and in-app alerts are.
