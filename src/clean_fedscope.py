"""
Clean the FedScope economist extracts produced by fetch_fedscope.py into
analysis-ready tables under data/processed/.

Snapshots
---------
  March 2025 (202503)  — full record-level detail (data/raw/fedscope/
                          employment_202503_economists.csv), ~4,670 series-0110
                          economists identifiable (DoD-redacted rows excluded).
  September 2024 (202409) — NO record-level file is public. Only OPM's
                          pre-aggregated summaries are available:
                            * exact total headcount + mean pay (complete)
                            * agency x pay-plan x grade cells with >10 employees
                              (~76% of economists; the small-cell tail is
                              suppressed and omitted on BOTH dates).

So totals and mean-pay comparisons are clean; agency/grade-level change is
partial on the September 2024 side. A fuller September 2024 comparison needs the
data.opm.gov monthly API (blocked from this environment — see
docs/2025_update_plan.md, "Deferred").

Outputs (data/processed/)
-------------------------
  fedscope_economists_202503.csv   one row per identifiable economist, March 2025
  fedscope_economist_totals.csv    202409 & 202503 totals (headcount, mean pay, LOS)
  fedscope_economist_cells.csv     agency x pay-plan x grade panel, both snapshots
  fedscope_economist_flows.csv     economist accessions & separations, monthly

Filtering note
--------------
`series_label` ("economist" / "economics_assistant") is the stable key. The
`series` column holds OPM's 4-char code ("0110"/"0119") but pandas re-reads it as
int 110/119 unless you pass `dtype={"series": str}`. Grades likewise
(`dtype={"grade": str}`) — some are non-numeric ("K", "2C").

Usage
-----
    python src/clean_fedscope.py
"""

from pathlib import Path

import pandas as pd

FEDSCOPE_DIR = Path(__file__).parent.parent / "data" / "raw" / "fedscope"
PROCESSED_DIR = Path(__file__).parent.parent / "data" / "processed"

# Bureau-level groupings, keyed by agency sub-element code. Everything else is
# grouped at the department level (AGYT). Mirrors src/analyze.py's AGENCY_LABELS
# so the FedScope tables line up with the FedsDataCenter panel.
BUREAU_BY_SUBCODE = {
    "DLLS": "BLS",
    "CM53": "BEA",
    "CM63": "Census Bureau",
    "AG18": "ERS",
}

RECORD_RENAME = {
    "DATECODE": "snapshot",
    "OCC": "series",
    "OCCT": "occupation",
    "AGYT": "agency",
    "AGYSUB": "agency_subcode",
    "AGYSUBT": "agency_sub",
    "PAYPLAN": "pay_plan",
    "PAYPLANT": "pay_plan_desc",
    "GRD": "grade",
    "SALARY": "salary",
    "STATET": "state",
    "STATE": "state_code",
    "COUNTRYT": "country",
    "AGELVLT": "age_band",
    "EDLVLT": "education",
    "LOS": "los",
    "TOAT": "appointment_type",
    "SUPERVIST": "supervisory",
    "WORKSCHT": "work_schedule",
    "STEMAGGT": "stem",
}


# --------------------------------------------------------------------------
# Shared helpers
# --------------------------------------------------------------------------

def _num(series: pd.Series) -> pd.Series:
    """To numeric; 'REDACTED', '', '10_OR_LESS' etc. -> NaN."""
    return pd.to_numeric(series, errors="coerce")


def _agency_group(df: pd.DataFrame) -> pd.Series:
    grp = df["agency"].str.title()
    sub = df["agency_subcode"].map(BUREAU_BY_SUBCODE)
    return sub.fillna(grp)


def _series_label(series_code: pd.Series) -> pd.Series:
    return series_code.map({"0110": "economist", "0119": "economics_assistant",
                            "110": "economist", "119": "economics_assistant"})


# --------------------------------------------------------------------------
# 1. Record-level March 2025
# --------------------------------------------------------------------------

def clean_record_level() -> pd.DataFrame:
    src = FEDSCOPE_DIR / "employment_202503_economists.csv"
    df = pd.read_csv(src, dtype=str)
    df = df.rename(columns=RECORD_RENAME)

    df["snapshot"] = df["snapshot"].astype(int)
    df["salary"] = _num(df["salary"])
    df["los"] = _num(df["los"])
    df["grade_num"] = _num(df["grade"])  # NaN for non-numeric grades (K, 2C, ...)
    df["series_label"] = _series_label(df["series"])
    df["agency_group"] = _agency_group(df)
    df["is_permanent"] = (
        df["appointment_type"].str.contains("PERMANENT", na=False)
        & ~df["appointment_type"].str.contains("NONPERMANENT", na=False)
    )
    df["is_supervisor"] = df["supervisory"].isin(
        ["SUPERVISOR OR MANAGER", "SUPERVISOR", "MANAGER"]
    )

    keep = [
        "snapshot", "series", "series_label", "occupation",
        "agency", "agency_group", "agency_sub", "agency_subcode",
        "pay_plan", "pay_plan_desc", "grade", "grade_num", "salary",
        "state", "country", "age_band", "education", "los",
        "appointment_type", "is_permanent", "supervisory", "is_supervisor",
        "work_schedule", "stem",
    ]
    out = df[keep].copy()

    out_path = PROCESSED_DIR / "fedscope_economists_202503.csv"
    out.to_csv(out_path, index=False)

    econ = out[out["series"] == "0110"]
    n_red = out["salary"].isna().sum()
    print(f"  {out_path.name}: {len(out)} rows "
          f"({len(econ)} series-0110, {len(out) - len(econ)} economics-assistant)")
    print(f"    series-0110 mean pay ${econ['salary'].mean():,.0f}  "
          f"median ${econ['salary'].median():,.0f}  ({n_red} salaries redacted)")
    return out


# --------------------------------------------------------------------------
# 2. Totals (both snapshots) from the "by Occupation" summary
# --------------------------------------------------------------------------

def clean_totals() -> pd.DataFrame:
    src = FEDSCOPE_DIR / "summary" / "Status Employment by Occupation_202503_and_202409.txt"
    raw = pd.read_csv(src, sep="\t", dtype={"OCC": str})
    econ = raw[raw["OCC"].isin(["110", "119"])].copy()
    econ = econ.rename(columns={
        "DATECODE": "snapshot", "OCC": "series", "OCCT": "occupation",
        "EMPCOUNT": "headcount", "AVGSAL": "mean_salary", "AVGLOS": "mean_los",
    })
    econ["series"] = econ["series"].map({"110": "0110", "119": "0119"})
    econ["series_label"] = _series_label(econ["series"])
    econ = econ[["snapshot", "series", "series_label", "occupation",
                 "headcount", "mean_salary", "mean_los"]].sort_values(["series", "snapshot"])

    out_path = PROCESSED_DIR / "fedscope_economist_totals.csv"
    econ.to_csv(out_path, index=False)

    e = econ[econ["series"] == "0110"].set_index("snapshot")
    d_head = e.loc[202503, "headcount"] - e.loc[202409, "headcount"]
    d_pay = e.loc[202503, "mean_salary"] - e.loc[202409, "mean_salary"]
    print(f"  {out_path.name}: series-0110 "
          f"{e.loc[202409, 'headcount']:,} -> {e.loc[202503, 'headcount']:,} "
          f"({d_head:+,}, {d_head / e.loc[202409, 'headcount']:+.1%}); "
          f"mean pay ${e.loc[202409, 'mean_salary']:,} -> ${e.loc[202503, 'mean_salary']:,} "
          f"({d_pay / e.loc[202409, 'mean_salary']:+.1%})")
    return econ


# --------------------------------------------------------------------------
# 3. Agency x pay-plan x grade cells, both snapshots
# --------------------------------------------------------------------------

def clean_cells() -> pd.DataFrame:
    src = FEDSCOPE_DIR / "summary" / "Employment by Agency PayPlan Grade Series_economists.csv"
    df = pd.read_csv(src, dtype=str)
    df = df.rename(columns={
        "DATECODE": "snapshot", "AGYT": "agency", "AGYSUB": "agency_subcode",
        "AGYSUBT": "agency_sub", "OCC": "series", "OCCT": "occupation",
        "PAYPLAN": "pay_plan", "GRD": "grade",
        "EMPCOUNT": "headcount", "AVGSAL": "mean_salary", "AVGLOS": "mean_los",
    })
    df["snapshot"] = df["snapshot"].astype(int)
    df["series"] = df["series"].map({"110": "0110", "119": "0119"}).fillna(df["series"])
    df["series_label"] = _series_label(df["series"])
    df["agency_group"] = _agency_group(df)
    for col in ("headcount", "mean_salary", "mean_los"):
        df[col] = _num(df[col])
    df["grade_num"] = _num(df["grade"])

    out = df[["snapshot", "series", "series_label", "agency", "agency_group",
              "agency_sub", "agency_subcode", "pay_plan", "grade", "grade_num",
              "headcount", "mean_salary", "mean_los"]].copy()
    out_path = PROCESSED_DIR / "fedscope_economist_cells.csv"
    out.to_csv(out_path, index=False)

    shown = out[out["series"] == "0110"].groupby("snapshot")["headcount"].sum()
    print(f"  {out_path.name}: {len(out)} cells "
          f"(series-0110 shown: {int(shown.get(202409, 0)):,} in 202409, "
          f"{int(shown.get(202503, 0)):,} in 202503; rest suppressed as <=10-count cells)")
    return out


# --------------------------------------------------------------------------
# 4. Flows: accessions & separations
# --------------------------------------------------------------------------

def clean_flows() -> pd.DataFrame:
    frames = []
    for fname, direction, code_col, desc_col in (
        ("accessions_202404_202503_economists.csv", "accession", "ACC", "ACCT"),
        ("separations_202404_202503_economists.csv", "separation", "SEP", "SEPT"),
    ):
        src = FEDSCOPE_DIR / fname
        df = pd.read_csv(src, dtype=str)
        df = df.rename(columns={
            **RECORD_RENAME,
            "EFDATE": "month", code_col: "action_code", desc_col: "action_type",
        })
        df["direction"] = direction
        df["month"] = df["month"].astype(int)
        df["salary"] = _num(df["salary"])
        df["los"] = _num(df["los"])
        df["series_label"] = _series_label(df["series"])
        df["agency_group"] = _agency_group(df)
        frames.append(df[[
            "direction", "month", "series", "series_label", "action_type",
            "agency", "agency_group", "agency_sub", "pay_plan", "grade",
            "salary", "age_band", "education", "los", "appointment_type",
        ]])

    out = pd.concat(frames, ignore_index=True).sort_values(["direction", "month"])
    out_path = PROCESSED_DIR / "fedscope_economist_flows.csv"
    out.to_csv(out_path, index=False)

    econ = out[out["series"] == "0110"]
    piv = econ.groupby("direction").size()
    q1_2025 = econ[(econ["month"] >= 202501) & (econ["direction"] == "separation")].shape[0]
    print(f"  {out_path.name}: series-0110 "
          f"{piv.get('accession', 0)} accessions, {piv.get('separation', 0)} separations "
          f"(Apr 2024-Mar 2025); {q1_2025} separations in Jan-Mar 2025")
    return out


# --------------------------------------------------------------------------

def run_all() -> None:
    if not (FEDSCOPE_DIR / "employment_202503_economists.csv").exists():
        raise FileNotFoundError(
            f"{FEDSCOPE_DIR}/ not populated. Run: python src/fetch_fedscope.py"
        )
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    print("1. record-level economists (March 2025)")
    clean_record_level()
    print("2. totals (Sept 2024 + March 2025)")
    clean_totals()
    print("3. agency x pay-plan x grade cells")
    clean_cells()
    print("4. flows (accessions & separations)")
    clean_flows()
    print(f"\nProcessed files written to {PROCESSED_DIR}/")


if __name__ == "__main__":
    run_all()
