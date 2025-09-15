"""
Database initialization commands.
"""

import asyncio
import click
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from core.database import init_database, check_db_health
from core.init_db import create_default_profiles
from core.db_utils import ProfileRepository
from core.database import AsyncSessionLocal

console = Console()

@click.group()
def init_group():
    """Database initialization commands."""
    pass

@init_group.command()
@click.option('--force', '-f', is_flag=True, help='Force reinitialization even if database exists')
@click.option('--drop-tables', is_flag=True, help='Drop existing tables before initialization')
def init_db(force: bool, drop_tables: bool):
    """Initialize the database schema."""
    console.print(Panel.fit("🗄️ Initializing Database", style="bold blue"))
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Initializing database...", total=None)
        
        try:
            result = asyncio.run(init_database(force=force, drop_tables=drop_tables))
            progress.update(task, description="✅ Database initialized successfully")
            
            console.print("\n[bold green]Database Initialization Complete![/bold green]")
            
            # Show database info
            info_table = Table(show_header=True, header_style="bold magenta")
            info_table.add_column("Component", style="cyan")
            info_table.add_column("Status", style="green")
            
            info_table.add_row("Tables Created", "✅ Success")
            info_table.add_row("Indexes Created", "✅ Success")
            info_table.add_row("Extensions Enabled", "✅ pgvector")
            info_table.add_row("Schema Version", "1.0.0")
            
            console.print(info_table)
            
        except Exception as e:
            progress.update(task, description=f"❌ Database initialization failed: {str(e)}")
            console.print(f"\n[red]Error: {str(e)}[/red]")
            raise click.Abort()

@init_group.command()
@click.option('--force', '-f', is_flag=True, help='Force recreation of default profiles')
def init_profiles(force: bool):
    """Create default AI profiles."""
    console.print(Panel.fit("🤖 Creating Default Profiles", style="bold blue"))
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Creating default profiles...", total=None)
        
        try:
            profiles_created = asyncio.run(create_default_profiles(force=force))
            progress.update(task, description=f"✅ Created {len(profiles_created)} default profiles")
            
            console.print("\n[bold green]Default Profiles Created![/bold green]")
            
            # Show created profiles
            profiles_table = Table(show_header=True, header_style="bold magenta")
            profiles_table.add_column("ID", style="cyan")
            profiles_table.add_column("Name", style="green")
            profiles_table.add_column("Provider", style="yellow")
            profiles_table.add_column("Model", style="blue")
            
            for profile in profiles_created:
                profiles_table.add_row(
                    str(profile.id),
                    profile.name,
                    profile.provider,
                    profile.model
                )
            
            console.print(profiles_table)
            
        except Exception as e:
            progress.update(task, description=f"❌ Profile creation failed: {str(e)}")
            console.print(f"\n[red]Error: {str(e)}[/red]")
            raise click.Abort()

@init_group.command()
@click.option('--all', '-a', is_flag=True, help='Initialize both database and profiles')
@click.option('--force', '-f', is_flag=True, help='Force reinitialization')
def setup(all: bool, force: bool):
    """Complete system setup (database + profiles)."""
    console.print(Panel.fit("🚀 Complete System Setup", style="bold blue"))
    
    try:
        # Initialize database
        console.print("\n[bold]Step 1: Database Initialization[/bold]")
        init_db.callback(force=force, drop_tables=False)
        
        # Create default profiles
        console.print("\n[bold]Step 2: Default Profiles[/bold]")
        init_profiles.callback(force=force)
        
        console.print("\n[bold green]🎉 System Setup Complete![/bold green]")
        console.print("[dim]You can now start using the RAG application.[/dim]")
        
    except Exception as e:
        console.print(f"\n[red]Setup failed: {str(e)}[/red]")
        raise click.Abort()
