from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import OperationalError
from src.config import settings
import logging

logger = logging.getLogger(__name__)

DATABASE_URL = settings.DATABASE_URL  # Database URL

try:
    engine = create_engine(DATABASE_URL)
    
    # Test the connection
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        logger.info(f"Database connection successful: {result.scalar()}")

except OperationalError as e:
    logger.error(f"Database connection failed: {e}")
    raise  # Re-raise the exception to halt execution

except Exception as e:
    logger.error(f"An unexpected error occurred: {e}")
    raise  # Re-raise the exception to halt execution

SessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine, class_=Session
)

def get_db() -> Session:
    """
    Creates a database session and yields it.

    This function is a dependency for FastAPI endpoints. It creates a new database session for each request,
    yields it to be used in the endpoint, and closes the session after the request is processed.

    """
    db = SessionLocal()
    try:
        db.execute(text("SELECT 1"))
        yield db
    except Exception as e:
        logger.error(f"Database error: {e}")
        raise
    finally:        
        db.close()