from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql.functions import current_timestamp

from app.db.base_class import Base

class Product(Base):
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), index=True, nullable=False)
    description = Column(String(500), nullable=True)
    sku = Column(String(50), unique=True, index=True, nullable=False)
    price = Column(Float, nullable=False)
    category_id = Column(Integer, ForeignKey("category.id"), nullable=False)
    created_at = Column(DateTime, default=current_timestamp())
    updated_at = Column(DateTime, default=current_timestamp(), onupdate=current_timestamp())
    deleted_at = Column(DateTime, nullable=True)
    
    # Relationships
    category = relationship("Category", back_populates="products")
    inventory = relationship("Inventory", back_populates="product", uselist=False)
    sales = relationship("Sale", back_populates="product") 