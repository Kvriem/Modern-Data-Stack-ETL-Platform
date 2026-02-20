-- Staging layer for orders
-- Clean and standardize order data from raw layer

WITH source AS (
    SELECT * FROM {{ source('raw', 'orders') }}
),

renamed AS (
    SELECT
        id AS order_id,
        customer_id,
        order_date,
        status AS order_status,
        total_amount AS order_total,
        shipping_address,
        created_at,
        updated_at
    FROM source
)

SELECT * FROM renamed
