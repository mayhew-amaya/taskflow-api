#SQLAlchemy imports for database setup
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base


# BASE_DIR points to backend/app no matter where you run the server from
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "taskflow.db")

# SQL CONNECTION STRING sqlite:////absolute/path  (four slashes after sqlite:)
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH}"

#Engine = the core interface to the database
#check_same_thread=False is required for SQLite with FastAPI
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}  # needed for SQLite + FastAPI
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
#Base is the class all db models will inherit from
