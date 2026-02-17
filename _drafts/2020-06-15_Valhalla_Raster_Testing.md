---
title: "Building a Python Module for Travel Time Raster Testing"
author: "Wes"
date: 2020-06-15

autoThumbnailImage: false
thumbnailImagePosition: "left"
thumbnailImage: https://res.cloudinary.com/wessport/image/upload/v1767000000/placeholder_thumb.png
coverImage: https://res.cloudinary.com/wessport/image/upload/v1767000000/placeholder_cover.jpg
metaAlignment: center
coverMeta: in
comments: true

keywords:
- Python
- Valhalla
- GDAL
- Geospatial
- Raster Data

categories:
- GIS
- Python

tags:
- valhalla
- gdal
- raster
- performance
---

*Reducing raster validation from days to under a minute with Valhalla and GDAL.*

<!--more-->

---

# The Problem #

Our team was developing travel time rasters — grid-based datasets that encode how long it takes to reach any point from a given origin. These rasters powered commute time search features.

The testing bottleneck: validating a raster required running QGIS least-cost-path tools, which took **over a day for a single raster**. With dozens of iterations needed to tune the product, this was unsustainable.

We needed two things:
1. **Fast iteration** — test multiple raster versions per day, not per week
2. **Production-compatible tooling** — use tools that engineering could implement, not desktop GIS software

---

# The Solution: Valhalla + GDAL #

I built a Python module that combined two open source tools:

- **Valhalla**: Open-source routing engine that calculates actual travel times along road networks
- **GDAL**: Geospatial Data Abstraction Library for raster manipulation

The approach: generate "ground truth" travel times from Valhalla for a sample of points, then compare those against what the raster predicted.

```
Raster (our product)     Valhalla (ground truth)
      ↓                         ↓
  Sample points ───────> Compare times
                              ↓
                    Error metrics (MAE, RMSE)
```

This let us validate raster accuracy without running expensive least-cost-path calculations.

---

# First Full Python Module #

This was the **first fully-fledged Python module** I developed on my own. I structured it for reusability:

```
valhalla_commute/
├── __init__.py
├── raster.py        # GDAL raster operations
├── routing.py       # Valhalla API client
├── sampling.py      # Point generation strategies
├── validation.py    # Comparison and metrics
└── cli.py           # Command-line interface
```

The `raster.py` module handled reading travel times from raster cells:

```python
from osgeo import gdal
import numpy as np

class TravelTimeRaster:
    def __init__(self, filepath: str):
        self.ds = gdal.Open(filepath)
        self.transform = self.ds.GetGeoTransform()
        self.data = self.ds.ReadAsArray()
    
    def get_travel_time(self, lat: float, lon: float) -> float:
        """Get travel time in minutes for a coordinate."""
        col = int((lon - self.transform[0]) / self.transform[1])
        row = int((lat - self.transform[3]) / self.transform[5])
        return self.data[row, col]
```

Clean separation of concerns meant I could swap out the routing engine or raster library without rewriting the validation logic.

---

# Valhalla Integration #

Valhalla exposes an HTTP API for routing. I set up Docker containers to run Valhalla locally with OpenStreetMap data:

```bash
docker run -d -p 8002:8002 \
  -v ~/osm-data:/data \
  valhalla/valhalla:latest
```

The routing client abstracted the API details:

```python
import requests

class ValhallaClient:
    def __init__(self, host: str = "localhost", port: int = 8002):
        self.base_url = f"http://{host}:{port}"
    
    def get_travel_time(
        self, 
        origin: tuple, 
        destination: tuple, 
        mode: str = "auto"
    ) -> float:
        """Get travel time in minutes between two points."""
        payload = {
            "locations": [
                {"lat": origin[0], "lon": origin[1]},
                {"lat": destination[0], "lon": destination[1]}
            ],
            "costing": mode
        }
        
        response = requests.post(
            f"{self.base_url}/route",
            json=payload
        )
        
        data = response.json()
        return data["trip"]["summary"]["time"] / 60
```

---

# Performance Results #

The improvement was dramatic:

| Method | Time per Raster | Notes |
|--------|-----------------|-------|
| QGIS least-cost-path | 24+ hours | Manual, desktop-only |
| Valhalla validation | **< 1 minute** | 1000 sample points |

From a multi-day process to under a minute — a **1000x+ improvement** in validation speed.

This meant we could test dozens of raster iterations in the time it previously took to test one. The project velocity increased significantly.

---

# Docker and VM Setup #

Setting up Valhalla locally required Docker knowledge, but I documented the full process:

1. Install Docker
2. Download OSM data for target region
3. Build Valhalla tiles (one-time, ~2 hours)
4. Run the container
5. Execute validation script

The one-time tile building was the slow part. Once tiles were built, spinning up a Valhalla instance took seconds.

For team use, I also set up a persistent VM running Valhalla so others didn't need to manage Docker locally.

---

# Expert-Level Raster Work #

Building this tool required deep understanding of raster data:

- **Coordinate transforms**: Converting lat/lon to pixel coordinates using geotransform arrays
- **NoData handling**: Recognizing and excluding invalid cells from sampling
- **Resolution tradeoffs**: Balancing accuracy vs. file size for different use cases
- **Projection systems**: Ensuring consistent coordinate references between raster and routing

I also learned to hold GDAL objects in memory via Python to keep processing as fast as possible — a technique that wasn't obvious from the documentation.

---

# Remote Work Advantage #

This project happened during a period of remote work. The distraction-free environment was actually a significant advantage for this type of work.

Building complex logic that spans multiple libraries — GDAL, Valhalla, coordinate systems, raster math — requires deep focus. Having uninterrupted blocks of time made it possible to hold the entire system in my head while developing.

---

# Takeaways #

**Performance bottlenecks are worth addressing directly.** A multi-day testing cycle made iteration painful and slowed the entire project. Investing time in tooling paid off immediately.

**Module structure matters.** Clean separation of concerns made the code reusable and maintainable. Other team members could use the validation module without understanding the implementation details.

**Documentation enables adoption.** The Docker setup guide and VM configuration meant the team could run validations independently, not just me.

**Use the right tools for production.** By using Valhalla instead of desktop GIS tools, we validated with the same routing engine that engineering could deploy. No translation layer needed.
