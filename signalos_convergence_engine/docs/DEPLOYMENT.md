# SignalOS Deployment Plan

## Goal

Use SignalOS from an iPhone.

## Option 1: Streamlit Cloud

Best first deployment.

Steps:

1. Create GitHub repo.
2. Upload this project.
3. Create Streamlit Cloud account.
4. Connect GitHub repo.
5. Set main file:

```text
app/streamlit_app.py
```

6. Add secrets if using APIs.
7. Deploy.
8. Open private app URL from phone.

## Option 2: Render / Railway

Better if the app needs scheduled jobs or background workers.

## Option 3: Local Laptop + Phone Browser

Run locally:

```bash
streamlit run app/streamlit_app.py
```

Then access from phone on same Wi-Fi using local IP.

## Recommended

Start with Streamlit Cloud for the dashboard. Move to Render/Railway when adding scheduled ingestion and alerts.
