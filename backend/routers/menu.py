from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from typing import List
from database import get_db
from models import MenuItem, MenuEmbedding
from schemas import MenuItemCreate, MenuItemResponse
from services.rag_service import RAGService

router = APIRouter(prefix="/menu", tags=["menu"])

@router.get("/", response_model=List[MenuItemResponse])
async def get_menu(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(MenuItem))
    return result.scalars().all()

@router.post("/", response_model=MenuItemResponse)
async def create_menu_item(item: MenuItemCreate, db: AsyncSession = Depends(get_db)):
    # 1. Save Menu Item
    new_item = MenuItem(**item.model_dump())
    db.add(new_item)
    await db.flush() # Get the ID

    # 2. Generate Embedding
    content_chunk = f"Name: {item.name}. Description: {item.description}. Category: {item.category or 'General'}."
    embedding_vector = RAGService.generate_embedding(content_chunk)
    
    # 3. Save Embedding
    new_embedding = MenuEmbedding(
        item_id=new_item.id,
        embedding=embedding_vector,
        content_chunk=content_chunk
    )
    db.add(new_embedding)
    
    await db.commit()
    await db.refresh(new_item)
    return new_item

@router.put("/{item_id}", response_model=MenuItemResponse)
async def update_menu_item(item_id: str, item_update: MenuItemCreate, db: AsyncSession = Depends(get_db)):
    # 1. Check if item exists
    query = select(MenuItem).where(MenuItem.id == item_id)
    result = await db.execute(query)
    db_item = result.scalar_one_or_none()
    
    if not db_item:
        raise HTTPException(status_code=404, detail="Menu item not found")
    
    # 2. Update fields
    for key, value in item_update.model_dump().items():
        setattr(db_item, key, value)
    
    # 3. Regenerate Embedding (since description/name might have changed)
    content_chunk = f"Name: {item_update.name}. Description: {item_update.description}. Category: {item_update.category or 'General'}."
    embedding_vector = RAGService.generate_embedding(content_chunk)
    
    # 4. Update Embedding Record
    # Check if embedding exists
    emb_query = select(MenuEmbedding).where(MenuEmbedding.item_id == item_id)
    emb_result = await db.execute(emb_query)
    db_embedding = emb_result.scalar_one_or_none()
    
    if db_embedding:
        db_embedding.embedding = embedding_vector
        db_embedding.content_chunk = content_chunk
    else:
        # Create if missing for some reason
        new_embedding = MenuEmbedding(
            item_id=item_id,
            embedding=embedding_vector,
            content_chunk=content_chunk
        )
        db.add(new_embedding)

    await db.commit()
    await db.refresh(db_item)
    return db_item

@router.delete("/{item_id}")
async def delete_menu_item(item_id: str, db: AsyncSession = Depends(get_db)):
    query = delete(MenuItem).where(MenuItem.id == item_id)
    await db.execute(query)
    await db.commit()
    return {"status": "success"}
