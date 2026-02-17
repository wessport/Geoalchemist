---
title: "Optimizing Geometric Search Grids"
author: "Wes"
date: 2022-06-06

autoThumbnailImage: false
thumbnailImagePosition: "left"
thumbnailImage: https://res.cloudinary.com/wessport/image/upload/v1660314226/noun-geometric-4653509_idrmdf.png
coverImage: https://res.cloudinary.com/wessport/image/upload/v1660314003/geometric_search_grid_sztpcm.png
metaAlignment: center
coverMeta: in
comments: true

keywords:
- blogging
- alltheplaces
- QGIS
- OSS

categories:
- Tech Blogging
- Python

tags:
- Tech blogging
- QGIS
- Python
- alltheplaces
- OSS

---

*How I leveraged a scientific paper on Multifractal Analysis to capture all of Dollar General's US stores*

<!--more-->

{{< grid_map >}}

# Background #

Before I dive into the spatial stuff, here's some background on why I sought out to create an optimized spatial search.

I like to contribute to a neat Open Source Project called [alltheplaces](https://github.com/alltheplaces/alltheplaces) 
(more on this project in future posts). The goal of the project is pretty simple - collect all 
store locations into a single geospatial dataset anyone can use.

# The DG Problem #

Not every company is great about listing their store locations. Sometimes companies have a list of stores that's easy to 
parse with a spider, other times they just provide a store lookup that takes a postal code and spits out the 
nearest stores.

Enter Dollar General (DG).

A scraper for DG already existed, but I noticed after mapping the data only the stores within a 100-mile  radius 
of the center of each state were actually collected. 

Weird, right? So what was going on?

![DG Problem](https://res.cloudinary.com/wessport/image/upload/c_scale,w_500/v1660318445/DG_problem_before_tgp81y.png)

The scraper was asking for stores in each state, **but only using the coordinates of the center of each state.**


# Potential Fixes #
Okay, so we need a solution that gives us national coverage for _**all stores**_.

### Option 1: Use Zipcodes ##
Sounds like a good approach at first **_but..._** the downside to this idea is a volume problem. There are ~ **42,000** zip 
codes in the US. That's nearly **3x** the number of Dollar General stores!

With a zip-code based search, we would be sending **way too many requests** to their website every second, _**dramatically 
slowing down the site**_.

![A witty gif](https://media.giphy.com/media/3o6MbnqLhX5tJ5wNQQ/giphy.gif)

Duplicates also become a major problem. With zipcodes we would be collecting every store within 100 
miles of each zipcode. There would be lots of overlap between nearby postal codes.

### Option 2: Create our own search grid ##
I couldn't be the first person to encounter this problem right? 

So I looked for scientific research papers related to optimizing search 
grids and found this awesome paper - [Barycentric ﬁxed-mass method for multifractal analysis by Kamer et al](https://www.researchgate.net/publication/256607366_The_Barycentric_Fixed_Mass_Method_for_Multifractal_Analysis).

![Another witty gif](https://media.giphy.com/media/5z0cCCGooBQUtejM4v/giphy-downsized.gif)

Using the methods contained in the paper above, I developed a Python script to generate a grid of minimally overlapping 
circles - each representing a 100mi search radius.

![Minimally Overlapping Search Grid](https://res.cloudinary.com/wessport/image/upload/v1660318157/minimally_overlapping_search_grid_hhyqip.png)
(**Source:** Kramer et al)

The centroid coordinates of each search radius are used in place of zipcodes for store locators that allow searches by 
coordinates. 

This drastically reduces the number of requests that are sent to the website from 42,000 to **773**.

### That's a 98% decrease!!! 

Because each search radius is minimally overlapping (~13%), the number of duplicates returned in each request is also greatly reduced.

<iframe width='100%' height='400px' src="https://api.mapbox.com/styles/v1/wporter/cl6qjbvbv000414qikre51aob.html?title=false&access_token=pk.eyJ1Ijoid3BvcnRlciIsImEiOiJjanphZDYwZHUwMDY4M29wY29nOHAzZWE3In0.Ou5txdwKKvL4qC-AYPR3UQ&zoomwheel=false#3.77/36.99/-96.25" title="Geometric Search Grid" style="border:none;"></iframe>

Win win.

# Results #

The locations represented in green were all the new locations we were able to capture thanks to the optimized search
grid. We were missing so much data originally! Our California data in particular is in much better shape now.

## Newly Captured DG Stores ##

![DG Stores After](https://res.cloudinary.com/wessport/image/upload/c_scale,w_500/v1660318444/DG_additions_after_jjbz0m.png)

