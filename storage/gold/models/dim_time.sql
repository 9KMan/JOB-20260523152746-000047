{{ config(materialized='table') }}

-- Generate time dimension from dates
WITH date_series AS (
    SELECT 
        DATEADD('day', row_number() - 1, DATE '2024-01-01') as date_key
    FROM TABLE(GENERATE_SERIES(1, 365*5))
)
SELECT
    date_key,
    DAYOFWEEK(date_key) as day_of_week,
    WEEKOFYEAR(date_key) as week_of_year,
    MONTH(date_key) as month,
    CASE 
        WHEN MONTH(date_key) <= 3 THEN 1
        WHEN MONTH(date_key) <= 6 THEN 2
        WHEN MONTH(date_key) <= 9 THEN 3
        ELSE 4
    END as quarter,
    CASE 
        WHEN DAYOFWEEK(date_key) IN (1, 7) THEN TRUE
        ELSE FALSE
    END as is_weekend
FROM date_series
