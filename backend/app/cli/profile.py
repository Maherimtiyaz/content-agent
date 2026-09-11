"""Profile management CLI commands."""

import typer
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.table import Table
from pathlib import Path
import json

profile_app = typer.Typer(help="Manage your professional profile")
console = Console()

PROFILE_PATH = Path(__file__).parent.parent.parent / "data" / "profile" / "profile.json"


@profile_app.command("create")
def create_profile():
    """Create or update your professional profile interactively."""
    console.print(Panel.fit("[bold blue]Create Professional Profile[/bold blue]"))
    
    profile = {}
    
    # Basic info
    console.print("\n[bold]Basic Information[/bold]")
    profile["role"] = Prompt.ask("Your role", default="Software Engineer")
    profile["name"] = Prompt.ask("Your name", default="")
    profile["bio"] = Prompt.ask("Short bio (1-2 sentences)", default="")
    
    # Technical interests
    console.print("\n[bold]Technical Interests[/bold]")
    console.print("(Comma-separated, e.g., AI engineering, LLMs, backend)")
    interests_str = Prompt.ask("Interests", default="AI engineering, LLMs, backend engineering")
    profile["interests"] = [i.strip() for i in interests_str.split(",")]
    
    # Content pillars
    console.print("\n[bold]Content Pillars[/bold]")
    console.print("(Main topics you want to be known for)")
    pillars_str = Prompt.ask("Pillars", default="AI engineering, software engineering, building in public")
    profile["content_pillars"] = [p.strip() for p in pillars_str.split(",")]
    
    # Target audience
    console.print("\n[bold]Target Audience[/bold]")
    audience_str = Prompt.ask("Audience", default="software engineers, AI engineers, developers")
    profile["audience"] = [a.strip() for a in audience_str.split(",")]
    
    # Writing style
    console.print("\n[bold]Writing Style[/bold]")
    profile["tone"] = Prompt.ask("Tone", default="professional but approachable")
    profile["style_notes"] = Prompt.ask("Style notes", default="concise, technical, example-driven")
    
    # Topics to avoid
    console.print("\n[bold]Topics to Avoid[/bold]")
    avoid_str = Prompt.ask("Topics to avoid", default="hype, motivational fluff")
    profile["topics_to_avoid"] = [t.strip() for t in avoid_str.split(",")]
    
    # Goals
    console.print("\n[bold]Goals[/bold]")
    profile["goals"] = Prompt.ask("Content goals", default="Share engineering insights and build reputation")
    
    # Save profile
    PROFILE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(PROFILE_PATH, "w") as f:
        json.dump(profile, f, indent=2)
    
    console.print(f"\n[green]✓ Profile saved to {PROFILE_PATH}[/green]")
    
    # Display summary
    _display_profile(profile)


@profile_app.command("show")
def show_profile():
    """Display current profile."""
    if not PROFILE_PATH.exists():
        console.print("[red]✗ No profile found. Run 'brand-engineer profile create' first.[/red]")
        raise typer.Exit(1)
    
    with open(PROFILE_PATH) as f:
        profile = json.load(f)
    
    _display_profile(profile)


@profile_app.command("edit")
def edit_profile():
    """Edit specific profile fields."""
    if not PROFILE_PATH.exists():
        console.print("[red]✗ No profile found. Run 'brand-engineer profile create' first.[/red]")
        raise typer.Exit(1)
    
    with open(PROFILE_PATH) as f:
        profile = json.load(f)
    
    console.print(Panel.fit("[bold yellow]Edit Profile[/bold yellow]"))
    console.print("Current values shown in [dim]brackets[/dim]. Press Enter to keep.\n")
    
    # Allow editing each field
    profile["role"] = Prompt.ask("Role", default=profile.get("role", ""))
    profile["name"] = Prompt.ask("Name", default=profile.get("name", ""))
    profile["bio"] = Prompt.ask("Bio", default=profile.get("bio", ""))
    
    interests_str = Prompt.ask(
        "Interests (comma-separated)", 
        default=", ".join(profile.get("interests", []))
    )
    profile["interests"] = [i.strip() for i in interests_str.split(",")]
    
    pillars_str = Prompt.ask(
        "Content pillars (comma-separated)",
        default=", ".join(profile.get("content_pillars", []))
    )
    profile["content_pillars"] = [p.strip() for p in pillars_str.split(",")]
    
    audience_str = Prompt.ask(
        "Audience (comma-separated)",
        default=", ".join(profile.get("audience", []))
    )
    profile["audience"] = [a.strip() for a in audience_str.split(",")]
    
    profile["tone"] = Prompt.ask("Tone", default=profile.get("tone", ""))
    profile["style_notes"] = Prompt.ask("Style notes", default=profile.get("style_notes", ""))
    
    avoid_str = Prompt.ask(
        "Topics to avoid (comma-separated)",
        default=", ".join(profile.get("topics_to_avoid", []))
    )
    profile["topics_to_avoid"] = [t.strip() for t in avoid_str.split(",")]
    
    profile["goals"] = Prompt.ask("Goals", default=profile.get("goals", ""))
    
    # Save
    with open(PROFILE_PATH, "w") as f:
        json.dump(profile, f, indent=2)
    
    console.print(f"\n[green]✓ Profile updated[/green]")
    _display_profile(profile)


def _display_profile(profile: dict):
    """Display profile in a formatted table."""
    table = Table(show_header=False, box=None)
    table.add_column("Field", style="cyan")
    table.add_column("Value")
    
    for key, value in profile.items():
        if isinstance(value, list):
            value = ", ".join(value)
        table.add_row(key.replace("_", " ").title(), str(value))
    
    console.print("\n")
    console.print(table)
