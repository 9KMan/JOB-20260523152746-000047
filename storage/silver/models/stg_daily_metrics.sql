{{ config(materialized='view') }}

-- Stage daily metrics from bronze
WITH metrics AS (
    SELECT
        date_key,
        source_id,
        SUM(record_count) as total_records,
        SUM(error_count) as total_errors,
        AVG(latency_p50_ms) as avg_latency_p50,
        AVG(latency_p99_ms) as avg_latency_p99,
        COUNT(DISTINCT date_key) as day_count,
        -- Deduplication
        MD5(CAST(COLLECT_LIST(date_key) AS STRING)) as dedup_hash,
        ROW_NUMBER() OVER (
            PARTITION BY date_key, source_id 
            ORDER BY MAX(ingested_at) DESC
        ) as rn
    FROM {{ source('bronze', 'fct_daily_aggregates') }}
    GROUP BY date_key, source_id
)
SELECT
    date_key,
    source_id,
    total_records,
    total_errors,
    avg_latency_p50,
    avg_latency_p99,
    day_count
FROM metrics
WHERE rn = 1
