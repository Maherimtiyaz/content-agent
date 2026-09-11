"""History CLI commands."""

import typer
from rich.console import Console
from rich.table import Table
from pathlib import Path
import json
from datetime import datetime

history_app = typer.Typer(help="View activity history")
console = Console()

DATA_PATH = Path(__file__).parent.parent.parent / "data"


@history_app.command()
def show(
    type: str = typer.Option("all", "--type", "-t", help="Filter by type"),
    limit: int = typer.Option(10, "--limit", "-l", help="Number of items to show"),
):
    """Show recent activity history."""
    console.print(f"[bold]Recent Activity ({type})[/bold]\n")
    
    if type in ("all", "research"):
        _show_research_history(limit)
    
    if type in ("all", "ideas"):
        _show_ideas_history(limit)
    
    if type in ("all", "drafts"):
        _show_draft_history(limit)
    
    if type in ("all", "learned"):
        _show_learned_history(limit)


def _show_research_history(limit: int):
    """Show research history."""
    research_path = DATA_PATH / "research"
    
    if not research_path.exists():
        return
    
    files = sorted(research_path.glob("research_*.json"), reverse=True)[:limit]
    
    if files:
        console.print("[cyan]Research Sessions:[/cyan]")
        table = Table(show_header=False, box=None)
        table.add_column("Date", style="dim")
        table.add_column("Topics")
        table.add_column("Items", justify="right")
        
        for file in files:
            with open(file) as f:
                data = json.load(f)
            
            date = data.get("timestamp", "unknown")[:10]
            topics = ", ".join(data.get("topics", [])[:2])
            count = data.get("count", 0)
            
            table.add_row(date, topics, str(count))
        
        console.print(table)
        console.print()


def _show_ideas_history(limit: int):
    """Show ideas history."""
    content_path = DATA_PATH / "content"
    
    if not content_path.exists():
        return
    
    files = sorted(content_path.glob("ideas_*.json"), reverse=True)[:limit]
    
    if files:
        console.print("[cyan]Idea Sessions:[/cyan]")
        table = Table(show_header=False, box=None)
        table.add_column("Date", style="dim")
        table.add_column("Ideas Generated")
        
        for file in files:
            with open(file) as f:
                data = json.load(f)
            
            date = data.get("timestamp", "unknown")[:10]
            count = data.get("count", 0)
            
            table.add_row(date, str(count))
        
        console.print(table)
        console.print()


def _show_draft_history(limit: int):
    """Show draft history."""
    content_path = DATA_PATH / "content"
    
    if not content_path.exists():
        return
    
    files = sorted(content_path.glob("draft_*.json"), reverse=True)[:limit]
    
    if files:
        console.print("[cyan]Drafts:[/cyan]")
        table = Table(show_header=False, box=None)
        table.add_column("Date", style="dim")
        table.add_column("Title")
        table.add_column("Status")
        
        for file in files:
            with open(file) as f:
                data = json.load(f)
            
            date = data.get("generated_at", "unknown")[:10]
            title = data.get("idea", {}).get("title", "Untitled")[:40]
            status = data.get("status", "draft")
            
            table.add_row(date, title, status)
        
        console.print(table)
        console.print()


def _show_learned_history(limit: int):
    """Show learned posts history."""
    memory_path = DATA_PATH / "brand_memory"
    
    if not memory_path.exists():
        return
    
    learning_file = memory_path / "published_posts.jsonl"
    
    if not learning_file.exists():
        return
    
    posts = []
    with open(learning_file) as f:
        for line in f:
            if line.strip():
                posts.append(json.loads(line))
    
    if posts:
        console.print("[cyan]Learned Posts:[/cyan]")
        table = Table(show_header=False, box=None)
        table.add_column("Date", style="dim")
        table.add_column("Platform")
        table.add_column("Length")
        
        for post in posts[-limit:]:
            date = post.get("timestamp", "unknown")[:10]
            platform = post.get("platform", "X")
            length = len(post.get("content", ""))
            
            table.add_row(date, platform, f"{length} chars")
        
        console.print(table)
        console.print()
