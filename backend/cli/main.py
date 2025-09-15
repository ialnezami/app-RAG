"""
Main CLI entry point for the RAG application.
"""
import asyncio
import click
from core.init_db import main as init_db_main
from core.database import check_db_health


@click.group()
def cli():
    """RAG Application CLI"""
    pass


@cli.command()
def init_db():
    """Initialize the database with tables and default data."""
    asyncio.run(init_db_main())


@cli.command()
def health():
    """Check database health."""
    async def check_health():
        is_healthy = await check_db_health()
        if is_healthy:
            click.echo("✅ Database is healthy")
        else:
            click.echo("❌ Database is not accessible")
            raise click.Abort()
    
    asyncio.run(check_health())


@cli.command()
@click.option('--profile-id', type=int, help='Profile ID to reset')
def reset_profile(profile_id):
    """Reset all data for a specific profile."""
    async def reset():
        from core.database import AsyncSessionLocal
        from core.db_utils import DocumentRepository, DocumentChunkRepository, ChatSessionRepository
        
        async with AsyncSessionLocal() as session:
            doc_repo = DocumentRepository(session)
            chunk_repo = DocumentChunkRepository(session)
            session_repo = ChatSessionRepository(session)
            
            # Delete all data for the profile
            await session.execute(
                "DELETE FROM chat_messages WHERE session_id IN "
                "(SELECT id FROM chat_sessions WHERE profile_id = :profile_id)",
                {"profile_id": profile_id}
            )
            await session.execute(
                "DELETE FROM chat_sessions WHERE profile_id = :profile_id",
                {"profile_id": profile_id}
            )
            await session.execute(
                "DELETE FROM document_chunks WHERE profile_id = :profile_id",
                {"profile_id": profile_id}
            )
            await session.execute(
                "DELETE FROM documents WHERE profile_id = :profile_id",
                {"profile_id": profile_id}
            )
            
            await session.commit()
            click.echo(f"✅ Reset all data for profile {profile_id}")
    
    asyncio.run(reset())


@cli.command()
def reset_all():
    """Reset all data (WARNING: This will delete all data)."""
    if not click.confirm("Are you sure you want to delete ALL data?"):
        click.echo("Operation cancelled")
        return
    
    async def reset():
        from core.database import AsyncSessionLocal
        
        async with AsyncSessionLocal() as session:
            # Delete all data
            await session.execute("DELETE FROM chat_messages")
            await session.execute("DELETE FROM chat_sessions")
            await session.execute("DELETE FROM document_chunks")
            await session.execute("DELETE FROM documents")
            await session.execute("DELETE FROM profiles")
            
            await session.commit()
            click.echo("✅ All data deleted")
    
    asyncio.run(reset())


if __name__ == "__main__":
    cli()
