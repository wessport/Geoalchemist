---
title: "Building Data Pipelines and Query Indexes from Scratch"
author: "Wes"
date: 2020-09-15

autoThumbnailImage: false
thumbnailImagePosition: "left"
thumbnailImage: https://res.cloudinary.com/wessport/image/upload/v1767000000/placeholder_thumb.png
coverImage: https://res.cloudinary.com/wessport/image/upload/v1767000000/placeholder_cover.jpg
metaAlignment: center
coverMeta: in
comments: true

keywords:
- Python
- Data Pipelines
- ETL
- Index Building

categories:
- Python
- Data Engineering

tags:
- data-pipelines
- etl
- python-architecture
---

*Extending an index builder to support new data sources and international markets.*

<!--more-->

---

# The Problem #

Our team needed to track how job geocoding quality changed over time. The existing index builder pulled data from a single source — a quality measurement task — and pushed it to an internal query index. But business requirements evolved:

1. The upstream quality task was migrating to a new system
2. We needed to support international markets, not just US
3. The data schema was changing

The challenge: extend the Python codebase to handle new data sources while maintaining backward compatibility with existing dashboards and consumers.

---

# The jobGeocodeDiff Index #

The index tracked the difference between what employers provided as job location versus what our geocoding system returned. This "diff" data powered quality metrics:

- What percentage of jobs geocode to the correct location?
- How often do we upgrade a city to a street address?
- What percentage fall back to less precise locations?

The index fed dashboards that stakeholders used to monitor geocoding accuracy across markets.

---

# Adding International Markets #

The original builder assumed US data. Adding international markets required:

1. **Multi-source fetching**: Different markets had different data sources
2. **Schema normalization**: Field names and formats varied
3. **Market-specific sampling**: Some markets had different sampling methodologies

I restructured the project to separate concerns:

```
index_builder/
├── sources/
│   ├── base.py          # Abstract source interface
│   ├── us_source.py     # US market data
│   └── intl_source.py   # International markets
├── transforms/
│   ├── geocode_diff.py  # Core transformation logic
│   └── sampling.py      # Sampling strategies
├── outputs/
│   └── index_writer.py  # Index upload
└── config/
    └── markets.yaml     # Market configuration
```

This structure made it straightforward to add new markets without touching the core transformation logic.

---

# Sampling for Quality Measurement #

A related challenge was populating quality measurement queues with representative job samples. The existing sampling methodology needed to be replicated in a data notebook environment so analysts could generate samples for manual review.

The sampling logic weighted jobs by search volume:

```python
def sample_jobs(df: pd.DataFrame, sample_size: int) -> pd.DataFrame:
    """
    Weight sampling by query volume to prioritize high-traffic jobs.
    """
    weights = df['query_count'] / df['query_count'].sum()
    return df.sample(n=sample_size, weights=weights, random_state=42)
```

Uniform random sampling would over-represent long-tail jobs that few users see. Weighted sampling aligned quality metrics with actual user experience.

---

# Regression Report Tooling #

A pain point in the quality workflow was analyzing bulk change regression reports. These reports — HTML files showing how database changes affected geocoding — were so large they wouldn't load in browsers.

I built a tool to parse these reports as web pages and convert them to CSV:

```python
from bs4 import BeautifulSoup
import pandas as pd

def parse_regression_report(html_path: str) -> pd.DataFrame:
    """
    Parse a regression report HTML file into a sortable DataFrame.
    """
    with open(html_path, 'r') as f:
        soup = BeautifulSoup(f, 'lxml')
    
    rows = []
    for tr in soup.select('table.regressions tr'):
        cells = [td.text.strip() for td in tr.select('td')]
        if cells:
            rows.append(cells)
    
    return pd.DataFrame(rows, columns=['location', 'before', 'after', 'impact'])
```

Some reports exceeded 8MB of HTML. The parser used a specialized HTML library (`lxml`) that could handle massive files without crashing, unlike the browser.

---

# Supporting New Data Fetch Methods #

The internal query language had evolved, and the index builder needed to support new fetching methods. The original code used direct database queries, but the new approach leveraged the query language's native capabilities.

I added an adapter layer:

```python
from typing import Protocol

class DataFetcher(Protocol):
    def fetch(self, market: str, date_range: tuple) -> pd.DataFrame:
        ...

class LegacyFetcher:
    """Direct database queries for backward compatibility."""
    
    def fetch(self, market: str, date_range: tuple) -> pd.DataFrame:
        query = self._build_query(market, date_range)
        return pd.read_sql(query, self.connection)

class NativeFetcher:
    """Native query language fetching."""
    
    def fetch(self, market: str, date_range: tuple) -> pd.DataFrame:
        query = self._build_native_query(market, date_range)
        return self.client.execute(query).to_dataframe()
```

The protocol-based approach let us switch between fetchers without changing downstream code. We could run both in parallel during migration to verify consistency.

---

# Results #

The updated index builder:

- Supported **US and international markets** from a single codebase
- Handled the **upstream data source migration** without breaking dashboards
- Ran in production for years, supporting markets we hadn't anticipated

The regression report parser unblocked analysts reviewing large database updates — a process that had been stalled for days.

---

# Takeaways #

**Design for extensibility.** Market expansion was on the roadmap, so the code was structured to accommodate it. Adding a new market required only configuration, not code changes.

**Build tooling for pain points.** The regression report parser took a few hours to build but saved days of frustration every time someone needed to review a large report.

**Use adapter patterns.** When data sources change, adapter layers isolate the impact. Downstream code doesn't need to know which fetcher is being used.

**Test at integration boundaries.** Mock data sources at the interface boundary to test transformation logic independently.
