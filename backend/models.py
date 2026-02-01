from sqlalchemy import Column, String, Text, Numeric, DateTime, ForeignKey, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector
from database import Base
import uuid

class MenuItem(Base):
    __tablename__ = "menu_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    image_data = Column(Text, nullable=True)  # Base64 string
    category = Column(String(50), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class MenuEmbedding(Base):
    __tablename__ = "menu_embeddings"

    item_id = Column(UUID(as_uuid=True), ForeignKey("menu_items.id", ondelete="CASCADE"), primary_key=True)
    embedding = Column(Vector(384), nullable=False) # Dimension for MiniLM-L6-v2
    content_chunk = Column(Text, nullable=False)
