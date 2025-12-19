from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

# Configuration for Database
# Using SQLite for local development/safety as requested
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

# Create Engine
# connect_args={"check_same_thread": False} is required for SQLite
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    session = SessionLocal()
    try:
        yield session
        session.commit()
    finally:
        session.close()