from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_pagination import Page, Params, paginate

from app.api.deps import get_items_service
from app.schema.response import StandardResponse, success

from ..schema.item import ItemCreate, ItemOut, ItemUpdate
from ..service.item import ItemsService

router = APIRouter()


@router.post(
    "/", response_model=StandardResponse[ItemOut], status_code=status.HTTP_201_CREATED
)
async def create_item(
    payload: ItemCreate, service: ItemsService = Depends(get_items_service)
):
    return success(await service.create_item(payload))


@router.get("/", response_model=StandardResponse[Page[ItemOut]])
async def list_items(
    params: Params = Depends(), service: ItemsService = Depends(get_items_service)
):
    items = await service.list_items(params)
    return success(items)


@router.get("/{item_id}", response_model=StandardResponse[ItemOut])
async def read_item(item_id: int, service: ItemsService = Depends(get_items_service)):
    obj = await service.get_item(item_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Item not found")
    return success(obj)


@router.put("/{item_id}", response_model=StandardResponse[ItemOut])
async def update_item(
    item_id: int,
    payload: ItemUpdate,
    service: ItemsService = Depends(get_items_service),
):
    obj = await service.update_item(item_id, payload)
    if not obj:
        raise HTTPException(status_code=404, detail="Item not found")
    return success(obj)
