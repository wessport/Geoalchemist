---
title: "Regression Report Automation"
author: "Wes"
date: 2024-02-15

autoThumbnailImage: false
thumbnailImagePosition: "left"
thumbnailImage: https://res.cloudinary.com/wessport/image/upload/v1767000000/placeholder_thumb.png
coverImage: https://res.cloudinary.com/wessport/image/upload/v1767000000/placeholder_cover.jpg
metaAlignment: center
coverMeta: in
comments: true

keywords:
- Automation
- Python
- Slack
- DevOps
- Documentation

categories:
- Automation
- DevOps

tags:
- automation
- python
- slack
- documentation
---

*Reducing a multi-day setup process to 30 minutes and removing team bottlenecks.*

<!--more-->

---

# Results #

| Metric | Before | After |
|--------|--------|-------|
| Setup time | 2-3 days | **30 minutes** |
| People who could run reports | 1 | **Multiple team members** |
| Notification delay | Hours of checking | **Instant Slack alert** |
| Epics supported | N/A | **5 different epics, 24 regression reports** |

---

# The Problem #

Regression reports are essential for validating database changes. Before any bulk update to our location database goes live, we run regression tests to ensure geocoding behavior doesn't unexpectedly change.

The setup process was painful:

1. Configure test environment with proposed changes
2. Set up data sources and connections
3. Run comparison queries
4. Wait for results (hours)
5. Check back periodically to see if it's done
6. Process and format results for review

Steps 1-3 alone took multiple days of analyst time. The periodic checking was disruptive. And only one person on the team knew how to do it — creating a critical bottleneck.

---

# Automating Setup #

I developed a process to automate setting up regression reports, turning a multi-day process into a 30-minute one:

```python
import subprocess
import yaml
from pathlib import Path

def setup_regression_environment(config_path: str):
    """Configure regression test environment from YAML config."""
    
    config = yaml.safe_load(Path(config_path).read_text())
    
    # Set up database connections
    configure_db_connections(config['databases'])
    
    # Load proposed changes to test environment
    load_test_data(config['test_data_path'])
    
    # Configure comparison parameters
    set_comparison_config(config['comparison'])
    
    return RegressionRunner(config)
```

The YAML config file captures all the parameters that used to require manual configuration:

```yaml
databases:
  baseline: 
    host: prod-db.example.com
    database: locations
  test:
    host: test-db.example.com
    database: locations_proposed

test_data_path: /data/proposed_updates.sql

comparison:
  sample_size: 10000
  markets: [US, GB, DE]
  metrics: [geocode_precision, fallback_rate]
```

What took days now takes 30 minutes: edit the config, run the script, walk away.

---

# Slack Notifications #

The regression run takes hours. Checking periodically wastes time and mental energy.

Solution: Slack alerts to instantly auto-notify analysts when their regression report finishes running.

```python
import requests
from datetime import datetime

SLACK_WEBHOOK = os.environ['SLACK_WEBHOOK_URL']

def notify_completion(report_path: str, stats: dict):
    """Send Slack notification when regression report completes."""
    
    message = {
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "Regression Report Complete"
                }
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*Report:* {report_path}"},
                    {"type": "mrkdwn", "text": f"*Duration:* {stats['duration_min']:.1f} min"},
                    {"type": "mrkdwn", "text": f"*Records tested:* {stats['record_count']:,}"},
                    {"type": "mrkdwn", "text": f"*Regressions found:* {stats['regression_count']}"}
                ]
            }
        ]
    }
    
    requests.post(SLACK_WEBHOOK, json=message)
```

Now I start the report, go do other work, and get pinged when results are ready.

---

# Documentation as Multiplier #

Automation is only useful if people can run it. I created extensive resources:

**Setup guide**: Step-by-step instructions for new users

**Video walkthroughs**: A series of recorded walkthrough videos for how to set up regression reports

**Troubleshooting FAQ**: Solutions to errors people encounter

**Reference documentation**: Config file format, parameter descriptions

The documentation lives alongside the code in version control. When the automation changes, the docs get updated in the same commit.

---

# Training Sessions #

I ran 1-on-1 training sessions with team members who needed to run reports. I also led regression report training sessions for the broader team.

The format:

1. Explain the purpose (why we run regression reports)
2. Walk through the config file
3. Run an actual report together
4. Review results together
5. Practice troubleshooting common issues

After training, each person ran a report independently while I observed. By the end, they could operate without assistance. Multiple team members can now run regression reports, removing the bottleneck on location database updates.

---

# Impact: Supporting Critical Work #

The automation supported **5 different epics** across the team (including Postal Code Coverage initiatives), **24 regression reports**, and enabled rapid iteration on database updates.

Specific examples:

- **DE Admin cleanup**: Helped guide strategy, diagnose regression issues, and suggest actionable solutions to unstick the project
- **CA Precise Postals**: Helped measure impact of change, resulting in a 23% gain in enhancement
- **JP Collator testing**: Supported high-priority collator testing by setting up and running a custom regression report incorporating experimental code
- **Testing Remote removal**: Ran regression reports for Remote removal and recommended global testing to avoid potential issues

---

# Code Structure #

The automation organized into clear modules:

```
regression_reports/
├── config/
│   ├── us_update.yaml
│   ├── gb_postal.yaml
│   └── template.yaml
├── src/
│   ├── setup.py          # Environment configuration
│   ├── runner.py         # Report execution
│   ├── notify.py         # Slack integration
│   └── report.py         # Result formatting
├── docs/
│   ├── setup_guide.md
│   ├── troubleshooting.md
│   └── videos/
└── run_regression.py     # Main entry point
```

---

# Error Handling #

Common failure modes and how the automation handles them:

**Database connection fails:**
```python
def configure_db_connections(db_config: dict):
    for name, config in db_config.items():
        try:
            conn = connect(config)
            conn.execute("SELECT 1")
        except Exception as e:
            raise SetupError(f"Cannot connect to {name}: {e}")
```

Clear error messages pointing to the problem, not generic stack traces.

**Long-running report times out:**
```python
def run_regression(env, timeout_hours: int = 8):
    start = time.time()
    
    while not env.is_complete():
        if (time.time() - start) > timeout_hours * 3600:
            notify_timeout(env)
            raise TimeoutError(f"Report exceeded {timeout_hours} hour limit")
        time.sleep(60)
```

Timeout alert goes to Slack so someone can investigate.

---

# Lessons #

**Automate the setup, not just the execution.** The report itself always ran automatically. The bottleneck was everything required to start it.

**Notifications beat polling.** Checking back every hour is disruptive. Push notifications let you context-switch cleanly.

**Documentation compounds.** Time spent on guides and videos pays off every time someone new needs to run a report. Training takes an hour instead of a day.

**Build for handoff.** Single points of failure are organizational risks. Multiple people should be able to run any critical process.
