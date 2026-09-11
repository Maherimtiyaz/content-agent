"""Content draft generation and quality checking."""

from typing import Dict, Any, List, Optional
import os


class ContentWorkflow:
    """Generate and quality-check content drafts."""
    
    def __init__(self, use_demo: bool = False):
        self.use_demo = use_demo
        self.llm_provider = None
        
        if not use_demo:
            llm_provider = os.getenv("LLM_PROVIDER", "demo")
            if llm_provider == "openai":
                try:
                    from openai import OpenAI
                    self.llm_provider = OpenAI()
                except Exception:
                    self.use_demo = True
            elif llm_provider == "anthropic":
                try:
                    from anthropic import Anthropic
                    self.llm_provider = Anthropic()
                except Exception:
                    self.use_demo = True
    
    def generate_draft(
        self,
        idea: Dict[str, Any],
        profile: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Generate a full draft from an idea.
        
        Args:
            idea: Content idea to expand
            profile: User profile for context
        
        Returns:
            Draft with content and quality check results
        """
        if self.use_demo or not self.llm_provider:
            return self._generate_demo_draft(idea, profile)
        
        return self._generate_llm_draft(idea, profile)
    
    def _generate_demo_draft(
        self,
        idea: Dict[str, Any],
        profile: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Generate demo draft without LLM."""
        title = idea.get("title", "Untitled")
        hook = idea.get("hook", "")
        angle = idea.get("angle", "")
        format_type = idea.get("format", "short_post")
        
        # Create realistic demo content
        content = self._create_demo_content(title, hook, angle, format_type, profile)
        
        # Run quality check
        quality = self._quality_check(content, idea, profile)
        
        return {
            "title": title,
            "content": content,
            "format": format_type,
            "word_count": len(content.split()),
            "character_count": len(content),
            "quality_check": quality,
            "sources": idea.get("sources", []),
            "provenance": {
                "idea_title": title,
                "research_count": len(idea.get("supporting_research", [])),
            },
        }
    
    def _create_demo_content(
        self,
        title: str,
        hook: str,
        angle: str,
        format_type: str,
        profile: Dict[str, Any],
    ) -> str:
        """Create demo content based on idea parameters."""
        tone = profile.get("tone", "professional")
        interests = profile.get("interests", ["engineering"])
        
        # Template-based content generation for demo
        templates = {
            "short_post": f"""{hook}

Key insights from working with {interests[0]}:

• Implementation matters more than theory
• Start simple, iterate based on real feedback  
• Document your decisions as you go

What's your experience been? #Engineering""",
            
            "lesson_learned": f"""{hook}

After implementing {title.lower()}, here are the key lessons:

**1. Start with the simplest solution**
The temptation is to over-engineer from day one. Resist it.

**2. Measure everything**
You can't improve what you don't measure. Set up observability early.

**3. Document decisions**
Future you will thank present you for writing down why choices were made.

**4. Iterate based on feedback**
No design survives first contact with production. Plan to evolve.

This approach has saved me countless hours of rework.""",
            
            "technical_explanation": f"""{hook}

Here's a technical breakdown of {title.lower()}:

**The Problem**
Traditional approaches struggle with scalability and maintainability.

**The Solution**
A layered architecture with clear separation of concerns:

```python
# Simplified example
class System:
    def __init__(self):
        self.core = CoreLogic()
        self.adapter = ExternalAdapter()
    
    def process(self, input_data):
        validated = self.core.validate(input_data)
        return self.adapter.execute(validated)
```

**Key Takeaways**
- Abstraction enables flexibility
- Testing each layer independently catches issues early
- Clear interfaces make onboarding easier""",
        }
        
        return templates.get(format_type, templates["short_post"])
    
    def _quality_check(
        self,
        content: str,
        idea: Dict[str, Any],
        profile: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Run quality checks on generated content."""
        warnings = []
        errors = []
        
        # Check length
        word_count = len(content.split())
        char_count = len(content)
        
        if char_count > 280 and idea.get("format") == "short_post":
            warnings.append(f"Content exceeds X post limit ({char_count}/280)")
        
        # Check for generic AI phrases
        generic_phrases = [
            "in today's world",
            "leveraging synergies",
            "game-changer",
            "revolutionary",
            "cutting-edge",
        ]
        
        content_lower = content.lower()
        for phrase in generic_phrases:
            if phrase in content_lower:
                warnings.append(f"Generic phrase detected: '{phrase}'")
        
        # Check for hashtags (limit)
        hashtag_count = content.count("#")
        if hashtag_count > 3:
            warnings.append(f"Too many hashtags ({hashtag_count}). Consider using 2-3.")
        
        # Check for engagement bait
        bait_phrases = ["like and subscribe", "smash that like button", "drop a comment"]
        for phrase in bait_phrases:
            if phrase in content_lower:
                warnings.append(f"Engagement bait detected: '{phrase}'")
        
        # Check technical accuracy markers
        if idea.get("format") in ("technical_explanation", "lesson_learned"):
            if "```" not in content and "code" not in content_lower:
                warnings.append("Technical post might benefit from code examples")
        
        # Calculate score
        passed = len(errors) == 0
        score = max(0, 100 - len(warnings) * 15 - len(errors) * 30)
        
        return {
            "passed": passed,
            "score": score,
            "warnings": warnings,
            "errors": errors,
            "metrics": {
                "word_count": word_count,
                "character_count": char_count,
                "hashtag_count": hashtag_count,
            },
        }
    
    def _generate_llm_draft(
        self,
        idea: Dict[str, Any],
        profile: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Generate draft using LLM."""
        # Prepare prompt
        prompt = f"""Generate a {idea.get('format', 'post')} based on this idea:

IDEA:
- Title: {idea.get('title')}
- Hook: {idea.get('hook')}
- Angle: {idea.get('angle')}

PROFILE:
- Role: {profile.get('role')}
- Tone: {profile.get('tone')}
- Style: {profile.get('style_notes', '')}

IMPORTANT RULES:
1. Do NOT invent personal experiences, projects, or achievements
2. If specific details are unknown, keep statements general or ask for clarification
3. Focus on providing genuine value
4. Match the person's tone and style
5. Avoid generic motivational content

Generate content that is:
- Technically accurate
- Specific and concrete
- True to the person's expertise
- Useful to their audience"""

        try:
            response = self.llm_provider.chat.completions.create(
                model=os.getenv("LLM_MODEL", "gpt-4o-mini"),
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=500,
            )
            
            content = response.choices[0].message.content
            
            # Quality check
            quality = self._quality_check(content, idea, profile)
            
            return {
                "title": idea.get("title"),
                "content": content,
                "format": idea.get("format"),
                "word_count": len(content.split()),
                "quality_check": quality,
                "sources": idea.get("sources", []),
            }
            
        except Exception as e:
            print(f"[warning] LLM draft generation failed: {e}")
            return self._generate_demo_draft(idea, profile)
