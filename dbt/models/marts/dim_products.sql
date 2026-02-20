-- Dimension table: Products
-- SCD Type 1 dimension for product attributes

WITH products AS (
    SELECT * FROM {{ ref('stg_products') }}
),

final AS (
    SELECT
        product_id,
        product_name,
        product_description,
        product_category,
        unit_price,
        stock_quantity,
        created_at AS product_since,
        updated_at AS last_updated
    FROM products
)

SELECT * FROM final
