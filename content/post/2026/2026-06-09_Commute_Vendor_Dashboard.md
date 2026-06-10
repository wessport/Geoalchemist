---
title: "More Plotly Dashboarding"
author: "Wes"
date: 2026-06-09

autoThumbnailImage: false
thumbnailImagePosition: "left"
thumbnailImage: /blog/2026/noun-plotly-dashboard.png
coverImage: /blog/2026/commute-vendor-dashboard-cover.jpg
metaAlignment: center
coverMeta: in
comments: true

keywords:
- Dash
- Plotly
- Dashboard
- Commute Times
- Routing

categories:
- Data Visualization
- Routing

tags:
- dash
- plotly
- dashboards
- routing
- commute-times
---

*A Dash/Plotly dashboard for comparing commute time estimates across routing providers.*

**[View the Dashboard →](https://commute-vendor-dashboard-demo.onrender.com)**

<!--more-->

More Plotly Dashboarding lately.

Have been working on incorporating guidelines for font usage, subtitle text, and using panes to organize content. This one has example data as well, but think it shows the type of in-depth analysis that occurred on this project.

{{< image classes="fancybox center fig-100" src="/blog/2026/commute-vendor-dashboard-valhalla-comparison.png" title="Commute vendor comparison dashboard" >}}

A few other conventions I've found stakeholders like:

- Methodology and Summary markdown at the top - a high level overview at the start
- Key metric cards
- Filters for drilling down to specific markets
- GGplot inspired colors - bright and easy to see on screen
- Error analysis and breakdown of assumptions/caveats and potential 'gotchas'

{{< image classes="fancybox center fig-100" src="/blog/2026/commute-vendor-dashboard-od-map.png" title="Origin-destination pairs map" >}}

Quickly building up templates and agent skills to create dashboards like this that used to take a week plus, into 30 minute sessions.
