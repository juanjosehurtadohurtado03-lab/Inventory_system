from fastapi import FastAPI
from app.api.routers.products_router import router as product_router
from app.api.routers.sale_router import router as sale_router
from fastapi.staticfiles import StaticFiles

from app.database.base import Base
from app.database.connect import engine

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title='Sistema de Inventario y Facturacion',
    version='1.0.0',
    description='API RESTful de inventario y ventas.'
)

app.mount("/static", StaticFiles(directory='static'), name='static')

app.include_router(product_router, prefix='/products')
app.include_router(sale_router, prefix='/sales')