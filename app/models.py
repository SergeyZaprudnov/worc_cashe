from sqlalchemy import (Column, Integer, String, Float, DateTime, ForeignKey, Boolean, BigInteger, Date, Text)
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime, date

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False, index=True)
    full_name = Column(String(255))
    phone = Column(String(20))
    is_admin = Column(Boolean, default=False)
    is_autorized = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    operations = relationship("UserOperation", back_populates="user", cascade="all, delete-orphan")
    work_sessions = relationship("WorkSession", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(tg={self.telegram_id}, name{self.full_name})>"

class OperationCategory(Base):
    """ Категория, главная операция"""
    __tablename__ = 'operation_categories'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    suboperations = relationship("SubOperation", back_populates="category", cascade="all, delete-orphan")
    user_operations = relationship("UserOperation", back_populates="category")

    def __repr__(self):
        return f"<Category{self.name})>"

class SubOperation(Base):
    """Подоперация"""
    __tablename__ = "suboperations"

    id = Column(Integer, primary_key=True)
    category_id = Column(Integer, ForeignKey("operation_categories.id"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    unit = Column(String(100), nullable=False)
    price = Column(Float, nullable=False, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    category = relationship("OperationCategory", back_populates="suboperations")
    user_operations = relationship("UserOperation", back_populates="suboperations")

    def __repr__(self):
        return f"<SubOperation({self.name}, price={self.price})>"

