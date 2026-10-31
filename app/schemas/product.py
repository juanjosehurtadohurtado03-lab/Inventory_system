from pydantic import BaseModel, Field, field_validator, ConfigDict
from decimal import Decimal

class ProductCreate(BaseModel):
    name: str
    price: Decimal = Field(ge=1, description='El precio no puede ser negativo.')
    stock: int = Field(ge=1, description='El stock no puede ser negativo.')
    
    @field_validator('name', mode='before')
    @classmethod
    def clean_name(cls, value: str):
        if isinstance(value, str):
            return value.strip().title()
        return value

class ProductResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    name: str
    price: Decimal
    stock: int