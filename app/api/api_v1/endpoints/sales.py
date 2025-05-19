from typing import Any, List, Optional
from datetime import datetime, date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app import crud, schemas
from app.db.session import get_db

router = APIRouter()

@router.get("/", response_model=List[schemas.Sale])
def read_sales(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    product_id: Optional[int] = None,
    platform: Optional[str] = None,
) -> Any:
    """
    Retrieve sales with optional filtering.
    """
    if start_date and end_date:
        # Convert date to datetime
        start_datetime = datetime.combine(start_date, datetime.min.time())
        end_datetime = datetime.combine(end_date, datetime.max.time())
        return crud.sale.get_by_date_range(db, start_date=start_datetime, end_date=end_datetime, skip=skip, limit=limit)
    elif product_id:
        return crud.sale.get_by_product(db, product_id=product_id, skip=skip, limit=limit)
    elif platform:
        return crud.sale.get_by_platform(db, platform=platform, skip=skip, limit=limit)
    else:
        return crud.sale.get_multi(db, skip=skip, limit=limit)

@router.get("/product/{product_id}", response_model=List[schemas.Sale])
def get_sales_by_product(
    *,
    db: Session = Depends(get_db),
    product_id: int,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Get sales for a specific product.
    """
    # Check if product exists
    product = crud.product.get(db, id=product_id)
    if not product:
        raise HTTPException(
            status_code=404,
            detail=f"Product with ID {product_id} not found",
        )
    
    sales = crud.sale.get_by_product(db, product_id=product_id, skip=skip, limit=limit)
    return sales

@router.get("/date-range/", response_model=List[schemas.Sale])
def get_sales_by_date_range(
    *,
    db: Session = Depends(get_db),
    start_date: date = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: date = Query(..., description="End date (YYYY-MM-DD)"),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Get sales within a specific date range.
    """
    # Convert date to datetime
    start_datetime = datetime.combine(start_date, datetime.min.time())
    end_datetime = datetime.combine(end_date, datetime.max.time())
    
    sales = crud.sale.get_by_date_range(db, start_date=start_datetime, end_date=end_datetime, skip=skip, limit=limit)
    return sales

@router.post("/", response_model=schemas.Sale)
def create_sale(
    *,
    db: Session = Depends(get_db),
    sale_in: schemas.SaleCreate,
) -> Any:
    """
    Create new sale record and update inventory.
    """
    # Check if product exists
    product = crud.product.get(db, id=sale_in.product_id)
    if not product:
        raise HTTPException(
            status_code=400,
            detail=f"Product with ID {sale_in.product_id} does not exist.",
        )
    
    # Check if product is deleted
    if product.deleted_at is not None:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot create sale for deleted product (ID: {sale_in.product_id}).",
        )
    
    # Check if inventory exists and has sufficient stock
    inventory = crud.inventory.get_by_product_id(db, product_id=sale_in.product_id)
    if not inventory:
        raise HTTPException(
            status_code=400,
            detail=f"No inventory found for product with ID {sale_in.product_id}.",
        )
    
    if inventory.quantity < sale_in.quantity:
        raise HTTPException(
            status_code=400,
            detail=f"Insufficient stock. Available: {inventory.quantity}, Requested: {sale_in.quantity}",
        )
    
    # Create sale record and update inventory
    return crud.sale.create_with_product(db, obj_in=sale_in)

@router.get("/summary/", response_model=schemas.SaleSummary)
def get_sales_summary(
    db: Session = Depends(get_db),
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
) -> Any:
    """
    Get summary of sales data.
    """
    # Convert date to datetime if provided
    start_datetime = datetime.combine(start_date, datetime.min.time()) if start_date else None
    end_datetime = datetime.combine(end_date, datetime.max.time()) if end_date else None
    
    # Get the main summary data
    summary = crud.sale.get_sales_summary(db, start_date=start_datetime, end_date=end_datetime)
    
    # Add sales by platform data
    platforms_data = crud.sale.get_sales_by_platform(db, start_date=start_datetime, end_date=end_datetime)
    summary["sales_by_platform"] = platforms_data
    
    return summary

@router.get("/by-period/", response_model=List[schemas.SaleByPeriod])
def get_sales_by_period(
    db: Session = Depends(get_db),
    period_type: str = Query(..., description="Period type: 'day', 'week', 'month', or 'year'"),
    start_date: date = Query(..., description="Start date"),
    end_date: date = Query(..., description="End date"),
) -> Any:
    """
    Get sales aggregated by specified time period.
    """
    if period_type not in ['day', 'week', 'month', 'year']:
        raise HTTPException(
            status_code=400,
            detail="period_type must be one of: 'day', 'week', 'month', 'year'",
        )
    
    # Convert date to datetime
    start_datetime = datetime.combine(start_date, datetime.min.time())
    end_datetime = datetime.combine(end_date, datetime.max.time())
    
    return crud.sale.get_sales_by_period(
        db, period_type=period_type, start_date=start_datetime, end_date=end_datetime
    )

@router.get("/by-category/")
def get_sales_by_category(
    db: Session = Depends(get_db),
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
) -> Any:
    """
    Get sales aggregated by product category.
    """
    # Convert date to datetime if provided
    start_datetime = datetime.combine(start_date, datetime.min.time()) if start_date else None
    end_datetime = datetime.combine(end_date, datetime.max.time()) if end_date else None
    
    return crud.sale.get_sales_by_category(db, start_date=start_datetime, end_date=end_datetime)

@router.get("/by-platform/")
def get_sales_by_platform(
    db: Session = Depends(get_db),
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
) -> Any:
    """
    Get sales aggregated by platform.
    """
    # Convert date to datetime if provided
    start_datetime = datetime.combine(start_date, datetime.min.time()) if start_date else None
    end_datetime = datetime.combine(end_date, datetime.max.time()) if end_date else None
    
    return crud.sale.get_sales_by_platform(db, start_date=start_datetime, end_date=end_datetime)

@router.get("/compare-periods/")
def compare_periods(
    db: Session = Depends(get_db),
    period1_start: date = Query(..., description="Period 1 start date"),
    period1_end: date = Query(..., description="Period 1 end date"),
    period2_start: date = Query(..., description="Period 2 start date"),
    period2_end: date = Query(..., description="Period 2 end date"),
) -> Any:
    """
    Compare sales between two time periods.
    """
    # Convert dates to datetimes
    period1_start_datetime = datetime.combine(period1_start, datetime.min.time())
    period1_end_datetime = datetime.combine(period1_end, datetime.max.time())
    period2_start_datetime = datetime.combine(period2_start, datetime.min.time())
    period2_end_datetime = datetime.combine(period2_end, datetime.max.time())
    
    return crud.sale.compare_periods(
        db,
        period1_start=period1_start_datetime,
        period1_end=period1_end_datetime,
        period2_start=period2_start_datetime,
        period2_end=period2_end_datetime
    ) 