from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app import crud, schemas
from app.db.session import get_db

router = APIRouter()

@router.get("/", response_model=List[schemas.Product])
def read_products(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    category_id: Optional[int] = None,
    search: Optional[str] = None,
) -> Any:
    """
    Retrieve products with optional filtering.
    """
    if category_id:
        products = crud.product.get_by_category(db, category_id=category_id, skip=skip, limit=limit)
    elif search:
        products = crud.product.search_products(db, query=search, skip=skip, limit=limit)
    else:
        products = crud.product.get_multi(db, skip=skip, limit=limit)
    return products

@router.get("/category/{category_id}", response_model=List[schemas.Product])
def read_products_by_category(
    *,
    db: Session = Depends(get_db),
    category_id: int,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve products by category ID.
    """
    # Check if category exists
    category = crud.category.get(db, id=category_id)
    if not category:
        raise HTTPException(
            status_code=404,
            detail=f"Category with ID {category_id} not found",
        )
        
    products = crud.product.get_by_category(db, category_id=category_id, skip=skip, limit=limit)
    return products

@router.get("/search/", response_model=List[schemas.Product])
def search_products(
    *,
    db: Session = Depends(get_db),
    query: str = Query(..., min_length=1, description="Search query"),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Search products by name.
    """
    products = crud.product.search_products(db, query=query, skip=skip, limit=limit)
    return products

@router.post("/", response_model=schemas.Product)
def create_product(
    *,
    db: Session = Depends(get_db),
    product_in: schemas.ProductCreate,
) -> Any:
    """
    Create new product.
    """
    # Check if product with same SKU exists
    product = crud.product.get_by_sku(db, sku=product_in.sku)
    if product:
        raise HTTPException(
            status_code=400,
            detail="Product with this SKU already exists.",
        )
    # Check if category exists
    category = crud.category.get(db, id=product_in.category_id)
    if not category:
        raise HTTPException(
            status_code=400,
            detail=f"Category with ID {product_in.category_id} does not exist.",
        )
    # Check if category is deleted
    if category.deleted_at is not None:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot create product in deleted category (ID: {product_in.category_id}). Restore the category first.",
        )
    return crud.product.create(db, obj_in=product_in)

@router.get("/{product_id}", response_model=schemas.Product)
def read_product(
    *,
    db: Session = Depends(get_db),
    product_id: int,
) -> Any:
    """
    Get product by ID.
    """
    product = crud.product.get(db, id=product_id)
    if not product or product.deleted_at is not None:
        raise HTTPException(
            status_code=404,
            detail="Product not found",
        )
    return product

@router.put("/{product_id}", response_model=schemas.Product)
def update_product(
    *,
    db: Session = Depends(get_db),
    product_id: int,
    product_in: schemas.ProductUpdate,
) -> Any:
    """
    Update a product.
    """
    product = crud.product.get(db, id=product_id)
    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found",
        )
    
    if product.deleted_at is not None:
        raise HTTPException(
            status_code=400,
            detail="Cannot update a deleted product. Restore it first.",
        )
        
    # If category_id is provided, check if it exists and is not deleted
    if product_in.category_id is not None:
        category = crud.category.get(db, id=product_in.category_id)
        if not category:
            raise HTTPException(
                status_code=400,
                detail=f"Category with ID {product_in.category_id} does not exist.",
            )
        # Check if category is deleted
        if category.deleted_at is not None:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot move product to deleted category (ID: {product_in.category_id}). Restore the category first.",
            )
    return crud.product.update(db, db_obj=product, obj_in=product_in)

@router.delete("/{product_id}", response_model=schemas.Product)
def delete_product(
    *,
    db: Session = Depends(get_db),
    product_id: int,
) -> Any:
    """
    Delete a product (soft delete).
    """
    product = crud.product.get(db, id=product_id)
    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found",
        )
    if product.deleted_at is not None:
        raise HTTPException(
            status_code=404,
            detail="Product already deleted",
        )
    return crud.product.remove(db, id=product_id)

@router.get("/deleted/", response_model=List[schemas.Product])
def read_deleted_products(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve all deleted products.
    """
    products = crud.product.get_deleted(db, skip=skip, limit=limit)
    return products

@router.put("/restore/{product_id}", response_model=schemas.Product)
def restore_product(
    *,
    db: Session = Depends(get_db),
    product_id: int,
) -> Any:
    """
    Restore a previously deleted product.
    """
    product = crud.product.get(db, id=product_id)
    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found",
        )
    if product.deleted_at is None:
        raise HTTPException(
            status_code=400,
            detail="Product is not deleted",
        )
    return crud.product.restore(db, id=product_id)

@router.get("/with-inventory/", response_model=List[schemas.ProductWithInventory])
def read_products_with_inventory(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve products with their inventory information.
    """
    # Get only non-deleted products using the CRUD method
    products = crud.product.get_multi(db, skip=skip, limit=limit)
    
    result = []
    for product in products:
        inventory = crud.inventory.get_by_product_id(db, product_id=product.id)
        if inventory:
            # Create a dictionary with product attributes
            product_dict = {
                "id": product.id,
                "name": product.name,
                "description": product.description,
                "sku": product.sku,
                "price": product.price,
                "category_id": product.category_id,
                "created_at": product.created_at,
                "updated_at": product.updated_at,
                "deleted_at": product.deleted_at,
                "inventory_quantity": inventory.quantity,
                "low_stock_threshold": inventory.low_stock_threshold,
                "is_low_stock": inventory.is_low_stock
            }
            result.append(product_dict)
    
    return result 