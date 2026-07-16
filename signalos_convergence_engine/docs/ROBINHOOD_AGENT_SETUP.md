# Robinhood Agentic Trading — Setup Checklist (Track A)

This documents how SignalOS connects to Robinhood's **agentic trading** (the
"Connect your agent" / MCP feature). It is the **execution arm** and is separate
from the **screen** (Track B), which only produces ranked candidates.

```
Screen (Track B)  →  ranked signals  →  Agent runtime (Track A)
                                         → risk-engine guardrails
                                         → Robinhood MCP places the order
```

## ⚠️ Beta reality (verified 2026-06)
Robinhood agentic trading is **equities-only** in beta. Options, crypto, and
futures are "coming soon." The MCP's only trade tools are `review_equity_order`,
`place_equity_order`, `cancel_equity_order` — **there is no options order tool
yet.** SignalOS produces *options* structures, so on Robinhood today you either:
- route the screen's **directional conviction to equity** orders
  (`RobinhoodMCPBroker(asset_class="equity")`), or
- keep **options execution on Tradier** and use RH for equities.
When RH ships options tools, the broker's `asset_class="option"` path lights up.

### MCP tools (confirmed)
- Read: `get_accounts`, `get_portfolio`, `get_equity_positions`,
  `get_equity_quotes`, `get_equity_orders`, `search`
- Watchlists: `get_watchlists`, `add_to_watchlist`, `update_watchlist`
- Trade: `review_equity_order` → `place_equity_order`, `cancel_equity_order`
  (always **review before place**)

## Important: where this runs
**Not in the Claude Code web sandbox.** That environment is ephemeral and
network-restricted, and you should never store a live brokerage OAuth token
there. Run the agent from **local Claude Code** (or the Claude Agent SDK) on a
machine you control, or use Robinhood's own in-app agent connection.

## Checklist

### 1. Enable on the Robinhood side
- [ ] Have a **primary individual investing account in good standing**.
- [ ] Enroll in the agentic-trading **beta** (**desktop device required** to open
      the Agentic account and authenticate the agent).
- [ ] Connect the MCP (below) — onboarding to create the **dedicated Agentic
      account** auto-opens after you connect.
- [ ] **Fund** the Agentic account with only risk capital. It's the only account
      the agent can trade; all other accounts stay read-only.

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
