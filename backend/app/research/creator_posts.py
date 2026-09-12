import json
import os
from pathlib import Path
from typing import List, Dict, Any
from app.research.providers.base import ResearchProvider
from app.models.research_item import ResearchItem

class LocalCreatorPostsProvider(ResearchProvider):
    """
    Loads creator research from local JSONL files.
    Directory: backend/data/creator_research/
    """
    
    def __init__(self, data_dir: str = "data/creator_research"):
        self.data_dir = Path(data_dir)
    
    def fetch(self, topics: List[str], **kwargs) -> List[ResearchItem]:
        if not self.data_dir.exists():
            return []
        
        items = []
        for file_path in self.data_dir.glob("*.jsonl"):
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
                        except json.JSONDecodeError as e:
                            # Skip malformed lines
                            continue
            except Exception:
                # Skip unreadable files
                continue
        
        return items
    
    def _parse_post(self, data: Dict[str, Any], source_file: str) -> ResearchItem:
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
        
        return ResearchItem(
            title=f"Post by @{creator}",
            summary=content[:200],  # Truncate for summary
            content=content,
            source=f"Creator: @{creator}",
            source_type="creator_post",
            url=url,
            topics=topics,
            metadata={
                'creator': creator,
                'original_length': len(content),
                'published_at': published_at
            }
        )
