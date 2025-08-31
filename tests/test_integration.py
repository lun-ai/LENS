"""
Integration tests for LENS pipelines.
"""

from src.pipelines import CodeInterpretationPipeline, SummaryExplanationPipeline, ResponseScoringPipeline
from src.tasks import Task
from src.task_factory import task_factory
import unittest
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add src to path for imports
test_dir = Path(__file__).parent
src_dir = test_dir.parent / "src"
sys.path.insert(0, str(src_dir))


class TestTaskFactoryPipelineIntegration(unittest.TestCase):
    """Test integration between task factory and pipelines."""

    """Test error handling in pipelines."""

    def setUp(self):
        self.api_configs = [{"api_key": "test_key", "model": "test-model"}]

    def test_task_factory_creates_compatible_tasks(self):
        """Test that task factory creates tasks compatible with pipelines."""
        # Create tasks of different types
        ci_task = task_factory.create_code_interpretation_task(
            "ci_test", "CI task", "Explain code", "Code: {code}",
            attributes={"code": "test_code"}
        )
        summary_task = task_factory.create_summary_task(
            "sum_test", "Summary task", "Summarize", "Content: {content}",
            attributes={"content": "test_content"}
        )
        scoring_task = task_factory.create_scoring_task(
            "score_test", "Scoring task", "Score", "Answer: {answer}",
            attributes={"answer": "test_answer"}
        )

        # Verify task types
        self.assertTrue(ci_task.is_code_interpretation)
        self.assertTrue(summary_task.is_summary)
        self.assertTrue(scoring_task.is_scoring)

        # Verify tasks have required attributes
        self.assertIn("code", ci_task.attributes)
        self.assertIn("content", summary_task.attributes)
        self.assertIn("answer", scoring_task.attributes)

    @patch('src.pipelines.generate_response')
    def test_end_to_end_pipeline_execution(self, mock_generate):
        """Test running tasks through appropriate pipelines."""
        mock_generate.side_effect = [
            {"test-model": "Interpreted code result"},
            {"test-model": "Summary result"},
            {"test-model": "Score: 8/10"}
        ]

        # Create tasks
        ci_task = task_factory.create_code_interpretation_task(
            "test_ci", "Test CI", "Explain", "Code: {code}",
            attributes={"code": "test_prolog"}
        )
        summary_task = task_factory.create_summary_task(
            "test_summary", "Test Summary", "Summarize", "Content: {content}",
            attributes={"content": "test_content"}
        )
        scoring_task = task_factory.create_scoring_task(
            "test_scoring", "Test Scoring", "Score", "Answer: {answer}",
            attributes={"answer": "test_answer"}
        )

        # Run through pipelines
        ci_pipeline = CodeInterpretationPipeline(self.api_configs)
        ci_tasks, ci_results = ci_pipeline.run([ci_task])

        # Use result in second pipeline
        summary_pipeline = SummaryExplanationPipeline(self.api_configs)
        summary_tasks, summary_results = summary_pipeline.run([summary_task])

        scoring_pipeline = ResponseScoringPipeline(self.api_configs)
        scoring_results = scoring_pipeline.run([scoring_task])

        # Verify results
        self.assertEqual(len(ci_tasks), 1)
        self.assertIn("test-model", ci_results)
        self.assertEqual(len(summary_tasks), 1)
        self.assertIn("test-model", summary_results)
        self.assertEqual(len(scoring_results), 1)

    @patch('src.pipelines.generate_response')
    def test_pipeline_chaining(self, mock_generate):
        """Test chaining pipeline outputs."""
        mock_generate.side_effect = [
            {"test-model": "First pipeline result"},
            {"test-model": "Second pipeline using: First pipeline result"}
        ]

        # Create first task
        first_task = task_factory.create_code_interpretation_task(
            "first", "First task", "Explain", "Code: {code}",
            attributes={"code": "initial_code"}
        )

        # Run first pipeline
        ci_pipeline = CodeInterpretationPipeline(self.api_configs)
        updated_tasks, interpretations = ci_pipeline.run([first_task])

        # Use result in second task
        second_task = task_factory.create_summary_task(
            "second", "Second task", "Summarize", "Based on: {previous}",
            attributes={"previous": interpretations["test-model"][0]}
        )

        # Run second pipeline
        summary_pipeline = SummaryExplanationPipeline(self.api_configs)
        summary_updated, summary_result = summary_pipeline.run([second_task])

        # Verify chaining
        self.assertEqual(
            interpretations["test-model"][0], "First pipeline result")
        self.assertIn("First pipeline result", summary_result["test-model"])
        self.assertEqual(mock_generate.call_count, 2)


class TestTaskValidation(unittest.TestCase):
    """Test task validation functionality."""

    def test_task_creation_validation(self):
        """Test that task creation validates required fields."""
        # Valid task creation
        task = task_factory.create_summary_task(
            "valid_task", "Valid task", "System", "User"
        )
        self.assertIsInstance(task, Task)

        # Test that task has expected properties
        self.assertEqual(task.task_name, "valid_task")
        self.assertEqual(task.description, "Valid task")
        self.assertEqual(task.task_type, "summary")

    def test_task_type_properties(self):
        """Test task type checking properties."""
        # Test each task type
        ci_task = task_factory.create_code_interpretation_task(
            "ci", "CI", "sys", "user")
        summary_task = task_factory.create_summary_task(
            "sum", "Sum", "sys", "user")
        scoring_task = task_factory.create_scoring_task(
            "score", "Score", "sys", "user")

        # Test type checking
        self.assertTrue(ci_task.is_code_interpretation)
        self.assertFalse(ci_task.is_summary)
        self.assertFalse(ci_task.is_scoring)

        self.assertFalse(summary_task.is_code_interpretation)
        self.assertTrue(summary_task.is_summary)
        self.assertFalse(summary_task.is_scoring)

        self.assertFalse(scoring_task.is_code_interpretation)
        self.assertFalse(scoring_task.is_summary)
        self.assertTrue(scoring_task.is_scoring)


class TestPipelineErrorHandling(unittest.TestCase):
    """Test pipeline error handling."""

    def setUp(self):
        self.api_configs = [{"api_key": "test_key", "model": "test-model"}]

    @patch('src.pipelines.generate_response')
    def test_pipeline_handles_api_errors(self, mock_generate):
        """Test that pipelines handle API errors gracefully."""
        # Mock an API error that returns error message (not exception)
        mock_generate.return_value = {
            "test-model": "Error: API rate limit exceeded"}

        task = task_factory.create_summary_task(
            "error_task", "Task that will error", "System", "User"
        )

        pipeline = SummaryExplanationPipeline(self.api_configs)
        updated_tasks, result = pipeline.run([task])

        # Should complete without throwing exception
        self.assertEqual(len(updated_tasks), 1)
        self.assertIn("Error:", result["test-model"])

    def test_pipeline_with_empty_task_list(self):
        """Test pipeline behavior with empty task list."""
        pipeline = CodeInterpretationPipeline(self.api_configs)
        updated_tasks, results = pipeline.run([])

        self.assertEqual(len(updated_tasks), 0)
        # With empty tasks, we should get a dict for each model
        self.assertIsInstance(results, dict)


if __name__ == '__main__':
    unittest.main()
