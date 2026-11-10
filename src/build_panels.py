"""
Aggregate the all-occupation FedScope files into two small panels for the
three-episode "who leaves" study (analyze_episodes.py).

  stock_sept.csv.gz   Sept snapshots 2004-2024: who is employed
                      columns: year, agysub, econ, ten, edu, gs, n
  sep_monthly.csv.gz  Oct 2004 - Mar 2025: who separated, and why
                      columns: month, agysub, econ, reason, ten, edu, gs, n

Dimensions
  econ    occupational series 0110 (economist)
  ten     length of service: <2, 2-5, 5-10, 10-20, 20+   (years)
  edu     below BA (codes 01-12), BA (13-16), MA (17-20), PhD (21-22)
  gs      GS grade band: GS<=8, GS9-12, GS13, GS14-15, Non-GS   (GS pay plan only,
          so the coded 1998-2024 cubes and the 2023-25 text files are comparable)
  reason  Quit, Retire_voluntary, Retire_early_out, Retire_other, RIF,
          Termination, Transfer, Death, Other

DoD caveat: in the Oct 2023 - Mar 2025 separation files every field except
agency, reason and month (occupation, tenure, education, pay plan, grade) is
REDACTED for Army, Navy, Air Force and defense agencies (~35% of rows). Those
rows get ten/edu/gs = "unk" and econ = False; analyses that use tenure,
education or grade must exclude DoD in every period (see analyze_episodes.py).

Inputs are read straight from the zips in data/raw/fedscope/_downloads/
(fetched by fetch_fedscope.py and fetch_fedscope_history.py); outputs go to
data/processed/panels/ and are git-ignored (rebuild in a few minutes).

Usage:
    python src/build_panels.py
"""

import zipfile
from pathlib import Path

import pandas as pd

from fetch_fedscope_history import fetch_panel_inputs

DL = Path(__file__).parent.parent / "data" / "raw" / "fedscope" / "_downloads"
OUT = Path(__file__).parent.parent / "data" / "processed" / "panels"

SEP_REASON = {
    "SA": "Transfer", "SB": "Transfer", "SC": "Quit", "SD": "Retire_voluntary",
    "SE": "Retire_early_out", "SF": "Retire_other", "SG": "Retire_other",
    "SH": "RIF", "SJ": "Termination", "SK": "Death", "SL": "Other",
}
TEN_BINS = [-1, 2, 5, 10, 20, 1000]
TEN_LABELS = ["<2", "2-5", "5-10", "10-20", "20+"]

# (zip name, member substring, delimiter, era)
SEP_SOURCES = [
    ("separations_FY2005-2009.zip", "SEPDATA", ",", "coded"),
    ("separations_FY2010-2014.zip", "SEPDATA", ",", "coded"),
    ("separations_FY2015-2019.zip", "SEPDATA", ",", "coded"),
    ("separations_FY2020-2024.zip", "SEPDATA", ",", "coded"),   # really ends Sep 2023
    ("separations_202310_to_202403.zip", ".txt", "|", "text"),
    ("separations_202404_to_202503.zip", "Separations.txt", "|", "text"),
]


def _read(zip_name: str, member_sub: str, sep: str, usecols: list[str]) -> pd.DataFrame:
    with zipfile.ZipFile(DL / zip_name) as zf:
        member = next(n for n in zf.namelist() if member_sub in n and not n.lower().endswith(".pdf"))
        with zf.open(member) as f:
            return pd.read_csv(f, sep=sep, dtype=str, usecols=lambda c: c in usecols,
                               encoding="latin-1", low_memory=False)


def _ten(los: pd.Series) -> pd.Series:
    x = pd.cut(pd.to_numeric(los, errors="coerce"), TEN_BINS, labels=TEN_LABELS, right=False)
    return x.astype(object).where(x.notna(), "unk")


def _edu(code: pd.Series) -> pd.Series:
    n = pd.to_numeric(code, errors="coerce")
    out = pd.Series("unk", index=code.index, dtype=object)
    out[n.between(1, 12)] = "below BA"
    out[n.between(13, 16)] = "BA"
    out[n.between(17, 20)] = "MA"
    out[n.between(21, 22)] = "PhD"
    return out


def _gs_band(n: pd.Series, is_gs: pd.Series, redacted: pd.Series) -> pd.Series:
    out = pd.Series("Non-GS", index=n.index, dtype=object)
    band = pd.cut(n, [0, 8, 12, 13, 15], labels=["GS<=8", "GS9-12", "GS13", "GS14-15"])
    ok = is_gs & band.notna()
    out[ok] = band[ok].astype(object)
    out[redacted] = "unk"
    return out


# --------------------------------------------------------------------------
# stock
# --------------------------------------------------------------------------

def build_stock() -> pd.DataFrame:
    frames = []
    for year in range(2004, 2025):
        d = _read(f"employment_{year}09.zip", "FACTDATA", ",",
                  ["AGYSUB", "OCC", "LOS", "EDLVL", "PPGRD", "EMPLOYMENT"])
        ppgrd = d["PPGRD"].fillna("")
        is_gs = ppgrd.str.startswith("GS-")
        gnum = pd.to_numeric(ppgrd.str.slice(3, 5), errors="coerce")
        g = pd.DataFrame({
            "year": year,
            "agysub": d["AGYSUB"],
            "econ": d["OCC"].eq("0110"),
            "ten": _ten(d["LOS"]),
            "edu": _edu(d["EDLVL"]),
            "gs": _gs_band(gnum, is_gs, pd.Series(False, index=d.index)),
            "n": pd.to_numeric(d["EMPLOYMENT"], errors="coerce").fillna(1),
        })
        frames.append(g.groupby(["year", "agysub", "econ", "ten", "edu", "gs"], as_index=False)["n"].sum())
        print(f"  stock Sep {year}: {int(frames[-1]['n'].sum()):,} employees")
    return pd.concat(frames, ignore_index=True)


# --------------------------------------------------------------------------
# separations
# --------------------------------------------------------------------------

def build_separations() -> pd.DataFrame:
    frames = []
    for zip_name, member, delim, era in SEP_SOURCES:
        cols = ["AGYSUB", "SEP", "EFDATE", "EDLVL", "LOS", "OCC", "COUNT"]
        cols += ["PPGRD"] if era == "coded" else ["PAYPLAN", "GRD"]
        d = _read(zip_name, member, delim, cols)
        if era == "coded":
            ppgrd = d["PPGRD"].fillna("")
            is_gs = ppgrd.str.startswith("GS-")
            gnum = pd.to_numeric(ppgrd.str.slice(3, 5), errors="coerce")
            red = pd.Series(False, index=d.index)
        else:
            red = d["PAYPLAN"].eq("REDACTED")
            is_gs = d["PAYPLAN"].eq("GS")
            gnum = pd.to_numeric(d["GRD"], errors="coerce")
        g = pd.DataFrame({
            "month": pd.to_numeric(d["EFDATE"], errors="coerce").astype("Int64"),
            "agysub": d["AGYSUB"],
            "econ": d["OCC"].eq("0110"),
            "reason": d["SEP"].map(SEP_REASON).fillna("Other"),
            "ten": _ten(d["LOS"]),
            "edu": _edu(d["EDLVL"]),
            "gs": _gs_band(gnum, is_gs, red),
            "n": pd.to_numeric(d["COUNT"], errors="coerce").fillna(1),
        })
        agg = g.groupby(["month", "agysub", "econ", "reason", "ten", "edu", "gs"], as_index=False)["n"].sum()
        print(f"  {zip_name}: {int(agg['n'].sum()):,} separations, "
              f"{agg.month.min()}-{agg.month.max()}")
        frames.append(agg)
    return pd.concat(frames, ignore_index=True)


def run_all() -> None:
    fetch_panel_inputs()
    OUT.mkdir(parents=True, exist_ok=True)
    print("stock panel (Sept snapshots):")
    stock = build_stock()
    stock.to_csv(OUT / "stock_sept.csv.gz", index=False)
    print("separations panel:")
    sep = build_separations()
    sep.to_csv(OUT / "sep_monthly.csv.gz", index=False)
    print(f"\nwrote {OUT}/ : stock {len(stock):,} rows, separations {len(sep):,} rows")


if __name__ == "__main__":
    run_all()
