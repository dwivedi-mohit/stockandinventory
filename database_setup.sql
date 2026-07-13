-- Database Setup for Inventory Management System
-- Run this script to create all required tables

DROP DATABASE IF EXISTS inventory_db;
CREATE DATABASE inventory_db;
USE inventory_db;

-- Products Table
CREATE TABLE Products (
    product_id INT AUTO_INCREMENT PRIMARY KEY,
    product_name VARCHAR(255) NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    stock_quantity INT NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Suppliers Table
CREATE TABLE Suppliers (
    supplier_id INT AUTO_INCREMENT PRIMARY KEY,
    supplier_name VARCHAR(255) NOT NULL,
    contact_info VARCHAR(100),
    email VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Purchases Table
CREATE TABLE Purchases (
    purchase_id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    quantity INT NOT NULL,
    purchase_date DATE NOT NULL,
    FOREIGN KEY (product_id) REFERENCES Products(product_id) ON DELETE CASCADE
);

-- Sales Table
CREATE TABLE Sales (
    sale_id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    quantity INT NOT NULL,
    sale_date DATE NOT NULL,
    FOREIGN KEY (product_id) REFERENCES Products(product_id) ON DELETE CASCADE
);

-- Create Indexes for better performance
CREATE INDEX idx_products_name ON Products(product_name);
CREATE INDEX idx_products_stock ON Products(stock_quantity);
CREATE INDEX idx_suppliers_name ON Suppliers(supplier_name);
CREATE INDEX idx_purchases_date ON Purchases(purchase_date);
CREATE INDEX idx_sales_date ON Sales(sale_date);

-- Insert sample data
INSERT INTO Products (product_name, price, stock_quantity) VALUES
('Laptop', 999.99, 50),
('Mouse', 29.99, 100),
('Keyboard', 79.99, 75),
('Monitor', 299.99, 30),
('USB Cable', 9.99, 200);

INSERT INTO Suppliers (supplier_name, contact_info, email) VALUES
('Tech Supplies Inc.', '+1-555-0100', 'contact@techsupplies.com'),
('Electronics World', '+1-555-0200', 'sales@electronicsworld.com'),
('Office Solutions', '+1-555-0300', 'info@officesolutions.com');

-- Show created tables
SHOW TABLES;