from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from services.rag_service import RAGService
import json

router = APIRouter(tags=["chat"])

@router.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket, db: AsyncSession = Depends(get_db)):
    await websocket.accept()
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message_data = json.loads(data)
            question = message_data.get("question", "")

            if not question:
                continue

            # 1. Embed the question
            query_vector = RAGService.generate_embedding(question)

            # 2. Find context
            context = await RAGService.find_similar_context(db, query_vector)

            # 3. Stream response
            async for chunk in RAGService.chat_stream(context, question):
                await websocket.send_text(chunk)
            
            # Send an indicator that streaming is finished (optional, or just wait for next msg)
            await websocket.send_text("[DONE]")

    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        print(f"Error: {e}")
        await websocket.close()
