from sqlalchemy.orm import Session
from app.models.sale import SaleModel
from app.models.sale_details import SaleDetailsModel
from app.services.products_service import ProductServices
from typing import Any

class CRUD_sale:
    def __init__(self, db: Session):
        self.db = db
    
    def create_sale(self, ci_client: int, total: int, sale_details: list[dict[str: Any]]):
        new_sale = SaleModel(
            ci_customer=ci_client,
            total=total
        )
        
        items_details_list = []
        for item in sale_details:
            detail = SaleDetailsModel(
                name=item['name'],
                quantity=item['quantity'],
                price_unit=item['price_unit'],
                subtotal=item['subtotal'],
                product_id=item['product_id']
            )
            items_details_list.append(detail)
        
        new_sale.sale_details = items_details_list
        
        self.db.add(new_sale)
        return new_sale
    
    def search_sale_by_id(self, sale_id:int):
        return self.db.query(SaleModel).filter(SaleModel.id == sale_id, SaleModel.status.in_(['PENDIENTE'])).first()
    
    def get_sale_by_id(self, sale_id: int):
        return self.db.query(SaleModel).filter(SaleModel.id == sale_id).first()

    def get_all_sales(self, limit: int = 50):
        return self.db.query(SaleModel).order_by(SaleModel.id.desc()).limit(limit).all()

    def get_pending_sales(self):
        return self.db.query(SaleModel).filter(SaleModel.status == 'PENDIENTE').order_by(SaleModel.id.desc()).all()
    
    def update_status_to_paid(self, sale: SaleModel, status: str):
        sale.status = status
        self.db.commit()
        self.db.refresh(sale)
        return sale
    
    def update_status_to_cancelled(self, sale: SaleModel, status: str):
        pass