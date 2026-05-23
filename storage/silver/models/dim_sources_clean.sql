{{ config(materialized='table') }}

-- Dimension table for sources with cleansing
SELECT
    {{ dbt_utils.generate_surrogate_key(['source_id']) }} as source_key,
    source_id,
    data['source_name']::VARCHAR as source_name,
    data['source_type']::VARCHAR as source_type,
    data['created_at']::TIMESTAMP as created_at,
    ingested_at as cleaned_at
FROM {{ ref('stg_sources') }}
WHERE record_hash IS NOT NULL
