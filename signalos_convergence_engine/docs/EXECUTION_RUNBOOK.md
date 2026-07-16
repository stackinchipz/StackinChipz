# Execution Runbook — Screen → Robinhood

Two ways to take SignalOS proposals to the Robinhood agentic sub-account. Both
run **locally** (never in a shared/ephemeral environment). Start with Model A.

Robinhood MCP: `https://agent.robinhood.com/mcp/trading` · server `robinhood-trading`.

> **⚠️ Beta reality (verified 2026-06): Robinhood is equities-only.** Trade tools
> are `review_equity_order` / `place_equity_order` / `cancel_equity_order` — no
> options tool yet. SignalOS builds options structures, so on RH today route the
> **directional conviction to equities** (`asset_class="equity"`), or keep
> **options on Tradier**. Always `review_equity_order` before `place_equity_order`.

---

## Model A — Claude Code drives it (recommended, human-in-the-loop)

No new code. You approve every trade.

### One-time
1. Enroll in Robinhood agentic beta; create + fund the dedicated sub-account
   (see `ROBINHOOD_AGENT_SETUP.md`).
2. Connect the MCP to local Claude Code:
   ```bash
   claude mcp add robinhood-trading --transport http https://agent.robinhood.com/mcp/trading
   ```
   Then `/mcp` → select **robinhood-trading** → authenticate (OAuth).

### Each session
1. Generate signals + propose-only proposals:
   ```bash
   python scripts/run_screen.py --demo          # or live providers
   python scripts/run_agent.py --signals outputs/screen_signals.csv
   ```
   This writes `outputs/screen_signals.csv` and `outputs/agent_proposals.jsonl`
   (each proposal already sized by the risk engine, with thesis + invalidation).
2. In local Claude Code (RH MCP connected), prompt (equities-only beta):
   > "Read `outputs/agent_proposals.jsonl`. For each **Bullish** proposal with
   > status PROPOSED and contracts > 0, buy the underlying stock in my Robinhood
   > Agentic account: first call `review_equity_order`, show me the pre-trade
   > result, and only `place_equity_order` after I confirm. Skip bearish/options
   > structures (RH beta can't place them). Stop if total notional would exceed
   > my budget."

   (Once RH ships options tools — or for options today — run the same flow
   against **Tradier** instead, using the defined-risk structures verbatim.)
3. Approve each order. Robinhood notifies you on every fill ("Track every move").

### Guardrails that still apply
The proposals are pre-sized against `max_risk_per_trade_pct`,
`max_portfolio_heat_pct`, `max_sector_heat_pct`, `max_positions`, and the daily
kill-switch (`RISK_ENGINE.md`). Keep the "confirm before submit" instruction
until you've watched it behave.

---

## Model B — Python broker (full automation, advanced)

`signalos.agent.RobinhoodMCPBroker` builds a normalized, **defined-risk order
spec** from a proposal and hands it to an `mcp_invoker` you wire locally (the RH
MCP attaches to an agent runtime, not to plain Python — so you provide the
callable that drives it, e.g. via the Claude Agent SDK with the MCP configured).

```python
from signalos.agent import RobinhoodMCPBroker, run_agent
import pandas as pd

signals = pd.read_csv("outputs/screen_signals.csv")

# 1) Stage only (safe): build orders, send nothing.
#    asset_class="equity" -> RH-executable equity orders (beta reality).
#    asset_class="option" -> defined-risk options specs for Tradier/future RH.
staged = run_agent(signals, broker=RobinhoodMCPBroker(asset_class="equity"), execute=True)
#   every routing -> status "STAGED", submitted False

# 2) Go live (two barriers): armed=True AND a real invoker.
def rh_invoker(order_spec: dict) -> dict:
    # Drive the robinhood-trading MCP order tool here (Agent SDK / local client),
    # return the broker's order result. THIS is the only code that sends.
    ...

live = run_agent(
    signals,
    broker=RobinhoodMCPBroker(armed=True, mcp_invoker=rh_invoker),
    execute=True,
)
```

### Two-barrier safety
A live order sends only when **both** are true: the broker is `armed=True` **and**
a real `mcp_invoker` is supplied. Default construction stages and returns the
order without sending. Rejected/zero-size/naked structures never submit, even
when armed.

### Staged rollout (do not skip)
propose-only → Model A manual approval → Model B **staged** (no send) →
Model B armed with tiny size → full automation — risk caps live throughout.
