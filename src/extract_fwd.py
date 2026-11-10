"""
Reduce the monthly data.opm.gov (Federal Workforce Data) raw files to small
analysis tables.

Input (downloaded by hand from data.opm.gov -> Data Downloads; ~41 GB, 24 months):
    data/raw/opm_datasets/{employment,separations,accessions}_YYYYMM_V_DATE.txt[.gz]
    pipe-delimited, one row per employee / separation / accession.

Why reduce: each Employment file is a ~1.7 GB snapshot of the whole workforce and
consecutive months repeat ~97% of the same people. This project needs only
  (1) economist rows (series 0110/0119), and
  (2) all-occupation counts by agency x tenure x education x GS band x economist,
so the raw files can be compressed or deleted once this has run.

Outputs
  data/raw/fedscope/fwd/economists_{employment,separations,accessions}.csv.gz
                                  economist rows, selected columns (committed)
  data/processed/fwd/stock_monthly.csv.gz      month, agysub, econ, ten, edu, gs, n
  data/processed/fwd/sep_monthly_fwd.csv.gz    month (effective), file_month, agysub,
                                               econ, reason, drp, ten, edu, gs, n
  data/processed/fwd/acc_monthly_fwd.csv.gz    same, accession type instead of reason
  data/processed/fwd/qa_files.csv              per-file row counts, DoD share, etc.
  (per-file parts under data/processed/fwd/_parts/ make the run restartable)

Notes
  * Files are keyed by the month they were *published*; separation/accession files
    also hold late-reported actions with other effective months, so analyses should
    key on the effective month (personnel_action_effective_date_yyyymm).
  * Unlike the Oct 2023-Mar 2025 classic files, DoD occupation/tenure/education/grade
    are NOT redacted here; pay, geography and bargaining unit are.
  * drp_indicator = 'Y' marks deferred-resignation-program separations.

Usage:
    python src/extract_fwd.py              # all months (restartable)
    python src/extract_fwd.py --month 202609   # one employment file, for testing
"""

import argparse
import time
from multiprocessing import Pool
from pathlib import Path

import pandas as pd

from build_panels import SEP_REASON, _edu, _gs_band, _ten

ROOT = Path(__file__).parent.parent
SRC = ROOT / "data" / "raw" / "opm_datasets"
OUT = ROOT / "data" / "processed" / "fwd"
PARTS = OUT / "_parts"
ECON_OUT = ROOT / "data" / "raw" / "fedscope" / "fwd"

ECON = {"0110", "0119"}
DOD = {"AR", "NV", "AF", "DD"}
ACC_TYPE = {"AA": "Transfer in", "AB": "Transfer in",
            "AC": "New hire", "AD": "New hire", "AE": "New hire"}

COMMON = ["agency_code", "agency_subelement_code", "occupational_series_code",
          "length_of_service_years", "education_level_code", "pay_plan_code", "grade",
          "annualized_adjusted_basic_pay", "age_bracket", "appointment_type_code",
          "supervisory_status_code", "work_schedule_code", "duty_station_state_abbreviation",
          "veteran_indicator", "count"]
EMP_COLS = ["snapshot_yyyymm"] + COMMON
FLOW_DATE = "personnel_action_effective_date_yyyymm"
SEP_COLS = [FLOW_DATE, "separation_category_code", "drp_indicator"] + COMMON
ACC_COLS = [FLOW_DATE, "accession_category_code"] + COMMON
KEYS = ["agysub", "econ", "ten", "edu", "gs"]


def _files(kind: str) -> list:
    return sorted(SRC.glob(f"{kind}_*.txt")) + sorted(SRC.glob(f"{kind}_*.txt.gz"))


def _file_month(p: Path) -> int:
    return int(p.name.split("_")[1])


def _dims(d: pd.DataFrame) -> pd.DataFrame:
    plan = d["pay_plan_code"]
    return pd.DataFrame({
        # blank sub-elements (~0.02% of rows, Oct 2024-Mar 2025) must not be dropped by groupby
        "agysub": d["agency_subelement_code"].fillna("MISSING"),
        "econ": d["occupational_series_code"].eq("0110"),
        "ten": _ten(d["length_of_service_years"]),
        "edu": _edu(d["education_level_code"]),
        "gs": _gs_band(pd.to_numeric(d["grade"], errors="coerce"), plan.eq("GS"), plan.eq("REDACTED")),
        "n": pd.to_numeric(d["count"], errors="coerce").fillna(1),
    })


# --------------------------------------------------------------------------
# employment (large): one worker per monthly file
# --------------------------------------------------------------------------

def do_employment(path: Path) -> dict:
    m = _file_month(path)
    part, epart = PARTS / f"emp_{m}.csv.gz", PARTS / f"emp_econ_{m}.csv.gz"
    stat = PARTS / f"emp_stat_{m}.csv"
    if part.exists() and epart.exists() and stat.exists():
        return pd.read_csv(stat).iloc[0].to_dict() | {"cached": True}
    t0 = time.time()
    aggs, econs, rows, dod, redacted_series, econ_rows = [], [], 0, 0, 0, 0
    for chunk in pd.read_csv(path, sep="|", dtype=str, usecols=EMP_COLS, chunksize=500_000,
                             low_memory=False):
        rows += len(chunk)
        dod += int(chunk["agency_code"].isin(DOD).sum())
        redacted_series += int(chunk["occupational_series_code"].eq("REDACTED").sum())
        g = _dims(chunk)
        g["month"] = m
        aggs.append(g.groupby(["month"] + KEYS, as_index=False)["n"].sum())
        e = chunk[chunk["occupational_series_code"].isin(ECON)]
        econ_rows += len(e)
        if len(e):
            econs.append(e)
    agg = pd.concat(aggs).groupby(["month"] + KEYS, as_index=False)["n"].sum()
    agg.to_csv(part, index=False)
    (pd.concat(econs) if econs else pd.DataFrame(columns=EMP_COLS)).to_csv(epart, index=False)
    s = dict(kind="employment", file_month=m, rows=rows, count_sum=int(agg["n"].sum()),
             dod_share=round(dod / rows, 4), redacted_series=redacted_series,
             econ_rows=econ_rows, seconds=round(time.time() - t0))
    pd.DataFrame([s]).to_csv(stat, index=False)
    return s


# --------------------------------------------------------------------------
# separations / accessions (small)
# --------------------------------------------------------------------------

def do_flows(kind: str):
    cols = SEP_COLS if kind == "separations" else ACC_COLS
    aggs, econs, stats = [], [], []
    for path in _files(kind):
        fm = _file_month(path)
        d = pd.read_csv(path, sep="|", dtype=str, usecols=cols, low_memory=False)
        g = _dims(d)
        g["month"] = pd.to_numeric(d[FLOW_DATE], errors="coerce").astype("Int64")
        g["file_month"] = fm
        if kind == "separations":
            g["reason"] = d["separation_category_code"].map(SEP_REASON).fillna("Other")
            g["drp"] = d["drp_indicator"].eq("Y")
            by = ["month", "file_month"] + KEYS + ["reason", "drp"]
        else:
            g["acc_type"] = d["accession_category_code"].map(ACC_TYPE).fillna("Other")
            by = ["month", "file_month"] + KEYS + ["acc_type"]
        aggs.append(g.groupby(by, as_index=False)["n"].sum())
        e = d[d["occupational_series_code"].isin(ECON)].copy()
        e.insert(0, "file_month", fm)
        econs.append(e)
        stats.append(dict(kind=kind, file_month=fm, rows=len(d), count_sum=int(g["n"].sum()),
                          dod_share=round(float(d["agency_code"].isin(DOD).mean()), 4),
                          redacted_series=int(d["occupational_series_code"].eq("REDACTED").sum()),
                          econ_rows=len(e), distinct_effective_months=int(d[FLOW_DATE].nunique())))
        print(f"  {kind} {fm}: {len(d):,} rows")
    out = pd.concat(aggs, ignore_index=True)
    name = "sep_monthly_fwd" if kind == "separations" else "acc_monthly_fwd"
    out.to_csv(OUT / f"{name}.csv.gz", index=False)
    pd.concat(econs, ignore_index=True).to_csv(ECON_OUT / f"economists_{kind}.csv.gz", index=False)
    return stats


# --------------------------------------------------------------------------

def run_all(month: int | None = None, workers: int = 4) -> None:
    for d in (OUT, PARTS, ECON_OUT):
        d.mkdir(parents=True, exist_ok=True)
    emp = _files("employment")
    if month:
        emp = [p for p in emp if _file_month(p) == month]
    if not emp:
        raise FileNotFoundError(f"No employment_*.txt[.gz] in {SRC}")
    print(f"employment: {len(emp)} files, {workers} workers")
    t0 = time.time()
    with Pool(workers) as pool:
        stats = []
        for s in pool.imap_unordered(do_employment, emp):
            stats.append(s)
            print(f"  employment {int(s['file_month'])}: {int(s['rows']):,} rows, "
                  f"{int(s['econ_rows'])} economists, DoD {s['dod_share']:.1%}")
    print(f"employment done in {time.time() - t0:.0f}s")
    if month:
        return

    parts = sorted(PARTS.glob("emp_2*.csv.gz"))
    pd.concat([pd.read_csv(p) for p in parts], ignore_index=True).to_csv(OUT / "stock_monthly.csv.gz", index=False)
    econ = pd.concat([pd.read_csv(p, dtype=str) for p in sorted(PARTS.glob("emp_econ_*.csv.gz"))], ignore_index=True)
    econ.to_csv(ECON_OUT / "economists_employment.csv.gz", index=False)
    print(f"stock panel from {len(parts)} months; {len(econ):,} economist rows")

    stats += do_flows("separations") + do_flows("accessions")
    qa = pd.DataFrame(stats).sort_values(["kind", "file_month"])
    qa.to_csv(OUT / "qa_files.csv", index=False)
    print(f"wrote {OUT}/ and {ECON_OUT}/")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--month", type=int, help="process just one employment file (test)")
    ap.add_argument("--workers", type=int, default=4)
    args = ap.parse_args()
    run_all(args.month, args.workers)
