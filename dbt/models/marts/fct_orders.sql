-- Fact table: Order summary metrics
-- One row per order with aggregated metrics

WITH orders AS (
    SELECT * FROM {{ ref('int_orders_enriched') }}
),

order_items AS (
    SELECT * FROM {{ ref('int_order_items_enriched') }}
),

order_aggregates AS (
    SELECT
        order_id,
        COUNT(*) AS total_items,
        SUM(item_quantity) AS total_quantity,
        SUM(line_total) AS calculated_total,
        AVG(item_price) AS avg_item_price,
        MIN(item_price) AS min_item_price,
        MAX(item_price) AS max_item_price
    FROM order_items
    GROUP BY order_id
),

final AS (
    SELECT
        o.order_id,
        o.order_date,
        o.order_status,
        o.customer_id,
        o.customer_name,
        o.customer_email,
        o.order_total,
        oa.total_items,
        oa.total_quantity,
        oa.calculated_total,
        oa.avg_item_price,
        oa.min_item_price,
        oa.max_item_price,
        o.shipping_address,
        o.created_at,
        o.updated_at
    FROM orders o
    LEFT JOIN order_aggregates oa
        ON o.order_id = oa.order_id
)

SELECT * FROM final
