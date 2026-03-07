from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from database import get_db
import models.project as project_models
import models.task as task_models
import models.user as user_models  # استيراد موديل المستخدمين لجلبه للقائمة
import schemas.project as schemas
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

router = APIRouter(prefix="/projects", tags=["Projects"])
templates = Jinja2Templates(directory="templates")

# Pages
@router.get("/", response_class=HTMLResponse)
def projects_page(request: Request, db: Session = Depends(get_db)):
    # جلب المشاريع
    projects = db.query(project_models.Project).all()
    # الإصلاح: جلب جميع المستخدمين لإظهارهم في الـ datalist للبحث
    users = db.query(user_models.User).all() 
    
    return templates.TemplateResponse("projects.html", {
        "request": request, 
        "projects": projects,
        "users": users  # الآن ستظهر الأسماء في قائمة البحث
    })

@router.get("/{project_id}", response_class=HTMLResponse)
def project_detail(request: Request, project_id: int, db: Session = Depends(get_db)):
    project = db.query(project_models.Project).filter(project_models.Project.id == project_id).first()
    if not project:
        raise HTTPException(404, "Project not found")
    
    # جلب المهام المرتبطة بهذا المشروع
    tasks = db.query(task_models.Task).filter(task_models.Task.project_id == project_id).all()
    
    return templates.TemplateResponse("project_detail.html", {
        "request": request, 
        "project": project, 
        "tasks": tasks
    })

# API
@router.post("/", response_model=schemas.ProjectResponse)
def create_project(project: schemas.ProjectCreate, db: Session = Depends(get_db)):
    # استخدام model_dump() للنسخ الحديثة من Pydantic
    db_project = project_models.Project(**project.model_dump())
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

@router.put("/{project_id}", response_model=schemas.ProjectResponse)
def update_project(project_id: int, project_data: schemas.ProjectUpdate, db: Session = Depends(get_db)):
    db_project = db.query(project_models.Project).filter(project_models.Project.id == project_id).first()
    if not db_project:
        raise HTTPException(404, "Project not found")
    
    for key, value in project_data.model_dump(exclude_unset=True).items():
        setattr(db_project, key, value)
        
    db.commit()
    db.refresh(db_project)
    return db_project

@router.delete("/{project_id}")
def delete_project(project_id: int, db: Session = Depends(get_db)):
    db_project = db.query(project_models.Project).filter(project_models.Project.id == project_id).first()
    if not db_project:
        raise HTTPException(404, "Project not found")
    db.delete(db_project)
    db.commit()
    return {"detail": "Project deleted"}
