# Email Templates

*A five-touch sequence plus three situational emails. Subject lines are deliberately plain: executives at these companies get dozens of "AI data center partnership" emails a week and delete the ones that look like marketing. Every email names a site, a megawatt figure, and a date. Substitute the per-company hook from `04_target_list.md`. No email is sent to an address that has not been verified; see the contacts file for sourcing rules.*

---

## Email 1 — First contact (day 0)

**Subject:** [Site] — Tesla as tenant on the uncontracted [X] MW

[First name],

Tesla would like to lease capacity at [Site]. We would be the tenant, not the vendor: we bring our own compute and our own Megapack storage in a self-contained module, and we pay you a fixed site fee on reserved megawatts from the day power is available.

Why that is a better trade than the leases you have seen so far:

- You do not build a data hall. Your capital is switchgear and pads, roughly $2M a megawatt, not $11–12M.
- Rent starts in months. Megablock integrates the transformer and switchgear, and we have deployed a gigawatt-hour of storage in twenty business days.
- You get Tesla credit on the paper, and a tenant who also makes the battery that firms the rest of your campus. Megapack is effectively sold out for 2027; we can talk about a priority allocation as part of the deal.

[One sentence per-company hook, e.g.: "Your Q3 release puts [Site] at [X] MW energized with [Y] MW not yet under lease, and we think that block is the right size for a first phase."]

I would like forty-five minutes with you and whoever owns power and grid strategy on your side. If [day] or [day] next week works, I will send a mutual NDA ahead of it.

[Caller]
[Title], Tesla Energy
[Phone]

---

## Email 2 — Follow-up (day 3)

**Subject:** Re: [Site] — Tesla as tenant on the uncontracted [X] MW

[First name],

Two numbers, in case the first note got buried.

At today's hashprice, a megawatt mining at 18 J/TH clears about $0.2M a year before opex. The site fee we would open with on reserved gross megawatts is in the high $0.7Ms per megawatt-year, escalating, with Tesla funding everything beyond your switchgear.

That is three to four times what the megawatt earns today, with no construction loan and no GPU on your balance sheet.

Happy to put that in a site-specific term sheet inside ten business days of an NDA. Who should I send the NDA to?

[Caller]

---

## Email 3 — Proof point (day 8)

**Subject:** How the Megapack side of this helps your remaining capacity

[First name],

Setting aside the tenancy for a moment.

[Per-company hook on firming, e.g.: "ERCOT has [Site / X MW of your pipeline] classified as [Partial Capacity Load / conditional Base Load], which means curtailment before transmission upgrades." or "Your Beacon Point design already calls for battery systems to manage voltage." or "Under SB6, loads over 75 MW can be ordered to curtail on roughly 24 hours' notice during firm load shed."]

A Megapod block carries one to two Megablocks, 20 to 40 MWh, per 20 MW of compute. That storage lets the load ride through a curtailment call, smooth training swings so the utility never sees them, and operate as a controllable load. The same approach can firm the capacity you keep for other tenants, and we would include a priority Megapack allocation for that in the term sheet.

If the tenancy is not interesting, the allocation conversation might still be. Fifteen minutes either way?

[Caller]

---

## Email 4 — Breakup (day 15)

**Subject:** Closing the loop on [Site]

[First name],

I have not heard back, which usually means one of three things: the capacity is spoken for, this is the wrong desk, or the timing is off.

If it is spoken for, congratulations, and I would still like to talk about Megapack for your next phase. If it is the wrong desk, a name is all I need. If the timing is off, tell me when to come back and I will.

Otherwise I will assume [Site] is not available and take it off our list for 2027.

[Caller]

---

## Email 5 — Re-engage on a trigger (as needed)

**Subject:** [Trigger] — revisiting [Site]

[First name],

Saw [the Q3 print / the ERCOT batch classification / the tenant announcement / the financing]. [One sentence on why it changes the picture, e.g.: "With Black Pearl now billing, the Odessa megawatts are the obvious next block, and a tenant that brings its own hall gets you there in 2027 instead of 2028."]

Our offer from [month] stands. Term sheet in ten business days of an NDA.

[Caller]

---

## Situational A — To the Chief Financial Officer (when the CEO has routed you there)

**Subject:** [Site] site fee economics for your model

[First name],

[CEO name] suggested I send you the structure directly.

- Fee basis: reserved gross MW at the point of interconnection, not consumed energy. Rent is owed whether or not we are running.
- Opening level: high $0.7Ms per MW-year, CPI escalator capped at 3%.
- Your capital: switchgear and pads, roughly $1.5–2M per MW. Everything from the switchgear in is Tesla's.
- Term: ten years with two five-year Tesla options. Equipment is a removable trade fixture, so your site stays marketable for a longer hyperscaler lease on the remaining capacity.
- Credit: Tesla parent guarantee. Hut 8 financed River Bend and Beacon Point with $3.25B and $4.25B of investment-grade project bonds against tenant leases; our paper should finance at least as well.
- Power: passed through at cost. Battery grid revenue stays with Tesla; in ERCOT it is worth about $24 per kW-year this year, so it is not material to either of us.

If the yield on a $2M per MW contribution at that fee works in your model, the rest is pad layout and paper.

[Caller]

---

## Situational B — To the head of power / grid strategy

**Subject:** [Site] — interconnection questions before we draft

[First name],

Before our team drafts the site schedule, I would like to confirm six things about [Site]:

1. Gross MW available at the point of interconnection by block, and energization dates.
2. Interconnection classification and any curtailment obligations (ERCOT batch status, SB6 demand-management enrollment, utility interruptible tariff).
3. Ramp-rate and load-factor limits in the interconnection agreement.
4. Current supply arrangement: utility tariff or retail electric provider, term, and whether it is assignable or can be mirrored back-to-back.
5. Fiber providers on site and the nearest long-haul route.
6. Acreage available for pads within reach of existing medium-voltage gear.

A reply in rough numbers is fine; we will refine on the call.

[Caller]

---

## Situational C — Introduction through a board member or banker

**Subject:** Intro request — Tesla Energy and [Company]

[Intermediary first name],

Tesla Energy is approaching a short list of operators with energized, uncontracted capacity about hosting Tesla-owned compute and storage modules under a fixed site-fee lease. [Company]'s [Site] is on that list because [one-line reason: megawatts, timing, interconnection status].

Would you be willing to introduce me to [Name, Title]? Two sentences from you will land better than a cold note from me. I have attached a one-paragraph description you can forward as is.

[Caller]

---

## Rules for the sequence

- Send from a named Tesla Energy individual, not a shared mailbox.
- One email per touch. No attachments until the NDA is signed; the "one-pager" is the body of Email 1.
- Log every send and reply in the tracker (`09_90_day_plan.md`, section 5).
- If a company has two targets (for example a CEO and a Chief Data Center Officer), send Email 1 to both on the same day and say so in each.
- Stop the sequence the moment anyone at the company replies, and move to Script C.
