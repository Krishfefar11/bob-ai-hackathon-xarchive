"""Validates ROR against the same synthetic contingency table used in test_prr.py."""
import pandas as pd

from signal_detection.ror import calculate_ror


def _synthetic_df():
    rows = []
    rows += [{"drug": "DRUGX", "reaction": "EVENTY"}] * 10
    rows += [{"drug": "DRUGX", "reaction": "EVENTOTHER"}] * 90
    rows += [{"drug": "DRUGZ", "reaction": "EVENTY"}] * 5
    rows += [{"drug": "DRUGZ", "reaction": "EVENTOTHER"}] * 895
    return pd.DataFrame(rows)


def test_known_signal_flagged():
    df = _synthetic_df()
    result = calculate_ror(df, min_reports=3)

    row = result[(result["drug"] == "DRUGX") & (result["reaction"] == "EVENTY")].iloc[0]
    assert row["ror"] > 2
    assert row["ci_low"] > 1
    assert row["signal"]


def test_below_threshold_not_flagged():
    df = _synthetic_df()
    result = calculate_ror(df, min_reports=3)

    row = result[(result["drug"] == "DRUGZ") & (result["reaction"] == "EVENTY")].iloc[0]
    assert not row["signal"]
