# Indicative Term Sheet Outline — Tesla Megapod Site Agreement

*Non-binding structure for a Tesla-as-offtaker Megapod deployment at a partner (Bitcoin miner or neocloud) site. Two variants are offered; counsel to convert into a Master Site Agreement (MSA) with site-specific schedules.*

## Parties and roles

| Role | Party | Obligations |
|---|---|---|
| **Site Partner** ("Host") | Miner / neocloud entity holding the interconnection agreement, land, and (where applicable) shells | Deliver energized capacity (MW at the point of interconnection), land/pad, fiber route, water (if any), security, 24/7 site operations |
| **Offtaker / Tenant** | Tesla, Inc. (or a Tesla Energy subsidiary) | Fund, deliver, install, and operate Megapods (Megapack 3 / Megablock storage + containerized compute); pay site fees; consume power |
| **Power counterparty** | Host's utility / retail electric provider / ERCOT QSE | Deliver energy under Host's existing supply arrangements, or assigned to Tesla under a back-to-back supply agreement |

## Variant A — "Powered Land Lease" (preferred for miners)

1. **Premises**: defined pad(s) sized for *N* Megapods, plus easements for switchgear, fiber, and access. Triple-net ground lease.
2. **Delivered capacity**: Host guarantees *X* MW of firm interconnection capacity available to the Premises by the Capacity Delivery Date, with liquidated damages for late delivery (fee abatement 1:1 plus a daily LD after a 60-day grace period).
3. **Term**: 10 years initial + two 5-year Tesla extension options. Tesla early-termination right after year 5 with 18 months' notice and a termination fee stepping down from 24 to 6 months of site fees.
4. **Site fee**: fixed $/MW-month on *reserved* capacity (not consumed energy), with CPI-linked escalator capped at 3%/yr. Indicative range to be set against colocation comps in `02_strategy_and_economics.md` (Tesla self-funds the Megapods, so the fee should sit well below turnkey colocation rents).
5. **Power pass-through**: energy at Host's actual cost plus a transparent, capped adder (or Tesla takes assignment of the supply contract). Tesla keeps 100% of battery-derived grid revenue (ancillary services, 4CP avoidance, demand response) unless the Host co-invests.
6. **Flexibility covenant**: Tesla commits to curtail compute load within ERCOT/utility notice windows, using Megapack discharge first, so the Host keeps any interruptible-load tariff benefits.
7. **Expansion**: Tesla ROFR on the next *Y* MW the Host energizes at the site and at named sister sites; Host ROFO to host Tesla's next regional deployment.
8. **Credit support**: Tesla parent guarantee (investment-grade). Host provides a security interest in site improvements paid for by Tesla and a non-disturbance agreement from Host's lenders.
9. **Operations**: Host provides physical security, grounds, and first-response; Tesla operates Megapods remotely with on-call Tesla Energy field service. Shared SLA with uptime credits on delivered capacity.
10. **Exit**: Megapods are removable trade fixtures; Tesla may remove or sell to Host at fair value at expiry. Host has purchase option on the Megapack units at depreciated book value.

## Variant B — "Hosted Compute Services" (preferred for neoclouds)

1. **Service**: Host operates Tesla-owned Megapods inside its campus and sells Tesla power, cooling (where used), network, and remote-hands as a managed colocation service.
2. **Pricing**: $/kW-month on installed IT capacity plus metered power at cost; Tesla self-provides compute hardware, so the rate card excludes GPU margin.
3. **Term**: 5–7 years, matched to Host's power contract term; renewal at then-market.
4. **Performance**: tiered SLA (99.9% on power delivered to Megapod bus; 99.99% where Megapack ride-through is in the loop) with service credits.
5. **Compute interoperability**: Tesla racks may be Tesla-designed (AI5/AI6) or merchant GPU; Host network must support Tesla's interconnect spec.
6. **Battery services option**: Host may lease Megapack capacity from Tesla for its own ride-through or grid-revenue purposes at a fixed $/MW-month, netting against site fees.
7. **Credit and exit**: as Variant A, with step-in rights for Tesla if Host becomes insolvent (direct agreement with Host's utility and landlord).

## Common schedules

- Schedule 1: Site description, interconnection agreement summary, capacity delivery milestones
- Schedule 2: Megapod specification (unit count, MWh storage, MW compute, footprint, cooling, fiber)
- Schedule 3: Fee schedule and escalators
- Schedule 4: SLA and curtailment protocol (ERCOT/utility notice windows, Megapack discharge priority)
- Schedule 5: Insurance, environmental, decommissioning
- Schedule 6: Transition / step-in plan

## Deal-protection points Tesla should hold firm on

- Reserved-capacity pricing (never tied to Tesla's compute revenue).
- Tesla owns all battery grid revenue by default.
- Capacity delivery LDs backed by escrow or a parent guarantee from the Host.
- No exclusivity granted to the Host beyond the specific site(s).
- Most-favored-nation on site fees versus any other tenant on the same campus.
