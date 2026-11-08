# Economics and Offer Design

*How to price a Tesla-as-offtaker Megapod deployment so that it clears for the host, beats Tesla's build-it-yourself alternative, and leaves room for a Megapack kicker. All figures are as of early November 2026. Deal values are public; per-MW math is ours (total contract value ÷ term ÷ MW). Items marked UNVERIFIED rest on a single secondary source and should be confirmed before they go into a term sheet.*

---

## 1. What the market already pays for powered capacity

Bitcoin miners have signed roughly $130B of AI colocation leases since mid-2024. Every one of them follows the same shape: a long-dated, triple-net lease on critical IT megawatts, with the landlord funding the shell and the tenant owning the compute. The implied rent is remarkably tight.

| Deal | Date | Critical IT MW | Base contract value | Term (yrs) | Implied rent ($M / MW-yr) | Landlord capex | Credit support |
|---|---|---|---|---|---|---|---|
| Cipher – AWS (Black Pearl, TX) | Nov 2025 | 300 | $5.5B | 15 | **1.22** | Landlord | AWS, investment grade |
| Riot – AMD (Rockdale, TX) | Jan 2026 | 25 → 50 | $311M | 10 | **1.24** | Landlord, $3.6M/MW retrofit | AMD corporate |
| Core Scientific – CoreWeave (6 sites) | 2024–25 | ~590 | ~$10.2B | 12 | **1.44** | Tenant fit-out ≤ $1.5M/MW credited; landlord shell | CoreWeave corporate |
| Core Scientific – AMD + neocloud | Jul 2026 | 529 | > $14B | 15 | **1.76** | Landlord | AMD credit support; 30M warrants |
| Cipher – Fluidstack (Barber Lake, TX) | Sep–Nov 2025 | 224 | ~$3.8B | 10 | **1.71** | Landlord | Google backstop $1.73B; 5.4% warrants |
| Applied Digital – CoreWeave (ND) | Jun–Sep 2025 | 400 | ~$11B | 15 | **1.83** | Landlord, $10–13M/MW | CoreWeave; annual escalator |
| TeraWulf – Fluidstack (Lake Mariner, NY) | Aug 2025 | 360 | ~$6.7B | 10 | **1.86** | Landlord | Google backstop $3.2B; ~14% warrants |
| Hut 8 – IG tenant (Beacon Point, TX) | May 2026 | 352 | $9.8B | 15 | **1.86** | Landlord, $4.25B IG bonds | NNN take-or-pay; 3% escalator; no termination for convenience |
| Hut 8 – Fluidstack / Anthropic (River Bend, LA) | Dec 2025 | 245 | $7.0B | 15 | **1.90** | Landlord, $3.25B IG notes | Google backstop |
| Riot – Corsicana powered-land lease (TX) | 2026 | 910 | ~$28B | 15 | **2.05** | Riot ~$2M/MW site electrical; tenant owns compute modules | Frontier AI lab; rent on full MW regardless of utilization |
| Galaxy – CoreWeave (Helios, TX) | 2025 | 526 | > $1.2B / yr | 15 | **2.28** | Landlord, $1.4B project debt | CoreWeave (pass-through treatment UNVERIFIED) |
| TeraWulf – Anthropic (Hawesville, KY) | Jul 2026 | 401 | ~$19B | 20 | **2.37** | Landlord | Anthropic direct; Google credit support |
| Riot – frontier AI lab (Rockdale, TX) | Aug 2026 | 191 | $9.1B | 20 | **2.38** | Landlord | IG backstop financing pending |

**Read-across.** Hyperscaler credit clears at $1.2–1.45M per MW-year. The market median for a full turnkey shell is $1.8–1.9M. Long-dated leases to AI labs clear at $2.2–2.4M. In colocation terms that is roughly $100–200 per kW-month, which is below CBRE's 2026 retail colocation range of $190–235 in Northern Virginia, because these are wholesale, single-tenant, remote sites.

The Riot Corsicana deal is the closest template to what Tesla would sign: the tenant brings its own compute modules, the landlord provides land and site electrical, and rent is owed on the full reserved capacity.

Critical IT megawatts are not gross megawatts. Miners quote mining capacity gross and HPC capacity as critical IT; the conversion is roughly 1.33 gross MW per IT MW for liquid-cooled builds. Tesla should contract on gross MW at the point of interconnection and let the Megapod's PUE be Tesla's problem.

## 2. What the same megawatt earns a miner today

| Line (100 MW gross) | Basis | Annual value |
|---|---|---|
| Bitcoin mining revenue | Hashprice $32.86 / PH / day (Nov 2, 2026), 18 J/TH fleet | ~$67M |
| Less power at $50 / MWh | 8,760 h | – $44M |
| **Mining gross margin before opex and depreciation** | | **~$23M** (≈ $0.23M / MW-yr; a 25 J/TH fleet is near breakeven) |
| ASIC hosting revenue (Hut 8 Vega comp) | $0.56M / gross MW incl. power pass-through | ~$56M |
| HPC colocation rent, hyperscaler credit | $1.22–1.44M / IT MW | $122–144M NNN |
| HPC colocation rent, market median | ~$1.85M / IT MW | ~$185M NNN |

Bitcoin traded near $76,000 on Nov 6, 2026, down about $25,000 year over year. Network hashrate is above 1,000 EH/s and difficulty hit a record 148.4T on Oct 29. CoinShares put the weighted average cash cost of public miners near $80,000 per BTC in late 2025, and estimated about one in five legacy miners is mining at a loss at today's five-year-low hashprice. That is the backdrop for every conversation: the same megawatt is worth five to twenty times more as HPC than as mining, and the miners know it.

Powered land itself has a price. MARA paid up to $600M for a 1,200-acre, 2 GW Texas site (≤ $300k per MW of future capacity). Core Scientific paid $421–444M for the 440 MW operating Muskogee site (~$957k per energized MW). CoinShares puts mining infrastructure at $0.7–1.0M per MW. An energized, interconnected megawatt is worth roughly $1M before anyone builds a data hall on it.

## 3. The capex stack and where Megapod changes it

| Layer | Conventional AI colocation | Megapod at a host site | Who pays (Megapod) |
|---|---|---|---|
| Land, interconnection, substation, high-voltage | $0.7–1.0M / MW (already sunk at miner sites) | Same, already sunk | Host |
| Medium-voltage switchgear, pads, fiber, security | ~$1.5–2M / MW | ~$1.5–2M / MW (Megablock integrates transformer and switchgear) | Host, or Tesla with rent credit |
| Shell, power distribution, cooling, UPS, generators | $8–12M / MW new build (Core Scientific CEO: $11.5–12M, May 2026); $3.6M / MW light retrofit (Riot–AMD) | **Replaced by Megapod enclosure plus Megapack ride-through** | Tesla |
| Compute (GB300 NVL72 class at 132–140 kW/rack, $4.3–5M/rack) | $30–40M / MW | $30–40M / MW merchant, or lower with Tesla AI5/AI6 | Tesla |
| Battery firming, 2-hour | Optional | 200 MWh per 100 MW IT; ~$260/kWh equipment (UNVERIFIED), $375–460/kWh installed third-party; Tesla internal cost lower | Tesla |

Three consequences follow.

1. **The host's capex falls from $10–14M per MW to $1.5–3M per MW.** That is why Tesla can and should pay less than $1.8M per MW-year. The host is renting power and dirt, not a data hall.
2. **Time-to-compute falls from 18–30 months to roughly 4–9 months** after a site is energized, because the long-lead items (shell, switchgear, transformers at 30–48 month lead times) are either sunk at the site or integrated into Megablock. Tesla has publicly claimed 1 GWh of Megablock can be deployed in 20 business days.
3. **Tesla owns ~80% of total capital at the site** (compute plus battery) and all of the residual value. Megapods are trade fixtures and move if the site underperforms.

## 4. Pricing the site fee

Set the fee with a formula the host's CFO can audit, not a number pulled from a comp.

**Site fee per gross MW-year = (Host capex per MW × target yield) + powered-land premium**

- Host capex of $1.5–3M per MW at a 30–35% unlevered yield (the yield Riot earns on its ~$2M/MW Corsicana contribution against ~$2.05M rent is higher, but that lease also carries a $4M/MW tenant reimbursement and a 15-year term) = $0.45–1.05M.
- Powered-land premium for firm, energized ERCOT capacity: $0.3–0.5M per MW-year, which values the interconnection at roughly $1M per MW on a 3-year payback, consistent with the Muskogee and MARA transactions.

| Position | $M per gross MW-year | 100 MW annual | Rationale |
|---|---|---|---|
| **Opening offer** | 0.75 | $75M | 3x the host's current mining margin; Tesla funds everything beyond the point of interconnection |
| **Target close** | 0.90–1.05 | $90–105M | Host funds switchgear and pads; CPI escalator capped at 3% |
| **Walk-away** | 1.25 | $125M | Above this, Cipher–AWS pricing for a full turnkey shell is cheaper per MW |

For a neocloud hosting variant where the host also supplies cooling water loops, network, and remote hands, add $15–35 per kW-month on installed IT load, which is the labor and operations component of a managed colocation rate card.

Power is passed through at cost. Tesla keeps battery grid revenue by default; in ERCOT this is small (Modo Energy benchmarks merchant battery revenue at about $24 per kW-year in 2026, down from $193 in 2023), so it is not worth fighting over, but it is worth owning for curtailment ride-through.

## 5. Tesla's build-versus-host comparison, 1 GW over 10 years

| | Tesla builds a new greenfield campus | Tesla hosts Megapods at miner / neocloud sites |
|---|---|---|
| Time to first 100 MW of compute | 36–60 months (interconnection 4+ years US average; 7 in Northern Virginia; ERCOT queue 474 GW, ~90% data centers) | 6–12 months on energized sites |
| Shell and site capex | $10–14B | ~$0 to Tesla; host funds $1.5–3B |
| Site fee over 10 years | $0 (owned) | $9–10.5B at $0.9–1.05M / MW-yr |
| Megapack pull-through | Internal, 2 GWh | Internal, 2 GWh, plus host-side Megapack sales for firming the host's remaining capacity |
| Flexibility | Low: fixed asset, single site | High: modular, removable, many ISOs |
| Exposure to one grid | Concentrated (Giga Texas / ERCOT) | Diversified across ERCOT, SPP, MISO, PJM, NYISO |
| Net 10-year cash difference | Baseline | Roughly neutral on cash, 3+ years faster, no stranded-shell risk |

The decision is not about saving money. It is about buying three years and keeping optionality while Tesla's own chip roadmap (AI5 in 2027, AI6 and Terafab after) matures. Tesla's 2026 capex is guided at about $20B and is explicitly weighted toward "superintelligence compute infrastructure," with the company targeting 400 MW of training compute by year-end 2026 from more than 225 MW at Q3. Hosting is the fastest way to add the next 400 MW without waiting on a second Giga Texas switchyard.

## 6. The Megapack kicker

Tesla is the only prospective tenant that also makes the firming asset the host needs. Megapack is reported as "almost sold out for 2027" with a record order backlog. That scarcity is a currency.

| Kicker | Mechanism | Who it suits |
|---|---|---|
| **Priority allocation** | Guaranteed 2027–28 Megapack delivery slots for the host's own firming needs, at list, in exchange for a site-fee discount or an expansion ROFR | Hosts with curtailable or "Partial Capacity Load" interconnections in ERCOT (Cipher's 1.4 GW; IREN Sweetwater's conditional Base Load status; Hut 8 Beacon Point's battery design) |
| **Battery-as-a-service** | Tesla owns the Megapacks, host leases ride-through capacity at a fixed $/MW-month, netted against site fees | Neoclouds and miners with weak balance sheets (high leverage, converts due 2030–32) |
| **Warrants** | Tesla takes penny warrants or discounted equity for anchoring a site, as Google did at Cipher (~5.4%) and TeraWulf (~14%), AMD at Core Scientific (30M shares), and Nvidia at IREN and Nebius | Small-cap hosts where a Tesla anchor re-rates the equity |
| **Backstop** | Tesla parent guarantee of site fees that the host can finance against (the River Bend and Beacon Point leases were financed with $3.25B and $4.25B of investment-grade project bonds) | Every host; this is what gets the host's lenders to say yes |

## 7. Why a host says yes

1. **Money.** $0.75–1.05M per MW-year is three to five times current mining margin on the same megawatt, with no shell to build and no construction loan to raise.
2. **Speed.** Revenue starts months, not years, after signing, because Tesla brings the data hall with it.
3. **Credit.** Tesla is investment grade and pays from operating cash flow. Hosts' lenders finance against this.
4. **Firming.** Megapack allocation turns curtailable megawatts into firm ones and keeps the host's remaining capacity marketable under Texas SB6 and ERCOT's batch process.
5. **Diversification.** Core Scientific (CoreWeave), Riot (one AI lab), Hut 8 (two tenants), and IREN (Microsoft at 47% of backlog) all carry tenant-concentration flags from analysts.
6. **Optionality.** Ten-year terms with removable equipment leave the host free to sign a 20-year hyperscaler lease on the rest of the campus.

## 8. Why Tesla says yes

1. 400 MW+ of incremental training and inference capacity in 2027 without a second multi-year interconnection.
2. Zero shell capex and no stranded real estate if the chip roadmap moves the compute elsewhere.
3. Two GWh of internal Megapack demand per gigawatt of compute, plus a sales channel into hosts' remaining capacity.
4. A productized, repeatable "Megapod site" that can later extend to Supercharger sites, as the CEO described on the Q2 2026 call.
5. Grid diversification away from a single ERCOT node at Giga Texas.

## 9. Key assumptions to confirm before term sheets

- Megapod reference block: 20 MW IT compute, 20–40 MWh Megapack (one or two Megablocks), ~26 MW gross at PUE 1.3, ~1 acre pad. *Program assumption; Tesla Energy engineering to confirm.*
- Megapack 3 internal cost and 2027 allocation carve-out for the program. *Tesla Energy finance.*
- Whether Tesla contracts through Tesla, Inc. or a Tesla Energy Ventures subsidiary (Tesla Energy Ventures already holds an ERCOT retail electric provider certificate).
- Fiber: training clusters need high-bandwidth backhaul to Austin, not low latency; confirm dark-fiber availability at each Tier 1 site.
- Tax: whether Megapods qualify for accelerated depreciation and energy-storage credits at third-party sites.
