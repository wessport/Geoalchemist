---
title: "Walk Times on a Hex Grid"
author: "Wes"
date: 2026-10-12

autoThumbnailImage: false
thumbnailImagePosition: "left"
thumbnailImage: /blog/2026/toho-icon.png
coverImage: /blog/2026/toho-walk-time-grid-cover.jpg
metaAlignment: center
coverMeta: out
comments: true

keywords:
- H3
- OpenStreetMap
- Routing
- Walking
- deck.gl

categories:
- Data Visualization
- Routing

tags:
- h3
- openstreetmap
- routing
- walking
- deck-gl
- python
- duckdb
---

*A H3 hexagon grid of walk times to the 3 nearest train stations in Tokyo, routed on OpenStreetMap data.*

<!--more-->

It's common for Japanese job posting to include the walking time from their office to the nearest station e.g. "5 minute walk from Shibuya Station." 

I really like this transit-focused convention (what I would give for light-rail in Nashville) which made me curious if I could accurately estimate this for any job in Japan. So I made a micro-service I'm calling Toho (Japanese for "on foot" 徒歩).

 Instead of calling a routing API for every address, I used an H3 grid and precomputed the walk for every ~50m hexagon in Tokyo's 23 wards to the 3 nearest stations. 
 
 "How far of a walk is the nearest station?" now takes just a few milliseconds to answer, with zero API cost.

{{< image classes="fancybox center fig-100" src="/blog/2026/toho-catchments-shibuya.gif" title="Station catchments, then a jump to Shibuya Scramble Crossing" >}}

The station catchments view is probably my favorite part. Each colour is the area whose closest station on foot is the same station where the borders follow streets, rivers and rail lines rather than straight lines.

{{< image classes="fancybox center fig-100" src="/blog/2026/toho-click-around-shibuya.gif" title="Clicking around Shibuya" >}}

Click anywhere and you get the 3 nearest stations with routed distance (meters) and walking time in minutes, plus the straight-line distance for comparison. When you zoom in enough you can see the outlines are the individual H3 cells. Black dots are station entrances; white dots are station points, used where no entrance is mapped.

A few things I learned along the way:

- Precomputing saves a lot of time and money. I generated about ~322,000 cells for Tokyo and the whole grid fits in a ~20 MB DuckDB file
- Route to the station entrances, not the station center-point. Each station's centre point introduced about ~100m of extra distance. I fixed this by adding  entrance points from OpenStreetMap
- deck.gl's H3 remains awesome and a lot of fun to use. It quickly draws 300k+ hexagons in the browser, so the demo is lightweight - a single HTML file with no server
- Walk times in listings are surprisingly noisy (inaccurate). Spot checking, many of the claimed walking times didn't match what other services calculated (but maybe some of these employers like to power walk)

Built with Python, OpenStreetMap, pyosmium, pandana, H3, DuckDB and deck.gl.
