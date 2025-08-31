"""
Minimal tests for existing workflow configuration.
"""

from src.workflow import WorkflowConfig, LENSWorkflow
import unittest
import sys
import json
import tempfile
from pathlib import Path
from unittest.mock import patch, mock_open

# Add src to path for imports
test_dir = Path(__file__).parent
src_dir = test_dir.parent / "src"
sys.path.insert(0, str(src_dir))


class TestWorkflowConfigBasic(unittest.TestCase):
    """Test basic WorkflowConfig functionality."""

    def test_config_creation_minimal(self):
        """Test basic config creation with required fields."""
        config = WorkflowConfig(
            domain_name="test_domain"
        )

        self.assertEqual(config.domain_name, "test_domain")
        self.assertEqual(config.domain_context, "")
        self.assertEqual(config.program_registry, {})
        self.assertFalse(config.debug_mode)
        self.assertFalse(config.verbose)

    def test_config_with_all_fields(self):
        """Test config creation with all fields."""
        config = WorkflowConfig(
            domain_name="circuit",
            domain_context="Digital circuits domain",
            program_registry={"lens_np": "and_gate(A,B,C)."},
            interpretation_apis=[
                {"api_key": "test_key", "model": "test-model"}],
            debug_mode=True,
            verbose=True
        )

        self.assertEqual(config.domain_name, "circuit")
        self.assertEqual(config.domain_context, "Digital circuits domain")
        self.assertEqual(
            config.program_registry["lens_np"], "and_gate(A,B,C).")
        self.assertTrue(config.debug_mode)
        self.assertTrue(config.verbose)
        self.assertEqual(config.interpretation_apis[0]["api_key"], "test_key")

    @patch('builtins.open', new_callable=mock_open, read_data='{"domain_name": "test_domain", "debug_mode": true}')
    def test_from_json_basic(self, mock_file):
        """Test loading config from JSON file."""
        config = WorkflowConfig.from_json("test_config.json")

        self.assertEqual(config.domain_name, "test_domain")
        self.assertTrue(config.debug_mode)
        mock_file.assert_called_once_with("test_config.json", 'r')

    def test_from_json_missing_file(self):
        """Test loading config from missing file."""
        with self.assertRaises(FileNotFoundError):
            WorkflowConfig.from_json("missing_config.json")


class TestLENSWorkflowBasic(unittest.TestCase):
    """Test basic LENSWorkflow functionality."""

    def test_workflow_creation(self):
        """Test basic workflow creation."""
        config = WorkflowConfig(domain_name="test_domain")
        workflow = LENSWorkflow(config)

        self.assertIsInstance(workflow.config, WorkflowConfig)
        self.assertEqual(workflow.config.domain_name, "test_domain")

    def test_workflow_has_execute_method(self):
        """Test that workflow has execute method."""
        config = WorkflowConfig(domain_name="test_domain")
        workflow = LENSWorkflow(config)

        # Should have execute method (we won't call it as it needs complex setup)
        self.assertTrue(hasattr(workflow, 'execute'))
        self.assertTrue(callable(getattr(workflow, 'execute')))


class TestConfigIntegrationMinimal(unittest.TestCase):
    """Test configuration integration with minimal dependencies."""

    def test_json_config_integration(self):
        """Test loading config from real JSON file."""
        config_data = {
            "domain_name": "integration_test",
            "domain_context": "Test domain for integration",
            "debug_mode": True,
            "interpretation_apis": [{
                "api_key": "test_key",
                "model": "test-model"
            }]
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            temp_file = f.name

        try:
            # Load config from file
            config = WorkflowConfig.from_json(temp_file)

            # Create workflow
            workflow = LENSWorkflow(config)

            # Verify basic functionality
            self.assertEqual(workflow.config.domain_name, "integration_test")
            self.assertTrue(workflow.config.debug_mode)
            self.assertEqual(
                workflow.config.interpretation_apis[0]["api_key"], "test_key")

        finally:
            Path(temp_file).unlink()  # Clean up temp file


if __name__ == '__main__':
    unittest.main()
