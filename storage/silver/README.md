# Silver Layer

The Silver layer contains Cleansed, deduplicated, and validated data.

## Models

- `stg_sources` - Staged source data with deduplication
- `stg_daily_metrics` - Staged daily metrics
- `dim_sources_clean` - Cleansed dimension table

## Materialization

- Views for staging models
- Tables for dimension models

## Testing

Run `dbt test` to validate:
- Unique constraints
- Not null constraints
- Relationship integrity
