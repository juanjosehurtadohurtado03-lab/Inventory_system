from app.schemas.product import ProductCreate
from app.models.product import ProductModel

from fastapi import HTTPException, status
from app.repositories.product_repository import CRUD_products

class ProductServices:
    def __init__(self, repo: CRUD_products):
        self.repo = repo
    
    def insert_or_restock_product(self, product: ProductCreate):
        existing_product = self.repo.post_by_name(product)
        if existing_product:
            product_db = existing_product
            if product.price:
                product_db.stock += product.stock
                product_db.price = product.price
            else:
                product_db.stock += product.stock
            self.repo.db.commit()
            self.repo.db.refresh(product_db)
            return product_db
        
        new_product = ProductModel(**product.model_dump())
        self.repo.db.add(new_product)
        self.repo.db.commit()
        self.repo.db.refresh(new_product)
        return new_product
    
    def search_products_by_optional_name_or_id(self, id: int = None, name: str = None):
        if name:
            name = name.capitalize()
        return self.repo.get_all_products(id, name)
    
    def search_one_product(self, product_id: int):
        return self.repo.get_by_id(product_id)
    
    def search_product_verific(self, id: int = None, name: str = None):
        product = self.repo.search_by_name_and_id(id, name)
        if not product:
            raise HTTPException(
                status_code=404,
                detail=f'El producto {id} no existe.'
            )
        return product
    
    def update_by_id(self, product_id: int, product_update: ProductCreate, name: str = None):
        product = self.repo.get_by_id_or_name(product_id, name)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Producto no encontrado.'
            )
        for field, value in product_update.model_dump().items():
                setattr(product, field, value)
        self.repo.db.commit()
        self.repo.db.refresh(product)
        return product
    
    def add_update_stock(self, product_id: int, update_stock: int):
        product = self.repo.search_product_by_id(product_id)
        if not product:
            raise HTTPException(
                status_code=404,
                detail=f'No se ha encontrado el producto ID {product_id}.'
            )
        product.stock += update_stock
    
    def soft_delete(self, product_id: int):
        product = self.repo.get_by_id(product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Producto no encontrado.'
            )
        product.is_active = False
        self.repo.db.commit()