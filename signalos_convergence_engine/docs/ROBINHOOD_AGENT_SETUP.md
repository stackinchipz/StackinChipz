# Robinhood Agentic Trading — Setup Checklist (Track A)

This documents how SignalOS connects to Robinhood's **agentic trading** (the
"Connect your agent" / MCP feature). It is the **execution arm** and is separate
from the **screen** (Track B), which only produces ranked candidates.

```
Screen (Track B)  →  ranked signals  →  Agent runtime (Track A)
                                         → risk-engine guardrails
                                         → Robinhood MCP places defined-risk trade
```

## Important: where this runs
**Not in the Claude Code web sandbox.** That environment is ephemeral and
network-restricted, and you should never store a live brokerage OAuth token
there. Run the agent from **local Claude Code** (or the Claude Agent SDK) on a
machine you control, or use Robinhood's own in-app agent connection.

## Checklist

### 1. Enable on the Robinhood side
- [ ] Enroll in the agentic-trading **beta** in the Robinhood app.
- [ ] Tap **Connect your agent** and create the **dedicated agent sub-account**
      (walled off from your main portfolio).
- [ ] **Fund** the sub-account with only risk capital.
- [ ] Capture the **MCP endpoint + OAuth** details Robinhood provides. Confirm
      the exact URL from the app — do not hard-code a guessed endpoint.

### 2. Connect the MCP locally
Add the Robinhood MCP server to local Claude Code. These are Robinhood's
official instructions (Agentic Trading overview), verified 2026-06:
```bash
claude mcp add robinhood-trading --transport http https://agent.robinhood.com/mcp/trading
```
Then in Claude Code: enter `/mcp`, select **robinhood-trading**, and authenticate
(OAuth). Server name is `robinhood-trading`; transport is Streamable HTTP.

Other runtimes (same MCP link `https://agent.robinhood.com/mcp/trading`):
- **Claude Desktop:** Settings → Connectors → Add custom connector → paste link.
- **Codex CLI:** `codex mcp add robinhood-trading --url https://agent.robinhood.com/mcp/trading`, then `/mcp` → select.
- **Cursor:** Settings → Tools & MCPs → Connect, give it the link.
- **ChatGPT / Grok / others:** add the same MCP link as a custom connector.

Keep the token in your OS keychain / local env — never commit it.

### 3. Insert SignalOS guardrails (mandatory)
- [ ] Run the screen → `outputs/screen_signals.csv`.
- [ ] Pass tradable rows through `signalos.risk.apply_risk_engine` so every
      proposed order has `contracts`, `dollar_risk`, and a binding constraint.
- [ ] Enforce, in code (not prompt): `max_risk_per_trade_pct`,
      `max_portfolio_heat_pct`, `max_sector_heat_pct`, `max_positions`,
      `daily_drawdown_kill_pct`. See `docs/RISK_ENGINE.md`.
- [ ] Defined-risk structures only (long options / debit / defined-risk credit).
      No naked short options.

### 4. Stage rollout (don't skip the order)
1. **Propose-only** — agent reads the screen and *suggests* trades; you approve
   each one manually in the app.
2. **Paper / tiny size** — let it place minimum-size defined-risk trades in the
   funded sub-account; compare fills vs. the screen's assumptions.
3. **Authorized execution** — only after live-vs-backtest hit rate holds, with
   the risk caps live and a kill-switch wired.

### 5. Audit + monitoring
- [ ] Log every signal → decision → order with a written thesis + invalidation.
- [ ] Reconcile sub-account positions vs. the system daily.
- [ ] Track per-layer P&L attribution (flow vs. fundamental) and signal decay.

## What this repo provides vs. what you wire locally
| Provided here | You wire locally |
|---|---|
| Screen, scores, IV regime | RH beta enrollment + sub-account |
| Risk engine / guardrails | RH MCP OAuth connection |
| Trade suggestions (defined-risk) | Agent runtime + approval gates |
| Audit-ready CSV outputs | Order placement via RH MCP |
