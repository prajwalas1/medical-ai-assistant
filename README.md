# ABC Hospital — AI Voice Appointment Assistant

**Live Demo:** [https://medical-ai-assistant-puce.vercel.app/](https://medical-ai-assistant-puce.vercel.app/)
**GitHub Repository:** [https://github.com/prajwalas1/medical-ai-assistant](https://github.com/prajwalas1/medical-ai-assistant)
**Backend API:** [https://medical-ai-assistant-rx70.onrender.com/](https://medical-ai-assistant-rx70.onrender.com/)
**API Documentation:** [https://medical-ai-assistant-rx70.onrender.com/docs](https://medical-ai-assistant-rx70.onrender.com/docs)

An AI-powered voice receptionist for a hospital, built with [LiveKit Agents](https://docs.livekit.io/agents/), FastAPI, and React. Patients can call in (via a web client) and book, cancel, reschedule, or check appointment availability entirely by voice — in English, Hindi, or Kannada.

## Features

- **Real-time voice conversation** — speech-to-text, LLM reasoning, and text-to-speech, all streamed live over WebRTC via LiveKit.
- **Multilingual support** — English, Hindi, and Kannada, selectable before the call starts.
- **Appointment management via natural conversation:**
  - Book a new appointment (new or returning patient)
  - Cancel an existing appointment
  - Reschedule an existing appointment
  - Check doctor availability by specialization, date, and time
  - General hospital FAQs (hours, location, emergency services, contact info)
- **Tool-calling architecture** — the LLM never invents appointment IDs, doctor availability, or booking confirmations; every action is backed by a real database call.
- **Returning-patient recognition** — looks up patients by phone number and reuses stored name/age/gender instead of asking again.

## Architecture

```
┌─────────────┐      LiveKit token       ┌──────────────────┐
│   Frontend  │ ───────────────────────► │   FastAPI Backend │
│ (React/Vite)│ ◄─────────────────────── │  (token issuing,  │
└──────┬──────┘                          │   REST endpoints) │
       │                                 └──────────────────┘
       │ WebRTC (audio)                            │
       ▼                                            │ SQLAlchemy
┌─────────────────┐                                 ▼
│  LiveKit Cloud   │                        ┌───────────────┐
│   (room/SFU)     │                        │  PostgreSQL   │
└────────┬─────────┘                        │    (Neon)     │
         │ job dispatch                     └───────────────┘
         ▼
┌────────────────────────────┐
│   LiveKit Agent Worker      │
│  (Python, always-on)        │
│                              │
│  STT  → Sarvam Saarika       │
│  LLM  → Sarvam / Cerebras /  │
│         OpenAI (pluggable)   │
│  TTS  → Sarvam Bulbul        │
│  Tools → book/cancel/        │
│          reschedule/lookup   │
└────────────────────────────┘
```

## Tech Stack

**Backend**
- FastAPI — REST API (LiveKit token issuing, patient/doctor/appointment endpoints)
- LiveKit Agents SDK — real-time voice agent runtime
- SQLAlchemy + PostgreSQL (Neon) — persistence
- Sarvam AI — Speech-to-Text (`saarika:v2.5`) and Text-to-Speech (`bulbul:v3`)
- LLM (pluggable): Sarvam (`sarvam-105b` / `sarvam-30b`), Cerebras (`zai-glm-4.7`, `gpt-oss-120b`), or OpenAI (`gpt-4o-mini`)
- `uv` — Python dependency management

**Frontend**
- React + TypeScript + Vite
- Tailwind CSS
- `livekit-client` — WebRTC room connection, audio publish/subscribe

## Prerequisites

- Python 3.12+
- [`uv`](https://docs.astral.sh/uv/) installed
- Node.js 18+
- A [LiveKit Cloud](https://cloud.livekit.io/) project (URL, API key, API secret)
- A [Sarvam AI](https://www.sarvam.ai/) API key (STT/TTS, and optionally LLM)
- A PostgreSQL database (e.g. [Neon](https://neon.tech/))
- (Optional) A [Cerebras](https://cloud.cerebras.ai/) or [OpenAI](https://platform.openai.com/) API key if using either as the LLM provider

## Setup

### Backend

```bash
cd backend
uv sync
```

Create a `.env` file in `backend/`:

```env
DATABASE_URL=postgresql://user:password@host/dbname
CEREBRAS_API_KEY=your_cerebras_key      # optional, only if using Cerebras LLM
OPENAI_API_KEY=your_openai_key          # optional, only if using OpenAI LLM
SARVAM_API_KEY=your_sarvam_key

LIVEKIT_URL=wss://your-project.livekit.cloud
LIVEKIT_API_KEY=your_livekit_api_key
LIVEKIT_API_SECRET=your_livekit_api_secret
```

Create the database tables:
```bash
uv run python -m app.database.create_tables
```

Run the FastAPI server (issues LiveKit tokens, serves REST endpoints):
```bash
uv run uvicorn app.main:app --reload
```

Run the LiveKit voice agent worker (in a **separate terminal**, must stay running to receive calls):
```bash
uv run python -m app.livekit.agent dev
```

### Frontend

```bash
cd frontend
npm install
```

Create a `.env` file in `frontend/` if your token endpoint isn't on the default local URL:
```env
VITE_API_BASE_URL=http://localhost:8000
```

Run the dev server:
```bash
npm run dev
```

Open the app, choose a language, and click **Start Call**.

## Project Structure

```
backend/
  app/
    ai/               # (unused legacy) LLM extraction pipeline — see note below
    api/v1/           # REST routes: patient, doctor, appointment, livekit_token, health
    core/             # settings/config
    database/         # SQLAlchemy engine, session, table creation
    enums/            # DoctorSpecialization, Gender, AppointmentStatus
    livekit/
      agent.py        # ★ the actual voice agent entrypoint (LiveKit AgentSession)
    models/           # SQLAlchemy ORM models
    schemas/           # Pydantic request/response schemas
    services/         # DB-facing business logic (appointment/doctor/patient)
    utils/            # date/time parsing helpers
  main.py             # FastAPI app entrypoint

frontend/
  src/
    components/VoiceAssistant/  # LanguageSelector, ListeningAnimation, VoiceControls
    hooks/useVoice.ts           # LiveKit room connection, mic publish, agent-state tracking
    pages/Home.tsx              # main UI
    services/livekit.ts         # fetches LiveKit token from backend
```

> **Note:** `app/ai/`, `app/livekit/backend_llm.py`, `app/livekit/hospital_agent.py`, and `app/voice/` are an earlier, superseded text-based conversation pipeline kept only for reference — the live product path is entirely through `app/livekit/agent.py`.

## Switching LLM Providers

The agent's LLM is configured in `app/livekit/agent.py` inside `entrypoint()`. Swap the `llm=` argument to change providers:

```python
# Sarvam (free)
llm=sarvam.LLM(model="sarvam-105b", temperature=0)

# Cerebras (free tier, rate-limited)
llm=cerebras.LLM(model="zai-glm-4.7", api_key=settings.CEREBRAS_API_KEY, temperature=0)

# OpenAI (paid, most reliable for tool-calling)
llm=openai.LLM(model="gpt-4o-mini", api_key=settings.OPENAI_API_KEY, temperature=0)
```

## Deployment

- **Frontend:** deployed on [Vercel](https://vercel.com/) — static React build.
- **LiveKit:** hosted on [LiveKit Cloud](https://cloud.livekit.io/) — a managed service, not something you deploy yourself. Both the local agent worker and the deployed Render agent worker connect to the same LiveKit Cloud project via `LIVEKIT_URL`/`LIVEKIT_API_KEY`/`LIVEKIT_API_SECRET`, so these three values must be set identically (as environment variables) on every environment/service that runs `app.livekit.agent` or issues tokens.
- **Backend:** deployed on [Render](https://render.com/) as **two separate services**, since the project has two independent long-running processes:

### 1. FastAPI API (Render Web Service)
- **Root Directory:** `backend`
- **Build Command:** `uv sync`
- **Start Command:** `uv run uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- **Environment variables:** same as `backend/.env` (`DATABASE_URL`, `SARVAM_API_KEY`, `LIVEKIT_URL`, `LIVEKIT_API_KEY`, `LIVEKIT_API_SECRET`, and whichever LLM key(s) you're using)
- Free tier is acceptable here — this service just issues tokens and serves REST endpoints, so occasional cold-start delay after inactivity is fine.
- Live URL: `https://<your-render-service>.onrender.com`

### 2. LiveKit Agent Worker (Render Background Worker)
- **Root Directory:** `backend`
- **Build Command:** `uv sync`
- **Start Command:** `uv run python -m app.livekit.agent start`
- **Environment variables:** same as above
- This process must stay **always-on** (registered with LiveKit Cloud, waiting for job dispatches) — Render's free web-service tier sleeps after inactivity and will miss incoming calls, so this service needs a paid always-on plan (Starter tier or above).

> Note: use the `start` subcommand (not `dev`) for the agent worker in production — `dev` is intended for local development with verbose logging.

Update the frontend's token-fetch URL (`frontend/src/services/livekit.ts` or its `VITE_API_BASE_URL` env var) to point at the deployed FastAPI service's Render URL instead of `localhost`.

## Known Limitations

- Free-tier LLM providers (Sarvam free tier, Cerebras Preview models) may hit rate limits or transient congestion under load.
- No authentication/authorization on the REST API — intended for demo/assignment purposes.
- Appointment booking does not currently check for double-booking conflicts at the same date/time.

## License

This project was built for an assignment/demo purpose. Add a license of your choice if distributing further.
