# DEPLOYMENT.md — Phiversity on free cloud hosting

Deploy the existing app with minimal changes: the **frontend** on Vercel,
the **backend API + renderer** on Render (Docker), the **database** on
Supabase (Postgres), and finished **videos** on Cloudinary. Everything
deploys from GitHub (auto-deploy on push). Every service below has a
free tier and none requires a credit card.

```
Browser ──> Vercel (Frontend/, static)
                │  /api/* proxied to ──> Render (FastAPI + pipeline)
                                           │        │
                                    Supabase     Cloudinary
                                    (jobs, users, (final mp4s,
                                     chats, vids)  permanent URLs)
```

## 0. Before you start — secrets hygiene

- **Never commit `.env` or `apihere.md`** (both are gitignored; `apihere.md`
  holds live API keys and must never leave your machine).
- All real keys live ONLY in the Render dashboard env vars (server side).
  The frontend gets zero secrets — it talks to `/api/*` on its own origin.
- If a key was ever pasted into a chat, a screenshot, or a shared file,
  rotate it at the provider (OpenAI / DeepSeek / Gemini).

## 1. Push the repo to GitHub

The backend deploys from this repository; remote `origin` should already
point at `github.com/sudish80/Phiversity`.

```bash
git add -A && git commit -m "Add cloud deployment (FastAPI, Supabase, Cloudinary, worker)"
git push origin main
```

## 2. Supabase — the database (free)

1. Create an account at <https://supabase.com> and **New project**
   (any name, any region, save the DB password somewhere safe).
2. Open **SQL Editor → New query**, paste the whole of
   `supabase/schema.sql` from this repo, **Run**. This creates the
   `users`, `jobs`, `videos`, `chats`, `lectures` tables with RLS
   policies and indexes.
3. Collect three values (**Project Settings → API**):
   - `Project URL`                → `SUPABASE_URL`
   - `service_role` secret key    → `SUPABASE_SERVICE_KEY` (server only!)
   - `anon` public key            → `SUPABASE_ANON_KEY` (safe for browsers)

## 3. Cloudinary — video storage (free)

1. Create a free account at <https://cloudinary.com>.
2. Dashboard → copy `Cloud name`, `API Key`, `API Secret`.

Finished lecture mp4s are uploaded here as
`phiversity/<slug>/lecture`, and lecture rows point at the permanent
Cloudinary URL (Render's free disk is ephemeral — this is why the
upload matters).

## 4. Render — the backend (free)

1. Create an account at <https://render.com> (GitHub login).
2. **New + → Web Service → connect the GitHub repo.**
3. Settings:
   - **Runtime:** Docker
   - **Root Directory:** (leave blank — the Dockerfile is at the repo root)
   - **Plan:** Free
   - **Health Check Path:** `/health`
4. **Environment variables** (add all that you use):

   | Key | Value |
   |---|---|
   | `LLM_API_KEY` | your provider key (OpenAI / NVIDIA / DeepSeek-compatible) |
   | `LLM_BASE_URL` | e.g. `https://api.openai.com/v1` (optional for OpenAI) |
   | `LLM_MODEL` | e.g. `gpt-4o-mini` |
   | `PHIVERSITY_PROVIDER` | `openai` (or `anthropic`) |
   | `PHIVERSITY_VOICE` | `en-US-AriaNeural` |
   | `SUPABASE_URL` | from step 2 |
   | `SUPABASE_SERVICE_KEY` | from step 2 (server-side only) |
   | `SUPABASE_ANON_KEY` | from step 2 |
   | `CLOUDINARY_CLOUD_NAME` | from step 3 |
   | `CLOUDINARY_API_KEY` | from step 3 |
   | `CLOUDINARY_API_SECRET` | from step 3 (server-side only) |
   | `ALLOWED_ORIGINS` | your Vercel URL, e.g. `https://phiversity.vercel.app` (or `*`) |
   | `PHIVERSITY_INLINE_WORKER` | `1` (render inside this service) |

5. **Create Web Service** and wait for the first build (the Docker image
   includes Manim, ffmpeg and a compact LaTeX — the first build takes a
   few minutes; later pushes rebuild only what changed).
6. Verify: open `https://<your-service>.onrender.com/health` →
   `{"status": "ok", "store": "supabase", "cdn": "cloudinary", ...}`.

Free-tier notes:
- The service **sleeps after ~15 min idle**; the first request then waits
  ~50 s (cold start). The frontend keeps it awake while a job runs
  (it polls every 2 s).
- CPU is shared: renders are slower than your machine. Prefer
  `quality: "l"` and 3–5 segments.
- The disk is wiped on every deploy/restart — queued jobs survive in
  Supabase and are re-run; finished videos live on Cloudinary.

## 5. Vercel — the frontend (free)

1. **Before deploying:** open `Frontend/vercel.json` and replace
   `REPLACE-WITH-YOUR-BACKEND` with your Render URL
   (e.g. `https://phiversity-api-abcd.onrender.com`). Commit + push.
2. <https://vercel.com> → **Add New → Project** → import the repo.
3. Settings:
   - **Root Directory:** `Frontend`
   - **Framework Preset:** Other
   - **Build Command / Output:** none (it is a static site)
4. Deploy. No env vars — the frontend has no secrets; `/api/*` is
   proxied to Render by the rewrite in `vercel.json`, so the existing
   pages (`lf.get/lf.post`, job polling, players) keep working unchanged.

## 6. End-to-end verification checklist

1. Open the Vercel site → `/health` reachable through the proxy
   (`https://<site>/api/status` shows `store: supabase`).
2. Create a lecture from a **bundled topic** (e.g. Pythagoras) — this
   proves the renderer works without any LLM key.
3. Ask a real **question** — proves the LLM plan/code path.
4. Watch the job progress page (stages plan → speak → code → render →
   compose, live log tail).
5. The finished video plays **directly from Cloudinary**
   (`res.cloudinary.com/...` in the player source).
6. Delete a lecture in the library → the Cloudinary asset is destroyed.
7. Save a chat thread, reload, reopen it (Supabase persistence).
8. Redeploy the Render service → lectures list survives (Supabase).

## 7. Optional: split the renderer into its own worker

When the API service should stay light (or you move to paid capacity):

1. Set `PHIVERSITY_INLINE_WORKER=0` on the web service.
2. Add a Render **Background Worker** (paid) — or any VPS — running the
   same image with the command:

   ```
   phiversity-worker --poll 5
   ```

   with the same `SUPABASE_*`, `LLM_*` and `CLOUDINARY_*` env vars.
   It claims queued jobs atomically (two workers never take the same
   job) and uploads to Cloudinary exactly like the inline path.

## 8. Troubleshooting

| Symptom | Cause / fix |
|---|---|
| 502/504 right after idle | free-tier cold start; retry after ~50 s |
| `store: sqlite` in /health | `SUPABASE_URL`/`SUPABASE_SERVICE_KEY` not set |
| `cdn: local-disk` | Cloudinary env vars missing; videos die on redeploy |
| Job stuck `queued` | inline worker off but no `phiversity-worker` running |
| `error_message: LLM_API_KEY` | no key set, or the base URL/model mismatch |
| edge-tts failures | outbound network is required for Microsoft neural TTS |
| CORS errors in the browser | add the exact Vercel origin to `ALLOWED_ORIGINS` |
| Uploads fail on Render | video too large: lower `quality` or fewer segments |
