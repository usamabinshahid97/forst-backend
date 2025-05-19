from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field

# Shared properties
class InventoryBase(BaseModel):
    product_id: int
    quantity: int = Field(..., ge=0)
    low_stock_threshold: int = Field(..., ge=1)

# Properties to receive on inventory creation
class InventoryCreate(InventoryBase):
    pass

# Properties to receive on inventory update
class InventoryUpdate(BaseModel):
    quantity: Optional[int] = None
    low_stock_threshold: Optional[int] = None
    last_restock_date: Optional[datetime] = None

# Properties for inventory restock
class InventoryRestock(BaseModel):
    quantity: int = Field(..., gt=0, description="Quantity to add to inventory (must be positive)")

# Properties shared by models stored in DB
class InventoryInDBBase(InventoryBase):
    id: int
    last_restock_date: Optional[datetime] = None
    updated_at: datetime

    class Config:
        from_attributes = True

# Properties to return to client
class Inventory(InventoryInDBBase):
    is_low_stock: bool 