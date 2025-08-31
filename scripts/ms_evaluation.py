"""
Merge Sort Domain Evaluation Script
"""

from src.task_factory import task_factory
from src.workflow import WorkflowConfig, LENSWorkflow
from src.pipelines import run_summary_pipeline, load_prompt, run_scoring_pipeline
from typing import List
from pathlib import Path
import pandas as pd
import json
from typing import Dict, Any
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def create_workflow_config(config_path: str) -> WorkflowConfig:
    """Create workflow configuration from JSON file and inject API keys."""
    # Load the base configuration
    config = WorkflowConfig.from_json(str(config_path))

    """Load API keys from files and inject them into model configurations."""
    # Define API key files and their corresponding model keywords
    try:
        available_keys = {
            'deepseek': json.load(open('deepseek_api_key.json', 'r'))['api_key'],
            'claude': json.load(open('anthropic_api_key.json', 'r'))['api_key'],
            'o3': json.load(open('openai_api_key.json', 'r'))['api_key']
        }
    except FileNotFoundError:
        print(f"Warning: APIs not found")

    # Inject API keys into all model configurations
    for api_configs in [config.interpretation_apis, config.summary_apis, config.scoring_apis]:
        for api_config in api_configs:
            if api_config.get('api_key'):
                continue  # Skip if already has API key

            model_name = api_config.get('model', '').lower()

            # Find matching API key and inject it
            for keyword, api_key in available_keys.items():
                if keyword in model_name:
                    api_config['api_key'] = api_key
                    break
    return config


# Function to run reasoning model only evaluation
def reasoning_model_evaluation(config: WorkflowConfig, task_ids: List[str]):

    conditions = {
        "rm_np": {
            "name": "Reasoning model with named ILP-learned programs",
            "use_code_interpretation": False,
            "sample": "experiments/programs/ms/target.pl",
            "prompts": {
                "system": "summary_system_reasoner_np.txt",
                "user": "summary_user_no_local.txt"
            }
        },
        "rm_ap": {
            "name": "Reasoning model with anonymised ILP-learned programs",
            "use_code_interpretation": False,
            "sample": "experiments/programs/ms/anonymous_invent.pl",
            "prompts": {
                "system": "summary_system_reasoner_ap.txt",
                "user": "summary_user_no_local.txt"
            }
        },
        "rm_global": {
            "name": "Only domain context and task description",
            "use_code_interpretation": False,
            "prompts": {
                "system": "summary_system_baseline.txt",
                "user": "summary_user_baseline.txt"
            }
        },
        "rm_global_local": {
            "name": "Domain context, task description and local prolog context",
            "use_code_interpretation": False,
            "prompts": {
                "system": "summary_system_baseline.txt",
                "user": "summary_user_baseline_local.txt"
            }
        }}

    task_descriptions = config.task_descriptions
    task_examples = getattr(config, 'task_examples', [
                            ''] * len(task_descriptions))

    summary_tasks = []
    for condition_key, condition_config in conditions.items():

        # Create tasks for each task description
        for i, task_desc in enumerate(task_descriptions):
            task_name = f"{task_ids[i]}_{condition_key}"

            # Prepare attributes for prompt formatting
            attributes = {
                'condition': condition_key,
                'domain': config.domain_name,
                'task_index': i,
                'task_id': task_ids[i],  # Add clean task ID for reference
                'domain_context': config.domain_context,
                'description': task_desc,
                'example_type': 'Prolog',
                'example': task_examples[i],
                'samples': open(condition_config['sample'], 'r').read() if condition_config.get('sample') else ''
            }

            # Load and format prompts for this condition
            system_prompt = load_prompt(
                condition_config['prompts']['system'], config.prompts_path)
            user_prompt = load_prompt(
                condition_config['prompts']['user'], config.prompts_path)

            # Create task for this template condition
            task = task_factory.create_summary_task(
                task_name=task_name,
                description=task_desc,
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                attributes=attributes,
            )
            summary_tasks.append(task)

    # Execute summary pipeline with multiple models
    updated_tasks, _ = run_summary_pipeline(
        tasks=summary_tasks,
        api_configs=config.summary_apis,  # Pass list of APIs
        debug=config.debug_mode,
        verbose=config.verbose
    )

    # Load scoring prompts
    system_prompt = load_prompt(
        config.judge_system_prompt, config.prompts_path)
    user_prompt = load_prompt(
        config.judge_user_prompt, config.prompts_path)

    scoring_tasks = []

    # Create scoring tasks for each summary model's response and each critic
    for summary_task in updated_tasks:
        # Use index-based reference answer access
        task_index = summary_task.attributes.get('task_index', 0)
        reference_answer = config.reference_answers[task_index]

        # Instructions from summary task input
        instructions = summary_task.attributes.get('instructions', '')

        # Get all model responses from the summary task
        model_summaries = summary_task.attributes.get('summaries', {})

        # If no model summaries, fall back to the main result (single model case)
        if not model_summaries and summary_task.result:
            # Single model case - use the first summary model name
            model_name = config.summary_apis[0].get(
                'model', 'unknown_summary_model')
            model_summaries = {model_name: summary_task.result}

        # Create scoring tasks for each summary model's response
        for summariser, response_text in model_summaries.items():
            # Prepare attributes for prompt formatting
            attributes = {
                **summary_task.attributes,
                'summariser': summariser,  # Track which model generated the response
                'instructions': instructions,
                'question': summary_task.description,  # scoring prompt expects 'question'
                'answer': response_text,
                'answer_ref': reference_answer  # scoring prompt expects 'answer_ref'
            }

            # Get condition and task info for naming
            condition_key = summary_task.attributes.get(
                'condition', 'unknown')
            task_id = summary_task.attributes.get(
                'task_id', f'task_{summary_task.attributes.get("task_index", 0)+1}')

            scoring_task = task_factory.create_scoring_task(
                task_name=f"score_{task_id}_{condition_key}_{summariser}",
                description=summary_task.description,
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                attributes=attributes
            )
            scoring_tasks.append(scoring_task)

    # Execute scoring pipeline with all scorers
    _, all_results = run_scoring_pipeline(
        tasks=scoring_tasks,
        api_configs=config.scoring_apis,
        scoring_repeats=config.scoring_repeats,
        debug=config.debug_mode,
        verbose=config.verbose
    )

    print("✅ Reasoning model evaluation complete!")
    return all_results


def template_evaluation(config: WorkflowConfig, task_ids: List[str]) -> List[Dict[str, Any]]:
    """Execute template evaluation for ms domain using pre-written template responses."""

    print("🔧 Running Template Evaluation")

    conditions = {
        'template_global': {
            'description': 'Template generated explanation with global context',
            'templates': {
                "task_1": "experiments/references/ms/template_task_1.txt",
                "task_2": "experiments/references/ms/template_task_2.txt",
                "task_3": "experiments/references/ms/template_task_3.txt",
            },
            "prompts": {
                "system": "summary_system_baseline.txt",
                "user": "summary_user_baseline.txt"
            }
        }
    }

    task_descriptions = config.task_descriptions

    # Load scoring prompts
    system_prompt = load_prompt(
        config.judge_system_prompt, config.prompts_path)
    user_prompt = load_prompt(
        config.judge_user_prompt, config.prompts_path)

    scoring_tasks = []

    # Create scoring tasks for each condition and task
    for condition_key, condition_config in conditions.items():
        for i, task_desc in enumerate(task_descriptions):
            task_id = task_ids[i]

            # Use index-based reference answer access
            reference_answer = config.reference_answers[i]

            # Load template response for this task
            template_file = condition_config['templates'].get(f"task_{i+1}")
            template_response = open(template_file, 'r').read().strip()

            # Load prompt templates using load_prompt function
            instruction_system = load_prompt(
                condition_config['prompts']['system'], config.prompts_path).format(
                domain_context=config.domain_context
            )
            instruction_user = load_prompt(
                condition_config['prompts']['user'], config.prompts_path).format(
                description=task_desc
            )
            instructions = f"{instruction_system}\n{instruction_user}"

            # Prepare attributes for prompt formatting
            attributes = {
                'condition': condition_key,
                'domain': config.domain_name,
                'task_index': i,
                'task_id': task_id,
                'summariser': 'template',  # Track that this is a template response
                'instructions': instructions,
                'question': task_desc,  # scoring prompt expects 'question'
                'answer': template_response,
                'answer_ref': reference_answer  # scoring prompt expects 'answer_ref'
            }

            scoring_task = task_factory.create_scoring_task(
                task_name=f"score_task_{i+1}_{condition_key}_template",
                description=task_desc,
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                attributes=attributes
            )
            scoring_tasks.append(scoring_task)

    if not scoring_tasks:
        print("❌ No template scoring tasks created")
        return []

    # Execute scoring pipeline with all scorers
    _, all_results = run_scoring_pipeline(
        tasks=scoring_tasks,
        api_configs=config.scoring_apis,
        scoring_repeats=config.scoring_repeats,
        debug=config.debug_mode,
        verbose=config.verbose
    )

    print("✅ Template evaluation complete!")
    return all_results


def run_evaluation(config_path, repeat_id, single_cm_config_path=None, save_results=True):
    """Run ms domain evaluation."""

    print("🔌 Starting Merge Sort Domain Evaluation")
    print("=" * 50)

    # Create workflow configuration and comprehensive configuration summary
    config = create_workflow_config(config_path=config_path)
    config.print_configuration_summary()
    print()

    # Execute LENS workflow
    workflow = LENSWorkflow(config)
    lens_results = workflow.execute()

    # Generate task IDs using the workflow method
    task_ids = workflow._generate_task_ids()

    # Execute reasoning model evaluation
    rm_results = reasoning_model_evaluation(config, task_ids)

    # Execute template evaluation
    template_results = template_evaluation(config, task_ids)

    # Combine scoring results from all evaluations
    all_scoring_results = []
    all_scoring_results.extend(lens_results.scoring_results)
    all_scoring_results.extend(rm_results)
    all_scoring_results.extend(template_results)

    # Load single condition model configuration if provided
    if single_cm_config_path:
        print("\n🔬 Running Single Coding Model Evaluation")
        single_cm_config = create_workflow_config(single_cm_config_path)
        single_cm_workflow = LENSWorkflow(single_cm_config)
        single_cm_lens_results = single_cm_workflow.execute()
        all_scoring_results.extend(single_cm_lens_results.scoring_results)

    if not all_scoring_results:
        print("❌ No scoring results generated")
        return

    # Organize results into CSV format
    print("\n📊 Organizing Results...")
    organized_results = workflow.organise_scoring_results_to_csv_format(
        all_scoring_results)

    if save_results:
        # Create results directory
        results_dir = Path(f"results/{config.domain_name}/sample_{repeat_id}/")
        results_dir.mkdir(parents=True, exist_ok=True)

        # Save organized results
        output_file = results_dir / \
            f"combined_results.csv"
        pd.DataFrame(organized_results).to_csv(output_file, index=False)
        print(f"✅ Results saved to: {output_file}")
        print(f"   Generated {len(organized_results)} scoring results")


def main():
    """Main evaluation function."""

    try:
        # Repeat the evaluation three times
        evaluation_repeat = 1
        for repeat_id in range(1, evaluation_repeat + 1):
            print(
                f"\n🔄 Running evaluation repeat {repeat_id}/{evaluation_repeat}...")
            run_evaluation(
                "experiments/configs/ms/evaluation_config.json",
                repeat_id,
                single_cm_config_path="experiments/configs/ms/evaluation_config_single_cm.json")

    except Exception as e:
        print(f"\n❌ Evaluation failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
