"""
Unit tests for task factory functionality.
"""

from src.task_factory import TaskFactory, task_factory
from src.tasks import Task
import unittest
import sys
from pathlib import Path

# Add src to path for imports
test_dir = Path(__file__).parent
src_dir = test_dir.parent / "src"
sys.path.insert(0, str(src_dir))


class TestTask(unittest.TestCase):
    """Test Task class functionality."""

    def test_task_creation(self):
        """Test basic task creation."""
        task = Task(
            task_name="test_task",
            description="Test task description",
            task_type="summary"
        )

        self.assertEqual(task.task_name, "test_task")
        self.assertEqual(task.description, "Test task description")
        self.assertEqual(task.task_type, "summary")
        self.assertEqual(task.result, "")
        self.assertIsInstance(task.attributes, dict)

    def test_task_type_validation(self):
        """Test task type validation."""
        # Valid task types
        for task_type in ['code_interpretation', 'summary', 'scoring']:
            task = Task(
                task_name="test",
                description="test",
                task_type=task_type
            )
            self.assertEqual(task.task_type, task_type)

    def test_task_properties(self):
        """Test task type properties."""
        # Test code interpretation task
        ci_task = Task(task_name="ci", description="ci",
                       task_type="code_interpretation")
        self.assertTrue(ci_task.is_code_interpretation)
        self.assertFalse(ci_task.is_summary)
        self.assertFalse(ci_task.is_scoring)

        # Test summary task
        sum_task = Task(task_name="sum", description="sum",
                        task_type="summary")
        self.assertFalse(sum_task.is_code_interpretation)
        self.assertTrue(sum_task.is_summary)
        self.assertFalse(sum_task.is_scoring)

        # Test scoring task
        score_task = Task(task_name="score",
                          description="score", task_type="scoring")
        self.assertFalse(score_task.is_code_interpretation)
        self.assertFalse(score_task.is_summary)
        self.assertTrue(score_task.is_scoring)

    def test_task_with_attributes(self):
        """Test task creation with attributes."""
        attributes = {"condition": "test", "domain": "test_domain"}
        task = Task(
            task_name="attr_test",
            description="Test with attributes",
            task_type="summary",
            attributes=attributes
        )

        self.assertEqual(task.attributes["condition"], "test")
        self.assertEqual(task.attributes["domain"], "test_domain")


class TestTaskFactory(unittest.TestCase):
    """Test TaskFactory class functionality."""

    def setUp(self):
        self.factory = TaskFactory()

    def test_create_task_generic(self):
        """Test generic task creation method."""
        task = self.factory.create_task(
            task_type="summary",
            task_name="generic_test",
            description="Generic task test",
            system_prompt="System prompt",
            user_prompt="User prompt",
            attributes={"test": "value"}
        )

        self.assertIsInstance(task, Task)
        self.assertEqual(task.task_type, "summary")
        self.assertEqual(task.task_name, "generic_test")
        self.assertEqual(task.system_prompt, "System prompt")
        self.assertEqual(task.attributes["test"], "value")

    def test_create_code_interpretation_task(self):
        """Test code interpretation task creation."""
        task = self.factory.create_code_interpretation_task(
            task_name="ci_test",
            description="Code interpretation test",
            system_prompt="Explain code",
            user_prompt="Code: {prolog}",
            attributes={"language": "prolog"}
        )

        self.assertIsInstance(task, Task)
        self.assertEqual(task.task_type, "code_interpretation")
        self.assertEqual(task.task_name, "ci_test")
        self.assertTrue(task.is_code_interpretation)
        self.assertEqual(task.attributes["language"], "prolog")

    def test_create_summary_task(self):
        """Test summary task creation."""
        task = self.factory.create_summary_task(
            task_name="summary_test",
            description="Summary test",
            system_prompt="Summarize",
            user_prompt="Task: {description}",
            attributes={"condition": "test_condition"}
        )

        self.assertIsInstance(task, Task)
        self.assertEqual(task.task_type, "summary")
        self.assertEqual(task.task_name, "summary_test")
        self.assertTrue(task.is_summary)
        self.assertEqual(task.attributes["condition"], "test_condition")

    def test_create_scoring_task(self):
        """Test scoring task creation."""
        task = self.factory.create_scoring_task(
            task_name="scoring_test",
            description="Scoring test",
            system_prompt="Rate the answer",
            user_prompt="Answer: {answer}",
            attributes={"scorer": "test_scorer"}
        )

        self.assertIsInstance(task, Task)
        self.assertEqual(task.task_type, "scoring")
        self.assertEqual(task.task_name, "scoring_test")
        self.assertTrue(task.is_scoring)
        self.assertEqual(task.attributes["scorer"], "test_scorer")

    def test_create_task_with_empty_attributes(self):
        """Test task creation with no attributes."""
        task = self.factory.create_task(
            task_type="summary",
            task_name="no_attrs",
            description="No attributes test"
        )

        self.assertIsInstance(task.attributes, dict)
        self.assertEqual(len(task.attributes), 0)

    def test_create_task_invalid_type(self):
        """Test task creation with invalid type."""
        with self.assertRaises(ValueError):
            self.factory.create_task(
                task_type="invalid_type",
                task_name="invalid",
                description="Invalid type test"
            )


class TestGlobalTaskFactory(unittest.TestCase):
    """Test the global task factory instance."""

    def test_global_factory_exists(self):
        """Test that global factory exists and works."""
        self.assertIsInstance(task_factory, TaskFactory)

        task = task_factory.create_summary_task(
            task_name="global_test",
            description="Global factory test",
            system_prompt="Test",
            user_prompt="Test"
        )

        self.assertIsInstance(task, Task)
        self.assertEqual(task.task_type, "summary")

    def test_factory_methods_consistency(self):
        """Test that all factory methods create consistent tasks."""
        # Create tasks using different methods
        ci_task = task_factory.create_code_interpretation_task(
            "ci", "CI task", "sys", "user"
        )
        sum_task = task_factory.create_summary_task(
            "sum", "Summary task", "sys", "user"
        )
        score_task = task_factory.create_scoring_task(
            "score", "Scoring task", "sys", "user"
        )

        # All should be Task instances
        self.assertIsInstance(ci_task, Task)
        self.assertIsInstance(sum_task, Task)
        self.assertIsInstance(score_task, Task)

        # Each should have correct type
        self.assertEqual(ci_task.task_type, "code_interpretation")
        self.assertEqual(sum_task.task_type, "summary")
        self.assertEqual(score_task.task_type, "scoring")


if __name__ == '__main__':
    unittest.main()
