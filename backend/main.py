from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from database import engine, Base
from routers import menu, chat
import asyncio

app = FastAPI(title="Smart Menu API")

# CORS Setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(menu.router)
app.include_router(chat.router)

@app.on_event("startup")
async def startup():
    # Create tables if they don't exist
    async with engine.begin() as conn:
        # Enable pgvector extension
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        await conn.run_sync(Base.metadata.create_all)

@app.get("/")
async def root():
    return {"message": "Welcome to Smart Menu API"}

