#!/usr/bin/env python
"""Script to create initial migration without database connection."""

import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from alembic.config import Config
from alembic import command

# Create alembic config
alembic_cfg = Config("alembic.ini")

# Generate revision
command.revision(
    alembic_cfg, 
    message="Initial migration: users, brand_profiles, content_pillars, knowledge_items",
    autogenerate=True
)

print("Migration created successfully!")
