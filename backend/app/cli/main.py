"""CLI entry point for Brand Engineer."""

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm

from app.cli.profile import profile_app
from app.cli.research import research_app
from app.cli.ideas import ideas_app
from app.cli.generate import generate_app
from app.cli.learn import learn_app
from app.cli.memory import memory_app
from app.cli.history import history_app
from app.cli.daily import daily_app

app = typer.Typer(
    name="brand-engineer",
    help="AI Personal Brand Research Agent for Software Engineers",
    add_completion=False,
)

console = Console()

# Include sub-applications
app.add_typer(profile_app, name="profile")
app.add_typer(research_app, name="research")
app.add_typer(ideas_app, name="ideas")
app.add_typer(generate_app, name="generate")
app.add_typer(learn_app, name="learn")
app.add_typer(memory_app, name="memory")
app.add_typer(history_app, name="history")
app.add_typer(daily_app, name="daily")


@app.command()
def version():
    """Show version information."""
    console.print("[bold blue]Brand Engineer[/bold blue] v0.1.0")
    console.print("AI-powered personal brand research agent")


@app.command()
def init(
    interactive: bool = typer.Option(False, "--interactive", "-i", help="Run interactive setup")
):
    """Initialize the brand engineer configuration.
    
    Creates necessary directories and prompts for initial profile setup.
    """
    from pathlib import Path
    
    console.print(Panel.fit("[bold green]Initializing Brand Engineer[/bold green]"))
    
    # Create data directories
    data_dirs = [
        "data/profile",
        "data/research", 
        "data/content",
        "data/brand_memory",
    ]
    
    base_path = Path(__file__).parent.parent.parent
    for dir_name in data_dirs:
        dir_path = base_path / dir_name
        dir_path.mkdir(parents=True, exist_ok=True)
        console.print(f"✓ Created directory: [cyan]{dir_path}[/cyan]")
    
    console.print("\n[green]✓ Initialization complete![/green]")
    console.print("\nNext steps:")
    console.print("  1. Run [bold]brand-engineer profile create[/bold] to set up your profile")
    console.print("  2. Run [bold]brand-engineer research[/bold] to start researching topics")
    console.print("  3. Run [bold]brand-engineer daily[/bold] for the complete workflow")


if __name__ == "__main__":
    app()
