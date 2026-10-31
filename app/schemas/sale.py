from pydantic import BaseModel, Field, field_validator, field_serializer, ConfigDict
from app.schemas.sale_details import SaleDetailsResponse
from decimal import Decimal
from enum import Enum
from typing import Optional
from datetime import datetime
from app.core.config import DATE_FORMAT, TIME_FORMAT

class SaleData(BaseModel):
    id: Optional[int] = Field(default=None, description='ID del producto')
    name: Optional[str] = Field(default=None, description='Nombre del producto')
    quantity: int = Field(ge=1, description='La cantidad no puede ser 0 o inferior.')
    
    @field_validator('name', mode='before')
    @classmethod
    def clean_name(cls, value: str):
        if isinstance(value, str):
            return value.strip().title()
        return value

class SaleCreate(BaseModel):
    ci_customer: str = Field(pattern=r"^\d{8}$", description='La C.I. no puede llevar letras, ni espacios ni simbolos.')
    items: list[SaleData] = []

class SaleResponde(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    date: datetime
    time: datetime
    ci_customer: str
    total: Decimal
    status: str
    sale_details: list[SaleDetailsResponse]
    
    @field_serializer('date')
    def serializer_date(self, date_value: datetime, _info) -> str:
        if date_value is None:
            return ''
        return date_value.strftime(DATE_FORMAT)
    
    @field_serializer('time')
    def serializer_time(self, time_value: datetime, _info) -> str:
        if time_value is None:
            return ''
        return time_value.strftime(TIME_FORMAT)

class SaleStatus(str, Enum):
    PAID = 'PAGADO'
    CANCELLED = 'CANCELADO'

class SaleUpdateStatus(BaseModel):
    status: SaleStatus