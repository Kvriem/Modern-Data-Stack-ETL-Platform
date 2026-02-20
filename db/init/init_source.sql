-- Initialize Source Database (OLTP)
-- This script runs when the source_db container starts for the first time

-- Create tables
CREATE TABLE IF NOT EXISTS customers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(50),
    address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    price DECIMAL(10, 2) NOT NULL,
    category VARCHAR(100),
    stock_quantity INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS orders (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(id),
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) DEFAULT 'pending',
    total_amount DECIMAL(12, 2),
    shipping_address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS order_items (
    id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES orders(id),
    product_id INTEGER REFERENCES products(id),
    quantity INTEGER NOT NULL,
    unit_price DECIMAL(10, 2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_orders_customer_id ON orders(customer_id);
CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status);
CREATE INDEX IF NOT EXISTS idx_orders_updated_at ON orders(updated_at);
CREATE INDEX IF NOT EXISTS idx_order_items_order_id ON order_items(order_id);
CREATE INDEX IF NOT EXISTS idx_order_items_product_id ON order_items(product_id);
CREATE INDEX IF NOT EXISTS idx_customers_updated_at ON customers(updated_at);
CREATE INDEX IF NOT EXISTS idx_products_updated_at ON products(updated_at);

-- Insert sample data
INSERT INTO customers (name, email, phone, address) VALUES
    ('John Doe', 'john.doe@example.com', '+1-555-0101', '123 Main St, New York, NY'),
    ('Jane Smith', 'jane.smith@example.com', '+1-555-0102', '456 Oak Ave, Los Angeles, CA'),
    ('Bob Johnson', 'bob.johnson@example.com', '+1-555-0103', '789 Pine Rd, Chicago, IL'),
    ('Alice Brown', 'alice.brown@example.com', '+1-555-0104', '321 Elm St, Houston, TX'),
    ('Charlie Wilson', 'charlie.wilson@example.com', '+1-555-0105', '654 Maple Dr, Phoenix, AZ')
ON CONFLICT (email) DO NOTHING;

INSERT INTO products (name, description, price, category, stock_quantity) VALUES
    ('Laptop Pro', 'High-performance laptop for professionals', 1299.99, 'Electronics', 50),
    ('Wireless Mouse', 'Ergonomic wireless mouse', 29.99, 'Electronics', 200),
    ('USB-C Hub', '7-in-1 USB-C hub with HDMI', 49.99, 'Electronics', 150),
    ('Mechanical Keyboard', 'RGB mechanical keyboard', 89.99, 'Electronics', 100),
    ('Monitor 27"', '4K UHD monitor', 399.99, 'Electronics', 30),
    ('Desk Chair', 'Ergonomic office chair', 249.99, 'Furniture', 40),
    ('Standing Desk', 'Electric standing desk', 599.99, 'Furniture', 25),
    ('Notebook Set', 'Premium notebook set of 3', 19.99, 'Office Supplies', 500),
    ('Pen Set', 'Professional pen set', 14.99, 'Office Supplies', 300),
    ('Webcam HD', '1080p HD webcam', 79.99, 'Electronics', 80)
ON CONFLICT DO NOTHING;

INSERT INTO orders (customer_id, order_date, status, total_amount, shipping_address) VALUES
    (1, '2026-01-15 10:30:00', 'completed', 1329.98, '123 Main St, New York, NY'),
    (2, '2026-01-16 14:45:00', 'completed', 489.98, '456 Oak Ave, Los Angeles, CA'),
    (3, '2026-01-17 09:15:00', 'shipped', 139.97, '789 Pine Rd, Chicago, IL'),
    (1, '2026-01-20 16:00:00', 'processing', 849.98, '123 Main St, New York, NY'),
    (4, '2026-02-01 11:30:00', 'pending', 1299.99, '321 Elm St, Houston, TX'),
    (5, '2026-02-10 08:45:00', 'completed', 349.97, '654 Maple Dr, Phoenix, AZ'),
    (2, '2026-02-15 13:20:00', 'shipped', 699.98, '456 Oak Ave, Los Angeles, CA')
ON CONFLICT DO NOTHING;

INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES
    (1, 1, 1, 1299.99),
    (1, 2, 1, 29.99),
    (2, 5, 1, 399.99),
    (2, 4, 1, 89.99),
    (3, 2, 2, 29.99),
    (3, 3, 1, 49.99),
    (3, 9, 2, 14.99),
    (4, 6, 1, 249.99),
    (4, 7, 1, 599.99),
    (5, 1, 1, 1299.99),
    (6, 4, 1, 89.99),
    (6, 6, 1, 249.99),
    (6, 9, 1, 14.99),
    (7, 7, 1, 599.99),
    (7, 3, 2, 49.99)
ON CONFLICT DO NOTHING;

-- Create function to auto-update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for auto-updating updated_at
DROP TRIGGER IF EXISTS update_customers_updated_at ON customers;
CREATE TRIGGER update_customers_updated_at
    BEFORE UPDATE ON customers
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_products_updated_at ON products;
CREATE TRIGGER update_products_updated_at
    BEFORE UPDATE ON products
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_orders_updated_at ON orders;
CREATE TRIGGER update_orders_updated_at
    BEFORE UPDATE ON orders
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_order_items_updated_at ON order_items;
CREATE TRIGGER update_order_items_updated_at
    BEFORE UPDATE ON order_items
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Grant permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO source_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO source_user;
