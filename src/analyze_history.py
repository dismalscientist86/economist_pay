"""
Long-run context for the 2024 -> 2025 change, from historical FedScope
(fetch_fedscope_history.py):

  1. Federal economists (series 0110) since September 1998 -- headcount, real
     pay, PhD share, seniority.
  2. Separations by reason and fiscal year, FY2015 - FY2025 H1, plus a
     calendar-Q1 (Jan-Mar) comparison across years and a separation *rate*
     (separations / headcount) so years are comparable.

Outputs (output/tables/):
  fedscope_economists_since_1998.csv
  fedscope_separations_by_fy_reason.csv
  fedscope_flows_q1_2015_2025.csv
  fedscope_separation_rate_by_fy.csv

Usage:
    python src/analyze_history.py
"""

import glob
import re
from pathlib import Path

import numpy as np
import pandas as pd

HISTORY_DIR = Path(__file__).parent.parent / "data" / "raw" / "fedscope" / "history"
PROCESSED = Path(__file__).parent.parent / "data" / "processed"
TABLES = Path(__file__).parent.parent / "output" / "tables"

# CPI-U, U.S. city average, all items, NSA (BLS CUUR0000SA0), September values;
# retrieved 2026-09-09. Everything is expressed in March 2025 dollars.
CPI_SEP = {
    1998: 163.6, 1999: 167.9, 2000: 173.7, 2001: 178.3, 2002: 181.0,
    2003: 185.2, 2004: 189.9, 2005: 198.8, 2006: 202.9, 2007: 208.490,
    2008: 218.783, 2009: 215.969, 2010: 218.439, 2011: 226.889,
    2012: 231.407, 2013: 234.149, 2014: 238.031, 2015: 237.945,
    2016: 241.428, 2017: 246.819, 2018: 252.439, 2019: 256.759,
    2020: 260.280, 2021: 274.310, 2022: 296.808, 2023: 307.789, 2024: 315.301,
}
CPI_MAR2025 = 319.799
BASE_CPI = CPI_MAR2025

# Separation reason: OPM SEP code -> bucket, and the pre-2025 vs 2025 text
# labels -> the same buckets.
SEP_BUCKET = {
    "SA": "Transfer", "SB": "Transfer",
    "SC": "Quit",
    "SD": "Retirement", "SE": "Retirement", "SF": "Retirement", "SG": "Retirement",
    "SH": "RIF",
    "SJ": "Termination", "SK": "Death", "SL": "Other",
}
TEXT_SEP_BUCKET = {
    "Transfer Out - Individual Transfer": "Transfer",
    "Transfer Out - Mass Transfer": "Transfer",
    "Quit": "Quit",
    "Retirement - Voluntary": "Retirement", "Retirement - Early Out": "Retirement",
    "Retirement - Disability": "Retirement", "Retirement - Other": "Retirement",
    "Reduction In Force (RIF)": "RIF",
    "Termination (Expired Appt/Other)": "Termination",
    "Death": "Death", "Other Separation": "Other",
}
ACC_BUCKET = {"AA": "Transfer in", "AB": "Transfer in",
              "AC": "New hire", "AD": "New hire", "AE": "New hire"}
TEXT_ACC_BUCKET = {
    "Transfer In - Individual Transfer": "Transfer in",
    "Transfer In - Mass Transfer": "Transfer in",
    "New Hire - Competitive Service Appointment": "New hire",
    "New Hire - Excepted Service Appointment": "New hire",
    "New Hire - Senior Executive Service (SES) Appt": "New hire",
}

PHD_EDLVL = {"21", "22"}          # doctorate / post-doctorate (coded files)


def _salary(s: pd.Series) -> pd.Series:
    return pd.to_numeric(s.astype(str).str.replace(r"[\$,]", "", regex=True),
                         errors="coerce")


# --------------------------------------------------------------------------
# 1. Employment since 1998
# --------------------------------------------------------------------------

def employment_series() -> pd.DataFrame:
    rows = []
    for path in sorted(glob.glob(str(HISTORY_DIR / "employment_*_economists.csv"))):
        yyyymm = int(re.search(r"employment_(\d{6})_", path).group(1))
        year = yyyymm // 100
        df = pd.read_csv(path, dtype=str)
        df = df[df["OCC"] == "0110"]
        sal = _salary(df["SALARY"])
        real = sal * BASE_CPI / CPI_SEP[year]
        rows.append({
            "period": f"Sep {year}", "date": yyyymm, "source": "FedScope cube",
            "headcount": len(df),
            "mean_salary_nominal": round(sal.mean()),
            "mean_salary_2025usd": round(real.mean()),
            "median_salary_2025usd": round(real.median()),
            "mean_los": round(pd.to_numeric(df["LOS"], errors="coerce").mean(), 1),
            "phd_share": round(df["EDLVL"].isin(PHD_EDLVL).mean(), 3),
            "share_gs14plus": round(
                (pd.to_numeric(df["GSEGRD"], errors="coerce") >= 14).mean(), 3),
        })

    # March 2025 from the record-level processed file (text labels, GRD/education)
    m = pd.read_csv(PROCESSED / "fedscope_economists_202503.csv",
                    dtype={"series": str, "grade": str})
    m = m[m["series_label"] == "economist"]
    sal = m["salary"]
    rows.append({
        "period": "Mar 2025", "date": 202503, "source": "FedScope record-level",
        "headcount": 4888,  # OPM summary total; record-level identifies ~4,670
        "mean_salary_nominal": round(sal.mean()),
        "mean_salary_2025usd": round(sal.mean()),
        "median_salary_2025usd": round(sal.median()),
        "mean_los": round(m["los"].mean(), 1),
        "phd_share": round(m["education"].str.contains("DOCTOR", na=False).mean(), 3),
        # this file has raw GRD, not the OPM-computed GS-equivalent (GSEGRD) the
        # cube rows use, so the GS-14+ share is not comparable -- leave it out
        "share_gs14plus": np.nan,
    })

    out = pd.DataFrame(rows).sort_values("date").reset_index(drop=True)
    out["headcount_vs_1998"] = (out["headcount"] / out["headcount"].iloc[0] - 1).round(3)
    # ~550 Department of State positions were reclassified out of series 0110
    # between Sep 2005 and Sep 2006 (Foreign Service economic officers), so the
    # 1998-2005 counts are ~550 higher than the post-2006 universe.
    out["coverage_note"] = np.where(
        out["date"] // 100 <= 2005,
        "includes ~550 State Dept positions reclassified out of 0110 after 2005", "")
    _write(out, "fedscope_economists_since_1998.csv")
    return out


# --------------------------------------------------------------------------
# Unified flow history
# --------------------------------------------------------------------------

def _load_flows() -> pd.DataFrame:
    frames = []

    # pre-2025 coded files: AGYSUB, SEP/ACC, EFDATE, ..., OCC, ..., SALARY, LOS
    for path in glob.glob(str(HISTORY_DIR / "*_fy20*_economists.csv")) + \
                glob.glob(str(HISTORY_DIR / "*_fy2015_2019_economists.csv")):
        df = pd.read_csv(path, dtype=str)
        direction = "separation" if "separation" in path else "accession"
        code_col = "SEP" if direction == "separation" else "ACC"
        bkt = SEP_BUCKET if direction == "separation" else ACC_BUCKET
        df = df[df["OCC"] == "0110"]
        frames.append(pd.DataFrame({
            "direction": direction,
            "month": df["EFDATE"].astype(int),
            "reason_code": df[code_col],
            "reason_bucket": df[code_col].map(bkt),
            "salary": _salary(df["SALARY"]),
            "los": pd.to_numeric(df["LOS"], errors="coerce"),
        }))

    # 2025-era text files (Oct 2023 - Mar 2024 here; Apr 2024 - Mar 2025 from repo)
    text_files = [
        (HISTORY_DIR / "separations_202310_202403_economists.csv", "separation"),
        (HISTORY_DIR / "accessions_202310_202403_economists.csv", "accession"),
        (HISTORY_DIR.parent / "separations_202404_202503_economists.csv", "separation"),
        (HISTORY_DIR.parent / "accessions_202404_202503_economists.csv", "accession"),
    ]
    for path, direction in text_files:
        df = pd.read_csv(path, dtype=str)
        df = df[df["OCC"] == "0110"]
        label_col = "SEPT" if direction == "separation" else "ACCT"
        bkt = TEXT_SEP_BUCKET if direction == "separation" else TEXT_ACC_BUCKET
        frames.append(pd.DataFrame({
            "direction": direction,
            "month": df["EFDATE"].astype(int),
            "reason_code": df[label_col],
            "reason_bucket": df[label_col].map(bkt),
            "salary": _salary(df["SALARY"]),
            "los": pd.to_numeric(df["LOS"], errors="coerce"),
        }))

    fl = pd.concat(frames, ignore_index=True).drop_duplicates()
    fl["cal_year"] = fl["month"] // 100
    fl["cal_q"] = (fl["month"] % 100 - 1) // 3 + 1
    fl["fiscal_year"] = fl["cal_year"] + (fl["month"] % 100 >= 10)
    return fl


# --------------------------------------------------------------------------
# 2. Separations by fiscal year and reason
# --------------------------------------------------------------------------

def separations_by_fy_reason(fl: pd.DataFrame) -> pd.DataFrame:
    sep = fl[fl["direction"] == "separation"]
    # FY2015-2024 are complete; FY2025 here is only Oct 2024 - Mar 2025.
    sep = sep[sep["fiscal_year"].between(2015, 2025)]
    tab = (sep.pivot_table(index="fiscal_year", columns="reason_bucket",
                           values="month", aggfunc="count", fill_value=0))
    tab["total"] = tab.sum(axis=1)
    tab = tab.reset_index()
    tab["note"] = np.where(tab["fiscal_year"] == 2025,
                           "PARTIAL - Oct 2024-Mar 2025 only", "full fiscal year")
    _write(tab, "fedscope_separations_by_fy_reason.csv", index=False)
    return tab


# --------------------------------------------------------------------------
# 3. Calendar-Q1 (Jan-Mar) comparison across years
# --------------------------------------------------------------------------

def flows_q1_by_year(fl: pd.DataFrame) -> pd.DataFrame:
    q1 = fl[(fl["cal_q"] == 1) & fl["cal_year"].between(2015, 2025)]
    rows = []
    for yr, g in q1.groupby("cal_year"):
        acc = (g["direction"] == "accession").sum()
        s = g[g["direction"] == "separation"]
        rows.append({
            "jan_mar": int(yr),
            "accessions": int(acc),
            "separations": len(s),
            "net": int(acc) - len(s),
            "sep_quit": int((s["reason_bucket"] == "Quit").sum()),
            "sep_retirement": int((s["reason_bucket"] == "Retirement").sum()),
            "sep_termination": int((s["reason_bucket"] == "Termination").sum()),
            "sep_transfer": int((s["reason_bucket"] == "Transfer").sum()),
            "sep_rif": int((s["reason_bucket"] == "RIF").sum()),
        })
    out = pd.DataFrame(rows)
    _write(out, "fedscope_flows_q1_2015_2025.csv", index=False)
    return out


# --------------------------------------------------------------------------
# 4. Separation rate (separations / headcount) by fiscal year
# --------------------------------------------------------------------------

def separation_rate(fl: pd.DataFrame, emp: pd.DataFrame) -> pd.DataFrame:
    # headcount at the *start* of each FY = the prior September snapshot
    head = emp.set_index(emp["date"] // 100)["headcount"]
    sep = fl[fl["direction"] == "separation"]
    rows = []
    for fy in range(2015, 2025):
        n = int((sep["fiscal_year"] == fy).sum())
        base = head.get(fy - 1, np.nan)          # Sep of prior calendar year
        rows.append({"fiscal_year": fy, "separations": n,
                     "headcount_start": int(base) if base == base else None,
                     "separation_rate": round(n / base, 3) if base == base else None})
    # FY2025 partial (6 months) annualised for rough comparability
    n25 = int((sep["fiscal_year"] == 2025).sum())
    base25 = head.get(2024, np.nan)
    rows.append({"fiscal_year": 2025, "separations": n25,
                 "headcount_start": int(base25),
                 "separation_rate": round(n25 / base25, 3),
                 })
    out = pd.DataFrame(rows)
    out["note"] = np.where(out["fiscal_year"] == 2025,
                           "6 months only (Oct 2024-Mar 2025); rate is half-year",
                           "")
    _write(out, "fedscope_separation_rate_by_fy.csv", index=False)
    return out


# --------------------------------------------------------------------------

def _write(df: pd.DataFrame, name: str, index: bool = True) -> None:
    TABLES.mkdir(parents=True, exist_ok=True)
    df.to_csv(TABLES / name, index=index)
    print(f"  wrote {name}")


def run_all() -> None:
    if not list(HISTORY_DIR.glob("employment_*_economists.csv")):
        raise FileNotFoundError("Run: python src/fetch_fedscope_history.py")

    print("1. federal economists since 1998")
    emp = employment_series()
    print(emp[["period", "headcount", "mean_salary_2025usd", "phd_share",
               "share_gs14plus"]].to_string(index=False), "\n")

    fl = _load_flows()
    print("2. separations by fiscal year and reason")
    r = separations_by_fy_reason(fl)
    print(r.to_string(index=False), "\n")

    print("3. Jan-Mar flows by year")
    q = flows_q1_by_year(fl)
    print(q.to_string(index=False), "\n")

    print("4. separation rate by fiscal year")
    print(separation_rate(fl, emp).to_string(index=False), "\n")

    print(f"All tables -> {TABLES}/")


if __name__ == "__main__":
    run_all()
