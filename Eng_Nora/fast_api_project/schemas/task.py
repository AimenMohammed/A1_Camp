from pydantic import BaseModel
from typing import Optional

# 1. الكلاس الأساسي (الحقول المشتركة)
class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    status: Optional[str] = "pending"
    project_id: int
    assigned_to: Optional[int] = None

# 2. كلاس الإنشاء (يستخدم عند استقبال بيانات مهمة جديدة)
class TaskCreate(TaskBase):
    pass

# 3. كلاس التحديث (ضروري لعمليات الـ PUT/PATCH)
# جعلنا جميع الحقول اختيارية (Optional) ليتمكن المستخدم من تحديث حقل واحد فقط إن أراد
class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    project_id: Optional[int] = None
    assigned_to: Optional[int] = None

# 4. كلاس الاستجابة (ما يرسله السيرفر للمتصفح)
class TaskResponse(TaskBase):
    id: int

    class Config:
        from_attributes = True # لتمكين Pydantic من قراءة بيانات SQLAlchemy models
