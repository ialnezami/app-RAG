"""
Document management commands.
"""

import asyncio
import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Confirm

from core.database import AsyncSessionLocal
from core.db_utils import DocumentRepository, DocumentChunkRepository

console = Console()

@click.group()
def documents_group():
    """Document management commands."""
    pass

@documents_group.command()
@click.option('--profile', type=int, help='Filter by profile ID')
@click.option('--status', type=click.Choice(['processed', 'processing', 'failed']), help='Filter by processing status')
@click.option('--format', 'output_format', type=click.Choice(['table', 'json']), default='table', help='Output format')
def list(profile: int, status: str, output_format: str):
    """List all documents."""
    console.print(Panel.fit("📄 Document List", style="bold blue"))
    
    async def _list_documents():
        async with AsyncSessionLocal() as db:
            repo = DocumentRepository(db)
            documents = await repo.get_all()
            
            # Apply filters
            if profile:
                documents = [d for d in documents if d.profile_id == profile]
            
            if status:
                if status == 'processed':
                    documents = [d for d in documents if d.processed]
                elif status == 'processing':
                    documents = [d for d in documents if not d.processed]
                elif status == 'failed':
                    # This would need additional status tracking
                    documents = []
            
            if output_format == 'json':
                import json
                documents_data = [
                    {
                        'id': d.id,
                        'filename': d.original_filename,
                        'file_size': d.file_size,
                        'processed': d.processed,
                        'profile_id': d.profile_id,
                        'upload_date': d.upload_date.isoformat(),
                        'metadata': d.metadata
                    }
                    for d in documents
                ]
                console.print(json.dumps(documents_data, indent=2))
            else:
                if not documents:
                    console.print("[yellow]No documents found[/yellow]")
                    return
                
                table = Table(show_header=True, header_style="bold magenta")
                table.add_column("ID", style="cyan", width=8)
                table.add_column("Filename", style="green", width=25)
                table.add_column("Size", style="yellow", width=10)
                table.add_column("Profile", style="blue", width=8)
                table.add_column("Status", style="magenta", width=10)
                table.add_column("Uploaded", style="dim", width=12)
                
                for doc in documents:
                    size_str = f"{doc.file_size / 1024 / 1024:.1f} MB" if doc.file_size else "Unknown"
                    status_str = "✅ Processed" if doc.processed else "⏳ Processing"
                    
                    table.add_row(
                        doc.id[:8] + "...",
                        doc.original_filename[:25] + ("..." if len(doc.original_filename) > 25 else ""),
                        size_str,
                        str(doc.profile_id),
                        status_str,
                        doc.upload_date.strftime("%Y-%m-%d")
                    )
                
                console.print(table)
                console.print(f"\n[dim]Total: {len(documents)} documents[/dim]")
    
    asyncio.run(_list_documents())

@documents_group.command()
@click.argument('document_id')
def show(document_id: str):
    """Show detailed information about a document."""
    console.print(Panel.fit(f"👁️ Document Details: {document_id[:8]}...", style="bold blue"))
    
    async def _show_document():
        async with AsyncSessionLocal() as db:
            repo = DocumentRepository(db)
            chunk_repo = DocumentChunkRepository(db)
            
            document = await repo.get_by_id(document_id)
            if not document:
                console.print(f"[red]Error: Document with ID {document_id} not found[/red]")
                raise click.Abort()
            
            # Basic info table
            info_table = Table(show_header=False, box=None)
            info_table.add_column("Field", style="cyan", width=15)
            info_table.add_column("Value", style="green")
            
            info_table.add_row("ID", document.id)
            info_table.add_row("Filename", document.original_filename)
            info_table.add_row("Size", f"{document.file_size / 1024 / 1024:.2f} MB" if document.file_size else "Unknown")
            info_table.add_row("MIME Type", document.mime_type or "Unknown")
            info_table.add_row("Profile ID", str(document.profile_id))
            info_table.add_row("Processed", "✅ Yes" if document.processed else "⏳ No")
            info_table.add_row("Upload Date", document.upload_date.strftime("%Y-%m-%d %H:%M:%S"))
            
            console.print(info_table)
            
            # Metadata
            if document.metadata:
                console.print("\n[bold]Metadata:[/bold]")
                metadata_table = Table(show_header=True, header_style="bold magenta")
                metadata_table.add_column("Key", style="cyan")
                metadata_table.add_column("Value", style="green")
                
                for key, value in document.metadata.items():
                    metadata_table.add_row(key.replace('_', ' ').title(), str(value))
                
                console.print(metadata_table)
            
            # Chunks info
            chunks = await chunk_repo.get_by_document_id(document_id)
            console.print(f"\n[bold]Chunks: {len(chunks)} total[/bold]")
            
            if chunks:
                chunks_table = Table(show_header=True, header_style="bold magenta")
                chunks_table.add_column("Index", style="cyan", width=6)
                chunks_table.add_column("Size", style="yellow", width=8)
                chunks_table.add_column("Has Embedding", style="green", width=12)
                chunks_table.add_column("Preview", style="dim", width=30)
                
                for chunk in chunks[:10]:  # Show first 10 chunks
                    preview = chunk.content[:30] + "..." if len(chunk.content) > 30 else chunk.content
                    chunks_table.add_row(
                        str(chunk.chunk_index),
                        f"{len(chunk.content)} chars",
                        "✅ Yes" if chunk.has_embedding else "❌ No",
                        preview
                    )
                
                console.print(chunks_table)
                
                if len(chunks) > 10:
                    console.print(f"[dim]... and {len(chunks) - 10} more chunks[/dim]")
    
    asyncio.run(_show_document())

@documents_group.command()
@click.argument('document_id')
@click.option('--force', '-f', is_flag=True, help='Skip confirmation prompt')
def delete(document_id: str, force: bool):
    """Delete a document and all its chunks."""
    console.print(Panel.fit(f"🗑️ Deleting Document: {document_id[:8]}...", style="bold red"))
    
    async def _delete_document():
        async with AsyncSessionLocal() as db:
            repo = DocumentRepository(db)
            chunk_repo = DocumentChunkRepository(db)
            
            # Get existing document
            document = await repo.get_by_id(document_id)
            if not document:
                console.print(f"[red]Error: Document with ID {document_id} not found[/red]")
                raise click.Abort()
            
            # Get chunk count
            chunks = await chunk_repo.get_by_document_id(document_id)
            chunk_count = len(chunks)
            
            # Confirmation
            if not force:
                if not Confirm.ask(f"Are you sure you want to delete document '{document.original_filename}' and its {chunk_count} chunks?"):
                    console.print("[yellow]Operation cancelled[/yellow]")
                    return
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task("Deleting document...", total=None)
                
                try:
                    # Delete chunks first
                    if chunk_count > 0:
                        await chunk_repo.delete_by_document_id(document_id)
                    
                    # Delete document
                    await repo.delete(document_id)
                    
                    progress.update(task, description="✅ Document deleted successfully")
                    
                    console.print(f"\n[bold green]Document '{document.original_filename}' and {chunk_count} chunks deleted successfully![/bold green]")
                    
                except Exception as e:
                    progress.update(task, description=f"❌ Document deletion failed: {str(e)}")
                    console.print(f"\n[red]Error: {str(e)}[/red]")
                    raise click.Abort()
    
    asyncio.run(_delete_document())

@documents_group.command()
@click.argument('document_id')
@click.argument('profile_id', type=int)
@click.option('--chunk-size', type=int, default=1000, help='Chunk size for reprocessing')
@click.option('--chunk-overlap', type=int, default=200, help='Overlap between chunks')
def reprocess(document_id: str, profile_id: int, chunk_size: int, chunk_overlap: int):
    """Reprocess a document with new settings."""
    console.print(Panel.fit(f"🔄 Reprocessing Document: {document_id[:8]}...", style="bold blue"))
    
    async def _reprocess_document():
        async with AsyncSessionLocal() as db:
            repo = DocumentRepository(db)
            chunk_repo = DocumentChunkRepository(db)
            
            # Get existing document
            document = await repo.get_by_id(document_id)
            if not document:
                console.print(f"[red]Error: Document with ID {document_id} not found[/red]")
                raise click.Abort()
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                # Delete existing chunks
                task1 = progress.add_task("Deleting existing chunks...", total=None)
                chunks = await chunk_repo.get_by_document_id(document_id)
                await chunk_repo.delete_by_document_id(document_id)
                progress.update(task1, description=f"✅ Deleted {len(chunks)} existing chunks")
                
                # Reprocess document
                task2 = progress.add_task("Reprocessing document...", total=None)
                
                try:
                    from utils.file_processing import FileProcessor
                    processor = FileProcessor()
                    
                    await processor.process_document(
                        document_id=document_id,
                        profile_id=profile_id,
                        chunk_size=chunk_size,
                        chunk_overlap=chunk_overlap
                    )
                    
                    progress.update(task2, description="✅ Document reprocessed successfully")
                    
                    console.print(f"\n[bold green]Document '{document.original_filename}' reprocessed successfully![/bold green]")
                    
                except Exception as e:
                    progress.update(task2, description=f"❌ Reprocessing failed: {str(e)}")
                    console.print(f"\n[red]Error: {str(e)}[/red]")
                    raise click.Abort()
    
    asyncio.run(_reprocess_document())
