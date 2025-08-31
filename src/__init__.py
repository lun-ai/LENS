"""
LENS: Learning Advanced Neural Strategies Framework

A hybrid neuro-symbolic framework that generates human-interpretable explanations
to improve human generalization on unseen tasks.

Simplified implementation focusing on essential functionality:
- Core task models
- Essential pipelines  
- Task factory for creation
- Workflow orchestration
"""

from .tasks import Task
from .pipelines import (
    run_summary_pipeline, run_scoring_pipeline, run_code_interpretation_pipeline,
    CodeInterpretationPipeline, SummaryExplanationPipeline, ResponseScoringPipeline
)
from .task_factory import task_factory
from .workflow import WorkflowConfig, LENSWorkflow

__version__ = "0.2.0"

__all__ = [
    # Core Task
    'Task',

    # Pipeline Functions
    'run_summary_pipeline', 'run_scoring_pipeline', 'run_code_interpretation_pipeline',

    # Pipeline Classes
    'CodeInterpretationPipeline', 'SummaryExplanationPipeline', 'ResponseScoringPipeline',

    # Task Factory
    'task_factory',

    # Workflow
    'WorkflowConfig', 'LENSWorkflow'
]
