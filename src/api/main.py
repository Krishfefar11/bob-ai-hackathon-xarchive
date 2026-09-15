"""FastAPI service exposing the P2 tools as REST/OpenAPI endpoints for IBM watsonx Orchestrate.

Orchestrate imports custom tools from an OpenAPI spec: run this service, then in the
Orchestrate console use "Add tool -> Import from OpenAPI spec" pointed at /openapi.json
(see ORCHESTRATE.md for the full walkthrough — that part needs your IBM Cloud account).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from fastapi import FastAPI, File, HTTPException, UploadFile

from api.schemas import (
    ModuleCompleteness,
    Signal,
    SignalDetectRequest,
    SignalDetectResponse,
    SubmissionCheckResponse,
)
from ingestion.openfda_client import fetch_faers_sample
from signal_detection.prr import calculate_prr
from signal_detection.signal_reporter import build_signal_report
from submission_checker.gap_analyzer import analyze_document

app = FastAPI(
    title="P2 Drug Safety & Regulatory Readiness Tools",
    description=(
        "Signal detection (PRR/FAERS) and CTD submission gap-checking, exposed as tools "
        "for IBM watsonx Orchestrate."
    ),
    version="1.0.0",
)


@app.post("/signals/detect", response_model=SignalDetectResponse, summary="Detect drug safety signals")
def detect_signals(request: SignalDetectRequest) -> SignalDetectResponse:
    """Fetch OpenFDA adverse event reports for a drug and flag disproportionality signals (PRR>=2, chi2>=4, n>=3)."""
    df = fetch_faers_sample(request.drug_name.strip(), n=request.n_records)
    if df.empty:
        raise HTTPException(404, f"No OpenFDA reports found for '{request.drug_name}'.")

    queried_drug = request.drug_name.strip().upper()
    prr_df = calculate_prr(df)
    report = build_signal_report(prr_df, use_llm=request.use_llm)
    matches = report[report["signal"] & (report["drug"] == queried_drug)]

    return SignalDetectResponse(
        drug_name=queried_drug,
        reports_fetched=int(df["report_id"].nunique()),
        signals=[
            Signal(
                drug=row.drug,
                reaction=row.reaction,
                reports=int(row.a),
                prr=float(row.prr),
                chi2=float(row.chi2),
                risk_level=row.risk_level,
                explanation=row.explanation,
            )
            for row in matches.itertuples()
        ],
    )


@app.post("/submission/check", response_model=SubmissionCheckResponse, summary="Check CTD submission readiness")
def check_submission(
    file: UploadFile = File(..., description="Draft regulatory document (PDF, DOCX, or TXT)")
) -> SubmissionCheckResponse:
    """Parse an uploaded document and check it against the ICH M4 CTD structure."""
    try:
        result = analyze_document(file.file, file.filename)
    except ValueError as exc:
        raise HTTPException(400, str(exc))

    return SubmissionCheckResponse(
        completeness_pct=result["completeness_pct"],
        present_count=result["present_count"],
        total_count=result["total_count"],
        missing_sections=result["missing_sections"],
        modules={
            name: ModuleCompleteness(
                title=info["title"],
                completeness_pct=info["completeness_pct"],
                present_count=info["present_count"],
                total_count=info["total_count"],
            )
            for name, info in result["modules"].items()
        },
    )
