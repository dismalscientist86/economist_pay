# Who leaves when federal workplace conditions change? Three episodes

*Draft — 2026-11-10. Combines the economist analysis (this repo) with the
`Federal-Remote-Work` project (submodule). Preliminary; read the caveats.*

## Summary

Three abrupt changes to federal workplace conditions, compared with each unit's
own normal turnover:

| episode | window | what happened to separations | who left |
|---|---|---|---|
| **E1** USDA ERS relocation | Jul–Dec 2019 | **3.6×** normal (DiD vs. other USDA: 3.5×) | skewed to long tenure: **9–10×** at 10+ years vs. 3× under 2 years |
| **E2** Commerce in-person mandate | Mar 2022–Feb 2023 | +13% (DiD +11%) — **but no break at the mandate** | mild, spread across 2–20 years; see placebo |
| **E3** 2025 (return-to-office order and ordinary-channel exits; DRP exits fall later) | Jan–Mar 2025 | **+25%** (highest Q1 since at least 2011) | outside economics, **20+ years** dominates; economists show a **barbell** |

- **E1 is a clear effect.** ERS separations roughly quadrupled and shifted toward
  experienced staff and toward retirements/transfers.
- **E2 does not show a mandate-timed effect.** The Commerce (ex-Census) rate was
  modestly above normal, but equally unusual windows appear in 2012 and 2023, and the
  one bureau with a large elevation (PTO) was already elevated a year *before* the
  mandate.
- **E3 is a real, broad surge, but its cause cannot be pinned down.** These Q1 exits are *not*
  deferred-resignation (DRP) exits: DRP participants (flagged in the monthly OPM files) stopped
  working around March but stayed on the payroll until September–December 2025. The January 20,
  2025 order ending remote work, probationary terminations and agency drawdowns overlap. Agencies with less in-person work saw larger increases
  (Spearman ρ = −0.51, n = 24), but agencies subject to separate, targeted
  reductions in 2025 (e.g., Education, USAID) are also low-in-person agencies.
- **Economists in 2025** lost about 38 more people than their normal Q1 rate implies
  (137 vs. 99 expected, non-DoD): **+19 with under 2 years of service, +23 with 20+
  years, and no excess at 2–20 years.** This replaces the memo's earlier "mid-career
  departures" description.

## Design

**Unit and outcome.** Separation rate = separations in a window ÷ employees at the
September snapshot before the window starts (so the stock is pre-event, not drained by
the event). The window is compared with the *same calendar window* in baseline years
(pre-pandemic: 2011–2018 for E1, 2011–2019 for E2 and E3), pooling person-years. The
headline statistic is the **rate ratio** (event ÷ baseline) with Poisson 95% intervals,
overall and by tenure, education, GS grade band and reason. For E1 and E2 the
**ratio of rate ratios** (treated ÷ comparison) is a difference-in-differences.

| | treated | comparison | baseline years |
|---|---|---|---|
| E1 | ERS (`AG18`), all occupations | other USDA | 2011–2018 |
| E2 | Commerce **excluding Census**, all occupations | all other non-DoD agencies | 2011–2019 |
| E3 | all non-DoD agencies (economists and non-economists shown separately) | none | 2011–2019 |

Census is reported separately: its decennial hiring cycle swamps the Commerce
aggregate (its Mar–Feb separation rate swings between 0.5× and 1.8× of normal).

**Data.** OPM FedScope: Sept employment cubes 2004–2024 and separation files
Oct 2004–Mar 2025, aggregated by `src/build_panels.py` (all occupations; tenure,
education, GS band, reason, agency, economist flag). Agency telework exposure comes
from the two 2024 CSVs in the `Federal-Remote-Work` submodule, linked through
`src/agency_xwalk.py`.

**Exclusions.** DoD is excluded throughout the tenure/education/grade analyses: in the
Oct 2023–Mar 2025 files, occupation, tenure, education, pay plan and grade are
REDACTED for Army, Navy, Air Force and the defense agencies (~35% of rows). DoD is
used only in the agency-level dose-response, which needs counts.

## Results

### E1 — ERS relocation (announced Aug 2019)

Separation rate in Jul–Dec 2019: **41.8%** of the prior-September stock vs. 11.7% in
the same half-year of 2011–18 (RR **3.57**, 95% CI 2.89–4.40); other USDA 1.02. Rate
ratios by length of service:

| tenure | ERS RR (95% CI) | other USDA RR |
|---|---|---|
| < 2 yrs | 3.3 (2.2–4.9) | 1.10 |
| 2–5 | 2.3 (1.2–4.3) | 0.89 |
| 5–10 | 5.3 (2.4–11.8) | 1.15 |
| 10–20 | 9.2 (4.3–19.6) | 1.03 |
| 20+ | **9.7** (6.7–14.0) | 1.21 |

Leavers were far more senior than usual (43% had 20+ years vs. 20% normally; 23% had
under 2 years vs. 60%) and left by retirement (47% vs. 20%) and transfer (23% vs. 7%)
rather than by early quit or termination. 59 of the 120 separations were economists
(RR 5.4, CI 3.9–7.5). This also corrects the earlier memo: ERS explains about half of
FY2019's jump in economist separations, not all of it.

### E2 — Commerce in-person mandate (March 2022)

Commerce ex-Census: RR **1.13** (1.09–1.18) vs. 1.02 for the comparison group, DiD
**1.11** (1.06–1.16). By tenure the DiD is 1.16–1.24 for 2–20 years and 0.90 at 20+
(the comparison group had a retirement bump in 2022); economists (30 separations) show
no effect (RR 0.88, 0.60–1.28).

**The placebo says not to read this as a mandate effect.** Repeating the calculation
for every Mar–Feb window, Commerce ex-Census's DiD is:

| 2012 | 2013 | 2014 | 2015 | 2016 | 2017 | 2018 | 2019 | 2020 | 2021 | **2022** | 2023 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1.17 | 0.92 | 0.99 | 1.02 | 1.01 | 0.93 | 0.92 | 0.99 | 1.04 | 1.05 | **1.11** | 1.22 |

2022 ranks third; 2023 and 2012 are as large. By bureau (DiD vs. comparison):
**PTO 1.37** (1.27–1.49), NOAA 1.12 (1.05–1.21), NIST 0.96, BEA 0.80 (0.57–1.14),
other 0.95, Census 0.88. But PTO's separation rate was already 1.47× its own norm in the
**Mar 2021** window (1.01 in 2019 and 2020), a year before the mandate, and stays
elevated through 2023. Whether the Commerce policy even applied to PTO's largely
remote examiner workforce is not established here.

### E3 — 2025: return-to-office order and ordinary-channel exits (Jan–Mar)

Non-DoD separations Jan–Mar 2025: **41,857** (2.72% of the September 2024 stock) vs.
2.17% in Q1 2011–19, RR **1.25** (1.24–1.27) — the highest first-quarter rate in the
series (previous peak 2.49% in 2022; 1.88% in 2024).

*Outside economics* the excess is senior and is coded as quits and "Other":

| tenure | RR | share of rate-adjusted excess |
|---|---|---|
| < 2 yrs | 1.11 | 15% |
| 2–5 | 1.14 | 9% |
| 5–10 | 1.09 | 5% |
| 10–20 | 1.17 | 10% |
| 20+ | **1.55** | **52%** |

By reason (total excess ≈ 8,400): "Other Separation" **+4,394** (17 expected, 4,411
observed — a code that was essentially unused in 2011–19 Q1s), quits +4,203,
voluntary retirement +927, early-out +492, transfers −948. They are not DRP exits —
DRP-flagged separations are coded Quit or Retirement (58 of 141,000 are "Other") — and the data
do not say what they are.

*Economists* (non-DoD): 137 separations vs. 99 expected at the 2011–19 rate (RR 1.38,
1.15–1.66; 2.86% quarterly rate, also the highest in 2011–25):

| tenure | Q1 2025 | expected | excess | RR (95% CI) |
|---|---|---|---|---|
| < 2 yrs | 37 | 18.3 | **+18.7** | 2.02 (1.39–2.92) |
| 2–5 | 24 | 26.4 | −2.4 | 0.91 |
| 5–10 | 15 | 14.1 | +0.9 | 1.07 |
| 10–20 | 10 | 14.0 | −4.0 | 0.72 |
| 20+ | 51 | 28.2 | **+22.8** | 1.81 (1.34–2.44) |

Across all tenures the economist excess is quits (+12.7), terminations (+11.0) and
"Other" (+8.9), plus retirements (voluntary +5.7, early-out +5.9); transfers were 5.4
*below* normal. Broken out by tenure (unadjusted counts), the under-2-year excess is
mostly quits, terminations and "Other" and the 20+ excess is mostly retirements. Junior
economists account for half the economist excess versus 15% in the rest of government.

**Agency telework exposure** (Federal-Remote-Work CSVs; all occupations, DoD included,
rate ratios by agency): ρ(RR, in-person share) = **−0.51** (p = 0.011, n = 24);
ρ(RR, remote share) = +0.27 (p = 0.20); for voluntary exits only (quits + voluntary and
early-out retirement), ρ(RR, in-person) = −0.27 (p = 0.20). Largest ratios: Education
4.7, Commerce 2.4, EPA 2.2, GSA 2.1, USAID 2.0, SSA 1.9; smallest: SBA 0.82, DoD 0.84,
Interior 0.91, VA 0.97, Treasury 1.01.

## What this does and does not show

- **E1 is the only episode with a clear, mandate-timed effect**, and it is the
  relocation, not telework.
- **No evidence the 2022 Commerce mandate drove separations**, at the department level
  or for economists; the PTO elevation predates it.
- **2025 is a large, broad surge that mixes several things**: the return-to-office order,
  probationary terminations and agency-specific drawdowns. The deferred resignation program is a
  separate, later wave (effective Sept–Dec 2025) that this Q1 window does not contain. The negative
  correlation with in-person share is suggestive but not identified — the most-affected
  agencies were targeted for reasons unrelated to telework.
- **Economists** look like the rest of government at the senior end (retirements) but
  lost proportionally more new hires (quits, terminations).

## Caveats

1. **One treated unit per episode** (E1, E2) and **no untreated group** (E3). The E2
   placebo shows year-to-year variation well beyond the Poisson intervals, so narrow
   CIs should not be taken at face value; E3 has no comparison year with the same
   policy mix.
2. **Pandemic-era baselines.** Baselines stop at 2019, but the 2021–22 "Great
   Resignation" overlaps E2; the comparison group absorbs the common part.
3. **Tenure mismatch.** Stock tenure is measured at the prior September and separation
   tenure at the separation date, so bins are shifted by up to about a year; the shift
   is the same in event and baseline windows.
4. **DoD is out of every tenure comparison** and DoD economists are unidentifiable
   after Oct 2023 (memo limitation 10). Non-DoD economists are ~95% of the series.
5. **Small cells.** Economist cells have 10–50 events; intervals are wide.
6. **Telework is observed only at the agency level** (2024 OPM report), not by person
   or by bureau, and it post-dates E1 and E2.
7. **Poisson intervals** ignore overdispersion in the baseline years.

## Reproducing

```bash
python src/build_panels.py          # ~5 min; downloads the two FY2005-14 separation files
python src/analyze_episodes.py      # tables in output/tables/episodes_*.csv
python src/make_figures.py --only episodes
# or: python main.py --episodes
git submodule update --init         # for the Federal-Remote-Work CSVs
```

Tables: `episodes_rates.csv` (every rate and ratio), `episodes_did.csv`,
`episodes_leaver_mix.csv`, `episodes_commerce_bureaus.csv`,
`episodes_E2_placebo.csv`, `episodes_commerce_bureau_placebo.csv`,
`episodes_E3_q1_series.csv`, `episodes_E3_excess.csv`,
`episodes_dose_response_2025.csv`, `episodes_dose_response_stats.csv`.
Figures: `who_leaves_episodes.pdf`, `econ_q1_2025_barbell.pdf`,
`e2_bureau_placebo.pdf`, `dose_response_2025.pdf`.

## Next steps

- Link the FEVS public files (`M:\opm_datasets`; agency-level, with self-reported gender,
  intent to leave and, in 2023, a telework item) to ask whether intent to leave tracks
  telework and gender, and whether it predicts actual exits.
- Use the quarterly cubes (Mar 2010–Mar 2024) for monthly denominators around March 2022.
- Extend with the June 2024 cube and later releases; add peer occupations (statisticians,
  analysts) as a comparison for economists.
- Fold the Federal-Remote-Work scripts onto the shared loaders (they currently use
  hardcoded paths and a corrupt-prone local archive).
