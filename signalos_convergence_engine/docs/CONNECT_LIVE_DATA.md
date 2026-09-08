# Connect SignalOS to Live Market Data

## Recommended First Connection: Tradier

Use Tradier first because one API can provide:

- Stock historical OHLCV
- Option expirations
- Option chains
- Bid / ask / last
- Volume
- Open interest
- Greeks
- Implied volatility

This build adds:

```text
src/signalos/data_sources/tradier_provider.py
src/signalos/data_sources/validation.py
src/signalos/data_sources/secrets.py
scripts/fetch_tradier_data.py
data/live/
```

## Local / Codespaces Setup

Set your token:

```bash
export TRADIER_TOKEN="your_token_here"
```

Then run:

```bash
python scripts/fetch_tradier_data.py --scan
```

This writes:

```text
data/live/stock_daily.csv
data/live/option_chain_latest.csv
outputs/daily_signals_live.csv
```

Then run the phone dashboard:

```bash
streamlit run app/mobile_app.py
```

The mobile app automatically uses `data/live` if present. Otherwise, it falls back to demo data.

## Streamlit Cloud Setup

In Streamlit Cloud:

1. Open the app settings.
2. Go to **Secrets**.
3. Add:

```toml
TRADIER_TOKEN = "your_token_here"
```

For now, because Streamlit Community Cloud does not run scheduled jobs by default, the cleanest workflow is:

```text
Codespaces or local machine fetches data
→ data/live CSVs are updated
→ Streamlit app reads data/live
```

Later we can add a scheduled job on Render, Railway, or GitHub Actions.

## GitHub Codespaces Setup

Add `TRADIER_TOKEN` as a Codespaces secret.

Then inside Codespaces:

```bash
pip install -r requirements.txt
python scripts/fetch_tradier_data.py --scan
streamlit run app/mobile_app.py
```

## Important Limitation

This first Tradier connector is a **chain-snapshot connector**, not a full institutional UOA tape reader.

It gets volume, open interest, Greeks, IV, bid/ask, and expirations. But true ask-side/bid-side trade classification and repeated flow require intraday options prints. That is the next data upgrade.

## Next Data Upgrade

For higher-quality UOA:

```text
Databento OPRA / ORATS / Polygon options snapshots
```

That gives better options-flow reconstruction and historical options P&L backtesting.
