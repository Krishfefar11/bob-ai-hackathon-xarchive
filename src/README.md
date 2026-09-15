# Source Code

```
src/
├── ingestion/           # OpenFDA API client + FAERS quarterly file loader
├── signal_detection/    # PRR + ROR calculation, risk banding, explanations
├── submission_checker/  # ICH M4 CTD schema, document parsing, gap analysis
├── llm/                 # Optional IBM watsonx.ai client + prompt templates
├── app/                 # Streamlit UI — run: streamlit run src/app/main.py
└── api/                 # FastAPI/OpenAPI service for watsonx Orchestrate —
                          # run: uvicorn api.main:app --app-dir src --port 8000
```

Both `app/` and `api/` are thin entry points over the same four packages (`ingestion`, `signal_detection`, `submission_checker`, `llm`) — no logic is duplicated between the UI and the API.

See [`../AGENTS.md`](../AGENTS.md) for the full architecture reference and [`../docs/architecture.md`](../docs/architecture.md) for the diagram and data flow.

`requirements.txt` and `.env.example` live at the repo root, not in this folder.
