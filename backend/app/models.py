#SQLAlchemy column and type imports
from sqlalchemy import Column, String, Date

#Base comes from database.py
from app.database import Base

#Task Table Defintion
class Task(Base):
    __tablename__ = "task" #table name in SQLite

    id = Column(String, primary_key=True, index=True)
    title = Column(String, nullable=False)
    due_date = Column(Date, nullable=True)
    status = Column(String, default="pending")

    #Defines the database table - Each attribute = a column - This replaces TASKS = []