-- Intermediate model: Orders enriched with customer data
-- Join orders with customer information for easier analysis

WITH orders AS (
    SELECT * FROM {{ ref('stg_orders') }}
),

customers AS (
    SELECT * FROM {{ ref('stg_customers') }}
),

enriched AS (
    SELECT
        o.order_id,
        o.order_date,
        o.order_status,
        o.order_total,
        o.shipping_address,
        o.customer_id,
        c.customer_name,
        c.customer_email,
        c.phone_number,
        c.full_address AS customer_address,
        o.created_at,
        o.updated_at
    FROM orders o
    LEFT JOIN customers c
        ON o.customer_id = c.customer_id
)

SELECT * FROM enriched
