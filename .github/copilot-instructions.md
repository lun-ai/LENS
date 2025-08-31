````instructions
# LENS: Learning Advanced Neural Strategies - AI Agent Instructions

## Project Overview
A hybrid neuro-symbolic framework that generates human-interpretable explanations to improve human generalization on unseen tasks. Combines curriculum-trained ILP (Inductive Logic Programming) with Large Language Models for Ultra-Strong Machine Learning - where AI systems teach knowledge to humans.

## Core Architecture: 3-Stage Pipeline Pattern

**Every domain (circuit, island, ms) follows this workflow:**
1. **Code Interpretation (CI)** → Generate natural language explanations of Prolog programs
2. **Summary Generation** → Create coherent explanations under different experimental conditions  
3. **Response Scoring** → Evaluate explanation quality using multiple critic models

## Essential Source Structure

### Core Modules (Read these first)
- `src/tasks.py` - Task definitions: `ILPTask`, `SummaryTask`, `ResponseScoringTask`, `CodeInterpretationTask`
- `src/pipelines.py` - Pipeline implementations with retry logic, error handling, and ResponseGenerator
- `src/task_factory.py` - **ALWAYS use** `task_factory.create_*_task()` for validation
- `src/utils.py` - High-level workflow functions like `create_tasks_for_condition()`

### Advanced Framework Features
- `src/config.py` - Configuration system with automatic API key loading
- `src/result_persistence.py` - SQLite-backed storage with metadata tracking
- `ADVANCED_FRAMEWORK.md` - Complete guide to new features and migration

### Domain Organization Pattern
```
experiments/
├── tasks/{domain}/          # Task descriptions (task_1.txt, domain.txt)
├── programs/{domain}/       # Prolog programs (target.pl, anonymous_invent.pl)  
├── data/{domain}/          # Training examples (prim.pl files)
└── references/{domain}/    # Reference solutions for scoring
```

## Development Workflows

### Environment & Dependencies
```bash
# ALWAYS use the project's conda environment
conda activate usml
# OR for single commands:
conda run -n usml python your_script.py

# Key dependencies already in environment.yml:
# litellm, anthropic, openai, google-generativeai, pydantic, pandas
```

### Standard Experimental Conditions
**Know these condition names - they're used across all domains:**
- `rm_global` - Reasoning model with domain context only
- `rm_global_local` - Domain + local Prolog examples  
- `lens_np` - LENS with non-anonymized programs
- `lens_np_global` - LENS + global domain context
- `lens_np_global_local` - LENS + global + local context
- `lens_ap` - LENS with anonymized programs (variable names removed)
- `lens_ap_global_local` - LENS + anonymized + all contexts

### Pipeline Execution Patterns
```python
# 1. Always use task factory for validation
from src.task_factory import task_factory

task = task_factory.create_summary_task(
    task_name="circuit_explanation",
    description="Generate circuit explanation", 
    system_prompt=prompt,
    attributes={'condition': 'lens_np', 'domain': 'circuit'}
)

# 2. Use framework pipeline functions (not direct pipeline classes)
from src.pipelines import run_summary_pipeline, run_scoring_pipeline

updated_tasks, results, context = run_summary_pipeline(
    tasks, api_config, verbose=True, debug=False
)

# 3. For production: enable persistence
context = pipeline.run(tasks, persist_results=True)
```

## Critical Code Patterns

### API Configuration (Never hardcode)
```python
# Load from JSON files in workspace root
ds_api = json.load(open('deepseek_api_key.json', 'r'))
anthropic_api = json.load(open('anthropic_api_key.json', 'r'))

# Standard multi-critic pattern (LiteLLM handles provider routing automatically)
critic_models = {
    'claude-3-5-sonnet': anthropic_api,
    'deepseek-reasoner': ds_api, 
    'o3-mini': openai_api
}
```

### Model Provider Integration
- **All APIs unified through LiteLLM** - Single interface for all model providers
- **DeepSeek** (`deepseek-reasoner`) - Primary reasoning model
- **Anthropic** (`claude-3-5-sonnet`, `claude-3-7-sonnet`) - Scoring and analysis
- **OpenAI** (`gpt-4o-mini`, `o3-mini`) - Additional critics
- **Ollama** (`starcoder2:instruct`, `qwen2.5-coder:14b-instruct`) - Code interpretation via LangChain

### API Configuration (Updated for LiteLLM)
```python
# Load from JSON files in workspace root (same as before)
ds_api = json.load(open('deepseek_api_key.json', 'r'))
anthropic_api = json.load(open('anthropic_api_key.json', 'r'))

# LiteLLM automatically handles provider routing
# The ResponseGenerator now uses litellm.completion() internally
# No changes needed to existing API configuration formats
```

### Prompt Loading Pattern
```python
# System and user prompts are separate files in prompts/
system_prompt = open('prompts/summary_system.txt', 'r').read()
user_prompt = open('prompts/summary_user.txt', 'r').read()

# Domain contexts loaded from experiments/tasks/
domain = open('experiments/tasks/circuit/domain.txt', 'r').read()
```

### Result Storage Conventions
- **Workspace results structure:** `results/{domain}/` with subdirectories
- **Code interpretations:** `{model_name}_CI.txt` (named), `{model_name}_CI_ap.txt` (anonymous)
- **Analysis outputs:** `{domain}_framework_results.csv`, `condition_analysis.csv`
- **Metadata tracking:** Automatic in `results/metadata.db`

## Integration Points & Workflows

### Key Reference Files
- `scripts/evaluation.ipynb` - Complete circuit domain workflow
- `scripts/island_evaluation.py` - Island domain automation  
- `examples/framework_usage.py` - Full pipeline demo with fake APIs
- `scripts/statistical_testing.ipynb` - Analysis and visualization

### Data Flow Example (Circuit Domain)
1. Load ILP tasks from `experiments/tasks/circuit/`
2. Generate code interpretations using `CodeInterpretationPipeline`
3. Create summary tasks for each condition using `create_tasks_for_condition()`
4. Generate summaries with `SummaryExplanationPipeline`
5. Score with multiple critics using `ResponseScoringPipeline`
6. Analyze results and save CSV files

## Debugging & Development

### Debug Mode
```python
# Use debug=True to generate mock responses (no API calls)
context = pipeline.run(tasks, debug=True, verbose=True)
```

### Common Issues
- **Import failures:** Check `conda activate usml` environment
- **Missing domain files:** Framework has graceful fallbacks, but verify file paths
- **API errors:** Check rate limits, retry logic handles most transient errors
- **Task validation:** Task factory will catch configuration errors early

### Error Handling
- Pipeline retry logic for rate limits/server errors (`RETRYABLE_ERRORS`)
- `continue_on_error=True` prevents single task failures from stopping pipelines
- Advanced error context in new framework (see `ADVANCED_FRAMEWORK.md`)

## Anti-Patterns to Avoid

❌ **Don't hardcode API keys** - Always load from JSON files  
❌ **Don't bypass task factory** - Validation prevents runtime errors  
❌ **Don't mix domain conditions** - Each domain has specific task names/structure  
❌ **Don't ignore the 3-stage pattern** - CI → Summary → Scoring is fundamental  
❌ **Don't use direct task constructors** - Use `task_factory.create_*_task()`

## Task Names by Domain
- **Circuit:** `['task_1', 'task_2_1', 'task_2_2', 'task_3']`
- **Island:** Check `scripts/island_evaluation.py` for specific task names
- **MS:** Check domain-specific evaluation files

This framework is designed for reproducible experiments across multiple domains with consistent patterns. The advanced framework (see `ADVANCED_FRAMEWORK.md`) adds sophisticated error handling, result persistence, and configuration management while maintaining backwards compatibility.

````
