"""Workflow Run model for tracking AI workflow executions."""

from datetime import datetime
from typing import Optional
from sqlalchemy import String, DateTime, ForeignKey, Text, Enum as SQLEnum, JSON, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum
import uuid

from app.db.base import Base


class WorkflowStatus(str, enum.Enum):
    """Workflow execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class WorkflowType(str, enum.Enum):
    """Types of workflows."""
    RESEARCH = "research"
    IDEA_GENERATION = "idea_generation"
    CONTENT_DRAFTING = "content_drafting"
    QUALITY_CHECK = "quality_check"
    ANALYTICS_ANALYSIS = "analytics_analysis"


class WorkflowRun(Base):
    """Record of an AI workflow execution."""
    
    __tablename__ = "workflow_runs"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    
    # Execution identification
    execution_id: Mapped[str] = mapped_column(
        String(255), 
        default=lambda: str(uuid.uuid4()), 
        unique=True, 
        nullable=False
    )
    
    # Workflow details
    workflow_type: Mapped[WorkflowType] = mapped_column(
        SQLEnum(WorkflowType), nullable=False
    )
    workflow_name: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # Status tracking
    status: Mapped[WorkflowStatus] = mapped_column(
        SQLEnum(WorkflowStatus),
        default=WorkflowStatus.PENDING,
        nullable=False
    )
    
    # Model/LLM information (if applicable)
    model_used: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Token usage (if available from LLM provider)
    input_tokens: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    output_tokens: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    total_tokens: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Input/output references (not storing actual content for security)
    input_references: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    output_reference: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Error handling
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Timestamps
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    
    def __repr__(self) -> str:
        return f"<WorkflowRun(id={self.id}, type={self.workflow_type.value}, status={self.status.value})>"
