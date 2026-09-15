"""Proportional Reporting Ratio (PRR) disproportionality analysis (Evans et al., 2001)."""
import numpy as np
import pandas as pd


def _contingency_counts(df: pd.DataFrame, drug_col: str, event_col: str, min_reports: int):
    total = len(df)
    pair_counts = df.groupby([drug_col, event_col]).size().rename("a").reset_index()
    pair_counts = pair_counts[pair_counts["a"] >= min_reports].reset_index(drop=True)

    drug_totals = df.groupby(drug_col).size()
    event_totals = df.groupby(event_col).size()

    a = pair_counts["a"].to_numpy(dtype=float)
    drug_n = pair_counts[drug_col].map(drug_totals).to_numpy(dtype=float)
    event_n = pair_counts[event_col].map(event_totals).to_numpy(dtype=float)

    b = drug_n - a
    c = event_n - a
    d = total - drug_n - event_n + a
    return pair_counts, a, b, c, d, total


def calculate_prr(
    df: pd.DataFrame,
    drug_col: str = "drug",
    event_col: str = "reaction",
    min_reports: int = 3,
) -> pd.DataFrame:
    """Flags drug-event pairs meeting the Evans et al. signal criteria: PRR>=2, chi2>=4, a>=min_reports."""
    if df.empty:
        return pd.DataFrame(columns=[drug_col, event_col, "a", "b", "c", "d", "prr", "chi2", "signal"])

    pair_counts, a, b, c, d, total = _contingency_counts(df, drug_col, event_col, min_reports)

    # Closed-form 2x2 chi-squared avoids an O(pairs) scipy.stats call per pair.
    with np.errstate(divide="ignore", invalid="ignore"):
        prr = (a / (a + b)) / (c / (c + d))
        chi2 = (total * (a * d - b * c) ** 2) / ((a + b) * (c + d) * (a + c) * (b + d))

    result = pair_counts.copy()
    result["b"] = b.astype(int)
    result["c"] = c.astype(int)
    result["d"] = d.astype(int)
    result["prr"] = prr.round(3)
    result["chi2"] = chi2.round(3)
    result["signal"] = (result["prr"] >= 2) & (result["chi2"] >= 4) & (result["a"] >= min_reports)

    return result.sort_values("prr", ascending=False).reset_index(drop=True)
