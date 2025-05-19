from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, schemas
from app.db.session import get_db

router = APIRouter()

@router.get("/", response_model=List[schemas.Category])
def read_categories(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve all non-deleted categories.
    """
    categories = crud.category.get_multi(db, skip=skip, limit=limit)
    return categories

@router.post("/", response_model=schemas.Category)
def create_category(
    *,
    db: Session = Depends(get_db),
    category_in: schemas.CategoryCreate,
) -> Any:
    """
    Create new category.
    """
    category = crud.category.get_by_name(db, name=category_in.name)
    if category:
        raise HTTPException(
            status_code=400,
            detail="Category with this name already exists.",
        )
    return crud.category.create(db, obj_in=category_in)

@router.get("/{category_id}", response_model=schemas.Category)
def read_category(
    *,
    db: Session = Depends(get_db),
    category_id: int,
) -> Any:
    """
    Get category by ID.
    """
    category = crud.category.get(db, id=category_id)
    if not category:
        raise HTTPException(
            status_code=404,
            detail="Category not found",
        )
    if category.deleted_at is not None:
        raise HTTPException(
            status_code=404,
            detail="Category not found",
        )
    return category

@router.put("/{category_id}", response_model=schemas.Category)
def update_category(
    *,
    db: Session = Depends(get_db),
    category_id: int,
    category_in: schemas.CategoryUpdate,
) -> Any:
    """
    Update a category.
    """
    category = crud.category.get(db, id=category_id)
    if not category:
        raise HTTPException(
            status_code=404,
            detail="Category not found",
        )
    if category.deleted_at is not None:
        raise HTTPException(
            status_code=400,
            detail="Cannot update a deleted category. Restore it first.",
        )
    return crud.category.update(db, db_obj=category, obj_in=category_in)

@router.delete("/{category_id}", response_model=schemas.Category)
def delete_category(
    *,
    db: Session = Depends(get_db),
    category_id: int,
) -> Any:
    """
    Delete a category (soft delete).
    """
    category = crud.category.get(db, id=category_id)
    if not category:
        raise HTTPException(
            status_code=404,
            detail="Category not found",
        )
    
    if category.deleted_at is not None:
        raise HTTPException(
            status_code=404,
            detail="Category already deleted",
        )
    
    # Check if category has any non-deleted products
    products = db.query(crud.product.model).filter(
        crud.product.model.category_id == category_id,
        crud.product.model.deleted_at == None
    ).all()
    
    if products:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete category with active products. Delete the products first or move them to another category.",
        )
    
    return crud.category.remove(db, id=category_id)

@router.get("/deleted/", response_model=List[schemas.Category])
def read_deleted_categories(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve all deleted categories.
    """
    categories = crud.category.get_deleted(db, skip=skip, limit=limit)
    return categories

@router.put("/restore/{category_id}", response_model=schemas.Category)
def restore_category(
    *,
    db: Session = Depends(get_db),
    category_id: int,
) -> Any:
    """
    Restore a previously deleted category.
    """
    category = crud.category.get(db, id=category_id)
    if not category:
        raise HTTPException(
            status_code=404,
            detail="Category not found",
        )
    if category.deleted_at is None:
        raise HTTPException(
            status_code=400,
            detail="Category is not deleted",
        )
    return crud.category.restore(db, id=category_id) 