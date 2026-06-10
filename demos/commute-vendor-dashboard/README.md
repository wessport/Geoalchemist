Commute Vendor Dashboard
========================

Dash/Plotly example for comparing commute time estimates across routing providers.

The app uses generated sample data only. It does not connect to private data sources, include real operational metrics, or expose internal service details.

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
- Root directory: `demos/commute-vendor-dashboard`
