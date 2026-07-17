# Setup & Login — from zero to running

Do this on your **local machine** (not a cloud sandbox — that's where broker
tokens must never live).

## 0. Get the code
```bash
git clone <your StackinChipz repo URL>
cd StackinChipz
git checkout claude/robin-hood-agents-nYZYe
cd signalos_convergence_engine
```

## 1. Python environment
```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## 2. Smoke test — no login needed
```bash
python scripts/make_demo_data.py
python scripts/run_screen.py --demo
python scripts/run_options_backtest.py --signals outputs/screen_signals.csv
python scripts/run_agent.py --signals outputs/screen_signals.csv
pytest -q                          # 56 tests should pass
```
If that works, the engine is healthy and you only need credentials for *live*
data + execution.

## 3. Logins / credentials

### A. Tradier — market data, option chains, AND options execution
1. **Sandbox first (paper):** sign up at **developer.tradier.com** → your
   sandbox account shows an **Access Token** and an **Account ID** (e.g. `VA########`).
2. **Live later:** open/fund a **Tradier Brokerage** account at tradier.com, then
   **dashboard.tradier.com → Settings → API Access** → create a production token.
   Your account number is your `TRADIER_ACCOUNT_ID`.
3. **Options approval:** to place debit/credit spreads you need **spreads-level
   options approval** on the account (typically level 2–3). Request it in Tradier.

### B. SEC EDGAR — free fundamentals
No login. Just set `EDGAR_USER_AGENT` to a descriptive string with your email
(SEC requires it). Nothing to authenticate.

### C. Robinhood agentic — equity execution (optional, equities-only beta)
1. Have a **primary Robinhood investing account in good standing**; use a
   **desktop** device.
2. Connect the MCP in **local Claude Code**:
   ```bash
   claude mcp add robinhood-trading --transport http https://agent.robinhood.com/mcp/trading
   ```
3. In Claude Code: `/mcp` → select **robinhood-trading** → **authenticate**
   (OAuth in your browser — your agent never sees your password).
4. Onboarding auto-opens: create + **fund the dedicated Agentic account**. That's
   the only account the agent can trade.

## 4. Store credentials
```bash
cp .env.example .env
# edit .env: TRADIER_TOKEN, TRADIER_ACCOUNT_ID, TRADIER_ENV=sandbox, EDGAR_USER_AGENT
```
`.env` is gitignored — never commit it. Load it into your shell:
```bash
set -a; source .env; set +a
```

## 5. Run on live data
```bash
# Live screen with free EDGAR fundamentals:
python scripts/run_screen.py \
  --stock-daily data/live/stock_daily.csv \
  --option-chain data/live/option_chain_latest.csv \
  --fundamentals-provider edgar --edgar-ua "$EDGAR_USER_AGENT"

# (Fetch data/live/*.csv from Tradier first — see scripts/fetch_tradier_data.py.)
python scripts/run_options_backtest.py --signals outputs/screen_signals.csv
python scripts/update_iv_history.py --option-chain data/live/option_chain_latest.csv
```

## 6. Execute options (Tradier) — preview then place
```python
from signalos.agent import TradierBroker, build_proposals
from signalos.pipeline_screen import size_screen
import os, pandas as pd

signals = pd.read_csv("outputs/screen_signals.csv")
props = build_proposals(size_screen(signals))

broker = TradierBroker(
    token=os.environ["TRADIER_TOKEN"],
    account_id=os.environ["TRADIER_ACCOUNT_ID"],
    sandbox=os.environ.get("TRADIER_ENV", "sandbox") == "sandbox",
    armed=True,
)
for p in [x.to_dict() for x in props if x.contracts > 0]:
    p["limit_price"] = ...              # net debit/credit or single-leg limit
    print(broker.preview(p))            # cost/margin/warnings — sends nothing
    # broker.submit(p)                  # places once you're satisfied
```

## Order of operations (don't skip)
1. Demo works → 2. Sandbox Tradier data + backtest → 3. Sandbox paper orders
(preview → submit) → 4. Live token, tiny size → 5. scale. Risk caps enforced
throughout (`docs/RISK_ENGINE.md`).
