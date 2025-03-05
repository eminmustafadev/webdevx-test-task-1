from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import (
    Session,
    joinedload,
)
import asyncio
from . import models, schemas, services
from .database import get_db

router = APIRouter()

@router.post("/projects/", response_model=schemas.ProjectResponse)
async def create_project(project: schemas.ProjectCreate, db: Session = Depends(get_db)):
    try:
        tasks = services.generate_tasks(project.project_name, project.location)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI error: {str(e)}")

    db_project = models.Project(**project.model_dump())
    db.add(db_project)
    db.commit()
    db.refresh(db_project)

    for task in tasks:
        db_task = models.Task(
            project_id=db_project.id,
            name=task,
            status="pending"
        )
        db.add(db_task)
    db.commit()

    asyncio.create_task(simulate_task_progress(db_project.id))
    return {
        **db_project.__dict__,
        "tasks": [{"name": t.name, "status": t.status} for t in db_project.tasks]
    }

@router.get("/projects/{project_id}", response_model=schemas.ProjectResponse)
def read_project(project_id: int, db: Session = Depends(get_db)):
    project = db.query(models.Project).options(
        joinedload(models.Project.tasks)
    ).get(project_id)

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    return {
        **project.__dict__,
        "tasks": [{"name": t.name, "status": t.status} for t in project.tasks]
    }

async def simulate_task_progress(project_id: int):
    await asyncio.sleep(2)
    db = next(get_db())

    project = db.query(models.Project).get(project_id)
    project.status = "in_progress"
    db.commit()

    tasks = db.query(models.Task).filter_by(project_id=project_id).all()
    for task in tasks:
        await asyncio.sleep(5)  # Simulate work delay
        task.status = "completed"
        db.commit()

    project.status = "completed"
    db.commit()
    db.close()
