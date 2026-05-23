{{ config(materialized='table') }}

SELECT
    source_key,
    source_id,
    source_name,
    source_type,
    created_at
FROM {{ source('silver', 'dim_sources_clean') }}
