---
title: "Developing Location Attributes with Text Extraction Rules"
author: "Wes"
date: 2021-03-15

autoThumbnailImage: false
thumbnailImagePosition: "left"
thumbnailImage: https://res.cloudinary.com/wessport/image/upload/v1767000000/placeholder_thumb.png
coverImage: https://res.cloudinary.com/wessport/image/upload/v1767000000/placeholder_cover.jpg
metaAlignment: center
coverMeta: in
comments: true

keywords:
- NLP
- Text Extraction
- Job Data
- Attributes
- Rosetta

categories:
- NLP
- Data Engineering

tags:
- nlp
- text-extraction
- attributes
- cross-team
---

*Building experimental job attributes using text extraction rules to identify "transient" jobs that don't fit the single-location model.*

<!--more-->

---

# The Problem #

Our team wanted to better identify jobs that didn't fit the standard "one job, one location" model. Delivery drivers, traveling nurses, construction workers — these roles are performed across multiple locations or while moving between sites.

The problem: our location enhancement metrics treated these jobs the same as office jobs. If we couldn't geocode a transient job to a single point, it counted as a failure, even though a single point might not be meaningful for that job type.

If we could identify and exclude transient jobs from our metrics, we'd have a more accurate picture of actual geocoding performance.

---

# Learning Rosetta #

The organization had a text extraction system called Rosetta for pulling structured data from unstructured job postings. I'd never worked with it directly, so the first step was learning how it worked.

I reached out to the Taxonomy team, who had built similar attributes for work settings. They pointed me to training resources and offered guidance on rule development.

The system used a rule-based approach with pattern matching. Rules could be combined and weighted to produce confidence scores for attribute detection.

---

# Developing the Transient Job Rule #

The goal was detecting jobs where the work is performed in multiple locations or while traveling. Common patterns in job postings:

- "Must be willing to travel 50% of the time"
- "Work performed at various client sites"
- "Regional position covering multiple states"
- "Travel required between warehouse locations"

I developed rules to capture these patterns while avoiding false positives. The false positive problem was significant — "travel benefits" or "close to public transit" shouldn't trigger the rule.

---

# Achieving 95% Precision #

After initial development, I ran the rule against a sample of job postings and manually reviewed the results. First iteration precision was around 80% — too many false positives.

The refinement process was iterative:

1. Pull sample of jobs flagged by the rule
2. Manually classify each as true/false positive
3. Analyze false positive patterns
4. Add exclusions or tighten patterns
5. Repeat

| Iteration | Precision | Main Issue |
|-----------|-----------|------------|
| 1 | 80% | "Travel" in benefits section |
| 2 | 88% | Company names with "Travel" |
| 3 | 93% | Ambiguous "regional" usage |
| 4 | **95%** | Minor edge cases |

The final rule achieved **95% precision** on the validation set — meeting our quality target.

---

# Java Code for Complex Regex #

Some patterns required more sophisticated handling than the rule language supported. I wrote Java code to handle complex regex cases for address normalization:

```java
public class AddressNormalizer {
    private static final Pattern SPECIAL_CHARS = 
        Pattern.compile("[^a-zA-Z0-9\\s,.-]");
    
    public String normalizeAddress(String input) {
        String cleaned = SPECIAL_CHARS.matcher(input).replaceAll("");
        cleaned = cleaned.replaceAll("\\s+", " ").trim();
        return cleaned;
    }
}
```

This code cleaned addresses extracted by the text extraction system before they were passed to the geocoder. Special characters like em-dashes or unusual apostrophes would cause geocoding failures.

---

# Cross-Team Collaboration #

The Taxonomy team was developing their own location-related attributes under "Work Settings" categories. Rather than duplicate effort, I pitched collaborating on the transient job detection.

By reaching out before diving in on my own, I was able to build on their existing work and gain access to training resources. This collaboration meant the experimental attributes I developed could eventually be promoted to production through their established pipeline.

---

# Impact Analysis #

Analysis of the experimental attributes showed a **~4% potential increase** in our enhancement metrics. By excluding transient jobs from the denominator, we'd have a more accurate picture of our actual geocoding performance.

```sql
SELECT 
    CASE WHEN is_transient THEN 'Transient' ELSE 'Standard' END as job_type,
    COUNT(*) as total_jobs,
    SUM(CASE WHEN geocoded THEN 1 ELSE 0 END) as geocoded_jobs,
    ROUND(100.0 * SUM(CASE WHEN geocoded THEN 1 ELSE 0 END) / COUNT(*), 2) as pct
FROM jobs_with_attributes
GROUP BY 1
```

| Job Type | Total | Geocoded | Rate |
|----------|-------|----------|------|
| Standard | 950K | 912K | 96% |
| Transient | 50K | 35K | 70% |

The 70% geocoding rate for transient jobs wasn't a quality problem — it reflected that these jobs legitimately don't have single locations.

---

# Takeaways #

**Learn from adjacent teams.** The Taxonomy team had already solved similar problems. Reaching out for guidance saved time and improved the final result.

**Iterative refinement is required.** 95% precision required four iterations. Each round surfaced new edge cases that weren't obvious initially.

**Measure potential impact.** Quantifying the ~4% metric improvement made the business case for the work clear.

**Build for production.** By collaborating with Taxonomy, the experimental attributes had a path to production through their established pipeline.
