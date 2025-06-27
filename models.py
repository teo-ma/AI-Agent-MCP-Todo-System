from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime

class TodoBase(BaseModel):
    title: str
    content: Optional[str] = None
    due_date: Optional[date] = None

class TodoCreate(TodoBase):
    pass

class TodoUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    due_date: Optional[date] = None
    completed: Optional[bool] = None

class Todo(TodoBase):
    id: int
    completed: bool = False
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class MCPRequest(BaseModel):
    method: str
    params: dict

class MCPResponse(BaseModel):
    result: Optional[dict] = None
    error: Optional[str] = None
