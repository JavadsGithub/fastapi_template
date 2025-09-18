from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from .service import ItemsService
from .schema import ItemCreate, ItemOut, ItemUpdate
from app.api.deps import get_items_service

router = APIRouter()


@router.post("/", response_model=ItemOut, status_code=status.HTTP_201_CREATED)
async def create_item(
    payload: ItemCreate, service: ItemsService = Depends(get_items_service)
):
    return await service.create_item(payload)


@router.get("/", response_model=List[ItemOut])
async def list_items(
    limit: int = 100, service: ItemsService = Depends(get_items_service)
):
    return await service.list_items(limit)


@router.get("/{item_id}", response_model=ItemOut)
async def read_item(item_id: int, service: ItemsService = Depends(get_items_service)):
    obj = await service.get_item(item_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Item not found")
    return obj


@router.put("/{item_id}", response_model=ItemOut)
async def update_item(
    item_id: int,
    payload: ItemUpdate,
    service: ItemsService = Depends(get_items_service),
):
    obj = await service.update_item(item_id, payload)
    if not obj:
        raise HTTPException(status_code=404, detail="Item not found")
    return obj
