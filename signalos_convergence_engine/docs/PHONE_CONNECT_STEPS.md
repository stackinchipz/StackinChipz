# Phone Connection Steps

## Objective

Use SignalOS from your phone with live data.

## Step 1 — Get Tradier API Token

1. Open Tradier.
2. Create or log into your brokerage/developer account.
3. Go to API settings.
4. Copy your live or sandbox API token.

## Step 2 — Store Token

### For GitHub Codespaces

Add a Codespaces secret:

```text
TRADIER_TOKEN
```

### For Streamlit Cloud

Open app settings → Secrets and paste:

```toml
TRADIER_TOKEN = "your_token_here"
```

Never commit the token to GitHub.

## Step 3 — Fetch Data

In Codespaces terminal:

```bash
pip install -r requirements.txt
python scripts/fetch_tradier_data.py --scan
```

## Step 4 — Open Mobile Dashboard

```bash
streamlit run app/mobile_app.py
```

Or deploy `app/mobile_app.py` on Streamlit Cloud.

## Step 5 — Use From iPhone

1. Open Streamlit URL in Safari.
2. Share → Add to Home Screen.
3. Open SignalOS.
4. Tap Trade / Watchlist / Rejected.
5. Execute manually in thinkorswim.

## Current State

This connector gives us the first live scanner. It is not yet a full tick-by-tick UOA engine.
