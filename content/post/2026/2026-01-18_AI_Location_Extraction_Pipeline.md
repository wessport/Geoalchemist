---
title: "Replacing a $90K/Year Manual Vendor Process using AI"
author: "Wes"
date: 2026-01-18

autoThumbnailImage: false
thumbnailImagePosition: "left"
thumbnailImage: https://res.cloudinary.com/wessport/image/upload/v1768771124/ai-pipeline.png
coverImage: https://res.cloudinary.com/wessport/image/upload/v1768769882/barbican-kitchen-golden-hour.jpg
metaAlignment: center
coverMeta: in
comments: true

keywords:
- AI
- Data Engineering
- Python
- ETL
- LLM
- Cost Optimization

categories:
- Data Engineering
- AI

tags:
- ai
- etl
- python
- data-pipelines
- llm
---

{{< youtube i48gRGkBZEE >}}

**[Try the live demo →](https://ai-loc-extraction-demo.onrender.com)**

*How I replaced a vendor moderation task with an LLM-powered pipeline, cutting costs by 99.4%.*

<!--more-->

---

# Background #

Since 2019, my team relied on a vendor moderation task to help measure location extraction accuracy. Human reviewers examined job postings and verified whether the extracted location was correct. This data fed into precision metrics tracking our geocoding quality over time.

The task answered a few key questions:

- How accurate is the location data we're collecting from employers?
- Are we capturing the most precise location possible (street address vs. city)?
- What percentage of jobs are single-location vs. remote or multi-location?

The limit: past **budget constraints limited the task to ~$5,000/month**, restricting volume of data we could collect and our market coverage. We could only afford to process jobs in three markets, and even then at a reduced scale.

With LLM capabilities maturing, this seemed like a good opportunity to transform our vendor task.

I think I was mostly excited because rather than adding “AI” for its own sake, this was a real case where recent improvements in LLM reliability (pinning models, setting the temperature, frequency penalty, etc - making responses more deterministic and stable), plus the lower cost made it pragmatic to test out the new tech and actually improve our process significantly.

---

# Results #

| Metric | Before (Vendor) | After (AI Pipeline) |
|--------|-----------------|---------------------|
| **Monthly Cost** | ~$5,000 | ~$30 |
| **Cost Reduction** | — | **99.4%** |
| **Annual Savings** | — | **~$89,000** |
| **Daily Volume** | Limited by budget | 4,200+ jobs/day |
| **Markets** | 3 (constrained) | 3 (expandable) |

The pipeline uses GPT-4o-mini at **$0.0002 per job** — roughly $1 per 5,000 jobs processed.

---

# Accuracy Validation #

Before replacing the vendor process, I needed to prove the model could match our vendor's accuracy. I ran the pipeline against historical data where we had "ground truth" from the vendor labels:

| Market | AI Accuracy | Sample Size |
|--------|-------------|-------------|
| US | 95.0% | 843 jobs |
| CA | 98.0% | 1,550 jobs |
| GB | 96.9% | 2,188 jobs |

These numbers matched or exceeded the vendor's calibrated accuracy of ~95%. It took a few attempts at crafting a strong enough prompt to handle edge cases, but the model performed surprisngly well. Even the earliest iterations were > 80% accurate out of the gate.  

---

# Pipeline Architecture #

I designed the system as a **library + scheduled job** pattern, separating reusable logic from deployment infrastructure:

| Component | Purpose |
|-----------|---------|
| **Pipeline Library** | Reusable extractors, classifiers, validation logic |
| **Production Cronjob** | Deployment wrapper with infrastructure integration |

This separation enables:

1. **Reusability** — The library can be imported by other projects or used for local testing
2. **Independent versioning** — Library updates can be validated before production deployment
3. **Clean CI/CD** — Each component has focused build/deploy pipelines

---

# Data Flow #

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────────┐
│  Data Warehouse │ ──▶ │  LLM Extraction  │ ──▶ │   Classification    │
│  (Job Sample)   │     │  (GPT-4o-mini)   │     │  (Remote/Multi-loc) │
└─────────────────┘     └──────────────────┘     └─────────────────────┘
                                                           │
                                                           ▼
                                                 ┌─────────────────────┐
                                                 │   Analytics Index   │
                                                 │   (47 fields)       │
                                                 └─────────────────────┘
```

### Stage 1: Data Ingestion

The pipeline samples jobs from our data warehouse, joining job metadata with full descriptions:

```sql
SELECT 
    job_id,
    feed_id,
    job_title,
    company,
    city,
    state,
    postal_code,
    job_description
FROM job_data
WHERE country = '{country}'
  AND created_date >= '{start_date}'
  AND feed_id NOT IN ({excluded_feeds})
```

### Stage 2: LLM Extraction

Each job description is sent to GPT-4o-mini with a structured prompt requesting:

- Primary work location (city, state, postal code)
- Location confidence score
- Whether location appears explicitly in the job text

The prompt engineering required some iteration. Early versions struggled with:
- Jobs listing multiple office locations
- Remote positions with residency requirements
- HR locations

I refined the prompts based on error analysis until accuracy stabilized above 95%. 
I also git tracked the prompts themselves so we can test prompt variations over time if need be.

#### Example Prompt
```
You are an information extraction assistant. Extract the most specific primary work location explicitly mentioned in the job posting. Only copy text that exists in the context; do not infer, normalize, or reformat.

Context:
{{INSERT_CONTEXT}}

Question:
{{INSERT_QUESTION}}

Extraction rules (strict):
- Prefer the most specific location by this order:
  1) full street address including suite/building and postal code
  2) city, state, postal code
  3) city, state
  4) city only
  5) state only
  6) country only
- If a full street address appears anywhere in the posting, return that entire address (including suite/floor/building, punctuation, abbreviations, and ZIP/postal code) exactly as written.
  - When the location line uses a label + dash pattern (e.g., "Location: [site name] - [address] (qualifier)"), return only the address after the dash and exclude any trailing parenthetical qualifiers like "(Hybrid)".
  - When a street address is present, capture the contiguous span from the street number through the postal code, inclusive. Do not drop leading street name/number segments or suite/building designators.
  - If a venue/site/facility/organization name appears adjacent to an address (e.g., "[Venue] - 123 Main St..." or "[Venue], 123 Main St..."), exclude the venue name and return only the address portion beginning at the first street number.
  - Treat separators such as "-", "–", "—", ":", and "," as potential dividers between a venue name and the address; always capture from the first street number through the postal code.
  - Terminate the span at the end of the postal/ZIP code; if a country name immediately follows, include the country name, but exclude any parenthetical country codes (e.g., "(US)").
  - Do not consider venue-only or unit-only mentions without a street name (e.g."#5 Woodfield Shopping Center") as a full street address; when no street name is present, fall back to the next granularity (e.g., city, state, postal).
  - Prefer locations explicitly labeled with "Location:", "Work Location", "Primary Location", "Office", "Site" near the role header over addresses in footer/contact sections.
  - If multiple candidates exist at the same granularity, choose the one most clearly tied to the job's work location (by label or proximity to the job title/overview).
  - Do not invent missing parts. If no higher-granularity location exists, fall back to the next level in the order above.
  - Exclude emails, phone numbers, URLs, and HR or corporate mailing blocks not tied to the job location.

Response format (JSON only):
- Return JSON only (no prose, no markdown).
- Use exactly this object and do not add extra keys:
{
  "explanation": string,
  "granularity": "full_street" | "city_state_postal" | "city_state" | "city" | "state" | "country" | "none",
  "answer": string
}
- If no location is present, set "granularity" to "none" and "answer" to "UNKNOWN".
```

### Stage 3: Classification

Beyond location extraction, the pipeline classifies jobs into categories:

**Remote/Hybrid/Onsite Classification**
- 1,487 pattern-matching rules for common remote indicators
- A custom TF-IDF model for ambiguous cases
- Confidence scoring for downstream filtering

**Non-Single Location Detection**
- Identifies transient jobs (delivery, trucking, sales territories)
- Flags multi-site positions where "location" is ambiguous

These were past side projects of mine that I incorporated into the pipeline to enrich the final data product.

### Stage 4: Index Upload

Results are uploaded to an analytics index with ~40 documented fields, enabling ad-hoc queries and monitoring for the team and stakeholders:

```sql
-- What percentage of jobs have precise location data?
SELECT 
    country,
    location_granularity,
    COUNT(*) as jobs,
    COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (PARTITION BY country) as pct
FROM ai_location_match
WHERE process_date >= CURRENT_DATE - 30
GROUP BY country, location_granularity
```

---

# Cost Analysis Methodology #

To help justify the project, I ran the numbers:

**Vendor Model (Before)**
- Per-task pricing from our moderation vendor
- Our volume capped by monthly budget allocation
- Additional costs/timesink for quality training and syncs

**AI Model (After)**
- LLM API cost: $0.15 per 1M input tokens, $0.60 per 1M output tokens
- Average job description: ~800 tokens
- Average extraction: ~200 tokens
- **Per-job cost: $0.0002**

At 4,200 jobs/day × 30 days = 126,000 jobs/month:
- **Vendor cost**: ~$5,000
- **AI cost**: ~$25-30

The 99.4% cost reduction meant the project paid for development time within the first month of operation.

---

# Lessons Learned #

**Start with accuracy benchmarks.** Having historical vendor data to compare against made model validation straightforward. Without the historical data, proving the model accuracy would have required building a golden dataset from scratch but would still have been critical to building a reliable output.

**Iterate on prompts to fine tune.** The first prompt hit about ~80% accuracy. Getting to 95%+ required analyzing the edge cases where the model tripped up and refining instructions with few-shot examples to draw from.

**Separate library from deployment runner.** The library + cronjob pattern simplified testing and enabled other teams to reuse the extraction logic for their own use cases. I wasn't sure if this was overkill at first, but the library is already being used by other projects.

**Model cost at the start.** Showing a $90K annual savings made leadership approval easier.

**Design for self-serve analytics.** The 47-field output schema was designed around the questions stakeholders actually ask with our prior task. The index now powers a dashboard to help us monitor location extraction accuracy.

---

# Takeaways #

Overall this project was a big win for our team. It demonstrated what's possible when you incorporate LLMs intelligently into problem spaces where they excell. We achieved actual cost savings and majorly upgraded one of our most important data products.

Definitely learned a lot from this work. Excited to already be leveraging this workflow for another project related to sentiment analysis of location feedback at scale for our Product teams.
