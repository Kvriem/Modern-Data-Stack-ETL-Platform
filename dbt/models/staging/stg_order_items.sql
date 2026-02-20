-- Staging layer for order items
-- Clean and standardize order items data from raw layer

WITH source AS (
    SELECT * FROM {{ source('raw', 'order_items') }}
),

renamed AS (
    SELECT
        id AS order_item_id,
        order_id,
        product_id,
        quantity AS item_quantity,
        unit_price AS item_price,
        (quantity * unit_price) AS line_total,
        created_at,
        updated_at
    FROM source
)

SELECT * FROM renamed
