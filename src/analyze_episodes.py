"""
Three-episode "who leaves" study.

Question: when federal workplace conditions change abruptly, who separates --
and does it differ from the same agency's normal turnover?

Episodes (all occupations for power; economists as a focal subgroup)
  E1  USDA Economic Research Service relocation   treated AG18, Jul-Dec 2019
      (announced Aug 2019)                          comparison: other USDA
  E2  Commerce in-person mandate                  treated CM* ex-Census, Mar 2022-Feb 2023
      (6 in-person days / pay period, Mar 2022)     comparison: all other non-DoD
      Census is reported separately: its decennial hiring cycle swamps the aggregate.
  E3  2025: return-to-office order (Jan 20) and   treated all non-DoD, Jan-Mar 2025
      deferred-resignation offer (Jan 28)           no untreated group; co-timed

Method. Separation rate = separations in the window / employees at a September
snapshot before the window starts (Sept of the prior year; the stock is therefore
pre-event, not drained by the event itself). Tenure is the stock's tenure at that
September versus tenure at separation, so bins are shifted by up to ~1 year, the same
way in event and baseline windows. Each
episode window is compared with the same calendar window in baseline years
(pre-pandemic, 2011-2018 or 2011-2019), pooling person-years. Output is the rate
ratio (event / baseline) overall and by tenure, education, GS grade band and
reason, with Poisson 95% CIs; for E1/E2 also the ratio of treated to comparison
rate ratios.

DoD is excluded throughout (tenure, education, grade and occupation are redacted
for DoD in the Oct 2023-Mar 2025 files), except in the agency-level 2025
dose-response table, which needs only counts.

Outputs (output/tables/):
  episodes_rates.csv, episodes_did.csv, episodes_leaver_mix.csv,
  episodes_commerce_bureaus.csv, episodes_E2_placebo.csv,
  episodes_commerce_bureau_placebo.csv, episodes_E3_q1_series.csv,
  episodes_E3_excess.csv, episodes_dose_response_2025.csv,
  episodes_dose_response_stats.csv

Usage:
    python src/build_panels.py        # once
    python src/analyze_episodes.py
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Optional

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

from agency_xwalk import load_telework_exposure

ROOT = Path(__file__).parent.parent
PANELS = ROOT / "data" / "processed" / "panels"
TABLES = ROOT / "output" / "tables"

DOD = {"AR", "NV", "AF", "DD"}
TEN_ORDER = ["<2", "2-5", "5-10", "10-20", "20+"]
EDU_ORDER = ["below BA", "BA", "MA", "PhD"]
GS_ORDER = ["GS<=8", "GS9-12", "GS13", "GS14-15", "Non-GS"]
Z = 1.96


@dataclass
class Episode:
    key: str
    name: str
    window: str
    start_month: int
    n_months: int
    event_year: int
    base_years: list
    denom_offset: int              # which September: event_year + offset
    treated: Callable
    comparison: Optional[Callable] = None
    comp_label: str = ""
    sectors: list = field(default_factory=lambda: ["all", "econ"])


EPISODES = [
    Episode("E1", "ERS relocation", "Jul-Dec 2019", 7, 6, 2019, list(range(2011, 2019)), -1,
            treated=lambda d: d.agysub.eq("AG18"),
            comparison=lambda d: d.agy.eq("AG") & d.agysub.ne("AG18"), comp_label="other USDA"),
    Episode("E2", "Commerce (ex-Census) in-person mandate", "Mar 2022-Feb 2023", 3, 12, 2022,
            list(range(2011, 2020)), -1,
            treated=lambda d: d.agy.eq("CM") & d.agysub.ne("CM63"),
            comparison=lambda d: ~d.agy.eq("CM") & ~d.agy.isin(DOD), comp_label="all other non-DoD"),
    Episode("E3", "2025 RTO order + buyout", "Jan-Mar 2025", 1, 3, 2025, list(range(2011, 2020)), -1,
            treated=lambda d: ~d.agy.isin(DOD), sectors=["all", "econ", "non_econ"]),
]


# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------

def months_in(year: int, start: int, n: int) -> list:
    out, y, m = [], year, start
    for _ in range(n):
        out.append(y * 100 + m)
        m += 1
        if m > 12:
            m, y = 1, y + 1
    return out


def load():
    stock = pd.read_csv(PANELS / "stock_sept.csv.gz",
                        dtype={"agysub": str, "ten": str, "edu": str, "gs": str})
    sep = pd.read_csv(PANELS / "sep_monthly.csv.gz",
                      dtype={"agysub": str, "ten": str, "edu": str, "gs": str, "reason": str})
    for d in (stock, sep):
        d["agy"] = d["agysub"].str.slice(0, 2)
        d["econ"] = d["econ"].astype(bool)
    return stock, sep


def sector_mask(d: pd.DataFrame, sector: str) -> pd.Series:
    if sector == "econ":
        return d.econ
    if sector == "non_econ":
        return ~d.econ
    return pd.Series(True, index=d.index)


def _agg(df: pd.DataFrame, by: Optional[str]) -> pd.Series:
    if by is None:
        return pd.Series({"all": df["n"].sum()})
    return df.groupby(by)["n"].sum()


def rr_stats(e_sep, e_stock, b_sep, b_stock):
    if min(e_sep, b_sep) <= 0 or min(e_stock, b_stock) <= 0:
        return np.nan, np.nan, np.nan
    rr = (e_sep / e_stock) / (b_sep / b_stock)
    se = np.sqrt(1 / e_sep + 1 / b_sep)
    return rr, rr * np.exp(-Z * se), rr * np.exp(Z * se)


def rate_rows(sep, stock, ep: Episode, grp: Callable, sector: str, dims=("all", "ten", "edu", "gs", "reason")):
    ev_months = months_in(ep.event_year, ep.start_month, ep.n_months)
    base_months = [m for y in ep.base_years for m in months_in(y, ep.start_month, ep.n_months)]
    ev_stock_year = ep.event_year + ep.denom_offset
    base_stock_years = [y + ep.denom_offset for y in ep.base_years]

    s = sep[grp(sep) & sector_mask(sep, sector)]
    k = stock[grp(stock) & sector_mask(stock, sector)]
    rows = []
    for dim in dims:
        s_use, k_use = s, k
        if dim in ("ten", "edu", "gs"):
            s_use, k_use = s[s[dim] != "unk"], k[k[dim] != "unk"]
        by_s = None if dim == "all" else dim
        by_k = dim if dim in ("ten", "edu", "gs") else None
        e_sep = _agg(s_use[s_use.month.isin(ev_months)], by_s)
        b_sep = _agg(s_use[s_use.month.isin(base_months)], by_s)
        e_stock = _agg(k_use[k_use.year == ev_stock_year], by_k)
        b_stock = _agg(k_use[k_use.year.isin(base_stock_years)], by_k)
        for lvl in e_sep.index.union(b_sep.index):
            es = float(e_sep.get(lvl, 0))
            bs = float(b_sep.get(lvl, 0))
            ek = float(e_stock.get(lvl, e_stock.iloc[0] if by_k is None else 0))
            bk = float(b_stock.get(lvl, b_stock.iloc[0] if by_k is None else 0))
            rr, lo, hi = rr_stats(es, ek, bs, bk)
            rows.append(dict(sector=sector, dim=dim, level=lvl, e_sep=es, e_stock=ek,
                             b_sep=bs, b_stock=bk,
                             e_rate_pct=100 * es / ek if ek else np.nan,
                             b_rate_pct=100 * bs / bk if bk else np.nan,
                             rr=rr, rr_lo=lo, rr_hi=hi, small=bool(min(es, bs) < 10)))
    return pd.DataFrame(rows)


# --------------------------------------------------------------------------
# main tables
# --------------------------------------------------------------------------

def run_episodes(sep, stock):
    rate_frames, did_frames, mix_frames = [], [], []
    for ep in EPISODES:
        groups = [("treated", ep.treated)]
        if ep.comparison is not None:
            groups.append(("comparison", ep.comparison))
        per = {}
        for gname, fn in groups:
            for sector in ep.sectors:
                df = rate_rows(sep, stock, ep, fn, sector)
                df.insert(0, "group", gname)
                df.insert(0, "episode", ep.key)
                rate_frames.append(df)
                per[(gname, sector)] = df

        # ratio of rate ratios (treated vs comparison)
        if ep.comparison is not None:
            for sector in ep.sectors:
                t, c = per[("treated", sector)], per[("comparison", sector)]
                m = t.merge(c, on=["sector", "dim", "level"], suffixes=("_t", "_c"))
                m["did_ratio"] = m["rr_t"] / m["rr_c"]
                se = np.sqrt(1 / m.e_sep_t.clip(lower=1) + 1 / m.b_sep_t.clip(lower=1)
                             + 1 / m.e_sep_c.clip(lower=1) + 1 / m.b_sep_c.clip(lower=1))
                m["did_lo"] = m["did_ratio"] * np.exp(-Z * se)
                m["did_hi"] = m["did_ratio"] * np.exp(Z * se)
                m["small"] = m.small_t | m.small_c
                m.insert(0, "episode", ep.key)
                did_frames.append(m[["episode", "sector", "dim", "level", "rr_t", "rr_c",
                                     "did_ratio", "did_lo", "did_hi", "small"]]
                                  .rename(columns={"rr_t": "rr_treated", "rr_c": "rr_comparison"}))

        # who the leavers are: shares of separations, event vs baseline (treated)
        for sector in ep.sectors:
            t = per[("treated", sector)]
            for dim in ("ten", "edu", "gs", "reason"):
                x = t[t.dim == dim].copy()
                tot_e, tot_b = x.e_sep.sum(), x.b_sep.sum()
                x["event_share"] = x.e_sep / tot_e if tot_e else np.nan
                x["baseline_share"] = x.b_sep / tot_b if tot_b else np.nan
                mix_frames.append(x[["episode", "sector", "dim", "level", "e_sep", "b_sep",
                                     "event_share", "baseline_share"]])

    rates = pd.concat(rate_frames, ignore_index=True)
    did = pd.concat(did_frames, ignore_index=True) if did_frames else pd.DataFrame()
    mix = pd.concat(mix_frames, ignore_index=True)
    _write(rates.round(4), "episodes_rates.csv")
    _write(did.round(4), "episodes_did.csv")
    _write(mix.round(4), "episodes_leaver_mix.csv")
    return rates, did, mix


# --------------------------------------------------------------------------
# E2 detail: bureaus and placebo years
# --------------------------------------------------------------------------

def commerce_bureaus(sep, stock):
    ep = next(e for e in EPISODES if e.key == "E2")
    bureaus = {"BEA": ["CM53"], "NOAA": ["CM54"], "PTO": ["CM56"], "NIST": ["CM57"], "Census": ["CM63"]}
    named = [c for v in bureaus.values() for c in v]
    bureaus["Other Commerce"] = None
    bureaus["Commerce ex-Census (pooled)"] = "EXCENSUS"
    comp = rate_rows(sep, stock, ep, ep.comparison, "all", dims=("all",)).iloc[0]
    rows = []
    for name, codes in bureaus.items():
        if codes is None:
            fn = lambda d: d.agy.eq("CM") & ~d.agysub.isin(named)
        elif codes == "EXCENSUS":
            fn = lambda d: d.agy.eq("CM") & d.agysub.ne("CM63")
        else:
            fn = lambda d, codes=codes: d.agysub.isin(codes)
        r = rate_rows(sep, stock, ep, fn, "all", dims=("all",)).iloc[0]
        did = r.rr / comp.rr if comp.rr == comp.rr else np.nan
        se = np.sqrt(1 / max(r.e_sep, 1) + 1 / max(r.b_sep, 1) + 1 / max(comp.e_sep, 1) + 1 / max(comp.b_sep, 1))
        rows.append(dict(bureau=name, employees_sep22=r.e_stock, e_sep=r.e_sep, b_sep=r.b_sep,
                         e_rate_pct=r.e_rate_pct, b_rate_pct=r.b_rate_pct, rr=r.rr,
                         comparison_rr=comp.rr, did_ratio=did,
                         did_lo=did * np.exp(-Z * se), did_hi=did * np.exp(Z * se)))
    out = pd.DataFrame(rows).round(4)
    _write(out, "episodes_commerce_bureaus.csv")
    return out


def e2_placebo(sep, stock):
    """Is Commerce's Mar 2022-Feb 2023 relative separation rate unusual vs other years?"""
    base_all = list(range(2011, 2020))
    rows = []
    for y in range(2012, 2024):
        rel = {}
        for gname, fn in (("treated", lambda d: d.agy.eq("CM") & d.agysub.ne("CM63")),
                          ("comparison", lambda d: ~d.agy.eq("CM") & ~d.agy.isin(DOD))):
            ep = Episode("P", "placebo", "", 3, 12, y, [b for b in base_all if b != y], -1, treated=fn)
            r = rate_rows(sep, stock, ep, fn, "all", dims=("all",)).iloc[0]
            rel[gname] = r
        did = rel["treated"].rr / rel["comparison"].rr
        rows.append(dict(window_start=f"Mar {y}", year=y, commerce_rr=rel["treated"].rr,
                         comparison_rr=rel["comparison"].rr, did_ratio=did,
                         commerce_sep=rel["treated"].e_sep, commerce_rate_pct=rel["treated"].e_rate_pct))
    out = pd.DataFrame(rows).round(4)
    _write(out, "episodes_E2_placebo.csv")
    return out


def bureau_placebo(sep, stock):
    """Each Commerce bureau's Mar-Feb separation rate relative to its own 2011-2019
    baseline, for every window year -- is Mar 2022 unusual for that bureau?"""
    base_all = list(range(2011, 2020))
    bureaus = {"BEA": ["CM53"], "NOAA": ["CM54"], "PTO": ["CM56"], "NIST": ["CM57"], "Census": ["CM63"]}
    rows = []
    for name, codes in bureaus.items():
        fn = lambda d, codes=codes: d.agysub.isin(codes)
        for y in range(2012, 2024):
            ep = Episode("P", "placebo", "", 3, 12, y, [b for b in base_all if b != y], -1, treated=fn)
            r = rate_rows(sep, stock, ep, fn, "all", dims=("all",)).iloc[0]
            rows.append(dict(bureau=name, window_start=f"Mar {y}", year=y, rr=r.rr, e_sep=r.e_sep,
                             rate_pct=r.e_rate_pct))
    out = pd.DataFrame(rows)
    out["rank_of_2022"] = out.groupby("bureau")["rr"].rank(ascending=False, method="min")
    out = out.round(4)
    _write(out, "episodes_commerce_bureau_placebo.csv")
    return out


def e3_excess(sep, stock):
    """Q1 2025 separations beyond what the 2011-2019 Jan-Mar rate would imply, by tenure
    and reason (non-DoD). Rate-adjusted: the workforce was ~12% larger in 2025 than in the
    baseline years, so raw count differences would overstate the excess."""
    ep = next(e for e in EPISODES if e.key == "E3")
    ev = months_in(2025, 1, 3)
    bm = [m for y in ep.base_years for m in months_in(y, 1, 3)]
    ev_stock_year = 2025 + ep.denom_offset
    base_stock_years = [y + ep.denom_offset for y in ep.base_years]
    s = sep[~sep.agy.isin(DOD) & (sep.ten != "unk")]
    k = stock[~stock.agy.isin(DOD) & (stock.ten != "unk")]
    rows = []
    for sector in ("econ", "non_econ"):
        xs, xk = s[sector_mask(s, sector)], k[sector_mask(k, sector)]
        for ten in TEN_ORDER + ["ALL"]:
            ts = xs if ten == "ALL" else xs[xs.ten == ten]
            tk = xk if ten == "ALL" else xk[xk.ten == ten]
            e_stock = tk[tk.year == ev_stock_year].n.sum()
            b_stock = tk[tk.year.isin(base_stock_years)].n.sum()
            for reason in ["ALL"] + sorted(xs.reason.unique()):
                tr = ts if reason == "ALL" else ts[ts.reason == reason]
                e = tr[tr.month.isin(ev)].n.sum()
                b = tr[tr.month.isin(bm)].n.sum()
                expected = (b / b_stock) * e_stock if b_stock else np.nan
                rows.append(dict(sector=sector, tenure=ten, reason=reason, q1_2025=e,
                                 expected_at_baseline_rate=expected, excess=e - expected,
                                 e_rate_pct=100 * e / e_stock if e_stock else np.nan,
                                 b_rate_pct=100 * b / b_stock if b_stock else np.nan))
    out = pd.DataFrame(rows).round(2)
    _write(out, "episodes_E3_excess.csv")
    return out


# --------------------------------------------------------------------------
# E3: Q1 series and agency dose-response
# --------------------------------------------------------------------------

def e3_q1_series(sep, stock):
    rows = []
    for y in range(2011, 2026):
        months = months_in(y, 1, 3)
        for sector in ("all", "econ"):
            s = sep[~sep.agy.isin(DOD) & sector_mask(sep, sector) & sep.month.isin(months)]
            k = stock[~stock.agy.isin(DOD) & sector_mask(stock, sector) & (stock.year == y - 1)]
            q = s[s.reason.eq("Quit")].n.sum()
            ret = s[s.reason.isin(["Retire_voluntary", "Retire_early_out"])].n.sum()
            rows.append(dict(jan_mar=y, sector=sector, separations=s.n.sum(), stock_sep_prev=k.n.sum(),
                             rate_pct=100 * s.n.sum() / k.n.sum(), quits=q, retirements=ret,
                             terminations=s[s.reason.eq("Termination")].n.sum(),
                             transfers=s[s.reason.eq("Transfer")].n.sum()))
    out = pd.DataFrame(rows).round(4)
    _write(out, "episodes_E3_q1_series.csv")
    return out


def dose_response(sep, stock):
    ep = next(e for e in EPISODES if e.key == "E3")
    exp = load_telework_exposure()
    ev_months = months_in(2025, 1, 3)
    base_months = [m for y in ep.base_years for m in months_in(y, 1, 3)]
    rows = []
    for _, r in exp.iterrows():
        codes = r["agy"]
        s = sep[sep.agy.isin(codes)]
        k = stock[stock.agy.isin(codes)]
        e = s[s.month.isin(ev_months)]
        b = s[s.month.isin(base_months)]
        ek = k[k.year == 2024].n.sum()
        bk = k[k.year.isin([y - 1 for y in ep.base_years])].n.sum()
        vol = ["Quit", "Retire_voluntary", "Retire_early_out"]
        rr, lo, hi = rr_stats(e.n.sum(), ek, b.n.sum(), bk)
        rrv, _, _ = rr_stats(e[e.reason.isin(vol)].n.sum(), ek, b[b.reason.isin(vol)].n.sum(), bk)
        rows.append(dict(agency=r["short"], agy="/".join(codes), employees_sep24=ek,
                         e_sep=e.n.sum(), e_rate_pct=100 * e.n.sum() / ek,
                         b_rate_pct=100 * b.n.sum() / bk, rr=rr, rr_lo=lo, rr_hi=hi,
                         rr_voluntary=rrv, inperson_pct=r["inperson_pct"],
                         remote_share=r["remote_share"], tw_eligible_share=r["tw_eligible_share"],
                         dod=bool(set(codes) & DOD)))
    out = pd.DataFrame(rows)
    stats = []
    for y in ("rr", "rr_voluntary"):
        for x in ("inperson_pct", "remote_share", "tw_eligible_share"):
            d = out[[x, y]].dropna()
            rho, p = spearmanr(d[x], d[y])
            stats.append(dict(outcome=y, exposure=x, n=len(d), spearman_rho=round(rho, 3), p=round(p, 3)))
    _write(out.round(4), "episodes_dose_response_2025.csv")
    _write(pd.DataFrame(stats), "episodes_dose_response_stats.csv")
    return out, pd.DataFrame(stats)


# --------------------------------------------------------------------------

def _write(df: pd.DataFrame, name: str) -> None:
    TABLES.mkdir(parents=True, exist_ok=True)
    df.to_csv(TABLES / name, index=False)
    print(f"  wrote {name}")


def run_all() -> None:
    if not (PANELS / "sep_monthly.csv.gz").exists():
        raise FileNotFoundError("Run: python src/build_panels.py")
    stock, sep = load()
    print("episodes:")
    rates, did, mix = run_episodes(sep, stock)
    print("E2 detail:")
    commerce_bureaus(sep, stock)
    e2_placebo(sep, stock)
    bureau_placebo(sep, stock)
    print("E3 detail:")
    e3_q1_series(sep, stock)
    e3_excess(sep, stock)
    dose_response(sep, stock)

    pd.set_option("display.width", 200)
    print("\n== overall rate ratios (event / baseline), all occupations ==")
    o = rates[(rates.dim == "all") & (rates.sector == "all")]
    print(o[["episode", "group", "e_sep", "e_rate_pct", "b_rate_pct", "rr", "rr_lo", "rr_hi"]].round(2).to_string(index=False))


if __name__ == "__main__":
    run_all()
