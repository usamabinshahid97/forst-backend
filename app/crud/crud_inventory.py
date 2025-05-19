from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.inventory import Inventory
from app.schemas.inventory import InventoryCreate, InventoryUpdate

class CRUDInventory(CRUDBase[Inventory, InventoryCreate, InventoryUpdate]):
    def get_by_product_id(self, db: Session, *, product_id: int) -> Optional[Inventory]:
        return db.query(Inventory).filter(Inventory.product_id == product_id).first()
    
    def get_low_stock_items(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[Inventory]:
        """Get items that are below their low stock threshold."""
        return db.query(Inventory).filter(
            Inventory.quantity <= Inventory.low_stock_threshold
        ).offset(skip).limit(limit).all()
    
    def update_stock(self, db: Session, *, product_id: int, quantity_change: int, restock: bool = False) -> Inventory:
        """Update stock quantity for a product."""
        inventory = self.get_by_product_id(db, product_id=product_id)
        if not inventory:
            return None
        
        # Update the quantity
        inventory.quantity += quantity_change
        
        # If this is a restock, update the last_restock_date
        if restock and quantity_change > 0:
            inventory.last_restock_date = datetime.now()
            
        db.add(inventory)
        db.commit()
        db.refresh(inventory)
        return inventory

inventory = CRUDInventory(Inventory) 