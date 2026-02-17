---
title: "Designing an MSA Database Schema"
author: "Wes"
date: 2024-05-15

autoThumbnailImage: false
thumbnailImagePosition: "left"
thumbnailImage: https://res.cloudinary.com/wessport/image/upload/v1767000000/placeholder_thumb.png
coverImage: https://res.cloudinary.com/wessport/image/upload/v1767000000/placeholder_cover.jpg
metaAlignment: center
coverMeta: in
comments: true

keywords:
- SQL
- Database Design
- Data Architecture
- Migrations

categories:
- Data Engineering
- SQL

tags:
- sql
- database-design
- migrations
- data-architecture
---

*Building a database schema for Metropolitan Statistical Area data that unblocked two engineering epics.*

<!--more-->

---

# Results #

| Metric | Value |
|--------|-------|
| **SQL Migration Files** | 13 files |
| **New MSAs** | 50 records inserted |
| **Updated MSAs** | 619 records updated |
| **Soft-Deleted MSAs** | 47 obsolete records |
| **Engineering Epics Unblocked** | 2 |

---

# The Problem #

Metropolitan Statistical Areas (MSAs) are geographic regions defined by the US Census Bureau. Many downstream services needed this data — market analysis, job distribution reporting, regional segmentation.

The existing approach: teams maintained their own CSV files. No single source of truth. Data freshness varied. Some teams used 2015 definitions; others had partially updated to 2020.

This fragmentation was blocking engineering work. Two separate epics were waiting on reliable MSA data:
- A lat/lon-to-MSA service for index builders
- Decommissioning MSA data from an older Location Matcher service

I independently designed a new sophisticated database schema to solve this problem.

---

# Schema Design #

The core table needed to support:

- Current MSA definitions
- Historical records (for trend analysis)
- Soft deletes (Census removes/redefines MSAs periodically)
- Audit trail (when did each record change?)

```sql
CREATE TABLE msa_admin (
    id SERIAL PRIMARY KEY,
    msa_code VARCHAR(5) NOT NULL,
    msa_name VARCHAR(255) NOT NULL,
    state_fips VARCHAR(2),
    county_fips VARCHAR(3),
    central_city VARCHAR(255),
    population INTEGER,
    
    -- Audit fields
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP DEFAULT NULL,
    
    -- Unique constraint on active records
    CONSTRAINT unique_active_msa 
        UNIQUE (msa_code, county_fips) 
        WHERE deleted_at IS NULL
);

CREATE INDEX idx_msa_code ON msa_admin(msa_code) WHERE deleted_at IS NULL;
CREATE INDEX idx_state_fips ON msa_admin(state_fips) WHERE deleted_at IS NULL;
```

The `deleted_at` field enables soft deletes. Queries filter on `WHERE deleted_at IS NULL` to get current data, but historical analysis can access everything. This anticipated a request from stakeholders who needed historical data for analysis.

---

# Automatic Timestamps #

I created SQL triggers within the geospatial database to automatically update the table with timestamps when records are inserted or updated:

```sql
CREATE OR REPLACE FUNCTION update_modified_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_msa_admin_modtime
    BEFORE UPDATE ON msa_admin
    FOR EACH ROW
    EXECUTE FUNCTION update_modified_column();
```

With this trigger, engineers don't need to remember to set `updated_at` — it happens automatically on any UPDATE. This increased team efficiency of data updates and enables data freshness tracking for downstream consumers.

---

# Migration Files #

I created **13 SQL migration files** to populate the initial data and bring the MSA data up to date with the latest US Census Bureau definitions:

| File | Purpose | Records |
|------|---------|---------|
| 001_create_msa_admin.sql | Table creation | - |
| 002_create_triggers.sql | Timestamp triggers | - |
| 003_insert_new_msas.sql | New MSA definitions | 50 |
| 004-012_update_existing.sql | Updated definitions | 619 |
| 013_soft_delete_obsolete.sql | Removed MSAs | 47 |

Each migration is idempotent where possible:

```sql
-- 003_insert_new_msas.sql
INSERT INTO msa_admin (msa_code, msa_name, state_fips, county_fips, population)
SELECT '12345', 'Example Metro', 'TX', '123', 500000
WHERE NOT EXISTS (
    SELECT 1 FROM msa_admin 
    WHERE msa_code = '12345' AND county_fips = '123' AND deleted_at IS NULL
);
```

Idempotent migrations can be re-run safely if something goes wrong mid-deployment.

---

# Soft Delete Implementation #

When the Census Bureau removes or redefines an MSA, we don't delete the record:

```sql
-- 013_soft_delete_obsolete.sql
UPDATE msa_admin
SET deleted_at = CURRENT_TIMESTAMP
WHERE msa_code IN ('12060', '14460', /* ... 45 more */)
  AND deleted_at IS NULL;
```

This preserves data for historical analysis. A query like "how many jobs were in the Austin MSA in 2019?" still works even if the Austin MSA definition changed in 2020.

---

# Query Patterns #

Common query patterns for the new schema:

**Get current MSAs:**
```sql
SELECT * FROM msa_admin WHERE deleted_at IS NULL;
```

**Get MSA at a point in time:**
```sql
SELECT * FROM msa_admin 
WHERE created_at <= '2020-01-01'
  AND (deleted_at IS NULL OR deleted_at > '2020-01-01');
```

**Get all changes to a specific MSA:**
```sql
SELECT * FROM msa_admin 
WHERE msa_code = '12420'
ORDER BY created_at;
```

---

# API Integration #

I bridged the technical gap between the Data team and Engineering team — taking the compiled MSA data, transforming it, and updating the geospatial database to seamlessly work with Engineering's MSA service.

The service layer built on top of the database provides:

```
GET /api/msa/{msa_code}          → Current MSA definition
GET /api/msa?state=TX            → All MSAs in Texas
GET /api/msa/{msa_code}/history  → All versions of an MSA
```

The API shields consumers from SQL details while providing the flexibility needed for different use cases.

---

# Downstream Impact #

This work unblocked **two engineering epics** that had been waiting on reliable MSA data:

1. **Lat/Lon-to-MSA Service**: Maps coordinates to MSA regions for index builders
2. **MSA Decommission in Location Matcher**: Removes outdated MSA logic from older services

It also eliminated the "CSV on someone's laptop" problem. Teams now query the API or database directly, ensuring everyone uses the same definitions.

Additional downstream benefits:
- Unblocked a Phase III experiment for another team
- Enabled the Segment-Configuration-Service to proceed

---

# Data Quality Checks #

I added validation queries that run as part of the deployment:

```sql
-- Check for orphaned county references
SELECT msa_code, county_fips
FROM msa_admin
WHERE deleted_at IS NULL
  AND county_fips NOT IN (SELECT fips FROM counties);

-- Check for duplicate active records
SELECT msa_code, county_fips, COUNT(*)
FROM msa_admin
WHERE deleted_at IS NULL
GROUP BY msa_code, county_fips
HAVING COUNT(*) > 1;

-- Check for missing required fields
SELECT id, msa_code
FROM msa_admin
WHERE deleted_at IS NULL
  AND (msa_name IS NULL OR msa_name = '');
```

Any failures block the migration and alert the team.

---

# Schema Evolution #

The schema was designed with evolution in mind. Adding new fields is straightforward:

```sql
-- Future migration: add metropolitan division support
ALTER TABLE msa_admin 
ADD COLUMN metro_division_code VARCHAR(5),
ADD COLUMN metro_division_name VARCHAR(255);
```

Existing queries continue to work. New functionality can use the additional fields.

---

# Lessons #

**Soft deletes are worth the complexity.** Historical data analysis is surprisingly common. Permanently deleting records would have caused problems for reporting teams.

**Triggers beat application logic for timestamps.** Relying on application code to set timestamps leads to inconsistency. Database triggers are reliable.

**Migration files are documentation.** The sequence of 13 migration files tells the story of the data: what was added, what changed, what was removed.

**Design for the API, not just the schema.** The schema choices directly influenced what the API could offer. Thinking about consumption patterns early led to better design.
