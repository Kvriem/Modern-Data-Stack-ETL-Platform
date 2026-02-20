-- Initialize Target Database (Data Warehouse)
-- This script runs when the target_db container starts for the first time

-- Create raw schema for ETL landing
CREATE SCHEMA IF NOT EXISTS raw;

-- Create staging schema for dbt
CREATE SCHEMA IF NOT EXISTS staging;

-- Create intermediate schema for dbt
CREATE SCHEMA IF NOT EXISTS intermediate;

-- Create marts schema for dbt
CREATE SCHEMA IF NOT EXISTS marts;

-- Create raw tables (mirrors of source tables)
CREATE TABLE IF NOT EXISTS raw.customers (
    id INTEGER PRIMARY KEY,
    name VARCHAR(255),
    email VARCHAR(255),
    phone VARCHAR(50),
    address TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    _etl_loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS raw.products (
    id INTEGER PRIMARY KEY,
    name VARCHAR(255),
    description TEXT,
    price DECIMAL(10, 2),
    category VARCHAR(100),
    stock_quantity INTEGER,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    _etl_loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS raw.orders (
    id INTEGER PRIMARY KEY,
    customer_id INTEGER,
    order_date TIMESTAMP,
    status VARCHAR(50),
    total_amount DECIMAL(12, 2),
    shipping_address TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    _etl_loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS raw.order_items (
    id INTEGER PRIMARY KEY,
    order_id INTEGER,
    product_id INTEGER,
    quantity INTEGER,
    unit_price DECIMAL(10, 2),
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    _etl_loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_raw_orders_customer_id ON raw.orders(customer_id);
CREATE INDEX IF NOT EXISTS idx_raw_orders_updated_at ON raw.orders(updated_at);
CREATE INDEX IF NOT EXISTS idx_raw_order_items_order_id ON raw.order_items(order_id);
CREATE INDEX IF NOT EXISTS idx_raw_customers_updated_at ON raw.customers(updated_at);
CREATE INDEX IF NOT EXISTS idx_raw_products_updated_at ON raw.products(updated_at);

-- Create ETL metadata table for tracking incremental loads
CREATE TABLE IF NOT EXISTS raw._etl_watermarks (
    table_name VARCHAR(100) PRIMARY KEY,
    last_extracted_at TIMESTAMP,
    last_loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    rows_processed INTEGER DEFAULT 0
);

-- Initialize watermarks
INSERT INTO raw._etl_watermarks (table_name, last_extracted_at) VALUES
    ('customers', '1970-01-01 00:00:00'),
    ('products', '1970-01-01 00:00:00'),
    ('orders', '1970-01-01 00:00:00'),
    ('order_items', '1970-01-01 00:00:00')
ON CONFLICT (table_name) DO NOTHING;

-- Grant permissions
GRANT ALL PRIVILEGES ON SCHEMA raw TO target_user;
GRANT ALL PRIVILEGES ON SCHEMA staging TO target_user;
GRANT ALL PRIVILEGES ON SCHEMA intermediate TO target_user;
GRANT ALL PRIVILEGES ON SCHEMA marts TO target_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA raw TO target_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA staging TO target_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA intermediate TO target_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA marts TO target_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA raw TO target_user;
