"""
routes.py

This file defines the API routes for the TaskFlow service.
It contains:
- Data models (what a Task looks like)
- API endpoints (how clients interact with Tasks)
- Temporary in-memory storage (will later be replaced by a database)
"""

from fastapi import HTTPException # add to imports at top (used for 404 errors)
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
    """Schema for partial updates.
    Any field omitted will remain unchanged.
    """
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    due_date: Optional[date] = None

#---------------------------
# Temporary In-Memory Storage
#--------------------------
#This list simulates a database for now.
# We will replace this with SQLite / Postgres later.
TASKS: List[Task] = []


#-----------------------
#API Endpoints
#----------------------

@router.post("/tasks", response_model = Task)
def create_task(payload: TaskCreate) -> Task:
    """
    Create a new task.

    Steps:
    1. Receive validated input from the client (payload)
    2. Generate a unique ID for the task
    3. Create a Task object
    4. Store it in memory
    5. Return the created task
    """
    task = Task(
        id=str(uuid4()),     # generate unique identifier
        title=payload.title,
        due_date=payload.due_date
    )

    TASKS.append(task)
    return task

def find_task_index(task_id: str) -> int:
    """
    Returns the index of the task in TASKS.
    Raises 404 if not found.
    """
    for i, task in enumerate(TASKS):
        if task.id == task_id:
            return i
    raise HTTPException(status_code=404, detail="Task not found")

@router.get("/tasks", response_model=List[Task])
def list_task() -> List[Task]:
    """
    Return all tasks.

    For now:
    - Reads from in-memory storage
    - Returns the full task list

    Later:
    - Will support pagination, filtering and database queries
    """
    return TASKS

@router.get("/task/{task_id}", response_model=Task)
def get_task(task_id: str) -> Task:
    """
    Fetch one task by ID.
    """
    idx = find_task_index(task_id)
    return TASKS[idx]

@router.put("/task/{task_id}", response_model = Task)
def update_task(task_id: str, payload: TaskUpdate) -> Task:
    """
    Update title and/or due_date for an existing task.
    """
    idx = find_task_index(task_id)
    task = TASKS[idx]

    if payload.title is not None:
        task.title = payload.title
    if payload.due_date is not None:
        task.due_date = payload.due_date

    TASKS[idx] = task
    return task

@router.post("/task/{task_id}/complete", response_model=Task)
def complete_task(task_id: str) -> Task:
    """
    Mark a task as completed.
    """
    idx = find_task_index(task_id)
    task = TASKS[idx]
    task.status = "completed"
    TASKS[idx] = task
    return task

@router.delete("/task/{task_id}")
def delete_task(task_id: str):
    """
    Delete a task by ID.
    """    
    idx = find_task_index(task_id)
    TASKS.pop(idx)
    return {"deleted": True, "id": task_id}