---
title: "About"
author: "Wes"
date: 2026-10-02
showMeta: false
showDate: false
showTags: false
comments: false
metaAlignment: center
---

I'm Wes Porter (Wesley Porter), a Senior Location Data Operations Analyst at Indeed, based in Nashville, Tennessee. I've been on Indeed's Location Data team since 2018.

Since then I've built production pipelines, internal applications, Python libraries, and dashboards, and I've built and curated location databases. My title says data operations, but most of the work is analytics engineering: taking a slow or repetitive location-data task and turning it into a system the team can run, test, measure, and maintain.

One recent example: an [AI pipeline that replaced a manual vendor review task]({{< ref "post/2026/2026-01-18_AI_Location_Extraction_Pipeline.md" >}}). It cut about $90K a year in vendor spend and raised throughput from roughly 120 to more than 4,200 jobs per day at about 95% accuracy.

For quick summaries of recent projects, see the [portfolio](/portfolio/).

# How I approach the work

1. **Find a slow or fragile workflow.** A manual vendor task, an error-prone SQL process, an hours-long review, or an inherited pipeline nobody fully understands.
2. **Learn enough of the system to solve the whole problem.** That often means application code, databases, CI/CD, cloud infrastructure, scheduling, and monitoring, not just the analysis.
3. **Build something practical.** Usually a reusable app, pipeline, library, dashboard, or validation step rather than a one-time answer.
4. **Measure whether it worked.** Cost, turnaround time, data quality, coverage, reliability, and analyst time.
5. **Make the knowledge reusable.** Process guides, validation checks, troubleshooting notes, and agent-readable project context, so people and AI agents can repeat the work safely.

# Selected work

**Production data and AI pipelines.** I design and run scheduled pipelines that ingest data, apply rules or models, validate results, and publish reusable outputs. The AI location extraction pipeline combines GPT-4o-mini with rules and a TF-IDF classifier, and publishes results the team uses to track precision and recall.

**Internal applications and self-service tools.** I build tools that let analysts do complex work without hand-written SQL or one-off setup: a validated editor for our places database, a [Streamlit app for location database updates and SQL validation]({{< ref "post/2025/2025-12-28_LocDB_Tools_Validation_and_SQL.md" >}}), self-service regression testing, and dashboards such as the [geocoding credit dashboard]({{< ref "post/2026/2026-06-01_Geocoding_Credit_Dashboard.md" >}}).

**Location-data quality and safety.** Database changes can shift how jobs geocode and how searches resolve. I wrote SQL validation checks that reject unsafe changes (invalid hierarchies, duplicates, bad coordinates, orphaned aliases) before they ship, and I [taught an AI agent to review regression reports]({{< ref "post/2025/2025-12-23_AI_Regression_Report_Analyzer.md" >}}) the way an analyst would.

**Location datasets.** I led the technical work to build transit data for the United States, Germany, and Japan: about 430,000 station records. A Python ETL and conflation workflow reduced thousands of possible manual comparisons to about 250. In 2025 I built a transit updater and used it to refresh the Japan data, adding 27 stations, 2 lines, and 3 companies with no service disruption. Earlier, I helped reach complete US county-level coverage through 8,867 updates.

**Measurement and decision support.** Representative results:

- Raised US street-address coverage for indexed jobs by 4%.
- Took one large applicant-tracking feed from roughly 20% to 90% of jobs with street addresses.
- Evaluated two point-of-interest vendors with an AI-assisted workflow, cutting about a week of analysis to a 40-minute session; one vendor produced 62% fewer false positives in the reviewed data.
- Led a commute-time proof of concept with the open-source Valhalla routing engine that cut test runs from a full day to minutes.

**Inherited and legacy systems.** I often maintain systems after their original owners move on, and sometimes the right move is to retire them. I led the [shutdown of a legacy Django application and its infrastructure]({{< ref "post/2025/2025-07-01_Decommissioning_Legacy_Infrastructure.md" >}}), cutting cloud cost and maintenance while keeping the useful capabilities in smaller tools.

# Career arc

- **2018–2020:** Geographic analysis, regression review, and geocoding quality, increasingly replacing manual data preparation with scripts.
- **2021:** Measurement and automation: coverage dashboards, safe SQL generation, and helping colleagues with difficult data problems.
- **2022–2023:** Data engineering: large transit datasets, a Python ETL pipeline, and moving applications and databases to AWS with Terraform.
- **2024–2025:** Owning team systems: self-service regression workflows, dashboards, repository maintenance, and retiring legacy applications.
- **2025–2026:** Production AI: LLM extraction, feedback classification, labeling workflows, and documenting how teams can make repositories clear to AI agents.

# Elsewhere

[GitHub](https://github.com/wessport) · [LinkedIn](https://www.linkedin.com/in/wes-porter-10250488/)
