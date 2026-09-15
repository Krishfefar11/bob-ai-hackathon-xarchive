"""Formats PRR/ROR results into risk-leveled, plain-language signal reports."""
import pandas as pd

from llm.prompts import SIGNAL_EXPLANATION_PROMPT
from llm.watsonx_client import WatsonxClient, WatsonxConfigError

_RISK_BANDS = [
    (9, "Very High"),
    (4, "High"),
    (2, "Moderate"),
]


def risk_level(prr: float) -> str:
    for threshold, label in _RISK_BANDS:
        if prr >= threshold:
            return label
    return "Not Significant"


def _template_explanation(drug: str, event: str, prr: float, chi2: float, a: int) -> str:
    if prr >= 2 and chi2 >= 4 and a >= 3:
        return (
            f"{drug} is reported with {event} {prr:.1f}x more often than expected relative to "
            f"other drugs (χ²={chi2:.1f}, based on {a} reports). This meets the Evans et al. "
            f"signal threshold (PRR≥2, χ²≥4, n≥3) and warrants pharmacovigilance review."
        )
    return (
        f"{drug} + {event} shows a PRR of {prr:.2f} (χ²={chi2:.1f}, {a} reports), which does "
        f"not meet the regulatory signal threshold."
    )


def build_signal_report(
    prr_df: pd.DataFrame,
    drug_col: str = "drug",
    event_col: str = "reaction",
    use_llm: bool = False,
) -> pd.DataFrame:
    if prr_df.empty:
        return prr_df.assign(risk_level=[], explanation=[])

    report = prr_df.copy()
    report["risk_level"] = report["prr"].apply(risk_level)

    client = None
    if use_llm:
        try:
            client = WatsonxClient()
        except WatsonxConfigError:
            client = None  # no watsonx credentials configured — fall back to templates

    explanations = []
    for row in report.itertuples():
        drug, event, prr, chi2, a = (
            getattr(row, drug_col),
            getattr(row, event_col),
            row.prr,
            row.chi2,
            row.a,
        )
        text = None
        if client is not None:
            try:
                text = client.generate(
                    SIGNAL_EXPLANATION_PROMPT.format(drug=drug, event=event, prr=prr, chi2=chi2, a=a)
                )
            except Exception:
                text = None  # LLM call failed — fall back to the template below
        explanations.append(text or _template_explanation(drug, event, prr, chi2, a))

    report["explanation"] = explanations
    return report
