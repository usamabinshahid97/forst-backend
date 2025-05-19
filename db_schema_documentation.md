# E-commerce Admin API Database Schema

The database is designed to support an e-commerce admin system with inventory management, product categorization, and sales tracking capabilities. Below is a detailed explanation of each table and their relationships.

## Category

**Purpose**: Stores product categories for organizing the product catalog.

**Fields**:
- `id`: Integer, primary key
- `name`: String (100), unique, indexed, required - The category name
- `description`: String (255), optional - A description of the category
- `created_at`: DateTime - When the category was created
- `updated_at`: DateTime - When the category was last updated (automatically updated)
- `deleted_at`: DateTime, nullable - When the category was soft-deleted (null if active)

**Relationships**:
- One-to-many with `Product` - A category can have multiple products

## Product

**Purpose**: Stores product information including pricing and categorization.

**Fields**:
- `id`: Integer, primary key
- `name`: String (100), indexed, required - The product name
- `description`: String (500), optional - A description of the product
- `sku`: String (50), unique, indexed, required - Stock Keeping Unit, unique identifier for inventory
- `price`: Float, required - The product price
- `category_id`: Integer, foreign key to Category.id, required - Which category the product belongs to
- `created_at`: DateTime - When the product was created
- `updated_at`: DateTime - When the product was last updated (automatically updated)
- `deleted_at`: DateTime, nullable - When the product was soft-deleted (null if active)

**Relationships**:
- Many-to-one with `Category` - A product belongs to one category
- One-to-one with `Inventory` - A product has one inventory record
- One-to-many with `Sale` - A product can have multiple sales records

## Inventory

**Purpose**: Tracks stock levels for products, including threshold monitoring for low stock alerts.

**Fields**:
- `id`: Integer, primary key
- `product_id`: Integer, foreign key to Product.id, required, unique - Which product this inventory belongs to
- `quantity`: Integer, required, default 0 - Current quantity in stock
- `low_stock_threshold`: Integer, required, default 10 - Threshold for low stock alerts
- `last_restock_date`: DateTime, nullable - When the product was last restocked
- `updated_at`: DateTime - When the inventory was last updated (automatically updated)

**Relationships**:
- One-to-one with `Product` - An inventory record belongs to one product

**Properties**:
- `is_low_stock`: Boolean - Computed property that returns true if quantity is at or below the low_stock_threshold

## Sale

**Purpose**: Records sales transactions for products across different platforms.

**Fields**:
- `id`: Integer, primary key
- `product_id`: Integer, foreign key to Product.id, required - Which product was sold
- `quantity`: Integer, required - How many units were sold
- `unit_price`: Float, required - Price per unit at time of sale
- `total_price`: Float, required - Total price of the sale (quantity × unit_price)
- `sale_date`: DateTime, required, default current time - When the sale occurred
- `platform`: String (50), required, indexed - Sales platform (e.g., Amazon, Walmart)
- `order_id`: String (100), required, indexed - Order identifier from the platform

**Relationships**:
- Many-to-one with `Product` - A sale record belongs to one product

## Global Features

All tables implement:
- Automatic table name generation based on the class name
- Automatic creation and update timestamps
- Support for soft deletion (where applicable)
- Proper indexing for efficient queries

## Database Relationships Overview

- Categories contain many Products
- Products belong to one Category
- Products have one Inventory record
- Products can have many Sales records
- Inventory tracks stock for one Product
- Sales are associated with one Product each

This schema supports key e-commerce operations including catalog management, inventory tracking with low stock alerts, sales recording across multiple platforms, and maintains data integrity through proper relationships and constraints. 