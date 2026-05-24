# Data Aggregation Pipeline — Specification

## 1. Project Overview

**Client:** Seeking a full-stack engineer to build an automated data aggregation pipeline with data storage, BI/reporting integration, and ML components.

**Core deliverables:**
- Automated data aggregation pipeline (collect from multiple sources)
- Data storage solution (warehousing + lake)
- BI/reporting platform integration (live dashboards, data infrastructure)
- API connections and automation logic
- Deployment pipeline

**Tech stack indicated:** Python, Machine Learning, Data Warehousing, BI layers, live dashboards, data infrastructure, API connections, automation, deployment

---

## 2. Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        DATA SOURCES                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────────┐ │
│  │  APIs    │  │ Databases│  │  Files   │  │  Streams/Events │ │
│  │ (REST)   │  │ (SQL/NoSQL)│ │(CSV/JSON)│  │  (Kafka/Pubsub)  │ │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────────┬─────────┘ │
└───────┼─────────────┼─────────────┼──────────────────┼──────────┘
        │             │             │                  │
        ▼             ▼             ▼                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                     INGESTION LAYER                              │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Python ETL/ELT Pipeline                                 │   │
│  │  • Connectors: REST, SQL, S3, GCS, Kafka                 │   │
│  │  • Schema detection & validation                          │   │
│  │  • Watermark-based incremental CDC                       │   │
│  │  • Error handling + dead-letter queue                     │   │
│  └──────────────────────────────────────────────────────────┘   │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                    STORAGE LAYER (Medallion)                     │
│                                                                   │
│  ┌────────────────┐  ┌────────────────┐  ┌───────────────────┐     │
│  │  Bronze        │→ │  Silver        │→ │  Gold             │     │
│  │  (Raw Parquet) │  │  ( Cleansed ) │  │  (Star Schema)    │     │
│  │  Raw ingest     │  │  Deduplicated  │  │  Dimension tables │     │
│  │  Partitioned    │  │  Validated     │  │  Fact aggregates  │     │
│  └────────────────┘  └────────────────┘  └───────────────────┘     │
│                                                                   │
│  Storage: MinIO / S3-compatible + dbt transformations              │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                    BI / REPORTING LAYER                          │
│  ┌───────────────┐  ┌──────────────────┐  ┌──────────────────┐   │
│  │  Live         │  │  Self-service    │  │  Scheduled       │   │
│  │  Dashboards   │  │  Analytics       │  │  Reports         │   │
│  │  (Metabase/   │  │  (Looker-style)  │  │  (email/slack)    │   │
│  │   Superset)   │  │                  │  │                  │   │
│  └───────────────┘  └──────────────────┘  └──────────────────┘   │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                    ML / ADVANCED ANALYTICS                       │
│  ┌──────────────────┐  ┌──────────────────────────────────────┐   │
│  │  Feature Store   │  │  ML Pipelines (training, inference)  │   │
│  │  (feast or custom)│ │  scikit-learn / PyTorch / MLflow     │   │
│  └──────────────────┘  └──────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                    ORCHESTRATION                                 │
│  Apache Airflow — DAG-based scheduling, retry, alerting          │
└─────────────────────────────────────────────────────────────────┘
```

---

## 3. Core Workstreams

### Workstream 1 — Ingestion Pipeline
- **Source connectors** for REST APIs, SQL databases, S3/GCS files, Kafka/Kinesis streams
- **Watermark-based incremental loading** — track last-processed timestamp per source
- **Schema validation** — reject or quarantine records that don't match expected schema
- **Dead-letter queue** — failed records go to DLQ for manual inspection/retry
- **Parallel processing** — concurrent source fetching for speed

### Workstream 2 — Medallion Storage (Bronze → Silver → Gold)
- **Bronze:** Raw Parquet files, partitioned by date, immutable
- **Silver:** Cleansed, deduplicated, schema-enforced tables (dbt)
- **Gold:** Star schema — fact tables (daily aggregates) + dimension tables (customers, products, time)
- **SCD Type 2** on slowly-changing dimensions (customer address history, etc.)

### Workstream 3 — BI / Reporting Integration
- **Live dashboards** connected to Gold layer via read replica or direct BI connection
- **Metric store** — consistent definitions across all reports
- **Scheduled reports** — email/Slack delivery of PDF/CSV snapshots
- **Row-level security** — multi-tenant data isolation

### Workstream 4 — ML Pipeline
- **Feature engineering** — compute features from Gold layer
- **Model training** — scikit-learn / PyTorch with experiment tracking (MLflow)
- **Batch inference** — score new records as they enter the pipeline
- **Model monitoring** — drift detection, accuracy tracking

### Workstream 5 — Orchestration & Deployment
- **Airflow DAGs** — schedule, monitor, alert on failure
- **Infrastructure as code** — Terraform/Pulumi for cloud resources
- **CI/CD** — GitHub Actions for test + deploy
- **Containerization** — Docker + Docker Compose for local dev, Kubernetes for prod

---

## 4. Data Model

### Gold Layer — Star Schema

**Fact Table: `fct_daily_aggregates`**
| Column | Type | Description |
|---|---|---|
| date_key | DATE | Partition key |
| source_id | VARCHAR | Data source identifier |
| record_count | BIGINT | Number of records processed |
| error_count | BIGINT | Number of failed records |
| latency_p50_ms | INT | P50 processing latency |
| latency_p99_ms | INT | P99 processing latency |

**Dimension Table: `dim_sources`**
| Column | Type | Description |
|---|---|---|
| source_id | VARCHAR | PK |
| source_name | VARCHAR | Human-readable name |
| source_type | VARCHAR | api / database / file / stream |
| created_at | TIMESTAMP | |

**Dimension Table: `dim_time`**
| Column | Type | Description |
|---|---|---|
| date_key | DATE | PK |
| day_of_week | INT | 1-7 |
| week_of_year | INT | 1-53 |
| month | INT | 1-12 |
| quarter | INT | 1-4 |
| is_weekend | BOOLEAN | |

---

## 5. API Design

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/v1/pipeline/trigger` | Manually trigger a DAG run |
| GET | `/api/v1/pipeline/status/{dag_id}` | Get DAG run status |
| GET | `/api/v1/sources` | List registered data sources |
| POST | `/api/v1/sources` | Register a new data source |
| GET | `/api/v1/reports` | List scheduled reports |
| POST | `/api/v1/reports` | Create a scheduled report |
| GET | `/api/v1/metrics/summary` | Aggregate pipeline metrics |

---

## 6. Technical Decisions

1. **Medallion architecture** over raw-to-prod direct write — ensures data quality gates at each layer
2. **Watermark-based CDC** over full re-loads — cost-effective for large source tables
3. **dbt for Silver/Gold transformations** — version-controlled, testable, documented
4. **Airflow over bare cron** — retry logic, alerting, visual DAG dependency graph are essential for production
5. **Parquet over CSV for storage** — columnar, compressed, schema evolution support
6. **MLflow for experiment tracking** — unified registry for models + parameters + metrics
7. **MinIO for local dev, S3 for prod** — same API, no code changes needed

---

## 7. Out of Scope
- Real-time streaming (micro-batches only, not sub-second)
- Custom ML model architecture design (we integrate existing models)
- Mobile app development
- End-user dashboard building (we build the data layer, not the frontend)

---

## 8. Success Metrics
- All source connectors healthy with <1% error rate
- Pipeline completes within defined SLA per DAG
- Gold layer 100% in sync with source data within 1 DAG cycle
- Zero data incidents (missing data, wrong aggregates) in 30-day period
- ML models retrained and redeployed automatically on schedule