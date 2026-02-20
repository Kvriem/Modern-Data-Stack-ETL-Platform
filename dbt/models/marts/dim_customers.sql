-- Dimension table: Customers
-- SCD Type 1 dimension for customer attributes

WITH customers AS (
    SELECT * FROM {{ ref('stg_customers') }}
),

final AS (
    SELECT
        customer_id,
        customer_name,
        customer_email,
        phone_number,
        full_address,
        created_at AS customer_since,
        updated_at AS last_updated
    FROM customers
)

SELECT * FROM final
