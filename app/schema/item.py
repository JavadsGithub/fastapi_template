from pydantic import BaseModel


class ItemBase(BaseModel):
    name: str


class ItemCreate(ItemBase):
    pass


class ItemUpdate(ItemBase):
    pass


class ItemOut(ItemBase):
    id: int

    class Config:
        from_attributes = True
