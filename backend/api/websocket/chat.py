"""
WebSocket chat handler for real-time RAG conversations.
"""
import json
import uuid
import asyncio
from typing import Dict, Set, Optional
from fastapi import WebSocket, WebSocketDisconnect, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import AsyncSessionLocal
from core.db_utils import ChatSessionRepository, ChatMessageRepository, ProfileRepository
from core.ai_providers import get_provider_manager
from core.retrieval import get_vector_retriever
import logging

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections."""
    
    def __init__(self):
        # Active connections: {session_id: {user_id: websocket}}
        self.active_connections: Dict[str, Dict[str, WebSocket]] = {}
        # Typing indicators: {session_id: {user_id: timestamp}}
        self.typing_indicators: Dict[str, Dict[str, float]] = {}
    
    async def connect(self, websocket: WebSocket, session_id: str, user_id: str = "anonymous"):
        """Accept a WebSocket connection."""
        await websocket.accept()
        
        if session_id not in self.active_connections:
            self.active_connections[session_id] = {}
        
        self.active_connections[session_id][user_id] = websocket
        
        # Notify other users in the session
        await self.broadcast_to_session(
            session_id,
            {
                "type": "user_joined",
                "user_id": user_id,
                "session_id": session_id,
                "timestamp": asyncio.get_event_loop().time()
            },
            exclude_user=user_id
        )
        
        logger.info(f"User {user_id} connected to session {session_id}")
    
    def disconnect(self, session_id: str, user_id: str):
        """Remove a WebSocket connection."""
        if session_id in self.active_connections:
            if user_id in self.active_connections[session_id]:
                del self.active_connections[session_id][user_id]
                
                # Clean up empty sessions
                if not self.active_connections[session_id]:
                    del self.active_connections[session_id]
        
        # Clean up typing indicators
        if session_id in self.typing_indicators:
            if user_id in self.typing_indicators[session_id]:
                del self.typing_indicators[session_id][user_id]
        
        logger.info(f"User {user_id} disconnected from session {session_id}")
    
    async def send_personal_message(self, websocket: WebSocket, message: dict):
        """Send a message to a specific WebSocket."""
        try:
            await websocket.send_text(json.dumps(message))
        except Exception as e:
            logger.error(f"Error sending message: {e}")
    
    async def broadcast_to_session(self, session_id: str, message: dict, exclude_user: Optional[str] = None):
        """Broadcast a message to all users in a session."""
        if session_id not in self.active_connections:
            return
        
        for user_id, websocket in self.active_connections[session_id].items():
            if exclude_user and user_id == exclude_user:
                continue
            
            await self.send_personal_message(websocket, message)
    
    async def send_typing_indicator(self, session_id: str, user_id: str, is_typing: bool):
        """Send typing indicator to session."""
        import time
        current_time = time.time()
        
        if session_id not in self.typing_indicators:
            self.typing_indicators[session_id] = {}
        
        if is_typing:
            self.typing_indicators[session_id][user_id] = current_time
        else:
            self.typing_indicators[session_id].pop(user_id, None)
        
        await self.broadcast_to_session(
            session_id,
            {
                "type": "typing_indicator",
                "user_id": user_id,
                "typing": is_typing,
                "session_id": session_id,
                "timestamp": current_time
            },
            exclude_user=user_id
        )


# Global connection manager
manager = ConnectionManager()


async def websocket_endpoint(websocket: WebSocket, session_id: str, user_id: str = "anonymous"):
    """WebSocket endpoint for chat sessions."""
    await manager.connect(websocket, session_id, user_id)
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Handle different message types
            message_type = message.get("type")
            
            if message_type == "join_session":
                await handle_join_session(websocket, session_id, user_id, message)
            elif message_type == "send_message":
                await handle_send_message(websocket, session_id, user_id, message)
            elif message_type == "typing":
                await handle_typing(websocket, session_id, user_id, message)
            else:
                await manager.send_personal_message(
                    websocket,
                    {
                        "type": "error",
                        "message": f"Unknown message type: {message_type}",
                        "timestamp": asyncio.get_event_loop().time()
                    }
                )
    
    except WebSocketDisconnect:
        manager.disconnect(session_id, user_id)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(session_id, user_id)


async def handle_join_session(websocket: WebSocket, session_id: str, user_id: str, message: dict):
    """Handle join session message."""
    try:
        session_uuid = uuid.UUID(session_id)
    except ValueError:
        await manager.send_personal_message(
            websocket,
            {
                "type": "error",
                "message": "Invalid session ID format",
                "timestamp": asyncio.get_event_loop().time()
            }
        )
        return
    
    # Validate session exists
    async with AsyncSessionLocal() as db:
        session_repo = ChatSessionRepository(db)
        session = await session_repo.get_by_id(session_uuid)
        
        if not session:
            await manager.send_personal_message(
                websocket,
                {
                    "type": "error",
                    "message": f"Session {session_id} not found",
                    "timestamp": asyncio.get_event_loop().time()
                }
            )
            return
        
        # Send session info
        await manager.send_personal_message(
            websocket,
            {
                "type": "session_joined",
                "session_id": session_id,
                "session_name": session.session_name,
                "profile_id": session.profile_id,
                "timestamp": asyncio.get_event_loop().time()
            }
        )


async def handle_send_message(websocket: WebSocket, session_id: str, user_id: str, message: dict):
    """Handle send message."""
    try:
        session_uuid = uuid.UUID(session_id)
    except ValueError:
        await manager.send_personal_message(
            websocket,
            {
                "type": "error",
                "message": "Invalid session ID format",
                "timestamp": asyncio.get_event_loop().time()
            }
        )
        return
    
    user_message = message.get("message", "").strip()
    profile_id = message.get("profile_id")
    
    if not user_message:
        await manager.send_personal_message(
            websocket,
            {
                "type": "error",
                "message": "Message cannot be empty",
                "timestamp": asyncio.get_event_loop().time()
            }
        )
        return
    
    if not profile_id:
        await manager.send_personal_message(
            websocket,
            {
                "type": "error",
                "message": "Profile ID is required",
                "timestamp": asyncio.get_event_loop().time()
            }
        )
        return
    
    async with AsyncSessionLocal() as db:
        try:
            # Validate session and profile
            session_repo = ChatSessionRepository(db)
            session = await session_repo.get_by_id(session_uuid)
            
            if not session:
                await manager.send_personal_message(
                    websocket,
                    {
                        "type": "error",
                        "message": f"Session {session_id} not found",
                        "timestamp": asyncio.get_event_loop().time()
                    }
                )
                return
            
            profile_repo = ProfileRepository(db)
            profile = await profile_repo.get_by_id(profile_id)
            
            if not profile:
                await manager.send_personal_message(
                    websocket,
                    {
                        "type": "error",
                        "message": f"Profile {profile_id} not found",
                        "timestamp": asyncio.get_event_loop().time()
                    }
                )
                return
            
            # Save user message
            message_repo = ChatMessageRepository(db)
            user_msg = await message_repo.create(
                session_id=session_uuid,
                role="user",
                content=user_message
            )
            
            # Broadcast user message to all users in session
            await manager.broadcast_to_session(
                session_id,
                {
                    "type": "message_received",
                    "id": str(user_msg.id),
                    "role": "user",
                    "content": user_message,
                    "context_chunks": [],
                    "timestamp": user_msg.timestamp.isoformat(),
                    "user_id": user_id
                }
            )
            
            # Get context chunks using RAG
            vector_retriever = get_vector_retriever()
            context_chunks = await vector_retriever.get_context_chunks(
                session=db,
                query=user_message,
                profile_id=profile_id,
                max_chunks=profile.settings.get("max_context_chunks", 5),
                similarity_threshold=0.7
            )
            
            # Generate AI response with streaming
            provider_manager = get_provider_manager()
            
            # Build context for the prompt
            context_text = "\n\n".join([
                f"Document: {chunk.get('document_filename', 'Unknown')}\nContent: {chunk['content']}"
                for chunk in context_chunks
            ])
            
            # Format prompt with context
            formatted_prompt = profile.prompt.format(
                context=context_text,
                question=user_message
            )
            
            # Send typing indicator
            await manager.broadcast_to_session(
                session_id,
                {
                    "type": "ai_typing",
                    "session_id": session_id,
                    "timestamp": asyncio.get_event_loop().time()
                }
            )
            
            # Stream AI response
            ai_response_content = ""
            async for chunk in provider_manager.stream_response(
                provider_name=profile.provider,
                model=profile.model,
                prompt=formatted_prompt,
                temperature=profile.settings.get("temperature", 0.7),
                max_tokens=profile.settings.get("max_tokens", 1000)
            ):
                ai_response_content += chunk
                
                # Send streaming chunk to all users in session
                await manager.broadcast_to_session(
                    session_id,
                    {
                        "type": "ai_streaming",
                        "chunk": chunk,
                        "session_id": session_id,
                        "timestamp": asyncio.get_event_loop().time()
                    }
                )
            
            # Save complete AI response
            ai_message = await message_repo.create(
                session_id=session_uuid,
                role="assistant",
                content=ai_response_content,
                context_chunks=context_chunks
            )
            
            # Send final AI message
            await manager.broadcast_to_session(
                session_id,
                {
                    "type": "ai_message_complete",
                    "id": str(ai_message.id),
                    "role": "assistant",
                    "content": ai_response_content,
                    "context_chunks": context_chunks,
                    "timestamp": ai_message.timestamp.isoformat(),
                    "session_id": session_id
                }
            )
            
        except Exception as e:
            logger.error(f"Error handling message: {e}")
            await manager.send_personal_message(
                websocket,
                {
                    "type": "error",
                    "message": f"Error processing message: {str(e)}",
                    "timestamp": asyncio.get_event_loop().time()
                }
            )


async def handle_typing(websocket: WebSocket, session_id: str, user_id: str, message: dict):
    """Handle typing indicator."""
    is_typing = message.get("typing", False)
    await manager.send_typing_indicator(session_id, user_id, is_typing)


# Additional WebSocket utilities
async def notify_session_created(session_id: str, session_name: str, profile_id: int):
    """Notify all connected users about a new session."""
    await manager.broadcast_to_session(
        session_id,
        {
            "type": "session_created",
            "session_id": session_id,
            "session_name": session_name,
            "profile_id": profile_id,
            "timestamp": asyncio.get_event_loop().time()
        }
    )


async def get_active_sessions() -> Dict[str, int]:
    """Get count of active connections per session."""
    return {
        session_id: len(connections)
        for session_id, connections in manager.active_connections.items()
    }


async def get_session_users(session_id: str) -> Set[str]:
    """Get list of users in a session."""
    if session_id in manager.active_connections:
        return set(manager.active_connections[session_id].keys())
    return set()
