"""
Database initialization script.
"""
import asyncio
import os
from sqlalchemy import text
from .database import engine, init_db, check_db_health
from .models import Profile


async def create_default_profiles():
    """Create default AI profiles."""
    from sqlalchemy.ext.asyncio import AsyncSession
    from sqlalchemy.orm import async_sessionmaker
    
    AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)
    
    async with AsyncSessionLocal() as session:
        # Check if profiles already exist
        result = await session.execute(text("SELECT COUNT(*) FROM profiles"))
        count = result.scalar()
        
        if count == 0:
            # Create default profiles
            default_profiles = [
                Profile(
                    name="General Assistant",
                    description="General purpose Q&A assistant",
                    prompt="You are a helpful assistant. Use the following context to answer questions accurately.\n\nContext: {context}\n\nQuestion: {question}\n\nAnswer:",
                    provider="openai",
                    model="gpt-4o-mini",
                    settings={
                        "max_context_chunks": 5,
                        "chunk_size": 1000,
                        "chunk_overlap": 200
                    }
                ),
                Profile(
                    name="Technical Expert",
                    description="Technical documentation assistant",
                    prompt="You are a technical expert. Provide detailed, accurate answers based on the documentation context.\n\nContext: {context}\n\nQuestion: {question}\n\nAnswer:",
                    provider="anthropic",
                    model="claude-3-sonnet",
                    settings={
                        "max_context_chunks": 8,
                        "chunk_size": 1500,
                        "chunk_overlap": 300
                    }
                )
            ]
            
            for profile in default_profiles:
                session.add(profile)
            
            await session.commit()
            print("✅ Default profiles created successfully")
        else:
            print(f"✅ {count} profiles already exist")


async def main():
    """Main initialization function."""
    print("🚀 Initializing database...")
    
    # Check database connection
    if not await check_db_health():
        print("❌ Database connection failed")
        return
    
    print("✅ Database connection successful")
    
    # Initialize database tables
    await init_db()
    print("✅ Database tables created")
    
    # Create default profiles
    await create_default_profiles()
    
    print("🎉 Database initialization complete!")


if __name__ == "__main__":
    asyncio.run(main())
