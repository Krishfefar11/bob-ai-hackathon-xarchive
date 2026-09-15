"""Reporting Odds Ratio (ROR) — alternative disproportionality measure with a 95% CI."""
import numpy as np
import pandas as pd

from signal_detection.prr import _contingency_counts


def calculate_ror(
    df: pd.DataFrame,
    drug_col: str = "drug",
    event_col: str = "reaction",
    min_reports: int = 3,
) -> pd.DataFrame:
    """Signal criterion: ROR >= 2 and the lower 95% CI bound > 1."""
    if df.empty:
        return pd.DataFrame(columns=[drug_col, event_col, "a", "b", "c", "d", "ror", "ci_low", "ci_high", "signal"])

    pair_counts, a, b, c, d, _ = _contingency_counts(df, drug_col, event_col, min_reports)

    with np.errstate(divide="ignore", invalid="ignore"):
        ror = (a * d) / (b * c)
        se_log_ror = np.sqrt(1 / a + 1 / b + 1 / c + 1 / d)
        ci_low = np.exp(np.log(ror) - 1.96 * se_log_ror)
        ci_high = np.exp(np.log(ror) + 1.96 * se_log_ror)

    result = pair_counts.copy()
    result["b"] = b.astype(int)
    result["c"] = c.astype(int)
    result["d"] = d.astype(int)
    result["ror"] = ror.round(3)
    result["ci_low"] = ci_low.round(3)
    result["ci_high"] = ci_high.round(3)
    result["signal"] = (result["ror"] >= 2) & (ci_low > 1)

    return result.sort_values("ror", ascending=False).reset_index(drop=True)
