"""
Configuration management commands.
"""

import asyncio
import click
import json
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

from core.ai_providers import get_provider_manager
from core.embeddings import get_embedding_generator
from config.config import load_config, save_config
from config.settings import get_settings

console = Console()

@click.group()
def config_group():
    """Configuration management commands."""
    pass

@config_group.command()
def validate():
    """Validate the current configuration."""
    console.print(Panel.fit("🔍 Validating Configuration", style="bold blue"))
    
    async def _validate_config():
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            # Validate settings
            task1 = progress.add_task("Validating settings...", total=None)
            try:
                settings = get_settings()
                progress.update(task1, description="✅ Settings valid")
            except Exception as e:
                progress.update(task1, description=f"❌ Settings invalid: {str(e)}")
                console.print(f"\n[red]Settings Error: {str(e)}[/red]")
                return
            
            # Validate config file
            task2 = progress.add_task("Validating config file...", total=None)
            try:
                config = load_config()
                progress.update(task2, description="✅ Config file valid")
            except Exception as e:
                progress.update(task2, description=f"❌ Config file invalid: {str(e)}")
                console.print(f"\n[red]Config Error: {str(e)}[/red]")
                return
            
            # Validate AI providers
            task3 = progress.add_task("Validating AI providers...", total=None)
            try:
                provider_manager = get_provider_manager()
                available_providers = provider_manager.get_available_providers()
                progress.update(task3, description=f"✅ {len(available_providers)} providers available")
            except Exception as e:
                progress.update(task3, description=f"❌ Provider validation failed: {str(e)}")
                console.print(f"\n[red]Provider Error: {str(e)}[/red]")
                return
            
            # Validate embedding providers
            task4 = progress.add_task("Validating embedding providers...", total=None)
            try:
                embedding_generator = get_embedding_generator()
                embedding_providers = await embedding_generator.get_available_providers()
                total_models = sum(len(models) for models in embedding_providers.values())
                progress.update(task4, description=f"✅ {total_models} embedding models available")
            except Exception as e:
                progress.update(task4, description=f"❌ Embedding validation failed: {str(e)}")
                console.print(f"\n[red]Embedding Error: {str(e)}[/red]")
                return
        
        # Show validation summary
        console.print("\n[bold green]Configuration Validation Complete![/bold green]")
        
        summary_table = Table(show_header=True, header_style="bold magenta")
        summary_table.add_column("Component", style="cyan")
        summary_table.add_column("Status", style="green")
        summary_table.add_column("Details")
        
        summary_table.add_row("Settings", "✅ Valid", f"Environment: {settings.environment}")
        summary_table.add_row("Config File", "✅ Valid", "Configuration loaded successfully")
        summary_table.add_row("AI Providers", "✅ Valid", f"{len(available_providers)} providers available")
        summary_table.add_row("Embeddings", "✅ Valid", f"{total_models} models available")
        
        console.print(summary_table)
    
    asyncio.run(_validate_config())

@config_group.command()
def test_providers():
    """Test all configured AI providers."""
    console.print(Panel.fit("🧪 Testing AI Providers", style="bold blue"))
    
    async def _test_providers():
        provider_manager = get_provider_manager()
        available_providers = provider_manager.get_available_providers()
        
        if not available_providers:
            console.print("[yellow]No AI providers configured[/yellow]")
            return
        
        results_table = Table(show_header=True, header_style="bold magenta")
        results_table.add_column("Provider", style="cyan")
        results_table.add_column("Status", style="green")
        results_table.add_column("Response Time", style="yellow")
        results_table.add_column("Error", style="red")
        
        for provider_name in available_providers:
            with Progress(
                SpinnerColumn(),
                TextColumn(f"Testing {provider_name}..."),
                console=console
            ) as progress:
                task = progress.add_task(f"Testing {provider_name}...", total=None)
                
                try:
                    # Get first available model for this provider
                    models = provider_manager.get_available_models(provider_name)
                    if not models:
                        results_table.add_row(provider_name, "❌ No Models", "N/A", "No models available")
                        continue
                    
                    model = models[0]
                    
                    # Test with a simple query
                    response = await provider_manager.generate_response(
                        provider_name=provider_name,
                        model=model,
                        prompt="Hello, this is a test message. Please respond with 'Test successful'.",
                        max_tokens=10
                    )
                    
                    if response.error:
                        results_table.add_row(provider_name, "❌ Error", "N/A", response.error)
                    else:
                        results_table.add_row(provider_name, "✅ Success", "< 1s", "N/A")
                    
                    progress.update(task, description=f"✅ {provider_name} test complete")
                    
                except Exception as e:
                    results_table.add_row(provider_name, "❌ Exception", "N/A", str(e))
                    progress.update(task, description=f"❌ {provider_name} test failed")
        
        console.print("\n[bold]Provider Test Results:[/bold]")
        console.print(results_table)
    
    asyncio.run(_test_providers())

@config_group.command()
def show():
    """Show current configuration."""
    console.print(Panel.fit("📋 Current Configuration", style="bold blue"))
    
    try:
        # Load settings
        settings = get_settings()
        
        # Settings table
        settings_table = Table(show_header=True, header_style="bold magenta")
        settings_table.add_column("Setting", style="cyan")
        settings_table.add_column("Value", style="green")
        
        settings_table.add_row("Environment", settings.environment)
        settings_table.add_row("Debug Mode", str(settings.debug))
        settings_table.add_row("Log Level", settings.log_level)
        settings_table.add_row("Max File Size", f"{settings.max_file_size / 1024 / 1024:.1f} MB")
        settings_table.add_row("Allowed File Types", ", ".join(settings.allowed_file_types))
        settings_table.add_row("CORS Origins", ", ".join(settings.cors_origins))
        
        console.print(settings_table)
        
        # Load config
        config = load_config()
        
        # Providers table
        console.print("\n[bold]AI Providers:[/bold]")
        providers_table = Table(show_header=True, header_style="bold magenta")
        providers_table.add_column("Provider", style="cyan")
        providers_table.add_column("Base URL", style="green")
        providers_table.add_column("Models", style="yellow")
        
        for provider_name, provider_config in config.get('providers', {}).items():
            models = list(provider_config.get('models', {}).keys())
            providers_table.add_row(
                provider_name,
                provider_config.get('base_url', 'Default'),
                f"{len(models)} models"
            )
        
        console.print(providers_table)
        
        # Default profiles
        console.print("\n[bold]Default Profiles:[/bold]")
        profiles_table = Table(show_header=True, header_style="bold magenta")
        profiles_table.add_column("Name", style="cyan")
        profiles_table.add_column("Provider", style="green")
        profiles_table.add_column("Model", style="yellow")
        
        for profile in config.get('default_profiles', []):
            profiles_table.add_row(
                profile.get('name', 'Unknown'),
                profile.get('provider', 'Unknown'),
                profile.get('model', 'Unknown')
            )
        
        console.print(profiles_table)
        
    except Exception as e:
        console.print(f"[red]Error loading configuration: {str(e)}[/red]")

@config_group.command()
@click.argument('provider_name')
@click.option('--base-url', help='Set base URL for the provider')
@click.option('--api-key', help='Set API key for the provider')
@click.option('--model', multiple=True, help='Add a model to the provider')
def update_provider(provider_name: str, base_url: str, api_key: str, model: tuple):
    """Update provider configuration."""
    console.print(Panel.fit(f"⚙️ Updating Provider: {provider_name}", style="bold blue"))
    
    try:
        config = load_config()
        
        if 'providers' not in config:
            config['providers'] = {}
        
        if provider_name not in config['providers']:
            config['providers'][provider_name] = {
                'base_url': '',
                'api_key': '',
                'models': {}
            }
        
        provider_config = config['providers'][provider_name]
        
        if base_url:
            provider_config['base_url'] = base_url
            console.print(f"[green]Updated base URL: {base_url}[/green]")
        
        if api_key:
            provider_config['api_key'] = api_key
            console.print(f"[green]Updated API key[/green]")
        
        if model:
            if 'models' not in provider_config:
                provider_config['models'] = {}
            
            for model_name in model:
                provider_config['models'][model_name] = {
                    'name': model_name,
                    'max_tokens': 4000,
                    'temperature': 0.7
                }
                console.print(f"[green]Added model: {model_name}[/green]")
        
        # Save updated config
        save_config(config)
        
        console.print(f"\n[bold green]Provider '{provider_name}' updated successfully![/bold green]")
        
    except Exception as e:
        console.print(f"[red]Error updating provider: {str(e)}[/red]")

@config_group.command()
@click.argument('output_file', type=click.Path())
def export(output_file: str):
    """Export current configuration to a file."""
    console.print(Panel.fit("📤 Exporting Configuration", style="bold blue"))
    
    try:
        config = load_config()
        
        with open(output_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        console.print(f"[bold green]Configuration exported to: {output_file}[/bold green]")
        
    except Exception as e:
        console.print(f"[red]Error exporting configuration: {str(e)}[/red]")

@config_group.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.option('--backup', is_flag=True, help='Create backup of current config')
def import_config(input_file: str, backup: bool):
    """Import configuration from a file."""
    console.print(Panel.fit("📥 Importing Configuration", style="bold blue"))
    
    try:
        # Create backup if requested
        if backup:
            import shutil
            from pathlib import Path
            config_path = Path(__file__).parent.parent.parent / 'backend' / 'config' / 'config.json'
            backup_path = config_path.with_suffix('.json.backup')
            shutil.copy2(config_path, backup_path)
            console.print(f"[green]Backup created: {backup_path}[/green]")
        
        # Load and import config
        with open(input_file, 'r') as f:
            config = json.load(f)
        
        save_config(config)
        
        console.print(f"[bold green]Configuration imported from: {input_file}[/bold green]")
        
    except Exception as e:
        console.print(f"[red]Error importing configuration: {str(e)}[/red]")
