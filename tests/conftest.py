import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.db.session import get_db, SessionLocal, engine
from sqlalchemy.exc import OperationalError, IntegrityError

# It's generally better to import models at the top level if possible,
# but to be safe from potential circular imports with conftest, 
# models can be imported inside the fixture when needed.

@pytest.fixture(scope="function")
def db():
    # Import models here to ensure they are loaded when the fixture runs
    from app.models.product import Product 
    from app.models.category import Category
    from app.models.inventory import Inventory
    from app.models.sale import Sale

    db_session = SessionLocal()
    
    # Clear relevant tables before each test
    # Order matters due to foreign key constraints.
    # Delete from tables that depend on others first.
    try:
        # Delete in correct order to respect foreign key constraints
        # First level: child tables with no dependents
        db_session.query(Sale).delete(synchronize_session=False)
        db_session.commit()
        
        # Second level: tables that depend on product
        db_session.query(Inventory).delete(synchronize_session=False)
        db_session.commit()
        
        # Third level: Product table (depends on Category)
        db_session.query(Product).delete(synchronize_session=False)
        db_session.commit()
        
        # Fourth level: Category table (top level parent)
        db_session.query(Category).delete(synchronize_session=False)
        db_session.commit()
    except (IntegrityError, OperationalError) as e:
        # If there's an error during setup, rollback and close the session
        db_session.rollback()
        db_session.close()
        raise e

    try:
        yield db_session
    finally:
        db_session.rollback()  # Rollback any uncommitted changes from the test itself
        db_session.close()


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="function")
def client_with_db(db):
    def override_get_db():
        try:
            yield db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as c:
        yield c
    
    app.dependency_overrides = {} 