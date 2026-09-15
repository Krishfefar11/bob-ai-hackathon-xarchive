# Wiring up IBM watsonx Orchestrate

CLAUDE.md §6B lists watsonx Orchestrate as optional: a no-code/low-code layer for coordinating
the signal-detection and submission-checker tools as agent-callable skills. Orchestrate is a
hosted SaaS product configured through the IBM Cloud console — there's no SDK call that "wires
it up" from inside this repo. What *is* code-side work is exposing our two tools in the format
Orchestrate actually consumes: an OpenAPI spec it can import.

That part is done — [`src/api/main.py`](src/api/main.py) is a FastAPI service wrapping the
existing `signal_detection` and `submission_checker` packages:

| Endpoint | Wraps | Purpose |
|---|---|---|
| `POST /signals/detect` | `ingestion` + `signal_detection` | Fetch OpenFDA reports for a drug, return flagged PRR signals |
| `POST /submission/check` | `submission_checker` | Upload a document, return its CTD completeness gap report |

FastAPI auto-generates the OpenAPI spec at `/openapi.json` from the Pydantic models in
`src/api/schemas.py` — that's the artifact Orchestrate imports.

Both endpoints are tested: `tests/test_api.py` covers them offline (via `TestClient`), and
they've been verified against live OpenFDA data and a real PDF upload over actual HTTP.

## Run it

```bash
source venv/bin/activate
uvicorn api.main:app --app-dir src --port 8000
```

Interactive docs: http://localhost:8000/docs · raw spec: http://localhost:8000/openapi.json

## The part only you can do

Orchestrate runs in IBM's cloud — it can't reach `http://localhost:8000` on your laptop.
Before importing the tool, make the API reachable from the internet, e.g.:

```bash
ngrok http 8000
```

(or deploy the FastAPI service somewhere public — note CLAUDE.md §13 says the *hackathon-provisioned*
IBM Cloud account specifically doesn't support deployment, so a free host like Render/Fly.io or
an ngrok tunnel for the demo are the practical options).

Then in the watsonx Orchestrate console (IBM Cloud → Resource list → your
watsonx-Hackathon Orchestrate instance):

1. **Add the tool** — find the tool/skill import option (labeled "Add tool" / "Import skill" /
   "Import from OpenAPI" depending on your Orchestrate version) and point it at your tunnel's
   `/openapi.json` URL, or upload that file directly. This should register two tools, one per
   endpoint above, using the `summary`/`description` text already in `main.py` and `schemas.py`.
2. **Build an agent** — in Agent Builder, create (or edit) an agent and add both tools to its
   toolset. Give it routing instructions along the lines of:
   > Use "Detect drug safety signals" when the user asks about a drug's adverse events, side
   > effects, or safety signals. Use "Check CTD submission readiness" when the user uploads or
   > references a regulatory/CTD document and wants its completeness checked.
3. **Test it** in the console's chat preview — e.g. "What safety signals does aspirin have?"
   should trigger the first tool; "Is my Module 2 document complete?" (with a file) the second.

Exact menu labels shift between Orchestrate releases, so follow whatever your instance's
current wizard shows rather than the labels above verbatim — the shape (import OpenAPI → get
two tools → attach both to one agent) is what matters.
