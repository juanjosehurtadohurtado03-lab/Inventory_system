from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.product import ProductModel
from app.schemas.product import ProductCreate

class CRUD_products:
    def __init__(self, db: Session):
        self.db = db
        
    def post_by_name(self, product: ProductCreate):
        return self.db.query(ProductModel).filter(ProductModel.name.ilike(f'%{product.name}%'), ProductModel.is_active == True).first()

    def get_all_products(self, id: int = None, name: str = None):
        if id or name:
            if id and name:
                return self.db.query(ProductModel).filter(ProductModel.id == id, ProductModel.name == name, ProductModel.is_active == True).all()
            elif id:
                return self.db.query(ProductModel).filter(ProductModel.id == id, ProductModel.is_active == True).all()
            elif name:
                return self.db.query(ProductModel).filter(ProductModel.name.ilike(f'%{name}%'), ProductModel.is_active == True).all()
        return self.db.query(ProductModel).filter(ProductModel.is_active == True).all()
    
    def search_by_name_and_id(self, id: int = None, name: str = None):
        if id or name:
            if id and name:
                return self.db.query(ProductModel).filter(ProductModel.id == id, ProductModel.name == name, ProductModel.is_active == True).first()
            elif id:
                return self.db.query(ProductModel).filter(ProductModel.id == id, ProductModel.is_active == True).first()
            elif name:
                return self.db.query(ProductModel).filter(ProductModel.name.ilike(f'%{name}%'), ProductModel.is_active == True).first()
        else:
            return None

    def get_by_id(self, product_id: int):
        return self.db.query(ProductModel).filter(ProductModel.id == product_id, ProductModel.is_active == True).first()

    def get_by_id_or_name(self, product_id: int, name: str):
        return self.db.query(ProductModel).filter((ProductModel.id == product_id) | (ProductModel.name.ilike(f'%{name}%')), ProductModel.is_active == True).first()
    
    def search_product_by_id(self, product_id: int):
        return self.db.query(ProductModel).filter(ProductModel.id == product_id, ProductModel.is_active == True).first()