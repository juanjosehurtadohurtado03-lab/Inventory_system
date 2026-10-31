from app.repositories.employee_repository import EmployeeRepository
from app.schemas.employee import EmployeeCreate, EmployeeUpdate
from fastapi import HTTPException, status
from typing import Optional

class EmployeeService:
    def __init__(self, repo: EmployeeRepository):
        self.repo = repo

    def list_employees(self, only_active: bool = False):
        return self.repo.get_all(only_active=only_active)

    def get_employee(self, employee_id: int):
        employee = self.repo.get_by_id(employee_id)
        if not employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Empleado con ID #{employee_id} no encontrado."
            )
        return employee

    def create_employee(self, data: EmployeeCreate):
        existing = self.repo.get_by_ci(data.ci)
        if existing:
            if not existing.is_active:
                # Reactivar si estaba inactivo
                existing.is_active = True
                existing.name = data.name
                existing.role = data.role
                existing.shift = data.shift
                existing.phone = data.phone
                existing.email = data.email
                existing.salary = data.salary
                existing.status = data.status or 'En Turno'
                self.repo.db.commit()
                self.repo.db.refresh(existing)
                return existing
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ya existe un empleado registrado con la C.I. {data.ci}."
            )
        return self.repo.create(data)

    def update_employee(self, employee_id: int, data: EmployeeUpdate):
        updated = self.repo.update(employee_id, data)
        if not updated:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No se pudo actualizar: Empleado #{employee_id} no encontrado."
            )
        return updated

    def update_status(self, employee_id: int, new_status: str):
        updated = self.repo.toggle_status(employee_id, new_status)
        if not updated:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Empleado #{employee_id} no encontrado."
            )
        return updated

    def delete_employee(self, employee_id: int):
        deleted = self.repo.soft_delete(employee_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Empleado #{employee_id} no encontrado."
            )
        return deleted

