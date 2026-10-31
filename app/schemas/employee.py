from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional
from datetime import datetime

class EmployeeCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, description='Nombre completo del empleado')
    ci: str = Field(..., min_length=6, max_length=20, description='Cédula de identidad')
    email: Optional[str] = Field(default=None, max_length=100)
    phone: Optional[str] = Field(default=None, max_length=30)
    role: str = Field(default='Cajero', max_length=50, description='Cargo o puesto (Cajero, Almacenista, Supervisor, etc.)')
    shift: str = Field(default='Mañana (07:00 - 15:00)', max_length=50, description='Horario de turno')
    salary: Optional[float] = Field(default=0.0, ge=0)
    status: Optional[str] = Field(default='En Turno', max_length=30)

    @field_validator('name', mode='before')
    @classmethod
    def clean_name(cls, value: str):
        if isinstance(value, str):
            return value.strip().title()
        return value

    @field_validator('ci', mode='before')
    @classmethod
    def clean_ci(cls, value: str):
        if isinstance(value, str):
            return value.strip().replace('.', '').replace('-', '')
        return str(value)

class EmployeeUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    role: Optional[str] = None
    shift: Optional[str] = None
    salary: Optional[float] = None
    status: Optional[str] = None
    is_active: Optional[bool] = None

class EmployeeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    ci: str
    email: Optional[str] = None
    phone: Optional[str] = None
    role: str
    shift: str
    salary: Optional[float] = 0.0
    status: str
    is_active: bool
    created_at: Optional[datetime] = None

