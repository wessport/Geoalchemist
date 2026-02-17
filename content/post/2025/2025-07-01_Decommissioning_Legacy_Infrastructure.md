---
title: "Decommissioning Legacy Infrastructure"
author: "Wes"
date: 2025-07-01

autoThumbnailImage: false
thumbnailImagePosition: "left"
thumbnailImage: https://res.cloudinary.com/wessport/image/upload/v1768857044/package-icon.png
coverImage: https://res.cloudinary.com/wessport/image/upload/v1768769858/dsc3850.jpg
metaAlignment: center
coverMeta: in
comments: true

keywords:
- Infrastructure
- Technical Debt
- Django
- AWS

categories:
- Infrastructure

tags:
- decommissioning
- technical-debt
- aws
---

*Shutting down a legacy Django application and modernizing 10+ repositories simultaneously.*

<!--more-->

---

# Background: Legacy Django Application #

Our team inherited a Django application (geodata-tools) that had been running for years. It served a handful of internal tools, but as our projects and services evolved, the orginal usecase for the tool had run its course. Most of its functionality had been replicated elsewhere or was just no longer needed.

The app was still running in Prod, backed by an Aurora database, registered in service catalogs, and subject to security scans. Every few months, something would require attention — a dependency update, a security config change, a cloud mandate.

The maintenance overhead wasn't justified by the value it provided to the team and I found myself increasingly busy fighting off tech debt. 

---

# The Decision to Decommission #

Decommissioning infrastructure is tricky. There's always uncertainty about what might break, who might still be using it, and what data might be lost.

Before proceeding, I went through a full audit:

1. **Usage** — traffic logs, a team survey - who was using the app and who would miss it the most?
2. **Dependencies** — what services and databases backed the app
3. **Data** — what needed to be archived vs. what could we let go
4. **Migration planning** — What functionality could be migrated to lightweight alternatives (scripts, etc.)

After putting together a plan and a host of jira tickets and an Epic later, I was ready to start the deprecation work.

---

# Execution: Django Decommission #

The shutdown followed a specific order:

```
1. Notify stakeholders (we gave a 4 weeks advance notice, since it was an internal tool, didn't need a long window)
2. Backup and archive Prod data
3. Spin down QA instance and resources
4. Monitor for issues (few days)
5. Spin down Prod instnace and resources
6. Backup and Delete Aurora databases (QA and Prod)
7. Archive GitLab repositories
8. Update service catalogs
9. Remove deployment pipelines
```

Each step had a rollback plan, though thankfully we didn't need them.

---

# Database Archival #

Before deleting anything, I created full database backups:

```sql
-- Create backup of all tables
mysqldump --host=prod-aurora-endpoint \
          --user=backup_user \
          --single-transaction \
          --routines \
          --triggers \
          geodata_tools > geodata_tools_final_backup.sql
```

The backups live in cold storage. If anyone needs historical data years from now, it's still retrievable.

---

# Repository Archival #

Rather than delete the repo, I archived it:

| Repository | Status |
|------------|--------|
| geodata-tools | Archived, read-only |

Archived repositories are set to read-only and remain searchable. Sometimes old code is useful as a reference. 
It's not uncommon to revist old projects where a tool or process suddenly becomes useful again.
Just a few days ago I revived an archived project from 3 years ago.

---

# What We Gained from Decommissioning #

| Category | Before | After |
|----------|--------|-------|
| Monthly AWS cost | Active | $0 |
| Security scan findings | Ongoing Updates | 0 |
| Code freshness mandates | Required | N/A |

Beyond the direct cost savings, the team no longer carries the update burden and tech debt. When the next cloud mandate comes through, we don't have to figure out how to update a Django app with complex environment dependencies.

---

# Repository Modernization & Auto Updates #

Alongside the decommission, I led an effort to modernize **10+ repositories** to achieve a 90-day code freshness goal.

This was mostly a security-focused initiative to help ensure our repos were up-to-date on security vulnerabilities. 

The work included:
- Implementing automated dependency management across Python libraries
- Configuring CODEOWNERS files for proper code review governance
- Establishing auto-dependency updater workflows that would automatically bump python dependencies
- Resolving critical build failures in library version bumping
- Migrating to Poetry for dependency configurations
- Fixing deployment pipeline configurations across Prod and QA environments

This work dove tailed conveniently with the decomissioning work as an opportunity to tidy up and improve our code base.

---
The main **win**: It enhanced our team's development velocity, standardized our projects' dependency management, made our projects more secure, and helped reduced our manual maintenance overhead. 
---

Instead of dependencies being updated sporadically, now they are automatically updated once a week.

---


# Related Cleanup #

The Django app wasn't the only legacy infrastructure we cleaned up. The same initiative also decommissioned:

- A Neighborhood Interactive Map hackathon project from a few years ago
- Associated databases
- Jenkins build configurations (part of earlier Jenkins→GitLab migration)

Each followed a similar pattern: audit usage, notify stakeholders, backup data, shut down, update catalogs.

---

# Results #

| Initiative | Impact |
|------------|--------|
| **Django App Decommissioned** | Eliminated maintenance burden |
| **Repositories Modernized** | 10+ repos updated for code freshness compliance |
| **Technical Debt Cleared** | Some repos had debt spanning 1,000+ days |
| **Code Freshness** | Met and automated our 100% compliance goal |

---

# Lessons Learned #

There's a cost involved with keeping a tool.  

Its important to re-assess periodically - is the cost of maintaining the tool worth the value you get out of it? I think there can be a hesitancy to let something go that people put a lot of time and effort into creating.

The hardest part is usually letting this tool go you've cared for for many years, but sometimes that's the right call so you can make other exciting things. Reducing technical debt freed up the team to focus on improving our other location services and create new better tools. 
