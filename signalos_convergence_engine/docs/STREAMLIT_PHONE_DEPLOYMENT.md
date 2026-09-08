# Deploy SignalOS Mobile Dashboard

## Goal

Deploy SignalOS so it can be opened from an iPhone as a private web app.

## Recommended Entry File

```text
app/mobile_app.py
```

## Streamlit Cloud Steps

1. Push this repo to GitHub.
2. Go to Streamlit Community Cloud.
3. Click **Create app**.
4. Select the GitHub repo.
5. Select branch:

```text
main
```

6. Main file path:

```text
app/mobile_app.py
```

7. Click **Deploy**.
8. Open the generated `streamlit.app` URL on your phone.
9. In Safari, tap:

```text
Share → Add to Home Screen
```

## Secrets

When API keys are added later, do not commit them to GitHub.

Use Streamlit secrets.

Example:

```toml
TRADIER_TOKEN = "..."
POLYGON_API_KEY = "..."
DATABENTO_API_KEY = "..."
```

## Current Demo Mode

The current mobile app uses demo data:

```text
data/demo/stock_daily.csv
data/demo/option_chain_latest.csv
```

Once real data is integrated, the same dashboard will show real daily signals.

## Local Test

```bash
streamlit run app/mobile_app.py
```

## iPhone UX

The mobile app uses card-based views because iPhone tables are hard to read.

Views:

- Trade
- Watchlist
- Rejected
- Drilldown
- Backtest
