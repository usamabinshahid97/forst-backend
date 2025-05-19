from typing import List, Optional
from sqlalchemy.orm import Session
import datetime
from sqlalchemy import func

from app.crud.base import CRUDBase
from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryUpdate

class CRUDCategory(CRUDBase[Category, CategoryCreate, CategoryUpdate]):
    def get_by_name(self, db: Session, *, name: str) -> Optional[Category]:
        return db.query(Category).filter(Category.name == name, Category.deleted_at == None).first()
    
    def get_multi(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[Category]:
        """Only return non-deleted categories"""
        return db.query(self.model).filter(self.model.deleted_at == None).offset(skip).limit(limit).all()
    
    def remove(self, db: Session, *, id: int) -> Category:
        """Soft delete a category by setting deleted_at timestamp without updating updated_at"""
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
    
    def get_deleted(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[Category]:
        """Get all deleted categories"""
        return db.query(self.model).filter(self.model.deleted_at != None).offset(skip).limit(limit).all()
    
    def restore(self, db: Session, *, id: int) -> Category:
        """Restore a soft-deleted category"""
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
    
    def get(self, db: Session, id: any) -> Optional[Category]:
        """Override the base get method to include deleted flag"""
        return db.query(self.model).filter(self.model.id == id).first()

category = CRUDCategory(Category) 