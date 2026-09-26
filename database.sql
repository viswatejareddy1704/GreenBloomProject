CREATE DATABASE IF NOT EXISTS green_bloom_db;

USE green_bloom_db;

-- ==========================================
-- REMOVE OLD TABLES
-- ==========================================

DROP TABLE IF EXISTS sales;
DROP TABLE IF EXISTS customers;
DROP TABLE IF EXISTS plants;
DROP TABLE IF EXISTS suppliers;


-- ==========================================
-- SUPPLIERS TABLE
-- ==========================================

CREATE TABLE suppliers (
    supplier_id VARCHAR(10) PRIMARY KEY,
    supplier_name VARCHAR(100) NOT NULL,
    phone VARCHAR(15),
    city VARCHAR(50)
);


-- ==========================================
-- PLANTS TABLE
-- ==========================================

CREATE TABLE plants (
    plant_id INT PRIMARY KEY AUTO_INCREMENT,
    plant_name VARCHAR(100) NOT NULL,
    category VARCHAR(50),
    price DECIMAL(10,2) NOT NULL,
    quantity INT NOT NULL DEFAULT 0,
    supplier_name VARCHAR(100),
    image_file VARCHAR(255)
);


-- ==========================================
-- CUSTOMERS TABLE
-- ==========================================

CREATE TABLE customers (
    customer_id INT PRIMARY KEY AUTO_INCREMENT,
    customer_name VARCHAR(100) NOT NULL,
    phone VARCHAR(15),
    city VARCHAR(50)
);


-- ==========================================
-- SALES TABLE
-- ==========================================

CREATE TABLE sales (
    sale_id INT PRIMARY KEY AUTO_INCREMENT,
    customer_name VARCHAR(100) NOT NULL,
    plant_name VARCHAR(100) NOT NULL,
    quantity INT NOT NULL,
    total_amount DECIMAL(10,2) NOT NULL,
    sale_date DATE NOT NULL
);


-- ==========================================
-- SAMPLE SUPPLIERS
-- ==========================================

INSERT INTO suppliers
(
    supplier_id,
    supplier_name,
    phone,
    city
)
VALUES
(
    'S001',
    'Green Nursery Suppliers',
    '9876543210',
    'Nandyal'
),
(
    'S002',
    'Nature Plants Traders',
    '9876501234',
    'Kurnool'
),
(
    'S003',
    'Fresh Garden Nursery',
    '9123456780',
    'Hyderabad'
);


-- ==========================================
-- SAMPLE PLANTS
-- ==========================================

INSERT INTO plants
(
    plant_name,
    category,
    price,
    quantity,
    supplier_name,
    image_file
)
VALUES
(
    'Tulasi',
    'Medicinal',
    80.00,
    25,
    'Green Nursery Suppliers',
    NULL
),
(
    'Aloe Vera',
    'Medicinal',
    120.00,
    20,
    'Green Nursery Suppliers',
    NULL
),
(
    'Money Plant',
    'Indoor',
    150.00,
    15,
    'Nature Plants Traders',
    NULL
),
(
    'Jasmine',
    'Flowering',
    100.00,
    30,
    'Fresh Garden Nursery',
    NULL
),
(
    'Rose',
    'Flowering',
    180.00,
    20,
    'Fresh Garden Nursery',
    NULL
),
(
    'Tulips',
    'Flowering',
    250.00,
    10,
    'Nature Plants Traders',
    NULL
);


-- ==========================================
-- SAMPLE CUSTOMERS
-- ==========================================

INSERT INTO customers
(
    customer_name,
    phone,
    city
)
VALUES
(
    'Viswa',
    '9876543210',
    'Nandyal'
),
(
    'Rahul',
    '9876501234',
    'Kurnool'
),
(
    'Anjali',
    '9123456780',
    'Hyderabad'
);


-- ==========================================
-- CHECK TABLES
-- ==========================================

SHOW TABLES;


-- ==========================================
-- CHECK PLANTS TABLE
-- ==========================================

DESCRIBE plants;


-- ==========================================
-- VIEW SAMPLE DATA
-- ==========================================

SELECT * FROM suppliers;

SELECT * FROM plants;

SELECT * FROM customers;

SELECT * FROM sales;