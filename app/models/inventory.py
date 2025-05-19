from sqlalchemy import Column, Integer, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql.functions import current_timestamp

from app.db.base_class import Base

class Inventory(Base):
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("product.id"), nullable=False, unique=True)
    quantity = Column(Integer, nullable=False, default=0)
    low_stock_threshold = Column(Integer, nullable=False, default=10)
    last_restock_date = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, default=current_timestamp(), onupdate=current_timestamp())
    
    # Relationships
    product = relationship("Product", back_populates="inventory")
    
    @property
    def is_low_stock(self) -> Boolean:
        """Check if the product is low on stock."""
        return self.quantity <= self.low_stock_threshold 