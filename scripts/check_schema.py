import sys
from pathlib import Path

# Add the parent directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import inspect, MetaData, Table
from app.db.session import engine

def check_schema():
    """Check the database schema."""
    inspector = inspect(engine)
    
    # Get all tables
    tables = inspector.get_table_names()
    print(f"Tables in database: {tables}")
    
    if 'product' in tables:
        # Reflect the database metadata
        metadata = MetaData()
        metadata.reflect(bind=engine)
        
        # Get the product table
        product_table = metadata.tables['product']
        
        print("\nProduct table columns:")
        for col in product_table.columns:
            print(f"- {col.name}: {col.type}")
        
        # Specifically check for deleted_at column
        if any(col.name == 'deleted_at' for col in product_table.columns):
            print("\n✅ deleted_at column exists in the product table!")
        else:
            print("\n❌ deleted_at column does not exist in the product table.")

if __name__ == "__main__":
    check_schema() 