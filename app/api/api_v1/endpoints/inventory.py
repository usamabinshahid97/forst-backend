from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, schemas
from app.db.session import get_db

router = APIRouter()

@router.get("/", response_model=List[schemas.Inventory])
def read_inventory_items(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve all inventory items.
    """
    inventory_items = crud.inventory.get_multi(db, skip=skip, limit=limit)
    return inventory_items

@router.get("/low-stock/", response_model=List[schemas.Inventory])
def read_low_stock_items(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve low stock inventory items.
    """
    low_stock_items = crud.inventory.get_low_stock_items(db, skip=skip, limit=limit)
    return low_stock_items

@router.post("/", response_model=schemas.Inventory)
def create_inventory(
    *,
    db: Session = Depends(get_db),
    inventory_in: schemas.InventoryCreate,
) -> Any:
    """
    Create new inventory item.
    """
    # Check if product exists and is not deleted
    product = crud.product.get(db, id=inventory_in.product_id)
    if not product:
        raise HTTPException(
            status_code=400,
            detail=f"Product with ID {inventory_in.product_id} does not exist.",
        )
    
    if product.deleted_at is not None:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot create inventory for deleted product (ID: {inventory_in.product_id}).",
        )
    
    # Check if inventory already exists for this product
    existing_inventory = crud.inventory.get_by_product_id(db, product_id=inventory_in.product_id)
    if existing_inventory:
        raise HTTPException(
            status_code=400,
            detail=f"Inventory already exists for product with ID {inventory_in.product_id}.",
        )
        
    return crud.inventory.create(db, obj_in=inventory_in)

@router.get("/{inventory_id}", response_model=schemas.Inventory)
def read_inventory(
    *,
    db: Session = Depends(get_db),
    inventory_id: int,
) -> Any:
    """
    Get inventory by ID.
    """
    inventory = crud.inventory.get(db, id=inventory_id)
    if not inventory:
        raise HTTPException(
            status_code=404,
            detail="Inventory not found",
        )
    return inventory

@router.get("/product/{product_id}", response_model=schemas.Inventory)
def read_inventory_by_product(
    *,
    db: Session = Depends(get_db),
    product_id: int,
) -> Any:
    """
    Get inventory by product ID.
    """
    # Check if product exists and is not deleted
    product = crud.product.get(db, id=product_id)
    if not product:
        raise HTTPException(
            status_code=404,
            detail=f"Product with ID {product_id} not found",
        )
        
    if product.deleted_at is not None:
        raise HTTPException(
            status_code=404,
            detail=f"Product with ID {product_id} is deleted",
        )
        
    inventory = crud.inventory.get_by_product_id(db, product_id=product_id)
    if not inventory:
        raise HTTPException(
            status_code=404,
            detail=f"Inventory not found for product ID {product_id}",
        )
    return inventory

@router.put("/{inventory_id}", response_model=schemas.Inventory)
def update_inventory(
    *,
    db: Session = Depends(get_db),
    inventory_id: int,
    inventory_in: schemas.InventoryUpdate,
) -> Any:
    """
    Update an inventory item.
    """
    inventory = crud.inventory.get(db, id=inventory_id)
    if not inventory:
        raise HTTPException(
            status_code=404,
            detail="Inventory not found",
        )
    return crud.inventory.update(db, db_obj=inventory, obj_in=inventory_in)

@router.post("/{inventory_id}/restock", response_model=schemas.Inventory)
def restock_inventory(
    *,
    db: Session = Depends(get_db),
    inventory_id: int,
    quantity: schemas.InventoryRestock,
) -> Any:
    """
    Restock an inventory item by inventory ID.
    """
    inventory = crud.inventory.get(db, id=inventory_id)
    if not inventory:
        raise HTTPException(
            status_code=404,
            detail="Inventory not found",
        )
    
    if quantity.quantity <= 0:
        raise HTTPException(
            status_code=400,
            detail="Quantity must be positive for restocking",
        )
    
    # Check if product is not deleted
    product = crud.product.get(db, id=inventory.product_id)
    if product.deleted_at is not None:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot restock deleted product (ID: {inventory.product_id})",
        )
    
    return crud.inventory.update_stock(
        db, product_id=inventory.product_id, quantity_change=quantity.quantity, restock=True
    )

@router.put("/product/{product_id}/restock", response_model=schemas.Inventory)
def restock_product(
    *,
    db: Session = Depends(get_db),
    product_id: int,
    quantity: int,
) -> Any:
    """
    Restock a product's inventory.
    """
    if quantity <= 0:
        raise HTTPException(
            status_code=400,
            detail="Quantity must be positive for restocking",
        )
    
    # Check if product exists and is not deleted
    product = crud.product.get(db, id=product_id)
    if not product:
        raise HTTPException(
            status_code=404,
            detail=f"Product with ID {product_id} not found",
        )
        
    if product.deleted_at is not None:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot restock deleted product (ID: {product_id})",
        )
        
    inventory = crud.inventory.update_stock(
        db, product_id=product_id, quantity_change=quantity, restock=True
    )
    
    if not inventory:
        raise HTTPException(
            status_code=404,
            detail=f"Inventory not found for product ID {product_id}",
        )
        
    return inventory 