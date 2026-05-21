from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import List
from database import get_db

# استيراد الموديلات
from models import task as models
from models import project as project_models  # تأكد من اسم الملف
from models import user as user_models        # تأكد من اسم الملف

import schemas.task as schemas
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

router = APIRouter(prefix="/tasks", tags=["Tasks"])
templates = Jinja2Templates(directory="templates")

# --- Pages ---

@router.get("/", response_class=HTMLResponse)
def tasks_page(request: Request, db: Session = Depends(get_db)):
    # جلب البيانات لملء الجدول والقوائم المنسدلة
    tasks = db.query(models.Task).all()
    projects = db.query(project_models.Project).all()
    users = db.query(user_models.User).all()
    
    return templates.TemplateResponse("tasks.html", {
        "request": request, 
        "tasks": tasks,
        "projects": projects,
        "users": users
    })

@router.get("/{task_id}", response_class=HTMLResponse)
def task_detail(request: Request, task_id: int, db: Session = Depends(get_db)):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(404, "Task not found")
    return templates.TemplateResponse("task_detail.html", {"request": request, "task": task})

# --- API ---

@router.post("/", response_model=schemas.TaskResponse)
def create_task(task: schemas.TaskCreate, db: Session = Depends(get_db)):
    # التحقق من وجود المشروع إذا أرسل المستخدم ID
    if task.project_id:
        p = db.query(project_models.Project).filter(project_models.Project.id == task.project_id).first()
        if not p:
            raise HTTPException(400, "Project not found")

    # التحقق من وجود المستخدم إذا أرسل المستخدم ID
    if task.assigned_to:
        u = db.query(user_models.User).filter(user_models.User.id == task.assigned_to).first()
        if not u:
            raise HTTPException(400, "User not found")

    db_task = models.Task(**task.dict())
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

@router.put("/{task_id}", response_model=schemas.TaskResponse)
def update_task(task_id: int, task: schemas.TaskUpdate, db: Session = Depends(get_db)):
    db_task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not db_task:
        raise HTTPException(404, "Task not found")
    
    for key, value in task.dict(exclude_unset=True).items():
        setattr(db_task, key, value)
    
    db.commit()
    db.refresh(db_task)
    return db_task

@router.delete("/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    db_task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not db_task:
        raise HTTPException(404, "Task not found")
    
    db.delete(db_task)
    db.commit()
    return {"detail": "Task deleted"}
