import pytest
from app import crud

def test_create_inventory(client_with_db, db):
    """Test creating inventory for a product"""
    # First create a category and product
    category_data = {"name": "Test Category", "description": "Category for testing inventory"}
    category_response = client_with_db.post("/api/v1/categories/", json=category_data)
    category_id = category_response.json()["id"]
    
    product_data = {
        "name": "Test Product",
        "description": "Product for testing inventory",
        "sku": "TEST-INV-001",
        "price": 29.99,
        "category_id": category_id
    }
    product_response = client_with_db.post("/api/v1/products/", json=product_data)
    product_id = product_response.json()["id"]
    
    # Create inventory
    inventory_data = {
        "product_id": product_id,
        "quantity": 100,
        "low_stock_threshold": 20
    }
    response = client_with_db.post("/api/v1/inventory/", json=inventory_data)
    assert response.status_code == 200
    data = response.json()
    assert data["product_id"] == product_id
    assert data["quantity"] == inventory_data["quantity"]
    assert data["low_stock_threshold"] == inventory_data["low_stock_threshold"]
    assert "id" in data
    assert "updated_at" in data
    assert data["last_restock_date"] is None

def test_create_duplicate_inventory(client_with_db, db):
    """Test creating inventory for a product that already has inventory"""
    # First create a category and product
    category_data = {"name": "Test Category", "description": "Category for testing duplicate inventory"}
    category_response = client_with_db.post("/api/v1/categories/", json=category_data)
    category_id = category_response.json()["id"]
    
    product_data = {
        "name": "Test Product",
        "description": "Product for testing duplicate inventory",
        "sku": "TEST-DUPINV-001",
        "price": 39.99,
        "category_id": category_id
    }
    product_response = client_with_db.post("/api/v1/products/", json=product_data)
    product_id = product_response.json()["id"]
    
    # Create first inventory
    inventory_data = {
        "product_id": product_id,
        "quantity": 50,
        "low_stock_threshold": 10
    }
    response = client_with_db.post("/api/v1/inventory/", json=inventory_data)
    assert response.status_code == 200
    
    # Try to create second inventory for same product
    second_inventory_data = {
        "product_id": product_id,
        "quantity": 100,
        "low_stock_threshold": 20
    }
    response = client_with_db.post("/api/v1/inventory/", json=second_inventory_data)
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"].lower()

def test_get_all_inventory(client_with_db, db):
    """Test retrieving all inventory records"""
    # Create two products with inventory
    # First product and its inventory
    category_data = {"name": "Test Category", "description": "Category for testing inventory listing"}
    category_response = client_with_db.post("/api/v1/categories/", json=category_data)
    category_id = category_response.json()["id"]
    
    product1_data = {
        "name": "Product 1",
        "description": "First product for inventory listing",
        "sku": "TEST-INV-LIST-001",
        "price": 29.99,
        "category_id": category_id
    }
    product1_response = client_with_db.post("/api/v1/products/", json=product1_data)
    product1_id = product1_response.json()["id"]
    
    inventory1_data = {
        "product_id": product1_id,
        "quantity": 50,
        "low_stock_threshold": 10
    }
    client_with_db.post("/api/v1/inventory/", json=inventory1_data)
    
    # Second product and its inventory
    product2_data = {
        "name": "Product 2",
        "description": "Second product for inventory listing",
        "sku": "TEST-INV-LIST-002",
        "price": 39.99,
        "category_id": category_id
    }
    product2_response = client_with_db.post("/api/v1/products/", json=product2_data)
    product2_id = product2_response.json()["id"]
    
    inventory2_data = {
        "product_id": product2_id,
        "quantity": 75,
        "low_stock_threshold": 15
    }
    client_with_db.post("/api/v1/inventory/", json=inventory2_data)
    
    # Get all inventory
    response = client_with_db.get("/api/v1/inventory/")
    assert response.status_code == 200
    data = response.json()
    
    # Verify our test inventories are in the response
    product_ids = [inv["product_id"] for inv in data]
    assert product1_id in product_ids
    assert product2_id in product_ids

def test_get_inventory_by_id(client_with_db, db):
    """Test retrieving inventory by ID"""
    # Create a product with inventory
    category_data = {"name": "Test Category", "description": "Category for testing get inventory by ID"}
    category_response = client_with_db.post("/api/v1/categories/", json=category_data)
    category_id = category_response.json()["id"]
    
    product_data = {
        "name": "Test Product",
        "description": "Product for testing get inventory by ID",
        "sku": "TEST-INV-GET-001",
        "price": 49.99,
        "category_id": category_id
    }
    product_response = client_with_db.post("/api/v1/products/", json=product_data)
    product_id = product_response.json()["id"]
    
    inventory_data = {
        "product_id": product_id,
        "quantity": 60,
        "low_stock_threshold": 12
    }
    inventory_response = client_with_db.post("/api/v1/inventory/", json=inventory_data)
    inventory_id = inventory_response.json()["id"]
    
    # Get inventory by ID
    response = client_with_db.get(f"/api/v1/inventory/{inventory_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == inventory_id
    assert data["product_id"] == product_id
    assert data["quantity"] == inventory_data["quantity"]
    assert data["low_stock_threshold"] == inventory_data["low_stock_threshold"]

def test_get_nonexistent_inventory(client_with_db, db):
    """Test retrieving a non-existent inventory record"""
    response = client_with_db.get("/api/v1/inventory/9999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()

def test_get_inventory_by_product(client_with_db, db):
    """Test retrieving inventory by product ID"""
    # Create a product with inventory
    category_data = {"name": "Test Category", "description": "Category for testing get inventory by product"}
    category_response = client_with_db.post("/api/v1/categories/", json=category_data)
    category_id = category_response.json()["id"]
    
    product_data = {
        "name": "Test Product",
        "description": "Product for testing get inventory by product",
        "sku": "TEST-INV-GETPROD-001",
        "price": 59.99,
        "category_id": category_id
    }
    product_response = client_with_db.post("/api/v1/products/", json=product_data)
    product_id = product_response.json()["id"]
    
    inventory_data = {
        "product_id": product_id,
        "quantity": 70,
        "low_stock_threshold": 14
    }
    client_with_db.post("/api/v1/inventory/", json=inventory_data)
    
    # Get inventory by product ID
    response = client_with_db.get(f"/api/v1/inventory/product/{product_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["product_id"] == product_id
    assert data["quantity"] == inventory_data["quantity"]
    assert data["low_stock_threshold"] == inventory_data["low_stock_threshold"]

def test_get_inventory_by_nonexistent_product(client_with_db, db):
    """Test retrieving inventory for a non-existent product"""
    response = client_with_db.get("/api/v1/inventory/product/9999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()

def test_update_inventory(client_with_db, db):
    """Test updating inventory"""
    # Create a product with inventory
    category_data = {"name": "Test Category", "description": "Category for testing inventory update"}
    category_response = client_with_db.post("/api/v1/categories/", json=category_data)
    category_id = category_response.json()["id"]
    
    product_data = {
        "name": "Test Product",
        "description": "Product for testing inventory update",
        "sku": "TEST-INV-UPDATE-001",
        "price": 69.99,
        "category_id": category_id
    }
    product_response = client_with_db.post("/api/v1/products/", json=product_data)
    product_id = product_response.json()["id"]
    
    initial_inventory_data = {
        "product_id": product_id,
        "quantity": 80,
        "low_stock_threshold": 16
    }
    inventory_response = client_with_db.post("/api/v1/inventory/", json=initial_inventory_data)
    inventory_id = inventory_response.json()["id"]
    
    # Update the inventory
    update_data = {
        "quantity": 100,
        "low_stock_threshold": 20
    }
    update_response = client_with_db.put(f"/api/v1/inventory/{inventory_id}", json=update_data)
    assert update_response.status_code == 200
    updated_data = update_response.json()
    assert updated_data["id"] == inventory_id
    assert updated_data["product_id"] == product_id
    assert updated_data["quantity"] == update_data["quantity"]
    assert updated_data["low_stock_threshold"] == update_data["low_stock_threshold"]
    
    # Verify the changes persisted
    get_response = client_with_db.get(f"/api/v1/inventory/{inventory_id}")
    assert get_response.status_code == 200
    get_data = get_response.json()
    assert get_data["quantity"] == update_data["quantity"]
    assert get_data["low_stock_threshold"] == update_data["low_stock_threshold"]

def test_update_nonexistent_inventory(client_with_db, db):
    """Test updating a non-existent inventory record"""
    update_data = {"quantity": 100, "low_stock_threshold": 20}
    response = client_with_db.put("/api/v1/inventory/9999", json=update_data)
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()

def test_restock_inventory(client_with_db, db):
    """Test restocking inventory"""
    # Create a product with inventory
    category_data = {"name": "Test Category", "description": "Category for testing inventory restock"}
    category_response = client_with_db.post("/api/v1/categories/", json=category_data)
    category_id = category_response.json()["id"]
    
    product_data = {
        "name": "Test Product",
        "description": "Product for testing inventory restock",
        "sku": "TEST-INV-RESTOCK-001",
        "price": 79.99,
        "category_id": category_id
    }
    product_response = client_with_db.post("/api/v1/products/", json=product_data)
    product_id = product_response.json()["id"]
    
    initial_inventory_data = {
        "product_id": product_id,
        "quantity": 10,
        "low_stock_threshold": 20
    }
    inventory_response = client_with_db.post("/api/v1/inventory/", json=initial_inventory_data)
    inventory_id = inventory_response.json()["id"]
    
    # Restock the inventory
    restock_data = {
        "quantity": 50
    }
    restock_response = client_with_db.post(f"/api/v1/inventory/{inventory_id}/restock", json=restock_data)
    assert restock_response.status_code == 200
    restocked_data = restock_response.json()
    assert restocked_data["id"] == inventory_id
    assert restocked_data["quantity"] == initial_inventory_data["quantity"] + restock_data["quantity"]
    assert restocked_data["last_restock_date"] is not None
    
    # Verify the changes persisted
    get_response = client_with_db.get(f"/api/v1/inventory/{inventory_id}")
    assert get_response.status_code == 200
    get_data = get_response.json()
    assert get_data["quantity"] == initial_inventory_data["quantity"] + restock_data["quantity"]
    assert get_data["last_restock_date"] is not None

def test_restock_nonexistent_inventory(client_with_db, db):
    """Test restocking a non-existent inventory record"""
    restock_data = {"quantity": 50}
    response = client_with_db.post("/api/v1/inventory/9999/restock", json=restock_data)
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()

def test_get_low_stock_inventory(client_with_db, db):
    """Test retrieving low stock inventory"""
    # Create two products with inventory, one with low stock
    category_data = {"name": "Test Category", "description": "Category for testing low stock inventory"}
    category_response = client_with_db.post("/api/v1/categories/", json=category_data)
    category_id = category_response.json()["id"]
    
    # First product with normal stock
    product1_data = {
        "name": "Normal Stock Product",
        "description": "Product with normal stock level",
        "sku": "TEST-INV-NORMAL-001",
        "price": 29.99,
        "category_id": category_id
    }
    product1_response = client_with_db.post("/api/v1/products/", json=product1_data)
    product1_id = product1_response.json()["id"]
    
    inventory1_data = {
        "product_id": product1_id,
        "quantity": 50,
        "low_stock_threshold": 10
    }
    client_with_db.post("/api/v1/inventory/", json=inventory1_data)
    
    # Second product with low stock
    product2_data = {
        "name": "Low Stock Product",
        "description": "Product with low stock level",
        "sku": "TEST-INV-LOW-001",
        "price": 39.99,
        "category_id": category_id
    }
    product2_response = client_with_db.post("/api/v1/products/", json=product2_data)
    product2_id = product2_response.json()["id"]
    
    inventory2_data = {
        "product_id": product2_id,
        "quantity": 5,
        "low_stock_threshold": 10
    }
    client_with_db.post("/api/v1/inventory/", json=inventory2_data)
    
    # Get low stock inventory
    response = client_with_db.get("/api/v1/inventory/low-stock/")
    assert response.status_code == 200
    data = response.json()
    
    # Should include the low stock product but not the normal stock one
    product_ids = [inv["product_id"] for inv in data]
    assert product2_id in product_ids
    assert product1_id not in product_ids 