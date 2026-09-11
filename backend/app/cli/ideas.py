"""Content ideas CLI commands."""

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from pathlib import Path
import json

ideas_app = typer.Typer(help="Generate and manage content ideas")
console = Console()

IDEAS_PATH = Path(__file__).parent.parent.parent / "data" / "content"


@ideas_app.command()
def generate(
    limit: int = typer.Option(5, "--limit", "-l", help="Number of ideas to generate"),
    demo: bool = typer.Option(False, "--demo", help="Use demo mode"),
):
    """Generate content ideas based on research and profile."""
    from app.ai.ideas import IdeaWorkflow
    
    console.print(Panel.fit("[bold magenta]Content Idea Generator[/bold magenta]"))
    
    # Load profile
    profile_path = Path(__file__).parent.parent.parent / "data" / "profile" / "profile.json"
    if not profile_path.exists():
        console.print("[red]✗ No profile found. Run 'brand-engineer profile create' first.[/red]")
        raise typer.Exit(1)
    
    with open(profile_path) as f:
        profile = json.load(f)
    
    # Load recent research
    research_items = _load_recent_research()
    
    if not research_items:
        console.print("[yellow]⚠ No research found. Run 'brand-engineer research' first.[/yellow]")
        if not demo:
            console.print("Or use [bold]--demo[/bold] flag for demo ideas.")
            raise typer.Exit(0)
    
    # Generate ideas
    workflow = IdeaWorkflow(use_demo=demo or not research_items)
    
    console.print(f"\n[cyan]Generating up to {limit} content ideas...[/cyan]\n")
    
    ideas = workflow.generate_ideas(
        profile=profile,
        research=research_items[:20],  # Use top 20 research items
        limit=limit,
    )
    
    # Save ideas
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    ideas_file = IDEAS_PATH / f"ideas_{timestamp}.json"
    IDEAS_PATH.mkdir(parents=True, exist_ok=True)
    
    with open(ideas_file, "w") as f:
        json.dump({
            "timestamp": timestamp,
            "ideas": ideas,
            "count": len(ideas),
        }, f, indent=2)
    
    # Display ideas
    if ideas:
        for i, idea in enumerate(ideas, 1):
            console.print(Panel(
                f"[bold cyan]{idea.get('title', 'Untitled')}[/bold cyan]\n\n"
                f"[dim]Hook:[/dim] {idea.get('hook', 'N/A')}\n"
                f"[dim]Angle:[/dim] {idea.get('angle', 'N/A')}\n"
                f"[dim]Format:[/dim] {idea.get('format', 'N/A')}\n"
                f"[dim]Confidence:[/dim] {idea.get('confidence', 'N/A')}\n"
                f"[dim]Sources:[/dim] {len(idea.get('supporting_research', []))} items",
                title=f"Idea #{i}",
                border_style="green" if idea.get('confidence', 0) > 0.7 else "yellow",
            ))
        
        console.print(f"\n[green]✓ Generated {len(ideas)} ideas[/green]")
        console.print(f"[dim]Saved to: {ideas_file}[/dim]")
    else:
        console.print("[yellow]⚠ No ideas generated. Try different research or profile.[/yellow]")


def _load_recent_research():
    """Load most recent research results."""
    research_path = Path(__file__).parent.parent.parent / "data" / "research"
    
    if not research_path.exists():
        return []
    
    files = sorted(research_path.glob("research_*.json"), reverse=True)
    
    if not files:
        return []
    
    # Load most recent research session
    with open(files[0]) as f:
        data = json.load(f)
    
    return data.get("items", [])
