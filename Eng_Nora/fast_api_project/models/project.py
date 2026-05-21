from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Project(Base):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String)
    
    # التعديل هنا: نغير CASCADE إلى SET NULL ونسمح بـ nullable=True
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    owner = relationship("User", back_populates="projects")
    
    # ملاحظة: بالنسبة للمهام التابعة للمشروع، يفضل ترك الـ Cascade 
    # إلا إذا كنت تريد بقاء المهام حتى لو حُذف المشروع نفسه!
    tasks = relationship("Task", back_populates="project", cascade="all, delete-orphan")
