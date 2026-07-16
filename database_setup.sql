-- Inventory Management System - Database Setup
-- Run: mysql -u root -p < database_setup.sql

DROP DATABASE IF EXISTS inventory_db;
CREATE DATABASE inventory_db;
USE inventory_db;

-- ==============================
-- Users & Authentication
-- ==============================
CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    role ENUM('admin', 'manager', 'staff') DEFAULT 'staff',
    is_active BOOLEAN DEFAULT TRUE,
    last_login DATETIME,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- ==============================
-- Categories
-- ==============================
CREATE TABLE categories (
    category_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    parent_id INT DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (parent_id) REFERENCES categories(category_id) ON DELETE SET NULL
);

-- ==============================
-- Products
-- ==============================
CREATE TABLE products (
    product_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    sku VARCHAR(50) UNIQUE NOT NULL,
    barcode VARCHAR(100),
    category_id INT,
    cost_price DECIMAL(12,2) NOT NULL DEFAULT 0.00,
    selling_price DECIMAL(12,2) NOT NULL DEFAULT 0.00,
    stock_quantity INT NOT NULL DEFAULT 0,
    min_stock_level INT DEFAULT 10,
    description TEXT,
    image_path VARCHAR(500),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES categories(category_id) ON DELETE SET NULL
);

-- ==============================
-- Suppliers
-- ==============================
CREATE TABLE suppliers (
    supplier_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    contact_person VARCHAR(100),
    email VARCHAR(100),
    phone VARCHAR(20),
    address TEXT,
    city VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- ==============================
-- Customers
-- ==============================
CREATE TABLE customers (
    customer_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(100),
    phone VARCHAR(20),
    address TEXT,
    loyalty_points INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- ==============================
-- Purchases
-- ==============================
CREATE TABLE purchases (
    purchase_id INT AUTO_INCREMENT PRIMARY KEY,
    supplier_id INT NOT NULL,
    user_id INT NOT NULL,
    purchase_date DATE NOT NULL,
    total_amount DECIMAL(12,2) DEFAULT 0.00,
    status ENUM('pending', 'received', 'cancelled') DEFAULT 'pending',
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- ==============================
-- Purchase Items
-- ==============================
CREATE TABLE purchase_items (
    item_id INT AUTO_INCREMENT PRIMARY KEY,
    purchase_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL,
    unit_cost DECIMAL(12,2) NOT NULL,
    FOREIGN KEY (purchase_id) REFERENCES purchases(purchase_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

-- ==============================
-- Sales
-- ==============================
CREATE TABLE sales (
    sale_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT,
    user_id INT NOT NULL,
    sale_date DATE NOT NULL,
    subtotal DECIMAL(12,2) DEFAULT 0.00,
    discount DECIMAL(12,2) DEFAULT 0.00,
    tax DECIMAL(12,2) DEFAULT 0.00,
    grand_total DECIMAL(12,2) DEFAULT 0.00,
    payment_method ENUM('cash', 'card', 'transfer') DEFAULT 'cash',
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE SET NULL,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- ==============================
-- Sale Items
-- ==============================
CREATE TABLE sale_items (
    item_id INT AUTO_INCREMENT PRIMARY KEY,
    sale_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL,
    unit_price DECIMAL(12,2) NOT NULL,
    discount DECIMAL(12,2) DEFAULT 0.00,
    FOREIGN KEY (sale_id) REFERENCES sales(sale_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

-- ==============================
-- Returns
-- ==============================
CREATE TABLE returns (
    return_id INT AUTO_INCREMENT PRIMARY KEY,
    sale_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL,
    reason TEXT,
    return_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sale_id) REFERENCES sales(sale_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

-- ==============================
-- Activity Log
-- ==============================
CREATE TABLE activity_log (
    log_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    action VARCHAR(50) NOT NULL,
    entity_type VARCHAR(50) NOT NULL,
    entity_id INT,
    details JSON,
    ip_address VARCHAR(45),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- ==============================
-- Company Settings
-- ==============================
CREATE TABLE company_settings (
    setting_id INT AUTO_INCREMENT PRIMARY KEY,
    company_name VARCHAR(255) DEFAULT 'My Company',
    address TEXT,
    phone VARCHAR(20),
    email VARCHAR(100),
    tax_id VARCHAR(50),
    currency_symbol VARCHAR(5) DEFAULT '$',
    tax_rate DECIMAL(5,2) DEFAULT 0.00,
    logo_path VARCHAR(500)
);

-- ==============================
-- Backup Log
-- ==============================
CREATE TABLE backup_log (
    backup_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size BIGINT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- ==============================
-- Indexes
-- ==============================
CREATE INDEX idx_products_category ON products(category_id);
CREATE INDEX idx_products_sku ON products(sku);
CREATE INDEX idx_products_stock ON products(stock_quantity);
CREATE INDEX idx_products_active ON products(is_active);

CREATE INDEX idx_purchases_supplier ON purchases(supplier_id);
CREATE INDEX idx_purchases_date ON purchases(purchase_date);
CREATE INDEX idx_purchases_status ON purchases(status);

CREATE INDEX idx_sales_date ON sales(sale_date);
CREATE INDEX idx_sales_customer ON sales(customer_id);
CREATE INDEX idx_sales_method ON sales(payment_method);

CREATE INDEX idx_activity_user ON activity_log(user_id);
CREATE INDEX idx_activity_entity ON activity_log(entity_type, entity_id);
CREATE INDEX idx_activity_created ON activity_log(created_at);

CREATE INDEX idx_returns_sale ON returns(sale_id);
CREATE INDEX idx_returns_date ON returns(return_date);

-- ==============================
-- Seed Data
-- ==============================

-- Default admin user (password: admin123)
-- Hash will be regenerated by the app on first run if needed
INSERT INTO users (username, email, password_hash, full_name, role)
VALUES ('admin', 'admin@inventory.local', '', 'System Administrator', 'admin');

-- Default company settings
INSERT INTO company_settings (company_name, currency_symbol, tax_rate)
VALUES ('My Inventory Systems', '$', 0.00);

-- Sample categories
INSERT INTO categories (name, description) VALUES
('Electronics', 'Electronic devices and accessories'),
('Clothing', 'Apparel and fashion items'),
('Food & Beverages', 'Food and drink products'),
('Office Supplies', 'Stationery and office equipment'),
('Other', 'Miscellaneous items');

-- Sample products
INSERT INTO products (name, sku, barcode, category_id, cost_price, selling_price, stock_quantity, min_stock_level) VALUES
('Laptop Pro 15', 'LAP-001', '8901234567890', 1, 800.00, 1299.99, 25, 5),
('Wireless Mouse', 'MOU-001', '8901234567891', 1, 15.00, 29.99, 100, 20),
('Mechanical Keyboard', 'KEY-001', '8901234567892', 1, 45.00, 89.99, 50, 10),
('Cotton T-Shirt', 'TSH-001', '8901234567893', 2, 8.00, 19.99, 200, 50),
('Denim Jeans', 'JEA-001', '8901234567894', 2, 25.00, 59.99, 80, 15),
('Green Tea Box', 'TEA-001', '8901234567895', 3, 3.00, 7.99, 300, 50),
('A4 Paper Pack', 'PAP-001', '8901234567896', 4, 2.50, 5.99, 500, 100);

-- Sample suppliers
INSERT INTO suppliers (name, contact_person, email, phone, address, city) VALUES
('Tech Distributors Inc.', 'John Smith', 'john@techdist.com', '+1-555-0100', '123 Tech Street', 'New York'),
('Fashion Wholesale Ltd.', 'Sarah Johnson', 'sarah@fashionwl.com', '+1-555-0200', '456 Fashion Ave', 'Los Angeles'),
('Global Foods Co.', 'Mike Brown', 'mike@globalfoods.com', '+1-555-0300', '789 Food Blvd', 'Chicago'),
('Office Essentials', 'Lisa Davis', 'lisa@officeess.com', '+1-555-0400', '321 Office Park', 'Houston');

-- Sample customers
INSERT INTO customers (name, email, phone, address) VALUES
('Alice Williams', 'alice@email.com', '+1-555-1001', '100 Main Street'),
('Bob Martin', 'bob@email.com', '+1-555-1002', '200 Oak Avenue'),
('Carol White', 'carol@email.com', '+1-555-1003', '300 Pine Road');

SHOW TABLES;
