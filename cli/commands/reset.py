"""
Data reset commands.
"""

import asyncio
import click
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Confirm

from core.database import AsyncSessionLocal
from core.db_utils import (
    ProfileRepository, 
    DocumentRepository, 
    DocumentChunkRepository,
    ChatSessionRepository,
    ChatMessageRepository
)

console = Console()

@click.group()
def reset_group():
    """Data reset commands."""
    pass

@reset_group.command()
@click.argument('profile_id', type=int)
@click.option('--force', '-f', is_flag=True, help='Skip confirmation prompt')
def reset_profile(profile_id: int, force: bool):
    """Reset all data for a specific profile."""
    console.print(Panel.fit(f"🔄 Resetting Profile ID: {profile_id}", style="bold red"))
    
    async def _reset_profile():
        async with AsyncSessionLocal() as db:
            # Validate profile
            profile_repo = ProfileRepository(db)
            profile = await profile_repo.get_by_id(profile_id)
            if not profile:
                console.print(f"[red]Error: Profile with ID {profile_id} not found[/red]")
                raise click.Abort()
            
            # Get counts
            doc_repo = DocumentRepository(db)
            chunk_repo = DocumentChunkRepository(db)
            session_repo = ChatSessionRepository(db)
            message_repo = ChatMessageRepository(db)
            
            documents = await doc_repo.get_by_profile_id(profile_id)
            sessions = await session_repo.get_by_profile_id(profile_id)
            
            total_chunks = 0
            total_messages = 0
            
            for doc in documents:
                chunks = await chunk_repo.get_by_document_id(doc.id)
                total_chunks += len(chunks)
            
            for session in sessions:
                messages = await message_repo.get_by_session_id(session.id)
                total_messages += len(messages)
            
            # Confirmation
            if not force:
                console.print(f"[yellow]This will delete:[/yellow]")
                console.print(f"  • {len(documents)} documents")
                console.print(f"  • {total_chunks} document chunks")
                console.print(f"  • {len(sessions)} chat sessions")
                console.print(f"  • {total_messages} chat messages")
                console.print(f"  • Profile: {profile.name}")
                
                if not Confirm.ask(f"Are you sure you want to reset profile '{profile.name}'?"):
                    console.print("[yellow]Operation cancelled[/yellow]")
                    return
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                # Delete messages
                task1 = progress.add_task("Deleting chat messages...", total=None)
                for session in sessions:
                    await message_repo.delete_by_session_id(session.id)
                progress.update(task1, description=f"✅ Deleted {total_messages} chat messages")
                
                # Delete sessions
                task2 = progress.add_task("Deleting chat sessions...", total=None)
                for session in sessions:
                    await session_repo.delete(session.id)
                progress.update(task2, description=f"✅ Deleted {len(sessions)} chat sessions")
                
                # Delete chunks
                task3 = progress.add_task("Deleting document chunks...", total=None)
                for doc in documents:
                    await chunk_repo.delete_by_document_id(doc.id)
                progress.update(task3, description=f"✅ Deleted {total_chunks} document chunks")
                
                # Delete documents
                task4 = progress.add_task("Deleting documents...", total=None)
                for doc in documents:
                    await doc_repo.delete(doc.id)
                progress.update(task4, description=f"✅ Deleted {len(documents)} documents")
                
                console.print(f"\n[bold green]Profile '{profile.name}' reset successfully![/bold green]")
    
    asyncio.run(_reset_profile())

@reset_group.command()
@click.option('--force', '-f', is_flag=True, help='Skip confirmation prompt')
@click.option('--keep-profiles', is_flag=True, help='Keep profiles, only delete data')
def reset_all(force: bool, keep_profiles: bool):
    """Reset all data in the system."""
    console.print(Panel.fit("🗑️ Resetting All Data", style="bold red"))
    
    async def _reset_all():
        async with AsyncSessionLocal() as db:
            # Get counts
            doc_repo = DocumentRepository(db)
            chunk_repo = DocumentChunkRepository(db)
            session_repo = ChatSessionRepository(db)
            message_repo = ChatMessageRepository(db)
            profile_repo = ProfileRepository(db)
            
            documents = await doc_repo.get_all()
            sessions = await session_repo.get_all()
            profiles = await profile_repo.get_all()
            
            total_chunks = 0
            total_messages = 0
            
            for doc in documents:
                chunks = await chunk_repo.get_by_document_id(doc.id)
                total_chunks += len(chunks)
            
            for session in sessions:
                messages = await message_repo.get_by_session_id(session.id)
                total_messages += len(messages)
            
            # Confirmation
            if not force:
                console.print(f"[yellow]This will delete:[/yellow]")
                console.print(f"  • {len(documents)} documents")
                console.print(f"  • {total_chunks} document chunks")
                console.print(f"  • {len(sessions)} chat sessions")
                console.print(f"  • {total_messages} chat messages")
                
                if not keep_profiles:
                    console.print(f"  • {len(profiles)} profiles")
                
                if not Confirm.ask("Are you sure you want to reset ALL data?"):
                    console.print("[yellow]Operation cancelled[/yellow]")
                    return
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                # Delete messages
                task1 = progress.add_task("Deleting chat messages...", total=None)
                for session in sessions:
                    await message_repo.delete_by_session_id(session.id)
                progress.update(task1, description=f"✅ Deleted {total_messages} chat messages")
                
                # Delete sessions
                task2 = progress.add_task("Deleting chat sessions...", total=None)
                for session in sessions:
                    await session_repo.delete(session.id)
                progress.update(task2, description=f"✅ Deleted {len(sessions)} chat sessions")
                
                # Delete chunks
                task3 = progress.add_task("Deleting document chunks...", total=None)
                for doc in documents:
                    await chunk_repo.delete_by_document_id(doc.id)
                progress.update(task3, description=f"✅ Deleted {total_chunks} document chunks")
                
                # Delete documents
                task4 = progress.add_task("Deleting documents...", total=None)
                for doc in documents:
                    await doc_repo.delete(doc.id)
                progress.update(task4, description=f"✅ Deleted {len(documents)} documents")
                
                # Delete profiles (if not keeping them)
                if not keep_profiles:
                    task5 = progress.add_task("Deleting profiles...", total=None)
                    for profile in profiles:
                        await profile_repo.delete(profile.id)
                    progress.update(task5, description=f"✅ Deleted {len(profiles)} profiles")
                
                console.print(f"\n[bold green]All data reset successfully![/bold green]")
                
                if keep_profiles:
                    console.print(f"[dim]Profiles preserved: {len(profiles)} profiles[/dim]")
    
    asyncio.run(_reset_all())

@reset_group.command()
@click.option('--force', '-f', is_flag=True, help='Skip confirmation prompt')
def reset_database(force: bool):
    """Reset the entire database (drop and recreate all tables)."""
    console.print(Panel.fit("🗄️ Resetting Database", style="bold red"))
    
    async def _reset_database():
        # Confirmation
        if not force:
            if not Confirm.ask("Are you sure you want to reset the ENTIRE DATABASE? This will delete ALL data and recreate all tables."):
                console.print("[yellow]Operation cancelled[/yellow]")
                return
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Resetting database...", total=None)
            
            try:
                from core.database import init_database
                
                # Drop and recreate all tables
                await init_database(force=True, drop_tables=True)
                
                progress.update(task, description="✅ Database reset successfully")
                
                console.print(f"\n[bold green]Database reset successfully![/bold green]")
                console.print("[dim]All tables have been dropped and recreated.[/dim]")
                
            except Exception as e:
                progress.update(task, description=f"❌ Database reset failed: {str(e)}")
                console.print(f"\n[red]Error: {str(e)}[/red]")
                raise click.Abort()
    
    asyncio.run(_reset_database())
