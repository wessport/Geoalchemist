---
title: "Cross-Team Data Partnerships"
author: "Wes"
date: 2024-10-15

autoThumbnailImage: false
thumbnailImagePosition: "left"
thumbnailImage: https://res.cloudinary.com/wessport/image/upload/v1767000000/placeholder_thumb.png
coverImage: https://res.cloudinary.com/wessport/image/upload/v1767000000/placeholder_cover.jpg
metaAlignment: center
coverMeta: in
comments: true

keywords:
- Data Partnerships
- Cross-Functional
- Data Quality
- Collaboration

categories:
- Data Engineering

tags:
- partnerships
- data-quality
- collaboration
---

*How working with external teams drove 4%+ increases in location data coverage.*

<!--more-->

---

# Results #

| Metric | Impact |
|--------|--------|
| **US Better Location Jobs** | +4% increase |
| **WorkForceNow Coverage** | 20% → 90% street address level |
| **US Street Address Jobs** | +3% increase (from WorkForceNow alone) |
| **ADP Partner Fix** | ~160,000 more precise location jobs |

---

# The Opportunity #

Our location database is only as good as the data that flows into it. We can clean, validate, and enrich — but if the source data is missing key fields, there's only so much we can do.

Street address data is a good example. Many job postings arrive with just a city name when they could include a full street address. The employer has the data; it's just not being passed through.

The Partner Management team works directly with data providers. They have relationships and leverage. We have the analytics to show impact. This seemed like a natural partnership.

---

# Building the Relationship #

I partnered with the Partner Management team to get street address data for the top indexed feeds, providing regular deep-dive analysis support and investigative feed reviews.

The first deliverable was an analysis tool — a data notebook that tracked street address coverage by partner over time. Partners could see their current state and track improvements after making changes.

```python
def calculate_coverage_metrics(partner_id: str, date_range: tuple) -> dict:
    jobs = fetch_partner_jobs(partner_id, date_range)
    
    with_street = sum(1 for j in jobs if j.get('street_address'))
    total = len(jobs)
    
    return {
        'partner_id': partner_id,
        'total_jobs': total,
        'with_street_address': with_street,
        'coverage_pct': (with_street / total * 100) if total > 0 else 0
    }
```

---

# The Analysis Tool #

I built a self-service notebook that the Partner Management team could run themselves. They didn't need to come to us every time they wanted to check on a partner.

Key features:

| Feature | Purpose |
|---------|---------|
| Partner-level breakdown | See coverage by individual data provider |
| Time series | Track changes over weeks/months |
| Job volume context | Coverage % means more when you see the raw numbers |
| Comparison to peers | How does Partner X compare to similar partners |

The notebook connected directly to our data warehouse. Results updated automatically.

---

# Case Study: WorkForceNow #

One of our biggest wins was with the WorkForceNow partner. Initial analysis showed:

- Significant job volume
- Only ~20% had street address data
- 80% were missing precise location info

The Partner Management team used this data in their conversations. The partner made changes to their data feed.

After the fix:

```
Before: ~20% street address coverage
After:  ~90% street address coverage
Change: +70 percentage points
```

This single partner improvement resulted in a **3% increase in US street address level jobs**.

---

# Case Study: ADP Feed Investigation #

As part of the Better Jobs initiative, I assisted with ATS partner feed investigations. For ADP, I provided a deep dive into their XML feed to show they were not sending the address data.

I created evidence documentation that the Partner Management team could send back to ADP demonstrating the data gap.

After the fix: **~160,000 more precise location jobs** now flow through correctly.

---

# Case Study: HiringThing #

Another win was with HiringThing. Initial analysis showed:

- ~17,000 jobs affected
- ~20% had street address data
- 80% were missing precise location info

After working with the Partner Management team:

```
Before: ~20% street address coverage
After:  ~60% street address coverage
Change: +40 percentage points
```

That's 17,000 jobs that now geocode to precise locations instead of city centroids.

---

# Financial Justification #

Partnerships require investment — engineering time to integrate feeds, analyst time to validate data, relationship management overhead. Sometimes stakeholders question whether it's worth it.

When Cloud FinOps questioned the geocoding costs from a recent data backfill for missing GB and CA markets, I provided comprehensive business value documentation:

- How the geocoding task powers the jobGeocodeDiff index
- Impact on location precision metrics critical to job search accuracy
- Downstream services that depend on the data

The funding was secured. More importantly, I established clear stakeholder communication channels and positioned the team as the technical point of contact for future inquiries.

---

# Scaling the Approach #

What worked with one partner could work with others. The pattern:

1. Identify partners with low data coverage
2. Quantify the impact (job volume, geographic distribution)
3. Provide Partner Management with concrete numbers
4. Track improvements over time
5. Report back on success

This became a repeatable workflow rather than a one-off project. I demonstrated over 40% increases in street address data coverage across multiple partners.

---

# Enabling Self-Service Analytics #

The real win was enabling the Partner Management team to showcase concrete business value to partners, strengthening relationships and encouraging continued data quality improvements.

The self-service notebook established a data-driven feedback loop for measuring partner onboarding success and optimizing location data collection strategies.

---

# Lessons Learned #

Data teams often focus on what they can control directly: cleaning data, building pipelines, improving algorithms. But some of the biggest wins come from influencing data quality at the source.

This requires stepping outside the technical work and building relationships with teams that have different leverage points. Partner Management can't write SQL, but they can convince a data provider to add a field to their feed.

Finding those complementary capabilities and building bridges between them is often more impactful than optimizing what you already do.
