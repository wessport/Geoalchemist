 Geocoding Credit Dashboard Demo
=================================

Public Dash/Plotly demo for a geocoding credit usage dashboard.

The app uses generated synthetic data only. It does not connect to internal data sources, include real vendor pricing, or expose operational metrics.

Local development:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Render free tier deployment:

- Runtime: Python 3
- Build command: `pip install -r requirements.txt`
- Start command: `gunicorn app:server`
- Root directory: `demos/geocoding-credit-dashboard`
