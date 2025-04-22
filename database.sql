CREATE DATABASE IF NOT EXISTS farmer_db;
USE farmer_db;

CREATE TABLE farmers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    land_area FLOAT,
    village VARCHAR(100),
    aadhaar VARCHAR(12)
);

CREATE TABLE schemes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    farmer_id INT,
    scheme_name VARCHAR(100),
    year INT,
    amount DECIMAL(10,2),
    FOREIGN KEY (farmer_id) REFERENCES farmers(id)
);
