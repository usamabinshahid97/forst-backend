import os
import sys
from datetime import datetime, timedelta
import random
from pathlib import Path

# Add the parent directory to the path so we can import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session

from app.db.session import SessionLocal, engine
from app.db.base import Base
from app import crud, schemas

# Sample data
CATEGORIES = [
    {"name": "Electronics", "description": "Electronic devices and accessories"},
    {"name": "Clothing", "description": "Apparel and fashion accessories"},
    {"name": "Home & Kitchen", "description": "Home goods and kitchen supplies"},
    {"name": "Books", "description": "Books and literature"},
    {"name": "Toys & Games", "description": "Toys, games, and entertainment"},
]

PRODUCTS = [
    # Electronics
    {
        "name": "Smartphone X", 
        "description": "Latest smartphone with advanced features", 
        "sku": "ELEC-SP-001", 
        "price": 899.99, 
        "category_id": 1,
        "inventory": {"quantity": 50, "low_stock_threshold": 10}
    },
    {
        "name": "Laptop Pro", 
        "description": "High-performance laptop for professionals", 
        "sku": "ELEC-LP-002", 
        "price": 1299.99, 
        "category_id": 1,
        "inventory": {"quantity": 30, "low_stock_threshold": 5}
    },
    {
        "name": "Wireless Earbuds", 
        "description": "Premium wireless earbuds with noise cancellation", 
        "sku": "ELEC-WE-003", 
        "price": 149.99, 
        "category_id": 1,
        "inventory": {"quantity": 100, "low_stock_threshold": 20}
    },
    
    # Clothing
    {
        "name": "Men's T-Shirt", 
        "description": "Comfortable cotton t-shirt for men", 
        "sku": "CLOTH-MT-001", 
        "price": 24.99, 
        "category_id": 2,
        "inventory": {"quantity": 200, "low_stock_threshold": 30}
    },
    {
        "name": "Women's Jeans", 
        "description": "Stylish denim jeans for women", 
        "sku": "CLOTH-WJ-002", 
        "price": 59.99, 
        "category_id": 2,
        "inventory": {"quantity": 150, "low_stock_threshold": 25}
    },
    
    # Home & Kitchen
    {
        "name": "Coffee Maker", 
        "description": "Programmable coffee maker with thermal carafe", 
        "sku": "HOME-CM-001", 
        "price": 79.99, 
        "category_id": 3,
        "inventory": {"quantity": 40, "low_stock_threshold": 8}
    },
    {
        "name": "Bedding Set", 
        "description": "Luxury bedding set with duvet cover and pillowcases", 
        "sku": "HOME-BS-002", 
        "price": 129.99, 
        "category_id": 3,
        "inventory": {"quantity": 60, "low_stock_threshold": 15}
    },
    
    # Books
    {
        "name": "Bestselling Novel", 
        "description": "Award-winning fiction novel", 
        "sku": "BOOK-BN-001", 
        "price": 19.99, 
        "category_id": 4,
        "inventory": {"quantity": 80, "low_stock_threshold": 20}
    },
    {
        "name": "Cookbook", 
        "description": "Collection of gourmet recipes", 
        "sku": "BOOK-CB-002", 
        "price": 34.99, 
        "category_id": 4,
        "inventory": {"quantity": 45, "low_stock_threshold": 10}
    },
    
    # Toys & Games
    {
        "name": "Board Game", 
        "description": "Family board game for all ages", 
        "sku": "TOY-BG-001", 
        "price": 39.99, 
        "category_id": 5,
        "inventory": {"quantity": 70, "low_stock_threshold": 15}
    },
    {
        "name": "Action Figure", 
        "description": "Collectible action figure", 
        "sku": "TOY-AF-002", 
        "price": 24.99, 
        "category_id": 5,
        "inventory": {"quantity": 90, "low_stock_threshold": 20}
    },
]

PLATFORMS = ["Amazon", "Walmart", "Direct"]

def init_db(db: Session) -> None:
    """Initialize the database with sample data."""
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    # Create categories
    for category_data in CATEGORIES:
        category = crud.category.get_by_name(db, name=category_data["name"])
        if not category:
            category_in = schemas.CategoryCreate(
                name=category_data["name"],
                description=category_data["description"]
            )
            crud.category.create(db, obj_in=category_in)
    
    # Create products and their inventory
    for product_data in PRODUCTS:
        product = crud.product.get_by_sku(db, sku=product_data["sku"])
        if not product:
            product_in = schemas.ProductCreate(
                name=product_data["name"],
                description=product_data["description"],
                sku=product_data["sku"],
                price=product_data["price"],
                category_id=product_data["category_id"]
            )
            product = crud.product.create(db, obj_in=product_in)
            
            # Create inventory for this product
            inventory_data = product_data["inventory"]
            inventory_in = schemas.InventoryCreate(
                product_id=product.id,
                quantity=inventory_data["quantity"],
                low_stock_threshold=inventory_data["low_stock_threshold"]
            )
            crud.inventory.create(db, obj_in=inventory_in)
    
    # Create sales data for the past 3 months
    end_date = datetime.now()
    start_date = end_date - timedelta(days=90)
    
    # Get all product IDs
    products = crud.product.get_multi(db)
    product_ids = [p.id for p in products]
    
    # Generate random sales data
    current_date = start_date
    while current_date <= end_date:
        # Random number of sales per day (0-15)
        num_sales = random.randint(0, 15)
        
        for _ in range(num_sales):
            # Random product
            product_id = random.choice(product_ids)
            product = crud.product.get(db, id=product_id)
            
            # Random quantity (1-5)
            quantity = random.randint(1, 5)
            
            # Random platform
            platform = random.choice(PLATFORMS)
            
            # Generate a random time on the current date
            hours = random.randint(8, 20)
            minutes = random.randint(0, 59)
            seconds = random.randint(0, 59)
            sale_datetime = current_date.replace(hour=hours, minute=minutes, second=seconds)
            
            # Create the sale if inventory is sufficient
            inventory = crud.inventory.get_by_product_id(db, product_id=product_id)
            if inventory and inventory.quantity >= quantity:
                sale_in = schemas.SaleCreate(
                    product_id=product_id,
                    quantity=quantity,
                    unit_price=product.price,
                    total_price=product.price * quantity,
                    sale_date=sale_datetime,
                    platform=platform,
                    order_id=f"ORD-{int(sale_datetime.timestamp())}-{random.randint(1000, 9999)}"
                )
                crud.sale.create_with_product(db, obj_in=sale_in)
        
        # Move to the next day
        current_date += timedelta(days=1)
    
    print("Database initialization completed.")

def main() -> None:
    """Main function to initialize the database."""
    db = SessionLocal()
    try:
        init_db(db)
    finally:
        db.close()

if __name__ == "__main__":
    main() 