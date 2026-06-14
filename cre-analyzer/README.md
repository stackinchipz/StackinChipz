# cre-analyzer

A TypeScript / Node.js CLI that runs a **Commercial Real Estate Lease vs. Buy**
analysis for a subject property. It ingests **4 sale comps** and **4 lease
comps**, **normalizes every cash flow for property taxes**, and outputs a
recommendation with IRR / NPV sensitivity tables.

> **The thesis:** 90% of lease-vs-buy models get property tax wrong. A sale
> comp's NOI reflects the *seller's* stale, low assessed value — not what *you*
> will pay after reassessment. A "$15 Gross" lease in a high-tax county is not
> the same as a "$15 NNN" bundle in a low-tax county. `cre-analyzer` restates
> **every** comp at the **subject property's** projected tax burden before it
> compares anything.

---

## Quick start

```bash
# 1. Install
npm install

# 2. Run the mock analysis (instant, no credentials)
npx ts-node src/cli/index.ts analyze \
  --provider mock \
  --address "123 Industrial Way, Austin, TX" \
  --discount-rate 0.08 \
  --report ./cre-analysis-report.html

# 3. Run the tests (validates the tax + finance math)
npm test

# 4. Open the HTML report
open ./cre-analysis-report.html   # macOS  (xdg-open on Linux)
```

After `npm run build`, the `cre-analyzer` bin is available:

```bash
npm run build
node dist/cli/index.js analyze --provider mock --address "Test St"
```

---

## Architecture

```
                         ┌──────────────────────────────────────┐
                         │                CLI                    │
                         │        src/cli/index.ts (commander)   │
                         └───────────────┬──────────────────────┘
                                         │
              ┌──────────────────────────┼───────────────────────────┐
              │                          │                           │
     ┌────────▼─────────┐      ┌─────────▼──────────┐      ┌─────────▼─────────┐
     │    PROVIDERS     │      │      ENGINE        │      │     REPORTERS     │
     │  IListingProvider│      │  (pure functions)  │      │                   │
     │  ├ MockProvider  │─────▶│  taxNormalizer  ◀──┼──┐   │  ConsoleReporter  │
     │  ├ ManualEntry   │ bundle  compSelector      │  │   │  JsonReporter     │
     │  ├ CoStarAdapter │      │  buyAnalyzer       │  │   │  HtmlReporter     │
     │  ├ CrexiAdapter  │      │  leaseAnalyzer     │  │   │  (Chart.js CDN)   │
     │  └ LoopNetAdapter│      │  comparisonEngine  │  │   └─────────▲─────────┘
     └──────────────────┘      │  sensitivity       │  │             │
                               │  finance (decimal) │  │   AnalysisResult
                               └─────────┬──────────┘  │             │
                                         │             │             │
                                         └─────────────┘─────────────┘
                                   normalize ALL comps to the
                                   subject's tax context FIRST
```

- **Adapter pattern** for data: there is no single API for "all commercial
  listings" — CoStar, Crexi, LoopNet and the MLSs are walled gardens. Program
  against `IListingProvider`; swap the implementation.
- **Pure functions** in `src/engine` — no I/O, no side effects. `decimal.js`
  is used for money-sensitive accumulations (amortization, NPV) to avoid
  floating-point drift across a 10-year hold.
- **Three reporters**: `console.table` for the terminal, `--json` export, and a
  self-contained `--report` HTML file with embedded Chart.js charts and a
  color-coded sensitivity grid.

### File structure

```
cre-analyzer/
├── src/
│   ├── types/index.ts            # Strict, tax-inclusive data models
│   ├── providers/                # Adapter pattern (mock, manual, costar, …)
│   ├── engine/                   # Pure financial + tax functions
│   │   ├── taxNormalizer.ts      #   ★ the heart — HIGH-PRIORITY TESTS
│   │   ├── compSelector.ts       #   subject-centric comp selection
│   │   ├── buyAnalyzer.ts        #   owner-occupied buy scenario
│   │   ├── leaseAnalyzer.ts      #   tenant lease scenario
│   │   ├── comparisonEngine.ts   #   NPV / differential IRR / break-even
│   │   ├── sensitivity.ts        #   exit cap × discount × tax growth grid
│   │   ├── finance.ts            #   PMT / NPV / IRR (decimal.js)
│   │   └── analysis.ts           #   orchestrator + default assumptions
│   ├── reporters/                # Console / JSON / HTML
│   └── cli/index.ts              # commander entry point
└── tests/                        # taxNormalizer, finance, buy, comparison
```

---

## How Tax Normalization Works

> *"All numbers must include property taxes."* This is the single most important
> requirement, and it is enforced at the type level: every comp carries a
> mandatory `PropertyTaxContext`.

### 1. Sale comps (historical) — strip the seller's basis, inject yours

A sale comp's reported NOI is **post-(its own)tax**. That tax reflects the
seller's assessment, which is often years stale and far below what a new buyer
will pay after a sale-triggered reassessment.

```
adjustedNoi = reportedNoi + oldTax − subjectProjectedTax
adjustedCapRate = adjustedNoi / salePrice
```

- `oldTax` is added back to restore pre-tax NOI.
- `subjectProjectedTax` (the subject's projected post-purchase bill, scaled to
  the comp's size) is then subtracted.

**Worked example (validation checklist #3):** comp taxed at **\$0.50/SF**,
subject projected at **\$2.00/SF**, on a \$1M / 10,000 SF comp with \$70k NOI
(7% reported cap):

```
adjustedNoi = 70,000 + 5,000 − 20,000 = 55,000
adjustedCap = 55,000 / 1,000,000 = 5.5%   ← cap rate drops, as it must
```

### 2. Lease comps (current market) — collapse to an NNN equivalent

Different lease structures bury property tax in different places. We collapse
every lease to a single **all-in occupancy cost** at the comp's own tax…

| Structure       | All-in (NNN-equivalent) occupancy cost |
| --------------- | -------------------------------------- |
| NNN             | base + tax + insurance + CAM           |
| NN              | base + tax + insurance (CAM in base)   |
| N               | base + tax (ins + CAM in base)         |
| Gross           | base (everything embedded)             |
| Modified Gross  | base + OpEx **above the expense stop** |

…then swap the comp's tax for the subject's:

```
subjectAdjustedRent = nnnEquivalent − compTax + subjectProjectedTax
```

**Worked example (validation checklist #4):** a **\$15 Gross** lease and a
**\$10 base + \$3 tax + \$1 ins + \$1 CAM** NNN lease both normalize to
**\$15/SF** effective. Shift them to different tax counties and they correctly
diverge — the whole point.

### 3. Subject buy scenario (Year 1+) — reassess immediately

The buy scenario never uses the subject's *current* tax bill. Year 1 uses the
**post-reassessment** bill (`estimatedPostTransactionTax`, or
`salePrice × assessmentRatio × millageRate` when jurisdiction data is supplied).
Subsequent years grow subject to any statutory cap (Prop 13 CA, FL 2%, etc.)
via `applyAssessmentCap`.

---

## The "4 comps on the same property" interpretation

A single building is rarely listed for sale **and** lease with four comps each
simultaneously. `cre-analyzer` uses the standard appraisal method — a
**Subject-Property-Centric** workflow:

1. Take the subject property's attributes + tax bill.
2. Pull 4 comparable **sales** (similar buildings that sold).
3. Pull 4 comparable **leases** (similar spaces for lease).
4. **Normalize both sets** to the subject's tax context, then derive value.

`compSelector.ts` ranks the pool by a similarity score (size, age, type) and
selects the closest four of each.

---

## CLI reference

```bash
cre-analyzer analyze \
  --address "123 Main St, City, ST" \
  --provider mock          # mock | manual | costar | crexi | loopnet
  --holding-period 10 \
  --discount-rate 0.08 \
  --ltv 0.70 \
  --interest-rate 0.065 \
  --amort-years 25 \
  --exit-cap-premium 0.0075 \
  --rent-growth 0.03 \
  --tax-growth 0.02 \
  --output table           # table | json
  --json ./out.json \
  --report ./report.html \
  --no-sensitivity         # skip the (slower) sensitivity grid
```

**Interactive mode:** `--provider manual` launches `inquirer` prompts to enter
4 sale + 4 lease comps by hand, with validation including *"Does this lease comp
include property taxes? Y/N"* and *"Does the reported NOI already deduct
taxes?"*.

---

## Output metrics

| Metric                     | Meaning                                                              |
| -------------------------- | ------------------------------------------------------------------- |
| **NPV of Costs** (Buy/Lease) | Present value of each scenario's net costs. **Lower is better.**   |
| **Differential IRR**       | Return on the *extra* capital buying ties up vs leasing. Beat the discount rate → buy wins. |
| **Break-Even Year**        | First year cumulative buy cash flow overtakes leasing.              |
| **Sensitivity Table**      | NPV advantage of buying across `[exit cap] × [discount] × [tax growth]`. |

---

## Using real data

There is **no** single API for all commercial listings. In order of effort:

1. **Low** — build a CSV provider: paste a CoStar/Crexi export into a CSV and
   implement `IListingProvider` over it (mirror `MockProvider`).
2. **Medium** — ATTOM Data or Reonomy (property + tax history, cheaper than
   CoStar). Implement an adapter; their tax-history endpoints feed the
   normalization step directly.
3. **High** — implement the `CoStarAdapter` / `CrexiAdapter` / `LoopNetAdapter`
   stubs with enterprise API keys.

### API key setup

The credentialed adapters read keys from environment variables (use a `.env`
or your shell):

| Provider | Variables                                               |
| -------- | ------------------------------------------------------- |
| CoStar   | `COSTAR_API_KEY`, `COSTAR_API_SECRET`, `COSTAR_BASE_URL` |
| Crexi    | `CREXI_API_KEY`, `CREXI_BASE_URL`                       |
| LoopNet  | `LOOPNET_API_KEY`, `LOOPNET_BASE_URL`                   |

```bash
export COSTAR_API_KEY="..."
export COSTAR_API_SECRET="..."
cre-analyzer analyze --provider costar --address "123 Main St"
```

The adapters are **stubs** — they validate credentials and document the
integration shape, then throw `NotImplemented`. Wire in the real HTTP mapping
(geocode → property attributes + tax history → sale/lease comps → map onto our
types, preserving each comp's tax basis) and remove the throw.

---

## Validation checklist

| Check | Status |
| ----- | ------ |
| `tsc --noEmit` compiles | ✅ |
| `npm test` passes (52 tests, >90% line coverage on `engine/`) | ✅ |
| Tax logic: comp \$0.50/SF vs subject \$2.00/SF → adjusted cap drops | ✅ `taxNormalizer.test.ts` |
| Lease logic: \$15 Gross vs \$10+\$3+\$1+\$1 NNN both → ~\$15 effective | ✅ `taxNormalizer.test.ts` |
| `--provider mock` → clean HTML report with sensitivity table | ✅ |
| Mock scenario: Buy IRR in 8–12% band, buy wins long-term | ✅ (~8.8% IRR, BUY) |

---

## Disclaimer

Estimates only — **not** investment, tax, or legal advice. Validate every
assumption (cap rates, reassessment rules, statutory caps) against local
jurisdiction data and a qualified professional before transacting.

_Built with [Claude Code](https://claude.com/claude-code)._
