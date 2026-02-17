---
title: "Leading a Data Quality Initiative: US Atlas Cleanup"
author: "Wes"
date: 2020-09-30

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
- Team Leadership
- SQL

categories:
- Data Quality
- GIS

tags:
- data-quality
- team-leadership
- location-data
---

*Coordinating a team of analysts to systematically improve location database accuracy, ultimately impacting 144,000+ jobs.*

<!--more-->

---

# The Challenge #

Our location database powered job search across millions of queries daily. But accumulated data quality issues were causing problems — jobs appearing in wrong cities, missing postal code mappings, and geocodes that placed jobs miles from their actual locations.

Leadership flagged the US atlas as a priority but noted it would be **"challenging in terms of efficiency and measuring impact."** The scope was enormous: every city, postal code, and geocoded point in the US.

I saw an opportunity to approach this systematically, using data to prioritize efforts and measure results.

---

# Prioritizing by Impact #

Rather than tackle the problem alphabetically or randomly, I developed a method to identify where cleanup efforts would have the most impact.

The approach: pull input/output pairs from the database showing what users searched for versus what the system returned. By joining this with job volume data, we could prioritize fixes that would affect the most users.

```sql
SELECT 
    input_postal,
    output_locality,
    COUNT(DISTINCT job_key) as job_count,
    COUNT(*) as query_count
FROM geocode_logs
WHERE country = 'US'
    AND input_postal != output_postal
GROUP BY input_postal, output_locality
ORDER BY query_count DESC
```

This query surfaced the highest-impact discrepancies. A postal code mapping affecting 10,000 jobs took priority over one affecting 10.

---

# Organizing the Work #

I led a team of **four analysts** through the cleanup effort. The workflow:

1. **Discovery**: Query to identify candidate issues
2. **Validation**: Manual review to confirm actual problems
3. **Fix**: Database updates with proper change management
4. **Verification**: Post-deployment checks

We met weekly to coordinate efforts and avoid duplication. I developed detailed workflows with instructions tabs that received positive feedback from team members for being intuitive.

---

# Missing Postal-Locality Combinations #

The first major focus was missing postal code to city mappings. When a user searched for jobs in a specific zip code, the system needed to know which city that zip code belonged to.

We discovered **251 missing combinations** that were actively causing issues. The impact: jobs were returning "zero results" or appearing in wrong locations.

The identification process combined SQL queries with manual validation:

```python
def find_missing_postals(df: pd.DataFrame) -> pd.DataFrame:
    """
    Identify postal codes that appear in job data 
    but have no corresponding entry in the location atlas.
    """
    job_postals = set(df['job_postal'].dropna().unique())
    atlas_postals = set(df['atlas_postal'].dropna().unique())
    
    missing = job_postals - atlas_postals
    
    return df[df['job_postal'].isin(missing)].groupby('job_postal').agg({
        'job_key': 'count',
        'locality': 'first'
    }).reset_index()
```

Each missing postal required research to determine the correct locality mapping, then a database update to add it.

---

# Fixing Poor Geocodes #

The second focus was geocoding accuracy. Some locations had coordinates that placed jobs in the wrong part of a city — or occasionally, the wrong city entirely.

We identified **70+ locations** with problematic geocodes affecting **over 5,000 jobs** and **50,000+ searches**. The detection method combined automated checks with manual review:

| Check | Description |
|-------|-------------|
| Distance from centroid | Geocode > 50km from city center |
| Cross-boundary | Geocode in different admin region |
| Water placement | Geocode in ocean/lake |
| Zero coordinates | Lat/long = 0,0 |

Each flagged location required manual investigation. Sometimes the geocode was wrong; sometimes the underlying address data was ambiguous.

---

# Measuring Impact #

To justify continued effort and report progress to leadership, I developed queries and dashboards to track impact over time.

I continuously monitored the frequency of discovered issues week by week, developing multiple tracking methods:

- IQL queries for measuring job impact
- An interactive notebook dashboard for ongoing monitoring
- Weekly progress reports to leadership

The data showed we were discovering issues at an increasing rate as we refined our detection methods.

---

# The Second Round #

Midway through the quarter, I noticed a trend: our initial list was generating diminishing returns, but our improved detection methods were surfacing new issues faster.

I advocated for extending the initiative into a second round, backed by the data. Leadership approved.

The second round improved accuracy for an additional **144,000 jobs** — significantly more impact than the first round. Better detection methods paid off.

---

# Final Results #

| Metric | Result |
|--------|--------|
| Missing postals added | 251 |
| Poor geocodes fixed | 70+ locations |
| Jobs with improved accuracy | 144,000+ |
| Analysts coordinated | 4 |

---

# Takeaways #

**Prioritize by impact.** Not all data quality issues are equal. A systematic approach to identifying high-impact problems maximizes the value of cleanup efforts.

**Measure continuously.** Data justifies continued investment. The metrics showing increased discovery rates made the case for a second round.

**Coordinate the team.** Detailed workflows and weekly syncs prevented duplication and ensured consistent quality across analysts.

**Iterate on detection.** Our detection methods improved with experience. The second round found more issues because we'd learned what to look for.

**Document the methodology.** The atlas cleanup became a template for how we approached data quality initiatives in subsequent quarters.
