"""Validates the FastAPI service's OpenAPI-documented tool endpoints (offline — no live OpenFDA calls)."""
from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)


def test_openapi_spec_exposes_both_tools():
    spec = client.get("/openapi.json").json()
    assert "/signals/detect" in spec["paths"]
    assert "/submission/check" in spec["paths"]


def test_submission_check_txt():
    text = (
        "2.1 CTD Table of Contents\n"
        "2.3 Quality Overall Summary\n"
        "2.5 Clinical Overview\n"
        "3.1 Table of Contents of Module 3\n"
        "3.2 Body of Data\n"
        "3.3 Literature References"
    )
    response = client.post(
        "/submission/check",
        files={"file": ("draft.txt", text.encode("utf-8"), "text/plain")},
    )
    assert response.status_code == 200
    body = response.json()
    assert 0 < body["completeness_pct"] < 100
    assert any("2.2" in m for m in body["missing_sections"])
    assert body["modules"]["Module 3"]["completeness_pct"] == 100.0


def test_submission_check_rejects_unsupported_type():
    response = client.post(
        "/submission/check",
        files={"file": ("draft.xyz", b"whatever", "application/octet-stream")},
    )
    assert response.status_code == 400
