"""
Simplified LENS Workflow

High-level orchestrator for managing LENS pipeline sequences.
Focuses on configuration, task creation, and pipeline coordination.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from pathlib import Path
import json
import os

from .pipelines import (
    run_code_interpretation_pipeline, run_summary_pipeline, run_scoring_pipeline,
    run_ilp_learning_pipeline, load_prompt
)
from .tasks import Task
from .task_factory import task_factory


@dataclass
class WorkflowConfig:
    """Configuration for LENS workflow execution."""
    # Essential configuration
    domain_name: str
    domain_context: str = ""

    # Program registry: program_content and metadata
    program_registry: Dict[str, Any] = field(default_factory=dict)

    # ILP Learning configuration
    use_ilp_learning: bool = True
    programs_with_comments: bool = False
    ilp_hopper_path: str = "experiments/programs/hopper/popper.py"
    ilp_learning_episodes: List[Dict[str, Any]] = field(
        default_factory=list)  # For episodic learning

    # API configurations - support multiple models per pipeline
    interpretation_apis: List[Dict[str, Any]] = field(default_factory=list)
    summary_apis: List[Dict[str, Any]] = field(default_factory=list)
    scoring_apis: List[Dict[str, Any]] = field(default_factory=list)

    # Experimental conditions
    conditions: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    task_examples: List[str] = field(default_factory=list)
    task_descriptions: List[str] = field(default_factory=list)
    reference_answers: List[str] = field(default_factory=list)

    # Options
    debug_mode: bool = False
    verbose: bool = False
    prompts_path: str = "prompts"
    num_interpretation_samples: int = 1  # Number of samples for code interpretation
    scoring_repeats: int = 1  # Number of times to repeat scoring for each task

    # Prompt file names (configurable)
    ci_system_prompt: str = "CI_system.txt"
    ci_user_prompt: str = "CI_user.txt"
    judge_system_prompt: str = "judge_reference_system.txt"
    judge_user_prompt: str = "judge_reference_user.txt"

    @classmethod
    def from_json(cls, file_path: str) -> 'WorkflowConfig':
        """Load configuration from JSON file."""
        with open(file_path, 'r') as f:
            config_dict = json.load(f)

        # Load domain_context from file if it's a file path
        domain_context = config_dict.get('domain_context', '')
        if domain_context and domain_context.endswith('.txt'):
            config_dict['domain_context'] = open(
                domain_context, 'r').read().strip()
        else:
            config_dict['domain_context'] = domain_context

        # Load program_registry from files if they're file paths
        program_registry = config_dict.get('program_registry', {})
        if isinstance(program_registry, dict):
            loaded_codes = {}
            for key, value in program_registry.items():
                if isinstance(value, str) and value.endswith('.pl'):
                    loaded_codes[key] = {
                        'content': open(value, 'r').read().strip(),
                        'type': 'predefined',
                        'dependencies': [],
                        'prim': ''
                    }
                else:
                    loaded_codes[key] = value
            config_dict['program_registry'] = loaded_codes
        else:
            raise ValueError(
                "program_registry must be a dictionary mapping program names to content or file paths")

        # Load task_descriptions from files if they're file paths
        task_descriptions = config_dict.get('task_descriptions', [])
        if isinstance(task_descriptions, list):
            loaded_descriptions = []
            for desc in task_descriptions:
                if isinstance(desc, str) and desc.endswith('.txt'):
                    loaded_descriptions.append(open(desc, 'r').read().strip())
                else:
                    loaded_descriptions.append(desc)
            config_dict['task_descriptions'] = loaded_descriptions
        else:
            raise ValueError(
                "task_descriptions must be a list of strings or file paths")

        # Load task_examples from files if they're file paths
        task_examples = config_dict.get('task_examples', [])
        if isinstance(task_examples, list):
            loaded_examples = []
            for example in task_examples:
                if isinstance(example, str) and '/' in example:
                    loaded_examples.append(open(example, 'r').read().strip())
                else:
                    loaded_examples.append(example)
            config_dict['task_examples'] = loaded_examples
        else:
            raise ValueError(
                "task_examples must be a list of strings or file paths")

        # Load reference_answers from files if they're file paths
        reference_answers = config_dict.get('reference_answers', [])
        if isinstance(reference_answers, list):
            # New list-based format (preferred)
            loaded_answers = []
            for value in reference_answers:
                if isinstance(value, str) and value.endswith('.txt'):
                    loaded_answers.append(open(value, 'r').read().strip())
                else:
                    loaded_answers.append(value)
            config_dict['reference_answers'] = loaded_answers
        else:
            raise ValueError(
                "reference_answers must be a list of content/file paths or dict mapping task keys to content/file paths")

        return cls(**config_dict)

    def get_configuration_summary(self) -> str:
        """
        Generate a comprehensive configuration summary for interpretability.

        Args:
            show_details: If True, includes detailed condition descriptions and model lists

        Returns:
            Formatted string summarizing the configuration
        """
        summary_lines = []

        # Header
        summary_lines.append("🔧 LENS Workflow Configuration Summary")
        summary_lines.append("=" * 50)

        # Basic configuration
        summary_lines.append(f"📋 Domain: {self.domain_name}")
        summary_lines.append(f"🎯 Total Tasks: {len(self.task_descriptions)}")
        summary_lines.append(
            f"🧪 Experimental Conditions: {len(self.conditions)}")

        # Pipeline configuration
        summary_lines.append(f"\n🔄 Pipeline Configuration:")
        summary_lines.append(
            f"   Code Interpretation: {len(self.interpretation_apis)} model(s)")
        summary_lines.append(
            f"   Summary Generation: {len(self.summary_apis)} model(s)")
        summary_lines.append(
            f"   Response Scoring: {len(self.scoring_apis)} model(s)")

        # Execution settings
        summary_lines.append(f"\n⚙️  Execution Settings:")
        summary_lines.append(
            f"   Debug Mode: {'✅ ON' if self.debug_mode else '❌ OFF'}")
        summary_lines.append(
            f"   Verbose Output: {'✅ ON' if self.verbose else '❌ OFF'}")
        summary_lines.append(
            f"   Interpretation Samples: {self.num_interpretation_samples}")
        summary_lines.append(f"   Scoring Repeats: {self.scoring_repeats}")
        summary_lines.append(
            f"   ILP Learning: {'✅ ENABLED' if self.use_ilp_learning else '❌ DISABLED'}")

        if self.verbose:
            # Program codes summary
            if self.program_registry:
                summary_lines.append(f"\n💾 Program Codes Available:")
                for condition, code in self.program_registry.items():
                    code_size = len(code) if isinstance(code, str) else 0
                    summary_lines.append(f"   {condition}: {code_size} chars")

            # Conditions requiring code interpretation
            ci_conditions = [name for name, config in self.conditions.items()
                             if config.get('use_code_interpretation', True)]
            if ci_conditions:
                summary_lines.append(
                    f"\n🔍 Conditions Using Code Interpretation ({len(ci_conditions)}):")
                for condition in ci_conditions:
                    has_code = "✅" if condition in self.program_registry else "❌"
                    summary_lines.append(f"   {has_code} {condition}")

            # Reference answers
            if self.reference_answers:
                summary_lines.append(
                    f"\n📚 Reference Answers: {len(self.reference_answers)} configured")
                for i, answer in enumerate(self.reference_answers):
                    answer_length = len(answer) if isinstance(
                        answer, str) else 0
                    summary_lines.append(
                        f"   task_{i+1}: {answer_length} chars")

            # Detailed model information
            summary_lines.append(f"\n🤖 Model Details:")

            if self.interpretation_apis:
                summary_lines.append("   Code Interpretation Models:")
                for i, api in enumerate(self.interpretation_apis):
                    model_name = api.get('model', f'model_{i}')
                    temp = api.get('temperature', 'default')
                    summary_lines.append(f"     • {model_name} (temp: {temp})")

            if self.summary_apis:
                summary_lines.append("   Summary Generation Models:")
                for i, api in enumerate(self.summary_apis):
                    model_name = api.get('model', f'model_{i}')
                    temp = api.get('temperature', 'default')
                    summary_lines.append(f"     • {model_name} (temp: {temp})")

            if self.scoring_apis:
                summary_lines.append("   Scoring Models:")
                for i, api in enumerate(self.scoring_apis):
                    model_name = api.get('model', f'model_{i}')
                    temp = api.get('temperature', 'default')
                    summary_lines.append(f"     • {model_name} (temp: {temp})")

            # Detailed condition information
            if self.conditions:
                summary_lines.append(f"\n📊 Condition Details:")
                for name, config in self.conditions.items():
                    description = config.get('name', 'No description')
                    use_ci = config.get('use_code_interpretation', True)
                    sys_prompt = config.get('prompts', {}).get(
                        'system', 'not specified')
                    user_prompt = config.get('prompts', {}).get(
                        'user', 'not specified')
                    ci_indicator = "🔍" if use_ci else "📝"
                    summary_lines.append(f"   {ci_indicator} {name}:")
                    summary_lines.append(f"     Description: {description}")
                    summary_lines.append(
                        f"     Prompts: {sys_prompt} + {user_prompt}")

            # Domain context info
            if self.domain_context:
                context_length = len(self.domain_context) if isinstance(
                    self.domain_context, str) else 0
                summary_lines.append(
                    f"\n🌐 Domain Context: {context_length} characters loaded")

            # Task descriptions info
            if self.task_descriptions:
                summary_lines.append(f"\n📝 Task Descriptions:")
                for i, desc in enumerate(self.task_descriptions):
                    summary_lines.append(
                        f"   Task {i+1}: \"{desc}\"")

        return "\n".join(summary_lines)

    def print_configuration_summary(self):
        """Print the configuration summary to console."""
        print(self.get_configuration_summary())

    def get_configuration_dict(self) -> Dict[str, Any]:
        """
        Generate a structured dictionary summary of the configuration.
        Useful for programmatic access and analysis.

        Returns:
            Dictionary containing key configuration metrics
        """
        # Count conditions by type
        ci_conditions = [name for name, config in self.conditions.items()
                         if config.get('use_code_interpretation', True)]
        baseline_conditions = [name for name, config in self.conditions.items()
                               if not config.get('use_code_interpretation', True)]

        # Count conditions with/without program codes
        ci_with_codes = [
            name for name in ci_conditions if name in self.program_registry]
        ci_without_codes = [
            name for name in ci_conditions if name not in self.program_registry]

        return {
            "domain": {
                "name": self.domain_name,
                "context_length": len(self.domain_context) if isinstance(self.domain_context, str) else 0,
                "has_context": bool(self.domain_context)
            },
            "tasks": {
                "total_count": len(self.task_descriptions),
                "descriptions_loaded": len([desc for desc in self.task_descriptions if desc])
            },
            "conditions": {
                "total_count": len(self.conditions),
                "code_interpretation_count": len(ci_conditions),
                "baseline_count": len(baseline_conditions),
                "ci_with_program_registry": len(ci_with_codes),
                "ci_missing_program_registry": len(ci_without_codes),
                "ci_condition_names": ci_conditions,
                "baseline_condition_names": baseline_conditions,
                "missing_codes": ci_without_codes
            },
            "program_registry": {
                "total_available": len(self.program_registry),
                "condition_mapping": {k: len(v) if isinstance(v, str) else 0
                                      for k, v in self.program_registry.items()}
            },
            "models": {
                "interpretation_models": len(self.interpretation_apis),
                "summary_models": len(self.summary_apis),
                "scoring_models": len(self.scoring_apis),
                "interpretation_model_names": [api.get('model', f'model_{i}')
                                               for i, api in enumerate(self.interpretation_apis)],
                "summary_model_names": [api.get('model', f'model_{i}')
                                        for i, api in enumerate(self.summary_apis)],
                "scoring_model_names": [api.get('model', f'model_{i}')
                                        for i, api in enumerate(self.scoring_apis)]
            },
            "execution_settings": {
                "debug_mode": self.debug_mode,
                "verbose": self.verbose,
                "interpretation_samples": self.num_interpretation_samples,
                "scoring_repeats": self.scoring_repeats,
                "ilp_learning_enabled": self.use_ilp_learning,
            },
            "reference_answers": {
                "total_configured": len(self.reference_answers),
                "answer_lengths": {f"task_{i+1}": len(v) if isinstance(v, str) else 0
                                   for i, v in enumerate(self.reference_answers)}
            },
            "estimated_total_runs": {
                "summary_tasks": len(self.conditions) * len(self.task_descriptions),
                "scoring_tasks": len(self.conditions) * len(self.task_descriptions) * len(self.summary_apis) * len(self.scoring_apis),
                "total_scoring_attempts": len(self.conditions) * len(self.task_descriptions) * len(self.summary_apis) * len(self.scoring_apis) * self.scoring_repeats
            }
        }


@dataclass
class WorkflowResults:
    """Container for workflow execution results."""
    code_interpretations: Dict[str, List[str]] = field(
        default_factory=dict)  # condition -> interpretations
    summary_tasks: List[Task] = field(default_factory=list)
    scoring_results: List[Dict[str, Any]] = field(default_factory=list)

    def get_summary_by_condition(self, condition: str) -> Optional[Task]:
        """Get summary task for a specific condition."""
        for task in self.summary_tasks:
            if task.attributes.get('condition') == condition:
                return task
        return None

    def get_scores_by_condition(self, condition: str) -> List[float]:
        """Get all scores for a specific condition."""
        scores = []
        for result in self.scoring_results:
            if result.get('attributes', {}).get('condition') == condition:
                if 'score' in result and result['score'] is not None:
                    scores.append(result['score'])
        return scores

    def get_average_score(self, condition: str) -> float:
        """Get average score for a condition."""
        scores = self.get_scores_by_condition(condition)
        return sum(scores) / len(scores) if scores else 0.0


class LENSWorkflow:
    """Simplified LENS workflow orchestrator."""

    def __init__(self, config: WorkflowConfig):
        self.config = config
        self.results = WorkflowResults()

    def execute(self) -> WorkflowResults:
        """Execute the complete LENS workflow."""
        print("🚀 Starting LENS Workflow Execution")
        print("=" * 50)

        try:
            # Step 0: ILP Learning (if enabled)
            self._execute_ilp_learning()

            # Step 1: Code Interpretation (if needed)
            code_interpretations = self._execute_code_interpretation()

            # Step 2: Summary Generation
            summary_tasks = self._execute_summary_generation(
                code_interpretations)

            # Step 3: Response Scoring
            scoring_results = self._execute_response_scoring(summary_tasks)

            # Collect results
            self.results.code_interpretations = code_interpretations
            self.results.summary_tasks = summary_tasks
            self.results.scoring_results = scoring_results

            print("\n🎉 LENS Workflow Complete!")
            return self.results

        except Exception as e:
            print(f"\n❌ Workflow execution failed: {e}")
            return self.results

    def _execute_ilp_learning(self) -> None:
        """Execute ILP learning step if enabled - supports both single and sequential learning."""
        if not self.config.use_ilp_learning:
            print("⏭️  Skipping ILP learning (not enabled)")
            return

        # Prepare learning sequence
        if self.config.ilp_learning_episodes:
            # Use configured sequence
            learning_episodes = self.config.ilp_learning_episodes
            print("📚 STEP 0: Sequential ILP Learning")
            print(f"   Learning {len(learning_episodes)} episodes in sequence")
        else:
            raise ValueError(
                "ILP learning enabled but learning_episodes specified")

        # Create a single pipeline instance to maintain learned program cache
        from .pipelines import ILPLearningPipeline
        pipeline = ILPLearningPipeline(self.config.ilp_hopper_path)

        # Learn each task in sequence
        for i, task_config in enumerate(learning_episodes):
            episode_name = task_config.get('name', f'episode_{i+1}')

            # Create ILP learning task
            task = task_factory.create_ilp_learning_task(
                task_name=episode_name,
                description=f"Learn Prolog rules for {episode_name}",
                attributes=task_config
            )

            # Run learning directly using the pipeline instance
            updated_tasks = pipeline.run(
                [task], debug=self.config.debug_mode, verbose=self.config.verbose)

        if pipeline.learned_programs:
            for episode_name, program in pipeline.learned_programs.items():
                # Find the task_config for this episode to get dependencies
                for task_config in learning_episodes:
                    if task_config.get('name') == episode_name:
                        episode_task_config = task_config

                        # Load primitives from specified path or fallback to kb_path
                        if 'prim_path' in episode_task_config:
                            primitives = open(
                                episode_task_config['prim_path'], 'r').read().strip()
                        else:
                            primitives = open(os.path.join(
                                episode_task_config['kb_path'], 'bk.pl'), 'r').read().strip()

                        primitives = '\n'.join([line for line in primitives.splitlines(
                        ) if not line.startswith('%') or self.config.programs_with_comments])

                        program_entry = {
                            'content': program,
                            'type': 'ilp_learned',
                            'dependencies': episode_task_config.get('depends_on', []),
                            'prim': primitives
                        }
                        self.config.program_registry[episode_name] = program_entry
                        break
        else:
            raise Exception("ILP learning failed - no programs learned")

    def _resolve_program_reference(self, program_ref: str) -> str:
        """Resolve a program reference to actual program content with dependencies."""

        # Check if the program reference exists in the registry
        if program_ref not in self.config.program_registry:
            raise ValueError(
                f"Program reference '{program_ref}' not found in program registry.")

        program_entry = self.config.program_registry[program_ref]
        program_content = program_entry.get('content', '')
        dependencies = program_entry.get('dependencies', [])

        # If no dependencies, return just the program content
        if not dependencies:
            return program_content

        combined_program = []
        prim_registry = set()
        for dep in dependencies:
            if dep in self.config.program_registry:

                # Resolve dependency content and knowledge base
                dep_entry = self.config.program_registry[dep]
                dep_content = dep_entry.get('content', '')
                dep_prim = dep_entry.get('prim', '')

                if dep_content:
                    combined_program.append(dep_content)

                if dep_prim:
                    prim_registry.add(dep_prim)

        combined_program.append(program_content)
        program_code = '\n\n'.join(combined_program)
        primitives = '\n\n'.join(prim_registry)

        program_code_padding = """%%%%%%%%%%%%%%%%%%%% Main program %%%%%%%%%%%%%%%%%%%%\n\n{program_code}\n\n"""
        primitive_code_padding = """%%%%%%%%%%%%%%%%%%%% Primitives %%%%%%%%%%%%%%%%%%%%\n\n{primitives}\n\n"""

        return program_code_padding.format(
            program_code=program_code) + primitive_code_padding.format(primitives=primitives)

    def _generate_task_ids(self) -> List[str]:
        """
        Generate task IDs for task descriptions, handling duplicates with suffixes.
        """
        task_ids = []
        description_to_base_task = {}
        description_counts = {}

        # First pass: assign base task numbers to unique descriptions
        base_task_num = 1
        for desc in self.config.task_descriptions:
            if desc not in description_to_base_task:
                description_to_base_task[desc] = base_task_num
                base_task_num += 1
            description_counts[desc] = description_counts.get(desc, 0) + 1

        # Second pass: generate task IDs with suffixes for duplicates
        description_seen = {}
        for desc in self.config.task_descriptions:
            base_num = description_to_base_task[desc]

            # If this description appears multiple times, add suffix
            if description_counts[desc] > 1:
                occurrence = description_seen.get(desc, 0) + 1
                description_seen[desc] = occurrence
                task_id = f"task_{base_num}_{occurrence}"
            else:
                task_id = f"task_{base_num}"

            task_ids.append(task_id)

        return task_ids

    def _execute_code_interpretation(self) -> Dict[str, List[str]]:
        """Execute code interpretation step with condition-specific program codes."""
        # Check if any condition requires code interpretation
        needs_interpretation = any(
            condition.get('use_code_interpretation', True)
            for condition in self.config.conditions.values()
        )

        if not needs_interpretation or not self.config.interpretation_apis:
            print("⏭️  Skipping code interpretation (not required)")
            return {}

        print("🔍 STEP 1: Code Interpretation")

        # Load prompts
        system_prompt = load_prompt(
            self.config.ci_system_prompt, self.config.prompts_path)
        user_prompt = load_prompt(
            self.config.ci_user_prompt, self.config.prompts_path)

        # Determine unique program codes needed based on condition program references
        program_registry_needed = {}
        condition_to_program = {}

        for condition_key, condition_config in self.config.conditions.items():
            if not condition_config.get('use_code_interpretation', True):
                continue

            program_ref = condition_config.get('program_ref', None)
            if not program_ref:
                raise ValueError(
                    f"Condition '{condition_key}' requires code interpretation but no program reference specified")

            program_content = self._resolve_program_reference(program_ref)
            program_registry_needed[program_content] = program_ref
            condition_to_program[condition_key] = program_content

        if not program_registry_needed:
            raise ValueError("No program codes available for interpretation")

        # Generate interpretations for each unique program code
        all_interpretations = {}
        program_to_interpretations = {}

        for program_code, program_ref in program_registry_needed.items():
            print(f"🔍 Interpreting program: {program_ref}")

            # Create task for this program code
            task = task_factory.create_code_interpretation_task(
                task_name=f"{self.config.domain_name}_interpretation_{program_ref}",
                description=f"Explain {self.config.domain_name} domain {program_ref} program code",
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                attributes={
                    'domain': self.config.domain_name,
                    'prolog': program_code
                }
            )

            # Execute pipeline with multiple models
            updated_tasks, interpretations_dict = run_code_interpretation_pipeline(
                tasks=[task],
                api_configs=self.config.interpretation_apis,
                num_samples=self.config.num_interpretation_samples,
                debug=self.config.debug_mode,
                verbose=self.config.verbose
            )

            # Store interpretations for this program code
            interpretations = []
            for model_interpretations in interpretations_dict.values():
                interpretations.extend(model_interpretations)

            program_to_interpretations[program_code] = interpretations

        # Map interpretations to conditions
        for condition_key, program_code in condition_to_program.items():
            all_interpretations[condition_key] = program_to_interpretations[program_code]

        print("✅ Code interpretation complete!")
        return all_interpretations

    def _execute_summary_generation(self, code_interpretations: Dict[str, List[str]]) -> List[Task]:
        """Execute summary generation for all conditions."""
        print("\n📝 STEP 2: Summary Generation")

        # Generate task IDs
        task_ids = self._generate_task_ids()

        summary_tasks = []

        for condition_key, condition_config in self.config.conditions.items():
            # Load prompts for this condition
            system_prompt = load_prompt(
                condition_config['prompts']['system'],
                self.config.prompts_path
            )
            user_prompt = load_prompt(
                condition_config['prompts']['user'],
                self.config.prompts_path
            )

            # Get condition-specific code interpretations
            condition_interpretations = code_interpretations.get(
                condition_key, [])

            # Format interpretation samples - single sample is special case of multiple
            if condition_interpretations:
                interpretation_text = "\n\n".join([
                    f"%%%%%%%%%%%%%%%%%%%% Sample {i+1} %%%%%%%%%%%%%%%%%%%%\n{interp}"
                    for i, interp in enumerate(condition_interpretations)
                ])
            else:
                interpretation_text = ""

            # Create tasks for each task description
            for i, task_desc in enumerate(self.config.task_descriptions):
                task_name = f"{task_ids[i]}_{condition_key}"

                # Prepare attributes for prompt formatting
                attributes = {
                    'condition': condition_key,
                    'domain': self.config.domain_name,
                    'task_index': i,
                    'task_id': task_ids[i],
                    'domain_context': self.config.domain_context,
                    'code_interpretation': interpretation_text,
                    'description': task_desc,
                    'example_type': 'Prolog',
                    'example': self.config.task_examples[i] if i < len(self.config.task_examples) else '',
                    'samples': interpretation_text
                }

                task = task_factory.create_summary_task(
                    task_name=task_name,
                    description=task_desc,
                    system_prompt=system_prompt,
                    user_prompt=user_prompt,
                    attributes=attributes
                )
                summary_tasks.append(task)

        # Execute summary pipeline with multiple models
        updated_tasks, summaries_dict = run_summary_pipeline(
            tasks=summary_tasks,
            api_configs=self.config.summary_apis,  # Pass list of APIs
            debug=self.config.debug_mode,
            verbose=self.config.verbose
        )

        print("✅ Summary generation complete!")
        return updated_tasks

    def _execute_response_scoring(self, summary_tasks: List[Task]) -> List[Dict[str, Any]]:
        """Execute response scoring for all summaries."""
        print("\n⭐ STEP 3: Response Scoring")

        # Load scoring prompts
        system_prompt = load_prompt(
            self.config.judge_system_prompt, self.config.prompts_path)
        user_prompt = load_prompt(
            self.config.judge_user_prompt, self.config.prompts_path)

        scoring_tasks = []

        # Create scoring tasks for each summary model's response and each critic
        for summary_task in summary_tasks:
            # Get reference answer
            task_index = summary_task.attributes.get('task_index', 0)
            reference_answer = self._get_reference_answer(task_index)

            # Instructions from summary task input
            instructions = summary_task.attributes.get('instructions', '')

            # Get all model responses from the summary task
            model_summaries = summary_task.attributes.get('summaries', {})

            # If no model summaries, fall back to the main result (single model case)
            if not model_summaries and summary_task.result:
                # Single model case - use the first summary model name
                model_name = self.config.summary_apis[0].get(
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
                    'task_id', f'task_{task_index+1}')

                scoring_task = task_factory.create_scoring_task(
                    task_name=f"score_{task_id}_{condition_key}_{summariser}",
                    description=summary_task.description,
                    system_prompt=system_prompt,
                    user_prompt=user_prompt,
                    attributes=attributes
                )
                scoring_tasks.append(scoring_task)

        # Execute scoring pipeline with all scorers
        updated_tasks, all_results = run_scoring_pipeline(
            tasks=scoring_tasks,
            api_configs=self.config.scoring_apis,
            scoring_repeats=self.config.scoring_repeats,
            debug=self.config.debug_mode,
            verbose=self.config.verbose
        )

        print("✅ Response scoring complete!")
        return all_results

    def _get_reference_answer(self, task_index: int = 0) -> str:
        """Get reference answer for scoring by index."""
        # Ensure task_index is within bounds
        if task_index >= len(self.config.reference_answers):
            raise ValueError(
                f"Reference answer not configured: task index {task_index} out of range. "
                f"Available: {len(self.config.reference_answers)} reference answers.")

        return self.config.reference_answers[task_index]

    def organise_scoring_results_to_csv_format(self, scoring_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Organise scoring results into CSV format compatible with combined_results format.

        Args:
            scoring_results: List of scoring result dictionaries from the workflow

        Returns:
            List of dictionaries in standardized CSV format
        """
        organized_results = []

        for result in scoring_results:
            # Multi-model result format - expand model_scores into separate rows
            if 'model_scores' in result and isinstance(result['model_scores'], dict):
                for scorer_model, model_result in result['model_scores'].items():
                    # Get the response model from attributes (the model that generated the summary)
                    summariser = result.get('attributes', {}).get(
                        'summariser', 'unknown_summariser')
                    task_id = result.get('attributes', {}).get(
                        'task_id', result.get('task_name', ''))

                    organized_result = {
                        'task_name': task_id,  # Use clean task ID instead of full task name
                        'condition': result.get('attributes', {}).get('condition', ''),
                        'summariser': summariser,  # Model that generated the summary being scored
                        'scorer': scorer_model,  # Model that provided the score
                        # 'question': result.get('description', ''),
                        'answer': result.get('answer', ''),
                        # 'answer_ref': result.get('attributes', {}).get('answer_ref', ''),
                        'judgment': model_result.get('judgment', ''),
                        'score': model_result.get('score', 0.0)
                    }
                    organized_results.append(organized_result)
            else:
                # Unexpected format - log warning but skip
                print(
                    f"Warning: Unexpected scoring result format for task {result.get('task_name', 'unknown')}")

        return organized_results
