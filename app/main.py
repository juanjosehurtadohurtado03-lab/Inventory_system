from fastapi import FastAPI, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path
from sqlalchemy.orm import Session
from sqlalchemy import func
from collections import defaultdict

from app.api.routers.products_router import router as product_router
from app.api.routers.sale_router import router as sale_router
from app.api.routers.employees_router import router as employee_router
from app.database.base import Base
from app.database.connect import engine, get_db
from app.models.product import ProductModel
from app.models.sale import SaleModel
from app.models.sale_details import SaleDetailsModel
from app.models.employee import EmployeeModel

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title='Tu Supermercado - Sistema de Inventario y Ventas',
    version='1.0.0',
    description='Sistema integral de gestión de inventario, punto de venta y empleados.'
)

URL_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(URL_DIR / 'templates'))

app.mount("/static", StaticFiles(directory='static'), name='static')

app.include_router(product_router, prefix='/products')
app.include_router(sale_router, prefix='/sales')
app.include_router(employee_router)

@app.get('/', response_class=HTMLResponse)
async def home_dashboard(request: Request, db: Session = Depends(get_db)):
    # 1. ESTADÍSTICAS REALES DE INVENTARIO
    all_products = db.query(ProductModel).all()
    active_products = [p for p in all_products if p.is_active]
    total_active_products = len(active_products)
    total_units_stock = sum(p.stock for p in active_products) if active_products else 0
    valor_inventario = sum(float(p.price) * p.stock for p in active_products) if active_products else 0.0

    low_stock_products = [p for p in active_products if p.stock <= 5 and p.stock > 0]
    out_of_stock_products = [p for p in active_products if p.stock <= 0]
    low_stock_count = len(low_stock_products)
    out_of_stock_count = len(out_of_stock_products)

    # 2. ESTADÍSTICAS REALES DESCRIPTIVAS DE VENTAS
    all_sales = db.query(SaleModel).order_by(SaleModel.id.desc()).all()
    total_sales_count = len(all_sales)
    paid_sales = [s for s in all_sales if s.status == 'PAGADO']
    pending_sales = [s for s in all_sales if s.status == 'PENDIENTE']
    cancelled_sales = [s for s in all_sales if s.status == 'CANCELADO']

    paid_sales_count = len(paid_sales)
    pending_sales_count = len(pending_sales)
    cancelled_sales_count = len(cancelled_sales)

    # Recaudación total e ingresos perdidos por cancelaciones
    total_revenue = sum(float(s.total) for s in paid_sales) if paid_sales else 0.0
    lost_revenue = sum(float(s.total) for s in cancelled_sales) if cancelled_sales else 0.0

    # Ticket promedio de compra
    ticket_promedio = (total_revenue / paid_sales_count) if paid_sales_count > 0 else 0.0

    # Tasa de conversión y tasa de cancelación (Análisis de por qué los clientes no compran)
    tasa_conversion = (paid_sales_count / total_sales_count * 100.0) if total_sales_count > 0 else 0.0
    tasa_cancelacion = (cancelled_sales_count / total_sales_count * 100.0) if total_sales_count > 0 else 0.0

    # 3. ANÁLISIS DE PRODUCTOS: LO QUE MÁS COMPRAN VS PRODUCTOS ESTANCADOS
    all_details = db.query(SaleDetailsModel).all()
    paid_sale_ids = {s.id for s in paid_sales}
    
    product_sales_stats = defaultdict(lambda: {'id': 0, 'name': '', 'units_sold': 0, 'revenue': 0.0, 'orders_count': 0})
    for detail in all_details:
        if detail.sale_id in paid_sale_ids:
            p_id = detail.product_id
            product_sales_stats[p_id]['id'] = p_id
            product_sales_stats[p_id]['name'] = detail.name
            product_sales_stats[p_id]['units_sold'] += detail.quantity
            product_sales_stats[p_id]['revenue'] += float(detail.subtotal)
            product_sales_stats[p_id]['orders_count'] += 1

    # Productos más vendidos (Top Sellers)
    top_selling_products = sorted(
        product_sales_stats.values(),
        key=lambda x: x['units_sold'],
        reverse=True
    )[:5]

    # Identificar productos sin movimiento (capital inmovilizado)
    sold_product_ids = set(product_sales_stats.keys())
    stagnant_products = [
        p for p in active_products if p.id not in sold_product_ids
    ]

    # 4. CLIENTES REALES
    customers = [s.ci_customer for s in all_sales]
    unique_customers_count = len(set(customers))
    recurrent_customers_count = sum(1 for c in set(customers) if customers.count(c) > 1)

    # 5. EMPLEADOS REALES DESDE LA BASE DE DATOS
    employees = db.query(EmployeeModel).all()
    active_employees = [e for e in employees if e.is_active]

    return templates.TemplateResponse(
        request,
        name='index.html',
        context={
            # Inventario
            "total_products": total_active_products,
            "total_stock": total_units_stock,
            "valor_inventario": valor_inventario,
            "low_stock_count": low_stock_count,
            "out_of_stock_count": out_of_stock_count,
            "low_stock_products": low_stock_products[:5],
            "stagnant_products": stagnant_products[:5],
            "stagnant_count": len(stagnant_products),

            # Ventas y Comportamiento Comercial
            "total_sales_count": total_sales_count,
            "paid_sales_count": paid_sales_count,
            "pending_sales_count": pending_sales_count,
            "cancelled_sales_count": cancelled_sales_count,
            "total_revenue": total_revenue,
            "lost_revenue": lost_revenue,
            "ticket_promedio": ticket_promedio,
            "tasa_conversion": round(tasa_conversion, 1),
            "tasa_cancelacion": round(tasa_cancelacion, 1),
            "recent_sales": all_sales[:6],

            # Lo que más compran
            "top_selling_products": top_selling_products,

            # Clientes
            "unique_customers_count": unique_customers_count,
            "recurrent_customers_count": recurrent_customers_count,

            # Empleados
            "employees": employees,
            "total_employees": len(employees),
            "active_employees": len(active_employees),
            "on_shift_count": sum(1 for e in active_employees if e.status == 'En Turno')
        }
    )
