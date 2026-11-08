# Strategy: Tesla as Offtaker at Miner and Neocloud Sites

*The case for the program, the design of the offer, how the market is segmented, the sequence of approach, and the risks. Written for Tesla executives who will be asked to sponsor it. Companion documents cover the economics (`03`), the target list and contacts (`04`, `contacts.csv`), scripts and emails (`05`, `06`), objections (`07`), the term sheet (`08`), and the 90-day plan (`09`). Facts are current to November 8, 2026 and sourced in `10_sources.md`.*

---

## 1. The thesis in one paragraph

Tesla needs a lot more training and inference compute and needs it before the end of 2027, but every new gigawatt of grid-connected load in the United States now waits three to seven years for interconnection. Bitcoin miners and a handful of power-first developers already hold more than 20 GW of energized or interconnection-approved capacity, and the mining business that justified it has collapsed to near breakeven. Hyperscalers and AI labs have spent eighteen months buying that capacity on fifteen- to twenty-year leases. Tesla has three advantages none of them has: it makes the battery every one of these sites needs to firm a curtailable interconnection, that battery is sold out for 2027, and it can show up with a self-contained compute-plus-storage module that removes the $10–12M-per-megawatt shell build from the deal. The program puts Tesla in as the tenant and offtaker at third-party sites, paying a fixed fee per reserved megawatt, bringing Megapods, and using Megapack allocation as the currency that closes.

## 2. Why now

**Tesla's demand is public and immediate.** Tesla told shareholders in October 2026 that it runs more than 225 MW of training compute at Giga Texas (Cortex 1 above 105 MW, Cortex 2 above 120 MW) and will reach 400 MW by year-end. 2026 capex is guided at roughly $20B and is explicitly weighted to "superintelligence compute infrastructure." The CEO's 2025 performance award vests on one million robotaxis in commercial operation, one million Optimus units delivered, and ten million paid FSD subscriptions, all of which are training-compute problems first. AI5 reaches volume in 2027 and Tesla has said spare AI5 silicon goes into Tesla data centers.

**Tesla already defined the product.** Tesla filed the MEGAPOD trademark in June 2026 for modular AI data center hardware in a Megapack-style enclosure. On the Q2 2026 call the CEO described Megapods as a way to "scale AI computing alongside aggregated power production" and talked about siting them at Superchargers. The Q3 2026 shareholder update says Megapack "excels in off-grid and on-grid applications, supplying large data center loads, buffering oscillating demand, helping interconnection grid-compliance." This program is the external version of that idea: Megapods where the power already is.

**The grid is the constraint, and miners own the exits.** ERCOT's large-load queue reached 474 GW in July 2026, about 90% of it data centers; PJM's large-load pipeline is in the hundreds of gigawatts; US average time-to-power for a new 100 MW+ load is around four years and seven in Northern Virginia; large transformers run 30–48 months. Modo Energy estimates only 7% of requested large load in ERCOT is deliverable by 2030. Meanwhile miners hold executed interconnection agreements and energized substations: Cipher alone has 807 MW energized and 3.2 GW with ERCOT conditional classifications; IREN energized 1.4 GW at Sweetwater in May 2026; Hut 8 has a 1 GW interconnection at Beacon Point; Core Scientific is expanding Pecos and Muskogee toward 1.5 GW gross each.

**Mining economics have broken.** Bitcoin at about $76,000, hashprice at $33 per PH per day (a five-year low), difficulty at a record, and a public-miner cash cost near $80,000 per coin mean roughly one in five legacy miners is losing money on every block. A megawatt that earns $0.2M a year mining earns $1.2–2.4M a year as HPC. Every miner CEO has said so on their last earnings call, and several (IREN, Keel, Cipher at Black Pearl) are shutting mining entirely.

**The buyers are stretched and the sellers are nervous.** Neoclouds have deployed only 25–30% of roughly $375B of contracted capacity. CoreWeave carries $51.6B of debt with bonds yielding above 16%; Microsoft said on Nov 6, 2026 that it will use fewer neoclouds. Nscale lost three Microsoft commitments this year. Crusoe paused and then sold a 1.8 GW Wyoming campus for lack of a tenant. Fermi America has 1.5 GW of turbines on the ground, one unclosed tenant, and lender deadlines in November and December. Keel Infrastructure (formerly Bitfarms) has 2.2 GW in development and zero signed leases. Texas elected a governor in November 2026 who campaigned on a data-center moratorium, which will make hosts with already-energized capacity more valuable and hosts with paper interconnections more motivated. An investment-grade tenant that funds its own build is the most valuable counterparty in this market, and today that role is played by Oracle, Microsoft, Anthropic, and Google. Tesla can be the fifth.

## 3. What Tesla is offering

**The product.** A Megapod block: roughly 20 MW of IT load in Tesla compute enclosures, paired with one or two Megablocks (20–40 MWh of Megapack 3 storage with integrated transformer and switchgear), on about an acre. Gross draw at the host's switchgear is about 26 MW. Five blocks make a 100 MW site. The battery does three jobs the host cares about: it smooths training-load swings so the utility never sees them, it rides through curtailment calls so the host's interconnection classification is protected, and it lets the site operate as a controllable load under Texas SB6 and ERCOT's batch rules. *Block spec is a program assumption for Tesla Energy engineering to confirm.*

**The deal.** Tesla is the tenant. The host keeps the land, the interconnection, the utility relationship, and site operations, and delivers energized gross megawatts at the point of interconnection. Tesla funds and owns everything from the switchgear in and pays a fixed site fee on reserved megawatts from the day power is available, with power passed through at cost. Ten-year initial term, two five-year Tesla options, Tesla parent guarantee. Equipment is a removable trade fixture.

**The price.** Opening at about $0.75M per gross MW-year, closing between $0.9M and $1.05M, walking away above $1.25M. That is three to five times the host's current mining margin on the same megawatt, with no shell to build. It is below the $1.8–1.9M market median for turnkey colocation because the host's capital is $1.5–3M per MW instead of $10–14M. The derivation is in `03_economics_and_offer_design.md`.

**The kicker.** Tesla is the only tenant that also makes the asset the host needs. Four forms, used singly or in combination: a priority Megapack allocation for the host's own firming needs; battery-as-a-service where Tesla owns Megapacks the host leases; warrants, as Google took at Cipher and TeraWulf, AMD at Core Scientific, and Nvidia at IREN and Nebius; and a Tesla guarantee the host can finance against, as Hut 8 financed River Bend and Beacon Point with $7.5B of investment-grade project bonds.

**Two variants.** Variant A, the powered-land lease, for miners and landlords. Variant B, hosted Megapod services, for neoclouds that want to operate the site and sell Tesla power, network, and remote hands on a managed rate card. Both are in `08_term_sheet_outline.md`.

## 4. Market segmentation

| Segment | Who | What they have | What they want | Lead with |
|---|---|---|---|---|
| **A. Miners with energized, uncontracted ERCOT/SPP capacity** | Riot (Rockdale ~500 MW still mining), Cipher (Odessa 207 MW; 270 MW in 2027), Core Scientific (~385 MW leasable), Hut 8 (Vega 205 MW, two West Texas sites up to 230 MW), Galaxy (Helios 830 MW "available to be contracted"), Bitdeer (Rockdale, "too big for us") | Power now, substations built, mining margin near zero | Rent in 2027 without a construction loan; tenant diversification | Variant A, speed, Tesla credit |
| **B. Miners with large 2027–28 blocks and firming problems** | IREN (Sweetwater 1.4 GW energized, 600 MW phase 2, conditional Base Load), Cipher (1.4 GW Partial Capacity Load; Colchis 1 GW), TeraWulf (Muskie 1 GW KY; Lake Hawkeye 400 MW with 800 MWh BESS planned), Hut 8 (Beacon Point battery design; 1.3 GW at exclusivity), Keel (Panther Creek 350–500 MW PJM, zero leases) | Interconnections that are curtailable, conditional, or late | A firm classification, a first lease, bankable paper | Megapack allocation first, tenancy second |
| **C. Power-first developers with stranded or tenant-less capacity** | Fermi America (6 GW permitted, 1.5 GW turbines, covenant deadlines), Lancium (Hall County, Fort Stockton), Prometheus Hyperscale (2.5 GW WY, tenant-less), Poolside Project Horizon (2 GW Fort Stockton, anchor lost), New Era/TCDC (1 GW Ector County), Soluna (wind-colocated TX) | Permits, land, generation, no tenant | Any creditworthy anchor; survival in some cases | Variant A with a Tesla backstop; move fast while deadlines bite |
| **D. Neoclouds that cannot fill or finance what they contracted** | Nebius (5 GW contracted vs <1 GW connected; explicitly wants partners to finance, build, operate), Nscale (Ward County TX ~1 GW potential untenanted after Microsoft declined), Crusoe (two unnamed Texas campuses and Missouri), Fluidstack (Cameron County 1.5 GW greenfield), CoreWeave (2.7 GW contracted-not-active; landlord stress) | Contracted power and GPU demand, thin balance sheets | Revenue conversion without new debt | Variant B; battery-as-a-service; Tesla as anchor for a building they operate |
| **E. Vendor-only relationships** | Everyone in A–D on their remaining capacity; Meta/Enbridge-style utility projects | Firming needs | Megapack supply | Standard Tesla Energy sales motion, separate from this program |

## 5. Why Tesla wins where others would not

1. **Tesla brings the data hall.** No other tenant removes the shell from the host's balance sheet. That is why Tesla can pay less, start sooner, and still be the host's best offer.
2. **Tesla controls the scarce firming asset.** Megapack allocation is a concession only Tesla can make. For a host with a Partial Capacity Load classification, it is worth more than the rent.
3. **Tesla is investment grade and pays from operating cash flow.** Hosts' lenders have already financed billions against Anthropic, AWS, and Google-backstopped Fluidstack leases. Tesla paper finances the same way.
4. **Tesla is not a competitor to the host's other tenants.** Tesla will not resell compute from these sites. Hosts can keep running hyperscaler processes on the rest of the campus.
5. **Tesla has done this at scale as a vendor.** Roughly $1B of Megapacks are already firming AI training loads at Colossus in Memphis, bought by SpaceX. The engineering is proven; the program changes who owns the compute.

## 6. Sequencing

**Wave 1 (first 45 days): Segment A, Texas and Oklahoma.** Six first calls: Riot, Cipher, Core Scientific, Hut 8, Galaxy, Bitdeer. Objective: two term sheets on energized capacity with 2027 delivery. These are the fastest closes because the power exists and the miners' commercial leads (several hired in 2025–26 from CyrusOne, Prime Data Centers, Digital Realty) are measured on signings.

**Wave 2 (days 30–75): Segment B and C, plus MARA and CleanSpark.** Lead with the Megapack allocation at IREN, TeraWulf, Keel, and Fermi; the tenancy follows. Fermi's lender and landlord deadlines in November and December 2026 make it a special case: a 200–400 MW Tesla letter of intent could cure its covenants, which gives Tesla extraordinary leverage on terms and warrants, but also means doing diligence on a counterparty with going-concern language.

**Wave 3 (days 60–90): Segment D.** Nebius and Nscale first, because both have said publicly they want partners who finance, build, and operate. Crusoe second, noting that its board now includes the CEO of a competing storage supplier. CoreWeave last, because its stress is real but its leases are with the same landlords Tesla is already calling.

**What not to do.** Do not approach SpaceX or xAI capacity; the program must be arm's length from related parties after the November 2025 shareholder vote. Do not announce anything until the first term sheet is signed. Do not let Megapack sales to hosts' other capacity be gated on the tenancy; run them as separate orders through the standard Energy channel.

## 7. Governance inside Tesla

The program sits at the seam between Tesla Energy (Megapack, Megablock, site engineering, ERCOT registrations through Tesla Energy Ventures) and Tesla AI (compute roadmap, cluster operations). It needs one executive sponsor on each side, a Megapack allocation carve-out of roughly 2 GWh over 2027–28 that does not come out of signed customer backlog, a frozen reference-block datasheet, and a fee model with approval thresholds, all before the first call. Tesla Energy's leadership changed in October 2026, so the first internal step is confirming who owns Megapack commercially today. Details are in `09_90_day_plan.md`.

## 8. Risks and mitigations

| Risk | Why it is real | Mitigation |
|---|---|---|
| Megapack supply diversion | Megapack is "almost sold out" for 2027 with a record backlog | Fixed carve-out approved up front; program sized to under 2% of planned nameplate once Megafactory Texas ramps |
| Host credit | Hashprice at five-year lows; converts due 2030–32 at several hosts; Hut 8 and Cipher stocks fell 20%+ on their Q3 prints; Fermi has going-concern language | Fee on reserved MW, Tesla owns all assets from the switchgear in, step-in rights with the utility, lender non-disturbance, no prepayments |
| Texas policy | SB6 curtailment authority; PUCT batch process; a governor-elect who campaigned on a data-center moratorium | Battery-backed controllable load in every block; prioritize already-energized sites; spread Wave 2 across SPP, MISO, PJM, NYISO |
| Interconnection reclassification | ERCOT Batch Zero audit in December 2026 may change conditional designations | Contract delivery LDs against classification outcomes; Megapack allocation is the hedge the host wants anyway |
| Related-party optics | SpaceX and xAI are the most visible Megapack data-center buyers | Program is Tesla-only; no SpaceX or xAI sites; disclosure reviewed by legal and IR |
| Naming | A cooling vendor already sells a "MegaPod" | Site agreements describe equipment generically; legal clears external naming |
| Internal priority | Capex was cut from $25B to $20B in October 2026 | Present the 1 GW build-versus-host comparison at the first executive review and ask for a decision, not a study |
| Fiber and operations at remote sites | Training clusters need high-bandwidth backhaul; West Texas and Oklahoma sites vary | Dark-fiber availability is a Tier 1 screening criterion; host provides security and first response under the SLA |

## 9. What success looks like

By the end of 2027: 400–600 MW of Megapod capacity energized at four to six third-party sites across at least three ISOs, at a weighted site fee at or below $1.05M per gross MW-year, with at least 1 GWh of Megapack deployed on Tesla's own account and a further pipeline of host-side Megapack orders attributable to the program. By the end of 2028: 1 GW, with the reference block productized for Supercharger and utility-partner sites.
