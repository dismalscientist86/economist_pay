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

## Data and method

| | |
|---|---|
| Source | OPM FedScope "classic" raw datasets (`data/raw/fedscope/SOURCES.md`) |
| Snapshots | September 2024 and **preliminary** March 2025, bundled in one OPM release |
| Population | Occupational series **0110 (Economist)**, executive branch, active pay status |
| Pipeline | `python main.py --fedscope` → `src/analyze_2025.py` → `output/tables/fedscope_*` |
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
- [ ] Re-pull the CPI-U and ECI values in `analyze_2025.py` for the new endpoint.
