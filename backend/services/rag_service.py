import os
import numpy as np
from sentence_transformers import SentenceTransformer
from openai import AsyncOpenAI
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import List, AsyncGenerator

# Load embedding model (cached globally)
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

# LM Studio Client
LM_STUDIO_URL = os.getenv("LM_STUDIO_URL", "http://host.docker.internal:1234/v1")
client = AsyncOpenAI(base_url=LM_STUDIO_URL, api_key="lm-studio")

class RAGService:
    @staticmethod
    def generate_embedding(content: str) -> List[float]:
        embedding = model.encode(content)
        return embedding.tolist()

    @staticmethod
    async def find_similar_context(session: AsyncSession, query_vector: List[float], limit: int = 3) -> str:
        # Perform cosine similarity search using pgvector
        query = text("""
            SELECT content_chunk 
            FROM menu_embeddings 
            ORDER BY embedding <=> :vector 
            LIMIT :limit
        """)
        
        result = await session.execute(query, {"vector": str(query_vector), "limit": limit})
        chunks = [row[0] for row in result.fetchall()]
        return "\n".join(chunks)

    @staticmethod
    async def chat_stream(context: str, question: str) -> AsyncGenerator[str, None]:
        system_prompt = (
            "You are a helpful restaurant concierge. Answer the customer's question based ONLY on the menu context provided below. "
            "If the answer is not in the context, say you don't know and suggest they ask about the dishes listed.\n\n"
            f"Context:\n{context}"
        )

        response = await client.chat.completions.create(
            model="qwen3-vl-4b-instruct-abliterated-v2", # Model name is ignored by LM Studio usually
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": question}
            ],
            stream=True
        )

        async for chunk in response:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
