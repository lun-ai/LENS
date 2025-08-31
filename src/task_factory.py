"""
Simplified LENS Task Factory

Essential task creation with the unified Task model.
"""

from typing import Dict, Any, List, Optional
from .tasks import Task


class TaskFactory:
    """Factory for creating validated LENS tasks."""

    def create_task(self, task_type: str, task_name: str, description: str,
                    system_prompt: str = '', user_prompt: str = '',
                    attributes: Dict[str, Any] = None) -> Task:
        """Create a task of the specified type."""
        return Task(
            task_name=task_name,
            description=description,
            task_type=task_type,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            attributes=attributes or {}
        )

    def create_code_interpretation_task(self, task_name: str, description: str,
                                        system_prompt: str, user_prompt: str,
                                        attributes: Dict[str, Any] = None) -> Task:
        """Create a code interpretation task."""
        return self.create_task('code_interpretation', task_name, description,
                                system_prompt, user_prompt, attributes)

    def create_summary_task(self, task_name: str, description: str,
                            system_prompt: str, user_prompt: str,
                            attributes: Dict[str, Any] = None) -> Task:
        """Create a summary task."""
        return self.create_task('summary', task_name, description,
                                system_prompt, user_prompt, attributes)

    def create_scoring_task(self, task_name: str, description: str,
                            system_prompt: str, user_prompt: str,
                            attributes: Dict[str, Any] = None) -> Task:
        """Create a scoring task."""
        return self.create_task('scoring', task_name, description,
                                system_prompt, user_prompt, attributes)

    def create_ilp_learning_task(self, task_name: str, description: str,
                                 attributes: Dict[str, Any] = None) -> Task:
        """Create an ILP learning task.
        """
        return self.create_task(
            'ilp_learning', task_name, description,
            system_prompt='',  # Not used for ILP learning
            user_prompt='',    # Not used for ILP learning
            attributes=attributes
        )


# Global factory instance
task_factory = TaskFactory()
