---
title: "AI-Powered Data Analysis Workflows"
author: "Wes"
date: 2025-06-15

autoThumbnailImage: false
thumbnailImagePosition: "left"
thumbnailImage: https://res.cloudinary.com/wessport/image/upload/v1767000000/placeholder_thumb.png
coverImage: https://res.cloudinary.com/wessport/image/upload/v1767000000/placeholder_cover.jpg
metaAlignment: center
coverMeta: in
comments: true

keywords:
- AI
- Data Analysis
- Python
- LLM
- Automation

categories:
- AI
- Data Engineering

tags:
- ai
- data-analysis
- automation
- python
---

*Practical applications of AI agents for data analysis and boosting team productivity.*

<!--more-->

---

# Background #

Over the past year, I've been experimenting with integrating AI tools into data analysis workflows across several projects. 

One, to test how well they perform, and two, to look for ways to reduce time spent on repetitive task we could handoff to ai agents.

Increasingly I think we will transition from tranditional IC roles, to ones where we're still IC's but managing a small team of ai agents under us that take care of repetitive tasks. This frees us up to plan bigger picture projects or tackle really tricky problems that we just didn't have time to explore before.

The end goal being, the team can focus on interpretation and decision-making.

I was a pretty early adopter, exploring tools like OpenAI's API, Cursor, and Amp. I saw it as an opportunity to completely rethink how we approach our work. 

Below I showcase a little of how our team is leading the way in integrating AI to transform complex data workflows from prior manual, error-prone processes into more automated, scalable, and highly accurate operations.

---

# AI Orchestrated Database Updates #

Updating transit data used to require days of manual work — reviewing records, identifying duplicates, validating relationships between stations, lines, and companies. Change tracking was complicated given the source data had to be transformed from its original format and configured for our usecase.

I wondered if I could leverage some of the new models like Sonnet to orchestrate some of the data operations.

For a recent database update, I explored orchestrating the data engineering components using AI agents for duplicate resolution, validation workflows, and automated migration report generation.

| Task | Manual Approach | AI-Assisted |
|------|-----------------|-------------|
| Duplicate resolution | Review each record | Automated matching with human review of edge cases |
| Validation workflows | Manual spot checks | Automated constraint validation |
| Migration reports | Manual compilation by the analyst | Auto-generated summaries similar to change logs |

For example:
---
The result: **27 net new transit stations, 2 new lines, and 3 new companies added**, with updates across **186 existing stations**. Complete Utsunomiya LRT system (18 stations), reactivated Hiroshima tram network (11 stations), and established Happi-line Fukui network — with **zero orphaned relationships** and complete service continuity throughout the migration process.
---

The key was using the agent as an orchestrator. I provided the data constraints (e.g. no orphaned relations) and report styling; the agent handled the repetitive validation and flagged only the records that needed human attention.

This vastly sped up our ability to get data updates out, and even raised data quality issues to us that might have gone unnoticed otherwise.

## Not Perfect ##

It wasn't perfect though, occassionally it would misinterpret locations as duplicates or forget work it had done prior. I had success in createing a git tracked directory `ai_logs/` where I would ask the agent at the end of each task to write a summary of all of it's work and **importantly where it had messed up**. 

At the beginning of each new session, I would ask the agent to read the latest log for context on the prior work - any issues were acknowledge (and added to the AGENT.md) before the next stage of work started.

Not perfect, but helped circumvent a lot of issues.

A few other important guardrails:
- Only read access to the DB, no writes
- Project specific virtualenv for temporary python skills
- Always asks for permission before performing git operations
- Tested with a local dump of the database to prevent unexpected issues
- Run in an isolate CVM environment

---

# AI Powered Vendor Analysis #

When evaluating a new POI (Points of Interest) vendor, the analysis historically took a week. You'd sample records, write a script to pass the data through vendors and ouput the results, manually verify accuracy against known locations, calculate match rates, and compile findings in a report.

Taking some learning from the Transit AI project, I led an AI-powered analysis comparing accuracy of our POI services for potential impact assessment. The workflow:

1. Built automated POI matching algorithms
2. Created verification workflows for a golden dataset (**500 prior manually reviewed records**)
3. Generated statistical comparisons automatically

**40 minutes** instead of a week — dramatically increasing efficiency of analysis workflows with AI, reducing a week-long task into a 40 minute work session.

The analysis revealed that the alternative provider had **62% fewer false positives** but lower overall coverage — a fundamental data quality vs coverage trade-off. The AI approach enabled fast insights that we could pass quickly to leadership to help with our vendor review.

## Important Note ##

The AI agent didn't do all of this on its own, it needed someone to guide it to know what metrics to look at, what data questions to ask. It's main benefit was in expediting the work, it still needs someone to drive and know the destination.

---

# Custom Repeatable AI Tooling - Regression Report Analyzer #

Location database changes require regression testing to ensure updates don't break downstream geocoding. Our regression reports often contain thousands of rows across multiple countries.

Previously, reviewing a single report took most of a workday. Analysts would scroll through changes, mentally categorize impact, and write up summaries.

I developed an AI-powered tool for automatically analyzing large location database regression reports, generating executive summaries with country-by-country impact analysis:

```
CSV File (600KB) → Python Aggregation → LLM Analysis → HTML Report
```

Features:
- Color-coded sections for quick scanning
- Standardized formatting across reports
- Key fallbacks, improvements, and data quality concerns highlighted
- Country-by-country impact breakdown

What was 8 hours of initial triage is now measured in seconds, with the analyst focusing on targeted review of the high-impact changes the AI flagged.

**Key Learning:** Context **_really_** matters - this approach was successfull because we had already compilled a lot of docs explaning the database, it's structure, location types, etc. This was context the model needed to complete the report accurately and consistently. Without it, the "summary" it generated was essentially useless.

**Impact**: I was able to streamline regression report review process for the team, enabling us to rapidly detect critical changes that needed a human eye on them. This was our first foray into creating custom, reusable AI tooling for our team and our data workflows.

---

# Team Training #

Tooling only matters if people use it. I conducted a live knowledge share/demo of the AI tools I had been using for my workflows covering:

- Prompt engineering practices
- Common pitfalls (overly broad requests, missing context)
- Practical applications for location data quality workflows including demoing the POI vendor analysis

AI agents are a mirror. They're only as useful as your understanding of the problem space and your creativity. 

They work best when you give it structured problems with clear criteria. Vague prompts produce vague results.

## A Common AI Repo ##
I put together a centralized repo as a resource for team AI prompts, workflows, and reusable analysis patterns. This helped us share learnings from each other and incorporate prompt patterns across projects and team members and has been immensely helpful.

---

# Patterns That Work #

A few observations from a year of this:

**Start with aggregation.** Raw data dumps overwhelm token limits and produce poor results. Pre-process the data to extract what's important, then ask the AI to analyze patterns.

**Define success criteria.** "Analyze this data" is a bad prompt. "Identify the top 10 countries by regression volume and flag any country where more than 5% of changes are fallbacks" is much better.

**Keep humans in the loop.** The AI surfaces patterns and drafts summaries. Humans validate the interpretation and make decisions. This isn't about removing human judgment; it's about focusing it on what matters.

**Version control prompts.** I track prompts in git so we can test variations over time and maintain consistency across team members.

**Ask Questions for Clarification as Needed** I always include this in my prompts - it helps me write more robust prompts, helps clear up misunderstandings with the agent, and more than not, helps uncover questions about the data I didn't think to ask.

---

# What Doesn't Work #

AI isn't a substitute for domain knowledge. I've seen cases where an agent confidently produced analysis that missed obvious issues because it didn't understand the usecase of the data or how it was collected.

It also struggles with:
- Edge cases that require institutional knowledge
- Data quality issues that aren't explicitly defined
- Problems where "correct" depends on stakeholder priorities

The pattern is: AI handles volume and exploration; humans handle nuance and judgment.

---

# Results #

| Metric | Impact |
|--------|--------|
| POI vendor analysis | **~1 week → 40 minutes** |
| False positive reduction | **62% improvement** with AI-assisted verification |
| Regression report triage | **~8 hours → minutes** |
| Transit data updates | Complex multi-phase work automated and reported with confidence |

---

# Positioning for the Future #

Ultimately we've used this work to help be proactive. AI isn't going away even after the bubble "pops". My thinking has been to try and learn it and harness it for good as much as possible rather than avoid it out of fear (some of which is justified).

I do think there are areas where it can be cost effective, and help transform manual processes into automated ones and accelerate team productivity. 

It just depends on if we use it intelligently or not.
