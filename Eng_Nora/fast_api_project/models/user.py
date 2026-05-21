from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True)
    is_active = Column(Boolean, default=True)

    # تم إزالة الـ cascade لضمان بقاء المشاريع والمهام بعد حذف المستخدم
    projects = relationship("Project", back_populates="owner")
    tasks = relationship("Task", back_populates="assigned_user")

