"""
Generate all figures for the Beamer slide deck.
Outputs PDF figures to output/figures/.

Usage:
    python src/make_figures.py
"""

import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd

TABLES    = Path(__file__).parent.parent / "output" / "tables"
FIGURES   = Path(__file__).parent.parent / "output" / "figures"
PROCESSED = Path(__file__).parent.parent / "data" / "processed"
FIGURES.mkdir(parents=True, exist_ok=True)

# ── Colour palette ──────────────────────────────────────────────────────────
BLUE   = "#2166AC"
RED    = "#D6604D"
GRAY   = "#888888"
LGRAY  = "#DDDDDD"
PAPER  = "#4DAC26"   # green for paper comparison series

plt.rcParams.update({
    "font.family":      "serif",
    "font.size":        12,
    "axes.spines.top":  False,
    "axes.spines.right":False,
    "axes.linewidth":   0.8,
    "grid.alpha":       0.35,
    "grid.linestyle":   "--",
    "figure.dpi":       150,
})

def save(name):
    plt.tight_layout()
    plt.savefig(FIGURES / f"{name}.pdf", bbox_inches="tight")
    plt.close()
    print(f"  Saved {name}.pdf")


# ── 1. Median salary by gender, 2015-2024 ───────────────────────────────────
def fig_salary_trends():
    df = pd.read_csv(TABLES / "salary_gap_by_year.csv", index_col=0)

    fig, axes = plt.subplots(1, 2, figsize=(10, 4))

    # Left: median salary levels
    ax = axes[0]
    ax.plot(df.index, df["median_male"]   / 1000, color=BLUE, marker="o", label="Men")
    ax.plot(df.index, df["median_female"] / 1000, color=RED,  marker="s", label="Women")
    ax.set_xlabel("Fiscal Year")
    ax.set_ylabel("Median Salary ($ thousands)")
    ax.set_title("Median Salary by Gender")
    ax.legend(frameon=False)
    ax.yaxis.set_major_formatter(mticker.FormatStrFormatter("$%g"))
    ax.set_xticks(df.index)
    ax.set_xticklabels(df.index, rotation=45)
    ax.grid(axis="y")

    # Right: gap %
    ax = axes[1]
    ax.bar(df.index, df["gap_pct"], color=[BLUE if g > 0 else RED for g in df["gap_pct"]], width=0.6)
    ax.axhline(0, color="black", linewidth=0.8)
    ax.set_xlabel("Fiscal Year")
    ax.set_ylabel("Men's Advantage (%)")
    ax.set_title("Median Salary Gap (Men − Women) / Men")
    ax.set_xticks(df.index)
    ax.set_xticklabels(df.index, rotation=45)
    ax.grid(axis="y")
    for yr, gap in zip(df.index, df["gap_pct"]):
        ax.text(yr, gap + 0.08, f"{gap:.1f}%", ha="center", va="bottom", fontsize=9)

    save("salary_trends")


# ── 2. Female share of federal economists by key agency, 2016-2024 ──────────
def fig_female_share_agency():
    df = pd.read_csv(TABLES / "female_share_by_agency_year.csv", index_col=0)
    df = df[df.index >= 2016]   # pre-2016 only has "All" and BLS/BEA/Census bureau-level

    # Select columns present throughout
    cols   = {
        "All":                              ("All", "black",  "-",  2.0),
        "Dept of Labor (incl. BLS)":        ("BLS (via Dept of Labor)", BLUE,   "-",  1.4),
        "BEA":                              ("BEA",          RED,   "--", 1.4),
        "Census Bureau":                    ("Census",       PAPER, "-.", 1.4),
        "Dept of Treasury":                 ("Treasury",     GRAY,  ":",  1.4),
        "Dept of Agriculture (incl. ERS)":  ("Agriculture",  "#8073AC", "-", 1.4),
    }

    fig, ax = plt.subplots(figsize=(8, 4.5))
    for col, (label, color, ls, lw) in cols.items():
        if col in df.columns:
            ax.plot(df.index, df[col], color=color, linestyle=ls,
                    linewidth=lw, marker="o", markersize=4, label=label)

    ax.set_xlabel("Fiscal Year")
    ax.set_ylabel("Female Share (%)")
    ax.set_title("Female Share of Federal Economists by Agency")
    ax.legend(frameon=False, fontsize=9, loc="upper left")
    ax.set_xticks(df.index)
    ax.set_xticklabels(df.index, rotation=45)
    ax.set_ylim(20, 55)
    ax.grid(axis="y")
    save("female_share_agency")


# ── 3. Salary by GS grade and gender (most recent year) ─────────────────────
def fig_grade_salary():
    df = pd.read_csv(TABLES / "salary_by_grade_all_years.csv")
    df = df.rename(columns={"Unnamed: 0": "grade", "Unnamed: 1": "gender"})
    # Reshape: grade, gender, median
    df = df.dropna(subset=["grade"])
    df["grade"] = pd.to_numeric(df["grade"], errors="coerce")
    df = df[df["grade"].between(7, 15)]

    male   = df[df["gender"] == "male"].set_index("grade")["median"]
    female = df[df["gender"] == "female"].set_index("grade")["median"]
    grades = sorted(set(male.index) & set(female.index))

    x = np.arange(len(grades))
    w = 0.35

    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.bar(x - w/2, [male[g]   / 1000 for g in grades], w, color=BLUE, label="Men",   alpha=0.9)
    ax.bar(x + w/2, [female[g] / 1000 for g in grades], w, color=RED,  label="Women", alpha=0.9)
    ax.set_xticks(x)
    ax.set_xticklabels([f"GS-{int(g)}" for g in grades])
    ax.set_xlabel("GS Grade")
    ax.set_ylabel("Median Salary ($ thousands)")
    ax.set_title("Median Salary by GS Grade and Gender (FY2015-2024 pooled)")
    ax.yaxis.set_major_formatter(mticker.FormatStrFormatter("$%g"))
    ax.legend(frameon=False)
    ax.grid(axis="y")
    save("grade_salary")


# ── 4. Salary gap by agency (all years) ──────────────────────────────────────
def fig_agency_gap():
    df = pd.read_csv(TABLES / "salary_by_agency_all_years.csv")
    df.columns = ["agency", "gender", "n", "median", "mean"]
    df = df.dropna(subset=["agency", "gender"])

    pivot = df.pivot_table(index="agency", columns="gender", values="median")
    pivot = pivot.dropna()
    pivot["gap_pct"] = (pivot["male"] - pivot["female"]) / pivot["male"] * 100

    # Drop "Dept of Commerce (other)" — too few and mixed
    pivot = pivot[~pivot.index.str.startswith("Dept of Commerce")]

    # Shorten labels
    label_map = {
        "BEA":                              "BEA",
        "BLS":                              "BLS",
        "Census Bureau":                    "Census Bureau",
        "Departmental Offices":             "Dept. Offices",
        "Dept of Agriculture (incl. ERS)":  "Agriculture (incl. ERS)",
        "Dept of Energy":                   "Energy",
        "Dept of HHS":                      "HHS",
        "Dept of Labor (incl. BLS)":        "Labor (incl. BLS)",
        "Dept of Treasury":                 "Treasury",
        "Economic Research Service":        "ERS (FY2015)",
        "Internal Revenue Service":         "IRS (FY2015)",
        "Other":                            "Other",
    }
    pivot.index = [label_map.get(i, i) for i in pivot.index]
    pivot = pivot.sort_values("gap_pct")

    colors = [RED if g < 0 else BLUE for g in pivot["gap_pct"]]

    fig, ax = plt.subplots(figsize=(8, 5.5))
    bars = ax.barh(pivot.index, pivot["gap_pct"], color=colors, alpha=0.85)
    ax.axvline(0, color="black", linewidth=0.8)
    ax.set_xlabel("Men's Salary Advantage (%)\n(negative = women earn more)")
    ax.set_title("Median Salary Gap by Agency (FY2015-2024 pooled)")
    ax.grid(axis="x")
    for bar, val in zip(bars, pivot["gap_pct"]):
        xpos = val + 0.1 if val >= 0 else val - 0.1
        ha   = "left"  if val >= 0 else "right"
        ax.text(xpos, bar.get_y() + bar.get_height() / 2,
                f"{val:.1f}%", va="center", ha=ha, fontsize=9)
    save("agency_gap")


# ── 5. Placement sector shares: our data vs. Early Career Paths paper ────────
def fig_placement_comparison():
    # Paper values from Table 1 (all programs)
    sectors = ["Academia", "Government", "Finance /\ncentral banks", "Consulting /\nprivate sector"]

    our_0107  = [58.1, 5.3, 9.1, 21.4]
    our_1417  = [63.0, 3.6, 7.3, 22.2]
    paper_0107 = [60.0, 5.0, 9.0, 22.0]
    paper_1417 = [54.0, 11.0, 9.0, 26.0]

    x  = np.arange(len(sectors))
    w  = 0.2

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.bar(x - 1.5*w, our_0107,   w, color=BLUE,  alpha=0.85, label="EconPhDPlacements, 2001-07")
    ax.bar(x - 0.5*w, our_1417,   w, color=BLUE,  alpha=0.50, label="EconPhDPlacements, 2014-17")
    ax.bar(x + 0.5*w, paper_0107, w, color=PAPER, alpha=0.85, label="Foster et al. (2023, JEP), 2001-07")
    ax.bar(x + 1.5*w, paper_1417, w, color=PAPER, alpha=0.50, label="Foster et al. (2023, JEP), 2014-17")

    ax.set_xticks(x)
    ax.set_xticklabels(sectors)
    ax.set_ylabel("Share of Placements (%)")
    ax.set_title("Initial Placement Shares: EconPhDPlacements vs. Foster et al. (2023, JEP)")
    ax.legend(frameon=False, fontsize=9)
    ax.grid(axis="y")

    note = ("Note: 'International orgs' (4-6% in EconPhDPlacements) not captured in paper (LEHD = US only).\n"
            "Paper: Foster, McEntarfer & Sandler (2023, JEP). Govt in paper = NAICS 92 only.")
    ax.text(0.01, -0.18, note, transform=ax.transAxes, fontsize=7.5,
            color=GRAY, va="top")
    save("placement_comparison")


# ── 6. Placement sector shares over time (our data) ──────────────────────────
def fig_placement_trends():
    df = pd.read_csv(TABLES / "placements_by_category_year.csv")
    df = df[df["year"] >= 2001]

    # Compute share within year
    totals = df.groupby("year")["n"].sum()
    df["share"] = df.apply(lambda r: r["n"] / totals[r["year"]] * 100, axis=1)

    cat_map = {
        "tenure_track":      "Tenure-track",
        "other_academic":    "Other academic",
        "private_sector":    "Private sector",
        "central_banks":     "Central banks",
        "government":        "Government",
        "think_tanks":       "Think tanks",
        "international_orgs":"International orgs",
    }
    colors_map = {
        "Tenure-track":      BLUE,
        "Other academic":    "#6BAED6",
        "Private sector":    RED,
        "Central banks":     "#FD8D3C",
        "Government":        PAPER,
        "Think tanks":       "#74C476",
        "International orgs":"#8073AC",
    }

    pivot = df.pivot_table(index="year", columns="category", values="share", aggfunc="sum").fillna(0)
    pivot.columns = [cat_map.get(c, c) for c in pivot.columns]

    # Smooth with 3-year rolling average for readability
    pivot_smooth = pivot.rolling(3, center=True, min_periods=1).mean()

    fig, ax = plt.subplots(figsize=(9, 5))
    for col in ["Tenure-track", "Other academic", "Private sector",
                "Central banks", "Government", "Think tanks", "International orgs"]:
        if col in pivot_smooth.columns:
            ax.plot(pivot_smooth.index, pivot_smooth[col],
                    color=colors_map[col], linewidth=1.8, label=col)

    ax.set_xlabel("Placement Year")
    ax.set_ylabel("Share of Placements (%, 3-yr moving avg.)")
    ax.set_title("PhD Economist Placement Shares Over Time")
    ax.legend(frameon=False, fontsize=8.5, loc="upper right", ncol=2)
    ax.set_xlim(2001, 2025)
    ax.grid(axis="y")
    save("placement_trends")


# ── 7. Female share by sector: our data vs. Diversity & Equity paper ─────────
def fig_female_sector_comparison():
    sectors   = ["Academia", "Industry", "Government\n(broad)"]
    ours_all  = [30.6, 30.4, 29.4]
    ours_0117 = [29.6, 31.2, 29.9]
    ours_1417 = [27.3, 28.2, 31.9]
    paper     = [32.8, 35.9, 38.5]

    x  = np.arange(len(sectors))
    w  = 0.18

    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.bar(x - 1.5*w, ours_0117, w, color=BLUE,  alpha=0.85, label="EconPhDPlacements, 2001-17")
    ax.bar(x - 0.5*w, ours_1417, w, color=BLUE,  alpha=0.50, label="EconPhDPlacements, 2014-17")
    ax.bar(x + 0.5*w, ours_all,  w, color=BLUE,  alpha=0.30, label="EconPhDPlacements, all years")
    ax.bar(x + 1.5*w, paper,     w, color=PAPER, alpha=0.85, label="Foster et al. (2023, JERP), 2017")

    ax.set_xticks(x)
    ax.set_xticklabels(sectors)
    ax.set_ylabel("Female Share (%)")
    ax.set_title("Female Share by Sector: EconPhDPlacements vs. Foster et al. (2023, JERP)")
    ax.axhline(34.6, color=PAPER, linestyle="--", linewidth=1.2, label="Paper overall (34.6%)")
    ax.legend(frameon=False, fontsize=8.5)
    ax.set_ylim(0, 50)
    ax.grid(axis="y")

    note = ("Note: Gender assigned via gender_guesser (50.5% of placements). Unassigned names\n"
            "skew international (likely male-heavy), so our female shares are likely understated.\n"
            "Paper uses self-reported SED gender (100% coverage). D&E = Diversity & Equity in\n"
            "Labor Market Outcomes for Economists (Foster, McEntarfer & Sandler, 2023, JERP).")
    ax.text(0.01, -0.28, note, transform=ax.transAxes, fontsize=7.5, color=GRAY, va="top")
    save("female_sector_comparison")


# ── 8. Federal salary gap vs. OPM paper comparison ───────────────────────────
def fig_salary_comparison_paper():
    """
    Side-by-side: our raw median gap vs. Foster et al. 2020 (OPM data) raw log gap.
    Both compare all federal economists; paper covers 2000-2015.
    """
    df = pd.read_csv(TABLES / "salary_gap_by_year.csv", index_col=0)

    # Paper's OPM result: raw log gap for white females = -1.41%;
    # with controls = -0.53%.  Shown as horizontal reference bands.
    fig, ax = plt.subplots(figsize=(8, 4.5))

    ax.plot(df.index, df["gap_pct"], color=BLUE, marker="o", linewidth=2,
            label="FedsDataCenter (median gap)")

    ax.axhspan(0, 1.41, alpha=0.12, color=PAPER,
               label="Foster et al. 2020 (OPM): raw gap for white women (1.4%)")
    ax.axhspan(0, 0.53, alpha=0.22, color=PAPER,
               label="Foster et al. 2020 (OPM): gap with agency+year controls (0.5%)")

    ax.axhline(0, color="black", linewidth=0.8)
    ax.set_xlabel("Fiscal Year")
    ax.set_ylabel("Men's Salary Advantage (%)")
    ax.set_title("Federal Economist Gender Salary Gap: FedsDataCenter vs. Prior Work")
    ax.legend(frameon=False, fontsize=8.5, loc="upper right")
    ax.set_xticks(df.index)
    ax.set_xticklabels(df.index, rotation=45)
    ax.set_ylim(-1, 6)
    ax.grid(axis="y")

    note = ("Our gap: raw median comparison (no controls). Paper gap: log earnings regression.\n"
            "Paper: Foster, Manzella, McEntarfer & Sandler (2020, AEA P&P), OPM data 2000-2015.")
    ax.text(0.01, -0.18, note, transform=ax.transAxes, fontsize=7.5, color=GRAY, va="top")
    save("salary_comparison_paper")


# ═══════════════════════════════════════════════════════════════════════════
# 2025 update (FedScope): has the number and pay of federal economists changed?
# Tables come from src/analyze_2025.py. September 2024 vs. preliminary
# March 2025, occupational series 0110. No gender in this source.
# ═══════════════════════════════════════════════════════════════════════════

ORANGE = "#E08214"   # FedScope series, to set it apart from FedsDataCenter


# ── 9. Headcount and mean pay, long run + 2025 ──────────────────────────────
def fig_fed_economists_2025():
    tr = pd.read_csv(TABLES / "fedscope_headcount_pay_trend.csv")
    fdc = tr[tr["source"].str.startswith("FedsDataCenter")].copy()
    fdc["year"] = fdc["period"].str.slice(2).astype(int)
    fs = tr[tr["source"].str.startswith("FedScope")].copy()
    fs_x = {"Sep 2024": 2024.5, "Mar 2025": 2025.0}
    fs["x"] = fs["period"].map(fs_x)

    hl = pd.read_csv(TABLES / "fedscope_headline_2024_2025.csv").set_index("measure")
    real_mar = hl.loc["mean_salary_real_cpi", "mar_2025"]

    fig, axes = plt.subplots(1, 2, figsize=(10, 4))

    ax = axes[0]
    ax.plot(fdc["year"], fdc["headcount"], color=BLUE, marker="o", label="FedsDataCenter (FOIA annual)")
    ax.plot(fs["x"], fs["headcount"], color=ORANGE, marker="D", markersize=7,
            linestyle="-", label="FedScope (EHRI month-end)")
    for _, r in fs.iterrows():
        ax.annotate(f"{int(r['headcount']):,}", (r["x"], r["headcount"]),
                    textcoords="offset points", xytext=(0, 8), ha="center", fontsize=9)
    ax.set_title("Number of Federal Economists (series 0110)")
    ax.set_ylabel("Headcount")
    ax.set_xlabel("Fiscal Year")
    ax.set_ylim(3800, 5200)
    ax.legend(frameon=False, fontsize=8.5, loc="lower left")
    ax.grid(axis="y")

    ax = axes[1]
    ax.plot(fdc["year"], fdc["mean_salary"] / 1000, color=BLUE, marker="o", label="FedsDataCenter")
    ax.plot(fs["x"], fs["mean_salary"] / 1000, color=ORANGE, marker="D", markersize=7,
            label="FedScope (nominal)")
    ax.plot([fs_x["Mar 2025"]], [real_mar / 1000], color=ORANGE, marker="o",
            markerfacecolor="white", markersize=8, label="Mar 2025, real (Sep-2024 $)")
    ax.set_title("Mean Adjusted Basic Pay")
    ax.set_ylabel("Mean Salary ($ thousands)")
    ax.set_xlabel("Fiscal Year")
    ax.yaxis.set_major_formatter(mticker.FormatStrFormatter("$%g"))
    ax.legend(frameon=False, fontsize=8.5, loc="upper left")
    ax.grid(axis="y")

    note = ("FedScope and FedsDataCenter are different universes (EHRI month-end status vs. annual FOIA extract);\n"
            "the March 2025 snapshot is preliminary and still counts administrative-leave / deferred-resignation staff.")
    fig.text(0.01, -0.04, note, fontsize=7.5, color=GRAY, va="top")
    save("fed_economists_2025")


# ── 10. March 2025 pay distribution ────────────────────────────────────────
def fig_econ_pay_distribution_2025():
    df = pd.read_csv(PROCESSED / "fedscope_economists_202503.csv",
                     dtype={"series": str, "grade": str})
    sal = df.loc[df["series_label"] == "economist", "salary"].dropna() / 1000

    hl = pd.read_csv(TABLES / "fedscope_headline_2024_2025.csv").set_index("measure")
    sep_mean = hl.loc["mean_salary_nominal", "sep_2024"] / 1000
    mar_mean = hl.loc["mean_salary_nominal", "mar_2025"] / 1000

    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.hist(sal, bins=40, color=BLUE, alpha=0.75, edgecolor="white", linewidth=0.4)
    ax.axvline(sal.median(), color="black", linestyle="-", linewidth=1.4,
               label=f"Mar 2025 median  ${sal.median():,.0f}k")
    ax.axvline(mar_mean, color=ORANGE, linestyle="--", linewidth=1.4,
               label=f"Mar 2025 mean  ${mar_mean:,.0f}k")
    ax.axvline(sep_mean, color=GRAY, linestyle=":", linewidth=1.6,
               label=f"Sep 2024 mean  ${sep_mean:,.0f}k")
    ax.set_xlabel("Adjusted Basic Pay ($ thousands)")
    ax.set_ylabel("Economists")
    ax.set_title("Federal Economist Pay Distribution, March 2025 (record-level, series 0110)")
    ax.legend(frameon=False, fontsize=9)
    ax.grid(axis="y")
    save("econ_pay_distribution_2025")


# ── 11. Headcount change by agency, Sep 2024 → Mar 2025 ────────────────────
def fig_econ_agency_change_2025():
    df = pd.read_csv(TABLES / "fedscope_by_agency_change.csv")
    df = df[df["coverage"] == "ok"].copy()

    fixups = {
        "Department Of Housing And Urban Developm": "Housing & Urban Dev.",
        "Department Of The Army": "Army",
    }

    def label(name):
        if name in fixups:
            return fixups[name]
        if name.isupper():                       # BLS, BEA, ERS
            return name
        return name.replace("Department Of ", "").replace(" And ", " & ")

    df["label"] = df["agency_group"].map(label)
    df = df.sort_values("headcount_change")

    colors = [RED if c < 0 else PAPER for c in df["headcount_change"]]
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.barh(df["label"], df["headcount_change"], color=colors, alpha=0.85)
    ax.axvline(0, color="black", linewidth=0.8)
    ax.set_xlabel("Change in economists, Sep 2024 → Mar 2025")
    ax.set_title("Where Federal Economists Were Gained and Lost")
    ax.grid(axis="x")
    for y, c in enumerate(df["headcount_change"]):
        ax.text(c + (0.4 if c >= 0 else -0.4), y, f"{c:+d}",
                va="center", ha="left" if c >= 0 else "right", fontsize=8)
    note = ("Agency × pay-plan × grade cells with ≤10 staff are suppressed, so this covers ~76% of\n"
            "economists; agencies whose count is small on either date are omitted.")
    ax.text(0.0, -0.13, note, transform=ax.transAxes, fontsize=7.5, color=GRAY, va="top")
    save("econ_agency_change_2025")


# ── 12. GS grade mix, Sep 2024 vs Mar 2025 ─────────────────────────────────
def fig_econ_grade_mix_2025():
    df = pd.read_csv(TABLES / "fedscope_by_grade_change.csv")
    df = df[df["gs_grade"].between(7, 15)]
    x = np.arange(len(df))
    w = 0.38

    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.bar(x - w/2, df["share_sep_2024"] * 100, w, color=GRAY, alpha=0.8, label="Sep 2024")
    ax.bar(x + w/2, df["share_mar_2025"] * 100, w, color=ORANGE, alpha=0.9, label="Mar 2025")
    ax.set_xticks(x)
    ax.set_xticklabels([f"GS-{int(g)}" for g in df["gs_grade"]])
    ax.set_xlabel("GS Grade")
    ax.set_ylabel("Share of GS economists (%)")
    ax.set_title("Grade Mix of GS Economists (shown cells, ~76% coverage)")
    ax.legend(frameon=False)
    ax.grid(axis="y")
    save("econ_grade_mix_2025")


# ── 13. Monthly accessions vs separations ──────────────────────────────────
def fig_econ_flows_2025():
    df = pd.read_csv(TABLES / "fedscope_flows_monthly_2025.csv")
    df["date"] = pd.to_datetime(df["month"].astype(str), format="%Y%m")
    prof = pd.read_csv(TABLES / "fedscope_flows_profile_2025.csv")

    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.bar(df["date"], df["accessions"], width=20, color=PAPER, alpha=0.85, label="Accessions (hires)")
    ax.bar(df["date"], -df["separations"], width=20, color=RED, alpha=0.85, label="Separations (departures)")
    ax.axhline(0, color="black", linewidth=0.8)
    ax.axvspan(pd.Timestamp("2025-01-01"), pd.Timestamp("2025-03-31"),
               color=GRAY, alpha=0.15)
    ax.set_ylabel("Economists per month")
    ax.set_title("Federal Economist Hires and Departures, April 2024 – March 2025")
    ax.legend(frameon=False, fontsize=9, loc="lower left")
    ax.grid(axis="y")

    acc = prof.set_index("direction").loc["accession"]
    sep = prof.set_index("direction").loc["separation"]
    note = (f"Shaded: Jan-Mar 2025. Joiners: mean {acc['mean_los']:.0f} yr service, "
            f"\\${acc['mean_salary']:,.0f}.  Leavers: mean {sep['mean_los']:.0f} yr, "
            f"\\${sep['mean_salary']:,.0f} (mid-career departures, not juniors).")
    ax.text(0.0, -0.15, note, transform=ax.transAxes, fontsize=7.5, color=GRAY, va="top")
    save("econ_flows_2025")


# ── 14. Separations by reason, by quarter ─────────────────────────────────
def fig_econ_separation_reasons_2025():
    df = pd.read_csv(TABLES / "fedscope_flows_by_reason_2025.csv")
    sep = df[df["direction"] == "separation"].copy()
    quarters = ["2024Q2", "2024Q3", "2024Q4", "2025Q1"]

    # Group the seven reason codes into five readable buckets
    bucket = {
        "Quit": "Quit",
        "Retirement - Voluntary": "Retirement",
        "Retirement - Early Out": "Retirement",
        "Retirement - Other": "Retirement",
        "Termination (Expired Appt/Other)": "Term-appt ended",
        "Transfer Out - Individual Transfer": "Transfer to another agency",
        "Other Separation": "Other",
    }
    sep["bucket"] = sep["action_type"].map(bucket)
    m = sep.groupby("bucket")[quarters].sum()

    order = ["Quit", "Retirement", "Term-appt ended", "Other", "Transfer to another agency"]
    colors = {"Quit": RED, "Retirement": "#FD8D3C", "Term-appt ended": "#B2182B",
              "Other": GRAY, "Transfer to another agency": "#6BAED6"}

    fig, ax = plt.subplots(figsize=(8, 4.5))
    bottom = np.zeros(len(quarters))
    for b in order:
        vals = m.loc[b, quarters].values if b in m.index else np.zeros(len(quarters))
        ax.bar(quarters, vals, bottom=bottom, label=b, color=colors[b], alpha=0.9)
        bottom += vals
    ax.set_ylabel("Economist separations")
    ax.set_title("Why Federal Economists Left, by Quarter (series 0110)")
    ax.legend(frameon=False, fontsize=8.5, loc="upper left")
    ax.grid(axis="y")
    note = ("2025 Q1 holds 86% of the year's early-out retirements, 64% of term-appointment\n"
            "endings, 42% of voluntary retirements and 37% of quits; transfers to other\n"
            "agencies fell — economists left government rather than moving within it.")
    ax.text(0.0, -0.17, note, transform=ax.transAxes, fontsize=7.5, color=GRAY, va="top")
    save("econ_separation_reasons_2025")


# ═══════════════════════════════════════════════════════════════════════════
# Long-run history (analyze_history.py): federal economists since 1998
# ═══════════════════════════════════════════════════════════════════════════

def fig_econ_headcount_since_1998():
    df = pd.read_csv(TABLES / "fedscope_economists_since_1998.csv")
    df["year"] = (df["date"] // 100).astype(float)
    df.loc[df["period"] == "Mar 2025", "year"] = 2025.25
    pre = df[df["date"] // 100 <= 2005]
    post = df[(df["date"] // 100 >= 2006) & (df["period"] != "Mar 2025")]
    mar = df[df["period"] == "Mar 2025"]

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(9, 6.5), sharex=True)

    ax1.plot(pre["year"], pre["headcount"], color=GRAY, marker="o", ms=4,
             label="pre-2006 (incl. ~550 State posts later reclassified)")
    ax1.plot(post["year"], post["headcount"], color=BLUE, marker="o", ms=4,
             label="FedScope cube (September)")
    ax1.plot(mar["year"], mar["headcount"], color=ORANGE, marker="D", ms=8,
             label="March 2025")
    ax1.axvline(2005.5, color=GRAY, ls=":", lw=1)
    ax1.set_ylim(4050, 5550)
    ax1.annotate("~550 State Dept posts\nreclassified out of 0110", (2005.5, 5250),
                 fontsize=7.5, color=GRAY, ha="center")
    ax1.annotate("ERS relocated to\nKansas City (FY2019)", (2019, 4281),
                 fontsize=7.5, color=GRAY, ha="center",
                 xytext=(2016.5, 4120), textcoords="data",
                 arrowprops=dict(arrowstyle="->", color=GRAY, lw=0.6))
    ax1.set_ylabel("Federal economists (series 0110)")
    ax1.set_title("Federal Economists, September 1998 – March 2025")
    ax1.legend(frameon=False, fontsize=8, loc="lower right", ncol=1)
    ax1.grid(axis="y")

    ax2.plot(post["year"], post["mean_salary_2025usd"] / 1000, color=PAPER,
             marker="o", ms=4, label="mean")
    ax2.plot(post["year"], post["median_salary_2025usd"] / 1000, color=PAPER,
             marker="o", ms=3, ls="--", alpha=0.6, label="median")
    ax2.plot(pre["year"], pre["mean_salary_2025usd"] / 1000, color=GRAY, marker="o", ms=3)
    ax2.plot(mar["year"], mar["mean_salary_2025usd"] / 1000, color=ORANGE, marker="D", ms=8)
    ax2.set_ylabel("Pay (2025 $ thousands)")
    ax2.set_xlabel("Year")
    ax2.set_title("Real Adjusted Basic Pay (CPI-U, March 2025 dollars)")
    ax2.yaxis.set_major_formatter(mticker.FormatStrFormatter("$%g"))
    ax2.legend(frameon=False, fontsize=8, loc="lower right")
    ax2.grid(axis="y")
    save("econ_headcount_since_1998")


def fig_econ_separations_history():
    df = pd.read_csv(TABLES / "fedscope_separations_by_fy_reason.csv")
    buckets = ["Quit", "Retirement", "Termination", "Transfer", "Other", "Death"]
    colors = {"Quit": RED, "Retirement": "#FD8D3C", "Termination": "#B2182B",
              "Transfer": "#6BAED6", "Other": GRAY, "Death": "#333333"}

    fig, ax = plt.subplots(figsize=(9, 4.5))
    bottom = np.zeros(len(df))
    for b in buckets:
        v = df[b].values if b in df.columns else np.zeros(len(df))
        ax.bar(df["fiscal_year"], v, bottom=bottom, color=colors[b], label=b,
               alpha=0.9, width=0.7)
        bottom += v
    # hatch the partial FY2025 bar
    ax.bar([2025], [df.loc[df.fiscal_year == 2025, "total"].iloc[0]], width=0.7,
           fill=False, hatch="///", edgecolor="black", lw=0.8)
    ax.set_xticks(df["fiscal_year"])
    ax.set_ylabel("Economist separations")
    ax.set_title("Federal Economist Separations by Reason and Fiscal Year")
    ax.legend(frameon=False, fontsize=8.5, ncol=3)
    ax.grid(axis="y")
    ax.text(0.0, -0.16, "FY = Oct–Sep. FY2025 (hatched) is Oct 2024 – Mar 2025 only "
            "— half a year already near a full prior year. FY2019's spike was the "
            "USDA/ERS relocation to Kansas City.",
            transform=ax.transAxes, fontsize=7.5, color=GRAY, va="top")
    save("econ_separations_history")


def fig_econ_q1_history():
    df = pd.read_csv(TABLES / "fedscope_flows_q1_2015_2025.csv")
    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.bar(df["jan_mar"], df["accessions"], width=0.7, color=PAPER, alpha=0.85,
           label="Accessions (Jan–Mar)")
    ax.bar(df["jan_mar"], -df["separations"], width=0.7, color=RED, alpha=0.85,
           label="Separations (Jan–Mar)")
    ax.axhline(0, color="black", lw=0.8)
    ax.text(2017, -128, "1st Trump\ntransition", ha="center", va="top",
            fontsize=7.5, color=GRAY)
    ax.text(2025, -140, "hiring freeze +\ndeferred resignation", ha="center",
            va="top", fontsize=7.5, color=GRAY)
    ax.set_xticks(df["jan_mar"])
    ax.set_ylabel("Economists (Jan–Mar)")
    ax.set_title("First-Quarter Hires and Departures, 2015–2025")
    ax.legend(frameon=False, fontsize=8.5, loc="upper left")
    ax.set_ylim(-165, 110)
    ax.grid(axis="y")
    save("econ_q1_history")


# ── Run all ──────────────────────────────────────────────────────────────────
def _gender_figures():
    fig_salary_trends()
    fig_female_share_agency()
    fig_grade_salary()
    fig_agency_gap()
    fig_placement_comparison()
    fig_placement_trends()
    fig_female_sector_comparison()
    fig_salary_comparison_paper()


def _fedscope_2025_figures():
    fig_fed_economists_2025()
    fig_econ_pay_distribution_2025()
    fig_econ_agency_change_2025()
    fig_econ_grade_mix_2025()
    fig_econ_flows_2025()
    fig_econ_separation_reasons_2025()
    fig_econ_headcount_since_1998()
    fig_econ_separations_history()
    fig_econ_q1_history()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--only", choices=["gender", "fedscope2025"],
                        help="Generate just one group of figures")
    args = parser.parse_args()

    print("Generating figures...")
    if args.only in (None, "gender"):
        _gender_figures()
    if args.only in (None, "fedscope2025"):
        _fedscope_2025_figures()
    print(f"Done. All figures saved to {FIGURES}/")
