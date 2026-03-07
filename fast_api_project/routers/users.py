from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError # لإمساك أخطاء تكرار البيانات
from database import get_db
import models.user as user_models
import models.project as project_models
import models.task as task_models
import schemas.user as schemas
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

router = APIRouter(prefix="/users", tags=["Users"])
templates = Jinja2Templates(directory="templates")

# --- القراءة (Read) ---

@router.get("/", response_class=HTMLResponse)
def read_users_page(request: Request, db: Session = Depends(get_db)):
    users = db.query(user_models.User).all()
    return templates.TemplateResponse("users.html", {"request": request, "users": users})

@router.get("/{user_id}", response_class=HTMLResponse)
def user_detail(request: Request, user_id: int, db: Session = Depends(get_db)):
    user = db.query(user_models.User).filter(user_models.User.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="المستخدم غير موجود")

    projects = db.query(project_models.Project).filter(project_models.Project.owner_id == user.id).all()
    tasks = db.query(task_models.Task).filter(task_models.Task.assigned_to == user.id).all()

    return templates.TemplateResponse("user_detail.html", {
        "request": request, 
        "user": user, 
        "projects": projects, 
        "tasks": tasks
    })

# --- العمليات (API) ---

@router.post("/", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user_data: schemas.UserCreate, db: Session = Depends(get_db)):
    try:
        db_user = user_models.User(**user_data.model_dump())
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except IntegrityError:
        # في حال كان الإيميل موجود مسبقاً، يجب عمل rollback لمنع تجميد قاعدة البيانات
        db.rollback()
        raise HTTPException(
            status_code=400, 
            detail="هذا البريد الإلكتروني مسجل بالفعل لمستخدم آخر"
        )

@router.put("/{user_id}", response_model=schemas.UserResponse)
def update_user(user_id: int, user_data: schemas.UserUpdate, db: Session = Depends(get_db)):
    db_user = db.query(user_models.User).filter(user_models.User.id == user_id).first()
    
    if not db_user:
        raise HTTPException(status_code=404, detail="المستخدم غير موجود")

    update_data = user_data.model_dump(exclude_unset=True)
    
    try:
        for key, value in update_data.items():
            setattr(db_user, key, value)
        db.commit()
        db.refresh(db_user)
        return db_user
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400, 
            detail="لا يمكن التحديث، البريد الإلكتروني الجديد مستخدم بالفعل"
        )

@router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(user_models.User).filter(user_models.User.id == user_id).first()
    
    if not db_user:
        raise HTTPException(status_code=404, detail="المستخدم غير موجود")

    # بفضل الـ Cascade في الموديلات، سيقوم PostgreSQL بحذف كل البيانات المرتبطة
    db.delete(db_user)
    db.commit()
    
    return {"detail": f"تم حذف المستخدم {user_id} وجميع مهامه ومشاريعة المرتبطة بنجاح"}
