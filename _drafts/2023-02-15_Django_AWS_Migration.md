---
title: "Migrating a Django App to AWS"
author: "Wes"
date: 2023-02-15

autoThumbnailImage: false
thumbnailImagePosition: "left"
thumbnailImage: https://res.cloudinary.com/wessport/image/upload/v1767000000/placeholder_thumb.png
coverImage: https://res.cloudinary.com/wessport/image/upload/v1767000000/placeholder_cover.jpg
metaAlignment: center
coverMeta: in
comments: true

keywords:
- Django
- AWS
- Terraform
- Cloud Migration
- Database

categories:
- DevOps
- Python

tags:
- django
- aws
- terraform
- cloud-migration
---

*100% uptime migration of a Django application and database to AWS.*

<!--more-->

---

# Results #

| Metric | Result |
|--------|--------|
| Downtime | **0%** — maintained full uptime throughout migration |
| Epic Scope | 10 tickets spanning code, database, infrastructure |
| Engineering Level | Completed as an engineer-level project |
| Deadline | Met organization-wide AWS mandate |

---

# The Context #

Our team maintained a Django application (geodata-tools) that had been running on legacy infrastructure for years. The organization was consolidating everything to AWS with a hard deadline — part of a company-wide cloud mandate.

The application served internal tools used daily by analysts. The Places DB processor alone handled over 224,000 new additions, supporting key initiatives across the organization. Any significant downtime would directly impact team productivity.

I independently scoped, planned, and executed the entire migration as an engineer-level project.

---

# Planning the Migration #

I scoped the project into an Epic with 10 tickets covering:

1. Terraform configuration for AWS resources
2. Application code updates for new environment
3. Database backup strategy
4. Database migration to Aurora
5. DNS and networking changes
6. Testing in QA environment
7. Production cutover plan
8. Rollback procedures
9. Documentation updates
10. Decommission of old infrastructure

Each ticket had clear acceptance criteria and dependencies mapped. The order of operations was critical for achieving zero downtime.

---

# Learning Terraform #

This was my first significant Terraform project. I learned to utilize Terraform to configure and provision AWS resources. The concepts map directly to what you'd do manually in the AWS console, but with reproducibility.

Basic resource definition:

```hcl
resource "aws_instance" "app_server" {
  ami           = "ami-0123456789abcdef0"
  instance_type = "t3.medium"
  
  vpc_security_group_ids = [aws_security_group.app_sg.id]
  subnet_id              = aws_subnet.private.id
  
  tags = {
    Name        = "geodata-tools-app"
    Environment = "production"
  }
}
```

The real value of Terraform is reproducibility. After setting up QA, standing up an identical production environment was a single command.

---

# Database Migration to Aurora #

The database contained years of accumulated data. Losing any of it wasn't an option.

I backed up, migrated, and decommissioned our Quartermaster database to an AWS Aurora database while maintaining 100% uptime of the application.

Migration approach:

1. Create Aurora PostgreSQL instance in AWS
2. Take full backup of source database
3. Restore backup to Aurora
4. Set up ongoing replication during transition
5. Cut over application to new database
6. Verify data integrity
7. Decommission old database

```bash
# Backup
pg_dump -h old-host -U admin -d geodata_prod > geodata_backup.sql

# Restore to Aurora
psql -h new-aurora-endpoint -U admin -d geodata_prod < geodata_backup.sql
```

The replication step was insurance. If anything went wrong after cutover, we could quickly fall back.

---

# Aurora Configuration #

Aurora required specific configuration for our use case:

```hcl
resource "aws_rds_cluster" "geodata" {
  cluster_identifier      = "geodata-cluster"
  engine                  = "aurora-postgresql"
  engine_version          = "13.7"
  database_name           = "geodata_prod"
  master_username         = var.db_username
  master_password         = var.db_password
  backup_retention_period = 7
  preferred_backup_window = "03:00-04:00"
  
  vpc_security_group_ids = [aws_security_group.db_sg.id]
  db_subnet_group_name   = aws_db_subnet_group.geodata.name
  
  skip_final_snapshot = false
  final_snapshot_identifier = "geodata-final-snapshot"
}

resource "aws_rds_cluster_instance" "geodata" {
  identifier         = "geodata-instance-1"
  cluster_identifier = aws_rds_cluster.geodata.id
  instance_class     = "db.r5.large"
  engine             = aws_rds_cluster.geodata.engine
  engine_version     = aws_rds_cluster.geodata.engine_version
}
```

Key decisions:
- 7-day backup retention for safety
- Private subnet only (no public access)
- Final snapshot required before any deletion

---

# Application Updates #

The Django app needed updates to work with the new infrastructure:

**Database connection:**
```python
# settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'HOST': os.environ.get('DB_HOST'),
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'PORT': '5432',
        'OPTIONS': {
            'sslmode': 'require',
        }
    }
}
```

**Static files to S3:**
```python
# settings.py
AWS_STORAGE_BUCKET_NAME = os.environ.get('S3_BUCKET')
AWS_S3_REGION_NAME = 'us-east-1'
STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
```

Environment variables replaced hardcoded values, making the same code work in QA and production.

---

# Zero-Downtime Cutover #

The cutover sequence:

```
T-30min: Final database sync from old to new
T-15min: Verify sync completed successfully
T-5min:  Stop writes to old database
T-0:     Update DNS to point to new app server
T+5min:  Verify application responding
T+30min: Confirm all functionality working
T+24hr:  Remove old infrastructure
```

DNS TTL was set low (60 seconds) a week before migration to ensure fast propagation.

Actual downtime: effectively zero. Users experienced a brief moment where requests went to the new infrastructure, but the application was already running and database was synced.

---

# Verification Checklist #

Post-migration verification:

| Check | Method | Result |
|-------|--------|--------|
| App responds | HTTP health check | ✓ |
| Database connected | Django management command | ✓ |
| Data intact | Row counts match | ✓ |
| Static files load | Manual spot check | ✓ |
| Background jobs run | Job queue dashboard | ✓ |
| Logs flowing | CloudWatch check | ✓ |

```bash
# Data integrity check
old_count=$(psql -h old-host -c "SELECT COUNT(*) FROM main_table")
new_count=$(psql -h aurora-endpoint -c "SELECT COUNT(*) FROM main_table")

if [ "$old_count" = "$new_count" ]; then
    echo "Row counts match: $old_count"
else
    echo "MISMATCH: old=$old_count, new=$new_count"
fi
```

---

# Decommissioning #

After 24 hours of stable operation on AWS, decommission began:

1. Final backup of old database (archive)
2. Terminate old application servers
3. Remove old DNS records
4. Archive Terraform state for old infrastructure
5. Update all documentation

The old infrastructure was kept available (powered off) for one week before final deletion, just in case.

---

# Lessons #

**Test the full migration in QA first.** The QA migration surfaced several issues (missing environment variables, security group rules) that would have caused production problems.

**Terraform state is precious.** Back up state files. Losing state means Terraform can't manage existing resources.

**Low DNS TTL early.** Set TTL to 60 seconds a week before migration. Waiting until migration day risks slow propagation.

**Keep the rollback path clear.** For 24 hours post-migration, we could have switched back to old infrastructure within minutes. That safety net made the cutover less stressful.

---

# Outcome #

The migration completed on schedule with 100% uptime. The application now runs on modern infrastructure with proper monitoring, automated backups, and infrastructure-as-code.

The geodata-tools app processed over 224,000 new Places DB additions after the migration, supporting the "Increase Location Enhancement in International Markets" initiative without interruption.

Total project time: approximately 3 weeks from planning to decommission of old infrastructure.
