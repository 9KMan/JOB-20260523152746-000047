{{ config(materialized='view') }}

-- Stage bronze source data with deduplication
WITH source_data AS (
    SELECT
        source_id,
        data,
        ingested_at,
        metadata,
        -- Deduplicate by hashing the data
        MD5(CAST(data AS STRING)) as record_hash,
        ROW_NUMBER() OVER (
            PARTITION BY source_id 
            ORDER BY ingested_at DESC
        ) as rn
    FROM {{ source('bronze', 'sources') }}
)
SELECT
    source_id,
    data,
    ingested_at,
    metadata,
    record_hash
FROM source_data
WHERE rn = 1
