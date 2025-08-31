"""
Simplified LENS Pipelines

Core pipeline implementations that format prompts with task attributes
and call LiteLLM for response generation. Focus on simplicity and essential functionality.
"""

import litellm
import time
import random
import re
import os
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

from .tasks import Task

RETRYABLE_ERRORS = ['overloaded', 'rate limit', '429',
                    '500', '502', '503', '529', 'empty response']


def setup_litellm_api(api_config: Dict[str, Any]) -> str:
    """Setup LiteLLM environment variables and return model name."""
    model_name = api_config.get('model', '')
    api_key = api_config.get('api_key', '')

    # Configure environment variables based on model provider
    if 'claude' in model_name:
        os.environ['ANTHROPIC_API_KEY'] = api_key
        return model_name
    elif 'gpt' in model_name or 'o1' in model_name or 'o3' in model_name:
        os.environ['OPENAI_API_KEY'] = api_key
        return model_name
    elif 'deepseek' in model_name:
        os.environ['DEEPSEEK_API_KEY'] = api_key
        return model_name
    else:
        return model_name


def _is_valid_response(result) -> bool:
    """Helper function to validate LiteLLM response structure."""
    return (result is not None and
            hasattr(result, 'choices') and
            result.choices and
            len(result.choices) > 0)


def _batch_completion(models: List[str], api_configs: List[Dict[str, Any]], messages: List[Dict] = []) -> Tuple[Dict[str, str], List[Tuple[str, Dict[str, Any], str]]]:
    """
    Batch completion function inspired by LiteLLM's implementation but with finer control
    over API parameters per model through individual api_configs.

    Args:
        models: List of model names to query
        api_configs: List of API configuration dictionaries, one per model
        messages: Messages to send to all models

    Returns:
        Tuple of (successful_responses, failed_models) where:
        - successful_responses: Dict mapping model names to their processed response strings
        - failed_models: List of tuples (model_name, api_config, error_message) for failed models
    """

    if len(models) != len(api_configs):
        raise ValueError(
            f"Number of models ({len(models)}) must match number of API configs ({len(api_configs)})")

    successful_responses = {}
    failed_models = []

    with ThreadPoolExecutor(max_workers=len(models)) as executor:
        # Submit all completion requests concurrently
        futures = {}
        for i, model in enumerate(models):
            config = api_configs[i].copy()

            # Remove non-completion parameters
            completion_params = {k: v for k, v in config.items()
                                 if k not in ['model', 'api_key', 'api_url']}

            future = executor.submit(
                litellm.completion,
                model=model,
                messages=messages,
                **completion_params
            )
            futures[model] = (future, api_configs[i])

        # Collect all results and process responses
        for model, (future, api_config) in futures.items():
            try:
                result = future.result()

                # Validate response structure
                if not _is_valid_response(result):
                    failed_models.append(
                        (model, api_config, "Invalid response structure"))
                    raise Exception(
                        f"Model {model} returned invalid response structure")

                # Extract content from valid response
                content = result.choices[0].message.content
                if not content or not content.strip():
                    failed_models.append(
                        (model, api_config, "Empty response content"))
                    raise Exception(
                        f"Model {model} returned empty response content")

                # Success case
                successful_responses[model] = content
                print(f"✅ Model {model} completed successfully")

            except Exception as e:
                failed_models.append((model, api_config, str(e)))
                print(f"❌ Model {model} failed with error: {e}")

    return successful_responses, failed_models


def generate_response(models: List[str], system_prompt: str, user_prompt: str,
                      api_configs: List[Dict[str, Any]], debug: bool = False,
                      max_retries: int = 3, message_history: Optional[List[Dict[str, str]]] = None) -> Dict[str, str]:
    """
    Generate responses using LiteLLM batch API with individual API configs per model.
    Handles retries for failed models while preserving successful responses.

    Args:
        models: List of model strings
        system_prompt: System prompt text
        user_prompt: User prompt text  
        api_configs: List of API configuration dictionaries, one per model
        debug: Whether to return debug responses
        max_retries: Maximum retry attempts
        message_history: Optional conversation history

    Returns:
        Dict mapping model names to their responses
    """
    # Ensure models is always a list
    if isinstance(models, str):
        models = [models]

    if debug:
        return {model: f"Debug response for model: {model}" for model in models}

    # Build messages with proper structure: system first, then history, then current user prompt
    messages = [{"role": "system", "content": system_prompt}]

    # Add history (excluding any system messages to avoid duplicates)
    if message_history:
        for msg in message_history:
            if msg.get('role') != 'system':  # Skip system messages in history
                messages.append(msg)

    # Add current user prompt
    messages.append({"role": "user", "content": user_prompt})

    # Track all responses across retries
    final_responses = {}

    # Initial attempt with all models
    models_to_retry = list(zip(models, api_configs))

    for attempt in range(max_retries + 1):
        if not models_to_retry:
            break

        current_models = [item[0] for item in models_to_retry]
        current_configs = [item[1] for item in models_to_retry]

        if attempt > 0:
            print(
                f"Retrying {len(models_to_retry)} failed models (attempt {attempt + 1}/{max_retries + 1})")
            # Add exponential backoff for retries
            delay = (2 ** attempt) + random.uniform(0, 1)
            time.sleep(delay)

        try:
            # Use batch completion to get successful responses and failed models
            successful_responses, failed_models = _batch_completion(
                models=current_models,
                api_configs=current_configs,
                messages=messages
            )

            # Add successful responses directly (they're already processed strings)
            final_responses.update(successful_responses)

            # Prepare failed models for retry (only retryable errors)
            models_to_retry = []
            for model, api_config, error_message in failed_models:
                error_lower = error_message.lower()
                is_retryable = any(
                    error_type in error_lower for error_type in RETRYABLE_ERRORS)

                if is_retryable and attempt < max_retries:
                    models_to_retry.append((model, api_config))
                else:
                    # Final error for non-retryable errors or max retries reached
                    final_responses[model] = f"Error: {error_message}"

        except Exception as e:
            # Handle unexpected errors in batch completion
            error_message = str(e).lower()
            is_retryable = any(
                error_type in error_message for error_type in RETRYABLE_ERRORS)

            if is_retryable and attempt < max_retries:
                print(
                    f"Batch completion failed, retrying in next attempt: {e}")
                continue
            else:
                # Add errors for any remaining models
                for model, _ in models_to_retry:
                    if model not in final_responses:
                        final_responses[model] = f"Error: {str(e)}"
                break

    # Ensure all original models have responses
    for model in models:
        if model not in final_responses:
            final_responses[model] = "Error: Max retries exceeded"

    return final_responses


def load_prompt(prompt_path: str, prompts_dir: str = "prompts") -> str:
    """Load prompt from file."""
    if not prompt_path.startswith(prompts_dir):
        full_path = Path(prompts_dir) / prompt_path
    else:
        full_path = Path(prompt_path)

    try:
        return full_path.read_text()
    except FileNotFoundError:
        print(f"Warning: Prompt file not found: {full_path}")
        return f"Default prompt for {prompt_path}"


def format_prompt(template: str, **kwargs) -> str:
    """Format prompt template with safe handling of missing keys."""
    try:
        # Filter out None values and duplicate keys
        clean_kwargs = {k: v for k, v in kwargs.items() if v is not None}
        return template.format(**clean_kwargs)
    except KeyError as e:
        print(f"Warning: Missing key {e} in prompt template")
        # Return template with placeholders intact for debugging
        return template
    except Exception as e:
        print(f"Warning: Error formatting template: {e}")
        return template


class ILPLearningPipeline:
    """Pipeline for learning Prolog programs using Hopper ILP system."""

    def __init__(self, hopper_path: str = "experiments/programs/hopper/popper.py"):
        """Initialize ILP learning pipeline."""
        self.hopper_path = hopper_path
        self.learned_programs = {}  # Cache for learned programs

    def run(self, tasks: List[Task], debug: bool = False,
            verbose: bool = False) -> List[Task]:
        """Run ILP learning pipeline."""
        import subprocess
        import tempfile
        import os
        from pathlib import Path

        updated_tasks = []

        for task in tasks:
            print(f"<Processing ILP learning task>: {task.task_name}")

            kb_path = task.attributes.get('kb_path', '')
            if not kb_path:
                task.result = "Error: No knowledge base path specified"
                updated_tasks.append(task)
                continue

            if debug:
                task.result = f"Debug: Mock learned program for {task.task_name}"
                # Cache clean mock program for dependencies in debug mode
                self.learned_programs[task.task_name] = task.result
                print(f"<Learning result>: \n{task.result}\n" + "=" * 50)
            else:
                try:
                    # Check if task depends on previous learned programs
                    dependencies = task.attributes.get('depends_on', None)
                    if dependencies:
                        # Handle both single dependency (string) and multiple dependencies (list)
                        if isinstance(dependencies, str):
                            dependencies = [dependencies]

                        # Filter to only include dependencies that have been learned
                        valid_dependencies = [
                            dep for dep in dependencies if dep in self.learned_programs]

                        if valid_dependencies:
                            # Create temporary knowledge base with dependencies
                            kb_path = self._create_dependent_kb(
                                kb_path, valid_dependencies)

                    # Run Hopper learning
                    cmd = ['python', self.hopper_path, '--kbpath', kb_path]
                    if 'max_ho' in task.attributes:
                        cmd += ['--max-ho', str(task.attributes['max_ho'])]
                    if 'max_rules' in task.attributes:
                        cmd += ['--max-rules',
                                str(task.attributes['max_rules'])]
                    if 'max_body' in task.attributes:
                        cmd += ['--max-body', str(task.attributes['max_body'])]

                    result = subprocess.run(
                        cmd, capture_output=True, text=True, timeout=120)

                    if result.returncode == 0 and result.stdout:
                        task.result = result.stdout.strip()
                        # Extract and cache only the learned Prolog rules
                        clean_program = self._extract_prolog_rules(task.result)

                        # Check if any rules were actually learned
                        if clean_program.strip():
                            self.learned_programs[task.task_name] = clean_program

                            if 'negation' in task.attributes and task.attributes['negation']:
                                # Add negation rules if specified
                                # Obtain the head of the rule
                                rule_head = clean_program.split(':-')[0]
                                clean_program += "\n" + \
                                    f"not_{rule_head}:- not({rule_head})."
                        else:
                            # No rules learned - treat as learning failure
                            print(
                                f"⚠️  No valid rules learned for {task.task_name}")
                    else:
                        task.result = f"Learning failed: {result.stderr or 'Unknown error'}"

                    if verbose:
                        print(
                            f"<Learning result>: \n{task.result}\n" + "=" * 50)

                except subprocess.TimeoutExpired:
                    task.result = "Learning timed out"
                except Exception as e:
                    task.result = f"Error: {str(e)}"

            updated_tasks.append(task)

        return updated_tasks

    def _extract_prolog_rules(self, hopper_output: str) -> str:
        """Extract only the Prolog rules from Hopper output, removing solution markers."""
        # Check for failure cases first
        if ('NO SOLUTION' in hopper_output or
                'NO PROGRAMS FOUND' in hopper_output):
            return ""

        lines = hopper_output.split('\n')
        prolog_rules = []
        in_solution = False

        for line in lines:
            line = line.strip()

            # Detect start of solution section
            if line.startswith('*') and 'SOLUTION' in line:
                in_solution = True
                continue

            # Detect end of solution section or skip metadata
            if (line.startswith('*') and in_solution) or \
               line.startswith('Time:') or \
               line.startswith('Clauses:') or \
               line.startswith('Accuracy:') or \
               line.startswith('Precision:') or \
               line.startswith('Recall:'):
                continue

            # Collect Prolog rules (lines with :- or ending with . and containing parentheses)
            if (in_solution and line and
                    (':-' in line or (line.endswith('.') and '(' in line))):
                prolog_rules.append(line)

        return '\n'.join(prolog_rules)

    def _create_dependent_kb(self, kb_path: str, dependencies: List[str]) -> str:
        """Create a temporary knowledge base that includes learned programs from dependencies."""
        import tempfile
        import shutil
        from pathlib import Path

        # Create a temporary directory
        temp_dir = Path(tempfile.mkdtemp(prefix="ilp_dependent_"))

        # Copy original kb directory to temp location
        original_kb = Path(kb_path)
        temp_kb = temp_dir / original_kb.name
        shutil.copytree(original_kb, temp_kb)

        # Create temporary target files for each dependency
        for i, dependency in enumerate(dependencies):
            dependency_program = self.learned_programs[dependency]
            target_file = temp_kb / f"learned_dependency_{i}.pl"
            with open(target_file, 'w') as f:
                f.write(dependency_program)

        # Update bk.pl to include all learned dependencies
        bk_file = temp_kb / "bk.pl"
        if bk_file.exists():
            with open(bk_file, 'a') as f:
                for i in range(len(dependencies)):
                    f.write(f"\n:- [learned_dependency_{i}].\n")

        return str(temp_kb)


class CodeInterpretationPipeline:
    """Pipeline for converting Prolog code to natural language explanations."""

    def __init__(self, api_configs: List[Dict[str, Any]]):
        """
        Initialize with multiple API configurations.

        Args:
            api_configs: List of API configuration dictionaries
        """
        self.api_configs = api_configs
        self.models = [setup_litellm_api(config) for config in api_configs]

    def run(self, tasks: List[Task], num_samples: int = 1, debug: bool = False,
            verbose: bool = False) -> Tuple[List[Task], Dict[str, List[str]]]:
        """
        Run code interpretation pipeline with multiple models and optional multiple samples.

        Args:
            tasks: List of tasks to process
            num_samples: Number of samples to generate per task per model (default: 1)
            debug: Debug mode flag
            verbose: Verbose output flag

        Returns:
            Tuple of (updated_tasks, model_interpretations)
        """
        model_interpretations = {model: [] for model in self.models}
        updated_tasks = []

        for task in tasks:
            print(
                f"<Processing code interpretation with {num_samples} samples>: {task.task_name}")

            # Format prompts using task attributes
            system_prompt = format_prompt(
                task.system_prompt, **task.attributes)
            user_prompt = format_prompt(task.user_prompt, **task.attributes)

            if verbose or debug:
                print(f"<Models>: {self.models}")
                print(f"<System>: \n{system_prompt}")
                print(f"<User>: \n{user_prompt}\n" + "=" * 50)

            # Generate multiple samples
            all_responses = {}
            for sample_idx in range(num_samples):
                if verbose and num_samples > 1:
                    print(f"  Sample repeat {sample_idx + 1}/{num_samples}")

                # Generate interpretations from all models
                responses = generate_response(
                    self.models, system_prompt, user_prompt,
                    self.api_configs, debug=debug
                )

                # Accumulate responses for each model
                for model, interpretation in responses.items():
                    if model not in all_responses:
                        all_responses[model] = []
                    all_responses[model].append(interpretation)

            # Store all interpretations for each model
            for model, interpretations in all_responses.items():
                model_interpretations[model].extend(interpretations)

            # Update task with interpretations - treat single sample as special case of multiple
            # Always store the first sample for backward compatibility
            task.attributes['interpretations'] = {
                model: interpretations[0] for model, interpretations in all_responses.items()
            }

            # Store all interpretations if multiple samples (including single sample case)
            task.attributes['all_interpretations'] = all_responses

            updated_tasks.append(task)

        return updated_tasks, model_interpretations


class SummaryExplanationPipeline:
    """Pipeline for generating summary explanations."""

    def __init__(self, api_configs: List[Dict[str, Any]]):
        """
        Initialize with multiple API configurations.

        Args:
            api_configs: List of API configuration dictionaries
        """
        self.api_configs = api_configs
        self.models = [setup_litellm_api(config) for config in api_configs]

    def run(self, tasks: List[Task], debug: bool = False,
            verbose: bool = False, use_history: bool = True) -> Tuple[List[Task], Dict[str, str]]:
        """Run summary generation pipeline with multiple models."""
        updated_tasks = []
        model_summaries = {model: [] for model in self.models}
        message_histories = {
            model: [] if use_history else None for model in self.models}

        for task in tasks:
            print(f"<Processing summary task>: {task.task_name}")

            # Format prompts using task attributes
            system_prompt = format_prompt(
                task.system_prompt, **task.attributes)
            user_prompt = format_prompt(task.user_prompt, **task.attributes)

            if verbose or debug:
                print(f"<Models>: {self.models}")
                print(f"<System>: \n{system_prompt}")
                print(f"<User>: \n{user_prompt}\n" + "=" * 50)
                if use_history:
                    for model in self.models:
                        if message_histories[model]:
                            print(
                                f"<{model} History Length>: {len(message_histories[model])} messages")

            # Generate summaries from all models
            # Pass individual API configs for each model
            responses = generate_response(
                self.models, system_prompt, user_prompt,
                self.api_configs, debug=debug,
                message_history=message_histories[self.models[0]
                                                  ] if use_history else None
            )

            # Update message histories if enabled
            if use_history:
                for model in self.models:
                    if message_histories[model] is not None:
                        message_histories[model].extend([
                            {"role": "user", "content": user_prompt},
                            {"role": "assistant", "content": responses[model]}
                        ])

            # Store summaries for each model
            for model, summary in responses.items():
                model_summaries[model].append(summary)

            # Update task with all summaries
            task.attributes['summaries'] = responses
            task.attributes['instructions'] = system_prompt + \
                "\n\n" + user_prompt
            updated_tasks.append(task)

        # Create combined summaries for each model
        final_summaries = {}
        for model in self.models:
            final_summaries[model] = "%%%%%%%%%%%%%%%%%%%% Summary %%%%%%%%%%%%%%%%%%%%\n" + \
                "\n\n%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n\n".join(
                    model_summaries[model])

        return updated_tasks, final_summaries


class ResponseScoringPipeline:
    """Pipeline for scoring response quality."""

    def __init__(self, api_configs: List[Dict[str, Any]]):
        """
        Initialize with multiple API configurations.

        Args:
            api_configs: List of API configuration dictionaries
        """
        self.api_configs = api_configs
        self.models = [setup_litellm_api(config) for config in api_configs]

    def run(self, tasks: List[Task], debug: bool = False,
            verbose: bool = False, scoring_repeats: int = 1) -> List[Dict[str, Any]]:
        """Run response scoring pipeline with multiple models and optional repeated scoring."""
        results = []

        for task in tasks:
            print(f"<Processing scoring task>: {task.task_name}")

            # Format prompts using task attributes
            system_prompt = format_prompt(
                task.system_prompt, **task.attributes)
            user_prompt = format_prompt(task.user_prompt, **task.attributes)

            if verbose or debug:
                print(f"<Models>: {self.models}")
                print(f"<System>: \n{system_prompt}")
                print(f"<User>: \n{user_prompt}\n" + "=" * 50)

            # Perform scoring multiple times if scoring_repeats > 1
            for repeat_idx in range(scoring_repeats):
                if scoring_repeats > 1:
                    print(
                        f"  Scoring attempt {repeat_idx + 1}/{scoring_repeats}")

                # Generate judgments from all models
                # Pass individual API configs for each model
                responses = generate_response(
                    self.models, system_prompt, user_prompt,
                    self.api_configs, debug=debug
                )

                # Extract scores from judgments for each model
                model_scores = {}
                for model, judgment in responses.items():
                    score = self._extract_score(judgment)
                    model_scores[model] = {
                        'judgment': judgment,
                        'score': score
                    }

                result = {
                    'task_name': task.task_name,
                    'description': task.description,
                    'answer': task.attributes.get('answer', ''),
                    'model_scores': model_scores,
                    'attributes': task.attributes,
                    'repeat_index': repeat_idx if scoring_repeats > 1 else None
                }
                results.append(result)

        return results

    def _extract_score(self, judgment: str) -> Optional[float]:
        """Extract numerical score from judgment text."""
        # Look for pattern like "Rating: [[5]]" or "[[5]]"
        rating_match = re.search(r'\[\[(\d+)\]\]', judgment)
        if rating_match:
            score = int(rating_match.group(1))
            if 0 <= score <= 10:
                return float(score)
        return None


def run_code_interpretation_pipeline(tasks: List[Task],
                                     api_configs: List[Dict[str, Any]],
                                     num_samples: int = 1, **kwargs) -> Tuple[List[Task], Dict[str, List[str]]]:
    """Run code interpretation pipeline with multiple models and optional multiple samples."""
    pipeline = CodeInterpretationPipeline(api_configs)
    updated_tasks, interpretations = pipeline.run(
        tasks, num_samples=num_samples, **kwargs)
    return updated_tasks, interpretations


def run_summary_pipeline(tasks: List[Task],
                         api_configs: List[Dict[str, Any]], **kwargs) -> Tuple[List[Task], Dict[str, str]]:
    """Run summary pipeline with multiple models."""
    pipeline = SummaryExplanationPipeline(api_configs)
    updated_tasks, final_summaries = pipeline.run(tasks, **kwargs)
    return updated_tasks, final_summaries


def run_scoring_pipeline(tasks: List[Task],
                         api_configs: List[Dict[str, Any]],
                         scoring_repeats: int = 1, **kwargs) -> Tuple[List[Task], List[Dict[str, Any]]]:
    """Run scoring pipeline with multiple models and optional repeated scoring."""
    pipeline = ResponseScoringPipeline(api_configs)
    results = pipeline.run(tasks, scoring_repeats=scoring_repeats, **kwargs)
    updated_tasks = tasks
    return updated_tasks, results


def run_ilp_learning_pipeline(tasks: List[Task],
                              hopper_path: str = "experiments/programs/hopper/popper.py",
                              pipeline_instance: Optional[ILPLearningPipeline] = None,
                              **kwargs) -> Tuple[List[Task], None]:
    """Run ILP learning pipeline with optional dependency support."""
    if pipeline_instance is None:
        pipeline = ILPLearningPipeline(hopper_path)
    else:
        pipeline = pipeline_instance
    updated_tasks = pipeline.run(tasks, **kwargs)
    return updated_tasks, None
