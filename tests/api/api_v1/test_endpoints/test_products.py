import pytest
from app import crud

def test_create_product(client_with_db, db):
    """Test creating a new product"""
    # First create a category
    category_data = {"name": "Test Category", "description": "Category for testing products"}
    category_response = client_with_db.post("/api/v1/categories/", json=category_data)
    category_id = category_response.json()["id"]
    
    # Create product
    product_data = {
        "name": "Test Product",
        "description": "Test product description",
        "sku": "TEST-PROD-001",
        "price": 29.99,
        "category_id": category_id
    }
    response = client_with_db.post("/api/v1/products/", json=product_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == product_data["name"]
    assert data["description"] == product_data["description"]
    assert data["sku"] == product_data["sku"]
    assert data["price"] == product_data["price"]
    assert data["category_id"] == category_id
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data
    assert data["deleted_at"] is None

def test_duplicate_sku(client_with_db, db):
    """Test that duplicate SKUs are rejected"""
    # First create a category
    category_data = {"name": "Test Category", "description": "Category for testing duplicate SKUs"}
    category_response = client_with_db.post("/api/v1/categories/", json=category_data)
    category_id = category_response.json()["id"]
    
    # Create first product
    product_data = {
        "name": "First Product",
        "description": "First test product",
        "sku": "DUPLICATE-SKU",
        "price": 19.99,
        "category_id": category_id
    }
    response = client_with_db.post("/api/v1/products/", json=product_data)
    assert response.status_code == 200
    
    # Try to create another with same SKU
    product_data["name"] = "Second Product"
    response = client_with_db.post("/api/v1/products/", json=product_data)
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"].lower()

def test_get_products(client_with_db, db):
    """Test retrieving all products"""
    # First create a category
    category_data = {"name": "Test Category", "description": "Category for testing product listing"}
    category_response = client_with_db.post("/api/v1/categories/", json=category_data)
    category_id = category_response.json()["id"]
    
    # Create test products
    product1_data = {
        "name": "Product 1",
        "description": "First test product",
        "sku": "TEST-LIST-001",
        "price": 19.99,
        "category_id": category_id
    }
    product2_data = {
        "name": "Product 2",
        "description": "Second test product",
        "sku": "TEST-LIST-002",
        "price": 29.99,
        "category_id": category_id
    }
    
    client_with_db.post("/api/v1/products/", json=product1_data)
    client_with_db.post("/api/v1/products/", json=product2_data)
    
    # Get all products
    response = client_with_db.get("/api/v1/products/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2
    
    # Verify our test products are in the response
    product_skus = [p["sku"] for p in data]
    assert "TEST-LIST-001" in product_skus
    assert "TEST-LIST-002" in product_skus

def test_get_product_by_id(client_with_db, db):
    """Test retrieving a specific product by ID"""
    # First create a category
    category_data = {"name": "Test Category", "description": "Category for testing get product by ID"}
    category_response = client_with_db.post("/api/v1/categories/", json=category_data)
    category_id = category_response.json()["id"]
    
    # Create a test product
    product_data = {
        "name": "Test Get By ID",
        "description": "Product to test get by ID",
        "sku": "TEST-GET-001",
        "price": 39.99,
        "category_id": category_id
    }
    create_response = client_with_db.post("/api/v1/products/", json=product_data)
    product_id = create_response.json()["id"]
    
    # Get the product by ID
    response = client_with_db.get(f"/api/v1/products/{product_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == product_id
    assert data["name"] == product_data["name"]
    assert data["description"] == product_data["description"]
    assert data["sku"] == product_data["sku"]
    assert data["price"] == product_data["price"]
    assert data["category_id"] == category_id

def test_get_nonexistent_product(client_with_db, db):
    """Test retrieving a non-existent product"""
    # Use a large ID that's unlikely to exist
    response = client_with_db.get("/api/v1/products/9999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()

def test_update_product(client_with_db, db):
    """Test updating a product"""
    # First create a category
    category_data = {"name": "Test Category", "description": "Category for testing product update"}
    category_response = client_with_db.post("/api/v1/categories/", json=category_data)
    category_id = category_response.json()["id"]
    
    # Create a test product
    original_data = {
        "name": "Original Name",
        "description": "Original description",
        "sku": "TEST-UPDATE-001",
        "price": 49.99,
        "category_id": category_id
    }
    create_response = client_with_db.post("/api/v1/products/", json=original_data)
    product_id = create_response.json()["id"]
    
    # Update the product
    update_data = {
        "name": "Updated Name",
        "description": "Updated description",
        "price": 59.99
    }
    update_response = client_with_db.put(f"/api/v1/products/{product_id}", json=update_data)
    assert update_response.status_code == 200
    updated_data = update_response.json()
    assert updated_data["id"] == product_id
    assert updated_data["name"] == update_data["name"]
    assert updated_data["description"] == update_data["description"]
    assert updated_data["price"] == update_data["price"]
    # SKU should remain unchanged
    assert updated_data["sku"] == original_data["sku"]
    
    # Verify the changes persisted
    get_response = client_with_db.get(f"/api/v1/products/{product_id}")
    assert get_response.status_code == 200
    get_data = get_response.json()
    assert get_data["name"] == update_data["name"]
    assert get_data["description"] == update_data["description"]
    assert get_data["price"] == update_data["price"]

def test_update_nonexistent_product(client_with_db, db):
    """Test updating a non-existent product"""
    update_data = {"name": "Updated Name", "description": "Updated description"}
    response = client_with_db.put("/api/v1/products/9999", json=update_data)
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()

def test_soft_delete_product(client_with_db, db):
    """Test soft deletion of a product"""
    # First create a test product
    category_data = {"name": "Test Category", "description": "Test category for deletion"}
    category_response = client_with_db.post("/api/v1/categories/", json=category_data)
    assert category_response.status_code == 200
    category_id = category_response.json()["id"]
    
    product_data = {
        "name": "Test Product",
        "description": "Test product for deletion",
        "sku": "TEST-DELETE-001",
        "price": 19.99,
        "category_id": category_id
    }
    product_response = client_with_db.post("/api/v1/products/", json=product_data)
    assert product_response.status_code == 200
    product_id = product_response.json()["id"]
    
    # Test soft deletion
    delete_response = client_with_db.delete(f"/api/v1/products/{product_id}")
    assert delete_response.status_code == 200
    
    # Verify product is not returned in normal get
    get_response = client_with_db.get(f"/api/v1/products/{product_id}")
    assert get_response.status_code == 404
    
    # Verify product appears in deleted products endpoint
    deleted_response = client_with_db.get("/api/v1/products/deleted/")
    assert deleted_response.status_code == 200
    deleted_products = deleted_response.json()
    deleted_product_ids = [p["id"] for p in deleted_products]
    assert product_id in deleted_product_ids
    
    # Test product restoration
    restore_response = client_with_db.put(f"/api/v1/products/restore/{product_id}")
    assert restore_response.status_code == 200
    
    # Verify product is now returned in normal get
    get_response = client_with_db.get(f"/api/v1/products/{product_id}")
    assert get_response.status_code == 200
    assert get_response.json()["id"] == product_id

def test_delete_nonexistent_product(client_with_db, db):
    """Test deleting a non-existent product"""
    response = client_with_db.delete("/api/v1/products/9999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()

def test_restore_nonexistent_product(client_with_db, db):
    """Test restoring a non-existent product"""
    response = client_with_db.put("/api/v1/products/restore/9999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()

def test_restore_non_deleted_product(client_with_db, db):
    """Test attempting to restore a product that isn't deleted"""
    # Create a product
    category_data = {"name": "Test Category", "description": "Category for testing product restore"}
    category_response = client_with_db.post("/api/v1/categories/", json=category_data)
    category_id = category_response.json()["id"]
    
    product_data = {
        "name": "Active Product",
        "description": "Product that's not deleted",
        "sku": "TEST-ACTIVE-001",
        "price": 19.99,
        "category_id": category_id
    }
    product_response = client_with_db.post("/api/v1/products/", json=product_data)
    assert product_response.status_code == 200
    product_id = product_response.json()["id"]
    
    # Try to restore it (should fail since it's not deleted)
    restore_response = client_with_db.put(f"/api/v1/products/restore/{product_id}")
    assert restore_response.status_code == 400
    assert "not deleted" in restore_response.json()["detail"].lower()

def test_get_deleted_products_empty(client_with_db, db):
    """Test getting deleted products when none exist"""
    # Create and then immediately restore a product to ensure deleted list is empty
    category_data = {"name": "Test Category", "description": "Temporary category"}
    category_response = client_with_db.post("/api/v1/categories/", json=category_data)
    category_id = category_response.json()["id"]
    
    product_data = {
        "name": "Temp Product",
        "description": "Temporary product",
        "sku": "TEST-TEMP-001",
        "price": 19.99,
        "category_id": category_id
    }
    product_response = client_with_db.post("/api/v1/products/", json=product_data)
    product_id = product_response.json()["id"]
    
    # Delete the product
    client_with_db.delete(f"/api/v1/products/{product_id}")
    
    # Restore it
    client_with_db.put(f"/api/v1/products/restore/{product_id}")
    
    # Verify deleted products list is empty
    response = client_with_db.get("/api/v1/products/deleted/")
    assert response.status_code == 200
    assert response.json() == []

def test_cannot_update_deleted_product(client_with_db, db):
    """Test that deleted products cannot be updated"""
    # Create and delete a product
    category_data = {"name": "Test Category", "description": "Category for testing"}
    category_response = client_with_db.post("/api/v1/categories/", json=category_data)
    category_id = category_response.json()["id"]
    
    product_data = {
        "name": "Product To Delete",
        "description": "Product to be deleted",
        "sku": "TEST-TODELETE-001",
        "price": 19.99,
        "category_id": category_id
    }
    product_response = client_with_db.post("/api/v1/products/", json=product_data)
    product_id = product_response.json()["id"]
    
    # Delete the product
    client_with_db.delete(f"/api/v1/products/{product_id}")
    
    # Try to update the deleted product
    update_data = {"name": "Updated Name", "description": "Updated description"}
    update_response = client_with_db.put(f"/api/v1/products/{product_id}", json=update_data)
    assert update_response.status_code == 400
    assert "deleted" in update_response.json()["detail"].lower()

def test_get_products_by_category(client_with_db, db):
    """Test getting products filtered by category"""
    # Create two categories
    category1_data = {"name": "Category 1", "description": "First test category"}
    category2_data = {"name": "Category 2", "description": "Second test category"}
    
    category1_response = client_with_db.post("/api/v1/categories/", json=category1_data)
    category1_id = category1_response.json()["id"]
    
    category2_response = client_with_db.post("/api/v1/categories/", json=category2_data)
    category2_id = category2_response.json()["id"]
    
    # Create products in each category
    product1_data = {
        "name": "Product in Category 1",
        "description": "Product in first category",
        "sku": "TEST-CAT1-001",
        "price": 19.99,
        "category_id": category1_id
    }
    
    product2_data = {
        "name": "Product in Category 2",
        "description": "Product in second category",
        "sku": "TEST-CAT2-001",
        "price": 29.99,
        "category_id": category2_id
    }
    
    client_with_db.post("/api/v1/products/", json=product1_data)
    client_with_db.post("/api/v1/products/", json=product2_data)
    
    # Get products from category 1
    response = client_with_db.get(f"/api/v1/products/category/{category1_id}")
    assert response.status_code == 200
    products = response.json()
    
    # Should only have products from category 1
    assert len(products) > 0
    for product in products:
        assert product["category_id"] == category1_id
    
    product_names = [p["name"] for p in products]
    assert "Product in Category 1" in product_names
    assert "Product in Category 2" not in product_names

def test_search_products(client_with_db, db):
    """Test searching for products by name"""
    # Create a category
    category_data = {"name": "Test Category", "description": "Category for testing product search"}
    category_response = client_with_db.post("/api/v1/categories/", json=category_data)
    category_id = category_response.json()["id"]
    
    # Create products with different names
    product1_data = {
        "name": "Unique Product Name",
        "description": "Product with unique name",
        "sku": "TEST-SEARCH-001",
        "price": 19.99,
        "category_id": category_id
    }
    
    product2_data = {
        "name": "Different Product",
        "description": "Product with different name",
        "sku": "TEST-SEARCH-002",
        "price": 29.99,
        "category_id": category_id
    }
    
    client_with_db.post("/api/v1/products/", json=product1_data)
    client_with_db.post("/api/v1/products/", json=product2_data)
    
    # Search for "Unique"
    response = client_with_db.get("/api/v1/products/search/?query=Unique")
    assert response.status_code == 200
    products = response.json()
    
    # Should only find the first product
    assert len(products) > 0
    product_names = [p["name"] for p in products]
    assert "Unique Product Name" in product_names
    assert "Different Product" not in product_names

def test_cannot_create_inventory_for_deleted_product(client_with_db, db):
    """Test that inventory cannot be created for a deleted product"""
    # First create and then delete a product
    category_data = {"name": "Test Category", "description": "Test category for inventory"}
    category_response = client_with_db.post("/api/v1/categories/", json=category_data)
    category_id = category_response.json()["id"]
    
    product_data = {
        "name": "Test Product",
        "description": "Test product for inventory",
        "sku": "TEST-INV-001",
        "price": 29.99,
        "category_id": category_id
    }
    product_response = client_with_db.post("/api/v1/products/", json=product_data)
    product_id = product_response.json()["id"]
    
    # Delete the product
    delete_response = client_with_db.delete(f"/api/v1/products/{product_id}")
    assert delete_response.status_code == 200
    
    # Try to create inventory for the deleted product
    inventory_data = {
        "product_id": product_id,
        "quantity": 10,
        "low_stock_threshold": 5
    }
    inventory_response = client_with_db.post("/api/v1/inventory/", json=inventory_data)
    assert inventory_response.status_code == 400
    assert "deleted product" in inventory_response.json()["detail"].lower()

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
        "order_id": "ORDER12345"
    }
    sale_response = client_with_db.post("/api/v1/sales/", json=sale_data)
    assert sale_response.status_code == 400
    assert "deleted product" in sale_response.json()["detail"].lower() 