"""
Database Connection Management
Handles database initilization and session management
"""
from sqlalchemy import Engine, create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from contextlib import contextmanager
from app.config import settings
import logging

logger = logging.getLogger(__name__)

engine_kwargs = {
    "echo": settings.DEBUG,
    "pool_pre_ping": True,
}

if "sqlite" in settings.DATABASE_URL:
    engine_kwargs.update({
        "connect_args": {"check_same_thread": False},
        "poolclass": StaticPool,
    })

elif "postgresql" in settings.DATABASE_URL:
    engine_kwargs.update({
        "pool_size": 5,
        "max_overflow": 10,
        "pool_timeout": 30,
        "pool_recycle": 3600,
    })

else: logger.warning(f"Using default database configuration for: {settings.DATABASE_URL.split('://')[0]}")

engine = create_engine(settings.DATABASE_URL, **engine_kwargs)

if "sqlite" in settings.DATABASE_URL:
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_conn, connection_record):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


@contextmanager
def get_db():
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Database error: {e}")
        raise
    finally:
        db.close()

def get_db_dependency():
    """
    FastAPI dependency for database sessions

    Usage:
        @app.get("/users")
        def get_users(db: Session = Depends(get_db_dependency)):
            return db.query(User).all()
    """

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """
    Initialize database - create all tables
    Should be called on application startup
    """

    from app.database.models import Base
    try:
        Base.metadata.create_all(bind=engine)

        db_type = "SQLite" if "sqlite" in settings.DATABASE_URL else "PostgreSQL"
        logger.info(f"✅ Database initialized successfully ({db_type})")

        table_names = Base.metadata.tables.keys()
        logger.info(f" Create {len(table_names)} tables: { ', '.join(table_names)}")

        return True
    except Exception as e:
        logger.error(f" Database initialization failed: {e}")
        raise

def drop_all_tables():
    """
    Drop all tabels - Use with caution!
    only for development/testing
    """

    if settings.is_production:
        raise RuntimeError("Cannot drop tables in production!")
    
    from app.database.models import Base

    Base.metadata.drop_all(bind=engine)
    logger.warning("⚠️ Alltalbes dropped!")

def reset_database():
    """
    Reset database - drop and recreate all tables
    Only for development/testing
    """

    if settings.is_production:
        raise RuntimeError("Cannot reset database in produciton!")
    drop_all_tables()

    init_db()
    logger.info("🔄 Database reset complete!")


def check_database_connection() -> bool:
    """
    Check if database is accessible
    Returns True if connection successful, False otherwise
    """

    try: 
        with get_db() as db:
            db.execute("SELECT 1")

        return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False
    
def get_database_info() -> dict:
    """
    Get database information
    """

    from app.database.models import Base

    return {
        "type": settings.database_type,
        "url": settings.DATABASE_URL.split("@")[-1] if "@" in settings.DATABASE_URL else "local",
        "tables": list(Base.metadata.tables.keys()),
        "table_count": len(Base.metadata.tables),
        "connected": check_database_connection()
    }


def get_table_counts() -> dict:
    """
    Get row counts for all tables
    """

    from app.database.models import (
        ContactMessage, ChatSession, ChatQuery,
        EmailGeneration, Visitor, ProjectView, ApiUsage
    )

    counts = {}
    with get_db() as db:
        counts['contact_messages'] = db.query(ContactMessage).count()
        counts['chat_sessions'] = db.query(ChatSession).count()
        counts['chat_queries'] = db.query(ChatQuery).count()
        counts['email_generations'] = db.query(EmailGeneration).count()
        counts['visitors'] = db.query(Visitor).count()
        counts['project_views'] = db.query(ProjectView).count()
        counts['api_usage'] = db.query(ApiUsage).count()
        counts['total'] = sum(counts.values())

    return counts

__all__ = [
    'engine',
    'SessionLocal',
    'get_db',
    'get_db_dependency',
    'init_db',
    'drop_all_tables',
    'reset_database',
    'check_database_connection',
    'get_database_info',
    'get_table_counts'
]