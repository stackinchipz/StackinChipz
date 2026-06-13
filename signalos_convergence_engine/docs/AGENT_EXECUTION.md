# Agent Execution Layer (propose-only)

The bridge between the screen and a broker. It reads screened signals, sizes
each through the risk engine, and emits guarded **trade proposals** with a
plain-English thesis and invalidation. By default it places **no live orders**.

Module: `src/signalos/agent/` · Runner: `scripts/run_agent.py`

## Two-barrier safety
A live order can only be sent when **both** are true:
1. a real (non-dry-run) broker is explicitly injected, **and**
2. `execute=True` is passed.

The default broker is `DryRunBroker`, which records intent but never submits —
even with `execute=True`. The only live-broker class, `MCPBrokerStub`, **raises**
on `submit()` by design: a real brokerage connection and its OAuth token must
live on your local machine, not in this repo or a shared environment. You
implement `submit()` locally against the Robinhood/Tradier MCP.

```
screen_signals.csv
   → size_screen (risk engine: sizing, heat, sector caps, kill-switch)
   → build_proposals (thesis + invalidation)
   → broker.submit (dry-run by default)
   → audit log (outputs/agent_proposals.jsonl)
```

## A proposal contains
`ticker, bias, screen, structure, contracts, risk_pct, max_loss_per_contract,
dollar_risk, binding_constraint, convergence_score, power_gauge_rating,
capital_verdict, iv_regime, thesis, invalidation, entry_note, status, created_at`

Example narrative (demo):
```
Thesis:       Compounder: capex is converting to returns; Uniform ROA 16%;
              ROIIC 19%; Power Gauge Bullish; UOA 92 / money flow 70 confirm
              bullish; IV Low.
Invalidation: Exit if CMF(21) flips negative or close breaks below 20DMA;
              premium stop -50%.
Entry:        Compounder Breakout | long call (cheap IV) | ref strike 200.46,
              exp 2026-08-17 | IV Low, ~3.7% expected move
```

## Run
```bash
python scripts/run_screen.py --demo
python scripts/run_agent.py --signals outputs/screen_signals.csv
```

## Going live (local only)
1. Connect the Robinhood/Tradier MCP locally (`docs/ROBINHOOD_AGENT_SETUP.md`).
2. Subclass `ExecutionBroker`, implement `submit()` against the MCP.
3. Stage the rollout: **propose-only → manual approval → tiny live size →
   authorized execution**, with the risk caps live the whole way.

The risk engine is the last gate before any order leaves. Guardrails are
enforced here in code — never delegated to a model's judgment.
