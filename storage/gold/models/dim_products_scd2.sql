{{ config(materialized='table') }}

-- SCD Type 2 for products
WITH product_changes AS (
    SELECT
        {{ dbt_utils.generate_surrogate_key(['product_id', 'change_hash']) }} as product_key,
        product_id,
        name,
        category,
        price,
        effective_date,
        COALESCE(
            LEAD(effective_date) OVER (PARTITION BY product_id ORDER BY effective_date),
            '9999-12-31'
        ) as expiry_date,
        CASE 
            WHEN LEAD(effective_date) OVER (PARTITION BY product_id ORDER BY effective_date) IS NULL 
            THEN TRUE 
            ELSE FALSE 
        END as is_current
    FROM (
        SELECT 
            product_id,
            name,
            category,
            price,
            effective_date,
            MD5(CONCAT(name, category, CAST(price AS STRING))) as change_hash
        FROM {{ source('silver', 'stg_products') }}
        GROUP BY product_id, name, category, price, effective_date
    )
)
SELECT * FROM product_changes
