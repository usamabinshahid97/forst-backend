from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field

# Shared properties
class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    sku: str
    price: float = Field(..., gt=0)
    category_id: int

# Properties to receive on product creation
class ProductCreate(ProductBase):
    pass

# Properties to receive on product update
class ProductUpdate(ProductBase):
    name: Optional[str] = None
    description: Optional[str] = None
    sku: Optional[str] = None
    price: Optional[float] = None
    category_id: Optional[int] = None

# Properties shared by models stored in DB
class ProductInDBBase(ProductBase):
    id: int
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    class Config:
        from_attributes = True

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None

# Properties to return to client
class Product(ProductInDBBase):
    pass

# Properties to return with inventory information
class ProductWithInventory(Product):
    inventory_quantity: int
    low_stock_threshold: int
    is_low_stock: bool 