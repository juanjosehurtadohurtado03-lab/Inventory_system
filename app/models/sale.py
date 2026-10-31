from sqlalchemy import Column, String, Integer, Numeric, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.base import Base

class SaleModel(Base):
    __tablename__ = 'sales'
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime(timezone=True), server_default=func.now())
    time = Column(DateTime(timezone=True), server_default=func.now())
    ci_customer = Column(String, nullable=False)
    total = Column(Numeric(10, 2), nullable=False)
    status = Column(String(20), default='PENDIENTE')
    sale_details = relationship('SaleDetailsModel', back_populates='sale', cascade='all, delete-orphan')