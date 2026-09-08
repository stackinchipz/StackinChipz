# Build SignalOS From Phone Only

This is possible, but the phone is not the compute environment. The phone controls cloud tools.

## Stack

```text
GitHub = code storage
GitHub Codespaces = cloud coding environment
Streamlit Cloud = app hosting
iPhone Safari = dashboard
thinkorswim mobile = execution
```

## Path A — Best Phone-Only Build

1. Download the SignalOS zip.
2. Create a GitHub repo named `signalos`.
3. Upload the zip contents to GitHub.
4. Open GitHub Codespaces from the repo.
5. Run:

```bash
pip install -r requirements.txt
python scripts/make_demo_data.py
python scripts/run_daily_scan.py --demo
streamlit run app/mobile_app.py
```

6. Deploy to Streamlit Cloud.
7. Add the Streamlit app to your iPhone home screen.

## Path B — Easier With Laptop Once

Use a laptop once to upload the repo and deploy Streamlit. After that, operate from phone.

## What To Avoid

- Do not try to make iPhone run the scanner locally.
- Do not use Shortcuts as the main engine.
- Do not make thinkorswim the entire system.
- Do not manually copy/paste option chains forever.

## Correct System

```text
Cloud computes.
Phone operates.
Broker executes.
Journal learns.
```
