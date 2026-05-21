from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    
    # الإضافة: حقل الوصف ليتوافق مع الـ Schema
    description = Column(String, nullable=True) 
    
    status = Column(String, default="pending")
    
    # 1. بالنسبة للمشروع: غالباً إذا حُذف المشروع تُحذف مهامه (CASCADE)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=True)
    
    # 2. بالنسبة للمستخدم: التعديل الجوهري هنا (SET NULL)
    assigned_to = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    # العلاقات (Relationships) كما هي دون تغيير
    project = relationship("Project", back_populates="tasks")
    assigned_user = relationship("User", back_populates="tasks")
