# CLAUDE.md — IBM Bob Hackathon: Problem P2
## Drug Safety Signal Detector & Regulatory Submission Readiness Checker

> **This file is a complete briefing for Claude Code.**  
> Read it fully before writing a single line of code. Everything you need to understand the problem, follow the hackathon rules, find real data, and build a working solution is here.

---

## 1. THE PROBLEM (P2) — Full Statement

**Domain:** Pharma & Biotech  
**Problem ID:** P2  
**Title:** Drug Safety Signal Detector & Regulatory Submission Readiness Checker

### What you must build

A system with **two modes**:

**Mode 1 — Drug Safety Signal Detector**  
Ingest FDA adverse event reports and automatically detect safety signals for drug-event pairs using Proportional Reporting Ratio (PRR) or similar disproportionality analysis. The system should flag signals above regulatory thresholds and explain what they mean in plain language.

**Mode 2 — Regulatory Submission Readiness Checker**  
Given a draft regulatory document (e.g., a CTD module section), check it against the ICH M4 Common Technical Document (CTD) structure to verify completeness, flag missing sections, and summarize gaps.

### Why this matters

Pharmacovigilance teams manually sift through millions of adverse event reports to find safety signals — a process that takes weeks. Regulatory affairs teams spend huge effort checking submission documents are structurally complete before filing. This tool automates both.

---

## 2. IBM BOB IDE — MANDATORY RULES

> **IBM Bob IDE is NOT optional.** The judging criteria require it as a core component. A solution that doesn't use Bob cannot win.

### What Bob Is

IBM Bob is an AI-powered IDE partner that:
- Reads your entire repository context
- Generates documentation and tests
- Automates developer tasks via chat
- Supports Plan, Code, Advanced, Ask, and Orchestrator modes
- Uses **Bobcoins** (credits) for each AI interaction

### Bobcoin Budget

- **40 Bobcoins per team member** — allocated at hackathon start
- **No refills** — once exhausted, no more Bob AI calls
- Plan carefully; use Bob for high-value tasks (architecture, complex logic, documentation)
- If Bobcoins run out, you may fall back to the optional watsonx services (see Section 6)

### REQUIRED: Bob Task Session Reports

Every team member must:
1. Complete tasks using Bob IDE
2. **Export the Bob task session report** after each significant task
3. Place all exported reports in a folder called **`bob_sessions/`** in the root of your code repository
4. This folder **must be present** for judging eligibility

### AGENTS.md / `/init`

Bob uses `AGENTS.md` (or you can run `/init`) to load persistent project context across conversations. Create this file early with project summary, key file paths, and architecture decisions so Bob understands your codebase without re-explaining it every session.

### Bob Modes

| Mode | Use For |
|------|---------|
| Plan | Architecture decisions, breaking down tasks |
| Code | Writing and editing code with repo context |
| Advanced | Complex multi-step implementations |
| Ask | Quick questions about code, docs, APIs |
| Orchestrator | Coordinating multi-agent workflows |

### SECURITY — Critical

**Before exporting task session reports or pushing to a public repo:**
- Remove ALL credentials, API keys, and secrets from code
- IBM Security actively scans public repositories
- **Accounts will be permanently deactivated if credentials are detected**
- Use `.env` files and add `.env` to `.gitignore` — never hardcode keys

---

## 3. HACKATHON DATA RULES

These rules are from the official IBM Bob Hackathon Guide. You must comply:

1. **Do not use any client data.**
2. **Do not use any data containing personal information (PI).**
3. **Do not use data obtained from social media.**
4. **Do not use data or assets containing company confidential data, or any other data without permission from the data owner.**
5. **Teams are responsible for ensuring all data used is compliant.**

> **Good news:** FDA FAERS is a public government database with no PI and explicit open-data terms. All datasets listed in Section 4 are safe to use.

---

## 4. DATASETS — ALL LINKS

### 4A. FDA FAERS — Primary Dataset (Mode 1)

**FDA Adverse Event Reporting System (FAERS)** — The canonical source. 20M+ adverse event reports from 2004 to present.

**Direct download page:**  
https://www.fda.gov/drugs/questions-and-answers-fdas-adverse-event-reporting-system-faers/fda-adverse-event-reporting-system-faers-public-dashboard

**Quarterly ASCII files (zip archives with TSV data):**  
https://fis.fda.gov/extensions/FPD-QDE-FAERS/FPD-QDE-FAERS.html

Download the most recent 1–4 quarters. Each zip contains:
- `DEMO` — demographics (patient age, sex, country, report date)
- `DRUG` — drug info (medicinal product name, role code, route)
- `REAC` — reactions (MedDRA preferred term)
- `OUTC` — outcomes (hospitalization, death, etc.)
- `RPSR` — report sources
- `THER` — therapy dates
- `INDI` — drug indications

Key fields for PRR:
- `primaryid` — unique report ID (join key)
- `caseid` — case identifier
- `drugname` / `prod_ai` — drug name
- `pt` — MedDRA preferred term reaction
- `role_cod` — `PS` = primary suspect drug (most important)

### 4B. OpenFDA REST API (Fastest to Get Running)

No account, no auth key required. Free. Up to 1000 records per call.

**Base URL:**
```
https://api.fda.gov/drug/event.json
```

**Example — get 100 records for aspirin adverse events:**
```
https://api.fda.gov/drug/event.json?search=patient.drug.medicinalproduct:"ASPIRIN"&limit=100
```

**Example — get serious events with a specific reaction:**
```
https://api.fda.gov/drug/event.json?search=patient.reaction.reactionmeddrapt:"myocardial+infarction"+AND+serious:1&limit=100
```

**Key response fields:**
```json
{
  "patient": {
    "drug": [
      {
        "medicinalproduct": "ASPIRIN",
        "drugcharacterization": "1"  // 1=primary suspect, 2=concomitant, 3=interacting
      }
    ],
    "reaction": [
      {
        "reactionmeddrapt": "Myocardial infarction"
      }
    ]
  },
  "receivedate": "20230115",
  "serious": "1",
  "reporttype": "1"
}
```

**Pagination:**
```
https://api.fda.gov/drug/event.json?limit=100&skip=100
```

**Max results per query:** 25,000 (use `skip` to paginate through them)

**Full API docs:** https://open.fda.gov/apis/drug/event/

### 4C. Pre-cleaned Kaggle Datasets

These are FAERS data already cleaned and formatted for analysis — faster to work with than raw FDA downloads:

1. **FDA Adverse Events (FAERS) — Cleaned**  
   https://www.kaggle.com/datasets/ramswaroopbhakar14/fda-adverse-events-faers  
   Pre-joined drug/reaction pairs, 2013–2023, ~2M rows

2. **Drug Adverse Events Dataset**  
   https://www.kaggle.com/datasets/uciml/drug-review-dataset  
   Drug reviews with conditions and ratings

3. **FAERS Drug Safety Signals**  
   https://www.kaggle.com/datasets/aryashah2k/fda-drug-adverse-event-reporting  
   Includes signal analysis starter notebooks

4. **Pharmacovigilance FAERS Dataset**  
   https://www.kaggle.com/datasets/tanveerali/fda-faers-adverse-event-reports  
   Quarterly FAERS data 2019–2022

### 4D. GitHub Repos with Working PRR Code

These repos have working signal detection code you can build on:

1. **faers-signal-detection** — Python PRR/ROR implementation  
   https://github.com/tatonetti-lab/faers-signal-detection

2. **PharmacoBridge** — FAERS signal analysis with OpenFDA  
   https://github.com/zhaobw61/PharmacoBridge

3. **PyVigilance** — Full pharmacovigilance library with PRR, ROR, BCPNN  
   https://github.com/tatonetti-lab/PyVigilance

4. **openFDA-signal-detection** — Disproportionality analysis on OpenFDA API data  
   https://github.com/benoitmarteau/openFDA-signal-detection

### 4E. ICH M4 CTD Guidelines (Mode 2)

The ICH Common Technical Document is a 5-module structure for drug regulatory submissions. Official PDFs:

**ICH M4 Overview:**  
https://www.ich.org/page/multidisciplinary-guidelines#4

**Module 2 — Summaries (most commonly checked):**  
https://www.ich.org/fileadmin/Public_Web_Site/ICH_Products/Guidelines/Multidisciplinary/M4/M4_R4_Guideline.pdf

**Module 3 — Quality (CMC):**  
https://www.ich.org/fileadmin/Public_Web_Site/ICH_Products/Guidelines/Multidisciplinary/M4Q/M4Q_R1_Guideline.pdf

**Module 4 — Nonclinical Study Reports:**  
https://www.ich.org/fileadmin/Public_Web_Site/ICH_Products/Guidelines/Multidisciplinary/M4S/M4S_R2_Guideline.pdf

**Module 5 — Clinical Study Reports:**  
https://www.ich.org/fileadmin/Public_Web_Site/ICH_Products/Guidelines/Multidisciplinary/M4E/M4E_R2_Guideline.pdf

---

## 5. SIGNAL DETECTION — The PRR Algorithm

### Proportional Reporting Ratio (PRR)

PRR measures how disproportionately a drug-event pair is reported compared to all drugs reporting that event.

**Contingency table:**

|  | Target Event | All Other Events |
|--|-------------|-----------------|
| **Target Drug** | a | b |
| **All Other Drugs** | c | d |

**Formula:**
```
PRR = (a / (a + b)) / (c / (c + d))
```

**Chi-squared:**
```
χ² = (a - E)² / E   where E = (a+b)(a+c) / (a+b+c+d)
```

**Signal criteria (Evans et al.):**
- PRR ≥ 2
- χ² ≥ 4
- a ≥ 3 (at least 3 reports of the drug-event pair)

All three conditions must be met to flag a signal.

**Interpretation:**
- PRR = 1.0 → No disproportionate reporting
- PRR = 3.5 → Drug X is reported with Event Y 3.5× more often than expected
- PRR ≥ 2 + χ² ≥ 4 + a ≥ 3 → **Signal detected — review required**

### Alternative: Reporting Odds Ratio (ROR)

```
ROR = (a/b) / (c/d) = (a*d) / (b*c)
```
Signal threshold: ROR ≥ 2 with 95% CI lower bound > 1

### Python Implementation Sketch

```python
import pandas as pd
import numpy as np
from scipy.stats import chi2_contingency

def calculate_prr(df, drug_col, event_col):
    """
    df: DataFrame with one row per drug-event report
    drug_col: column name for drug
    event_col: column name for MedDRA reaction term
    """
    results = []
    all_reports = len(df)
    
    for drug in df[drug_col].unique():
        for event in df[event_col].unique():
            a = len(df[(df[drug_col] == drug) & (df[event_col] == event)])
            if a < 3:
                continue  # Evans criterion: minimum 3 reports
            
            b = len(df[(df[drug_col] == drug) & (df[event_col] != event)])
            c = len(df[(df[drug_col] != drug) & (df[event_col] == event)])
            d = len(df[(df[drug_col] != drug) & (df[event_col] != event)])
            
            if (a + b) == 0 or (c + d) == 0:
                continue
            
            prr = (a / (a + b)) / (c / (c + d))
            
            # Chi-squared
            contingency = [[a, b], [c, d]]
            _, p_val, _, _ = chi2_contingency(contingency)
            chi2 = chi2_contingency(contingency)[0]
            
            if prr >= 2 and chi2 >= 4:
                results.append({
                    'drug': drug,
                    'event': event,
                    'a': a, 'b': b, 'c': c, 'd': d,
                    'prr': round(prr, 3),
                    'chi2': round(chi2, 3),
                    'signal': True
                })
    
    return pd.DataFrame(results).sort_values('prr', ascending=False)
```

---

## 6. OPTIONAL IBM SERVICES

These are optional but can strengthen the submission and impress judges.

### 6A. IBM watsonx.ai

**Access:** After joining the IBM Cloud hackathon account  
**Credits:** $80 automatically applied to your account  
**Region:** Always use **Dallas** (`us-south`)  
**Endpoint URL:** `https://us-south.ml.cloud.ibm.com`

**What to use it for:**
- LLM-powered explanation of detected signals in plain language
- Summarizing ICH M4 compliance gaps
- Natural language Q&A over adverse event data

**Supported frameworks:** LangChain, LangGraph, LlamaIndex, CrewAI, BeeAI, AutoGen

**Programmatic access — you need 3 things:**
1. **Project ID** — from watsonx.ai home page → Developer access section
2. **Endpoint URL** — `https://us-south.ml.cloud.ibm.com`
3. **API Key** — create at watsonx.ai home → Developer access → Create API key

**Generate IAM token:**
```bash
curl -X POST 'https://iam.cloud.ibm.com/identity/token' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'grant_type=urn:ibm:params:oauth:grant-type:apikey&apikey=YOUR_IBM_API_KEY'
```
Token expires in 60 minutes. Use `expires_in` property to track it.

**Models available (Prompt Lab):** granite-3-8b-instruct (default recommended), granite-13b-instruct-v2, codellama-34b-instruct-hf, etc.

**⚠️ Models OUT OF SCOPE (do NOT use — will negatively impact judging):**
- llama-3-405b-instruct
- mistral-medium-2505
- mistral-small-3-1-24b-instruct-2503

**⚠️ Features OUT OF SCOPE for this hackathon:**
- Agent Lab (Beta)
- Bring your own model
- Fine tuning models
- AutoAI pipeline
- AI governance
- Evaluation Studio
- SPSS Modeler

**Note:** Cloud accounts do NOT support deployment. Run your solution locally and showcase it in your submission video/demo.

### 6B. IBM watsonx Orchestrate

**Purpose:** No-code/low-code multi-agent orchestration  
**Use for:** Coordinating the signal detection agent + submission checker agent  
**Access:** IBM Cloud account → Resource list → AI/Machine Learning → watsonx-Hackathon Orchestrate

**What NOT to use:** "Build with AI (Preview)" feature is out of scope for this hackathon.

### 6C. IBM Natural Language Understanding (NLU)

- Entity extraction from adverse event narratives
- Sentiment and keyword analysis on drug descriptions
- Available in your IBM Cloud resource list

---

## 7. RECOMMENDED TECH STACK

```
Backend:        Python 3.10+
Data:           pandas, numpy, scipy (for PRR), requests (for OpenFDA)
AI/LLM:         watsonx.ai Python SDK or LangChain + IBM Granite model
Vector store:   FAISS or ChromaDB (for document similarity in Mode 2)
Web UI:         Streamlit (fast demo UI) or FastAPI + React
Bob IDE:        Primary development tool (REQUIRED)
```

**Python packages:**
```
pandas
numpy
scipy
requests
python-dotenv
streamlit
ibm-watsonx-ai     # official IBM SDK
langchain
langchain-ibm
faiss-cpu
```

---

## 8. PROJECT STRUCTURE

```
p2-drug-safety/
├── AGENTS.md                    # Bob IDE context file — create this first
├── CLAUDE.md                    # This file
├── .env                         # API keys (NEVER commit)
├── .gitignore                   # Must include .env
├── bob_sessions/                # REQUIRED — export Bob task reports here
│   ├── session_001_setup.json
│   ├── session_002_prr_engine.json
│   └── session_003_ui.json
├── requirements.txt
├── README.md
│
├── data/
│   ├── raw/                     # Downloaded FAERS files (not committed if large)
│   └── processed/               # Cleaned DataFrames
│
├── src/
│   ├── ingestion/
│   │   ├── faers_loader.py      # Load FAERS quarterly TSV files
│   │   └── openfda_client.py    # OpenFDA REST API client
│   │
│   ├── signal_detection/
│   │   ├── prr.py               # PRR + chi-squared calculation
│   │   ├── ror.py               # ROR as alternative
│   │   └── signal_reporter.py   # Format signal results + LLM explanation
│   │
│   ├── submission_checker/
│   │   ├── ctd_schema.py        # ICH M4 CTD structure as JSON schema
│   │   ├── document_parser.py   # Parse uploaded PDF/DOCX
│   │   └── gap_analyzer.py      # Check document against CTD schema
│   │
│   ├── llm/
│   │   ├── watsonx_client.py    # IBM watsonx.ai API wrapper
│   │   └── prompts.py           # Prompt templates
│   │
│   └── app/
│       ├── main.py              # Streamlit entrypoint
│       ├── mode1_ui.py          # Signal detection interface
│       └── mode2_ui.py          # Submission checker interface
│
└── notebooks/
    └── exploration.ipynb        # EDA and algorithm validation
```

---

## 9. BUILD PLAN — Step by Step

### Day 1: Foundation

**Task 1.1 — Set up repo and Bob context**
- Initialize git repo
- Create `AGENTS.md` with project summary, architecture, and key file paths
- Create `bob_sessions/` folder
- Create `.env` with API key placeholders; add to `.gitignore`
- Ask Bob (in Plan mode): "Review this project structure for a pharmacovigilance signal detection tool and suggest improvements"
- Export Bob session → save to `bob_sessions/session_001_setup.json`

**Task 1.2 — OpenFDA data ingestion**
- Build `src/ingestion/openfda_client.py`
- Fetch 5,000–10,000 records for common drugs (aspirin, ibuprofen, metformin)
- Parse into a flat DataFrame: `[report_id, drug, reaction, serious, date]`
- Validate data quality; check for nulls
- Ask Bob to review the ingestion code and suggest error handling
- Export Bob session

**Task 1.3 — PRR engine**
- Implement `src/signal_detection/prr.py`
- Test on aspirin + gastrointestinal bleeding (known signal)
- Validate: PRR should be >> 2, chi2 >> 4 for known drug-event pairs
- Ask Bob (in Code mode): "Review my PRR implementation for correctness against the Evans 2001 criteria"
- Export Bob session

### Day 2: Features + UI

**Task 2.1 — LLM signal explanation (optional but impressive)**
- Set up `src/llm/watsonx_client.py` with IBM Granite model
- Given a detected signal, generate plain-language explanation: "Aspirin has a PRR of 3.4 for gastrointestinal bleeding, meaning..."
- Store API key in `.env` only
- Ask Bob to write prompt templates for signal explanation

**Task 2.2 — ICH M4 CTD schema**
- Encode CTD module structure in `src/submission_checker/ctd_schema.py`
- Key sections: 1 (Admin), 2.1 (ToC), 2.3 (Quality Overall Summary), 2.4 (Nonclinical Overview), 2.5 (Clinical Overview), 2.6 (Nonclinical Summaries), 2.7 (Clinical Summaries), 3 (Quality), 4 (Nonclinical), 5 (Clinical)
- Build section presence checker: uploads text → identifies which CTD sections are present/missing
- Ask Bob to generate the CTD schema as a Python dict

**Task 2.3 — Streamlit UI**
- Two tabs: "Signal Detector" and "Submission Checker"
- Mode 1: Drug name input → fetch from OpenFDA → run PRR → display signal table with risk levels
- Mode 2: Document upload (PDF or text) → extract text → check against CTD → show gap report
- Ask Bob to review UI code for usability

### Day 3: Polish + Submission

**Task 3.1 — Testing and validation**
- Test with at least 3 known drug-event pairs (aspirin/GI bleeding, warfarin/bleeding, SSRIs/QT prolongation)
- Verify PRR values are in the expected range
- Export final Bob sessions

**Task 3.2 — Documentation**
- Ask Bob to generate: README.md, code docstrings, inline comments
- Ask Bob to write a summary of the system architecture

**Task 3.3 — Pre-submission checklist**
- [ ] All Bob task session reports in `bob_sessions/` folder
- [ ] `.env` NOT committed; `.gitignore` contains `.env`
- [ ] No API keys or credentials in any code file
- [ ] `requirements.txt` is complete and accurate
- [ ] Demo video recorded
- [ ] Repo pushed to public GitHub

---

## 10. JUDGING CONTEXT

The judges will look for:
1. **IBM Bob IDE integration** — visible use in the codebase (Bob-generated docs, comments mentioning Bob, bob_sessions/ present)
2. **Problem-solving depth** — does the PRR implementation actually work correctly?
3. **Real data usage** — are you using FDA FAERS, not mock data?
4. **Innovation** — LLM-powered plain-language explanations of signals would stand out
5. **Demo quality** — clear, working demo showing both modes

### Optional watsonx integration for bonus points

If Bobcoins remain, use Bob to wire in watsonx.ai for LLM signal explanations. This shows the full IBM stack.

---

## 11. ENVIRONMENT SETUP

```bash
# Clone and set up
git clone <your-repo>
cd p2-drug-safety
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Create .env file (fill in your values)
cp .env.example .env
```

**.env.example:**
```env
# IBM watsonx.ai (optional)
WATSONX_API_KEY=your_ibm_cloud_api_key_here
WATSONX_PROJECT_ID=your_project_id_here
WATSONX_URL=https://us-south.ml.cloud.ibm.com

# OpenFDA (no key required — leave blank)
OPENFDA_API_KEY=
```

**requirements.txt:**
```
pandas>=2.0.0
numpy>=1.24.0
scipy>=1.11.0
requests>=2.31.0
python-dotenv>=1.0.0
streamlit>=1.28.0
ibm-watsonx-ai>=0.2.0
langchain>=0.1.0
langchain-ibm>=0.1.0
PyPDF2>=3.0.0
```

---

## 12. QUICK-START: GET DATA IN 15 MINUTES

Run this in Python to immediately have 1,000 real adverse event records:

```python
import requests
import pandas as pd

def fetch_faers_sample(drug_name: str, n: int = 1000) -> pd.DataFrame:
    """Fetch FAERS adverse event records for a drug via OpenFDA API."""
    base_url = "https://api.fda.gov/drug/event.json"
    params = {
        "search": f'patient.drug.medicinalproduct:"{drug_name}"',
        "limit": min(n, 1000)
    }
    response = requests.get(base_url, params=params, timeout=30)
    response.raise_for_status()
    data = response.json()
    
    rows = []
    for report in data.get("results", []):
        report_id = report.get("safetyreportid", "")
        serious = report.get("serious", 0)
        
        drugs = report.get("patient", {}).get("drug", [])
        reactions = report.get("patient", {}).get("reaction", [])
        
        for drug in drugs:
            if drug.get("drugcharacterization") != "1":  # primary suspect only
                continue
            drug_name_clean = drug.get("medicinalproduct", "")
            
            for reaction in reactions:
                pt = reaction.get("reactionmeddrapt", "")
                rows.append({
                    "report_id": report_id,
                    "drug": drug_name_clean,
                    "reaction": pt,
                    "serious": serious
                })
    
    return pd.DataFrame(rows)

# Test it
df = fetch_faers_sample("ASPIRIN", n=1000)
print(f"Fetched {len(df)} drug-reaction pairs")
print(df.head())
```

---

## 13. IMPORTANT REMINDERS

- **Save your watsonx work before the hackathon ends** — IBM Cloud accounts are deactivated after the event. Export your Prompt Lab sessions and download any notebooks.
- **Bob session reports are mandatory** — judges check for the `bob_sessions/` folder
- **All FAERS data is public domain** — safe to use, no PI, no licensing issues
- **Run locally** — the hackathon-provisioned IBM Cloud accounts do NOT support deployment. Showcase via demo video
- **Credits warning** — watsonx.ai sends email alerts at 25%, 50%, 80% usage; you may exhaust credits before receiving the alert (hourly emails only)
- **No sensitive data** — FAERS has been de-identified; do not attempt to re-identify any individuals

---

*Problem P2 | IBM Bob Hackathon | Lablab.ai*  
*This document compiled from: IBM Bob Hackathon Guide (May 2026), FDA FAERS public database, OpenFDA API documentation, ICH M4 CTD guidelines*
