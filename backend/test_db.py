"""
Test script to verify database setup and models.
"""
import asyncio
import os
from core.database import get_db, check_db_health, init_db
from core.models import Profile, Document, DocumentChunk, ChatSession, ChatMessage
from core.db_utils import ProfileRepository, DocumentRepository


async def test_database():
    """Test database functionality."""
    print("🧪 Testing database setup...")
    
    # Test connection
    if not await check_db_health():
        print("❌ Database connection failed")
        return False
    
    print("✅ Database connection successful")
    
    # Test models
    async for session in get_db():
        try:
            # Test profile operations
            profile_repo = ProfileRepository(session)
            
            # Create a test profile
            test_profile = await profile_repo.create(
                name="Test Profile",
                description="Test profile for database testing",
                prompt="You are a test assistant.",
                provider="openai",
                model="gpt-4o-mini",
                settings={"test": True}
            )
            print(f"✅ Created test profile: {test_profile.id}")
            
            # Test document operations
            doc_repo = DocumentRepository(session)
            
            test_document = await doc_repo.create(
                filename="test.txt",
                original_filename="Test Document.txt",
                profile_id=test_profile.id,
                file_size=1000,
                mime_type="text/plain",
                metadata={"test": True}
            )
            print(f"✅ Created test document: {test_document.id}")
            
            # Test chunk operations
            from core.db_utils import DocumentChunkRepository
            chunk_repo = DocumentChunkRepository(session)
            
            test_chunk = await chunk_repo.create(
                document_id=test_document.id,
                profile_id=test_profile.id,
                chunk_index=0,
                content="This is a test chunk.",
                embedding=[0.1] * 1536,  # Mock embedding
                metadata={"test": True}
            )
            print(f"✅ Created test chunk: {test_chunk.id}")
            
            # Test chat session operations
            from core.db_utils import ChatSessionRepository
            session_repo = ChatSessionRepository(session)
            
            test_session = await session_repo.create(
                profile_id=test_profile.id,
                session_name="Test Chat Session"
            )
            print(f"✅ Created test session: {test_session.id}")
            
            # Test chat message operations
            from core.db_utils import ChatMessageRepository
            message_repo = ChatMessageRepository(session)
            
            test_message = await message_repo.create(
                session_id=test_session.id,
                role="user",
                content="Hello, this is a test message.",
                context_chunks=[{"chunk_id": str(test_chunk.id), "similarity": 0.9}]
            )
            print(f"✅ Created test message: {test_message.id}")
            
            # Clean up test data
            await session.execute("DELETE FROM chat_messages WHERE id = :id", {"id": test_message.id})
            await session.execute("DELETE FROM chat_sessions WHERE id = :id", {"id": test_session.id})
            await session.execute("DELETE FROM document_chunks WHERE id = :id", {"id": test_chunk.id})
            await session.execute("DELETE FROM documents WHERE id = :id", {"id": test_document.id})
            await session.execute("DELETE FROM profiles WHERE id = :id", {"id": test_profile.id})
            await session.commit()
            
            print("✅ Cleaned up test data")
            print("🎉 All database tests passed!")
            return True
            
        except Exception as e:
            print(f"❌ Database test failed: {e}")
            await session.rollback()
            return False
        finally:
            await session.close()


async def main():
    """Main test function."""
    success = await test_database()
    if not success:
        exit(1)


if __name__ == "__main__":
    asyncio.run(main())
