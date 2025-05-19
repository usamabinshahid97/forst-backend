from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field

# Shared properties
class SaleBase(BaseModel):
    product_id: int
    quantity: int = Field(..., gt=0)
    unit_price: float = Field(..., gt=0)
    total_price: float = Field(..., gt=0)
    platform: str
    order_id: str

# Properties to receive on sale creation
class SaleCreate(SaleBase):
    sale_date: Optional[datetime] = None

# Properties to receive on sale update
class SaleUpdate(BaseModel):
    quantity: Optional[int] = None
    unit_price: Optional[float] = None
    total_price: Optional[float] = None
    sale_date: Optional[datetime] = None
    platform: Optional[str] = None
    order_id: Optional[str] = None

# Properties shared by models stored in DB
class SaleInDBBase(SaleBase):
    id: int
    sale_date: datetime

    class Config:
        from_attributes = True

# Properties to return to client
class Sale(SaleInDBBase):
    pass

# Additional schemas for platform-specific sales data
class SaleByPlatform(BaseModel):
    platform: str
    sales_count: int
    total_revenue: float

# Additional schemas for reporting
class SaleSummary(BaseModel):
    total_sales: int
    total_revenue: float
    average_order_value: float
    total_units_sold: int
    sales_by_platform: List[SaleByPlatform]

class SaleByPeriod(BaseModel):
    period: str  # e.g. '2023-01', '2023-W01', '2023-01-01'
    sales_count: int
    total_revenue: float 