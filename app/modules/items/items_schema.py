from typing import Optional
from pydantic import BaseModel, ConfigDict


class ItemBase(BaseModel):
    name: str
    price: float
    is_offer: Optional[bool] = None

class ItemCreate(ItemBase):
    pass

class ItemUpdate(ItemBase):
    pass

class ItemOut(ItemBase):
    id: int
    
    model_config = ConfigDict(from_attributes=True) #changed 

