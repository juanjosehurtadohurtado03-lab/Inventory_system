from fastapi import APIRouter, Depends, Request, status
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse

from pydantic import TypeAdapter
from app.schemas.product import ProductCreate, ProductResponse
from app.services.products_service import ProductServices
from app.api.depends.deps_product.product import get_product_service

from pathlib import Path

URL_DIR = Path(__file__).resolve().parent.parent.parent
DETAIL_SCHEMA = TypeAdapter(list[ProductResponse])

router = APIRouter(prefix='/management', tags=['Products'])
templates = Jinja2Templates(directory=str(URL_DIR / 'templates'))

@router.post('/insert', response_class=HTMLResponse, status_code=status.HTTP_201_CREATED)
async def add_product(product: ProductCreate, serviceProduct: ProductServices = Depends(get_product_service)):
    serviceProduct.insert_or_restock_product(product)
    return RedirectResponse(url="/management/", status_code=303)

@router.get('/', response_class=HTMLResponse)
async def search_products(request: Request, id: int = None, name: str = None, serviceProduct: ProductServices = Depends(get_product_service)):
    products = serviceProduct.search_products_by_optional_name_or_id(id, name)
    try:
        products = DETAIL_SCHEMA.validate_python(products)
        return templates.TemplateResponse(
            request, name='product.html', context={'products': products}
        )
    except Exception as e:
        return templates.TemplateResponse(
            request, name='exc.html', context={'Error': f'{e}'}, status_code=500
        )

@router.put('/{product_id}', response_model=ProductResponse)
async def update_product(request: Request, product_id: int, product_update: ProductCreate, name: str = None, serviceProduct: ProductServices = Depends(get_product_service)):
    product = serviceProduct.update_by_id(product_id, product_update, name)
    try:
        product = ProductResponse.model_validate(product)
        return templates.TemplateResponse(
            request, name='product.html', context={'products': product}
        )
    except Exception as e:
        return templates.TemplateResponse(
            request, name='exc.html', context={'Error': f'{e}'}, status_code=500
        )

@router.delete('/{product_id}')
async def soft_delete_product(product_id: int, serviceProduct: ProductServices = Depends(get_product_service)):
    serviceProduct.soft_delete(product_id)
    return RedirectResponse(url='/management/', status_code=303)

#! MODIFICAR EL DINERO PARA QUE SE GUARDE COMO ENTEROS EL VALOR INGRESADO CON DECIMALES Y SE MULTIPLIQUE *100 PARA EL GUARDADO, AL TRAERLO A LA INTERFAZ O ENVIARSELO AL USUARIO, /100 PARA QUE VUELVA A SU VALOR DECIMAL