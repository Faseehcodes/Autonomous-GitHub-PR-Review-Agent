# Start Here

This project is the backend for your AI GitHub PR Review Agent.

You do not need to paste code manually if you open this folder in VS Code:

```text
C:\Users\fasee\Documents\Codex\2026-05-12\files-mentioned-by-the-user-prd
```

## 1. Install Python 3.11

Install Python 3.11 from:

```text
https://www.python.org/downloads/release/python-3119/
```

During install, tick:

```text
Add python.exe to PATH
```

## 2. Open Project in VS Code

1. Open VS Code.
2. Click `File`.
3. Click `Open Folder`.
4. Select:

```text
C:\Users\fasee\Documents\Codex\2026-05-12\files-mentioned-by-the-user-prd
```

## 3. Create Virtual Environment

Open the VS Code terminal:

```text
Terminal > New Terminal
```

Run:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, run this once:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

Then activate again:

```powershell
.\.venv\Scripts\Activate.ps1
```

## 4. Install Packages

Run:

```powershell
pip install -r requirements.txt
```

## 5. Create Your `.env` File

Copy `.env.example` and rename the copy to `.env`.

Fill these values first:

```env
GITHUB_APP_SECRET=make_any_random_secret_here
GITHUB_TOKEN=your_github_token_here
GROQ_API_KEY=your_groq_api_key_here
GROQ_TRIAGE_MODEL=llama-3.1-8b-instant
GROQ_ANALYSIS_MODEL=llama-3.3-70b-versatile
GROQ_SECURITY_MODEL=llama-3.3-70b-versatile
GOOGLE_API_KEY=
SUPABASE_URL=
SUPABASE_SERVICE_KEY=
```

You can leave Google and Supabase empty for the first backend run.

## 6. Run Backend

Run:

```powershell
uvicorn main:app --reload --port 8000
```

Open this in your browser:

```text
http://127.0.0.1:8000/health
```

You should see:

```json
{"status":"ok"}
```

## 7. What Each Folder Means

```text
agent/
```

The AI review brain. It controls triage, analysis, security review, and posting comments.

```text
api/
```

The FastAPI endpoints. GitHub sends PR webhook events here.

```text
services/
```

Helper code for GitHub, Groq, and diff splitting.

```text
models/
```

Data shapes for reviews and repositories.

```text
tests/
```

Small tests to make sure helper logic works.

## 8. Next Step After Backend Runs

To test real GitHub webhooks locally, install ngrok and run:

```powershell
ngrok http 8000
```

Then use the ngrok URL as your GitHub webhook URL:

```text
https://your-ngrok-url.ngrok-free.app/webhook/github
```

## 9. Supabase Setup

Open Supabase SQL Editor and paste the contents of:

```text
supabase_schema.sql
```

Then click `Run`.

The backend will save review history automatically when `SUPABASE_URL` and `SUPABASE_SERVICE_KEY` are filled in `.env`.
