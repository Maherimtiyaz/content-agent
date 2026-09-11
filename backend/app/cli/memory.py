"""Brand memory CLI commands."""

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from pathlib import Path
import json

memory_app = typer.Typer(help="View and manage brand memory")
console = Console()

BRAND_MEMORY_PATH = Path(__file__).parent.parent.parent / "data" / "brand_memory"


@memory_app.command("show")
def show_memory():
    """Display current brand memory."""
    memory_file = BRAND_MEMORY_PATH / "brand_memory.json"
    
    if not memory_file.exists():
        console.print("[yellow]⚠ No brand memory found.[/yellow]")
        console.print("Use [bold]brand-engineer learn post[/bold] to start building memory.")
        return
    
    with open(memory_file) as f:
        memory = json.load(f)
    
    console.print(Panel.fit("[bold magenta]Brand Memory[/bold magenta]"))
    
    # Display summary
    table = Table(show_header=False, box=None)
    table.add_column("Attribute", style="cyan")
    table.add_column("Value")
    
    table.add_row("Last Updated", memory.get("updated_at", "N/A")[:10])
    table.add_row("Posts Analyzed", str(memory.get("total_posts_analyzed", 0)))
    table.add_row("Avg Word Count", str(memory.get("average_word_count", 0)))
    table.add_row("Top Topics", ", ".join(memory.get("strongest_topics", [])))
    table.add_row("Top Formats", ", ".join(memory.get("strongest_formats", [])))
    table.add_row("Technical Depth", memory.get("strongest_technical_depth", "mixed"))
    
    console.print("\n")
    console.print(table)
    
    # Show patterns
    console.print("\n[bold]Strong Patterns:[/bold]")
    for pattern in memory.get("strongest_patterns", []):
        if pattern:
            console.print(f"  ✓ {pattern}")
    
    console.print("\n[bold]Areas to Improve:[/bold]")
    for pattern in memory.get("weak_patterns", []):
        if pattern:
            console.print(f"  ⚠ {pattern}")
    
    console.print(f"\n[dim]Recommended mix: {memory.get('recommended_mix', 'N/A')}[/dim]")


@memory_app.command("clear")
def clear_memory(confirm: bool = typer.Option(False, "--yes", "-y")):
    """Clear all brand memory."""
    if not confirm:
        if not Confirm.ask("[red]This will delete all learned patterns. Continue?[/red]"):
            raise typer.Exit(0)
    
    # Remove memory files
    for file in BRAND_MEMORY_PATH.glob("*.json*"):
        file.unlink()
    
    console.print("[green]✓ Brand memory cleared[/green]")
