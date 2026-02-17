---
title: "Location Data Quality at Scale"
author: "Wes"
date: 2025-05-15

autoThumbnailImage: false
thumbnailImagePosition: "left"
thumbnailImage: https://res.cloudinary.com/wessport/image/upload/v1767000000/placeholder_thumb.png
coverImage: https://res.cloudinary.com/wessport/image/upload/v1767000000/placeholder_cover.jpg
metaAlignment: center
coverMeta: in
comments: true

keywords:
- Data Quality
- Location Data
- Regression Testing
- Data Governance

categories:
- Data Engineering

tags:
- data-quality
- location-data
- testing
---

*Proactive data quality work that prevented regressions and removed decade-old artifacts.*

<!--more-->

---

# Results #

| Initiative | Impact |
|------------|--------|
| JP Postal Code Testing | **4% increase** in JP better locations |
| COUNTY Cleanup | Improved **~2,000 daily geocoder requests** |
| Prevented Regressions | Tokyo fallback bug, Remote JP→US bug |

---

# The Challenge #

Location databases accumulate cruft over time. Original data sources get deprecated. Business rules change. Edge cases that made sense in 2015 don't make sense in 2025.

Meanwhile, downstream services keep expanding. Data that sat dormant for years suddenly starts surfacing through new interfaces. Problems that were invisible become visible.

Proactive cleanup is unglamorous work, but it prevents fires.

---

# COUNTY Type Record Cleanup #

Our location database contained COUNTY type records from an original third-party data source. These were decade-old artifacts — cities that had been labeled as counties, with coordinates pointing to the wrong place.

For years, nobody noticed. The records existed in the database but weren't heavily used. Then downstream services expanded their coverage, and these bad records started appearing in geocoder responses, causing confusion for consuming teams.

```sql
-- Example of problematic records
SELECT name, type, lat, lon 
FROM location_table 
WHERE type = 'COUNTY' 
  AND name IN (SELECT name FROM location_table WHERE type = 'CITY');

-- Many records where county name matches a city name
-- With coordinates that don't make sense for counties
```

---

# Analysis and Impact Assessment #

Before deleting anything, I analyzed the downstream impact:

| Service | Daily Requests Affected |
|---------|------------------------|
| Geocoder | ~2,000 |
| Location Services | Growing as services expanded |

These weren't huge numbers, but they were growing. Better to fix now than wait for complaints.

I applied data quality expertise to distinguish between legitimate geographic entities and erroneous city-labeled county records with incorrect coordinate values.

---

# The Cleanup Process #

The deletion followed our standard change management process:

1. **Identify candidates** — SQL query to find suspicious records
2. **Manual review** — Spot-check a sample to confirm they're bad
3. **Regression report** — Run against test environment
4. **Stakeholder review** — Share with teams that consume the data
5. **Staged rollout** — Delete in batches, monitor for issues
6. **Post-deployment verification** — Confirm no unexpected regressions

```python
def identify_suspicious_counties(db_connection) -> list[dict]:
    query = """
        SELECT c.id, c.name, c.lat, c.lon, c.country
        FROM location_table c
        WHERE c.type = 'COUNTY'
          AND EXISTS (
              SELECT 1 FROM location_table city
              WHERE city.type = 'CITY'
                AND city.name = c.name
                AND city.country = c.country
          )
          AND c.created_date < '2016-01-01'
    """
    return db_connection.fetch_all(query)
```

**Impact**: Prevented expanding downstream location service issues by proactively cleaning legacy data quality problems before wider service adoption. Enhanced location database data integrity by eliminating historical data artifacts that were beginning to surface through updated service interfaces.

---

# JP Postal Code Regression Testing #

On the other end of the spectrum: preventing bad data from getting in.

We were adding new postal code data for Japan along with geocoder improvements. The changes looked straightforward — new records, updated coordinates, minor hierarchy adjustments.

I collaborated with team members to set up a custom regression report CVM (Change Verification Method) to facilitate evaluating the new JP geocoder and JP Postal Code additions. This allowed us to quickly iterate on regression tests — we could focus on the data results while engineering focused on code improvements.

---

# Prevented Serious Regressions #

The regression testing caught two serious issues:

1. **Tokyo locations falling back to ADMIN2** — Jobs that should resolve to specific neighborhoods were resolving to the entire Tokyo prefecture
2. **Remote JP jobs moving to the US** — A logic error was causing some remote job postings in Japan to geocode to US locations

Both would have been bad user experiences. The regression testing caught them before production.

---

# Setting Up Custom Regression Tests #

For complex changes, standard regression reports aren't enough. We set up custom CVM configurations to test specific scenarios:

```yaml
# Custom regression config for JP postal changes
test_scenarios:
  - name: "Tokyo neighborhood resolution"
    input_locations:
      - "Shibuya, Tokyo"
      - "Shinjuku, Tokyo"
    expected_type: "LOCALITY"
    
  - name: "Remote job handling"
    input_locations:
      - "Remote, Japan"
    expected_country: "JP"
    
  - name: "New postal codes"
    input_postal_codes:
      - "150-0001"
      - "160-0022"
    expected_resolution: "POSTAL"
```

The custom tests let us iterate quickly. When something failed, we knew exactly which scenario broke.

**Result**: The JP postal code additions resulted in a **4% increase to JP better locations**.

---

# Coordination Across Teams #

Data quality at scale requires coordination. The COUNTY cleanup affected multiple downstream services. The JP postal changes required alignment with engineering on geocoder behavior.

For each initiative:

1. Document the proposed changes
2. Identify affected teams
3. Share timeline and rollback plan
4. Get explicit sign-off before proceeding
5. Communicate completion

This adds overhead, but it prevents the "who changed this and broke everything" conversations.

---

# Technical Leadership in Data Restructuring #

Beyond cleanup, I applied location data expertise to lead complex technical decision making across multiple markets during admin restructuring work:

- **Thailand**: Leveraged database knowledge to architect a four-tier hierarchical solution while mitigating potential data conflicts
- **Vietnam**: Provided strategic advice addressing admin consolidation issues and structural recommendations

This involved assisting team members with problem solving, weighing improvements vs tradeoffs for holistic decision making, and utilizing effective communication to guide team decision making.

---

# Lessons Learned #

Proactive data quality work pays off in ways that are hard to measure. You prevent problems that would have consumed time later. You build credibility with downstream teams. You reduce the surprise factor when changes do need to happen.

The hard part is prioritizing it. There's always something more urgent. But letting data quality slide creates compounding problems — and eventually, urgent fires.

Establishing technical authority through systematic problem-solving and clear communication of trade-offs enables confident team decision-making on complex data challenges.
