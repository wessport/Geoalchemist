---
title: "Reducing Location Complaints by 47%"
author: "Wes"
date: 2021-09-30

autoThumbnailImage: false
thumbnailImagePosition: "left"
thumbnailImage: https://res.cloudinary.com/wessport/image/upload/v1767000000/placeholder_thumb.png
coverImage: https://res.cloudinary.com/wessport/image/upload/v1767000000/placeholder_cover.jpg
metaAlignment: center
coverMeta: in
comments: true

keywords:
- Data Analysis
- User Feedback
- Problem Solving
- Cross-Functional

categories:
- Data Analysis

tags:
- user-feedback
- data-analysis
- problem-solving
---

*Using feedback data to identify and fix the biggest source of location complaints — reducing overall complaint volume by 47%.*

<!--more-->

---

# The Data #

Our team had access to jobseeker feedback — complaints submitted when someone felt a job was displayed in the wrong location. The data had been collected for a while, but nobody had systematically analyzed it.

I started by categorizing the complaints. What were people actually complaining about?

The breakdown was revealing:

| Category | Percentage |
|----------|------------|
| **Remote jobs** | **25%** |
| Wrong city | 18% |
| Wrong state | 15% |
| Too far from search location | 14% |
| Other | 28% |

Remote jobs were the single largest category. **One in four location complaints was about a remote job.**

---

# Digging Into Remote #

"Remote job" complaints weren't all the same problem. I broke them down further:

```python
def categorize_remote_complaint(complaint: dict) -> str:
    job = fetch_job_details(complaint['job_id'])
    
    if job.get('remote_flag') and job.get('location_displayed'):
        return 'remote_with_location'
    
    if not job.get('remote_flag') and 'remote' in job.get('title', '').lower():
        return 'remote_in_title_only'
    
    if job.get('remote_flag') and contradicts_job_details(job):
        return 'contradictory_details'
    
    return 'other_remote'
```

The results:

| Remote Subcategory | Percentage of Remote Complaints |
|-------------------|--------------------------------|
| **Contradictory details** | **28%** |
| Remote with location display | 25% |
| Title only | 22% |
| Other | 25% |

Contradictory responses to job detail questions accounted for ~28% of our issues. Jobs flagged as remote, but with job descriptions saying "must be able to commute to office."

---

# Finding Actionable Issues #

Not all problems are equally fixable. Some require product changes, some require employer education, some require source data improvements.

I focused on issues we could **query programmatically**. If we could find the bad jobs automatically, we could do something about them.

Contradictory details were queryable:

```sql
SELECT job_id, title, remote_flag, job_details_response
FROM jobs
WHERE remote_flag = 1
  AND (job_details_response LIKE '%commute%'
       OR job_details_response LIKE '%on-site%'
       OR job_details_response LIKE '%in-office%')
```

This gave us a list of jobs that were marked as remote but contained conflicting information.

---

# The Proposal #

I drafted a proposal for addressing these issues:

1. **Visibility rules** — Jobs with contradictory remote flags could be flagged for review
2. **Employer nudges** — When posting, employers with conflicting data could see a warning
3. **Search filtering** — Remote jobs with location requirements could be filtered differently

The proposal wasn't about building new systems. It was about using existing policy mechanisms to encourage employers to fix their data.

---

# Cross-Team Coordination #

Implementing this required buy-in from teams outside our immediate scope:

- **Search Quality** — They owned the policy rules that could flag jobs
- **Employer Products** — They owned the job posting flow
- **Customer Support** — They dealt with employer complaints when jobs got flagged

I led meetings to walk through the proposal, share the data, and address concerns.

The key selling point: we weren't proposing to remove jobs. We were proposing to surface conflicting information so employers could fix it themselves.

---

# Implementation #

Search Quality implemented a visibility policy rule based on our query logic. Jobs matching the contradiction pattern would trigger an employer notification encouraging them to review their job details.

The rule went live on **August 11, 2021**.

---

# Results #

One month after implementation:

| Metric | Before | After | Change |
|--------|--------|-------|--------|
| Remote-related complaints | 25% of total | 14% of total | **-11 percentage points** |
| Complaint volume | Baseline | 53% of baseline | **-47%** |

Complaint volume dropped by **47%**. The percentage of complaints about remote jobs dropped by **11 percentage points**.

---

# Why This Mattered #

This was the **first time our team successfully influenced search quality policy rules** to make location improvements.

We had good data analysis capabilities. We had identified problems before. But translating analysis into action required:

- Working across team boundaries
- Building coalitions with teams that owned implementation
- Making proposals that other teams could execute

The technical work was straightforward. The cross-functional coordination was the hard part.

---

# Lessons Learned #

**Start with the data.** Categorizing complaints systematically revealed patterns that weren't obvious from anecdotal reports.

**Focus on actionable issues.** Some problems require product changes that won't happen soon. Find the subset you can address with existing mechanisms.

**Build coalitions.** Data analysis alone doesn't change anything. You need teams with implementation authority to buy in.

**Measure the outcome.** Before-and-after measurement proved the intervention worked. That builds credibility for future proposals.
