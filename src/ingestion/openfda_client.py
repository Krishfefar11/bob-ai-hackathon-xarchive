"""Client for the OpenFDA drug adverse event API (https://open.fda.gov/apis/drug/event/)."""
import os
import time

from dotenv import load_dotenv
import pandas as pd
import requests

load_dotenv()

BASE_URL = "https://api.fda.gov/drug/event.json"
OPENFDA_API_KEY = os.getenv("OPENFDA_API_KEY", "").strip()
# OpenFDA rejects anonymous (no api_key) requests above limit=500 with a 403
# API_KEY_MISSING error; the documented limit=1000 ceiling only applies with a key.
MAX_PER_CALL = 1000 if OPENFDA_API_KEY else 500
MAX_TOTAL = 25000  # OpenFDA's hard cap on skip + limit


def fetch_events(drug_name: str, limit: int = 100, skip: int = 0) -> dict:
    params = {
        "search": f'patient.drug.medicinalproduct:"{drug_name}"',
        "limit": min(limit, MAX_PER_CALL),
        "skip": skip,
    }
    if OPENFDA_API_KEY:
        params["api_key"] = OPENFDA_API_KEY
    response = requests.get(BASE_URL, params=params, timeout=30)
    if response.status_code == 404:
        return {"results": []}  # OpenFDA returns 404 (not an empty list) when nothing matches
    response.raise_for_status()
    return response.json()


def fetch_events_bulk(drug_name: str, n: int = 1000, pause: float = 0.2) -> list:
    n = min(n, MAX_TOTAL)
    results = []
    skip = 0
    while len(results) < n:
        page_size = min(MAX_PER_CALL, n - len(results))
        page = fetch_events(drug_name, limit=page_size, skip=skip)
        batch = page.get("results", [])
        if not batch:
            break
        results.extend(batch)
        skip += len(batch)
        if len(batch) < page_size:
            break
        time.sleep(pause)  # courteous pacing for a free, unauthenticated API
    return results


def to_dataframe(raw_results: list, primary_suspect_only: bool = True) -> pd.DataFrame:
    rows = []
    for report in raw_results:
        report_id = report.get("safetyreportid", "")
        serious = report.get("serious", "0")
        receive_date = report.get("receivedate", "")
        patient = report.get("patient", {})

        for drug in patient.get("drug", []):
            if primary_suspect_only and drug.get("drugcharacterization") != "1":
                continue
            drug_name = drug.get("medicinalproduct", "").strip().upper()
            if not drug_name:
                continue
            for reaction in patient.get("reaction", []):
                pt = reaction.get("reactionmeddrapt", "").strip().upper()
                if not pt:
                    continue
                rows.append(
                    {
                        "report_id": report_id,
                        "drug": drug_name,
                        "reaction": pt,
                        "serious": serious,
                        "receive_date": receive_date,
                    }
                )
    return pd.DataFrame(rows, columns=["report_id", "drug", "reaction", "serious", "receive_date"])


def fetch_faers_sample(drug_name: str, n: int = 1000) -> pd.DataFrame:
    return to_dataframe(fetch_events_bulk(drug_name, n))
