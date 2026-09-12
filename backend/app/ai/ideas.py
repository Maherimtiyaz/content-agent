"""AI-powered content idea generation workflow."""

from typing import List, Dict, Any, Optional
import os


class IdeaWorkflow:
    """Generate content ideas from profile and research."""
    
    def __init__(self, use_demo: bool = False):
        self.use_demo = use_demo
        self.llm_provider = None
        
        if not use_demo:
            # Try to initialize LLM provider
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
    
    def generate_ideas(
        self,
        profile: Dict[str, Any],
        research: List[Dict[str, Any]],
        limit: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Generate content ideas based on profile and research.
        
        Args:
            profile: User's professional profile
            research: List of research items
            limit: Maximum number of ideas to generate
        
        Returns:
            List of structured content ideas
        """
        if self.use_demo or not self.llm_provider:
            return self._generate_demo_ideas(profile, research, limit)
        
        return self._generate_llm_ideas(profile, research, limit)
    
    def _generate_demo_ideas(
        self,
        profile: Dict[str, Any],
        research: List[Dict[str, Any]],
        limit: int,
    ) -> List[Dict[str, Any]]:
        """Generate demo ideas without LLM - using research patterns."""
        interests = profile.get("interests", ["AI engineering"])
        pillars = profile.get("content_pillars", ["technical insights"])
        
        # Separate creator posts from other research
        creator_posts = [r for r in research if r.get("source_type") == "creator_post"]
        other_research = [r for r in research if r.get("source_type") != "creator_post"]
        
        ideas = []
        
        # Priority 1: Create ideas inspired by creator posts (patterns, not copies)
        for post in creator_posts[:limit]:
            topics = post.get("topics", [])
            topic = topics[0] if topics else "AI engineering"
            content = post.get("content", "")
            creator = post.get("metadata", {}).get("creator", "unknown")
            
            # Extract pattern from the post, generate original angle
            idea = {
                "title": f"The {topic} Tradeoff: What Most Engineers Miss",
                "hook": f"Everyone talks about {topic.lower()}, but few mention this critical constraint...",
                "angle": f"Contrarian take based on industry patterns observed from @{creator}",
                "content_pillar": next((p for p in pillars if p.lower() in topic.lower()), pillars[0]),
                "supporting_knowledge": [],
                "supporting_research": [post.get("url", "")] if post.get("url") else [],
                "confidence": min(0.95, post.get("relevance_score", 0.8) + 0.1),
                "format": self._suggest_format(post),
                "why_now": f"Active discussion in the AI engineering community about {topic.lower()}",
                "why_fits_brand": f"Aligns with your focus on {topic} and {pillars[0]}",
                "sources": [post],
                "inspired_by_pattern": True,
            }
            ideas.append(idea)
        
        # Priority 2: Create ideas from other research
        remaining = limit - len(ideas)
        for item in other_research[:remaining]:
            topics = item.get("topics", [])
            topic = topics[0] if topics else interests[0]
            
            idea = {
                "title": f"{topic}: A Practical Framework for Production",
                "hook": f"After evaluating multiple approaches to {topic.lower()}, here's what actually works...",
                "angle": "Synthesis of recent developments with practical application",
                "content_pillar": next((p for p in pillars if p.lower() in topic.lower()), pillars[0]),
                "supporting_knowledge": [],
                "supporting_research": [item.get("url", "")] if item.get("url") else [],
                "confidence": item.get("relevance_score", 0.7),
                "format": self._suggest_format(item),
                "why_now": f"Recent developments in {topic} make this timely",
                "why_fits_brand": f"Aligns with your focus on {topic} and {pillars[0]}",
                "sources": [item],
            }
            ideas.append(idea)
        
        return ideas[:limit]
    
    def _generate_llm_ideas(
        self,
        profile: Dict[str, Any],
        research: List[Dict[str, Any]],
        limit: int,
    ) -> List[Dict[str, Any]]:
        """Generate ideas using LLM."""
        # Prepare context
        interests_str = ", ".join(profile.get("interests", []))
        pillars_str = ", ".join(profile.get("content_pillars", []))
        
        research_summary = "\n".join([
            f"- {r.get('title', 'Untitled')}: {r.get('summary', '')}"
            for r in research[:10]
        ])
        
        prompt = f"""You are helping a software engineer generate content ideas.

PROFILE:
- Role: {profile.get('role', 'Engineer')}
- Interests: {interests_str}
- Content Pillars: {pillars_str}
- Audience: {", ".join(profile.get('audience', []))}
- Tone: {profile.get('tone', 'professional')}

RECENT RESEARCH:
{research_summary}

Generate {limit} high-quality content ideas that:
1. Are grounded in the research provided
2. Match the person's expertise and interests
3. Provide genuine value to their audience
4. Avoid generic motivational content
5. Focus on technical substance

For each idea, provide:
- title: Catchy but accurate title
- hook: Opening line that grabs attention
- angle: Unique perspective or approach
- content_pillar: Which pillar this supports
- format: One of: short_post, thread, technical_explanation, lesson_learned, project_update, opinion, experiment
- confidence: 0.0-1.0 score of idea quality
- why_now: Why this is timely
- why_fits_brand: Why this matches their brand

Return as JSON array."""

        try:
            response = self.llm_provider.chat.completions.create(
                model=os.getenv("LLM_MODEL", "gpt-4o-mini"),
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=2000,
            )
            
            # Parse response (simplified - would need proper JSON parsing)
            ideas = self._parse_ideas_response(response.choices[0].message.content)
            return ideas[:limit]
            
        except Exception as e:
            print(f"[warning] LLM idea generation failed: {e}")
            return self._generate_demo_ideas(profile, research, limit)
    
    def _parse_ideas_response(self, response_text: str) -> List[Dict[str, Any]]:
        """Parse LLM response into structured ideas."""
        # Simplified parsing - in production would use proper JSON parsing
        import json
        try:
            # Try to extract JSON from response
            start = response_text.find("[")
            end = response_text.rfind("]") + 1
            if start >= 0 and end > start:
                json_str = response_text[start:end]
                return json.loads(json_str)
        except Exception:
            pass
        
        return []
    
    def _suggest_format(self, research_item: Dict[str, Any]) -> str:
        """Suggest content format based on research item."""
        source_type = research_item.get("source_type", "")
        
        if source_type == "paper":
            return "technical_explanation"
        elif source_type == "github":
            return "project_update"
        elif source_type in ("blog", "technical_blog"):
            return "lesson_learned"
        else:
            return "short_post"
