"""
Unit tests for simplified pipelines.
"""

from src.pipelines import (
    setup_litellm_api, generate_response, format_prompt,
    CodeInterpretationPipeline, SummaryExplanationPipeline, ResponseScoringPipeline
)
from src.tasks import Task
import unittest
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open
import json

# Add src to path for imports
test_dir = Path(__file__).parent
src_dir = test_dir.parent / "src"
sys.path.insert(0, str(src_dir))


class TestUtilityFunctions(unittest.TestCase):
    """Test utility functions for pipelines."""

    def test_format_prompt_basic(self):
        """Test basic prompt formatting."""
        template = "Hello {name}, you are {age} years old."

        result = format_prompt(template, name="Alice", age=25)

        self.assertEqual(result, "Hello Alice, you are 25 years old.")

    def test_format_prompt_no_variables(self):
        """Test prompt formatting with no variables."""
        template = "Static prompt text"

        result = format_prompt(template)

        self.assertEqual(result, "Static prompt text")

    def test_format_prompt_missing_variable(self):
        """Test prompt formatting with missing variable."""
        template = "Hello {name}, you are {age} years old."

        # Should handle missing variables gracefully
        result = format_prompt(template, name="Alice")

        # Should return original template since age is missing
        self.assertEqual(result, template)

    @patch('src.pipelines.litellm.completion')
    def test_generate_response_success(self, mock_completion):
        """Test successful response generation."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Test response"
        mock_completion.return_value = mock_response

        api_configs = [{"api_key": "test_key"}]

        response = generate_response(
            models=["test-model"],
            system_prompt="System prompt",
            user_prompt="User prompt",
            api_configs=api_configs
        )

        self.assertEqual(response, {"test-model": "Test response"})
        mock_completion.assert_called_once()

    @patch('src.pipelines.litellm.completion')
    def test_generate_response_debug_mode(self, mock_completion):
        """Test response generation in debug mode."""
        api_configs = [{"api_key": "test_key"}]

        response = generate_response(
            models=["test-model"],
            system_prompt="System prompt",
            user_prompt="User prompt",
            api_configs=api_configs,
            debug=True
        )

        # In debug mode, should return debug response without calling API
        self.assertIn("test-model", response)
        self.assertIn("Debug response", response["test-model"])
        mock_completion.assert_not_called()

    @patch('src.pipelines.litellm.completion')
    def test_generate_response_failure(self, mock_completion):
        """Test response generation failure."""
        mock_completion.side_effect = Exception("API Error")

        api_configs = [{"api_key": "test_key"}]

        response = generate_response(
            models=["test-model"],
            system_prompt="System prompt",
            user_prompt="User prompt",
            api_configs=api_configs,
            max_retries=0  # No retries for faster test
        )

        # Should return error message
        self.assertIn("test-model", response)
        self.assertIn("Error:", response["test-model"])
        mock_completion.assert_called_once()


class TestCodeInterpretationPipeline(unittest.TestCase):
    """Test CodeInterpretationPipeline class."""

    def setUp(self):
        self.api_configs = [{"api_key": "test_key", "model": "test-model"}]
        self.pipeline = CodeInterpretationPipeline(self.api_configs)

    @patch('src.pipelines.generate_response')
    def test_run_single_task(self, mock_generate):
        """Test running a single code interpretation task."""
        mock_generate.return_value = {
            "test-model": "Interpreted code explanation"}

        task = Task(
            task_name="test_ci",
            description="Test code interpretation",
            task_type="code_interpretation",
            system_prompt="Explain the code",
            user_prompt="Code: {prolog}",
            attributes={"prolog": "test_code"}
        )

        updated_tasks, interpretations = self.pipeline.run([task])

        self.assertEqual(len(updated_tasks), 1)
        self.assertEqual(len(interpretations), 1)
        # interpretations is now a dict mapping models to lists of interpretations
        self.assertEqual(
            interpretations["test-model"], ["Interpreted code explanation"])
        mock_generate.assert_called_once()

    @patch('src.pipelines.generate_response')
    def test_run_multiple_tasks(self, mock_generate):
        """Test running multiple code interpretation tasks."""
        mock_generate.side_effect = [
            {"test-model": "Response 1"},
            {"test-model": "Response 2"}
        ]

        tasks = [
            Task(
                task_name="test_ci_1",
                description="Test 1",
                task_type="code_interpretation",
                system_prompt="Explain",
                user_prompt="Code: {prolog}",
                attributes={"prolog": "code1"}
            ),
            Task(
                task_name="test_ci_2",
                description="Test 2",
                task_type="code_interpretation",
                system_prompt="Explain",
                user_prompt="Code: {prolog}",
                attributes={"prolog": "code2"}
            )
        ]

        updated_tasks, interpretations = self.pipeline.run(tasks)

        self.assertEqual(len(updated_tasks), 2)
        # interpretations is now a dict mapping models to lists
        self.assertEqual(len(interpretations["test-model"]), 2)
        self.assertEqual(interpretations["test-model"][0], "Response 1")
        self.assertEqual(interpretations["test-model"][1], "Response 2")
        self.assertEqual(mock_generate.call_count, 2)

    @patch('src.pipelines.generate_response')
    def test_run_with_error(self, mock_generate):
        """Test running with an error."""
        mock_generate.side_effect = Exception("API Error")

        task = Task(
            task_name="test_ci_error",
            description="Test error",
            task_type="code_interpretation",
            system_prompt="Explain",
            user_prompt="Code: test"
        )

        with self.assertRaises(Exception):
            self.pipeline.run([task])

    def test_run_empty_tasks(self):
        """Test running with empty task list."""
        updated_tasks, interpretations = self.pipeline.run([])
        self.assertEqual(len(updated_tasks), 0)
        # With empty tasks, we should get empty dict for each model
        self.assertIsInstance(interpretations, dict)
        for model_interpretations in interpretations.values():
            self.assertEqual(len(model_interpretations), 0)


class TestSummaryExplanationPipeline(unittest.TestCase):
    """Test SummaryExplanationPipeline class."""

    def setUp(self):
        self.api_configs = [{"api_key": "test_key", "model": "test-model"}]
        self.pipeline = SummaryExplanationPipeline(self.api_configs)

    @patch('src.pipelines.generate_response')
    def test_run_single_task(self, mock_generate):
        """Test running a single summary task."""
        mock_generate.return_value = {"test-model": "Generated summary"}

        task = Task(
            task_name="test_summary",
            description="Test summary",
            task_type="summary",
            system_prompt="Create a summary",
            user_prompt="Content: {content}",
            attributes={"content": "test content"}
        )

        updated_tasks, summaries = self.pipeline.run([task])

        self.assertEqual(len(updated_tasks), 1)
        self.assertIn("test-model", summaries)
        # Summary pipeline adds formatting around the actual summary
        expected_summary = "%%%%%%%%%%%%%%%%%%%% Summary %%%%%%%%%%%%%%%%%%%%\nGenerated summary"
        self.assertEqual(summaries["test-model"], expected_summary)
        mock_generate.assert_called_once()

    @patch('src.pipelines.generate_response')
    def test_run_with_debug_mode(self, mock_generate):
        """Test running with debug mode."""
        mock_generate.return_value = {"test-model": "Summary with debug"}

        task = Task(
            task_name="test_summary",
            description="Test summary",
            task_type="summary",
            system_prompt="Create a summary",
            user_prompt="Content: test"
        )

        updated_tasks, summaries = self.pipeline.run([task], debug=True)

        # Should succeed with debug mode
        self.assertEqual(len(updated_tasks), 1)
        self.assertIsInstance(summaries, dict)
        self.assertIn("test-model", summaries)


class TestResponseScoringPipeline(unittest.TestCase):
    """Test ResponseScoringPipeline class."""

    def setUp(self):
        self.api_configs = [{"api_key": "test_key", "model": "test-model"}]
        self.pipeline = ResponseScoringPipeline(self.api_configs)

    @patch('src.pipelines.generate_response')
    def test_run_single_task(self, mock_generate):
        """Test running a single scoring task."""
        mock_generate.return_value = {"test-model": "Score: 8/10"}

        task = Task(
            task_name="test_scoring",
            description="Test scoring",
            task_type="scoring",
            system_prompt="Score the answer",
            user_prompt="Answer: {answer}",
            attributes={"answer": "test answer"}
        )

        results = self.pipeline.run([task])

        self.assertEqual(len(results), 1)
        self.assertIn("task_name", results[0])
        self.assertIn("model_scores", results[0])
        self.assertIn("test-model", results[0]["model_scores"])
        mock_generate.assert_called_once()

    @patch('src.pipelines.generate_response')
    def test_run_with_verbose(self, mock_generate):
        """Test running with verbose mode."""
        mock_generate.return_value = {"test-model": "Score with verbose"}

        task = Task(
            task_name="test_scoring",
            description="Test scoring",
            task_type="scoring",
            system_prompt="Score",
            user_prompt="Answer: test"
        )

        results = self.pipeline.run([task], verbose=True)

        # Should succeed with verbose mode
        self.assertEqual(len(results), 1)
        self.assertIsInstance(results[0], dict)


class TestPipelineIntegration(unittest.TestCase):
    """Test pipeline integration features."""

    def setUp(self):
        self.api_configs = [{"api_key": "test_key", "model": "test-model"}]

    @patch('src.pipelines.generate_response')
    def test_pipeline_with_verbose_mode(self, mock_generate):
        """Test pipeline execution with verbose mode."""
        mock_generate.return_value = {"test-model": "Test response"}

        task = Task(
            task_name="test",
            description="Test",
            task_type="summary",
            system_prompt="Test",
            user_prompt="Test"
        )

        pipeline = SummaryExplanationPipeline(self.api_configs)

        # Test verbose mode doesn't break execution
        updated_tasks, summaries = pipeline.run([task], verbose=True)

        self.assertEqual(len(updated_tasks), 1)
        self.assertIsInstance(summaries, dict)
        self.assertIn("test-model", summaries)


if __name__ == '__main__':
    unittest.main()
