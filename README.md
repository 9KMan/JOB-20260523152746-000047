# Data Aggregation Pipeline — Production-Ready PoC

## 🎯 Business Problem Solved

Organizations waste 20+ hours/week manually aggregating data from multiple sources (REST APIs, SQL databases, S3 files, Kafka streams) into a coherent analytics layer. Bad records silently break dashboards. Schema changes in source systems drop fields without warning. This pipeline solves end-to-end data delivery: ingest → cleanse → warehouse → BI/ML — with zero manual intervention after setup.

## 🏗 Technical Approach

```
┌──────────────────────────────────────────────────────────────┐
│  DATA SOURCES                                                │
│  REST APIs · SQL Databases · S3/GCS Files · Kafka Streams    │
└──────────────────────┬─────────────────────────────────────┘
                       ▼
┌──────────────────────────────────────────────────────────────┐
│  INGESTION LAYER                                             │
│  Watermark CDC · Schema Validation · Dead-Letter Queue        │
│  Parallel connector execution                                 │
└──────────────────────┬─────────────────────────────────────┘
                       ▼
┌──────────────────────────────────────────────────────────────┐
│  MEDALLION STORAGE (MinIO/S3)                                 │
│  Bronze (Raw Parquet) → Silver (dbt cleanse) → Gold (Star)   │
│  SCD Type 2 on dimension tables                               │
└──────────────────────┬─────────────────────────────────────┘
                       ▼
┌───────────────────────┬──────────────────────┬──────────────┐
│  BI LAYER             │  ML LAYER             │  ORCHESTRATION│
│  Live dashboards      │  Feature store        │  Apache Airflow│
│  (Metabase/Grafana)   │  Training + inference │  DAG scheduling │
└───────────────────────┴──────────────────────┴──────────────┘
```

## 📦 What You Get

- **Production-ready ETL pipeline** with watermark-based incremental CDC (no full re-loads), parallel source connectors, and dead-letter queue for failed records
- **Medallion architecture** — Bronze/Silver/Gold on MinIO + dbt transformations, SCD Type 2 dimensions
- **Airflow DAG library** — ingestion, bronze→silver, silver→gold, ML training, ML inference, BI refresh
- **ML feature store** — batch feature computation + inference endpoints + training pipeline
- **Terraform + Kubernetes configs** for cloud deployment
- **API service** with REST endpoints for pipeline status and manual triggers

## 🚀 Quick Start

> **Note:** This is a data pipeline platform — local Quick Start runs the Docker Compose stack with a simulated source.

```bash
git clone https://github.com/9KMan/JOB-20260523152746-000047
cd JOB-20260523152746-000047

# Install Python deps
pip install -r requirements.txt
pip install -r ingestion/requirements.txt
pip install -r api/requirements.txt
pip install -r ml/requirements.txt
pip install -r orchestration/requirements.txt

# Start pipeline (MinIO + Airflow + API)
docker-compose up -d

# Simulate a source ingestion run
python ingestion/pipeline.py --dry-run

# Check API
curl http://localhost:8000/health
```

## 👨‍💻 About the Architect

**Mongkolpoj Phanutaecha** — Principal Data Platform Architect | 15+ years building production data systems

**Recent relevant experience:**
- **Logistics SaaS ETL** (10M records/day) — Built medallion architecture from scratch for a 50-person data team. Migrated from raw SQL joins to Airflow + dbt + Metabase. Reduced dashboard refresh latency from 45 min to <8 min.
- **Fintech ML feature store** — Designed Spark + Feast feature store for a lending platform. 200+ batch features, sub-100ms online serving p99 latency.
- **E-commerce aggregation hub** — Multi-source pipeline (5 sources, 3 warehouses, nightly + micro-batch) with unified schema normalization. Saved 20 hr/week of manual data wrangling.

**Frameworks & tools I work with:**

| Category | Tools |
|----------|-------|
| Orchestration | Apache Airflow, Prefect, Dagster |
| ETL/Processing | Python (Polars, Pandas), Apache Spark (PySpark), dbt Core |
| Storage | MinIO/S3, PostgreSQL, BigQuery, Snowflake, Delta Lake |
| BI/Visualization | Metabase, Grafana, DOMO, Looker, Streamlit |
| ML | MLflow, BQML, SageMaker batch inference, scikit-learn, PyTorch |
| Infrastructure | Docker Compose, Kubernetes, Terraform, GitHub Actions |

**Tech stack:** Python · Airflow · dbt · MinIO · PostgreSQL · Docker · Kubernetes · Terraform

GitHub: [github.com/9KMan](https://github.com/9KMan) | Open to remote contracts | GMT+7 (Bangkok)