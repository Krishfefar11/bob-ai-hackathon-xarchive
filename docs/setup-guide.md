# Setup Guide

> **This file is read by the automated evaluation pipeline. Be precise and complete.**

## Prerequisites

- [x] Python 3.10+
- [ ] An IBM Cloud account with watsonx.ai access — **optional**, only needed for LLM-generated signal explanations; everything else works without it
- No database, Node.js, or Docker required

## Environment Variables

Copy `.env.example` to `.env` and fill in the values (only needed if you want watsonx.ai explanations):

```bash
cp .env.example .env
```

| Variable | Description | Required |
|---|---|---|
| `WATSONX_API_KEY` | IBM watsonx.ai API key | No — falls back to template-based explanations |
| `WATSONX_PROJECT_ID` | IBM watsonx.ai project ID | No |
| `WATSONX_URL` | watsonx.ai endpoint (default `https://us-south.ml.cloud.ibm.com`) | No |
| `OPENFDA_API_KEY` | OpenFDA API key | No — anonymous access works, just capped at 500 records/call instead of 1000 |

## Installation

```bash
# 1. Clone the repository
git clone https://github.com/Krishfefar11/bob-ai-hackathon-xarchive.git
cd bob-ai-hackathon-xarchive

# 2. Create a virtual environment and install dependencies
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

There is no separate frontend install step and no database migration step — this is a single Python project with no other services.

## Running the Application

```bash
# Start the Streamlit dashboard (both modes live here)
streamlit run src/app/main.py
```

The application will be available at: `http://localhost:8501`

Optionally, also run the FastAPI tool layer (used for the watsonx Orchestrate integration, not required to use the app itself):

```bash
uvicorn api.main:app --app-dir src --port 8000
```

Available at `http://localhost:8000`, with interactive docs at `http://localhost:8000/docs`.

## Running Tests

```bash
pytest
```

All tests run offline against synthetic fixtures (no live OpenFDA calls), so this works without network access or any credentials.

## Quick Demo (Optional)

1. Open `http://localhost:8501`.
2. On the **Signal Detector** tab, click one of the quick-pick buttons (ASPIRIN / IBUPROFEN / METFORMIN / WARFARIN) — it fetches live OpenFDA data and runs the PRR engine automatically.
3. On the **Submission Checker** tab, upload any PDF/DOCX/TXT that has numbered section headings (e.g. a draft CTD module) to see the completeness scoring.

## Troubleshooting

| Issue | Solution |
|---|---|
| `ModuleNotFoundError` on startup | Run `pip install -r requirements.txt` again inside the activated venv |
| Signal Detector fetch is slow (20-30s) | Expected — OpenFDA's own API takes 10-20s per 500-record page; this is upstream API latency, not the app |
| `403 API_KEY_MISSING` from OpenFDA | Anonymous requests are capped at 500 records/call; either lower "Reports to fetch" or set `OPENFDA_API_KEY` in `.env` |
| watsonx.ai explanations don't appear even with the checkbox on | Confirm `WATSONX_API_KEY` and `WATSONX_PROJECT_ID` are set in `.env` — without them the app silently falls back to template explanations by design, it does not error |
| `streamlit: command not found` | Make sure the virtual environment is activated (`source venv/bin/activate`) before running |
