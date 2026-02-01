from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime
from decimal import Decimal

class MenuItemBase(BaseModel):
    name: str
    description: str
    price: Decimal
    image_data: Optional[str] = None
    category: Optional[str] = None

class MenuItemCreate(MenuItemBase):
    pass

class MenuItemResponse(MenuItemBase):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True

class ChatRequest(BaseModel):
    question: str

class ChatResponse(BaseModel):
    answer: str
