from pydantic import BaseModel
from typing import Optional

# الكلاس الأساسي
class ProjectBase(BaseModel):
    title: str
    description: Optional[str] = None

# كلاس الإنشاء
class ProjectCreate(ProjectBase):
    owner_id: int

# كلاس التحديث (هذا هو الجزء الناقص الذي يسبب الخطأ)
class ProjectUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    owner_id: Optional[int] = None

# كلاس الاستجابة
class ProjectResponse(ProjectBase):
    id: int
    owner_id: int

    class Config:
        from_attributes = True
