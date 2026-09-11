"""Research CLI commands."""

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from pathlib import Path
import json
from datetime import datetime

research_app = typer.Typer(help="Research topics and trends")
console = Console()

RESEARCH_PATH = Path(__file__).parent.parent.parent / "data" / "research"


@research_app.command()
def run(
    topic: str = typer.Argument(None, help="Specific topic to research"),
    deep: bool = typer.Option(False, "--deep", "-d", help="Deep research mode"),
    demo: bool = typer.Option(False, "--demo", help="Use demo/mock data"),
):
    """Research topics relevant to your interests.
    
    If no topic is specified, researches based on your profile interests.
    """
    from app.research.engine import ResearchEngine
    
    console.print(Panel.fit("[bold green]Research Engine[/bold green]"))
    
    # Load profile
    profile_path = Path(__file__).parent.parent.parent / "data" / "profile" / "profile.json"
    if not profile_path.exists():
        console.print("[red]✗ No profile found. Run 'brand-engineer profile create' first.[/red]")
        raise typer.Exit(1)
    
    with open(profile_path) as f:
        profile = json.load(f)
    
    # Determine topics
    if topic:
        topics = [topic]
    else:
        topics = profile.get("interests", ["AI engineering", "LLMs"])[:5]
    
    console.print(f"\n[bold]Researching:[/bold] {', '.join(topics)}")
    if deep:
        console.print("[dim]Deep research mode enabled[/dim]")
    
    # Initialize research engine
    engine = ResearchEngine(use_demo=demo)
    
    # Run research
    console.print("\n[cyan]Searching sources...[/cyan]")
    results = engine.research(topics, deep=deep)
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    research_file = RESEARCH_PATH / f"research_{timestamp}.json"
    RESEARCH_PATH.mkdir(parents=True, exist_ok=True)
    
    with open(research_file, "w") as f:
        json.dump({
            "timestamp": timestamp,
            "topics": topics,
            "items": results,
            "count": len(results),
        }, f, indent=2)
    
    # Display summary
    console.print(f"\n[green]✓ Found {len(results)} research items[/green]")
    console.print(f"[dim]Saved to: {research_file}[/dim]\n")
    
    # Show top items
    if results:
        table = Table(title="Top Research Findings")
        table.add_column("#", style="dim")
        table.add_column("Title", style="cyan")
        table.add_column("Source", style="green")
        table.add_column("Relevance", justify="right")
        
        for i, item in enumerate(results[:10], 1):
            relevance_score = item.get("relevance_score", 0)
            score_display = f"{relevance_score:.1f}" if isinstance(relevance_score, (int, float)) else "N/A"
            table.add_row(
                str(i),
                item.get("title", "Untitled")[:50] + ("..." if len(item.get("title", "")) > 50 else ""),
                item.get("source_type", "unknown"),
                score_display,
            )
        
        console.print(table)
        console.print(f"\n[dim]Showing top 10 of {len(results)} items. See full results in JSON file.[/dim]")
    else:
        console.print("[yellow]⚠ No research items found. Try different topics or enable demo mode.[/yellow]")


@research_app.command("list")
def list_research(limit: int = typer.Option(10, "--limit", "-l")):
    """List recent research results."""
    if not RESEARCH_PATH.exists():
        console.print("[yellow]No research history found.[/yellow]")
        return
    
    files = sorted(RESEARCH_PATH.glob("research_*.json"), reverse=True)[:limit]
    
    if not files:
        console.print("[yellow]No research files found.[/yellow]")
        return
    
    table = Table(title="Recent Research Sessions")
    table.add_column("Date", style="cyan")
    table.add_column("Topics", style="green")
    table.add_column("Items", justify="right")
    table.add_column("File")
    
    for file in files:
        with open(file) as f:
            data = json.load(f)
        
        date = data.get("timestamp", "unknown")[:10]
        topics = ", ".join(data.get("topics", [])[:3])
        count = data.get("count", 0)
        
        table.add_row(date, topics, str(count), file.name)
    
    console.print(table)
