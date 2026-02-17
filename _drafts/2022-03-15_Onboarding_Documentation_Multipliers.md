---
title: "Onboarding and Documentation as Force Multipliers"
author: "Wes"
date: 2022-03-15

autoThumbnailImage: false
thumbnailImagePosition: "left"
thumbnailImage: https://res.cloudinary.com/wessport/image/upload/v1767000000/placeholder_thumb.png
coverImage: https://res.cloudinary.com/wessport/image/upload/v1767000000/placeholder_cover.jpg
metaAlignment: center
coverMeta: in
comments: true

keywords:
- Documentation
- Onboarding
- Mentorship
- Knowledge Sharing

categories:
- Team Building
- Documentation

tags:
- onboarding
- mentorship
- documentation
- team-enablement
---

*How investing in documentation and training multiplies team output.*

<!--more-->

---

# The Problem with Tribal Knowledge #

Every team accumulates knowledge that exists only in people's heads. How to run regression reports. Which config file controls the batch job. Why that one query uses a left join instead of an inner join.

This tribal knowledge creates bottlenecks. New team members take months to become productive. Key processes stall when certain people are on vacation. The same questions get answered repeatedly.

When I joined our team, the onboarding docs were two years out of date. Setup instructions referenced deprecated tools. Links pointed to moved pages. New hires spent days just getting their environment working.

I started treating documentation and training as force multipliers — investments that pay compound returns.

---

# Training on Core Tools #

I led onboarding training on topics where new team members consistently struggled:

**Internal Query Language (IQL)**

Our organization's query language powers most location data analysis, but it has a learning curve. I developed training sessions covering:

- Basic syntax and query structure
- Common patterns for location data
- Performance considerations for large datasets
- Debugging failed queries

The training included hands-on exercises using real datasets from our domain — geocoding results, location match metrics, job distribution analysis.

**Regression Reports**

Understanding regression reports is critical for anyone touching the location database. Before any bulk update goes live, we run regressions to ensure geocoding behavior doesn't unexpectedly change.

I created training covering:

- What the reports measure
- How to identify true regressions vs. noise
- Common patterns and their causes
- Escalation paths for concerning findings

I also ran 1-on-1 training sessions with team members to help them get set up to run regression reports independently.

---

# Video Walkthroughs #

Some knowledge transfers better in video than text. I recorded YouTube walkthroughs for complex processes:

- Setting up the regression report environment
- Importing geojson data into the analysis environment
- Configuring local database connections for testing

Videos captured the nuance that documentation missed — where to click, what the output should look like, how to recover from common errors.

These recordings became a reference that team members could rewatch as needed, rather than asking the same questions repeatedly.

---

# Template Collections #

Our analysis environment supports shareable templates. I developed a collection of templates for common tasks:

| Template | Purpose |
|----------|---------|
| Data quality check | Standard queries for validating bulk changes |
| Impact measurement | Calculate jobs affected by proposed changes |
| Geocoding comparison | Compare geocoders across markets |
| Sampling | Generate weighted samples for quality measurement |

New team members could start from a working template rather than a blank page. Templates encoded best practices — proper joins, efficient filtering, correct aggregation logic.

---

# Documentation Modernization #

I audited our existing documentation and found critical gaps. The modernization effort included:

**Postman Quickstart** — A guide for testing geocoding APIs locally. New team members could validate their understanding of the APIs without waiting for code review.

**Geocoding Tools** — Comprehensive documentation of the tools available for location analysis, which had been passed down verbally but never written down.

**Database Access Documentation** — A common friction point. New team members didn't know which databases existed, how to request access, or how to connect. I created documentation covering:

- Available databases and their purposes
- Access request process (with links to the right forms)
- Connection configuration for different tools
- Troubleshooting connection issues

```bash
# Example connection command included in docs
mysql -h db-host.example.com \
      -u $USER \
      -p \
      --ssl-mode=REQUIRED \
      location_db
```

This reduced the "how do I connect to the database?" questions significantly.

---

# Reducing Onboarding Time #

The onboarding documentation was severely out of date. The modernization effort:

1. Identified the critical onboarding docs
2. Walked through each process myself to find gaps
3. Updated instructions with current tooling
4. Added troubleshooting sections for common issues
5. Created a clear onboarding checklist

The result: new team members reached productivity faster. Questions that used to require synchronous help could be answered by documentation.

---

# Mentoring First Code Contributions #

Documentation only goes so far. For code contributions, I mentored team members through their first merge requests.

The process:

1. Pair on understanding the codebase structure
2. Review their approach before they start coding
3. Provide feedback on draft implementations
4. Conduct code review with teaching mindset
5. Support them through the merge process

One team member's first contribution updated a critical backfill script. The code review covered naming conventions, error handling patterns, testing approaches, and documentation expectations.

That contribution enhanced 7,800+ jobs that were previously unprocessed. More importantly, the team member could now make similar contributions independently.

---

# The Compound Effect #

Documentation and training have compounding returns:

| Investment | Returns |
|------------|---------|
| 2-hour training session | Saved ~20 hours of 1:1 questions |
| 30-minute video | Watched 50+ times by different people |
| Template collection | Starting point for 100+ analyses |
| Updated onboarding docs | Faster ramp for every new hire |

The time spent creating these resources was recovered many times over. More importantly, it freed up senior team members to focus on higher-leverage work.

---

# Takeaways #

Documentation isn't just about writing things down. It's about identifying where knowledge bottlenecks exist and systematically eliminating them.

The most effective approaches:

1. **Multiple formats**: Text for reference, video for process, templates for starting points
2. **Teach, then document**: Training reveals what's actually confusing
3. **Keep it current**: Outdated docs are worse than no docs
4. **Mentor through contribution**: Some knowledge requires hands-on transfer

Investing in team enablement is one of the highest-leverage activities available. Every hour spent on good documentation saves many hours for everyone else.
