{{ config(materialized='table') }}

-- SCD Type 2 for customers
WITH customer_changes AS (
    SELECT
        {{ dbt_utils.generate_surrogate_key(['customer_id', 'change_hash']) }} as customer_key,
        customer_id,
        name,
        email,
        address,
        effective_date,
        COALESCE(
            LEAD(effective_date) OVER (PARTITION BY customer_id ORDER BY effective_date),
            '9999-12-31'
        ) as expiry_date,
        CASE 
            WHEN LEAD(effective_date) OVER (PARTITION BY customer_id ORDER BY effective_date) IS NULL 
            THEN TRUE 
            ELSE FALSE 
        END as is_current
    FROM (
        SELECT 
            customer_id,
            name,
            email,
            address,
            effective_date,
            MD5(CONCAT(name, email, address)) as change_hash
        FROM {{ source('silver', 'stg_customers') }}
        GROUP BY customer_id, name, email, address, effective_date
    )
)
SELECT * FROM customer_changes
