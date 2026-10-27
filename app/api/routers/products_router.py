from fastapi import APIRouter, Depends, Request, status
from fastapi.templating import Jinja2Templates

from app.schemas.product import ProductCreate, ProductResponse
from app.services.products_service import ProductServices
from app.api.depends.deps_product.product import get_product_service

from pathlib import Path

URL_DIR = Path(__file__).resolve().parent.parent.parent

router = APIRouter(prefix='/management', tags=['Products'])
templates = Jinja2Templates(directory=str(URL_DIR / 'templates'))

@router.post('/', response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def add_product(product: ProductCreate, serviceProduct: ProductServices = Depends(get_product_service)):
    return serviceProduct.insert_or_restock_product(product)

@router.get('/', response_model=list[ProductResponse])
async def search_products(id: int = None, name: str = None, serviceProduct: ProductServices = Depends(get_product_service)):
    return serviceProduct.search_products_by_optional_name_or_id(id, name)

@router.put('/{product_id}', response_model=ProductResponse)
async def update_product(product_id: int, product_update: ProductCreate, name: str = None, serviceProduct: ProductServices = Depends(get_product_service)):
    return serviceProduct.update_by_id(product_id, product_update, name)

@router.delete('/{product_id}', status_code=status.HTTP_204_NO_CONTENT)
async def soft_delete_product(product_id: int, serviceProduct: ProductServices = Depends(get_product_service)):
    return serviceProduct.soft_delete(product_id)

# Patron modelo vista controlador