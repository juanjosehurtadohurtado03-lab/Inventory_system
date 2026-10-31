from fastapi import APIRouter, Depends, Request, status, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse

from app.schemas.sale import SaleCreate, SaleResponde, SaleUpdateStatus
from app.schemas.sale_details import SaleDetailsResponse
from app.api.depends.deps_sale.sale import get_sale_service
from app.services.sale_service import SaleService

from pathlib import Path

URL_DIR = Path(__file__).resolve().parent.parent.parent

router = APIRouter(prefix='/sale', tags=['Sale'])
templates = Jinja2Templates(directory=str(URL_DIR / 'templates'))

@router.get('/', response_class=HTMLResponse)
def get_sale_page(request: Request, serviceSale: SaleService = Depends(get_sale_service)):
    products = serviceSale.ProductService.search_products_by_optional_name_or_id()
    pending_sales = serviceSale.get_pending_sales()
    recent_sales = serviceSale.get_all_sales(limit=25)
    return templates.TemplateResponse(
        request,
        name='sale.html',
        context={
            'products': products,
            'pending_sales': pending_sales,
            'recent_sales': recent_sales,
        }
    )

@router.post('/', status_code=status.HTTP_201_CREATED)
def add_product_sale(request: Request, sale_data: SaleCreate, serviceSale: SaleService = Depends(get_sale_service)):
    try:
        sale = serviceSale.verific_and_add_product_sale(sale_data)
        validated_sale = SaleResponde.model_validate(sale)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error al procesar la venta: {e}")

    accept = request.headers.get('accept', '')
    if 'application/json' in accept:
        return validated_sale

    products = serviceSale.ProductService.search_products_by_optional_name_or_id()
    pending_sales = serviceSale.get_pending_sales()
    recent_sales = serviceSale.get_all_sales(limit=25)
    return templates.TemplateResponse(
        request,
        name='sale.html',
        context={
            'sale': validated_sale,
            'products': products,
            'pending_sales': pending_sales,
            'recent_sales': recent_sales,
            'success_msg': f'Venta #{sale.id} creada con éxito.'
        }
    )

@router.post('/{sale_id}', status_code=status.HTTP_200_OK)
@router.patch('/{sale_id}', status_code=status.HTTP_200_OK)
def pay(request: Request, sale_id: int, status_sale: SaleUpdateStatus, serviceSale: SaleService = Depends(get_sale_service)):
    serviceSale.pay_or_cancel(sale_id, status_sale)
    accept = request.headers.get('accept', '')
    if 'application/json' in accept:
        return {
            "status": "ok",
            "message": f"Factura #{sale_id} marcada como {status_sale.status}.",
            "sale_id": sale_id,
            "sale_status": str(status_sale.status)
        }
    return RedirectResponse(url='/sales/sale/', status_code=status.HTTP_303_SEE_OTHER)

@router.get('/invoice/{sale_id}', response_class=HTMLResponse)
def get_invoice(request: Request, sale_id: int, serviceSale: SaleService = Depends(get_sale_service)):
    sale = serviceSale.get_sale_by_id(sale_id)
    if not sale:
        return HTMLResponse(content="<div style='font-family:sans-serif;padding:20px;text-align:center;'><h2>Factura no encontrada</h2><p>El ID solicitado no existe.</p></div>", status_code=404)
    
    now_fecha = sale.date.strftime("%d/%m/%Y") if sale.date else ""
    now_time = sale.time.strftime("%I:%M %p") if sale.time else ""
    
    formatted_products = [
        {
            'name': item.name,
            'cant': item.quantity,
            'price': f"{item.price_unit:.2f}"
        }
        for item in sale.sale_details
    ]
    
    return templates.TemplateResponse(
        request,
        name='invoice.html',
        context={
            'client': f"C.I. {sale.ci_customer}",
            'rif': sale.ci_customer,
            'bill_id': f"{sale.id:06d}",
            'now_fecha': now_fecha,
            'now_time': now_time,
            'products': formatted_products,
            'price_total': f"Bs. {sale.total:.2f}"
        }
    )
