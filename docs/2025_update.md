# Federal government economists, 2024 → 2026: has the number and pay changed?

*Draft findings memo — first written 2026-09-09; updated 2026-11-10 with OPM data through September 2026.*

## Bottom line

**Through September 2026 (§7), federal economists (series 0110) fell from 4,998 to 3,802
— down 24%, versus 13% for the federal workforce as a whole.** That is below every
year since at least 2006. Roughly 44% of the drop is the Deferred Resignation Program
(532 economists who stayed on the payroll until separating, mostly on September 30 (396)
or December 31 (115), 2025); most
of the rest is ordinary-channel exits combined with a hiring freeze that eased only in
mid-2026. Headcount stopped falling around spring 2026 and hiring has resumed (25–33
economists a month, June–September 2026).

**The original window, September 2024 → March 2025,** looked mild on the payroll: the
number of economists fell about 2% (4,998 → 4,888) and mean pay rose 2.8% nominal
(+1.4% real), almost entirely the January 2025 federal pay raise. But the March payroll
**overstates the working workforce**: participants in the deferred resignation program
(DRP) are reported to have stopped working around March 2025 while staying on the payroll
until they separated (the data show only the separation dates). About 530 of the 4,888
economists on the March payroll were such participants, so the working workforce was
nearer 4,350 — about 13% below September 2024, not 2%.

**The first-quarter 2025 exits in the flow data are not DRP exits** (those are dated
September–December 2025). They are ordinary-channel separations — 137 in Jan–Mar, the
most of any first quarter since 2015, against 36 hires, the fewest. Measured against normal
first-quarter turnover, the excess came from **both ends of the tenure distribution**:
about 19 above-normal separations among staff with under 2 years of service (quits,
terminations) and about 23 among staff with 20+ years (retirements, early-outs), while
economists with 2–20 years were not elevated (`docs/who_leaves_study.md`). Non-DRP exits
stayed elevated from February to July 2025 (1.4–2.3× the same-month 2011–19 norm, peaking in
April), returned to normal in August–December, and ran *below* normal throughout 2026.

**What caused the 2025 exits cannot be settled from this data.** The January 20, 2025 order
ending remote work, the January 28 deferred-resignation offer, probationary terminations
and, from June 2025, formal reductions in force (41 economist RIF separations April–September
2025, against none before) all overlap. DRP participants are identifiable; the rest are not.

In historical perspective (§6–7): through September 2025 the headcount was still near the
top of its post-2006 range; the DRP separations and later attrition took it to a
**post-2006 low**. The FY2025 outflow was also extreme by flow measures: the first six months
alone saw 218 economist separations (78% of all of FY2024's 279).

## Data and method

| | |
|---|---|
| Source | OPM FedScope "classic" raw datasets (`data/raw/fedscope/SOURCES.md`) |
| Snapshots | September 2024 and **preliminary** March 2025, bundled in one OPM release |
| Population | Occupational series **0110 (Economist)**, executive branch, active pay status |
| Pipeline | `python main.py --fedscope` → `src/analyze_2025.py` → `output/tables/fedscope_*` |
| Long-run context | `src/fetch_fedscope_history.py` → `src/analyze_history.py` (employment cubes to Sep 1998; separations/accessions to FY2015) |
| Figures | `python src/make_figures.py --only fedscope2025` |

FedsDataCenter.com — the source for the FY2015–2024 gender panel — stops at
FY2024, so this update switches sources. FedScope is a different universe (an
EHRI month-end status snapshot rather than an annual FOIA extract) and its raw
files **have never carried gender or race** — not in any cube from 1998 through
2025. (The interactive FedScope site did offer gender and race cuts; OPM took
those down in March 2025 under EOs 14151 / 14168 / 14173, which also removed
them from the replacement data.opm.gov platform.) The gender analysis in this
repo comes from name-based assignment on FedsDataCenter and therefore ends at
FY2024; this update is headcount and pay only.

Real values deflate the March 2025 mean to September 2024 dollars using
BLS CPI-U (+1.43% over the six months) and, separately, the ECI for wages and
salaries (+1.66%). The January 2025 federal pay adjustment was **2.0% on
average** (1.7% base + 0.3% locality; Executive Order 14139).

## Findings

### 1. Headcount

`output/tables/fedscope_headline_2024_2025.csv`, figure `fed_economists_2025.pdf`

| | Sep 2024 | Mar 2025 | change |
|---|---:|---:|---:|
| Economists (series 0110) | 4,998 | 4,888 | **−110 (−2.2%)** |
| Mean length of service | 12.4 yr | 12.6 yr | +0.2 yr |

The figure now uses **FedScope only** (September employment cubes, from
`fedscope_economists_since_1998.csv`) so there is no source break: the series
runs 4,469 (Sep 2015) → 4,281 (Sep 2019 trough) → 4,998 (Sep 2024 peak) → 4,888
(Mar 2025). See §6 for the full 1998– picture. The FedsDataCenter panel, used
for the gender analysis through FY2024, is a narrower universe (FY2024 count
4,718 vs. FedScope's 4,998) but tracks the same shape and nearly identical mean
pay ($146,848 vs. $146,952 for 2024).

### 2. Pay

`fedscope_headline_2024_2025.csv`, `fedscope_pay_distribution_2025.csv`,
figure `econ_pay_distribution_2025.pdf`

| | Sep 2024 | Mar 2025 | change |
|---|---:|---:|---:|
| Mean pay, nominal | $146,952 | $151,094 | **+$4,142 (+2.8%)** |
| Mean pay, real (CPI-U) | $146,952 | $148,969 | +$2,017 (+1.4%) |
| Mean pay, real (ECI) | $146,952 | $148,633 | +$1,681 (+1.1%) |

March 2025 record-level distribution: median **$148,716**, 10th percentile
$92,433, 90th percentile $200,691.

**Decomposition of the GS mean-pay change** (`fedscope_pay_change_decomp.csv`,
GS cells only, ~76% coverage): of the +$2,869 change in GS mean pay,

| component | $ | share |
|---|---:|---:|
| January 2025 pay raise (2.0%) | 2,735 | 95% |
| within-grade steps / promotions | 10 | 0% |
| grade-mix shift | 118 | 4% |
| interaction | 6 | 0% |

The workforce did not become materially more senior on the pay side over these
six months. The pay increase is the statutory raise.

### 3. Flows — the clearest signal

`fedscope_flows_quarterly_2025.csv`, `fedscope_flows_by_reason_2025.csv`,
`fedscope_flows_profile_2025.csv`, figures `econ_flows_2025.pdf` and
`econ_separation_reasons_2025.pdf`. Covers April 2024 – March 2025.

| quarter | hires | departures | net |
|---|---:|---:|---:|
| 2024 Q2 | 78 | 57 | +21 |
| 2024 Q3 | 145 | 81 | +64 |
| 2024 Q4 | 58 | 81 | −23 |
| **2025 Q1** | **36** | **137** | **−101** |

Hiring fell to a quarter of its mid-2024 pace while departures rose sharply.
Over the full year, 317 economists were hired and 356 left.

- **Leavers** over the year: mean **12.8 years** of federal service, mean pay
  **$144,938**; **joiners**: mean **1.9 years**, mean pay **$114,890**. (The leavers'
  average mostly reflects normal turnover; it says little about *who left more than
  usual*. Against the 2011–19 first-quarter norm, the 2025 excess is a barbell — under
  2 years and 20+ years of service — not mid-career staff. See
  `docs/who_leaves_study.md`.)

**Why they left.** 2025 Q1 is one of four quarters but holds a lopsided share of
the year's departures by reason:

| reason | full year | 2025 Q1 | Q1 share |
|---|---:|---:|---:|
| Quit | 136 | 50 | 37% |
| Retirement – Voluntary | 90 | 38 | 42% |
| Retirement – Early Out | 7 | 6 | 86% |
| Termination (term appointment ended) | 28 | 18 | 64% |
| Transfer to another agency | 66 | 13 | 20% |

Quits, voluntary and early-out retirements, and term-appointment endings all
spiked; only agency-to-agency **transfers fell** (20% of the year's total landed
in Q1, below the 25% an even quarter would carry). Economists were leaving
federal employment altogether, not moving within it — the early-out retirements
and term terminations point to reduction-in-force and buyout activity, not
ordinary turnover.

### 4. Where economists were gained and lost

`fedscope_by_agency_change.csv`, figure `econ_agency_change_2025.pdf` (agencies
with a solid count on both dates; ~76% coverage)

- **Lost:** BLS −24, BEA −14, Treasury −13, Agriculture (ex-ERS) −13, FTC −9,
  Transportation −11.
- **Gained:** Energy +17, FDIC +12, DHS +11, HHS +7, Census +6.

The statistical agencies (BLS, BEA) are among the losers; several financial and
energy agencies grew. This is net reallocation on top of the overall decline.

### 5. March 2025 workforce profile

`fedscope_profile_2025.csv` (record-level, single snapshot)

- **Pay system:** 75% GS, 23% other systems (higher-paid — SEC, FRS, FDIC pay
  plans average $185k), 2% SES/ES.
- **GS grade:** GS-13 the plurality (30%), GS-14 25%, GS-15 17%.
- **Appointment:** 96.5% permanent; 3.5% non-permanent (mean 5.1 years service).
- **Supervisory:** 16% supervisors/managers.
- **Education:** 29% doctorate, 31% master's, 25% bachelor's. Doctorate holders
  average $179,524 and cluster at HHS, Treasury, ERS, SEC, FTC.
- **Age:** 25% under 35; 21% 55 or older.

### 6. Historical context (1998–2025)

`fedscope_economists_since_1998.csv`, `fedscope_separations_by_fy_reason.csv`,
`fedscope_flows_q1_2015_2025.csv`, `fedscope_separation_rate_by_fy.csv`;
figures `econ_headcount_since_1998.pdf`, `econ_separations_history.pdf`,
`econ_q1_history.pdf`. Built by `src/analyze_history.py` from FedScope
employment cubes back to September 1998 and separation/accession files back to
FY2015.

**Headcount.** On a consistent post-2006 basis, federal economists ranged from a
low of ~4,280 (2008, and again 2019) to the September 2024 peak of 4,998. The
March 2025 figure of 4,888 is still near the top of that 20-year range — the
decline so far has unwound roughly one year of growth, back to about the 2023
level (4,883) as of March 2025. (By September 2026 it is a historic low — §7.) (Pre-2006 counts of
~5,000–5,400 include ~550 Department of State positions reclassified out of
series 0110 after 2005, so they overstate the earlier level.)

**Real pay.** In constant March 2025 dollars, mean pay rose from ~$133k (1998)
to a ~$160k peak around 2010, held near $155–158k through 2020, fell to ~$143k
in 2022 as inflation outran the raises, and has recovered to ~$152k. Today's
real pay is mid-range historically — above the late-1990s but still below the
2010 and 2018–2020 peaks.

**Composition.** The PhD share climbed from 20% (1998) to ~29% by the mid-2010s
and has been flat since (29.7% in March 2025). The GS-14-and-above share rose
from 23% (1998) to 32% (2020–2024).

**Separations — how 2025 compares.** Full fiscal years FY2015–FY2023 saw
321–461 economist separations (rate 7–11% of headcount). FY2024 was the calmest
year in the series — 279 separations, a 5.7% rate. Then **FY2025 recorded 218
separations in just its first six months** (Oct 2024–Mar 2025) — 78% of
FY2024's full-year total (4.4% of headcount in half a year, ~8.7% annualized),
and the reason mix shifted toward retirements (77 in six months vs. 65 in all of
FY2024) and term-appointment terminations (22 vs. 9).

The one clear historical precedent for elevated economist attrition is
**FY2019** (461 separations, 10.6% rate). The USDA decision to relocate the
Economic Research Service to Kansas City accounts for about half of that year's
jump: ERS economist separations tripled from 21 (FY2018) to 63 (FY2019),
concentrated in September 2019 (20 retirements, 11 transfers, 3 quits), while
all other agencies rose from 360 to 398. FY2025 differs in being
government-wide and retirement/termination-heavy.

**First-quarter comparison.** January–March is normally a modest-outflow
quarter. Jan–Mar 2025 had **137 separations and 36 accessions** — the most
departures and the fewest hires of any Q1 in 2015–2025. The previous high for
separations was 2017 (123, the first Trump transition); 2025 is higher and,
unlike 2017, pairs it with a hiring freeze.

**RIFs: none until June 2025, then a few.** Through March 2025 **zero** economist separations
carry OPM's Reduction-in-Force code, and OPM's FY2005–FY2014 separation files show just one in ten
years (FY2013), even though government-wide RIFs ran roughly 370–1,900 a year — economists almost
never leave by formal RIF. That changed after the window above: the monthly files (§7) show 41
economist RIF separations in April–September 2025 (22 in July) and 43 through September 2026.

### 7. Through September 2026 (monthly OPM files)

`fwd_headcount_monthly.csv`, `fwd_flows_monthly.csv`, `fwd_drp_profile.csv`,
`fwd_nondrp_rate_ratio.csv`; figure `fwd_economists_2026.pdf`. Built by `src/extract_fwd.py` and
`src/analyze_fwd.py` from the monthly Federal Workforce Data files on data.opm.gov (October 2024
– September 2026, published through 11/04/2026), which replace the quarterly FedScope cubes.
Unlike the classic Oct 2023–Mar 2025 files, DoD occupation, tenure, education and grade are not
redacted here; pay and geography are.

| | Sep 2024 | Mar 2025 | Sep 2025 | Oct 2025 | Mar 2026 | Sep 2026 |
|---|---:|---:|---:|---:|---:|---:|
| Economists (0110) | 4,998 | 4,888 | 4,517 | 4,081 | 3,831 | **3,802** |
| index, Sep 2024 = 100 | 100 | 97.8 | 90.4 | 81.7 | 76.7 | **76.1** |
| All federal employees (index) | 100 | 99.0 | 94.7 | 90.7 | 87.5 | **87.2** |

Economists fell about 11 index points *more* than the workforce as a whole (−24% vs. −13%),
bottoming at 3,785 in August 2026. The September 2025 → October 2025 step (−436) is the
deferred-resignation separations.

**Where the −1,196 came from:** deferred-resignation exits 532 (44%); other separations 831
less 251 hires, net −580 (49%); about −84 (7%) is unexplained — reclassification into or out
of series 0110 and late-reported actions — so flows and headcount reconcile within 7%.

**Deferred resignation (DRP).** Separations carry a `drp_indicator`. DRP economists left almost
entirely on September 30, 2025 (396) and December 31 (115); 62% are coded Quit, 26% voluntary
retirement and 12% early-out retirement. They skew senior (36% with 20+ years of service vs. 31% of
other exits) and away from the newest staff (11% under 2 years vs. 16%). Across all occupations
141,000 separations were DRP (6% of the September 2024 workforce), 95% of them effective
September–December 2025 (76% on September 30). DRP participants are reported to have stopped working about March 2025, so the *working*
workforce fell earlier and further than the payroll shows (§Bottom line). DRP exits are coded
Quit or Retirement, not "Other Separation", so the Q1 2025 "Other" surge (§who-leaves study) is
something else.

**Other exits.** Non-DRP separations by effective month ran at 1.4–2.3× the 2011–19 same-month
rate from February to July 2025 (peak 2.3× in April), 0.7–1.6× in August–December (1.6× in
September), and 0.4–1.0× in 2026 (0.37× in September 2026). By reason, non-DRP quits more than
doubled from 74 (Oct 2024–Mar 2025) to 170 (Apr–Sep 2025) and then fell to 86 and 63; RIFs were 41 in April–September 2025 and near zero
afterward.

**Hiring.** 106 economists were hired October 2024–September 2025 (88 of them by January) and 145
October 2025–September 2026, rising to 25–33 a month in June–September 2026. Net non-DRP flow
turned positive in June 2026.

**Composition.** The workforce got older and more tenured: mean length of service rose from 12.4
years (Sept 2024) to 14.2 (Sept 2026); the PhD share is unchanged (28.8%); real mean pay is flat
(about $150,000 in March 2025 dollars; nominal $158,209 in September 2026).

**Caveats.** Files are keyed by the month they were published and also hold late-reported actions, so
flows are dated by effective month; some actions for the latest months may not be in yet. OPM flags a
Department of War submission-processing issue for September 2026 (non-DoD data unaffected). Mean pay
excludes the ~1% of rows with redacted pay.

## Robustness

**Definition** (`fedscope_definition_sensitivity.csv`). The result holds under
alternatives:

| definition | Sep 2024 | Mar 2025 | headcount | pay |
|---|---:|---:|---:|---:|
| 0110 economist (headline) | 4,998 | 4,888 | −2.2% | +2.8% |
| 0110 + 0119 economics assistant | 5,333 | 5,219 | −2.1% | +2.8% |
| 0110 with a doctorate (Foster proxy) | — | 1,386 | — | mean $179,499 |

**Reconciliation with prior work.** Foster, Manzella, McEntarfer & Sandler
(2020, *AEA P&P*) and Foster et al. (2023, *JERP*) study federal economists in
OPM data but **restrict to PhD holders** (series 0110 *or* an economics field of
degree, then a PhD filter). Their federal-economist universe therefore
corresponds to roughly the 1,386 doctorate-holding 0110 economists here — about
28% of the full 0110 population. This also explains why they describe economists
as concentrated in "Treasury, Agriculture, Commerce, HHS and the independent
agencies" and do not feature BLS: BLS is this dataset's single largest employer
of 0110 economists (~1,160), but many are survey/data economists at GS-12/13
without a PhD. Both their work and this update share the OPM/FedScope universe
exclusions — the White House (CEA), the Federal Reserve Board, and legislative
agencies (CBO) — plus USPS and the intelligence agencies. Their ~30–33% female
share of federal economists (2018) is the last such figure available; 2025 data
cannot update it.

## Limitations

1. **Six months, not a year.** September 2024 → March 2025 is the cleanest
   single-source comparison available, not a 12-month one.
2. **March 2025 is preliminary** and subject to OPM revision.
3. **Headcount loss is understated.** Admin-leave / deferred-resignation staff
   are still counted as employed in March 2025.
4. **No gender or race.** FedScope's raw files never included them (only the
   interactive site did, until OPM removed it in March 2025).
5. **Universe break.** FedScope levels are not directly comparable to the
   FedsDataCenter FY2015–2024 series.
6. **~76% coverage on the agency/grade breakdown.** Agency × pay-plan × grade
   cells of ≤10 are suppressed on both dates (`fedscope_cell_coverage_2025.csv`);
   the suppressed tail is concentrated in small agencies and, within the shown
   cells, understates senior staff (record-level March 2025 shows 17.0% at
   GS-15 vs. 14.9% in the cells).
7. **No record-level September 2024.** Percentiles and person-level cross-tabs
   exist only for March 2025.
8. **Coverage gaps.** Some Department of Defense / Department of War components
   submitted late or incompletely in 2025 releases.
9. **Historical universe drift (§6).** FedScope agency coverage and occupational
   coding shift over 27 years. The visible ~11% step down from 2005 to 2006 is
   ~550 Department of State positions reclassified out of series 0110, not a
   workforce cut; smaller drifts elsewhere are not individually adjusted.
   Historical `SALARY` is nominal and CPI-deflated (not ECI).
10. **DoD economists are invisible in flows since Oct 2023.** In the Oct 2023 –
    Mar 2025 separation and accession files, occupation, tenure, education and grade
    are REDACTED for Army, Navy, Air Force and the defense agencies (~35% of all rows),
    so DoD economists (~4–5% of the series) cannot be identified. FY2024–25 economist
    flow counts therefore run ~4–5% low relative to earlier years — a conservative bias
    for the "2025 is extreme" comparison. The tenure analysis in
    `docs/who_leaves_study.md` excludes DoD in every period for the same reason.

## Refresh checklist

When OPM publishes newer FedScope data:

- [ ] **Finalised March 2025** replaces the preliminary snapshot — re-run
      `python main.py --fedscope --overwrite` after updating the URLs in
      `src/fetch_fedscope.py`.
- [ ] **September 2025 quarterly** — enables a true 12-month comparison; add
      `202509` as a third snapshot in `clean_fedscope.py` / `analyze_2025.py`
      (`SNAP0`, `SNAP1`, and a new `SNAP2`).
- [ ] **data.opm.gov monthly API** (blocked from the current environment) —
      would give record-level monthly snapshots and a continuous 2024–2026
      trajectory. If reachable, replace the FedScope-classic fetch.
- [ ] Extend `fetch_fedscope.py` accessions/separations to the next
      `AprYYYY-to-MarYYYY` release for updated flows.
- [ ] Add the next September employment cube to `EMPLOYMENT_HISTORY` in
      `src/fetch_fedscope_history.py` to extend the 1998– series, and the next
      FY separations file to `FLOW_HISTORY`.
- [ ] Re-pull CPI-U / ECI in `analyze_2025.py` and `analyze_history.py` for the
      new endpoint. (Watch quits, early-out retirements and term-appointment
      endings rather than the RIF code, which is near-zero for economists in
      every year.)
