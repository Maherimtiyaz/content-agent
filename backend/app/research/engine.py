"""Research engine with multi-source support."""

from typing import List, Dict, Any, Optional
from pathlib import Path
import json
from datetime import datetime


class ResearchProvider:
    """Base interface for research providers."""
    
    def search(self, query: str, **kwargs) -> List[Dict[str, Any]]:
        """Search for relevant content."""
        raise NotImplementedError


class DemoProvider(ResearchProvider):
    """Demo provider that returns mock research data for testing."""
    
    def __init__(self):
        self.demo_data = [
            {
                "title": "New LLM Framework Released",
                "source": "Tech Blog",
                "source_type": "blog",
                "url": "https://example.com/llm-framework",
                "published_date": "2024-01-15",
                "summary": "A new framework for building LLM applications has been released with improved RAG capabilities.",
                "topics": ["LLMs", "AI engineering", "RAG"],
                "relevance_score": 0.85,
                "brand_fit_score": 0.80,
                "content_potential": "high",
            },
            {
                "title": "Best Practices for AI Agent Architecture",
                "source": "Engineering Blog",
                "source_type": "technical_blog",
                "url": "https://example.com/agent-architecture",
                "published_date": "2024-01-14",
                "summary": "Key patterns and anti-patterns in designing AI agent systems for production.",
                "topics": ["AI agents", "software architecture", "AI engineering"],
                "relevance_score": 0.92,
                "brand_fit_score": 0.88,
                "content_potential": "high",
            },
            {
                "title": "MCP Protocol Gains Traction",
                "source": "GitHub Trends",
                "source_type": "github",
                "url": "https://github.com/example/mcp",
                "published_date": "2024-01-13",
                "summary": "Model Context Protocol sees rapid adoption among AI tool builders.",
                "topics": ["MCP", "AI tools", "developer tools"],
                "relevance_score": 0.78,
                "brand_fit_score": 0.75,
                "content_potential": "medium",
            },
            {
                "title": "RAG Performance Optimization Techniques",
                "source": "Research Paper",
                "source_type": "paper",
                "url": "https://arxiv.org/example/rag-opt",
                "published_date": "2024-01-12",
                "summary": "Novel approaches to improving retrieval-augmented generation latency and accuracy.",
                "topics": ["RAG", "LLMs", "performance"],
                "relevance_score": 0.88,
                "brand_fit_score": 0.82,
                "content_potential": "high",
            },
            {
                "title": "Backend Engineering Trends 2024",
                "source": "Industry Report",
                "source_type": "report",
                "url": "https://example.com/backend-trends",
                "published_date": "2024-01-10",
                "summary": "Survey of backend engineering practices and emerging technologies.",
                "topics": ["backend engineering", "developer tools", "trends"],
                "relevance_score": 0.72,
                "brand_fit_score": 0.70,
                "content_potential": "medium",
            },
        ]
    
    def search(self, query: str, **kwargs) -> List[Dict[str, Any]]:
        """Return demo results matching the query topics."""
        query_lower = query.lower()
        results = []
        
        for item in self.demo_data:
            # Simple keyword matching for demo
            item_topics = " ".join(item.get("topics", [])).lower()
            if any(word in item_topics for word in query_lower.split()):
                results.append(item.copy())
        
        return results


class DuckDuckGoProvider(ResearchProvider):
    """Web search using DuckDuckGo (no API key required)."""
    
    def search(self, query: str, num_results: int = 10, **kwargs) -> List[Dict[str, Any]]:
        try:
            from duckduckgo_search import DDGS
            
            results = []
            with DDGS() as ddgs:
                search_results = list(ddgs.text(query, max_results=num_results))
                
                for result in search_results:
                    results.append({
                        "title": result.get("title", "Untitled"),
                        "source": "DuckDuckGo",
                        "source_type": "web",
                        "url": result.get("href", ""),
                        "published_date": None,
                        "summary": result.get("body", ""),
                        "topics": [],
                        "relevance_score": 0.5,  # Would need LLM scoring
                        "brand_fit_score": 0.5,
                        "content_potential": "unknown",
                    })
            
            return results
        except ImportError:
            raise RuntimeError("duckduckgo-search not installed")
        except Exception as e:
            # Graceful degradation
            print(f"[warning] DuckDuckGo search failed: {e}")
            return []


class LocalCreatorPostsProvider(ResearchProvider):
    """Loads creator research from local JSONL files."""
    
    def __init__(self, data_dir: str = "data/creator_research"):
        self.data_dir = Path(data_dir)
    
    def search(self, query: str, **kwargs) -> List[Dict[str, Any]]:
        """Load all creator posts regardless of query (filtering happens later)."""
        if not self.data_dir.exists():
            print(f"[info] Creator research directory not found: {self.data_dir}")
            return []
        
        items = []
        files_found = 0
        
        for file_path in self.data_dir.glob("*.jsonl"):
            files_found += 1
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    for line_num, line in enumerate(f, 1):
                        line = line.strip()
                        if not line:
                            continue
                        try:
                            data = json.loads(line)
                            item = self._parse_post(data, str(file_path))
                            if item:
                                items.append(item)
                        except json.JSONDecodeError:
                            # Skip malformed lines
                            continue
            except Exception as e:
                # Skip unreadable files
                print(f"[warning] Could not read {file_path}: {e}")
                continue
        
        if files_found > 0:
            print(f"[info] Loaded {len(items)} creator posts from {files_found} file(s)")
        else:
            print(f"[info] No .jsonl files found in {self.data_dir}")
        
        return items
    
    def _parse_post(self, data: Dict[str, Any], source_file: str) -> Optional[Dict[str, Any]]:
        content = data.get('content', '')
        if not content:
            return None
        
        creator = data.get('creator', 'unknown')
        url = data.get('url', f'file://{source_file}')
        published_at = data.get('published_at')
        
        # Extract topics from content or use provided
        topics = data.get('topics', [])
        if not topics and len(content) > 50:
            # Simple heuristic: first sentence often contains topic
            topics = [content.split('.')[0][:50]]
        
        return {
            "title": f"Post by @{creator}",
            "source": f"Creator: @{creator}",
            "source_type": "creator_post",
            "url": url,
            "published_date": published_at,
            "summary": content[:200],
            "content": content,
            "topics": topics,
            "relevance_score": 0.9,  # High relevance since user selected these creators
            "brand_fit_score": 0.85,
            "content_potential": "high",
            "metadata": {
                'creator': creator,
                'original_length': len(content),
                'published_at': published_at
            }
        }


class ResearchEngine:
    """Multi-source research engine."""
    
    def __init__(self, use_demo: bool = False):
        self.providers: List[ResearchProvider] = []
        
        # Always add LocalCreatorPostsProvider first (if directory exists)
        try:
            self.providers.append(LocalCreatorPostsProvider())
        except Exception as e:
            print(f"[warning] Could not initialize creator posts provider: {e}")
        
        if use_demo:
            self.providers.append(DemoProvider())
        else:
            # Try to add real providers
            try:
                self.providers.append(DuckDuckGoProvider())
            except Exception:
                # Fall back to demo if no providers available
                self.providers.append(DemoProvider())
                print("[warning] Using demo mode - no API keys configured")
    
    def research(
        self, 
        topics: List[str], 
        deep: bool = False,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Research multiple topics across all providers.
        
        Args:
            topics: List of topics to research
            deep: If True, do deeper research with more sources
            **kwargs: Additional provider-specific arguments
        
        Returns:
            List of normalized research items
        """
        all_results = []
        seen_urls = set()
        
        for topic in topics:
            for provider in self.providers:
                try:
                    num_results = 20 if deep else 10
                    results = provider.search(topic, num_results=num_results, **kwargs)
                    
                    for item in results:
                        # Deduplicate by URL
                        url = item.get("url", "")
                        if url and url in seen_urls:
                            continue
                        seen_urls.add(url)
                        
                        # Normalize and enrich
                        enriched = self._enrich_item(item, topic)
                        all_results.append(enriched)
                        
                except Exception as e:
                    # Continue with other providers even if one fails
                    print(f"[warning] Provider failed for topic '{topic}': {e}")
                    continue
        
        # Sort by relevance score
        all_results.sort(
            key=lambda x: (x.get("relevance_score", 0) or 0),
            reverse=True
        )
        
        return all_results
    
    def _enrich_item(self, item: Dict[str, Any], topic: str) -> Dict[str, Any]:
        """Enrich research item with additional metadata."""
        # Add discovery timestamp
        item["discovered_at"] = datetime.utcnow().isoformat()
        item["queried_topic"] = topic
        
        # Ensure all required fields exist
        item.setdefault("key_points", [])
        item.setdefault("credibility_score", 0.5)
        item.setdefault("novelty_score", 0.5)
        item.setdefault("technical_depth", "medium")
        
        return item
