from pydantic import BaseModel, ConfigDict
from decimal import Decimal

class SaleDetailsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    name: str
    quantity: int
    price_unit: Decimal
    subtotal: Decimal