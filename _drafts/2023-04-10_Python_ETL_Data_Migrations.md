---
title: "Python ETL for Complex Data Migrations"
author: "Wes"
date: 2023-04-10

autoThumbnailImage: false
thumbnailImagePosition: "left"
thumbnailImage: https://res.cloudinary.com/wessport/image/upload/v1767000000/placeholder_thumb.png
coverImage: https://res.cloudinary.com/wessport/image/upload/v1767000000/placeholder_cover.jpg
metaAlignment: center
coverMeta: in
comments: true

keywords:
- Python
- ETL
- Data Engineering
- SQL
- Automation

categories:
- Data Engineering
- Python

tags:
- etl
- python
- data-pipelines
- sql
---

*Patterns and practices from building production ETL pipelines.*

<!--more-->

---

# Why Custom ETL #

Off-the-shelf ETL tools work well for straightforward transformations. They struggle with:

- Complex business logic that doesn't fit standard transformations
- Multi-source data that requires custom deduplication
- Validation rules specific to your domain
- SQL generation where you need reviewable output before execution

For these cases, Python provides the flexibility to build exactly what you need.

Over the past year, I've built several ETL pipelines for location data migrations — transit databases, location hierarchies, postal code updates. These patterns emerged from that work.

---

# Pipeline Structure #

A well-structured ETL pipeline follows a predictable pattern:

```
┌─────────────────────────────────────────────────────────────┐
│  EXTRACT                                                     │
│  - Load source data (CSV, API, database)                    │
│  - Parse into consistent internal structures                │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  TRANSFORM                                                   │
│  - Clean and normalize                                      │
│  - Deduplicate                                              │
│  - Enrich with external data                                │
│  - Validate against business rules                          │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  LOAD                                                        │
│  - Generate SQL statements                                  │
│  - Write to staging tables or files                         │
│  - Execute with transaction safety                          │
└─────────────────────────────────────────────────────────────┘
```

The key is keeping each stage independent. Extract shouldn't care about transform logic; transform shouldn't know about the target database schema.

---

# Data Classes for Structure #

Python dataclasses provide clean internal representations:

```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class StationRecord:
    source_id: str
    name: str
    lat: float
    lon: float
    line_id: Optional[str] = None
    company_id: Optional[str] = None
    
    def is_valid(self) -> bool:
        return (
            self.name.strip() != '' and
            -90 <= self.lat <= 90 and
            -180 <= self.lon <= 180
        )
```

This approach catches type errors early and makes the code self-documenting.

---

# Multi-Source Extraction #

When combining multiple data sources, standardize early. For a transit database build, I had to merge four separate Japan datasets — station registry, line data, company ownership, and coordinates:

```python
def extract_source_a(filepath: str) -> list[StationRecord]:
    """Extract from Source A CSV format."""
    records = []
    with open(filepath) as f:
        reader = csv.DictReader(f)
        for row in reader:
            records.append(StationRecord(
                source_id=f"A-{row['id']}",
                name=row['station_name'],
                lat=float(row['latitude']),
                lon=float(row['longitude'])
            ))
    return records

def extract_source_b(api_url: str) -> list[StationRecord]:
    """Extract from Source B API."""
    response = requests.get(api_url)
    data = response.json()
    
    records = []
    for item in data['stations']:
        records.append(StationRecord(
            source_id=f"B-{item['stationCode']}",
            name=item['displayName'],
            lat=item['coords']['lat'],
            lon=item['coords']['lng']
        ))
    return records
```

By returning the same type from both extractors, the transform stage doesn't need to know where the data came from.

---

# Deduplication Strategies #

Duplicates are inevitable when combining sources. Common approaches:

**Exact match**: Records match on a key field

```python
def dedupe_exact(records: list[StationRecord]) -> list[StationRecord]:
    seen = {}
    for r in records:
        key = r.name.lower().strip()
        if key not in seen:
            seen[key] = r
    return list(seen.values())
```

**Fuzzy match**: Records match based on similarity threshold

```python
from rapidfuzz import fuzz

def dedupe_fuzzy(records: list[StationRecord], threshold: int = 85) -> list[StationRecord]:
    unique = []
    for r in records:
        is_dupe = False
        for existing in unique:
            if fuzz.ratio(r.name, existing.name) >= threshold:
                is_dupe = True
                break
        if not is_dupe:
            unique.append(r)
    return unique
```

**Spatial match**: Records match based on proximity

```python
from scipy.spatial import cKDTree

def dedupe_spatial(records: list[StationRecord], threshold_m: float = 200) -> list[StationRecord]:
    coords = np.array([[r.lat * 111000, r.lon * 111000 * cos(radians(r.lat))] 
                       for r in records])
    tree = cKDTree(coords)
    
    # Find pairs within threshold
    pairs = tree.query_pairs(r=threshold_m)
    
    # Mark duplicates (keep first occurrence)
    to_remove = set()
    for i, j in pairs:
        to_remove.add(j)
    
    return [r for i, r in enumerate(records) if i not in to_remove]
```

Choose based on your data. Often you'll combine approaches — exact match first, then spatial for remaining ambiguous cases. For a transit database project, spatial matching reduced manual review from 1,000+ records to approximately 250.

---

# Validation as a Pipeline Stage #

Build validation as an explicit step that can halt processing:

```python
@dataclass
class ValidationResult:
    is_valid: bool
    errors: list[str]

def validate_records(records: list[StationRecord]) -> ValidationResult:
    errors = []
    
    for i, r in enumerate(records):
        if not r.is_valid():
            errors.append(f"Record {i}: invalid coordinates or empty name")
        
        if r.line_id and not line_exists(r.line_id):
            errors.append(f"Record {i}: references unknown line {r.line_id}")
    
    # Check for duplicate IDs
    ids = [r.source_id for r in records]
    duplicates = [id for id in ids if ids.count(id) > 1]
    if duplicates:
        errors.append(f"Duplicate IDs found: {set(duplicates)}")
    
    return ValidationResult(
        is_valid=len(errors) == 0,
        errors=errors
    )
```

If validation fails, stop processing and report errors rather than generating invalid SQL.

---

# SQL Generation #

Generate SQL as strings rather than executing directly. This provides a review step:

```python
def generate_insert_sql(records: list[StationRecord], table: str) -> str:
    lines = [
        f"-- Generated: {datetime.now().isoformat()}",
        f"-- Record count: {len(records)}",
        "",
        f"INSERT INTO {table} (source_id, name, lat, lon, line_id, company_id) VALUES"
    ]
    
    values = []
    for r in records:
        line_id = f"'{r.line_id}'" if r.line_id else "NULL"
        company_id = f"'{r.company_id}'" if r.company_id else "NULL"
        values.append(
            f"  ('{escape(r.source_id)}', '{escape(r.name)}', "
            f"{r.lat}, {r.lon}, {line_id}, {company_id})"
        )
    
    lines.append(",\n".join(values) + ";")
    return "\n".join(lines)

def escape(s: str) -> str:
    return s.replace("'", "''")
```

Write the SQL to a file, review it, then execute. For large migrations, this catches issues before they hit production.

---

# Enrichment via Spatial Joins #

For a Japan transit database update, stakeholders requested administrative region information for each station. Manually looking this up for 9,000 stations wasn't feasible.

The solution: nearest-neighbor spatial joins to enrich incoming data with existing database records:

```python
def enrich_with_admin_data(stations: list[StationRecord], 
                            locdb_stations: list[dict],
                            threshold_m: float = 200) -> list[StationRecord]:
    # Build spatial index of LocDB stations
    locdb_coords = np.array([[s['lat'] * 111000, s['lon'] * 111000 * cos(radians(s['lat']))] 
                             for s in locdb_stations])
    tree = cKDTree(locdb_coords)
    
    for station in stations:
        station_coord = [station.lat * 111000, station.lon * 111000 * cos(radians(station.lat))]
        dist, idx = tree.query(station_coord)
        
        if dist <= threshold_m:
            # Auto-join: copy admin fields
            station.admin1 = locdb_stations[idx]['admin1']
            station.admin2 = locdb_stations[idx]['admin2']
        else:
            # Flag for manual review
            station.needs_review = True
    
    return stations
```

This approach handled ~95% of records automatically, with only the ambiguous cases requiring human review.

---

# Error Handling #

ETL pipelines fail. Plan for it:

```python
def run_pipeline(config: PipelineConfig) -> PipelineResult:
    try:
        # Extract
        records = []
        for source in config.sources:
            records.extend(extract(source))
        
        # Transform
        records = transform(records, config.transform_rules)
        
        # Validate
        validation = validate_records(records)
        if not validation.is_valid:
            return PipelineResult(
                success=False,
                errors=validation.errors,
                output_file=None
            )
        
        # Load
        sql = generate_insert_sql(records, config.target_table)
        output_path = config.output_dir / f"migration_{datetime.now():%Y%m%d}.sql"
        output_path.write_text(sql)
        
        return PipelineResult(
            success=True,
            errors=[],
            output_file=output_path
        )
        
    except Exception as e:
        return PipelineResult(
            success=False,
            errors=[f"Pipeline failed: {str(e)}"],
            output_file=None
        )
```

Return structured results rather than raising exceptions. This makes it easier to log, retry, or report failures.

---

# Logging #

Visibility into pipeline execution matters for debugging:

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def run_pipeline(config):
    logger.info(f"Starting pipeline with {len(config.sources)} sources")
    
    records = extract_all(config.sources)
    logger.info(f"Extracted {len(records)} records")
    
    records = transform(records)
    logger.info(f"After transform: {len(records)} records")
    
    validation = validate(records)
    if not validation.is_valid:
        logger.error(f"Validation failed: {validation.errors}")
        return
    
    # ... continue
```

When something goes wrong, good logs tell you where and why.

---

# Testing ETL Code #

Test each stage independently:

```python
def test_extract_handles_empty_file():
    records = extract_source_a("tests/fixtures/empty.csv")
    assert records == []

def test_dedupe_removes_exact_duplicates():
    records = [
        StationRecord("1", "Tokyo", 35.6, 139.7),
        StationRecord("2", "tokyo", 35.6, 139.7),  # dupe
        StationRecord("3", "Osaka", 34.6, 135.5),
    ]
    result = dedupe_exact(records)
    assert len(result) == 2

def test_validation_catches_invalid_coords():
    records = [StationRecord("1", "Bad Station", 999, 999)]
    result = validate_records(records)
    assert not result.is_valid
```

Use fixtures with known data for predictable test cases.

---

# Putting It Together #

A production pipeline combining these patterns:

```python
def main():
    config = load_config("config.yaml")
    
    # Extract
    records = []
    for source in config.sources:
        records.extend(extract(source))
    logger.info(f"Extracted {len(records)} total records")
    
    # Transform
    records = normalize_names(records)
    records = dedupe_spatial(records, threshold_m=200)
    records = enrich_with_admin_data(records)
    logger.info(f"After transforms: {len(records)} records")
    
    # Validate
    result = validate_records(records)
    if not result.is_valid:
        for error in result.errors:
            logger.error(error)
        sys.exit(1)
    
    # Generate SQL
    sql = generate_insert_sql(records, config.target_table)
    output_path = Path(f"output/migration_{date.today()}.sql")
    output_path.write_text(sql)
    
    logger.info(f"Generated {output_path}")
```

Clear stages, structured data, validation gates, reviewable output.
