# 🚀 Drug Safety Signal Detector & Regulatory Submission Readiness Checker

---

## 👥 Team

| Field | Value |
|---|---|
| **Team Name** | TODO — fill in before final submission |
| **Track** | AI |
| **Team Lead** | TODO — drashtifefar7777@gmail.com |
| **Members** | TODO |

---

## 🎯 Problem Statement

FDA's FAERS database holds 20M+ adverse event reports that pharmacovigilance teams must manually sift through to catch safety signals — a process that takes weeks (Vioxx caused 27,000+ heart attacks before its signal was acted on). Separately, regulatory affairs teams assemble 100,000+ page CTD drug approval dossiers across 5 modules, where a single missing section causes rejection, costing 6–12 months and $50–100M. Both problems share the same root cause: too much complex data for manual review.

---

## 💡 Solution

A two-mode tool built on real FDA/ICH data. **Signal Detector** pulls live OpenFDA adverse event reports for a drug and runs Proportional Reporting Ratio (PRR) + Reporting Odds Ratio (ROR) disproportionality analysis, flagging drug-event pairs that meet the Evans et al. (2001) signal criteria (PRR≥2, χ²≥4, n≥3). **Submission Checker** parses a draft regulatory document and checks it against the ICH M4 CTD structure, scoring completeness per module and producing a gap report.

---

## ✨ Key Features

- **Live PRR + ROR signal detection** against real OpenFDA data, using the Evans et al. (2001) criteria
- **Per-module CTD completeness scoring** (not just one overall number) with a downloadable gap report
- **Interactive Streamlit dashboard** — risk-filterable signal tables, Plotly charts color-coded by risk, CSV export
- **FastAPI + OpenAPI tool layer** for wiring both modes into IBM watsonx Orchestrate as agent-callable tools
- **Optional watsonx.ai plain-language explanations** of detected signals, with a safe template fallback

---

## 🛠️ Tech Stack

| Category | Technologies |
|---|---|
| **Languages** | Python |
| **Frameworks** | Streamlit, FastAPI, Plotly |
| **IBM Technologies** | watsonx.ai (`ibm-watsonx-ai` SDK), watsonx Orchestrate (via OpenAPI tool import) |
| **Databases** | None — stateless, queries OpenFDA/FAERS live |
| **Other** | pandas, numpy, scipy, OpenFDA REST API, PyPDF2, python-docx, pytest |

---

## 📁 Repository Structure

```
├── src/                  # All source code (see src/README.md)
├── docs/                 # Written documentation
│   ├── problem-statement.md
│   ├── solution-overview.md
│   ├── architecture.md
│   └── setup-guide.md
├── demo/                 # Demo artifacts
│   ├── screenshots/      # App screenshots
│   └── demo-video-link.txt  # Link to demo video
├── presentation/         # Slide deck
├── AGENTS.md             # Architecture/context reference for AI dev tools (Bob, Claude, etc.)
├── ORCHESTRATE.md        # How to wire the FastAPI tool layer into watsonx Orchestrate
└── submission.yaml       # Structured submission metadata
```

---

## ⚡ How to Run

```bash
# 1. Clone the repo
git clone https://github.com/Krishfefar11/bob-ai-hackathon-xarchive.git
cd bob-ai-hackathon-xarchive

# 2. Install dependencies
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 3. Configure environment (optional — only needed for watsonx.ai LLM explanations)
cp .env.example .env

# 4. Run the Streamlit app
streamlit run src/app/main.py

# (Optional) Run the FastAPI tool layer for watsonx Orchestrate
uvicorn api.main:app --app-dir src --port 8000
```

Full details, including troubleshooting, in [`docs/setup-guide.md`](docs/setup-guide.md).

---

## 🖥️ Demo

| Artifact | Link |
|---|---|
| 📹 Demo Video | [See demo/demo-video-link.txt](demo/demo-video-link.txt) — TODO, not recorded yet |
| 🌐 Live Demo | [See demo/live-demo-url.txt](demo/live-demo-url.txt) |
| 🖼️ Screenshots | [See demo/screenshots/](demo/screenshots/) — TODO, not added yet |
| 📊 Presentation | [See presentation/slides.pdf](presentation/) — TODO, not added yet |

---

## ⚠️ Known Limitations

- `bob_sessions/` is not yet populated — that requires real IBM Bob IDE usage, which hasn't happened yet
- The watsonx.ai LLM-explanation path is implemented but untested with real credentials (falls back to template explanations without them)
- The watsonx Orchestrate console wiring (importing the tool, building the agent) still needs to be done manually in the IBM Cloud console — see [ORCHESTRATE.md](ORCHESTRATE.md)
- The CTD checker detects section headings structurally and cannot distinguish an actual filled-in dossier from a reference document that merely tabulates the same section numbers (confirmed against a real EMA guideline PDF during testing)
- No demo video or slide deck yet

---

## 🏅 What We're Most Proud Of

The signal-detection engine wasn't just implemented — it was validated live against real FDA data during development: aspirin correctly surfaces GI-bleeding-adjacent signals, warfarin correctly flags 15 bleeding-related reactions (PRR 2.5–35), and an SSRI (citalopram) correctly shows the right-direction QT-prolongation signal. We also caught and fixed three real bugs by testing against live data and a real EMA regulatory PDF rather than trusting the code on paper: an OpenFDA anonymous rate-limit issue, a drug-attribution leak in the signal table, and a CTD-heading false-positive/false-negative pair in the document parser.

---
