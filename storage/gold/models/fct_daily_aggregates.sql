{{ config(materialized='table') }}

-- Fact table: daily aggregates
SELECT
    d.date_key,
    s.source_key,
    s.source_id,
    COALESCE(m.total_records, 0) as record_count,
    COALESCE(m.total_errors, 0) as error_count,
    COALESCE(m.avg_latency_p50, 0) as latency_p50_ms,
    COALESCE(m.avg_latency_p99, 0) as latency_p99_ms
FROM {{ ref('dim_time') }} d
CROSS JOIN {{ ref('dim_sources') }} s
LEFT JOIN {{ source('silver', 'stg_daily_metrics') }} m
    ON d.date_key = m.date_key
    AND s.source_id = m.source_id
WHERE d.date_key >= '2024-01-01'
