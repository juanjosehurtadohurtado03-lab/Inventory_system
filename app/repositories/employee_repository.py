from sqlalchemy.orm import Session
from app.models.employee import EmployeeModel
from app.schemas.employee import EmployeeCreate, EmployeeUpdate
from typing import Optional

class EmployeeRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self, only_active: bool = True):
        query = self.db.query(EmployeeModel)
        if only_active:
            query = query.filter(EmployeeModel.is_active == True)
        return query.order_by(EmployeeModel.id.asc()).all()

    def get_by_id(self, employee_id: int) -> Optional[EmployeeModel]:
        return self.db.query(EmployeeModel).filter(EmployeeModel.id == employee_id).first()

    def get_by_ci(self, ci: str) -> Optional[EmployeeModel]:
        return self.db.query(EmployeeModel).filter(EmployeeModel.ci == ci).first()

    def create(self, data: EmployeeCreate) -> EmployeeModel:
        new_employee = EmployeeModel(
            name=data.name,
            ci=data.ci,
            email=data.email,
            phone=data.phone,
            role=data.role,
            shift=data.shift,
            salary=data.salary,
            status=data.status or 'En Turno',
            is_active=True
        )
        self.db.add(new_employee)
        self.db.commit()
        self.db.refresh(new_employee)
        return new_employee

    def update(self, employee_id: int, data: EmployeeUpdate) -> Optional[EmployeeModel]:
        employee = self.get_by_id(employee_id)
        if not employee:
            return None
        
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(employee, field, value)

        self.db.commit()
        self.db.refresh(employee)
        return employee

    def toggle_status(self, employee_id: int, new_status: str) -> Optional[EmployeeModel]:
        employee = self.get_by_id(employee_id)
        if not employee:
            return None
        employee.status = new_status
        self.db.commit()
        self.db.refresh(employee)
        return employee

    def soft_delete(self, employee_id: int) -> Optional[EmployeeModel]:
        employee = self.get_by_id(employee_id)
        if not employee:
            return None
        employee.is_active = False
        employee.status = 'Inactivo'
        self.db.commit()
        self.db.refresh(employee)
        return employee

