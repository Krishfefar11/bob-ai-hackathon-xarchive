# AGENTS.md — Project Context for IBM Bob IDE

## Project

Drug Safety Signal Detector & Regulatory Submission Readiness Checker — IBM Bob Hackathon, Problem P2.

Two modes in one Streamlit app:
1. **Signal Detector** — pulls FDA adverse event reports (OpenFDA API or FAERS quarterly files), computes PRR/ROR disproportionality analysis, flags safety signals per Evans et al. (2001) criteria.
2. **Submission Checker** — parses an uploaded CTD module document (PDF/DOCX/TXT) and checks it against the ICH M4 CTD structure, reporting missing sections.

## Architecture

```
src/
├── ingestion/           # OpenFDA API client + FAERS quarterly file loader → flat (report, drug, reaction) DataFrame
├── signal_detection/    # PRR + ROR calculation, plain-language + optional LLM signal explanations
├── submission_checker/  # ICH M4 CTD schema, document text/section extraction, gap analysis
├── llm/                 # IBM watsonx.ai client + prompt templates (optional — falls back to templates without credentials)
├── app/                 # Streamlit UI (main.py entry point, one module per mode)
└── api/                 # FastAPI service exposing the two tools over REST/OpenAPI, for watsonx Orchestrate (see ORCHESTRATE.md)
```

Both ingestion paths (`ingestion.openfda_client`, `ingestion.faers_loader`) converge on the same schema: one row per `(report_id, drug, reaction, serious)`, which is what `signal_detection.prr` / `.ror` expect.

## Key files

- [src/signal_detection/prr.py](src/signal_detection/prr.py) — core PRR/chi-squared algorithm (Evans et al. 2001)
- [src/submission_checker/ctd_schema.py](src/submission_checker/ctd_schema.py) — ICH M4 CTD module/section reference structure
- [src/app/main.py](src/app/main.py) — Streamlit entry point (`streamlit run src/app/main.py`)
- [CLAUDE.md](CLAUDE.md) — full problem statement, hackathon rules, and build plan this project follows

## Conventions

- All cross-package imports are absolute (`from signal_detection.prr import calculate_prr`), resolved via `src/` being added to `sys.path` in `src/app/main.py` and `conftest.py`.
- watsonx.ai credentials are optional; code that depends on them fails gracefully (see `llm.watsonx_client.WatsonxConfigError`) rather than crashing the app.
- No client data, PI, or social-media-sourced data — only public FDA FAERS/OpenFDA data (see `CLAUDE.md` §3).

## Status

Full build complete: ingestion, PRR/ROR engine, CTD gap analyzer, Streamlit UI, FastAPI tool layer for Orchestrate, and tests (10/10 passing). Not yet done: real Bob IDE session usage (`bob_sessions/` reports — see that folder's README), watsonx.ai credential wiring (needs a real IBM Cloud API key in `.env`), and the actual Orchestrate console setup (needs your IBM Cloud account — see [ORCHESTRATE.md](ORCHESTRATE.md)).
