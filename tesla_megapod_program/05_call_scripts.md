# Call Scripts

*Three scripts: the first live call to a decision-maker, the gatekeeper / executive-assistant call, and the second call once a non-disclosure agreement is in place. Written to be spoken, not read. Brackets mark where the caller substitutes the per-company hook from `04_target_list.md`. Keep the first call under twelve minutes; the only goal is a 45-minute working session with their power and commercial leads.*

---

## Script A — First call to the CEO, President, or Chief Commercial / Data Center Officer

### Open (30 seconds)

"[Name], this is [Caller] with Tesla Energy. I run [commercial / strategic sites] for the Megapack business and I'm calling about [Site], specifically the [X] megawatts you have [energized / coming online in 2027] that aren't under a long-term lease yet. I have a specific proposal and it takes about ten minutes to lay out. Is now bad?"

*If "now is bad":* "Understood. I'll send two paragraphs by email so you can decide whether it's worth fifteen minutes with your power and commercial leads. What's the best address for that?" Then stop. Do not pitch on a bad call.

### Frame (60 seconds)

"The short version: Tesla wants to be a tenant, not a vendor. We'd bring our own compute and our own batteries to your site in a self-contained module we call a Megapod, and we'd pay you a fixed site fee on reserved megawatts, starting from the day power is available. You keep the interconnection, the land, and the operations. We bring everything from the switchgear in."

"Three things make that different from the AWS or CoreWeave leases you've seen. First, you don't build a data hall, so your capital is a couple of million per megawatt, not eleven or twelve. Second, we can energize months after signing instead of two years, because Megablock integrates the transformer and switchgear and we've deployed a gigawatt-hour in twenty business days. Third, you're getting Tesla credit on the paper, and you're getting a tenant that also makes the battery you need to firm the rest of your campus."

### Discover (4–5 minutes)

Ask, then listen. Write down the numbers.

1. "Walk me through what's actually uncontracted at [Site] today, in gross megawatts at the point of interconnection, and when each block is energized."
2. "What's your interconnection classification? Firm, or [curtailable / Partial Capacity Load / conditional Base Load] under the ERCOT batch process?" *(Outside Texas: "Any curtailment or demand-response obligations attached to the interconnection?")*
3. "What are you earning per megawatt on that capacity right now, mining or hosting, and what's your power cost?"
4. "Have you got a tenant process running on it? Who's leading that on your side and where is it?"
5. "If a tenant paid you a fixed fee per reserved megawatt and funded the entire build beyond the switchgear, what would you need per megawatt-year to prefer that over waiting for a fifteen-year hyperscaler lease?"
6. "Who on your side owns power procurement and grid strategy? I'd like them on the next call."

### Position (2 minutes)

Use their numbers. Example at a Texas site mining at 18 J/TH with $50 power:

"At today's hashprice you're clearing something like two hundred thousand dollars a megawatt-year before opex. We'd open in the high seven hundreds on reserved gross megawatts, escalating with CPI, and we'd fund everything past your switchgear. That's three to four times what the megawatt earns today, with no construction loan and no GPU risk on your books. And because we'd put Megapacks on the pad, we'd be happy to talk about a priority allocation for your own firming needs on the rest of the campus. Megapack is effectively sold out for 2027, so that allocation is worth something."

*If they anchor on $1.8M+ colocation rent:* "That's the right number for a landlord who funds a twelve-million-dollar-a-megawatt shell and waits two years for rent. We're asking you to fund two, and rent starts in months. The yield on your capital is higher in our structure. If you'd rather build the shell and have us lease it, we can price that too, but then we're in a hyperscaler process and we'd expect hyperscaler pricing."

### Close (60 seconds)

"Here's what I'd propose. We sign a mutual NDA this week. You send me the one-line summary of each uncontracted block: gross megawatts, energization date, interconnection status, power cost. We come back inside ten business days with a site-specific term sheet, including the Megapack allocation option. Then we get your power lead and our Megapack engineering lead on a forty-five minute call to walk the pad layout. Does [day] or [day] next week work for that call?"

Confirm the attendees, confirm the NDA path, confirm the email address for the one-pager. Thank them. End the call.

### Do not

- Do not discuss Tesla's own compute roadmap, chip plans, or Giga Texas capacity beyond what is public.
- Do not quote a walk-away number.
- Do not mention SpaceX, xAI, or Colossus except to answer a direct question, and then only with public facts.
- Do not disparage CoreWeave, Fluidstack, or any existing tenant.

---

## Script B — Executive assistant or gatekeeper

"Good morning, this is [Caller] from Tesla Energy. I'm trying to reach [Name] about [Company]'s [Site] data center capacity. It's a commercial matter, not a sales call: Tesla is looking at leasing capacity at the site. Is [Name] the right person, or would that sit with [alternate name and title from the target list]?"

*If asked to email:* "Happy to. What's the best address, and is there a time [Name] usually takes outside calls? I'll keep it to two paragraphs."

*If asked what Tesla wants:* "We'd like to be a tenant at [Site]. We'd bring our own equipment and pay a fixed fee on reserved megawatts. I'd rather [Name] hear the numbers directly than through me paraphrasing, but that's the substance."

Ask for a calendar hold rather than a callback. Send the Email 1 template within the hour and reference the assistant by name.

---

## Script C — Second call, after NDA, with the host's power and commercial leads

### Agenda (state it up front, 30 seconds)

"Forty-five minutes. Three parts: you walk us through the blocks and the interconnection; we walk you through the Megapod reference block and how it sits on the pad; then we agree what goes into the term sheet and who signs what by when."

### Part 1 — Their blocks (15 minutes)

Get on the record, block by block: gross MW at the point of interconnection; energization date; firm versus curtailable; utility or retail electric provider and current contract term and price; any existing tenant process, exclusivity, or right of first offer on the capacity; lender consents required; fiber providers at the site; water availability; acreage available for pads; any demand-response or 4CP programs the site participates in.

### Part 2 — The reference block (15 minutes)

"Our reference Megapod block is about 20 megawatts of IT load with one to two Megablocks, which is 20 to 40 megawatt-hours of storage, on roughly an acre. Gross draw at the switchgear is about 26 megawatts. The battery does three jobs: it smooths the training load so your utility never sees the swings; it gives us ride-through so we can honor a curtailment call without dropping the job; and it lets us run as a controllable load, which protects your interconnection classification. Five blocks is a hundred megawatts and about five acres."

Then ask: "What does your interconnection agreement say about ramp rates and load factor? And what notice do you get on curtailment?"

### Part 3 — Term sheet mechanics (15 minutes)

Agree on paper: reserved gross MW and delivery schedule by block; fee basis (reserved MW, not consumed energy) and the escalator; power pass-through mechanism; initial term and extension options; capacity-delivery liquidated damages; Tesla's expansion right of first refusal and the host's right of first offer on Tesla's next regional site; the Megapack allocation option and whether it is priced as a fee credit or a separate purchase order; credit support on both sides; who drafts (Tesla drafts the master site agreement; host drafts the site schedule).

### Close

"We'll circulate the term sheet draft within ten business days of receiving your block data. Our ask is that you hold the [X] megawatts for thirty days while we paper it. Can you do that?"

---

## Voicemail (under 25 seconds)

"[Name], [Caller] with Tesla Energy. Calling about the uncontracted capacity at [Site]. Tesla would like to be a tenant there, bringing our own compute and batteries and paying a fixed fee per reserved megawatt. I've sent a short email with the specifics. [Number]. Thanks."
