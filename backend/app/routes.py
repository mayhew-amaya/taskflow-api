"""
routes.py

This file defines the API routes for the TaskFlow service.
It contains:
- Data models (what a Task looks like)
- API endpoints (how clients interact with Tasks)
- Temporary in-memory storage (will later be replaced by a database)
"""

from fastapi import HTTPException, Depends # add to imports at top (used for 404 errors)
#prevents invalid dates, API accepts a due date, automatically converts object. 
from datetime import date
#List used to store multiple Task Objects(Task List)
#Optional allows a value to be present OR None (due_date may be missing)
from typing import List, Optional
#uuid4 generates a universally unique Identifier, We use this to assign each task a unique ID 
from uuid import uuid4
#APIRouter lets us group API endpoints together
#This keeps routes separates from main.py and makes the app scalable
from fastapi import APIRouter
#BaseModel is the foundation for request foundation for request/response validation
#Field lets us add constraints (length, description, required fields)
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Task as TaskModel


def get_db():
    """
    Creates a Database session per request.
    Closes it after the request finishes.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


#APIRouter allows us to group related endpoints
# instead of putting everything in main.py
router = APIRouter()

#--------------
# Data Models (Schemas)
# -------------

class TaskCreate(BaseModel):
    """
    Schema for creating a task.
    This represents the request body sent by the client.
    """

    title: str = Field(

        ...,
        min_length=1,
        max_length=200,
        description="Short description of the task"
    )
    due_date: Optional[date] = None
    #Optional due date in ISO format: YYYY-MM-DD

class Task(TaskCreate):
    """
    Schema for returning a task to the client.
    Extends TaskCreate by adding system-managed fields.
    """
    id: str
    status: str = "pending"
    # status will later support updates (completed, archived, etc.)

class TaskUpdate(BaseModel):
    """
    What the client is allowed to change on an existing task.
    Optional fields mean you can update only what you send.
    """
    title: Optional[str] = None
    due_date: Optional[date] = None
    status: Optional[str] = None  # allow status updates too

#---------------------------
# Temporary In-Memory Storage
#--------------------------
#This list simulates a database for now.
# We will replace this with SQLite / Postgres later.
TASKS: List[Task] = []


#-----------------------
#API Endpoints
#----------------------

# -----------------------
# API Endpoints (SQLite-backed)
# -----------------------

@router.post("/tasks", response_model=Task)
def create_task(payload: TaskCreate, db: Session = Depends(get_db)):
    """
    Create a new task and store it in SQLite.

    - payload: validated request body (title, optional due_date)
    - db: database session injected per request
    """

    # Create a new SQLAlchemy Task object (not yet saved)
    task = TaskModel(
        id=str(uuid4()),          # generate unique task ID
        title=payload.title,      # task title from request
        due_date=payload.due_date,
        status="pending"          # default status
    )

    # Stage the object for insertion
    db.add(task)

    # Commit transaction (writes to database)
    db.commit()

    # Refresh pulls DB-generated values back into the object
    db.refresh(task)

    # Return the saved task (FastAPI converts to response_model)
    return task

@router.get("/tasks", response_model=List[Task])
def list_tasks(db: Session = Depends(get_db)):
    """
    Retrieve all tasks from SQLite.
    """

    # Query all rows from the tasks table
    tasks = db.query(TaskModel).all()

    # Return list of TaskModel objects
    return tasks

@router.get("/tasks/{task_id}", response_model=Task)
def get_task(task_id: str, db: Session = Depends(get_db)):
    """
    Retrieve a single task by its ID.
    """

    # Look up task by primary key
    task = db.query(TaskModel).filter(TaskModel.id == task_id).first()

    # If no task exists, return HTTP 404
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Return the found task
    return task

@router.put("/tasks/{task_id}", response_model=Task)
def update_task(task_id: str, payload: TaskUpdate, db: Session = Depends(get_db)):
    """
    Update fields on an existing task.

    Only fields sent by the client will be updated.
    """

    # Fetch task from database
    task = db.query(TaskModel).filter(TaskModel.id == task_id).first()

    # If task doesn't exist, return 404
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Update fields only if provided
    if payload.title is not None:
        task.title = payload.title

    if payload.due_date is not None:
        task.due_date = payload.due_date

    if payload.status is not None:
        task.status = payload.status

    # Persist changes
    db.commit()

    # Refresh to ensure updated values are returned
    db.refresh(task)

    return task

@router.post("/tasks/{task_id}/complete", response_model=Task)
def complete_task(task_id: str, db: Session = Depends(get_db)):
    """
    Mark a task as completed.
    """

    # Fetch task from database
    task = db.query(TaskModel).filter(TaskModel.id == task_id).first()

    # If task doesn't exist, return 404
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Update status field
    task.status = "completed"

    # Commit change
    db.commit()

    # Refresh updated task
    db.refresh(task)

    return task

@router.delete("/tasks/{task_id}")
def delete_task(task_id: str, db: Session = Depends(get_db)):
    """
    Delete a task from SQLite by ID.
    """

    # Fetch task
    task = db.query(TaskModel).filter(TaskModel.id == task_id).first()

    # Return 404 if task not found
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Remove task from database
    db.delete(task)
    db.commit()

    return {
        "deleted": True,
        "id": task_id
    }
