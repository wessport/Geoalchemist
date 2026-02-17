---
title: "Contributing to an Open Source POI Scraping Project"
author: "Wes"
date: 2019-11-15

autoThumbnailImage: false
thumbnailImagePosition: "left"
thumbnailImage: https://res.cloudinary.com/wessport/image/upload/v1767000000/placeholder_thumb.png
coverImage: https://res.cloudinary.com/wessport/image/upload/v1767000000/placeholder_cover.jpg
metaAlignment: center
coverMeta: in
comments: true

keywords:
- Python
- Scrapy
- Web Scraping
- POI Data
- Open Source

categories:
- Python

tags:
- scrapy
- web-scraping
- open-source
---

*How contributing to an open source project helped build a POI dataset that enhanced tens of thousands of job listings.*

<!--more-->

---

# The Project #

Our team needed point-of-interest (POI) data — addresses and coordinates for retail chains, restaurants, and service providers. Commercial datasets exist but are expensive and often stale.

An open source project called AllThePlaces collects this data by scraping company store locator pages. Contributors write "spiders" — Scrapy scripts that extract location data from specific websites. The project aggregates thousands of spiders into a regularly-updated POI dataset.

We started contributing spiders to fill gaps in the data we needed. The locations we collected fed into a database that powers job location enhancement — matching job postings to precise physical locations.

---

# Spider Week #

Once a quarter, the team ran a focused sprint on spider development. The goal: write as many spiders as possible for high-priority companies.

During one spider week, I contributed:
- **16 commits** to the project
- **12 new spiders** for different companies

That put me at **#6 on the all-time contributor list**.

The collaborative energy was high. We shared techniques, debugged together, and pushed through the tedious parts as a team. The result: significant expansion of our POI coverage in a single week.

---

# High-Impact Contributions #

Not all locations are equal. We prioritized spiders for companies with high job posting volume.

**College Locations**

One contribution I'm proud of was adding ~7,000 college and university locations to the database. Educational institutions are significant employers, and having precise campus coordinates improved job search accuracy for a large number of postings.

**Retail and Restaurant Chains**

High-impact companies often had the most difficult sites to scrape. The sites with anti-scraping measures required the most creativity — but they also had the most locations to capture.

---

# Technical Challenges #

Each spider presented unique challenges:

**Handling Rate Limits and Retries**

Some store locators aggressively rate-limited requests. The spider needed custom retry logic with exponential backoff:

```python
custom_settings = {
    'RETRY_TIMES': 5,
    'RETRY_HTTP_CODES': [500, 502, 503, 504, 403, 429],
    'DOWNLOAD_DELAY': 2,
}
```

**Address Parsing**

Many sites return addresses as single strings rather than structured fields. Extracting city, state, and postal code required parsing libraries like `usaddress`:

```python
import usaddress

def parse_address(self, address_string):
    try:
        parsed, addr_type = usaddress.tag(address_string)
        return {
            'street': parsed.get('AddressNumber', '') + ' ' + parsed.get('StreetName', ''),
            'city': parsed.get('PlaceName', ''),
            'state': parsed.get('StateName', ''),
            'postcode': parsed.get('ZipCode', ''),
        }
    except usaddress.RepeatedLabelError:
        return {'addr_full': address_string}
```

**Pagination and AJAX**

The most common issue: spiders that capture only the first page of results. Store locators often use pagination or AJAX calls that require following links or inspecting network requests to find the underlying API.

---

# Office Hours #

To spread knowledge across the team, I ran spider office hours — drop-in sessions where people could get help with:

- Python environment issues
- Scrapy configuration
- CSS/XPath selector debugging
- Handling pagination and AJAX content
- Dealing with anti-scraping measures

The most common blockers were environment setup and understanding Scrapy's asynchronous model. A 15-minute pairing session often unblocked days of frustration.

---

# Contribution Stats #

| Metric | Count |
|--------|-------|
| Spiders written | 12 |
| Commits | 16 |
| Issues filed | 36 |
| Pull requests reviewed | 8 |

The issues were for sites I identified as good candidates but didn't have time to write spiders for. Filing detailed issues — with notes on site structure, API endpoints, and data format — helped other contributors pick them up quickly.

---

# Code Review Catches Real Problems #

One spider I wrote initially captured ~400 locations. A teammate's code review caught issues:

- Missing pagination handling (only captured first page)
- Not following links to individual store pages for complete data
- Incorrect extraction of phone numbers

After fixes: **~1,200 locations** with complete data — 3x the original output.

Code review on scraping projects catches problems that are easy to miss when you're focused on getting *something* working.

---

# Downstream Impact #

The POI data we collected fed into a job enhancement system. When a job posting mentions a company name, the system looks up that company's locations to improve geocoding accuracy.

By the end of the initiative, our team's collective contributions had helped enhance **tens of thousands of jobs** with more precise location data.

---

# Lessons Learned #

**Start with the network tab.** Before writing code, understand what requests the site makes. Store locators often fetch JSON from an API endpoint that's easier to parse than HTML.

**Respect rate limits.** Aggressive scraping gets IPs blocked. Add delays, handle errors gracefully, and consider the impact on the sites you're scraping.

**File detailed issues.** Even when you don't have time to write a spider, documenting the site structure helps others. Include API endpoints, data formats, and pagination patterns.

**Code review is essential.** It's easy to miss pagination, edge cases, or data quality issues when you're focused on getting a working spider. A second set of eyes catches problems before they reach production.

**Contribute back.** Open source projects thrive on contributions. The AllThePlaces dataset benefits everyone who uses it — including the team that originally collected the data.
