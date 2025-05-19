from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
from sqlalchemy import func, extract
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.sale import Sale
from app.schemas.sale import SaleCreate, SaleUpdate

class CRUDSale(CRUDBase[Sale, SaleCreate, SaleUpdate]):
    def create_with_product(self, db: Session, *, obj_in: SaleCreate) -> Sale:
        """Create a sale record and update inventory."""
        # Create the sale
        sale = self.create(db, obj_in=obj_in)
        
        # Update inventory (in a real app, this would be handled by a transaction)
        from app.crud.crud_inventory import inventory
        inventory.update_stock(db, product_id=obj_in.product_id, quantity_change=-obj_in.quantity)
        
        return sale
    
    def get_by_date_range(
        self, db: Session, *, start_date: datetime, end_date: datetime, skip: int = 0, limit: int = 100
    ) -> List[Sale]:
        """Get sales between start_date and end_date."""
        from app.models.product import Product
        
        return db.query(Sale).join(
            Product, Sale.product_id == Product.id
        ).filter(
            Sale.sale_date >= start_date,
            Sale.sale_date <= end_date,
            Product.deleted_at == None
        ).order_by(Sale.sale_date.desc()).offset(skip).limit(limit).all()
    
    def get_by_product(
        self, db: Session, *, product_id: int, skip: int = 0, limit: int = 100
    ) -> List[Sale]:
        """Get sales for a specific product."""
        from app.models.product import Product
        
        return db.query(Sale).join(
            Product, Sale.product_id == Product.id
        ).filter(
            Sale.product_id == product_id,
            Product.deleted_at == None
        ).order_by(Sale.sale_date.desc()).offset(skip).limit(limit).all()
    
    def get_by_platform(
        self, db: Session, *, platform: str, skip: int = 0, limit: int = 100
    ) -> List[Sale]:
        """Get sales for a specific platform."""
        from app.models.product import Product
        
        return db.query(Sale).join(
            Product, Sale.product_id == Product.id
        ).filter(
            Sale.platform == platform,
            Product.deleted_at == None
        ).order_by(Sale.sale_date.desc()).offset(skip).limit(limit).all()
    
    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[Sale]:
        """Get all sales for non-deleted products."""
        from app.models.product import Product
        
        return db.query(Sale).join(
            Product, Sale.product_id == Product.id
        ).filter(
            Product.deleted_at == None
        ).order_by(Sale.sale_date.desc()).offset(skip).limit(limit).all()
    
    def get_sales_summary(
        self, db: Session, *, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get summary of sales including total count, revenue, average order value, and total units sold."""
        from app.models.product import Product
        
        query = db.query(
            func.count(Sale.id).label("total_sales"),
            func.sum(Sale.total_price).label("total_revenue"),
            func.avg(Sale.total_price).label("average_order_value"),
            func.sum(Sale.quantity).label("total_units_sold")
        ).join(
            Product, Sale.product_id == Product.id
        ).filter(
            Product.deleted_at == None
        )
        
        if start_date:
            query = query.filter(Sale.sale_date >= start_date)
        if end_date:
            query = query.filter(Sale.sale_date <= end_date)
            
        result = query.first()
        return {
            "total_sales": result.total_sales if result.total_sales else 0,
            "total_revenue": float(result.total_revenue) if result.total_revenue else 0.0,
            "average_order_value": float(result.average_order_value) if result.average_order_value else 0.0,
            "total_units_sold": result.total_units_sold if result.total_units_sold else 0
        }
    
    def get_sales_by_period(
        self, db: Session, *, period_type: str, start_date: datetime, end_date: datetime
    ) -> List[Dict[str, Any]]:
        """
        Get sales aggregated by time period.
        period_type can be 'day', 'week', 'month', or 'year'
        """
        from app.models.product import Product
        
        if period_type == 'day':
            # Daily sales
            date_format = func.date_format(Sale.sale_date, '%Y-%m-%d')
        elif period_type == 'week':
            # Weekly sales
            date_format = func.concat(func.year(Sale.sale_date), '-W', func.week(Sale.sale_date))
        elif period_type == 'month':
            # Monthly sales
            date_format = func.date_format(Sale.sale_date, '%Y-%m')
        elif period_type == 'year':
            # Yearly sales
            date_format = func.date_format(Sale.sale_date, '%Y')
        else:
            raise ValueError("period_type must be one of: 'day', 'week', 'month', 'year'")
        
        results = db.query(
            date_format.label("period"),
            func.count(Sale.id).label("sales_count"),
            func.sum(Sale.total_price).label("total_revenue")
        ).join(
            Product, Sale.product_id == Product.id
        ).filter(
            Sale.sale_date >= start_date,
            Sale.sale_date <= end_date,
            Product.deleted_at == None
        ).group_by("period").order_by("period").all()
        
        return [
            {
                "period": str(r.period),
                "sales_count": r.sales_count,
                "total_revenue": float(r.total_revenue)
            }
            for r in results
        ]
    
    def get_sales_by_category(
        self, db: Session, *, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """Get sales aggregated by product category."""
        from app.models.product import Product
        from app.models.category import Category
        
        query = db.query(
            Category.name.label("category_name"),
            func.count(Sale.id).label("sales_count"),
            func.sum(Sale.total_price).label("total_revenue")
        ).join(
            Product, Sale.product_id == Product.id
        ).join(
            Category, Product.category_id == Category.id
        ).filter(
            Product.deleted_at == None
        )
        
        if start_date:
            query = query.filter(Sale.sale_date >= start_date)
        if end_date:
            query = query.filter(Sale.sale_date <= end_date)
            
        results = query.group_by(Category.name).order_by(func.sum(Sale.total_price).desc()).all()
        
        return [
            {
                "category_name": r.category_name,
                "sales_count": r.sales_count,
                "total_revenue": float(r.total_revenue)
            }
            for r in results
        ]
    
    def get_sales_by_platform(
        self, db: Session, *, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """Get sales aggregated by platform."""
        from app.models.product import Product
        
        query = db.query(
            Sale.platform,
            func.count(Sale.id).label("sales_count"),
            func.sum(Sale.total_price).label("total_revenue")
        ).join(
            Product, Sale.product_id == Product.id
        ).filter(
            Product.deleted_at == None
        )
        
        if start_date:
            query = query.filter(Sale.sale_date >= start_date)
        if end_date:
            query = query.filter(Sale.sale_date <= end_date)
            
        results = query.group_by(Sale.platform).order_by(func.sum(Sale.total_price).desc()).all()
        
        return [
            {
                "platform": r.platform,
                "sales_count": r.sales_count,
                "total_revenue": float(r.total_revenue)
            }
            for r in results
        ]
    
    def compare_periods(
        self, db: Session, *, 
        period1_start: datetime, period1_end: datetime,
        period2_start: datetime, period2_end: datetime
    ) -> Dict[str, Any]:
        """Compare sales between two time periods."""
        period1 = self.get_sales_summary(db, start_date=period1_start, end_date=period1_end)
        period2 = self.get_sales_summary(db, start_date=period2_start, end_date=period2_end)
        
        # Calculate changes
        sales_change = period2["total_sales"] - period1["total_sales"]
        sales_change_pct = (sales_change / period1["total_sales"] * 100) if period1["total_sales"] > 0 else None
        
        revenue_change = period2["total_revenue"] - period1["total_revenue"]
        revenue_change_pct = (revenue_change / period1["total_revenue"] * 100) if period1["total_revenue"] > 0 else None
        
        aov_change = period2["average_order_value"] - period1["average_order_value"]
        aov_change_pct = (aov_change / period1["average_order_value"] * 100) if period1["average_order_value"] > 0 else None
        
        return {
            "period1": {
                "start_date": period1_start.isoformat(),
                "end_date": period1_end.isoformat(),
                "total_sales": period1["total_sales"],
                "total_revenue": period1["total_revenue"],
                "average_order_value": period1["average_order_value"]
            },
            "period2": {
                "start_date": period2_start.isoformat(),
                "end_date": period2_end.isoformat(),
                "total_sales": period2["total_sales"],
                "total_revenue": period2["total_revenue"],
                "average_order_value": period2["average_order_value"]
            },
            "changes": {
                "sales_change": {
                    "absolute": sales_change,
                    "percentage": sales_change_pct
                },
                "revenue_change": {
                    "absolute": revenue_change,
                    "percentage": revenue_change_pct
                },
                "aov_change": {
                    "absolute": aov_change,
                    "percentage": aov_change_pct
                }
            }
        }

sale = CRUDSale(Sale) 