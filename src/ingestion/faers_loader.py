"""Loads raw FDA FAERS quarterly ASCII data files (DRUG/REAC/OUTC) into the shared analysis schema."""
from pathlib import Path

import pandas as pd

DELIMITER = "$"  # FAERS ASCII exports are $-delimited despite the .txt extension


def _read_faers_file(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, delimiter=DELIMITER, dtype=str, encoding="latin-1", low_memory=False)


def load_faers_quarter(data_dir: str, quarter_suffix: str) -> pd.DataFrame:
    data_dir = Path(data_dir)
    drug = _read_faers_file(data_dir / f"DRUG{quarter_suffix}.txt")
    reac = _read_faers_file(data_dir / f"REAC{quarter_suffix}.txt")

    drug.columns = [c.lower() for c in drug.columns]
    reac.columns = [c.lower() for c in reac.columns]
    drug = drug[drug["role_cod"] == "PS"]  # primary suspect drug only

    serious_ids = set()
    outc_path = data_dir / f"OUTC{quarter_suffix}.txt"
    if outc_path.exists():
        outc = _read_faers_file(outc_path)
        outc.columns = [c.lower() for c in outc.columns]
        serious_ids = set(outc["primaryid"])

    merged = drug.merge(reac, on="primaryid", suffixes=("_drug", "_reac"))
    merged["drug"] = merged["drugname"].str.strip().str.upper()
    merged["reaction"] = merged["pt"].str.strip().str.upper()
    merged["serious"] = merged["primaryid"].isin(serious_ids).map({True: "1", False: "2"})
    merged["report_id"] = merged["primaryid"]

    return merged[["report_id", "drug", "reaction", "serious"]].dropna(subset=["drug", "reaction"])
