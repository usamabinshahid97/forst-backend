from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine.url import make_url

from app.core.config import settings

# Add connection timeout settings to help with lock issues during tests
url = make_url(settings.DATABASE_URL)
engine = create_engine(
    url,
    pool_recycle=3600,
    pool_pre_ping=True,
    connect_args={
        "connect_timeout": 60,  # Connection timeout in seconds
    }
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 