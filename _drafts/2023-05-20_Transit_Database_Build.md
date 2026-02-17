---
title: "Building a Transit Database from Scratch"
author: "Wes"
date: 2023-05-20

autoThumbnailImage: false
thumbnailImagePosition: "left"
thumbnailImage: https://res.cloudinary.com/wessport/image/upload/v1767000000/placeholder_thumb.png
coverImage: https://res.cloudinary.com/wessport/image/upload/v1767000000/placeholder_cover.jpg
metaAlignment: center
coverMeta: in
comments: true

keywords:
- Data Engineering
- ETL
- Python
- Spatial Data
- Transit

categories:
- Data Engineering
- Python

tags:
- etl
- databases
- spatial-data
- python
---

*Building data infrastructure for transit search across three markets in a tight timeline.*

<!--more-->

---

# Results #

| Metric | Value |
|--------|-------|
| **Total Stations** | ~430,000 records across 3 markets |
| **Transit Lines** | 773 lines |
| **Transit Companies** | 193 companies |
| **ETL Pipeline** | 1,254 lines of code |
| **Commits** | 41 commits across 3 merge requests |
| **Deadline** | February 1st — met with margin |

---

# The Problem #

We needed a transit database to support station-based job search across the US, Germany, and Japan. The challenge: no unified data source existed. Each market had different data providers, formats, and quality levels.

The deadline was tight — February 1st. The platform team needed the data in weeks, not months. I took the technical lead on building out the entire transit database, prioritizing this work over other initiatives to meet the deadline.

---

# Scale of the Build #

Final database stats:

| Market | Stations | Lines | Companies |
|--------|----------|-------|-----------|
| US | ~419,000 | - | - |
| DE | ~5,000 | 400+ | 50+ |
| JP | ~9,000 | 373 | 143 |
| **Total** | **~430,000** | **773** | **193** |

This wasn't just loading CSVs into a database. The data required significant transformation, deduplication, and validation before it could serve production queries.

---

# Data Sources #

Japan was the most complex. Four separate datasets needed to be combined:

1. Official station registry (Eki data)
2. Line and route data
3. Company ownership information
4. Coordinate and naming data

Each dataset used different identifiers and had overlapping but inconsistent information. A station might appear in multiple datasets with slightly different names, different coordinate precision, or conflicting company assignments.

I also built web scrapers to collect location hierarchies and complex transit hierarchies directly from source websites, creating datasets that didn't exist in any centralized form.

---

# ETL Pipeline Architecture #

I built a Python ETL pipeline to handle the transformation. Final stats: **1,254 lines of code**, **41 commits** across **3 merge requests**.

The pipeline followed a standard pattern:

```
Extract (source CSVs/APIs)
    ↓
Transform (normalize, deduplicate, validate)
    ↓
Load (generate SQL insert statements)
```

For Japan specifically:

```python
# Pseudocode structure
def process_japan_transit():
    # 1. Load all four source datasets
    eki_stations = load_eki_data()
    line_data = load_line_data()
    company_data = load_company_data()
    coord_data = load_coordinate_data()
    
    # 2. Create unified station records
    stations = merge_datasets(eki_stations, coord_data)
    
    # 3. Resolve duplicates using spatial matching
    stations = deduplicate_by_proximity(stations, threshold_meters=200)
    
    # 4. Validate relationships
    validate_station_line_relationships(stations, line_data)
    
    # 5. Generate SQL
    generate_insert_statements(stations, line_data, company_data)
```

---

# Spatial Deduplication #

The deduplication logic used nearest-neighbor spatial joins. Two records within 200 meters were candidate duplicates.

The algorithm:

1. Build a spatial index of all station coordinates
2. For each station, find neighbors within threshold distance
3. Compare names using fuzzy matching
4. Flag matches for review or auto-merge based on confidence score

This reduced manual review from 1,000+ records to approximately 250 — the ambiguous cases where automation couldn't make a confident call.

```python
from scipy.spatial import cKDTree
import numpy as np

def find_nearby_stations(stations, threshold_m=200):
    # Convert lat/lon to approximate meters
    coords = np.array([[s.lat, s.lon * cos(radians(s.lat))] for s in stations])
    coords_m = coords * 111000  # rough degree-to-meter conversion
    
    tree = cKDTree(coords_m)
    pairs = tree.query_pairs(r=threshold_m)
    
    return pairs
```

The result: **reduced work from 1,000+ records (a week+ of manual review) to only ~250 records (one day of work)** while meeting our tight February 1st deadline.

---

# Administrative Data Enrichment #

Stakeholders later requested that each JP station include administrative region information from our location database. Manually looking this up for 9,000 stations wasn't feasible.

The solution: join each incoming station to its nearest existing station record in our database, then copy the admin fields.

Stations under 200 meters from a known location were auto-joined. Anything beyond that went to manual review. This approach handled ~95% of records automatically.

---

# Validation Layer #

Before generating SQL, the pipeline validated:

- **Referential integrity**: Every station references a valid line; every line references a valid company
- **Coordinate validity**: All coordinates fall within expected bounding boxes for the market
- **Name quality**: No empty names, no invalid characters
- **Duplicate detection**: No duplicate station IDs

Validation failures blocked SQL generation and produced detailed error reports. Local testing detected and removed duplicate stations before they were applied in production.

---

# SQL Generation #

The pipeline generated SQL files rather than directly executing database operations. This provided:

1. **Audit trail**: Every change documented in version control
2. **Review step**: Human approval before execution
3. **Rollback capability**: Clear record of what was inserted

Example output:

```sql
-- Generated by transit-etl pipeline
-- Market: JP
-- Stations: 9,247
-- Generated: 2023-01-15T14:32:00Z

INSERT INTO transit_stations (id, name, lat, lon, line_id, company_id) 
VALUES 
  ('JP-001', 'Shibuya', 35.6580, 139.7016, 'LINE-001', 'COMP-001'),
  ('JP-002', 'Shinjuku', 35.6896, 139.7006, 'LINE-001', 'COMP-001'),
  -- ... 9,245 more rows
```

---

# Documentation and Process #

I also created documentation to enable the team to maintain the data independently:

- **ERD visualization** of the database structure to help team members understand the transit schema
- **Technical guide** on setting up and testing the TransitDB locally
- **Process documentation** for applying TransitDB changes

This enabled the data team to fully support transit update requests with minimal oversight going forward.

---

# Meeting the Deadline #

The tight deadline required strategic tradeoffs:

- **Prioritized automation over perfection**: Accepted 95% automated matching rather than 100%
- **Batched manual review**: Grouped similar edge cases for efficient human review
- **Parallel processing**: Built the pipeline to process each market independently
- **Advocated for pragmatism**: Pushed to move forward with US transit data despite missing line data to meet the deadline

We delivered on time. The transit database went live supporting station-based search across all three markets.

---

# Lessons Learned #

**Invest in the pipeline, not manual fixes.** It was tempting to manually fix data issues as they appeared. Investing that time in automation paid off when we needed to reprocess data after upstream corrections.

**Spatial operations are expensive.** The nearest-neighbor joins were the slowest part of the pipeline. Building proper spatial indexes up front saved significant processing time.

**Generate SQL, don't execute directly.** Having a reviewable artifact before database changes caught several issues that would have been painful to fix in production.

---

# Outcome #

The transit database now serves production queries for job search across three markets. The ETL pipeline remains in use for ongoing updates — when source data changes, we rerun the pipeline rather than manually editing records.

The data unlocked support for transit search for a major platformization initiative as well as ongoing transit display tests.

Total development time: approximately 3 weeks from blank slate to production data.
