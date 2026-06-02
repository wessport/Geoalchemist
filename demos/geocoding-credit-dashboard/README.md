Geocoding Credit Dashboard
==========================

Dash/Plotly example for a geocoding credit usage dashboard.

The app uses generated sample data only. It does not connect to live data sources, include real pricing, or expose operational metrics.

Local development:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Render free tier deployment:

- Runtime: Python 3
- Python version: set by the repo-root `.python-version`
- Build command: `pip install -r requirements.txt`
- Start command: `gunicorn app:server`
- Root directory: `demos/geocoding-credit-dashboard`
