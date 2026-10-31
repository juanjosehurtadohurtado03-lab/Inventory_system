from fastapi import Depends
from sqlalchemy.orm import Session
from app.database.connect import get_db
from app.repositories.employee_repository import EmployeeRepository
from app.services.employee_service import EmployeeService

def get_employee_repository(db: Session = Depends(get_db)) -> EmployeeRepository:
    return EmployeeRepository(db)

def get_employee_service(repo: EmployeeRepository = Depends(get_employee_repository)) -> EmployeeService:
    return EmployeeService(repo)

