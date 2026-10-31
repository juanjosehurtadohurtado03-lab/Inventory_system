from fastapi import APIRouter, Depends, Request, status, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from pathlib import Path

from app.schemas.employee import EmployeeCreate, EmployeeUpdate, EmployeeResponse
from app.services.employee_service import EmployeeService
from app.api.depends.deps_employee.employee import get_employee_service

URL_DIR = Path(__file__).resolve().parent.parent.parent

router = APIRouter(prefix='/employees', tags=['Employees'])
templates = Jinja2Templates(directory=str(URL_DIR / 'templates'))

@router.get('/', response_class=HTMLResponse)
def list_employees_view(request: Request, service: EmployeeService = Depends(get_employee_service)):
    employees = service.list_employees(only_active=False)
    accept = request.headers.get('accept', '')
    if 'application/json' in accept:
        return [EmployeeResponse.model_validate(e) for e in employees]

    active_count = sum(1 for e in employees if e.is_active)
    on_shift_count = sum(1 for e in employees if e.is_active and e.status == 'En Turno')
    cashiers_count = sum(1 for e in employees if e.is_active and 'cajer' in e.role.lower())

    return templates.TemplateResponse(
        request,
        name='employees.html',
        context={
            'employees': employees,
            'total_employees': len(employees),
            'active_count': active_count,
            'on_shift_count': on_shift_count,
            'cashiers_count': cashiers_count
        }
    )

@router.post('/', status_code=status.HTTP_201_CREATED)
def create_employee(request: Request, data: EmployeeCreate, service: EmployeeService = Depends(get_employee_service)):
    new_emp = service.create_employee(data)
    accept = request.headers.get('accept', '')
    if 'application/json' in accept:
        return EmployeeResponse.model_validate(new_emp)
    return RedirectResponse(url='/employees/', status_code=status.HTTP_303_SEE_OTHER)

@router.put('/{employee_id}', response_model=EmployeeResponse)
def update_employee(employee_id: int, data: EmployeeUpdate, service: EmployeeService = Depends(get_employee_service)):
    updated = service.update_employee(employee_id, data)
    return EmployeeResponse.model_validate(updated)

@router.patch('/{employee_id}/status')
def update_status(employee_id: int, request_data: dict, service: EmployeeService = Depends(get_employee_service)):
    new_status = request_data.get('status', 'En Turno')
    updated = service.update_status(employee_id, new_status)
    return {"status": "ok", "message": f"Estado actualizado a {new_status}", "employee_id": employee_id}

@router.delete('/{employee_id}')
def delete_employee(employee_id: int, service: EmployeeService = Depends(get_employee_service)):
    service.delete_employee(employee_id)
    return {"status": "ok", "message": f"Empleado #{employee_id} desactivado."}

