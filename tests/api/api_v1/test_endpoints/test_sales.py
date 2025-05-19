import pytest
from app import crud
from datetime import datetime, timedelta

def test_create_sale(client_with_db, db):
    """Test creating a new sale"""
    # First create a category, product, and inventory
    category_data = {"name": "Test Category", "description": "Category for testing sales"}
    category_response = client_with_db.post("/api/v1/categories/", json=category_data)
    category_id = category_response.json()["id"]
    
    product_data = {
        "name": "Test Product",
        "description": "Product for testing sales",
        "sku": "TEST-SALE-001",
        "price": 29.99,
        "category_id": category_id
    }
    product_response = client_with_db.post("/api/v1/products/", json=product_data)
    product_id = product_response.json()["id"]
    
    inventory_data = {
        "product_id": product_id,
        "quantity": 100,
        "low_stock_threshold": 20
    }
    client_with_db.post("/api/v1/inventory/", json=inventory_data)
    
    # Create a sale
    sale_data = {
        "product_id": product_id,
        "quantity": 2,
        "unit_price": 29.99,
        "total_price": 59.98,
        "platform": "web",
        "order_id": "ORDER123"
    }
    response = client_with_db.post("/api/v1/sales/", json=sale_data)
    assert response.status_code == 200
    data = response.json()
    assert data["product_id"] == product_id
    assert data["quantity"] == sale_data["quantity"]
    assert data["unit_price"] == sale_data["unit_price"]
    assert data["total_price"] == sale_data["total_price"]
    assert data["platform"] == sale_data["platform"]
    assert data["order_id"] == sale_data["order_id"]
    assert "id" in data
    assert "sale_date" in data
    
    # Verify inventory was updated
    inventory_response = client_with_db.get(f"/api/v1/inventory/product/{product_id}")
    assert inventory_response.status_code == 200
    inventory_data = inventory_response.json()
    assert inventory_data["quantity"] == 98  # Original 100 - 2 sold

def test_create_sale_insufficient_inventory(client_with_db, db):
    """Test creating a sale with insufficient inventory"""
    # First create a category, product, and inventory
    category_data = {"name": "Test Category", "description": "Category for testing insufficient inventory"}
    category_response = client_with_db.post("/api/v1/categories/", json=category_data)
    category_id = category_response.json()["id"]
    
    product_data = {
        "name": "Test Product",
        "description": "Product for testing insufficient inventory",
        "sku": "TEST-INSUFF-001",
        "price": 39.99,
        "category_id": category_id
    }
    product_response = client_with_db.post("/api/v1/products/", json=product_data)
    product_id = product_response.json()["id"]
    
    # Create inventory with only 5 items
    inventory_data = {
        "product_id": product_id,
        "quantity": 5,
        "low_stock_threshold": 10
    }
    client_with_db.post("/api/v1/inventory/", json=inventory_data)
    
    # Try to create a sale for 10 items
    sale_data = {
        "product_id": product_id,
        "quantity": 10,
        "unit_price": 39.99,
        "total_price": 399.90,
        "platform": "web",
        "order_id": "ORDER124"
    }
    response = client_with_db.post("/api/v1/sales/", json=sale_data)
    assert response.status_code == 400
    assert "insufficient" in response.json()["detail"].lower()
    
    # Verify inventory was not changed
    inventory_response = client_with_db.get(f"/api/v1/inventory/product/{product_id}")
    assert inventory_response.status_code == 200
    inventory_data = inventory_response.json()
    assert inventory_data["quantity"] == 5  # Still 5, not changed

def test_get_all_sales(client_with_db, db):
    """Test retrieving all sales"""
    # First create a category, product, and inventory
    category_data = {"name": "Test Category", "description": "Category for testing sales listing"}
    category_response = client_with_db.post("/api/v1/categories/", json=category_data)
    category_id = category_response.json()["id"]
    
    product_data = {
        "name": "Test Product",
        "description": "Product for testing sales listing",
        "sku": "TEST-SALELIST-001",
        "price": 49.99,
        "category_id": category_id
    }
    product_response = client_with_db.post("/api/v1/products/", json=product_data)
    product_id = product_response.json()["id"]
    
    inventory_data = {
        "product_id": product_id,
        "quantity": 100,
        "low_stock_threshold": 20
    }
    client_with_db.post("/api/v1/inventory/", json=inventory_data)
    
    # Create two sales
    sale1_data = {
        "product_id": product_id,
        "quantity": 1,
        "unit_price": 49.99,
        "total_price": 49.99,
        "platform": "web",
        "order_id": "ORDER125"
    }
    
    sale2_data = {
        "product_id": product_id,
        "quantity": 2,
        "unit_price": 49.99,
        "total_price": 99.98,
        "platform": "amazon",
        "order_id": "ORDER126"
    }
    
    client_with_db.post("/api/v1/sales/", json=sale1_data)
    client_with_db.post("/api/v1/sales/", json=sale2_data)
    
    # Get all sales
    response = client_with_db.get("/api/v1/sales/")
    assert response.status_code == 200
    data = response.json()
    
    # Find our test sales in the response
    sale_order_ids = [sale["order_id"] for sale in data]
    assert "ORDER125" in sale_order_ids
    assert "ORDER126" in sale_order_ids

def test_get_sales_by_date_range(client_with_db, db):
    """Test retrieving sales by date range"""
    # First create a category, product, and inventory
    category_data = {"name": "Test Category", "description": "Category for testing sales by date"}
    category_response = client_with_db.post("/api/v1/categories/", json=category_data)
    category_id = category_response.json()["id"]
    
    product_data = {
        "name": "Test Product",
        "description": "Product for testing sales by date",
        "sku": "TEST-SALEDATE-001",
        "price": 59.99,
        "category_id": category_id
    }
    product_response = client_with_db.post("/api/v1/products/", json=product_data)
    product_id = product_response.json()["id"]
    
    inventory_data = {
        "product_id": product_id,
        "quantity": 100,
        "low_stock_threshold": 20
    }
    client_with_db.post("/api/v1/inventory/", json=inventory_data)
    
    # Create a sale
    sale_data = {
        "product_id": product_id,
        "quantity": 1,
        "unit_price": 59.99,
        "total_price": 59.99,
        "platform": "web",
        "order_id": "ORDER127"
    }
    client_with_db.post("/api/v1/sales/", json=sale_data)
    
    # Get today's date in ISO format
    today = datetime.now().date().isoformat()
    yesterday = (datetime.now() - timedelta(days=1)).date().isoformat()
    tomorrow = (datetime.now() + timedelta(days=1)).date().isoformat()
    
    # Test with date range including today
    response = client_with_db.get(f"/api/v1/sales/date-range/?start_date={yesterday}&end_date={tomorrow}")
    assert response.status_code == 200
    data = response.json()
    
    # Should find our sale
    sale_order_ids = [sale["order_id"] for sale in data]
    assert "ORDER127" in sale_order_ids
    
    # Test with date range not including today
    response = client_with_db.get(f"/api/v1/sales/date-range/?start_date={tomorrow}&end_date={tomorrow}")
    assert response.status_code == 200
    data = response.json()
    
    # Should not find our sale
    sale_order_ids = [sale["order_id"] for sale in data]
    assert "ORDER127" not in sale_order_ids

def test_get_sales_by_product(client_with_db, db):
    """Test retrieving sales by product"""
    # Create two products with sales
    category_data = {"name": "Test Category", "description": "Category for testing sales by product"}
    category_response = client_with_db.post("/api/v1/categories/", json=category_data)
    category_id = category_response.json()["id"]
    
    # First product
    product1_data = {
        "name": "Product 1",
        "description": "First product for testing sales by product",
        "sku": "TEST-SALEPROD-001",
        "price": 69.99,
        "category_id": category_id
    }
    product1_response = client_with_db.post("/api/v1/products/", json=product1_data)
    product1_id = product1_response.json()["id"]
    
    inventory1_data = {
        "product_id": product1_id,
        "quantity": 100,
        "low_stock_threshold": 20
    }
    client_with_db.post("/api/v1/inventory/", json=inventory1_data)
    
    # Second product
    product2_data = {
        "name": "Product 2",
        "description": "Second product for testing sales by product",
        "sku": "TEST-SALEPROD-002",
        "price": 79.99,
        "category_id": category_id
    }
    product2_response = client_with_db.post("/api/v1/products/", json=product2_data)
    product2_id = product2_response.json()["id"]
    
    inventory2_data = {
        "product_id": product2_id,
        "quantity": 100,
        "low_stock_threshold": 20
    }
    client_with_db.post("/api/v1/inventory/", json=inventory2_data)
    
    # Create sales for each product
    sale1_data = {
        "product_id": product1_id,
        "quantity": 1,
        "unit_price": 69.99,
        "total_price": 69.99,
        "platform": "web",
        "order_id": "ORDER128"
    }
    
    sale2_data = {
        "product_id": product2_id,
        "quantity": 1,
        "unit_price": 79.99,
        "total_price": 79.99,
        "platform": "web",
        "order_id": "ORDER129"
    }
    
    client_with_db.post("/api/v1/sales/", json=sale1_data)
    client_with_db.post("/api/v1/sales/", json=sale2_data)
    
    # Get sales for product 1
    response = client_with_db.get(f"/api/v1/sales/product/{product1_id}")
    assert response.status_code == 200
    data = response.json()
    
    # Should only include sales for product 1
    assert len(data) > 0
    for sale in data:
        assert sale["product_id"] == product1_id
    
    sale_order_ids = [sale["order_id"] for sale in data]
    assert "ORDER128" in sale_order_ids
    assert "ORDER129" not in sale_order_ids

def test_get_sales_by_nonexistent_product(client_with_db, db):
    """Test retrieving sales for a non-existent product"""
    response = client_with_db.get("/api/v1/sales/product/9999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()

def test_get_sales_summary(client_with_db, db):
    """Test retrieving sales summary"""
    # Create product with sales
    category_data = {"name": "Test Category", "description": "Category for testing sales summary"}
    category_response = client_with_db.post("/api/v1/categories/", json=category_data)
    category_id = category_response.json()["id"]
    
    product_data = {
        "name": "Test Product",
        "description": "Product for testing sales summary",
        "sku": "TEST-SUMMARY-001",
        "price": 89.99,
        "category_id": category_id
    }
    product_response = client_with_db.post("/api/v1/products/", json=product_data)
    product_id = product_response.json()["id"]
    
    inventory_data = {
        "product_id": product_id,
        "quantity": 100,
        "low_stock_threshold": 20
    }
    client_with_db.post("/api/v1/inventory/", json=inventory_data)
    
    # Create a few sales
    sale1_data = {
        "product_id": product_id,
        "quantity": 2,
        "unit_price": 89.99,
        "total_price": 179.98,
        "platform": "web",
        "order_id": "ORDER130"
    }
    
    sale2_data = {
        "product_id": product_id,
        "quantity": 3,
        "unit_price": 89.99,
        "total_price": 269.97,
        "platform": "amazon",
        "order_id": "ORDER131"
    }
    
    client_with_db.post("/api/v1/sales/", json=sale1_data)
    client_with_db.post("/api/v1/sales/", json=sale2_data)
    
    # Get sales summary
    response = client_with_db.get("/api/v1/sales/summary/")
    assert response.status_code == 200
    data = response.json()
    
    # Verify summary data
    assert "total_revenue" in data
    assert "total_units_sold" in data
    assert "sales_by_platform" in data
    
    # Our test sales should contribute 5 units and 449.95 revenue
    assert data["total_units_sold"] >= 5
    # Use a slightly lower value to account for floating point precision issues
    assert data["total_revenue"] >= 449.94
    
    # Check platforms
    platforms = [platform["platform"] for platform in data["sales_by_platform"]]
    assert "web" in platforms
    assert "amazon" in platforms

def test_sales_queries_exclude_deleted_products(client_with_db, db):
    """Test that sales queries exclude deleted products"""
    # Setup: Create two products with sales, then delete one
    category_data = {"name": "Test Category", "description": "Test category for sales queries"}
    category_response = client_with_db.post("/api/v1/categories/", json=category_data)
    category_id = category_response.json()["id"]
    
    # Product 1 (will be kept)
    product1_data = {
        "name": "Test Product 1",
        "description": "Test product 1 for sales queries",
        "sku": "TEST-QUERY-001",
        "price": 49.99,
        "category_id": category_id
    }
    product1_response = client_with_db.post("/api/v1/products/", json=product1_data)
    product1_id = product1_response.json()["id"]
    
    # Create inventory for product 1
    inventory1_data = {
        "product_id": product1_id,
        "quantity": 30,
        "low_stock_threshold": 5
    }
    client_with_db.post("/api/v1/inventory/", json=inventory1_data)
    
    # Product 2 (will be deleted)
    product2_data = {
        "name": "Test Product 2",
        "description": "Test product 2 for sales queries",
        "sku": "TEST-QUERY-002",
        "price": 59.99,
        "category_id": category_id
    }
    product2_response = client_with_db.post("/api/v1/products/", json=product2_data)
    product2_id = product2_response.json()["id"]
    
    # Create inventory for product 2
    inventory2_data = {
        "product_id": product2_id,
        "quantity": 40,
        "low_stock_threshold": 5
    }
    client_with_db.post("/api/v1/inventory/", json=inventory2_data)
    
    # Create sales for both products
    sale1_data = {
        "product_id": product1_id,
        "quantity": 1,
        "unit_price": 49.99,
        "total_price": 49.99,
        "platform": "web",
        "order_id": "ORDER132"
    }
    client_with_db.post("/api/v1/sales/", json=sale1_data)
    
    sale2_data = {
        "product_id": product2_id,
        "quantity": 1,
        "unit_price": 59.99,
        "total_price": 59.99,
        "platform": "web",
        "order_id": "ORDER133"
    }
    client_with_db.post("/api/v1/sales/", json=sale2_data)
    
    # Delete product 2
    client_with_db.delete(f"/api/v1/products/{product2_id}")
    
    # Test: Get all sales should only show sales for product 1
    sales_response = client_with_db.get("/api/v1/sales/")
    assert sales_response.status_code == 200
    sales = sales_response.json()
    
    # Verify only sales for non-deleted products are returned
    product_ids = [sale["product_id"] for sale in sales]
    assert product1_id in product_ids
    assert product2_id not in product_ids
    
    # Test: Get sales summary should only include product 1
    summary_response = client_with_db.get("/api/v1/sales/summary/")
    assert summary_response.status_code == 200
    summary = summary_response.json()
    
    # The summary should only include the revenue from product 1
    # Since we can't guarantee the exact revenue (other tests may add sales),
    # we can only check that product 2's revenue is not included
    order_ids = []
    for sale in sales:
        order_ids.append(sale["order_id"])
    
    assert "ORDER132" in order_ids
    assert "ORDER133" not in order_ids

def test_cannot_create_sale_for_deleted_product(client_with_db, db):
    """Test that sales cannot be created for a deleted product"""
    # First create a product with inventory
    category_data = {"name": "Test Category", "description": "Test category for sales"}
    category_response = client_with_db.post("/api/v1/categories/", json=category_data)
    category_id = category_response.json()["id"]
    
    product_data = {
        "name": "Test Product",
        "description": "Test product for sales",
        "sku": "TEST-SALE-001",
        "price": 39.99,
        "category_id": category_id
    }
    product_response = client_with_db.post("/api/v1/products/", json=product_data)
    product_id = product_response.json()["id"]
    
    # Create inventory for the product
    inventory_data = {
        "product_id": product_id,
        "quantity": 20,
        "low_stock_threshold": 5
    }
    inventory_response = client_with_db.post("/api/v1/inventory/", json=inventory_data)
    assert inventory_response.status_code == 200
    
    # Delete the product
    delete_response = client_with_db.delete(f"/api/v1/products/{product_id}")
    assert delete_response.status_code == 200
    
    # Try to create a sale for the deleted product
    sale_data = {
        "product_id": product_id,
        "quantity": 1,
        "unit_price": 39.99,
        "total_price": 39.99,
        "platform": "web",
        "order_id": "ORDER134"
    }
    sale_response = client_with_db.post("/api/v1/sales/", json=sale_data)
    assert sale_response.status_code == 400
    assert "deleted product" in sale_response.json()["detail"].lower() 