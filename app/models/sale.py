from sqlalchemy import Column, Integer, Float, ForeignKey, DateTime, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql.functions import current_timestamp

from app.db.base_class import Base

class Sale(Base):
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("product.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    total_price = Column(Float, nullable=False)
    sale_date = Column(DateTime, nullable=False, default=current_timestamp())
    platform = Column(String(50), nullable=False, index=True)  # Amazon, Walmart, etc.
    order_id = Column(String(100), nullable=False, index=True)
    
    # Relationships
    product = relationship("Product", back_populates="sales") 