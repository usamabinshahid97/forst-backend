from typing import List, Optional
from sqlalchemy.orm import Session
import datetime
from sqlalchemy import func

from app.crud.base import CRUDBase
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate
from app.models.category import Category

class CRUDProduct(CRUDBase[Product, ProductCreate, ProductUpdate]):
    def get_by_sku(self, db: Session, *, sku: str) -> Optional[Product]:
        return db.query(Product).filter(Product.sku == sku, Product.deleted_at == None).first()
    
    def get_by_category(self, db: Session, *, category_id: int, skip: int = 0, limit: int = 100) -> List[Product]:
        return db.query(Product).join(
            Category, Product.category_id == Category.id
        ).filter(
            Product.category_id == category_id,
            Product.deleted_at == None,
            Category.deleted_at == None
        ).offset(skip).limit(limit).all()
    
    def search_products(self, db: Session, *, query: str, skip: int = 0, limit: int = 100) -> List[Product]:
        return db.query(Product).filter(
            Product.name.ilike(f"%{query}%"),
            Product.deleted_at == None
        ).offset(skip).limit(limit).all()

    def remove(self, db: Session, *, id: int) -> Product:
        """Soft delete a product by setting deleted_at timestamp without updating updated_at"""
        # First get the current object to preserve the updated_at value
        obj = db.query(self.model).get(id)
        if not obj:
            return None
            
        # Get the current updated_at value to preserve it
        current_updated_at = obj.updated_at
        
        # Set deleted_at while preserving the current updated_at
        now = datetime.datetime.now()
        db.query(self.model).filter(self.model.id == id).update(
            {
                "deleted_at": now,
                "updated_at": current_updated_at  # Explicitly preserve the current updated_at
            },
            synchronize_session=False
        )
        db.commit()
        
        # Get the updated object
        obj = db.query(self.model).get(id)
        return obj

    def get_multi(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[Product]:
        """Only return non-deleted products"""
        return db.query(self.model).filter(self.model.deleted_at == None).offset(skip).limit(limit).all()
    
    def restore(self, db: Session, *, id: int) -> Product:
        """Restore a soft-deleted product"""
        # First get the current object to preserve the updated_at value
        obj = db.query(self.model).get(id)
        if not obj:
            return None
            
        # Get the current updated_at value to preserve it
        current_updated_at = obj.updated_at
        
        # Clear deleted_at while preserving the current updated_at
        db.query(self.model).filter(self.model.id == id).update(
            {
                "deleted_at": None,
                "updated_at": current_updated_at  # Explicitly preserve the current updated_at
            },
            synchronize_session=False
        )
        db.commit()
        
        # Get the updated object
        obj = db.query(self.model).get(id)
        return obj
    
    def get_deleted(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[Product]:
        """Get all deleted products"""
        return db.query(self.model).filter(self.model.deleted_at != None).offset(skip).limit(limit).all()
    
    def get(self, db: Session, id: any) -> Optional[Product]:
        """Override the base get method to include deleted flag"""
        return db.query(self.model).filter(self.model.id == id).first()

product = CRUDProduct(Product) 