"""AI-powered content idea generation workflow."""

from typing import List, Dict, Any
import json
import os

from openai import OpenAI


class IdeaWorkflow:
    """Generate content ideas from profile and research."""

    def __init__(self, use_demo: bool = False):
        self.use_demo = use_demo
        self.llm_provider = None

        if use_demo:
            return

        llm_provider = os.getenv("LLM_PROVIDER", "demo").lower()

        if llm_provider == "openai":
            try:
                self.llm_provider = OpenAI(
                    api_key=os.getenv("LLM_API_KEY", "ollama"),
                    base_url=os.getenv(
                        "LLM_BASE_URL",
                        "http://localhost:11434/v1",
                    ),
                )

                print(
                    f"[info] LLM configured: "
                    f"{os.getenv('LLM_MODEL', 'gpt-4o-mini')} "
                    f"@ {os.getenv('LLM_BASE_URL', 'default')}"
                )

            except Exception as e:
                print(f"[error] LLM initialization failed: {e}")
                self.llm_provider = None
                self.use_demo = True

        elif llm_provider == "anthropic":
            try:
                from anthropic import Anthropic

                self.llm_provider = Anthropic(
                    api_key=os.getenv("LLM_API_KEY")
                )

            except Exception as e:
                print(f"[error] Anthropic initialization failed: {e}")
                self.llm_provider = None
                self.use_demo = True

        else:
            print(
                f"[warning] Unsupported or missing LLM_PROVIDER: "
                f"{llm_provider}"
            )
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
            profile: User's professional profile.
            research: List of research items.
            limit: Maximum number of ideas to generate.

        Returns:
            List of structured content ideas.
        """

        if self.use_demo or not self.llm_provider:
            print("[info] Using research-based fallback idea generation")
            return self._generate_demo_ideas(profile, research, limit)

        print("[info] Generating ideas using LLM...")
        return self._generate_llm_ideas(profile, research, limit)

    def _generate_demo_ideas(
        self,
        profile: Dict[str, Any],
        research: List[Dict[str, Any]],
        limit: int,
    ) -> List[Dict[str, Any]]:
        """
        Generate ideas without an LLM.

        This fallback intentionally uses creator research when available
        instead of the old generic 'A Practical Framework for Production'
        template.
        """

        interests = profile.get(
            "interests",
            ["AI engineering"],
        )

        pillars = profile.get(
            "content_pillars",
            ["technical insights"],
        )

        creator_posts = [
            r
            for r in research
            if r.get("source_type") == "creator_post"
        ]

        other_research = [
            r
            for r in research
            if r.get("source_type") != "creator_post"
        ]

        ideas = []

        # Priority 1: Generate ideas from creator research.
        for post in creator_posts[:limit]:
            topics = post.get("topics", [])

            topic = (
                topics[0]
                if topics
                else "AI engineering"
            )

            creator = (
                post.get("metadata", {})
                .get("creator", "unknown")
            )

            idea = {
                "title": (
                    f"The {topic} Tradeoff: "
                    "What Most Engineers Miss"
                ),
                "hook": (
                    f"Everyone talks about {topic.lower()}, "
                    "but few mention this critical constraint..."
                ),
                "angle": (
                    "Contrarian take based on patterns "
                    f"observed from @{creator}"
                ),
                "content_pillar": self._match_pillar(
                    topic,
                    pillars,
                ),
                "supporting_knowledge": [],
                "supporting_research": (
                    [post.get("url")]
                    if post.get("url")
                    else []
                ),
                "confidence": min(
                    0.95,
                    post.get("relevance_score", 0.8) + 0.1,
                ),
                "format": self._suggest_format(post),
                "why_now": (
                    "Active discussion in the AI engineering "
                    f"community about {topic.lower()}"
                ),
                "why_fits_brand": (
                    f"Aligns with your focus on {topic} "
                    f"and {pillars[0]}"
                ),
                "sources": [post],
                "inspired_by_pattern": True,
            }

            ideas.append(idea)

        # Priority 2: Use other research if more ideas are needed.
        remaining = limit - len(ideas)

        for item in other_research[:remaining]:
            topics = item.get("topics", [])

            topic = (
                topics[0]
                if topics
                else interests[0]
            )

            idea = {
                "title": (
                    f"{topic}: "
                    "Engineering Lessons From Recent Research"
                ),
                "hook": (
                    f"What recent work on {topic.lower()} "
                    "reveals about building reliable systems..."
                ),
                "angle": (
                    "Research-backed synthesis with "
                    "practical engineering implications"
                ),
                "content_pillar": self._match_pillar(
                    topic,
                    pillars,
                ),
                "supporting_knowledge": [],
                "supporting_research": (
                    [item.get("url")]
                    if item.get("url")
                    else []
                ),
                "confidence": item.get(
                    "relevance_score",
                    0.7,
                ),
                "format": self._suggest_format(item),
                "why_now": (
                    f"Recent developments in {topic} "
                    "make this timely"
                ),
                "why_fits_brand": (
                    f"Aligns with your focus on {topic} "
                    f"and {pillars[0]}"
                ),
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
        """Generate ideas using the configured LLM."""

        interests_str = ", ".join(
            profile.get("interests", [])
        )

        pillars_str = ", ".join(
            profile.get("content_pillars", [])
        )

        audience_str = ", ".join(
            profile.get("audience", [])
        )

        # Include actual creator content, not just titles.
        research_parts = []

        for index, item in enumerate(research[:20], 1):
            creator = (
                item.get("metadata", {})
                .get("creator")
            )

            source = (
                f"@{creator}"
                if creator
                else item.get("source", "Unknown source")
            )

            content = (
                item.get("content")
                or item.get("summary")
                or ""
            )

            research_parts.append(
                f"""RESEARCH ITEM {index}
Source: {source}
Title: {item.get("title", "Untitled")}
Topics: {", ".join(item.get("topics", []))}
Content:
{content}
"""
            )

        research_context = "\n".join(research_parts)

        prompt = f"""
You are helping an AI engineer create technically useful content.

PROFILE
Role: {profile.get("role", "AI Engineer")}
Interests: {interests_str}
Content pillars: {pillars_str}
Audience: {audience_str}
Tone: {profile.get("tone", "professional but approachable")}
Style: {profile.get("style_notes", "concise, technical, example-driven")}
Topics to avoid: {", ".join(profile.get("topics_to_avoid", []))}

RESEARCH
The research below comes from technical sources and selected AI
engineering creators. Use the actual substance of the research.
Do not merely repeat creator names or generic topic labels.

{research_context}

TASK

Generate exactly {limit} original content ideas.

Requirements:

1. Ground every idea in one or more research items.
2. Use specific technical insights from the research.
3. Prefer useful engineering tradeoffs, architecture decisions,
   failure modes, experiments, benchmarks, or practical lessons.
4. Do not invent personal experiences for the author.
5. Do not copy or imitate a creator's wording.
6. Do not produce generic titles such as:
   - "A Practical Framework for Production"
   - "Lessons from Best Practices"
   - "Things I Learned"
7. Avoid motivational fluff, hype, and engagement bait.
8. Make each idea meaningfully different.
9. The audience is software and AI engineers.
10. The ideas should be technically specific enough that a strong
    draft can be written from them.

For each idea return:

- title
- hook
- angle
- content_pillar
- format
- confidence
- why_now
- why_fits_brand
- research_basis

Allowed formats:
short_post
thread
technical_explanation
lesson_learned
project_update
opinion
experiment
emerging_tech
engineering_lessons

Return ONLY a valid JSON array.
"""

        try:
            response = self.llm_provider.chat.completions.create(
                model=os.getenv(
                    "LLM_MODEL",
                    "llama3.1:8b",
                ),
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You generate precise technical content "
                            "ideas for software engineers. "
                            "Return valid JSON only."
                        ),
                    },
                    {
                        "role": "user",
                        "content": prompt,
                    },
                ],
                temperature=0.7,
                max_tokens=3000,
            )

            response_text = (
                response.choices[0]
                .message
                .content
                or ""
            )

            ideas = self._parse_ideas_response(
                response_text
            )

            if not ideas:
                raise ValueError(
                    "LLM returned no parseable ideas"
                )

            return ideas[:limit]

        except Exception as e:
            # Do NOT silently turn an LLM failure into the old
            # generic template. Surface the actual failure.
            raise RuntimeError(
                f"LLM idea generation failed: {e}"
            ) from e

    def _parse_ideas_response(
        self,
        response_text: str,
    ) -> List[Dict[str, Any]]:
        """Parse an LLM JSON-array response."""

        try:
            response_text = response_text.strip()

            # Remove optional markdown JSON fences.
            if response_text.startswith("```"):
                lines = response_text.splitlines()

                if lines:
                    lines = lines[1:]

                if lines and lines[-1].strip() == "```":
                    lines = lines[:-1]

                response_text = "\n".join(lines).strip()

            # First try direct JSON parsing.
            parsed = json.loads(response_text)

            if isinstance(parsed, list):
                return parsed

        except json.JSONDecodeError:
            pass

        # Fallback: extract the first JSON array.
        try:
            start = response_text.find("[")
            end = response_text.rfind("]")

            if start >= 0 and end > start:
                json_str = response_text[start:end + 1]
                parsed = json.loads(json_str)

                if isinstance(parsed, list):
                    return parsed

        except Exception:
            pass

        return []

    def _match_pillar(
        self,
        topic: str,
        pillars: List[str],
    ) -> str:
        """Find the most relevant content pillar."""

        topic_lower = topic.lower()

        for pillar in pillars:
            if pillar.lower() in topic_lower:
                return pillar

        return pillars[0] if pillars else "technical insights"

    def _suggest_format(
        self,
        research_item: Dict[str, Any],
    ) -> str:
        """Suggest content format based on research type."""

        source_type = research_item.get(
            "source_type",
            "",
        )

        if source_type == "paper":
            return "technical_explanation"

        if source_type == "github":
            return "project_update"

        if source_type in (
            "blog",
            "technical_blog",
        ):
            return "lesson_learned"

        if source_type == "creator_post":
            return "engineering_lessons"

        return "short_post"
