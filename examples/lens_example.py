"""
Simplified LENS Example

Demonstrates the streamlined LENS workflow with minimal overhead.
Focus on essential functionality: task creation, prompt formatting, and LiteLLM calls.
"""

import json
from pathlib import Path

from src.workflow import WorkflowConfig, LENSWorkflow


def load_llm_config():
    """Load API configuration from file if available."""
    try:
        # Use Ollama local model if available
        config = {
            'model': 'ollama/qwen3:8b',
            'api_base': 'http://localhost:11434',
            'max_tokens': 8192,
            'temperature': 1
        }

        # Use Proprietary API if available
        # config = json.loads(open('openai_api_key.json', 'r').read())
        # config['max_tokens'] = 8192
        # config['temperature'] = 1

        return config
    except FileNotFoundError:
        return {
            'model': 'LLM Mock',
            'api_key': 'demo-key',
            'max_tokens': 8192,
            'temperature': 1
        }


def main():
    """Run the LENS example."""
    print("🚀 LENS Example")
    print("=" * 50)
    print("This example demonstrates the streamlined LENS approach:")
    print()

    try:
        # Load configuration from JSON
        config_path = 'examples/configs/example_config.json'
        config = WorkflowConfig.from_json(str(config_path))
        config.print_configuration_summary()

        # Override API configuration with real keys if available
        api_config = load_llm_config()

        # Update the APIs with the loaded configuration
        # The config.json already has the correct list format, just update with real API keys
        config.interpretation_apis[0].update(api_config)
        config.summary_apis[0].update(api_config)
        config.scoring_apis[0].update(api_config)

        # Show debug mode status
        if config.debug_mode:
            print("🧪 Running in DEBUG mode (no real API calls)")
        else:
            print("🌐 Running with real API calls")
        print()

        # Run workflow
        workflow = LENSWorkflow(config)
        results = workflow.execute()

        # Show results
        print("\n📊 Results Summary:")
        print(f"• Code interpretations: {len(results.code_interpretations)}")
        print(f"• Summary tasks: {len(results.summary_tasks)}")
        print(f"• Scoring results: {len(results.scoring_results)}")

        # Show condition performance
        print("\n📈 Condition Performance:")
        for condition in config.conditions.keys():
            avg_score = results.get_average_score(condition)
            task_count = len([t for t in results.summary_tasks
                              if t.attributes.get('condition') == condition])
            print(
                f"• {condition}: {avg_score:.1f}/10 (avg) from {task_count} tasks")

        print("\n✅ LENS example completed successfully!")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
