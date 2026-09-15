# Solution Overview

## What We Built

A two-mode pharma/regulatory tool, available both as a Streamlit dashboard and as a REST/OpenAPI service for IBM watsonx Orchestrate.

**Mode 1 — Signal Detector.** Given a drug name, fetch real adverse event reports from OpenFDA, compute Proportional Reporting Ratio (PRR) and Reporting Odds Ratio (ROR) disproportionality statistics for every drug-event pair, and flag the ones that meet the Evans et al. (2001) signal criteria.

**Mode 2 — Submission Checker.** Given a draft regulatory document (PDF, DOCX, or TXT), detect which ICH M4 CTD sections it contains and score completeness per module, with a downloadable gap report listing exactly what's missing.

## How It Works

**Signal Detector:**
1. The user enters a drug name (or picks a quick example — aspirin, ibuprofen, metformin, warfarin).
2. `ingestion.openfda_client` pages through the OpenFDA adverse-event API, flattening each report into `(report_id, drug, reaction, serious)` rows.
3. `signal_detection.prr` builds a 2×2 contingency table for every observed drug-event pair (vectorized over the whole dataset, not a nested Python loop) and computes PRR and a closed-form chi-squared statistic.
4. Pairs meeting PRR≥2, χ²≥4, and n≥3 are flagged as signals, assigned a risk band, and given a plain-language explanation (template-based by default, or watsonx.ai-generated if credentials are configured).
5. The UI scopes the *displayed* signal table to the searched drug specifically — OpenFDA's search matches a drug name appearing anywhere on a report, not only as primary suspect, so unrelated drugs can otherwise leak into the results.

**Submission Checker:**
1. The user uploads a document.
2. `submission_checker.document_parser` extracts text (PyPDF2 for PDF, python-docx for DOCX) and detects section-number headings via a pattern anchored to line starts, tolerant of both the "2.3 Title" and official ICH-style "2.3. Title" (trailing-period) formats, and normalized against PDF extraction losing real line breaks.
3. `submission_checker.gap_analyzer` checks the detected headings against `ctd_schema.CTD_SCHEMA` (the ICH M4 module/section structure) and computes completeness per module and overall.

## Key Design Decisions

| Decision | Rationale |
|---|---|
| Vectorized PRR/chi-squared over the whole dataset, not a per-pair scipy call | FAERS-scale data (millions of rows) makes an O(pairs) loop impractically slow; a closed-form 2×2 chi-squared formula computed over numpy arrays handles the same math in one pass |
| Scope the displayed signal table to the searched drug | OpenFDA's search isn't restricted to primary-suspect matches, so a naive "show every drug in the pull" view surfaces unrelated drugs as false "top signals" — confirmed by testing (an aspirin search initially surfaced an unrelated antibiotic as the #1 signal) |
| Anchor CTD heading detection to line starts, not "appears anywhere" | A document that merely *discusses* the CTD format (e.g. a guideline explaining what goes in each section) mentions nearly every section number in prose — treating any occurrence as "present" scores such a document as a 100%-complete dossier, which is wrong |
| LLM explanations are optional with a template fallback | The tool must work end-to-end without any IBM Cloud credentials configured, since those are hackathon-provisioned and time-limited |
| Expose both modes as a FastAPI/OpenAPI service in addition to the Streamlit UI | watsonx Orchestrate imports custom tools from an OpenAPI spec — this is the actual integration contract, not something wired through the UI |

## IBM Technologies Used

- **watsonx.ai** (`src/llm/watsonx_client.py`): wraps `ibm_watsonx_ai.foundation_models.ModelInference` to generate plain-language signal explanations from a detected PRR/χ² result, using the recommended `granite-3-8b-instruct` model. Used only when `WATSONX_API_KEY`/`WATSONX_PROJECT_ID` are configured; the app is fully functional without it.
- **watsonx Orchestrate**: the FastAPI service in `src/api/` exposes `/signals/detect` and `/submission/check` with an auto-generated OpenAPI spec, which Orchestrate can import as agent tools. See [ORCHESTRATE.md](../ORCHESTRATE.md) for the console-side setup (that part requires an IBM Cloud account and hasn't been completed yet).
- **IBM Bob IDE**: primary intended development tool per the hackathon rules; see `bob_sessions/` and [AGENTS.md](../AGENTS.md).
