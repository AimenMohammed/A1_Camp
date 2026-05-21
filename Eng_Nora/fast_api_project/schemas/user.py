from pydantic import BaseModel, EmailStr
from typing import Optional, List

# المخطط الأساسي الذي يحتوي على الحقول المشتركة
class UserBase(BaseModel):
    name: str
    email: EmailStr
    is_active: bool = True  # القيمة الافتراضية "نشط"

# المخطط المستخدم عند إنشاء مستخدم جديد (POST)
class UserCreate(UserBase):
    pass

# المخطط المستخدم عند تحديث بيانات مستخدم موجود (PUT / PATCH)
class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None  # يسمح بتغيير الحالة بشكل اختياري

# المخطط المستخدم عند إرسال البيانات للواجهة (الرد من السيرفر)
class UserResponse(UserBase):
    id: int
    
    # إذا أردت إظهار المشاريع التابعة للمستخدم في الرد (اختياري)
    # projects: List["ProjectResponse"] = [] 

    class Config:
        from_attributes = True  # للسماح بقرائة البيانات من SQLAlchemy models
