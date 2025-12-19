from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import urllib.parse
import os

# Configuration for SQL Server
# Read from Environment Variables with defaults
# Prioritize DB_SERVER as used in user's docker-compose, fallback to DB_HOST
SERVER = os.getenv("DB_SERVER", os.getenv("DB_HOST", "localhost"))
DATABASE = os.getenv("DB_NAME", "MyDatabase")
USERNAME = os.getenv("DB_USER", "sa")
PASSWORD = os.getenv("DB_PASSWORD", "YourStrongPassword123")
DRIVER = os.getenv("DB_DRIVER", "ODBC Driver 17 for SQL Server")

print(f"--- Database Connection Config ---")
print(f"Server: {SERVER}")
print(f"Database: {DATABASE}")
print(f"User: {USERNAME}")
print(f"----------------------------------")

# Create connection string
params = urllib.parse.quote_plus(
    f'DRIVER={{{DRIVER}}};SERVER={SERVER};DATABASE={DATABASE};UID={USERNAME};PWD={PASSWORD}'
)
SQLALCHEMY_DATABASE_URL = f"mssql+pyodbc:///?odbc_connect={params}"

# Create Engine
# pool_pre_ping=True is recommended for SQL Server to handle connection drops gracefully.
engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    session = SessionLocal()
    try:
        yield session
        session.commit()
    finally:
        session.close()