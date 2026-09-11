"""Content generation CLI commands."""

import typer
from rich.console import Console
from rich.panel import Panel
from pathlib import Path
import json

generate_app = typer.Typer(help="Generate content drafts")
console = Console()

CONTENT_PATH = Path(__file__).parent.parent.parent / "data" / "content"


@generate_app.command()
def draft(
    idea_id: int = typer.Option(None, "--idea", "-i", help="Specific idea ID to expand"),
    limit: int = typer.Option(3, "--limit", "-l", help="Number of drafts to generate"),
    demo: bool = typer.Option(False, "--demo", help="Use demo mode"),
):
    """Generate full drafts from content ideas."""
    from app.ai.content import ContentWorkflow
    
    console.print(Panel.fit("[bold blue]Draft Generator[/bold blue]"))
    
    # Load profile
    profile_path = Path(__file__).parent.parent.parent / "data" / "profile" / "profile.json"
    if not profile_path.exists():
        console.print("[red]✗ No profile found.[/red]")
        raise typer.Exit(1)
    
    with open(profile_path) as f:
        profile = json.load(f)
    
    # Load ideas
    ideas_file = _get_latest_ideas_file()
    if not ideas_file:
        console.print("[yellow]⚠ No ideas found. Run 'brand-engineer ideas generate' first.[/yellow]")
        if not demo:
            raise typer.Exit(0)
    
    with open(ideas_file) as f:
        ideas_data = json.load(f)
    
    ideas = ideas_data.get("ideas", [])
    
    if not ideas:
        console.print("[yellow]No ideas available.[/yellow]")
        return
    
    # Select ideas to expand
    if idea_id and 0 < idea_id <= len(ideas):
        selected_ideas = [ideas[idea_id - 1]]
    else:
        selected_ideas = ideas[:limit]
    
    # Generate drafts
    workflow = ContentWorkflow(use_demo=demo)
    
    console.print(f"\n[cyan]Generating {len(selected_ideas)} drafts...[/cyan]\n")
    
    for i, idea in enumerate(selected_ideas, 1):
        draft = workflow.generate_draft(
            idea=idea,
            profile=profile,
        )
        
        # Save draft
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        draft_file = CONTENT_PATH / f"draft_{timestamp}_{i}.json"
        CONTENT_PATH.mkdir(parents=True, exist_ok=True)
        
        with open(draft_file, "w") as f:
            json.dump({
                "idea": idea,
                "draft": draft,
                "generated_at": timestamp,
                "status": "draft",
            }, f, indent=2)
        
        # Display draft
        console.print(Panel(
            f"{draft.get('content', 'No content generated')}",
            title=f"Draft #{i}: {idea.get('title', 'Untitled')[:40]}",
            border_style="blue",
        ))
        
        # Show quality check preview
        quality = draft.get("quality_check", {})
        if quality:
            status = "✓ Passed" if quality.get("passed", False) else "⚠ Needs review"
            console.print(f"[dim]Quality: {status} | Score: {quality.get('score', 'N/A')}[/dim]\n")


def _get_latest_ideas_file() -> Path:
    """Get most recent ideas file."""
    if not CONTENT_PATH.exists():
        return None
    
    files = sorted(CONTENT_PATH.glob("ideas_*.json"), reverse=True)
    return files[0] if files else None
