# Cursor Build Prompt: SignalOS

You are building SignalOS, a modular quantitative trading operating system.

## Current Product

The current repo contains an MVP options-convergence scanner.

The logic:

```text
Unusual Options Activity = conviction
Money Flow = direction
Convergence = conviction + direction
```

## Current Modules

- Demo data generator
- Daily scanner
- UOA score
- Money-flow score
- Trend score
- Relative strength score
- Liquidity score
- Convergence score
- Reject-reason engine
- Defined-risk trade suggestions
- Basic underlying-return backtest
- Streamlit dashboard

## Build Principles

- Keep everything modular.
- Do not mix data ingestion, scoring, backtesting, and UI logic.
- Every score must be auditable.
- Every rejected trade must have an explicit reason.
- No auto-trading.
- Defined-risk structures only.
- Do not optimize thresholds until backtests exist.
- Prefer simple measurable systems over complex black boxes.

## Immediate Next Task

Implement v0.2 real data integration.

### Requirements

1. Create provider abstraction:

```text
src/signalos/data_sources/base.py
src/signalos/data_sources/csv_provider.py
src/signalos/data_sources/tradier_provider.py
```

2. Add data validation:

```text
src/signalos/data_sources/validation.py
```

3. Add CLI command:

```bash
python scripts/run_daily_scan.py --stock-daily <path> --option-chain <path>
```

4. Preserve demo mode.

5. Add tests for validation.

## Do Not

- Rewrite the whole repo.
- Add machine learning yet.
- Add broker execution yet.
- Remove CSV support.
- Remove explicit reject reasons.

## Definition of Done

- Demo still works.
- CSV import works.
- Missing columns produce clear errors.
- Dashboard still loads.
- README updated.
