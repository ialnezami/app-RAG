#!/usr/bin/env python3
"""
RAG Application CLI Tool

A comprehensive command-line interface for managing the RAG application,
including database initialization, profile management, document ingestion,
and system configuration.
"""

import sys
import os
import asyncio
from pathlib import Path
from typing import Optional

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent.parent / 'backend'
sys.path.insert(0, str(backend_dir))

import click
from click import Context
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich.text import Text

from commands.init import init_group
from commands.profiles import profiles_group
from commands.ingest import ingest_group
from commands.documents import documents_group
from commands.reset import reset_group
from commands.config import config_group
from utils.file_processing import FileProcessor
from core.database import check_db_health
from core.ai_providers import get_provider_manager
from config.settings import get_settings

# Initialize rich console
console = Console()

# CLI version
__version__ = "1.0.0"

@click.group()
@click.version_option(version=__version__, prog_name="RAG CLI")
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--config', '-c', help='Path to configuration file')
@click.pass_context
def cli(ctx: Context, verbose: bool, config: Optional[str]):
    """
    RAG Application CLI Tool
    
    A comprehensive command-line interface for managing the RAG application.
    """
    ctx.ensure_object(dict)
    ctx.obj['verbose'] = verbose
    ctx.obj['config'] = config
    
    if verbose:
        console.print(f"[bold blue]RAG CLI v{__version__}[/bold blue]")
        console.print(f"[dim]Verbose mode enabled[/dim]")

@cli.command()
@click.pass_context
def status(ctx: Context):
    """Check system status and health."""
    console.print(Panel.fit("🔍 Checking System Status", style="bold blue"))
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        # Check database
        task1 = progress.add_task("Checking database connection...", total=None)
        try:
            db_healthy = asyncio.run(check_db_health())
            progress.update(task1, description="✅ Database connection: OK")
        except Exception as e:
            progress.update(task1, description=f"❌ Database connection: FAILED - {str(e)}")
            db_healthy = False
        
        # Check AI providers
        task2 = progress.add_task("Checking AI providers...", total=None)
        try:
            provider_manager = get_provider_manager()
            available_providers = provider_manager.get_available_providers()
            progress.update(task2, description=f"✅ AI providers: {len(available_providers)} available")
        except Exception as e:
            progress.update(task2, description=f"❌ AI providers: FAILED - {str(e)}")
            available_providers = []
        
        # Check settings
        task3 = progress.add_task("Checking configuration...", total=None)
        try:
            settings = get_settings()
            progress.update(task3, description="✅ Configuration: OK")
        except Exception as e:
            progress.update(task3, description=f"❌ Configuration: FAILED - {str(e)}")
    
    # Display status summary
    console.print("\n[bold]System Status Summary:[/bold]")
    
    status_table = Table(show_header=True, header_style="bold magenta")
    status_table.add_column("Component", style="cyan", no_wrap=True)
    status_table.add_column("Status", style="green")
    status_table.add_column("Details")
    
    status_table.add_row(
        "Database",
        "✅ Healthy" if db_healthy else "❌ Unhealthy",
        "PostgreSQL with pgvector"
    )
    
    status_table.add_row(
        "AI Providers",
        f"✅ {len(available_providers)} Available" if available_providers else "❌ None Available",
        ", ".join(available_providers) if available_providers else "No providers configured"
    )
    
    status_table.add_row(
        "Configuration",
        "✅ Valid",
        f"Environment: {get_settings().environment}"
    )
    
    console.print(status_table)
    
    # Overall status
    overall_status = "✅ System Healthy" if db_healthy and available_providers else "⚠️ System Issues Detected"
    console.print(f"\n[bold]{overall_status}[/bold]")

@cli.command()
@click.pass_context
def version(ctx: Context):
    """Show version information."""
    console.print(f"[bold blue]RAG CLI v{__version__}[/bold blue]")
    console.print(f"[dim]Backend API: v1.0.0[/dim]")
    console.print(f"[dim]Database: PostgreSQL with pgvector[/dim]")

# Add command groups
cli.add_command(init_group, name='init')
cli.add_command(profiles_group, name='profiles')
cli.add_command(ingest_group, name='ingest')
cli.add_command(documents_group, name='documents')
cli.add_command(reset_group, name='reset')
cli.add_command(config_group, name='config')

def main():
    """Main entry point for the CLI."""
    try:
        cli()
    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled by user[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n[red]Error: {str(e)}[/red]")
        if ctx.obj.get('verbose', False):
            console.print_exception()
        sys.exit(1)

if __name__ == '__main__':
    main()
