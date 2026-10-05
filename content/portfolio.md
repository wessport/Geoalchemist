---
title: "Portfolio"
author: "Wes"
date: 2026-10-02
showMeta: false
showDate: false
showTags: false
comments: false
metaAlignment: center
thumbnailImage: /images/portfolio/carmen-place-detail.png
---

A few projects I've built on the Location Data team at Indeed. Where I've written a longer post, the title links to it.

For the longer story, see [About me](/about/).

<style>
  .portfolio-grid { display: grid; grid-template-columns: 1fr; gap: 56px; margin-top: 32px; }
  .portfolio-card h3 { margin: 0 0 12px; }
  .portfolio-card img { width: 100%; height: auto; display: block; margin: 0 0 12px; }
  .portfolio-card p { margin: 0 0 10px; }
  .portfolio-card img.portfolio-shot { border: 2px solid #E1E5EA; border-radius: 12px; }
  .portfolio-tags span { display: inline-block; font-size: 0.75em; letter-spacing: 0.04em; text-transform: uppercase; color: #4A5260; background: #EEF1F5; border-radius: 4px; padding: 2px 8px; margin: 0 6px 6px 0; }
</style>

<div class="portfolio-grid">

<div class="portfolio-card">
  <h3>Carmen: places database editor</h3>
  <img class="portfolio-shot" src="/images/portfolio/carmen-place-detail.png" alt="Carmen place detail view with an interactive map">
  <p>A validated, transactional web app that replaced hand-written SQL for creating, editing, and deactivating point-of-interest records.</p>
  <p class="portfolio-tags"><span>Python</span><span>Flask</span><span>MySQL</span><span>Leaflet</span></p>
</div>

<div class="portfolio-card">
  <h3><a href="{{< ref "post/2026/2026-01-18_AI_Location_Extraction_Pipeline.md" >}}">AI location extraction pipeline</a></h3>
  <img src="/images/portfolio/ai-location-pipeline.svg" alt="Daily pipeline: sample job postings, extract locations with an LLM, classify, match with a geocoder, and publish results for precision and recall tracking.">
  <p>An LLM pipeline that replaced a manual vendor review task: ~$90K/yr saved, 120 → 4,200+ jobs/day, ~95% accuracy.</p>
  <p class="portfolio-tags"><span>Python</span><span>GPT</span><span>TF-IDF</span><span>Scheduled jobs</span><span>APIs</span></p>
</div>

<div class="portfolio-card">
  <h3><a href="{{< ref "post/2026/2026-06-01_Geocoding_Credit_Dashboard.md" >}}">Geocoding credit &amp; volume dashboard</a></h3>
  <img class="portfolio-shot" src="https://res.cloudinary.com/wessport/image/upload/f_auto,q_auto,w_1600/v1780430945/blog/2026/geocoding-credit-dashboard-screenshot.png" alt="Geocoding credit dashboard demo with sample data">
  <p>Makes geocoding and autocomplete spend, cache behavior, and market usage visible, with a 30-day burn projection. <a href="https://geocoding-credit-dashboard-demo.onrender.com">Live demo</a> (sample data).</p>
  <p class="portfolio-tags"><span>Plotly Dash</span><span>Python</span><span>SQL</span><span>Business Intelligence</span></p>
</div>

<div class="portfolio-card">
  <h3><a href="{{< ref "post/2025/2025-12-23_AI_Regression_Report_Analyzer.md" >}}">Regression report toolkit</a></h3>
  <img src="/images/portfolio/regression-toolkit.svg" alt="A proposed location database change is checked for hierarchy, duplicate, coordinate, and orphaned alias problems.">
  <p>Self-service regression testing for location database changes, with SQL validation checks that block unsafe edits before they ship.</p>
  <p class="portfolio-tags"><span>Python</span><span>Flask</span><span>MySQL</span><span>Docker</span><span>Bash</span><span>Java</span></p>
</div>

<div class="portfolio-card">
  <h3>Location labeling studio</h3>
  <img class="portfolio-shot" src="/images/portfolio/labeling-studio.jpg" alt="Location labeling studio queue: the model's extracted address next to the job description">
  <p>Human review of model-extracted street addresses: it allows for a shared queue with handling for concurrency, labeling, immutable revisions, and snapshots that feed model training.</p>
  <p class="portfolio-tags"><span>Python</span><span>Flask</span><span>Trino</span></p>
</div>

<div class="portfolio-card">
  <h3>Transit updater: Japan transit data</h3>
  <img src="/images/portfolio/transit-updater.svg" alt="A quarterly EKI snapshot is diffed, screened by anomaly detectors, turned into Flyway SQL, reviewed by an analyst, and validated.">
  <p>Turns each quarterly Japan transit data (EKI) refresh into reviewed, validated SQL migrations with zero service disruptions.</p>
  <p class="portfolio-tags"><span>Python</span><span>PostgreSQL</span><span>Flyway</span><span>pytest</span></p>
</div>

</div>
