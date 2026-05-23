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

---

### Case Study 1: Real-Time Stock & Sales Platform
**Challenge:** Real-time inventory & sales visibility across 3,000+ POS terminals across hundreds of stores. Legacy systems couldn't support live reconciliation.

**Solution:**
- Designed Kafka-based event streaming for real-time POS ingestion
- Built Node.js microservices for high-throughput event processing
- Deployed Apache Cassandra cluster for transactional storage + Elasticsearch for sub-second inventory search
- Implemented Talend + Python ETL for daily Stock-On-Hand sync from SAP/Oracle/AS400
- Delivered Flutter apps for store managers to monitor & resync inventory

**Outcome:** ✅ Near real-time inventory visibility across all locations | ✅ Accurate reconciliation between POS, merchandising, and warehouse systems | ✅ Stable 24/7 performance under heavy transactional loads | ✅ Seamless coexistence of legacy and modern distributed systems

---

### Case Study 2: Multi-Source ETL Pipeline for Legacy Modernization
**Challenge:** Fragmented data across SAP, Oracle Retail, JDA, AS/400, and DB2 causing delays, inconsistencies, and manual reconciliation.

**Solution:**
- Architected high-volume ETL/ELT pipelines consolidating multiple legacy sources
- Automated scheduling with Prefect + distributed compute with Dask
- Built cross-system validation layers to ensure upstream/downstream data integrity
- Migrated critical workloads to modern distributed databases without downtime

**Outcome:** ✅ Reduced processing times from hours → minutes | ✅ Improved data consistency across enterprise systems | ✅ Enabled scalable, cloud-ready architecture while preserving legacy investments

---

### Case Study 3: Operational Data API Platform
**Challenge:** Business teams needed fast, reliable access to consolidated inventory & sales metrics via mobile and web dashboards.

**Solution:**
- Designed RESTful microservices using Node.js
- Optimized PostgreSQL queries + materialized views for reporting
- Added Redis caching to achieve <150ms P95 response times
- Integrated Kafka event stream for real-time data updates

**Outcome:** ✅ Sub-150ms API response for high-demand endpoints | ✅ Improved operational visibility for store managers | ✅ Enabled scalable, data-driven decision tools for business teams

---

**Frameworks & tools I work with:**

| Category | Tools |
|----------|-------|
| Orchestration | Apache Airflow, Prefect, Dagster |
| ETL/Processing | Python (Polars, Pandas), Dask, dbt Core, Talend |
| Storage | MinIO/S3, PostgreSQL, BigQuery, Snowflake, Delta Lake, Cassandra, Elasticsearch |
| BI/Visualization | Metabase, Grafana, DOMO, Looker, Streamlit |
| ML | MLflow, BQML, SageMaker batch inference, scikit-learn, PyTorch |
| Infrastructure | Docker Compose, Kubernetes, Terraform, GitHub Actions |

**Tech stack:** Python · Airflow · Kafka · Cassandra · Elasticsearch · PostgreSQL · Redis · Prefect · Dask · Flutter

GitHub: [github.com/9KMan](https://github.com/9KMan) | Open to remote contracts | GMT+7 (Bangkok)