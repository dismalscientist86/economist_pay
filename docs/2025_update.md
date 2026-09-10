# Federal government economists, 2024 → 2025: has the number and pay changed?

*Draft findings memo — 2026-09-09. Preliminary data; see limitations.*

## Bottom line

Between **September 2024 and March 2025**, the number of economists in the
federal government fell **about 2%** (4,998 → 4,888, series 0110) and mean pay
rose **2.8% in nominal terms** — roughly **1.4% in real terms** after inflation.
Almost the entire pay increase is the January 2025 federal pay raise, not a
shift toward more senior staff.

The 2% headcount drop **understates** what is happening. OPM's March 2025
snapshot still counts employees on administrative leave pending
resignation/retirement as employed. The **flow data** — actual hires and
departures — shows the turn clearly: in the first quarter of 2025, economist
hiring collapsed while departures roughly doubled, for a net loss of ~100
economists in three months. The people leaving were experienced mid-career
staff (mean 12.8 years of federal service), and the reason mix — a surge in
early-out retirements, term-appointment terminations, voluntary retirements and
quits, with agency-to-agency transfers falling — is the signature of a
reduction-in-force and buyout, not ordinary turnover.

In historical perspective (§6): the March 2025 headcount is still near the top
of the post-2006 range — the drop so far has unwound about a year of growth, not
decades. But the *outflow* is extreme. FY2025's first six months already saw 215
economist separations (78% of all of FY2024), and January–March 2025 had the
most departures and nearly the fewest hires of any first quarter since 2015 —
worse than the FY2019 ERS relocation on a rate basis and worse than the 2017
transition on Q1 departures. No separations yet carry a formal RIF code.

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
EHRI month-end status snapshot rather than an annual FOIA extract) and, since
March 2025, **carries no gender or race fields** (removed under EOs 14151 /
14168 / 14173). The gender analysis in this repo therefore ends at FY2024; this
update is headcount and pay only.

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

For context, the FedsDataCenter series (different universe) ran 4,266 in FY2015
up to 4,718 in FY2024 — a decade of slow growth. FedScope's September 2024
count of 4,998 and mean pay of $146,952 line up closely with FedsDataCenter's
FY2024 ($146,848), which makes the March 2025 comparison credible even across
the source change.

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

- **Leavers**: mean **12.8 years** of federal service, mean pay **$144,938** —
  established mid-career economists, consistent with the deferred-resignation
  program rather than ordinary probationary attrition.
- **Joiners**: mean **1.9 years** of service, mean pay **$114,890** — junior.

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
level (4,883). It is **not yet** a historic low. (Pre-2006 counts of
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
310–460 economist separations (rate 6–11% of headcount). FY2024 was the calmest
year in the series — 277 separations, a 5.7% rate. Then **FY2025 recorded 215
separations in just its first six months** (Oct 2024–Mar 2025) — already 78% of
FY2024's full-year total, and the reason mix shifted toward retirements (76 in
six months vs. 65 in all of FY2024) and term-appointment terminations (20 vs. 9).

The one clear historical precedent for elevated economist attrition is
**FY2019** (461 separations, 10.6% rate), driven by the USDA decision to
relocate the Economic Research Service to Kansas City — an exodus concentrated
in transfers and quits at one agency. FY2025 differs in being government-wide
and retirement/termination-heavy.

**First-quarter comparison.** January–March is normally a modest-outflow
quarter. Jan–Mar 2025 had **134 separations and 34 accessions** — the most
departures and nearly the fewest hires of any Q1 in 2015–2025. The previous
worst Q1 for separations was 2017 (122, the first Trump transition); 2025 is
worse and, unlike 2017, pairs it with a hiring freeze.

**No formal RIF yet.** Across every file, FY2015 through March 2025, **zero**
economist separations carry OPM's Reduction-in-Force code. The 2025 drawdown is
running through quits, retirements (including early-outs) and term-appointment
endings — consistent with the deferred-resignation program rather than
statutory RIF, at least through March 2025.

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
4. **No gender or race.** Removed from FedScope as of March 2025.
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
      new endpoint — a formal RIF code (SEP `SH`) in a future file is the number
      to watch.
