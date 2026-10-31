from sqlalchemy import Column, String, Integer, Boolean, Numeric, DateTime
from sqlalchemy.sql import func
from app.database.base import Base

class EmployeeModel(Base):
    __tablename__ = 'employees'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    ci = Column(String(20), unique=True, nullable=False, index=True)
    email = Column(String(100), nullable=True)
    phone = Column(String(30), nullable=True)
    role = Column(String(50), nullable=False, default='Cajero')
    shift = Column(String(50), nullable=False, default='Mañana (07:00 - 15:00)')
    salary = Column(Numeric(10, 2), nullable=True, default=0.0)
    status = Column(String(30), nullable=False, default='En Turno')
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

