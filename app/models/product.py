from sqlalchemy import Column, String, Integer, Boolean, Numeric
from app.database.base import Base
from sqlalchemy.orm import relationship

class ProductModel(Base):
    __tablename__ = 'products'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    price = Column(Numeric(10, 2), nullable=False)
    stock = Column(Integer, nullable=False)
    is_active = Column(Boolean, default=True)