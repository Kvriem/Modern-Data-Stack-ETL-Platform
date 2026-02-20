-- Staging layer for customers
-- Clean and standardize customer data from raw layer

WITH source AS (
    SELECT * FROM {{ source('raw', 'customers') }}
),

renamed AS (
    SELECT
        id AS customer_id,
        name AS customer_name,
        email AS customer_email,
        phone AS phone_number,
        address AS full_address,
        created_at,
        updated_at
    FROM source
)

SELECT * FROM renamed
