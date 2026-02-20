-- Intermediate model: Order items with product details
-- Join order items with product information

WITH order_items AS (
    SELECT * FROM {{ ref('stg_order_items') }}
),

products AS (
    SELECT * FROM {{ ref('stg_products') }}
),

enriched AS (
    SELECT
        oi.order_item_id,
        oi.order_id,
        oi.product_id,
        p.product_name,
        p.product_description,
        p.product_category,
        oi.item_quantity,
        oi.item_price,
        oi.line_total,
        oi.created_at,
        oi.updated_at
    FROM order_items oi
    LEFT JOIN products p
        ON oi.product_id = p.product_id
)

SELECT * FROM enriched
