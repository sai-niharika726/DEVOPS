-- Run this manually in psql to set up the database
-- psql -U postgres -f schema.sql

CREATE DATABASE novastore;
\c novastore

CREATE USER nova WITH PASSWORD 'nova123';
GRANT ALL PRIVILEGES ON DATABASE novastore TO nova;
GRANT ALL ON SCHEMA public TO nova;

CREATE TABLE IF NOT EXISTS products (
    id          SERIAL PRIMARY KEY,
    name        TEXT NOT NULL,
    description TEXT,
    price       NUMERIC(10,2),
    category    TEXT,
    image_url   TEXT,
    stock       INTEGER DEFAULT 10
);

CREATE TABLE IF NOT EXISTS orders (
    id             SERIAL PRIMARY KEY,
    customer_name  TEXT,
    customer_email TEXT,
    product_id     INTEGER REFERENCES products(id),
    quantity       INTEGER,
    total          NUMERIC(10,2),
    created_at     TIMESTAMP DEFAULT NOW()
);

INSERT INTO products (name, description, price, category, image_url, stock) VALUES
('MacBook Pro M3',     'Apple MacBook Pro with M3 chip, 16GB RAM, 512GB SSD',        1999.99, 'Laptops',     'https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=400', 15),
('Sony WH-1000XM5',   'Industry-leading noise cancelling wireless headphones',          349.99, 'Audio',       'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400', 30),
('iPhone 15 Pro',     'Apple iPhone 15 Pro with titanium design and A17 Pro chip',    1199.99, 'Phones',      'https://images.unsplash.com/photo-1695048133142-1a20484d2569?w=400', 20),
('Samsung 4K OLED TV','55-inch 4K OLED Smart TV with HDR10+',                         1299.99, 'TVs',         'https://images.unsplash.com/photo-1593784991095-a205069470b6?w=400',  8),
('iPad Air M2',       'Apple iPad Air with M2 chip, 10.9-inch Liquid Retina display',  749.99, 'Tablets',     'https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0?w=400', 25),
('DJI Mini 4 Pro',    'Compact drone with 4K/60fps camera and 34-min flight time',     759.99, 'Cameras',     'https://images.unsplash.com/photo-1473968512647-3e447244af8f?w=400', 12),
('LG UltraWide 34"',  '34-inch curved UltraWide QHD IPS display for professionals',   799.99, 'Monitors',    'https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?w=400', 18),
('Keychron K2 Pro',   'Wireless mechanical keyboard with RGB backlight',               119.99, 'Accessories', 'https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=400', 50);
