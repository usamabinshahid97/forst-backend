import pytest
from app import crud

def test_create_category(client_with_db, db):
    """Test creating a new category"""
    category_data = {"name": "Test Category", "description": "Test category description"}
    response = client_with_db.post("/api/v1/categories/", json=category_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == category_data["name"]
    assert data["description"] == category_data["description"]
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data
    assert data["deleted_at"] is None

def test_duplicate_category_name(client_with_db, db):
    """Test that duplicate category names are rejected"""
    category_data = {"name": "Duplicate Category", "description": "Test duplicate category"}
    # Create first category
    response = client_with_db.post("/api/v1/categories/", json=category_data)
    assert response.status_code == 200
    
    # Try to create another with the same name
    response = client_with_db.post("/api/v1/categories/", json=category_data)
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"].lower()

def test_get_categories(client_with_db, db):
    """Test retrieving all categories"""
    # Create test categories
    category1_data = {"name": "Category 1", "description": "First test category"}
    category2_data = {"name": "Category 2", "description": "Second test category"}
    
    client_with_db.post("/api/v1/categories/", json=category1_data)
    client_with_db.post("/api/v1/categories/", json=category2_data)
    
    # Get all categories
    response = client_with_db.get("/api/v1/categories/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2
    
    # Verify our test categories are in the response
    category_names = [c["name"] for c in data]
    assert "Category 1" in category_names
    assert "Category 2" in category_names

def test_get_category_by_id(client_with_db, db):
    """Test retrieving a specific category by ID"""
    # Create a test category
    category_data = {"name": "Test Category by ID", "description": "Category to test get by ID"}
    create_response = client_with_db.post("/api/v1/categories/", json=category_data)
    category_id = create_response.json()["id"]
    
    # Get the category by ID
    response = client_with_db.get(f"/api/v1/categories/{category_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == category_id
    assert data["name"] == category_data["name"]
    assert data["description"] == category_data["description"]

def test_get_nonexistent_category(client_with_db, db):
    """Test retrieving a non-existent category"""
    # Use a large ID that's unlikely to exist
    response = client_with_db.get("/api/v1/categories/9999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()

def test_update_category(client_with_db, db):
    """Test updating a category"""
    # Create a test category
    original_data = {"name": "Original Name", "description": "Original description"}
    create_response = client_with_db.post("/api/v1/categories/", json=original_data)
    category_id = create_response.json()["id"]
    
    # Update the category
    update_data = {"name": "Updated Name", "description": "Updated description"}
    update_response = client_with_db.put(f"/api/v1/categories/{category_id}", json=update_data)
    assert update_response.status_code == 200
    updated_data = update_response.json()
    assert updated_data["id"] == category_id
    assert updated_data["name"] == update_data["name"]
    assert updated_data["description"] == update_data["description"]
    
    # Verify the changes persisted
    get_response = client_with_db.get(f"/api/v1/categories/{category_id}")
    assert get_response.status_code == 200
    get_data = get_response.json()
    assert get_data["name"] == update_data["name"]
    assert get_data["description"] == update_data["description"]

def test_update_nonexistent_category(client_with_db, db):
    """Test updating a non-existent category"""
    update_data = {"name": "Updated Name", "description": "Updated description"}
    response = client_with_db.put("/api/v1/categories/9999", json=update_data)
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()

def test_soft_delete_category(client_with_db, db):
    """Test soft deletion of a category"""
    # First create a test category
    category_data = {"name": "Test Category for Deletion", "description": "Test category for deletion"}
    category_response = client_with_db.post("/api/v1/categories/", json=category_data)
    assert category_response.status_code == 200
    category_id = category_response.json()["id"]
    
    # Test soft deletion
    delete_response = client_with_db.delete(f"/api/v1/categories/{category_id}")
    assert delete_response.status_code == 200
    
    # Verify category is not returned in normal get
    get_response = client_with_db.get(f"/api/v1/categories/{category_id}")
    assert get_response.status_code == 404
    
    # Verify category appears in deleted categories endpoint
    deleted_response = client_with_db.get("/api/v1/categories/deleted/")
    assert deleted_response.status_code == 200
    deleted_categories = deleted_response.json()
    deleted_category_ids = [c["id"] for c in deleted_categories]
    assert category_id in deleted_category_ids
    
    # Test category restoration
    restore_response = client_with_db.put(f"/api/v1/categories/restore/{category_id}")
    assert restore_response.status_code == 200
    
    # Verify category is now returned in normal get
    get_response = client_with_db.get(f"/api/v1/categories/{category_id}")
    assert get_response.status_code == 200
    assert get_response.json()["id"] == category_id

def test_delete_nonexistent_category(client_with_db, db):
    """Test deleting a non-existent category"""
    response = client_with_db.delete("/api/v1/categories/9999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()

def test_cannot_delete_category_with_products(client_with_db, db):
    """Test that categories with active products cannot be deleted"""
    # First create a test category
    category_data = {"name": "Test Category with Products", "description": "Test category with products"}
    category_response = client_with_db.post("/api/v1/categories/", json=category_data)
    assert category_response.status_code == 200
    category_id = category_response.json()["id"]
    
    # Create a product in this category
    product_data = {
        "name": "Test Product",
        "description": "Test product in category",
        "sku": "TEST-CAT-001",
        "price": 19.99,
        "category_id": category_id
    }
    product_response = client_with_db.post("/api/v1/products/", json=product_data)
    assert product_response.status_code == 200
    
    # Try to delete the category
    delete_response = client_with_db.delete(f"/api/v1/categories/{category_id}")
    assert delete_response.status_code == 400
    assert "cannot delete category with active products" in delete_response.json()["detail"].lower()
    
    # Delete the product
    product_id = product_response.json()["id"]
    client_with_db.delete(f"/api/v1/products/{product_id}")
    
    # Now we should be able to delete the category
    delete_response = client_with_db.delete(f"/api/v1/categories/{category_id}")
    assert delete_response.status_code == 200

def test_cannot_create_product_in_deleted_category(client_with_db, db):
    """Test that products cannot be created in deleted categories"""
    # First create and then delete a category
    category_data = {"name": "Deleted Category", "description": "Category to be deleted"}
    category_response = client_with_db.post("/api/v1/categories/", json=category_data)
    assert category_response.status_code == 200
    category_id = category_response.json()["id"]
    
    # Delete the category
    delete_response = client_with_db.delete(f"/api/v1/categories/{category_id}")
    assert delete_response.status_code == 200
    
    # Try to create a product in the deleted category
    product_data = {
        "name": "Test Product",
        "description": "Test product in deleted category",
        "sku": "TEST-DELCAT-001",
        "price": 29.99,
        "category_id": category_id
    }
    product_response = client_with_db.post("/api/v1/products/", json=product_data)
    assert product_response.status_code == 400
    assert "deleted category" in product_response.json()["detail"].lower()

def test_cannot_update_product_to_deleted_category(client_with_db, db):
    """Test that products cannot be moved to deleted categories"""
    # Create two categories - one to keep, one to delete
    category1_data = {"name": "Active Category", "description": "Category to keep"}
    category1_response = client_with_db.post("/api/v1/categories/", json=category1_data)
    assert category1_response.status_code == 200
    category1_id = category1_response.json()["id"]
    
    category2_data = {"name": "Category To Delete", "description": "Category to delete"}
    category2_response = client_with_db.post("/api/v1/categories/", json=category2_data)
    assert category2_response.status_code == 200
    category2_id = category2_response.json()["id"]
    
    # Create a product in the active category
    product_data = {
        "name": "Test Product",
        "description": "Test product for category update",
        "sku": "TEST-CATUPDATE-001",
        "price": 39.99,
        "category_id": category1_id
    }
    product_response = client_with_db.post("/api/v1/products/", json=product_data)
    assert product_response.status_code == 200
    product_id = product_response.json()["id"]
    
    # Delete the second category
    delete_response = client_with_db.delete(f"/api/v1/categories/{category2_id}")
    assert delete_response.status_code == 200
    
    # Try to update the product to the deleted category
    update_data = {
        "category_id": category2_id
    }
    update_response = client_with_db.put(f"/api/v1/products/{product_id}", json=update_data)
    assert update_response.status_code == 400
    assert "deleted category" in update_response.json()["detail"].lower()

def test_restore_nonexistent_category(client_with_db, db):
    """Test restoring a non-existent category"""
    response = client_with_db.put("/api/v1/categories/restore/9999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()

def test_restore_non_deleted_category(client_with_db, db):
    """Test attempting to restore a category that isn't deleted"""
    # Create a category
    category_data = {"name": "Active Category", "description": "Category that's not deleted"}
    category_response = client_with_db.post("/api/v1/categories/", json=category_data)
    assert category_response.status_code == 200
    category_id = category_response.json()["id"]
    
    # Try to restore it (should fail since it's not deleted)
    restore_response = client_with_db.put(f"/api/v1/categories/restore/{category_id}")
    assert restore_response.status_code == 400
    assert "not deleted" in restore_response.json()["detail"].lower()

def test_get_deleted_categories_empty(client_with_db, db):
    """Test getting deleted categories when none exist"""
    # First make sure there are no deleted categories
    # (We need to create and delete all test categories within this test)
    
    # Create and then immediately restore a category to ensure deleted list is empty
    category_data = {"name": "Temp Category", "description": "Temporary category"}
    category_response = client_with_db.post("/api/v1/categories/", json=category_data)
    category_id = category_response.json()["id"]
    
    # Delete the category
    client_with_db.delete(f"/api/v1/categories/{category_id}")
    
    # Restore it
    client_with_db.put(f"/api/v1/categories/restore/{category_id}")
    
    # Verify deleted categories list is empty
    response = client_with_db.get("/api/v1/categories/deleted/")
    assert response.status_code == 200
    assert response.json() == []

def test_cannot_update_deleted_category(client_with_db, db):
    """Test that deleted categories cannot be updated"""
    # Create and delete a category
    category_data = {"name": "Category To Delete", "description": "Category to be deleted"}
    category_response = client_with_db.post("/api/v1/categories/", json=category_data)
    category_id = category_response.json()["id"]
    
    # Delete the category
    client_with_db.delete(f"/api/v1/categories/{category_id}")
    
    # Try to update the deleted category
    update_data = {"name": "Updated Name", "description": "Updated description"}
    update_response = client_with_db.put(f"/api/v1/categories/{category_id}", json=update_data)
    assert update_response.status_code == 400
    assert "deleted" in update_response.json()["detail"].lower() 