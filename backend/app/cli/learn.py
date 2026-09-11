"""Learn from published posts CLI commands."""

import typer
from rich.console import Console
from rich.panel import Panel
from pathlib import Path
import json
from datetime import datetime

learn_app = typer.Typer(help="Learn from your published content")
console = Console()

BRAND_MEMORY_PATH = Path(__file__).parent.parent.parent / "data" / "brand_memory"


@learn_app.command()
def post(
    content: str = typer.Argument(None, help="Published post content"),
    file: Path = typer.Option(None, "--file", "-f", help="File containing published post"),
    platform: str = typer.Option("X", "--platform", "-p", help="Platform where published"),
):
    """Teach the agent about a post you published.
    
    This helps the agent learn your writing style and what resonates.
    """
    console.print(Panel.fit("[bold green]Learning from Published Post[/bold green]"))
    
    # Get content
    if file:
        if not file.exists():
            console.print(f"[red]✗ File not found: {file}[/red]")
            raise typer.Exit(1)
        with open(file) as f:
            content = f.read().strip()
    elif content is None:
        # Interactive mode
        console.print("\n[dim]Paste your published post content (end with blank line or Ctrl+D):[/dim]\n")
        lines = []
        try:
            while True:
                line = input()
                if not line.strip():
                    break
                lines.append(line)
        except EOFError:
            pass
        content = "\n".join(lines).strip()
    
    if not content:
        console.print("[red]✗ No content provided.[/red]")
        raise typer.Exit(1)
    
    # Analyze the post
    analysis = _analyze_post(content, platform)
    
    # Save to brand memory
    BRAND_MEMORY_PATH.mkdir(parents=True, exist_ok=True)
    
    # Append to learning history
    learning_file = BRAND_MEMORY_PATH / "published_posts.jsonl"
    with open(learning_file, "a") as f:
        f.write(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "content": content,
            "platform": platform,
            "analysis": analysis,
        }) + "\n")
    
    # Update brand memory summary
    _update_brand_memory()
    
    console.print(f"\n[green]✓ Learned from post ({len(content)} chars)[/green]")
    console.print(f"[dim]Saved to: {learning_file}[/dim]\n")
    
    # Show analysis
    console.print(Panel(
        f"[bold]Style Analysis:[/bold]\n"
        f"• Tone: {analysis.get('tone', 'N/A')}\n"
        f"• Format: {analysis.get('format', 'N/A')}\n"
        f"• Length: {analysis.get('length_category', 'N/A')}\n"
        f"• Hashtags: {analysis.get('hashtag_count', 0)}\n"
        f"• Questions: {analysis.get('question_count', 0)}\n"
        f"• Technical depth: {analysis.get('technical_depth', 'N/A')}",
        title="Post Analysis",
        border_style="green",
    ))


@learn_app.command("deep")
def deep_learn():
    """Analyze all learned posts and update brand memory."""
    console.print(Panel.fit("[bold magenta]Deep Brand Memory Update[/bold magenta]"))
    
    learning_file = BRAND_MEMORY_PATH / "published_posts.jsonl"
    
    if not learning_file.exists():
        console.print("[yellow]⚠ No published posts to analyze.[/yellow]")
        console.print("Use [bold]brand-engineer learn post[/bold] to add posts first.")
        return
    
    # Load all learned posts
    posts = []
    with open(learning_file) as f:
        for line in f:
            if line.strip():
                posts.append(json.loads(line))
    
    console.print(f"\n[cyan]Analyzing {len(posts)} published posts...[/cyan]\n")
    
    # Generate comprehensive analysis
    memory_update = _generate_brand_memory(posts)
    
    # Save updated memory
    memory_file = BRAND_MEMORY_PATH / "brand_memory.json"
    with open(memory_file, "w") as f:
        json.dump(memory_update, f, indent=2)
    
    # Display summary
    console.print(Panel(
        f"[bold]Topics You Cover:[/bold]\n"
        f"{', '.join(memory_update.get('strongest_topics', []))}\n\n"
        f"[bold]Preferred Formats:[/bold]\n"
        f"{', '.join(memory_update.get('strongest_formats', []))}\n\n"
        f"[bold]Writing Patterns:[/bold]\n"
        f"• {memory_update.get('strongest_patterns', ['N/A'])[0]}\n"
        f"• {memory_update.get('strongest_patterns', ['N/A'])[1] if len(memory_update.get('strongest_patterns', [])) > 1 else ''}\n\n"
        f"[bold]Recommended Mix:[/bold]\n"
        f"{memory_update.get('recommended_mix', 'N/A')}",
        title="Brand Evolution Report",
        border_style="magenta",
    ))
    
    console.print(f"\n[green]✓ Brand memory updated[/green]")
    console.print(f"[dim]Saved to: {memory_file}[/dim]")


def _analyze_post(content: str, platform: str) -> dict:
    """Analyze a single post for style markers."""
    words = content.split()
    word_count = len(words)
    char_count = len(content)
    
    # Count hashtags
    hashtag_count = content.count("#")
    
    # Count questions
    question_count = content.count("?")
    
    # Detect format
    if word_count < 50:
        format_type = "short_post"
        length_category = "short"
    elif word_count < 150:
        format_type = "medium_post"
        length_category = "medium"
    else:
        format_type = "long_post"
        length_category = "long"
    
    # Detect tone (simplified)
    if any(word in content.lower() for word in ["lesson", "learned", "after"]):
        tone = "educational"
    elif any(word in content.lower() for word in ["opinion", "think", "believe"]):
        tone = "opinion"
    elif any(word in content.lower() for word in ["experiment", "trying", "testing"]):
        tone = "experimental"
    else:
        tone = "informational"
    
    # Technical depth (simplified)
    technical_markers = ["```", "code", "API", "system", "architecture", "implementation"]
    technical_count = sum(1 for marker in technical_markers if marker in content.lower())
    
    if technical_count >= 3:
        technical_depth = "high"
    elif technical_count >= 1:
        technical_depth = "medium"
    else:
        technical_depth = "low"
    
    return {
        "word_count": word_count,
        "char_count": char_count,
        "length_category": length_category,
        "format": format_type,
        "hashtag_count": hashtag_count,
        "question_count": question_count,
        "tone": tone,
        "technical_depth": technical_depth,
        "first_person": "I " in content or "my " in content.lower(),
        "includes_examples": "```" in content or "example" in content.lower(),
    }


def _update_brand_memory():
    """Update brand memory summary from all learned posts."""
    learning_file = BRAND_MEMORY_PATH / "published_posts.jsonl"
    
    if not learning_file.exists():
        return
    
    posts = []
    with open(learning_file) as f:
        for line in f:
            if line.strip():
                posts.append(json.loads(line))
    
    if posts:
        memory = _generate_brand_memory(posts)
        memory_file = BRAND_MEMORY_PATH / "brand_memory.json"
        with open(memory_file, "w") as f:
            json.dump(memory, f, indent=2)


def _generate_brand_memory(posts: list) -> dict:
    """Generate comprehensive brand memory from posts."""
    # Aggregate statistics
    tones = {}
    formats = {}
    technical_depths = {}
    
    for post in posts:
        analysis = post.get("analysis", {})
        
        tone = analysis.get("tone", "unknown")
        tones[tone] = tones.get(tone, 0) + 1
        
        format_type = analysis.get("format", "unknown")
        formats[format_type] = formats.get(format_type, 0) + 1
        
        depth = analysis.get("technical_depth", "unknown")
        technical_depths[depth] = technical_depths.get(depth, 0) + 1
    
    # Find strongest patterns
    strongest_tones = sorted(tones.items(), key=lambda x: x[1], reverse=True)[:3]
    strongest_formats = sorted(formats.items(), key=lambda x: x[1], reverse=True)[:3]
    strongest_depths = sorted(technical_depths.items(), key=lambda x: x[1], reverse=True)[:1]
    
    # Calculate recommended mix
    total_posts = len(posts)
    recommended_mix = []
    for topic, count in strongest_tones:
        percentage = int((count / total_posts) * 100) if total_posts > 0 else 0
        if percentage > 10:
            recommended_mix.append(f"{percentage}% {topic}")
    
    return {
        "updated_at": datetime.utcnow().isoformat(),
        "total_posts_analyzed": total_posts,
        "strongest_topics": [t[0] for t in strongest_tones],
        "strongest_formats": [f[0] for f in strongest_formats],
        "strongest_technical_depth": strongest_depths[0][0] if strongest_depths else "mixed",
        "strongest_patterns": [
            "Uses first-person perspective" if any(p.get("analysis", {}).get("first_person") for p in posts) else "Third-person perspective",
            "Includes concrete examples" if any(p.get("analysis", {}).get("includes_examples") for p in posts) else "Abstract explanations",
        ],
        "weak_patterns": [
            "Could use more questions for engagement" if sum(p.get("analysis", {}).get("question_count", 0) for p in posts) < len(posts) * 0.3 else "",
        ],
        "recommended_mix": ", ".join(recommended_mix) if recommended_mix else "Continue current mix",
        "average_word_count": sum(p.get("analysis", {}).get("word_count", 0) for p in posts) // max(total_posts, 1),
    }
