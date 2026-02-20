-- Fact table: Sales
-- Incremental model tracking all sales transactions
-- Grain: One row per order line item

{{
    config(
        materialized='incremental',
        unique_key='order_item_id',
        on_schema_change='fail'
    )
}}

WITH order_items AS (
    SELECT * FROM {{ ref('int_order_items_enriched') }}
    {% if is_incremental() %}
    WHERE updated_at > (SELECT MAX(last_updated) FROM {{ this }})
    {% endif %}
),

orders AS (
    SELECT * FROM {{ ref('int_orders_enriched') }}
),

final AS (
    SELECT
        oi.order_item_id,
        oi.order_id,
        o.order_date,
        o.order_status,
        o.customer_id,
        o.customer_name,
        oi.product_id,
        oi.product_name,
        oi.product_category,
        oi.item_quantity,
        oi.item_price,
        oi.line_total,
        o.order_total,
        o.shipping_address,
        oi.updated_at AS last_updated
    FROM order_items oi
    INNER JOIN orders o
        ON oi.order_id = o.order_id
)

SELECT * FROM final
