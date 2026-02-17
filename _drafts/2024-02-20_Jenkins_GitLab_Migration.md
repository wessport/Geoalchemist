---
title: "Migrating Team Infrastructure from Jenkins to GitLab CI"
author: "Wes"
date: 2024-02-20

autoThumbnailImage: false
thumbnailImagePosition: "left"
thumbnailImage: https://res.cloudinary.com/wessport/image/upload/v1767000000/placeholder_thumb.png
coverImage: https://res.cloudinary.com/wessport/image/upload/v1767000000/placeholder_cover.jpg
metaAlignment: center
coverMeta: in
comments: true

keywords:
- DevOps
- CI/CD
- GitLab
- Jenkins
- Infrastructure

categories:
- DevOps
- Python

tags:
- gitlab-ci
- jenkins
- infrastructure
- migration
---

*Moving a team's entire CI/CD infrastructure to meet an organization-wide deadline.*

<!--more-->

---

# Results #

| Metric | Value |
|--------|-------|
| **Merge Requests** | 7 MRs across 6 unique projects |
| **Projects Migrated** | 1 app, 2 ORC tasks, 2 libraries |
| **Deadline** | Met organization-wide Jenkins retirement |
| **Downtime** | Zero disruption to team workflows |

---

# Background #

Our organization was retiring Jenkins. Every team had a deadline to migrate their pipelines to GitLab CI. For our data team, this meant independently migrating all of our tooling:

- 1 web application
- 2 scheduled task runners (ORC tasks)
- 2 shared libraries

The work touched 6 different repositories and required coordinating changes across all of them.

---

# Scoping the Work #

I started by auditing our Jenkins usage. Each project had different requirements:

| Project Type | Jenkins Usage | Migration Complexity |
|--------------|---------------|----------------------|
| Web app | Build, test, deploy | Medium |
| ORC tasks | Scheduled execution | High |
| Libraries | Build, test, publish | Low |

The ORC task runners were the trickiest. Jenkins handled scheduling natively, but GitLab CI treats scheduled pipelines differently — you configure them in the UI rather than in code.

---

# GitLab CI Configuration #

The core migration involved translating Jenkinsfiles to `.gitlab-ci.yml`. Here's a simplified example of what the task runner configuration looked like:

```yaml
stages:
  - build
  - test
  - deploy

variables:
  PYTHON_VERSION: "3.9"

build:
  stage: build
  script:
    - pip install -r requirements.txt
    - python setup.py build
  artifacts:
    paths:
      - dist/

test:
  stage: test
  script:
    - pip install pytest
    - pytest tests/

deploy:
  stage: deploy
  script:
    - ./deploy.sh
  only:
    - main
  when: manual
```

The `when: manual` flag was important for our deployment workflow — we wanted CI to validate changes automatically, but deployments required explicit approval.

---

# Handling Scheduled Tasks #

The scheduled task runners required additional setup. In Jenkins, cron expressions lived in the Jenkinsfile. In GitLab, schedules are configured through the web interface:

1. Navigate to CI/CD → Schedules
2. Create schedule with cron expression
3. Specify target branch and variables

This separation of concerns is actually cleaner — the pipeline definition stays in code, but operational scheduling is managed as infrastructure.

For documentation purposes, I added comments to the `.gitlab-ci.yml`:

```yaml
# Scheduling configured in GitLab UI
# Production: 0 6 * * * (6 AM daily)
# See: Settings → CI/CD → Schedules
```

---

# Library Publishing #

The shared libraries needed to publish to our internal package registry. GitLab CI integrates directly with GitLab Package Registry:

```yaml
publish:
  stage: deploy
  script:
    - pip install twine
    - python setup.py sdist bdist_wheel
    - twine upload --repository-url ${CI_API_V4_URL}/projects/${CI_PROJECT_ID}/packages/pypi dist/*
  only:
    - tags
```

The `CI_*` variables are injected by GitLab, eliminating the need for manual credential management.

---

# The Migration Process #

I approached the migration systematically:

1. **Week 1**: Migrate libraries (lowest risk, establishes patterns)
2. **Week 2**: Migrate web application (validate deployment workflow)
3. **Week 3**: Migrate ORC task runners (most complex, validate scheduling)
4. **Week 4**: Buffer for issues and documentation

In practice, the migration went faster than expected. Having clear patterns from the library migration made the later projects straightforward.

---

# Additional Mandates #

Alongside the Jenkins migration, I also helped the team respond to other organization-wide mandates:

- **Redash Sunsetting**: Migrated our Redash dashboards to the new internal dashboard platform in response to Redash being deprecated
- **Docker Desktop Removal**: Helped the team update their systems with a detailed guide to meet the guidance to remove Docker Desktop

Anticipating and responding to these mandates before they became urgent saved the team from scrambling at deadlines.

---

# Merge Request Summary #

The final tally — **7 merge requests** across **6 unique projects**:

| Repository | Changes |
|------------|---------|
| Library A | New `.gitlab-ci.yml`, remove Jenkinsfile |
| Library B | New `.gitlab-ci.yml`, remove Jenkinsfile |
| Web App | New `.gitlab-ci.yml`, update deploy scripts |
| ORC Task A | New `.gitlab-ci.yml`, configure schedules |
| ORC Task B | New `.gitlab-ci.yml`, configure schedules |
| Shared Config | Update CI templates |

The deadline was met with time to spare.

---

# Takeaways #

CI/CD migrations are mostly about understanding the conceptual differences between platforms rather than the syntax. Jenkins and GitLab CI accomplish the same goals but with different paradigms:

- Jenkins: Everything in code, including scheduling
- GitLab CI: Pipeline definition in code, operational config in UI

For teams considering a similar migration, start with your simplest projects to establish patterns, then apply those patterns to more complex ones.
