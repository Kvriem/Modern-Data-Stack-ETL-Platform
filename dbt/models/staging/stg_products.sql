-- Staging layer for products
-- Clean and standardize product data from raw layer

WITH source AS (
    SELECT * FROM {{ source('raw', 'products') }}
),

renamed AS (
    SELECT
        id AS product_id,
        name AS product_name,
        description AS product_description,
        price AS unit_price,
        category AS product_category,
        stock_quantity,
        created_at,
        updated_at
    FROM source
)

SELECT * FROM renamed
