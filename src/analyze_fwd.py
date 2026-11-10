"""
Economists (series 0110) through September 2026, from the monthly data.opm.gov
files reduced by extract_fwd.py -- the first look past March 2025.

Tables (output/tables/):
  fwd_headcount_monthly.csv    0110 headcount and the whole workforce, Sept 2024-Sept 2026,
                               indexed to Sept 2024
  fwd_flows_monthly.csv        economist separations (deferred-resignation-program flagged or
                               not) and hires by *effective* month
  fwd_drp_profile.csv          who took the deferred resignation program vs. other exits
  fwd_nondrp_rate_ratio.csv    non-DRP separation rate vs. the 2011-2019 same-month norm

Timing note: a person with drp_indicator = 'Y' stopped working around March 2025
but stayed on the payroll until separation (mostly Sept 30, 2025), so payroll
headcount through Sept 2025 overstates the working workforce by roughly the number
of DRP separations still to come.

Usage:
    python src/extract_fwd.py       # once
    python src/analyze_fwd.py
"""

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).parent.parent
FWD = ROOT / "data" / "processed" / "fwd"
OLD = ROOT / "data" / "processed" / "panels"
TABLES = ROOT / "output" / "tables"

BASE_YEARS = list(range(2011, 2020))
START, END = 202410, 202609


def _write(df: pd.DataFrame, name: str) -> None:
    TABLES.mkdir(parents=True, exist_ok=True)
    df.to_csv(TABLES / name, index=False)
    print(f"  wrote {name}")


def headcount(stock: pd.DataFrame, old_stock: pd.DataFrame) -> pd.DataFrame:
    econ = stock[stock.econ].groupby("month")["n"].sum()
    allw = stock.groupby("month")["n"].sum()
    o24 = old_stock[old_stock.year == 2024]
    base = pd.DataFrame({"month": [202409], "econ_0110": [int(o24[o24.econ].n.sum())],
                         "all_workforce": [int(o24.n.sum())]})
    cur = pd.DataFrame({"month": econ.index, "econ_0110": econ.values.astype(int),
                        "all_workforce": allw.reindex(econ.index).values.astype(int)})
    out = pd.concat([base, cur], ignore_index=True)
    b = out.iloc[0]
    out["econ_index"] = (100 * out.econ_0110 / b.econ_0110).round(1)
    out["all_index"] = (100 * out.all_workforce / b.all_workforce).round(1)
    out["econ_minus_all_pts"] = (out.econ_index - out.all_index).round(1)
    out["econ_change_vs_sep24"] = out.econ_0110 - int(b.econ_0110)
    _write(out, "fwd_headcount_monthly.csv")
    return out


def flows(sep: pd.DataFrame, acc: pd.DataFrame) -> pd.DataFrame:
    s = sep[sep.econ & sep.month.between(START, END)]
    sd = s.groupby(["month", "drp"])["n"].sum().unstack(fill_value=0)
    sd = sd.rename(columns={False: "sep_other", True: "sep_drp"})
    for c in ("sep_other", "sep_drp"):
        if c not in sd:
            sd[c] = 0
    a = acc[acc.econ & acc.month.between(START, END)].groupby("month")["n"].sum().rename("hires")
    out = sd.join(a, how="outer").fillna(0).astype(int)
    out["sep_total"] = out.sep_other + out.sep_drp
    out["net_non_drp"] = out.hires - out.sep_other
    out = out.reset_index()
    _write(out, "fwd_flows_monthly.csv")
    return out


def drp_profile(sep: pd.DataFrame) -> pd.DataFrame:
    s = sep[sep.month.between(START, END)]
    rows = []
    for sector, x in (("economists", s[s.econ]), ("all occupations", s)):
        for grp, g in (("DRP", x[x.drp]), ("other exits", x[~x.drp])):
            for dim in ("ten", "edu", "gs", "reason"):
                t = g.groupby(dim)["n"].sum()
                for lvl, n in t.items():
                    rows.append(dict(sector=sector, group=grp, dim=dim, level=lvl, n=int(n),
                                     share=n / t.sum()))
    out = pd.DataFrame(rows).round(4)
    _write(out, "fwd_drp_profile.csv")
    return out


def nondrp_rate_ratio(sep: pd.DataFrame, stock: pd.DataFrame, old_sep: pd.DataFrame,
                      old_stock: pd.DataFrame) -> pd.DataFrame:
    """Monthly non-DRP separations / prior-month payroll, vs. the 2011-2019 same-month rate
    (old panels use the preceding September's stock as the denominator)."""
    rows = []
    months = sorted(stock.month.unique())
    for sector in ("economists", "all occupations"):
        sm = (lambda d: d[d.econ]) if sector == "economists" else (lambda d: d)
        cur_sep = sm(sep[~sep.drp]).groupby("month")["n"].sum()
        cur_stock = sm(stock).groupby("month")["n"].sum()
        osep = sm(old_sep)
        ostk = sm(old_stock).groupby("year")["n"].sum()
        for m in months[1:]:
            prev = months[months.index(m) - 1]
            if m not in cur_sep.index:
                continue
            mo = m % 100
            num = den = 0.0
            for y in BASE_YEARS:
                num += osep[osep.month == y * 100 + mo].n.sum()
                den += ostk.get(y if mo >= 10 else y - 1, np.nan)
            base = 100 * num / den
            rate = 100 * cur_sep[m] / cur_stock[prev]
            rows.append(dict(sector=sector, month=int(m), nondrp_seps=int(cur_sep[m]),
                             stock_prev_month=int(cur_stock[prev]), rate_pct=rate,
                             baseline_rate_pct=base, rr=rate / base))
    out = pd.DataFrame(rows).round(3)
    _write(out, "fwd_nondrp_rate_ratio.csv")
    return out


def run_all() -> None:
    if not (FWD / "stock_monthly.csv.gz").exists():
        raise FileNotFoundError("Run: python src/extract_fwd.py")
    stock = pd.read_csv(FWD / "stock_monthly.csv.gz")
    sep = pd.read_csv(FWD / "sep_monthly_fwd.csv.gz")
    acc = pd.read_csv(FWD / "acc_monthly_fwd.csv.gz")
    old_stock = pd.read_csv(OLD / "stock_sept.csv.gz", dtype={"agysub": str})
    old_sep = pd.read_csv(OLD / "sep_monthly.csv.gz", dtype={"agysub": str})
    for d in (stock, sep, acc, old_stock, old_sep):
        d["econ"] = d["econ"].astype(bool)
    sep["drp"] = sep["drp"].astype(bool)

    pd.set_option("display.width", 200)
    print("headcount:")
    h = headcount(stock, old_stock)
    print(h.to_string(index=False))
    print("flows:")
    f = flows(sep, acc)
    print(f.to_string(index=False))
    print("DRP profile:")
    drp_profile(sep)
    print("non-DRP rate ratio:")
    r = nondrp_rate_ratio(sep, stock, old_sep, old_stock)
    print(r[r.sector == "economists"].to_string(index=False))


if __name__ == "__main__":
    run_all()
