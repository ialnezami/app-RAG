"""
Profile management commands.
"""

import asyncio
import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt, Confirm

from core.database import AsyncSessionLocal
from core.db_utils import ProfileRepository
from core.ai_providers import get_provider_manager
from config.config import load_config

console = Console()

@click.group()
def profiles_group():
    """Profile management commands."""
    pass

@profiles_group.command()
@click.option('--provider', help='Filter by provider')
@click.option('--format', 'output_format', type=click.Choice(['table', 'json']), default='table', help='Output format')
def list(provider: str, output_format: str):
    """List all profiles."""
    console.print(Panel.fit("📋 Profile List", style="bold blue"))
    
    async def _list_profiles():
        async with AsyncSessionLocal() as db:
            repo = ProfileRepository(db)
            profiles = await repo.get_all()
            
            if provider:
                profiles = [p for p in profiles if p.provider == provider]
            
            if output_format == 'json':
                import json
                profiles_data = [
                    {
                        'id': p.id,
                        'name': p.name,
                        'description': p.description,
                        'provider': p.provider,
                        'model': p.model,
                        'created_at': p.created_at.isoformat(),
                        'updated_at': p.updated_at.isoformat()
                    }
                    for p in profiles
                ]
                console.print(json.dumps(profiles_data, indent=2))
            else:
                if not profiles:
                    console.print("[yellow]No profiles found[/yellow]")
                    return
                
                table = Table(show_header=True, header_style="bold magenta")
                table.add_column("ID", style="cyan", width=4)
                table.add_column("Name", style="green", width=20)
                table.add_column("Provider", style="yellow", width=12)
                table.add_column("Model", style="blue", width=15)
                table.add_column("Description", style="dim", width=30)
                table.add_column("Created", style="dim", width=12)
                
                for profile in profiles:
                    table.add_row(
                        str(profile.id),
                        profile.name,
                        profile.provider,
                        profile.model,
                        profile.description or "No description",
                        profile.created_at.strftime("%Y-%m-%d")
                    )
                
                console.print(table)
                console.print(f"\n[dim]Total: {len(profiles)} profiles[/dim]")
    
    asyncio.run(_list_profiles())

@profiles_group.command()
@click.argument('name')
@click.option('--provider', required=True, help='AI provider (openai, anthropic, google)')
@click.option('--model', required=True, help='Model name')
@click.option('--description', help='Profile description')
@click.option('--prompt', help='Custom prompt template')
@click.option('--temperature', type=float, default=0.7, help='Temperature setting')
@click.option('--max-tokens', type=int, default=1000, help='Max tokens setting')
def create(name: str, provider: str, model: str, description: str, prompt: str, temperature: float, max_tokens: int):
    """Create a new profile."""
    console.print(Panel.fit(f"➕ Creating Profile: {name}", style="bold blue"))
    
    async def _create_profile():
        # Validate provider and model
        provider_manager = get_provider_manager()
        available_providers = provider_manager.get_available_providers()
        
        if provider not in available_providers:
            console.print(f"[red]Error: Provider '{provider}' not available. Available: {', '.join(available_providers)}[/red]")
            raise click.Abort()
        
        available_models = provider_manager.get_available_models(provider)
        if model not in available_models:
            console.print(f"[red]Error: Model '{model}' not available for provider '{provider}'. Available: {', '.join(available_models)}[/red]")
            raise click.Abort()
        
        # Default prompt if not provided
        if not prompt:
            prompt = """You are a helpful AI assistant. Use the following context to answer the user's question:

Context:
{context}

Question: {question}

Please provide a helpful and accurate response based on the context provided."""
        
        async with AsyncSessionLocal() as db:
            repo = ProfileRepository(db)
            
            profile_data = {
                'name': name,
                'description': description,
                'prompt': prompt,
                'provider': provider,
                'model': model,
                'settings': {
                    'temperature': temperature,
                    'max_tokens': max_tokens,
                    'max_context_chunks': 5
                }
            }
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task("Creating profile...", total=None)
                
                try:
                    profile = await repo.create(**profile_data)
                    progress.update(task, description="✅ Profile created successfully")
                    
                    console.print(f"\n[bold green]Profile '{name}' created successfully![/bold green]")
                    console.print(f"[dim]Profile ID: {profile.id}[/dim]")
                    
                except Exception as e:
                    progress.update(task, description=f"❌ Profile creation failed: {str(e)}")
                    console.print(f"\n[red]Error: {str(e)}[/red]")
                    raise click.Abort()
    
    asyncio.run(_create_profile())

@profiles_group.command()
@click.argument('profile_id', type=int)
@click.option('--name', help='Update profile name')
@click.option('--description', help='Update description')
@click.option('--prompt', help='Update prompt template')
@click.option('--provider', help='Update provider')
@click.option('--model', help='Update model')
@click.option('--temperature', type=float, help='Update temperature')
@click.option('--max-tokens', type=int, help='Update max tokens')
def update(profile_id: int, name: str, description: str, prompt: str, provider: str, model: str, temperature: float, max_tokens: int):
    """Update an existing profile."""
    console.print(Panel.fit(f"✏️ Updating Profile ID: {profile_id}", style="bold blue"))
    
    async def _update_profile():
        async with AsyncSessionLocal() as db:
            repo = ProfileRepository(db)
            
            # Get existing profile
            profile = await repo.get_by_id(profile_id)
            if not profile:
                console.print(f"[red]Error: Profile with ID {profile_id} not found[/red]")
                raise click.Abort()
            
            # Prepare update data
            update_data = {}
            if name is not None:
                update_data['name'] = name
            if description is not None:
                update_data['description'] = description
            if prompt is not None:
                update_data['prompt'] = prompt
            if provider is not None:
                update_data['provider'] = provider
            if model is not None:
                update_data['model'] = model
            
            # Update settings
            if temperature is not None or max_tokens is not None:
                settings = profile.settings.copy()
                if temperature is not None:
                    settings['temperature'] = temperature
                if max_tokens is not None:
                    settings['max_tokens'] = max_tokens
                update_data['settings'] = settings
            
            if not update_data:
                console.print("[yellow]No changes specified[/yellow]")
                return
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task("Updating profile...", total=None)
                
                try:
                    updated_profile = await repo.update(profile_id, **update_data)
                    progress.update(task, description="✅ Profile updated successfully")
                    
                    console.print(f"\n[bold green]Profile '{updated_profile.name}' updated successfully![/bold green]")
                    
                except Exception as e:
                    progress.update(task, description=f"❌ Profile update failed: {str(e)}")
                    console.print(f"\n[red]Error: {str(e)}[/red]")
                    raise click.Abort()
    
    asyncio.run(_update_profile())

@profiles_group.command()
@click.argument('profile_id', type=int)
@click.option('--force', '-f', is_flag=True, help='Skip confirmation prompt')
def delete(profile_id: int, force: bool):
    """Delete a profile."""
    console.print(Panel.fit(f"🗑️ Deleting Profile ID: {profile_id}", style="bold red"))
    
    async def _delete_profile():
        async with AsyncSessionLocal() as db:
            repo = ProfileRepository(db)
            
            # Get existing profile
            profile = await repo.get_by_id(profile_id)
            if not profile:
                console.print(f"[red]Error: Profile with ID {profile_id} not found[/red]")
                raise click.Abort()
            
            # Confirmation
            if not force:
                if not Confirm.ask(f"Are you sure you want to delete profile '{profile.name}'?"):
                    console.print("[yellow]Operation cancelled[/yellow]")
                    return
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task("Deleting profile...", total=None)
                
                try:
                    await repo.delete(profile_id)
                    progress.update(task, description="✅ Profile deleted successfully")
                    
                    console.print(f"\n[bold green]Profile '{profile.name}' deleted successfully![/bold green]")
                    
                except Exception as e:
                    progress.update(task, description=f"❌ Profile deletion failed: {str(e)}")
                    console.print(f"\n[red]Error: {str(e)}[/red]")
                    raise click.Abort()
    
    asyncio.run(_delete_profile())

@profiles_group.command()
@click.argument('profile_id', type=int)
def show(profile_id: int):
    """Show detailed information about a profile."""
    console.print(Panel.fit(f"👁️ Profile Details: ID {profile_id}", style="bold blue"))
    
    async def _show_profile():
        async with AsyncSessionLocal() as db:
            repo = ProfileRepository(db)
            
            profile = await repo.get_by_id(profile_id)
            if not profile:
                console.print(f"[red]Error: Profile with ID {profile_id} not found[/red]")
                raise click.Abort()
            
            # Basic info table
            info_table = Table(show_header=False, box=None)
            info_table.add_column("Field", style="cyan", width=15)
            info_table.add_column("Value", style="green")
            
            info_table.add_row("ID", str(profile.id))
            info_table.add_row("Name", profile.name)
            info_table.add_row("Description", profile.description or "No description")
            info_table.add_row("Provider", profile.provider)
            info_table.add_row("Model", profile.model)
            info_table.add_row("Created", profile.created_at.strftime("%Y-%m-%d %H:%M:%S"))
            info_table.add_row("Updated", profile.updated_at.strftime("%Y-%m-%d %H:%M:%S"))
            
            console.print(info_table)
            
            # Settings table
            console.print("\n[bold]Settings:[/bold]")
            settings_table = Table(show_header=True, header_style="bold magenta")
            settings_table.add_column("Setting", style="cyan")
            settings_table.add_column("Value", style="green")
            
            for key, value in profile.settings.items():
                settings_table.add_row(key.replace('_', ' ').title(), str(value))
            
            console.print(settings_table)
            
            # Prompt preview
            console.print("\n[bold]Prompt Template:[/bold]")
            console.print(Panel(profile.prompt, title="Prompt", border_style="dim"))
    
    asyncio.run(_show_profile())
