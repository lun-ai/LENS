"""
Simplified LENS Task Definitions

Essential task model with minimal attributes. All task behavior is driven by
task_type and attributes rather than complex inheritance.
"""

from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional, Literal


class Task(BaseModel):
    """Universal task model for all LENS operations."""
    task_name: str
    description: str
    task_type: Literal['code_interpretation', 'summary',
                       'scoring', 'ilp_learning'] = 'summary'
    system_prompt: str = ''
    user_prompt: str = ''
    attributes: Dict[str, Any] = Field(default_factory=dict)

    # Result field (populated by pipelines)
    result: str = ''  # Generic result field for any task output

    class Config:
        arbitrary_types_allowed = True

    @property
    def is_code_interpretation(self) -> bool:
        """Check if this is a code interpretation task."""
        return self.task_type == 'code_interpretation'

    @property
    def is_summary(self) -> bool:
        """Check if this is a summary task."""
        return self.task_type == 'summary'

    @property
    def is_scoring(self) -> bool:
        """Check if this is a scoring task."""
        return self.task_type == 'scoring'

    @property
    def is_ilp_learning(self) -> bool:
        """Check if this is an ILP learning task."""
        return self.task_type == 'ilp_learning'
