---
title: "Building a Streamlit Validation Tool"
author: "Wes"
date: 2022-09-15

autoThumbnailImage: false
thumbnailImagePosition: "left"
thumbnailImage: https://res.cloudinary.com/wessport/image/upload/v1767000000/placeholder_thumb.png
coverImage: https://res.cloudinary.com/wessport/image/upload/v1767000000/placeholder_cover.jpg
metaAlignment: center
coverMeta: in
comments: true

keywords:
- Python
- Streamlit
- Data Validation
- Quality Assurance

categories:
- Python

tags:
- streamlit
- validation
- automation
---

*Automating quality checks for database updates with a self-service Streamlit app.*

<!--more-->

---

# The Problem #

Our team manages a location database used by several downstream services. We have quality triggers in place to catch issues during writes — things like duplicate locations, invalid coordinates, orphaned aliases, and broken geographic admin references.

The triggers worked, but few people on the team actually used them.

The friction was too high. Testing your data against the triggers required:

1. Downloading a large database dump
2. Setting up a local instance of MySQL
3. Manually applying 4 trigger SQL files
4. Running your update script and watching for errors

Most people skipped it and hoped for the best.

---

# The Solution: Reduce Friction #

I built a Streamlit app — LocDB Tools — that implements the same validation logic in Python, running against a read-only connection to the database. No local setup required. Upload your SQL file, click a button, get a report.

```python
def validate_coordinates(record: dict) -> list[str]:
    errors = []
    lat, lon = record.get('lat'), record.get('lon')
    
    if lat is not None and (lat < -90 or lat > 90):
        errors.append(f"Latitude {lat} out of valid range [-90, 90]")
    
    if lon is not None and (lon < -180 or lon > 180):
        errors.append(f"Longitude {lon} out of valid range [-180, 180]")
    
    return errors
```

The validator catches:

| Check | What It Catches |
|-------|-----------------|
| Coordinate bounds | Lat/lon outside valid ranges — dangerous to downstream services |
| Admin references | Country/admin1/admin2 that don't match parent records |
| Duplicates | Within the upload AND against existing prod data |
| Orphaned aliases | parent_id references pointing to nothing |

---

# Map Visualization #

The app includes an interactive map for spot-checking coordinate data. When you're dealing with hundreds of records, visual inspection catches things that raw numbers miss — like a cluster of points that should be in Texas but are sitting in the ocean.

```python
import folium
from streamlit_folium import st_folium

def create_validation_map(records: list[dict]) -> folium.Map:
    m = folium.Map(location=[39.8283, -98.5795], zoom_start=4)
    
    for record in records:
        color = 'red' if record.get('has_errors') else 'green'
        folium.CircleMarker(
            location=[record['lat'], record['lon']],
            radius=5,
            color=color,
            popup=record.get('name', 'Unknown')
        ).add_to(m)
    
    return m
```

The map uses color coding: green for records that pass validation, red for those that need attention.

---

# Admin Reference Validation #

The trickiest validation is checking that geographic hierarchies are intact. Every location needs valid parent references — a city should reference a real admin2, which references a real admin1, which references a real country.

```python
def validate_admin_references(record: dict, db_connection) -> list[str]:
    errors = []
    
    if record['country']:
        country_exists = db_connection.query(
            "SELECT 1 FROM location_table WHERE country=%s AND type='COUNTRY'",
            (record['country'],)
        )
        if not country_exists:
            errors.append(f"Country '{record['country']}' not found")
    
    if record['admin1']:
        admin1_exists = db_connection.query(
            """SELECT 1 FROM location_table 
               WHERE admin1=%s AND country=%s AND type='ADMIN1'""",
            (record['admin1'], record['country'])
        )
        if not admin1_exists:
            errors.append(f"Admin1 '{record['admin1']}' not found")
    
    return errors
```

Broken admin references cause cascading issues downstream. Jobs end up geocoding to the wrong place, or worse, failing to geocode at all.

---

# App Design Philosophy #

I designed the app with a few principles:

**Soliciting Feedback**: Added a sidebar introducing the app with sections for submitting feedback and contributing ideas via pull requests.

**Prioritized MVP**: Identified that the initial prototype met our requirements and could be developed further as needed. This allowed us to redirect focus to other incoming priorities while still having a functional tool.

**Self-Service**: The goal was reducing dependency on me or other senior team members. Anyone on the team could validate their data without scheduling a meeting.

---

# Results #

| Metric | Before | After |
|--------|--------|-------|
| Trigger validation usage | ~20% of updates | ~90% of updates |
| Time to validate | 30+ min setup | < 2 minutes |
| Issues caught pre-deploy | Variable | Consistent |

The biggest win was adoption. When validation is a one-click operation, people actually do it. The quality gates that already existed are now actually enforced.

---

# Supporting IN Location Updates #

The tool proved especially valuable when I stepped in to take ownership of India location database updates after a team member's departure. 

I quickly learned the project history and created a public wiki to provide QA guidance to international analysts when preparing data to add to LocDB. I also created a web map to help the India segmentation team see their location data in an interactive format to highlight and identify quality issues.

The combination of documentation and tooling enabled us to identify quality concerns with the neighborhood updates and require improvements before proceeding — a process that would have been much more difficult without the Streamlit validation layer.

---

# Lessons Learned #

The validation logic already existed. The problem was access. By wrapping the same checks in a user-friendly interface, we went from "I'll skip it this time" to "I'll just check it real quick."

Reducing friction is often more effective than adding features.
