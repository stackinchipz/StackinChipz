# SignalOS iPhone Quickstart

## Practical Architecture

Your iPhone should operate the system. It should not run the Python engine directly.

```text
Cloud runs SignalOS
iPhone opens the dashboard
thinkorswim executes trades
GitHub stores the code
```

## What You Use On Phone

1. **SignalOS mobile dashboard**
   - Review A+ setups
   - Review tradable setups
   - Review rejected UOA
   - Drill into ticker details
   - Download daily CSV

2. **thinkorswim mobile**
   - Confirm option chain
   - Check bid/ask
   - Place limit orders
   - Monitor positions

3. **GitHub mobile/browser**
   - Store project
   - Update docs
   - Create issues

## Best Setup

### Step 1 — Create GitHub repo

Create a repo named:

```text
signalos
```

Upload the project files.

### Step 2 — Deploy to Streamlit Community Cloud

Use this as the app entry file:

```text
app/mobile_app.py
```

### Step 3 — Open the Streamlit URL on iPhone

Open the deployed app URL in Safari.

Then:

```text
Share → Add to Home Screen
```

Now SignalOS behaves like an app icon on your phone.

## Daily Phone Workflow

### Morning

1. Open SignalOS from your iPhone home screen.
2. Tap **Trade**.
3. Review confirmed setups.
4. Tap **Rejected** and see what the model blocked.
5. Choose at most 1–3 names to inspect.

### Execution

1. Open thinkorswim mobile.
2. Search ticker.
3. Open option chain.
4. Confirm:
   - DTE
   - delta
   - volume
   - open interest
   - bid/ask spread
5. Use a limit order only.
6. Use defined-risk structure only.

### After Trade

1. Save screenshot.
2. Log thesis.
3. Log max risk.
4. Log exit plan.
5. Review later.

## Phone Operating Rule

Do not chase alerts.

SignalOS gives you candidates. thinkorswim gives you execution. You make the decision.
