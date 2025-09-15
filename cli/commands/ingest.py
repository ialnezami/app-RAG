"""
Document ingestion commands.
"""

import asyncio
import click
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn
from rich.table import Table

from core.database import AsyncSessionLocal
from core.db_utils import DocumentRepository, ProfileRepository
from utils.file_processing import FileProcessor

console = Console()

@click.group()
def ingest_group():
    """Document ingestion commands."""
    pass

@ingest_group.command()
@click.argument('profile_id', type=int)
@click.argument('file_path', type=click.Path(exists=True))
@click.option('--chunk-size', type=int, default=1000, help='Chunk size for text processing')
@click.option('--chunk-overlap', type=int, default=200, help='Overlap between chunks')
@click.option('--force', '-f', is_flag=True, help='Force reprocessing if document exists')
def ingest(profile_id: int, file_path: str, chunk_size: int, chunk_overlap: int, force: bool):
    """Ingest a single document."""
    file_path = Path(file_path)
    console.print(Panel.fit(f"�� Ingesting Document: {file_path.name}", style="bold blue"))
    
    async def _ingest_document():
        async with AsyncSessionLocal() as db:
            # Validate profile
            profile_repo = ProfileRepository(db)
            profile = await profile_repo.get_by_id(profile_id)
            if not profile:
                console.print(f"[red]Error: Profile with ID {profile_id} not found[/red]")
                raise click.Abort()
            
            # Check if document already exists
            doc_repo = DocumentRepository(db)
            existing_docs = await doc_repo.get_by_filename(file_path.name)
            if existing_docs and not force:
                console.print(f"[yellow]Document '{file_path.name}' already exists. Use --force to reprocess.[/yellow]")
                return
            
            # Initialize file processor
            processor = FileProcessor()
            
            with Progress(
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                TimeRemainingColumn(),
                console=console
            ) as progress:
                # Upload task
                upload_task = progress.add_task("Uploading document...", total=100)
                
                try:
                    # Upload document
                    document = await processor.upload_document(
                        file_path=file_path,
                        profile_id=profile_id,
                        progress_callback=lambda p: progress.update(upload_task, completed=p)
                    )
                    
                    progress.update(upload_task, description="✅ Document uploaded")
                    
                    # Processing task
                    process_task = progress.add_task("Processing document...", total=100)
                    
                    # Process document
                    await processor.process_document(
                        document_id=document.id,
                        profile_id=profile_id,
                        chunk_size=chunk_size,
                        chunk_overlap=chunk_overlap,
                        progress_callback=lambda p: progress.update(process_task, completed=p)
                    )
                    
                    progress.update(process_task, description="✅ Document processed")
                    
                    console.print(f"\n[bold green]Document '{file_path.name}' ingested successfully![/bold green]")
                    
                    # Show document info
                    info_table = Table(show_header=False, box=None)
                    info_table.add_column("Field", style="cyan", width=15)
                    info_table.add_column("Value", style="green")
                    
                    info_table.add_row("Document ID", document.id)
                    info_table.add_row("Filename", document.original_filename)
                    info_table.add_row("Size", f"{document.file_size / 1024 / 1024:.2f} MB" if document.file_size else "Unknown")
                    info_table.add_row("Profile", profile.name)
                    info_table.add_row("Status", "✅ Processed")
                    
                    console.print(info_table)
                    
                except Exception as e:
                    progress.update(upload_task, description=f"❌ Upload failed: {str(e)}")
                    console.print(f"\n[red]Error: {str(e)}[/red]")
                    raise click.Abort()
    
    asyncio.run(_ingest_document())

@ingest_group.command()
@click.argument('profile_id', type=int)
@click.argument('folder_path', type=click.Path(exists=True, file_okay=False))
@click.option('--recursive', '-r', is_flag=True, help='Process subdirectories recursively')
@click.option('--pattern', default='*', help='File pattern to match (e.g., "*.pdf")')
@click.option('--chunk-size', type=int, default=1000, help='Chunk size for text processing')
@click.option('--chunk-overlap', type=int, default=200, help='Overlap between chunks')
@click.option('--force', '-f', is_flag=True, help='Force reprocessing of existing documents')
@click.option('--max-files', type=int, help='Maximum number of files to process')
def ingest_folder(profile_id: int, folder_path: str, recursive: bool, pattern: str, chunk_size: int, chunk_overlap: int, force: bool, max_files: int):
    """Ingest all documents in a folder."""
    folder_path = Path(folder_path)
    console.print(Panel.fit(f"📁 Ingesting Folder: {folder_path.name}", style="bold blue"))
    
    async def _ingest_folder():
        async with AsyncSessionLocal() as db:
            # Validate profile
            profile_repo = ProfileRepository(db)
            profile = await profile_repo.get_by_id(profile_id)
            if not profile:
                console.print(f"[red]Error: Profile with ID {profile_id} not found[/red]")
                raise click.Abort()
            
            # Find files
            if recursive:
                files = list(folder_path.rglob(pattern))
            else:
                files = list(folder_path.glob(pattern))
            
            # Filter files
            supported_extensions = {'.pdf', '.doc', '.docx', '.txt', '.md'}
            files = [f for f in files if f.is_file() and f.suffix.lower() in supported_extensions]
            
            if max_files:
                files = files[:max_files]
            
            if not files:
                console.print("[yellow]No supported files found in the specified folder[/yellow]")
                return
            
            console.print(f"[dim]Found {len(files)} files to process[/dim]")
            
            # Initialize file processor
            processor = FileProcessor()
            
            with Progress(
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                TimeRemainingColumn(),
                console=console
            ) as progress:
                main_task = progress.add_task("Processing files...", total=len(files))
                
                successful = 0
                failed = 0
                
                for i, file_path in enumerate(files):
                    try:
                        progress.update(main_task, description=f"Processing {file_path.name}...")
                        
                        # Check if document already exists
                        doc_repo = DocumentRepository(db)
                        existing_docs = await doc_repo.get_by_filename(file_path.name)
                        if existing_docs and not force:
                            console.print(f"[yellow]Skipping '{file_path.name}' (already exists)[/yellow]")
                            continue
                        
                        # Upload document
                        document = await processor.upload_document(
                            file_path=file_path,
                            profile_id=profile_id
                        )
                        
                        # Process document
                        await processor.process_document(
                            document_id=document.id,
                            profile_id=profile_id,
                            chunk_size=chunk_size,
                            chunk_overlap=chunk_overlap
                        )
                        
                        successful += 1
                        
                    except Exception as e:
                        console.print(f"[red]Failed to process '{file_path.name}': {str(e)}[/red]")
                        failed += 1
                    
                    progress.update(main_task, completed=i + 1)
                
                progress.update(main_task, description="✅ Processing complete")
                
                # Summary
                console.print(f"\n[bold green]Folder ingestion complete![/bold green]")
                
                summary_table = Table(show_header=True, header_style="bold magenta")
                summary_table.add_column("Status", style="cyan")
                summary_table.add_column("Count", style="green")
                
                summary_table.add_row("✅ Successful", str(successful))
                summary_table.add_row("❌ Failed", str(failed))
                summary_table.add_row("📁 Total Files", str(len(files)))
                
                console.print(summary_table)
    
    asyncio.run(_ingest_folder())

@ingest_group.command()
@click.argument('profile_id', type=int)
@click.argument('url')
@click.option('--chunk-size', type=int, default=1000, help='Chunk size for text processing')
@click.option('--chunk-overlap', type=int, default=200, help='Overlap between chunks')
def ingest_url(profile_id: int, url: str, chunk_size: int, chunk_overlap: int):
    """Ingest content from a URL."""
    console.print(Panel.fit(f"🌐 Ingesting URL: {url}", style="bold blue"))
    
    async def _ingest_url():
        async with AsyncSessionLocal() as db:
            # Validate profile
            profile_repo = ProfileRepository(db)
            profile = await profile_repo.get_by_id(profile_id)
            if not profile:
                console.print(f"[red]Error: Profile with ID {profile_id} not found[/red]")
                raise click.Abort()
            
            # Initialize file processor
            processor = FileProcessor()
            
            with Progress(
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                TimeRemainingColumn(),
                console=console
            ) as progress:
                # Download task
                download_task = progress.add_task("Downloading content...", total=100)
                
                try:
                    # Download and process URL content
                    document = await processor.ingest_url(
                        url=url,
                        profile_id=profile_id,
                        chunk_size=chunk_size,
                        chunk_overlap=chunk_overlap,
                        progress_callback=lambda p: progress.update(download_task, completed=p)
                    )
                    
                    progress.update(download_task, description="✅ Content ingested")
                    
                    console.print(f"\n[bold green]URL content ingested successfully![/bold green]")
                    
                    # Show document info
                    info_table = Table(show_header=False, box=None)
                    info_table.add_column("Field", style="cyan", width=15)
                    info_table.add_column("Value", style="green")
                    
                    info_table.add_row("Document ID", document.id)
                    info_table.add_row("Source URL", url)
                    info_table.add_row("Profile", profile.name)
                    info_table.add_row("Status", "✅ Processed")
                    
                    console.print(info_table)
                    
                except Exception as e:
                    progress.update(download_task, description=f"❌ Ingestion failed: {str(e)}")
                    console.print(f"\n[red]Error: {str(e)}[/red]")
                    raise click.Abort()
    
    asyncio.run(_ingest_url())
