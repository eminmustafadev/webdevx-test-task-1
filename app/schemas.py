from pydantic import BaseModel
from datetime import datetime
from typing import List


class ProjectCreate(BaseModel):
    project_name: str
    location: str


class TaskResponse(BaseModel):
    name: str
    status: str


class ProjectResponse(ProjectCreate):
    id: int
    status: str
    created_at: datetime
    tasks: List[TaskResponse]
