# E-commerce Admin API

A FastAPI-based backend for an e-commerce admin dashboard, providing tools for inventory management, sales tracking, and detailed analytics.

## Features

- **Product Management**: CRUD operations for products with soft deletion
- **Category Management**: Organize products into categories
- **Inventory Management**: Track stock levels with low-stock alerts
- **Sales Analytics**: 
  - Track sales by time period, category, or platform
  - Compare sales between different time periods
  - Generate sales summaries with key metrics

## Setup Instructions

### Prerequisites

- Python 3.8+
- MySQL Server

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/e-commerce-admin-api.git
   cd e-commerce-admin-api
   ```

2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a MySQL database:
   ```sql
   CREATE DATABASE ecommerce_admin;
   ```

5. Update the database connection string in `.env` or `app/core/config.py`:
   ```
   DATABASE_URL=mysql+pymysql://username:password@localhost/ecommerce_admin
   ```

6. Run database migrations:
   ```bash
   alembic upgrade head
   ```

7. Start the application:
   ```bash
   uvicorn app.main:app --reload
   ```

8. Open the Swagger documentation at [http://localhost:8000/docs](http://localhost:8000/docs)

### Dependencies

The application requires the following main dependencies:

- **FastAPI**: Web framework
- **SQLAlchemy**: ORM for database operations
- **Pydantic**: Data validation and settings management
- **PyMySQL**: MySQL database connector
- **Alembic**: Database migration tool
- **Pytest**: Testing framework

All dependencies are listed in `requirements.txt`.

## API Endpoints

### Categories

- `GET /api/v1/categories/`: Get all categories
- `POST /api/v1/categories/`: Create a new category
- `GET /api/v1/categories/{category_id}`: Get a specific category
- `PUT /api/v1/categories/{category_id}`: Update a category
- `DELETE /api/v1/categories/{category_id}`: Soft delete a category
- `GET /api/v1/categories/deleted/`: List all deleted categories
- `PUT /api/v1/categories/restore/{category_id}`: Restore a deleted category

### Products

- `GET /api/v1/products/`: Get all products
- `POST /api/v1/products/`: Create a new product
- `GET /api/v1/products/{product_id}`: Get a specific product
- `PUT /api/v1/products/{product_id}`: Update a product
- `DELETE /api/v1/products/{product_id}`: Soft delete a product
- `GET /api/v1/products/deleted/`: List all deleted products
- `PUT /api/v1/products/restore/{product_id}`: Restore a deleted product
- `GET /api/v1/products/with-inventory/`: Get products with inventory information
- `GET /api/v1/products/category/{category_id}`: Get products by category
- `GET /api/v1/products/search/`: Search products by name

### Inventory

- `GET /api/v1/inventory/`: Get all inventory items
- `GET /api/v1/inventory/low-stock/`: Get low stock inventory items
- `POST /api/v1/inventory/`: Create a new inventory item
- `GET /api/v1/inventory/{inventory_id}`: Get a specific inventory item
- `GET /api/v1/inventory/product/{product_id}`: Get inventory for a specific product
- `PUT /api/v1/inventory/{inventory_id}`: Update an inventory item
- `POST /api/v1/inventory/{inventory_id}/restock`: Restock an inventory item
- `PUT /api/v1/inventory/product/{product_id}/restock`: Restock a product by product ID

### Sales

- `GET /api/v1/sales/`: Get all sales with optional filtering
- `POST /api/v1/sales/`: Create a new sale
- `GET /api/v1/sales/product/{product_id}`: Get sales for a specific product
- `GET /api/v1/sales/date-range/`: Get sales within a date range
- `GET /api/v1/sales/summary/`: Get sales summary with platforms breakdown
- `GET /api/v1/sales/by-period/`: Get sales aggregated by period (day, week, month, year)
- `GET /api/v1/sales/by-category/`: Get sales aggregated by category
- `GET /api/v1/sales/by-platform/`: Get sales aggregated by platform
- `GET /api/v1/sales/compare-periods/`: Compare sales between two periods

## Soft Deletion Implementation

Both products and categories in the system can be "soft deleted" rather than permanently removed from the database. This provides several benefits:

- Preserves historical data for sales and analytics
- Allows products and categories to be restored if needed
- Prevents accidental data loss
- Maintains referential integrity between related entities

### How Soft Deletion Works

#### For Products:
When a product is deleted:
1. The `deleted_at` timestamp is set to the current time
2. The product no longer appears in standard product listings
3. Inventory operations cannot be performed on deleted products
4. New sales cannot be created for deleted products
5. Deleted products are excluded from sales analytics

#### For Categories:
When a category is deleted:
1. The `deleted_at` timestamp is set to the current time
2. The category no longer appears in standard category listings
3. Products cannot be created in or moved to deleted categories
4. Categories with active (non-deleted) products cannot be deleted

## Testing

Run the tests with pytest:

```bash
pytest
```

Or run specific test files:

```bash
pytest tests/api/api_v1/test_endpoints/test_categories.py
pytest tests/api/api_v1/test_endpoints/test_products.py
pytest tests/api/api_v1/test_endpoints/test_inventory.py
pytest tests/api/api_v1/test_endpoints/test_sales.py
```

Tests are available for all API functionality, including specific tests for soft deletion behavior.

## Database Schema

### Models

#### Product
- `id`: Integer (Primary Key)
- `name`: String
- `description`: String
- `sku`: String (Unique)
- `price`: Float
- `category_id`: Integer (Foreign Key)
- `created_at`: DateTime
- `updated_at`: DateTime
- `deleted_at`: DateTime (Nullable, used for soft deletion)

#### Category
- `id`: Integer (Primary Key)
- `name`: String
- `description`: String
- `created_at`: DateTime
- `updated_at`: DateTime
- `deleted_at`: DateTime (Nullable, used for soft deletion)

#### Inventory
- `id`: Integer (Primary Key)
- `product_id`: Integer (Foreign Key)
- `quantity`: Integer
- `low_stock_threshold`: Integer
- `last_restock_date`: DateTime
- `updated_at`: DateTime

#### Sale
- `id`: Integer (Primary Key)
- `product_id`: Integer (Foreign Key)
- `quantity`: Integer
- `unit_price`: Float
- `total_price`: Float
- `platform`: String
- `order_id`: String
- `sale_date`: DateTime

### Relationships
- A **Category** can have multiple **Products**
- A **Product** has one **Inventory** record
- A **Product** can have multiple **Sale** records

## License

MIT 