# Running SignalOS without a computer

You do **not** need a local machine to run the screen. GitHub Actions runners
have unrestricted internet, so they can reach Tradier, EDGAR, and Databento —
the exact hosts that cloud dev sandboxes block. Everything below is doable from
a phone browser.

## One-time setup (from your phone)

1. Open your repo on github.com → **Settings → Secrets and variables → Actions**
   → **New repository secret**. Add:

   | Secret | Required | Value |
   |---|---|---|
   | `TRADIER_TOKEN` | yes | your Tradier access token (start with **sandbox**) |
   | `TRADIER_ACCOUNT_ID` | yes | e.g. `VA########` |
   | `TRADIER_ENV` | no | `sandbox` (default) or `live` |
   | `EDGAR_USER_AGENT` | yes | `SignalOS research you@email.com` |
   | `DATABENTO_API_KEY` | no | enables real OPRA ask-side flow |

2. Go to the **Actions** tab → **Daily SignalOS Screen** → **Run workflow**.

That's it. The workflow runs `check_setup.py` first, so if a credential is wrong
you get a precise ✅/❌ report instead of a confusing failure.

## What you get, every weekday ~4:15pm ET

- **Job summary** — top setups rendered right on the run page (readable on mobile).
- **Artifacts** — `screen_signals.csv`, `agent_proposals.jsonl`,
  `options_backtest_*.csv`, downloadable from the phone.
- **`signalos-outputs` branch** — results committed each run, including the
  accumulating `iv_history.csv` so your **52-week IV rank sharpens over time**
  instead of resetting. (This is the main reason to let it run daily.)

Trigger it manually anytime with **Run workflow**; pass `preview: 5` to also get
Tradier order previews (still places nothing).

## What you cannot do from a phone

| Task | Why |
|---|---|
| **Robinhood agentic auth** | Robinhood requires a **desktop** to open the Agentic account and authorize an agent. No workaround — this is their restriction. |
| **Placing live orders via the agent** | Needs an authenticated broker session on a machine you control. |
| Interactive `claude mcp` / `/mcp` | Terminal + browser OAuth. |

So: **screening, backtesting, and proposals — phone is fine.** **Execution —
needs a desktop at least once.**

## Recommended sequence

1. Add the **sandbox** Tradier secrets → run the workflow → confirm real signals.
2. Let it run daily for a couple of weeks — builds IV history, and gives you a
   live sample to judge the edge (`options_backtest_comparison.csv` shows
   Flow-only vs Convergence vs Convergence+Fundamental).
3. Only then, on a desktop: connect a broker and start with tiny defined-risk
   size.

## Security notes

- GitHub Actions secrets are encrypted and not exposed in logs. Still, start
  with a **sandbox** token; only add a live token once you trust the flow.
- Rotate any token you've pasted into a chat, email, or screenshot.
- If your repo is public, secrets remain private — but **fork PRs cannot read
  them**, which is the intended protection.
