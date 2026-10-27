import sqlite3 
from sqlalchemy.exc import SQLAlchemyError
from app.repositories.sale_repository import CRUD_sale
from app.models.sale import SaleModel
from app.schemas.sale import SaleData, SaleCreate, SaleStatus, SaleUpdateStatus
from app.services.products_service import ProductServices
from fastapi import HTTPException, status

class SaleService:
    def __init__(self, repo: CRUD_sale, ProductService: ProductServices):
        self.repo = repo
        self.ProductService = ProductService
    
    def verific_and_add_product_sale(self, sale_data: SaleCreate):
        total = 0
        processed_item = []
        
        try:
            for item in sale_data.items:
                if item.id or item.name:
                    product = self.ProductService.search_product_verific(item.id, item.name)
                    if product is None:
                        raise HTTPException(
                            status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'El producto {item.name or item.id} no existe en el inventario..'
                        )
                    if product.stock < item.quantity:
                        raise HTTPException(
                            status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'No contamos con {item.quantity} unidades de {product.name} en el inventario.'
                        )
                    total += product.price * item.quantity
                    product.stock -= item.quantity
                    if product.stock == 0:
                        product.is_active = False
                    
                    processed_item.append({
                        'product_id': product.id,
                        'name': product.name,
                        'quantity': item.quantity,
                        'price_unit': product.price,
                        'subtotal': product.price * item.quantity
                    })
                else:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail='No se permiten campos vacios.'
                    )
            new_sale = self.repo.create_sale(ci_client=sale_data.ci_customer, total=total, sale_details=processed_item)
            self.repo.db.commit()
            self.repo.db.refresh(new_sale)
            return new_sale
        except SQLAlchemyError as e:
            self.repo.db.rollback()
            raise HTTPException(
                status_code=404, detail=f'SQL error: {e}'
            )
    
    def pay_or_cancel(self, sale_id: int, sale_status: SaleUpdateStatus):
        sale = self.repo.search_sale_by_id(sale_id)
        if not sale:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'No existe una factura pendiente con el ID {sale_id}.'
            )
        if sale.status in [SaleStatus.PAID, SaleStatus.CANCELLED]:
            raise HTTPException(
                status_code=404,
                detail=f'Esta factura se encuentra en estado {sale.status}.'
            )

        if sale_status.status == SaleStatus.PAID:
            return self._handle_paid(sale)
        elif sale_status.status == SaleStatus.CANCELLED:
            return self._handle_cancelled(sale)
        
    def _handle_paid(self, sale: SaleModel):
        sale.status = SaleStatus.PAID
        self.repo.db.commit()
        self.repo.db.refresh(sale)
        return sale
        # incluir sistema de factura.
    
    def _handle_cancelled(self, sale: SaleModel):
        list_product_restock = []
        try:
            for item in sale.sale_details:
                self.ProductService.add_update_stock(item.product_id, item.quantity)
                product_detail = {
                    'id': item.id,
                    'name': item.name,
                    'quantity': item.quantity,
                    'price_unit': item.price_unit,
                    'subtotal': item.subtotal
                }
                list_product_restock.append(product_detail)
            sale.status = SaleStatus.CANCELLED
            self.repo.db.commit()
            self.repo.db.refresh(sale)
            return list_product_restock
        except SQLAlchemyError as e:
            self.repo.db.rollback()
            raise HTTPException(
                status_code=404,
                detail=f'SQL Error: {e}'
            )