"""Daily workflow CLI command - the main entry point."""

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from pathlib import Path
import json
from datetime import datetime

daily_app = typer.Typer(help="Run complete daily workflow")
console = Console()

DATA_PATH = Path(__file__).parent.parent.parent / "data"


@daily_app.command()
def run(
    demo: bool = typer.Option(False, "--demo", help="Use demo mode (no API keys needed)"),
    skip_research: bool = typer.Option(False, "--skip-research", help="Skip research step"),
    limit: int = typer.Option(5, "--limit", "-l", help="Number of ideas to generate"),
):
    """Execute the complete daily brand research workflow.
    
    This command runs the full pipeline:
    1. Load profile and brand memory
    2. Research fresh topics
    3. Generate content ideas
    4. Create drafts
    5. Quality check
    6. Present top opportunities
    
    Human review is required before any publishing.
    """
    console.print(Panel.fit(
        "[bold green]Daily Brand Research[/bold green]\n"
        "[dim]AI-powered content discovery and drafting[/dim]",
        border_style="green",
    ))
    
    # Step 1: Load profile
    console.print("\n[bold step 1/6] Loading profile...[/bold step 1/6]")
    profile_path = DATA_PATH / "profile" / "profile.json"
    
    if not profile_path.exists():
        console.print("[red]✗ No profile found.[/red]")
        console.print("Run [bold]brand-engineer profile create[/bold] first.")
        raise typer.Exit(1)
    
    with open(profile_path) as f:
        profile = json.load(f)
    
    console.print(f"  ✓ Profile loaded: {profile.get('role', 'Engineer')}")
    
    # Step 2: Load brand memory
    console.print("\n[bold step 2/6] Loading brand memory...[/bold step 2/6]")
    memory_path = DATA_PATH / "brand_memory" / "brand_memory.json"
    
    if memory_path.exists():
        with open(memory_path) as f:
            memory = json.load(f)
        console.print(f"  ✓ Brand memory loaded ({memory.get('total_posts_analyzed', 0)} posts analyzed)")
    else:
        console.print("  ⚠ No brand memory yet (use 'brand-engineer learn' to build)")
        memory = {}
    
    # Step 3: Research
    if not skip_research:
        console.print("\n[bold step 3/6] Researching topics...[/bold step 3/6]")
        
        from app.research.engine import ResearchEngine
        
        topics = profile.get("interests", ["AI engineering"])[:5]
        console.print(f"  Topics: {', '.join(topics)}")
        
        engine = ResearchEngine(use_demo=demo)
        research_results = engine.research(topics, deep=False)
        
        # Save research
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        research_file = DATA_PATH / "research" / f"research_{timestamp}.json"
        research_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(research_file, "w") as f:
            json.dump({
                "timestamp": timestamp,
                "topics": topics,
                "items": research_results,
                "count": len(research_results),
            }, f, indent=2)
        
        console.print(f"  ✓ Found {len(research_results)} research items")
    else:
        console.print("\n[bold step 3/6] Skipping research (using existing)...[/bold step 3/6]")
        research_results = _load_recent_research()
    
    # Step 4: Generate ideas
    console.print("\n[bold step 4/6] Generating content ideas...[/bold step 4/6]")
    
    from app.ai.ideas import IdeaWorkflow
    
    workflow = IdeaWorkflow(use_demo=demo or not research_results)
    ideas = workflow.generate_ideas(
        profile=profile,
        research=research_results[:20],
        limit=limit,
    )
    
    # Save ideas
    ideas_file = DATA_PATH / "content" / f"ideas_{timestamp}.json"
    ideas_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(ideas_file, "w") as f:
        json.dump({
            "timestamp": timestamp,
            "ideas": ideas,
            "count": len(ideas),
        }, f, indent=2)
    
    console.print(f"  ✓ Generated {len(ideas)} content ideas")
    
    # Step 5: Generate drafts for top ideas
    console.print("\n[bold step 5/6] Creating drafts...[/bold step 5/6]")
    
    from app.ai.content import ContentWorkflow
    
    content_workflow = ContentWorkflow(use_demo=demo)
    
    drafts_created = 0
    for i, idea in enumerate(ideas[:3], 1):  # Draft top 3 ideas
        draft = content_workflow.generate_draft(idea=idea, profile=profile)
        
        # Save draft
        draft_file = DATA_PATH / "content" / f"draft_{timestamp}_{i}.json"
        
        with open(draft_file, "w") as f:
            json.dump({
                "idea": idea,
                "draft": draft,
                "generated_at": timestamp,
                "status": "draft",
            }, f, indent=2)
        
        drafts_created += 1
    
    console.print(f"  ✓ Created {drafts_created} drafts")
    
    # Step 6: Present results
    console.print("\n[bold step 6/6] Top Content Opportunities[/bold step 6/6]")
    
    if ideas:
        for i, idea in enumerate(ideas[:5], 1):
            confidence = idea.get('confidence', 0)
            border = "green" if confidence > 0.7 else "yellow" if confidence > 0.5 else "red"
            
            console.print(Panel(
                f"[bold]{idea.get('title', 'Untitled')}[/bold]\n\n"
                f"[dim]Hook:[/dim] {idea.get('hook', 'N/A')}\n"
                f"[dim]Format:[/dim] {idea.get('format', 'N/A')}\n"
                f"[dim]Why now:[/dim] {idea.get('why_now', 'N/A')}\n"
                f"[dim]Confidence:[/dim] {confidence:.0%}",
                title=f"Opportunity #{i}",
                border_style=border,
            ))
        
        console.print(f"\n[green]✓ Daily workflow complete![/green]")
        console.print("\n[dim]Next steps:[/dim]")
        console.print("  • Review drafts: [bold]brand-engineer history -t drafts[/bold]")
        console.print("  • Learn from published posts: [bold]brand-engineer learn post[/bold]")
        console.print("  • Run again tomorrow: [bold]brand-engineer daily run[/bold]")
    else:
        console.print("[yellow]⚠ No ideas generated. Try different profile interests or research topics.[/yellow]")


def _load_recent_research():
    """Load most recent research results."""
    research_path = DATA_PATH / "research"
    
    if not research_path.exists():
        return []
    
    files = sorted(research_path.glob("research_*.json"), reverse=True)
    
    if not files:
        return []
    
    with open(files[0]) as f:
        data = json.load(f)
    
    return data.get("items", [])
