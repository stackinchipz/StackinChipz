# 90-Day Execution Plan

*From internal approval to first signed term sheet. Assumes a small deal team: one commercial lead (owner), one Megapack applications engineer, one power-markets analyst, one in-house counsel, and a finance partner for the fee model. Dates are relative to the approval date (D0).*

## 1. Governance before any outreach (D0 to D10)

| Item | Owner | Done when |
|---|---|---|
| Program sponsor named on the Tesla Energy side and on the AI side | Executive sponsor | Both names on the charter. Tesla Energy leadership is in transition (the VP of Energy and Charging reportedly departed in mid-October 2026), so the sponsor must be whoever now owns Megapack commercially. |
| Megapack allocation carve-out for the program | Tesla Energy finance | Written allocation of ~2 GWh across 2027–28 that does not come out of signed customer backlog |
| Reference block spec frozen | Energy engineering | One-page datasheet: IT MW, MWh, gross MW, footprint, cooling, fiber, ramp limits |
| Fee model approved | Finance | Opening, target, walk-away per MW-year by ISO; approval thresholds |
| Contracting entity and ISO registrations confirmed | Legal, power markets | Entity chosen; ERCOT retail and controllable-load registrations mapped |
| Naming cleared | Legal | Decision on using "Megapod" externally given the existing third-party mark |
| Communications rules | Comms, IR | No public statements until the first signed term sheet; related-party firewall with SpaceX documented |

## 2. Target waves

**Wave 1 (D10 to D45) — energized, uncontracted ERCOT and SPP capacity, 2027 delivery.** Tier 1 targets from `04_target_list.md`. Objective: six first calls, four NDAs, two term sheets.

**Wave 2 (D30 to D75) — large 2027–28 blocks and battery-friendly hosts.** Tier 2 targets. Objective: six first calls, three NDAs, one term sheet.

**Wave 3 (D60 to D90) — neoclouds and powered-land developers with financing stress or undersubscribed campuses.** Tier 3 targets. Objective: four first calls, two NDAs. These are slower because the counterparties want to sell GPU hours, not space; lead with the battery-as-a-service variant.

## 3. Weekly cadence

- Monday: pipeline review, 30 minutes. Every target has a status (not started, contacted, NDA, data received, term sheet drafted, term sheet sent, negotiating, signed, dropped) and a next action with a date.
- Wednesday: engineering clinic. Site data received in the prior week is turned into a pad layout and a gross-MW reconciliation.
- Friday: finance and legal clinic. Term sheet drafts reviewed against the fee model and the deal-protection list in `08_term_sheet_outline.md`.

## 4. Milestones

| Day | Milestone |
|---|---|
| D10 | Governance complete; outreach begins |
| D20 | First six calls made; Email 1 sent to every Tier 1 target |
| D30 | First NDA signed; first block data received |
| D45 | First term sheet issued; Wave 2 outreach underway |
| D60 | Second term sheet issued; first site visit with Megapack engineering |
| D75 | First term sheet signed; project team formed for site schedule and interconnection review |
| D90 | Three term sheets signed or in final negotiation; Wave 3 underway; board or executive update with pipeline in gross MW and 2027 energization dates |

## 5. Tracker

Keep one row per target company in `contacts.csv` for people, and one row per site in a pipeline sheet with these columns:

```
company, site, iso, gross_mw_available, energization_date, interconnection_status,
status, owner, last_touch_date, next_action, next_action_date, fee_offer_$M_per_mw_yr,
fee_counter, nda_date, data_received_date, term_sheet_sent_date, term_sheet_signed_date, notes
```

## 6. Success metrics at D90

- Gross MW under signed term sheet: target 150 MW, stretch 300 MW.
- Gross MW under NDA with block data in hand: target 600 MW.
- Weighted average fee: at or below the target band in `03_economics_and_offer_design.md`.
- At least one term sheet with a Megapack priority-allocation option exercised.
- Zero outreach to an unverified email address; zero public leaks.

## 7. What kills the program, and the early warning for each

| Risk | Early warning | Response |
|---|---|---|
| No Megapack carve-out | Allocation request stalls past D10 | Escalate to the sponsor; without it, pitch the tenancy only and drop the kicker |
| Hosts anchor at full colocation rent | Two or more Tier 1 counters above $1.5M / MW-yr | Shift to hosts with no process running (Tier 1 names with zero contracted HPC) and to Variant B pricing |
| Interconnection classification changes in ERCOT | PUCT or ERCOT rulemaking on batch results in December 2026 | Prioritize firm, energized blocks and non-ERCOT sites in Wave 2 |
| Host credit event | Convert maturities, covenant news, stock down 20%+ on a print | Require step-in and non-disturbance before signing; do not prepay |
| Internal priority shift to Giga Texas only | Capex re-guidance without a hosting line | Present the 1 GW build-versus-host table at the D45 review and ask for a decision |
