"""
Dependent ILP Learning Example

Demonstrates how to learn Prolog programs in a dependent sequence where each
task builds on the previous learned programs. Uses the circuit domain with the
learning order: inv_0 → inv_1 → inv_2 → inv_3 → inv_4
"""

from pathlib import Path
from src.pipelines import ILPLearningPipeline
from src.task_factory import task_factory


def main():
    """Run dependent ILP learning example."""
    print("🔗 Dependent ILP Learning Example")
    print("=" * 50)
    print("Learning circuit domain programs in dependent sequence:")
    print("inv_0 → inv_1 → inv_2 → inv_3 → inv_4")
    print()

    # Define the learning sequence with dependencies
    learning_sequence = [
        {
            'name': 'inv_0',
            'kb_path': 'experiments/programs/circuit/inv_0',
            'depends_on': None,  # First task has no dependencies
            'max_ho': 3,
            'max_rules': 3
        },
        {
            'name': 'inv_1',
            'kb_path': 'experiments/programs/circuit/inv_1',
            'depends_on': 'inv_0',
            'max_ho': 3,
            'max_rules': 3,
            'negation': True  # Enable negation for this task
        },
        {
            'name': 'inv_2',
            'kb_path': 'experiments/programs/circuit/inv_2',
            'depends_on': ['inv_0', 'inv_1'],
            'max_ho': 3,
            'max_rules': 3
        },
        {
            'name': 'inv_3',
            'kb_path': 'experiments/programs/circuit/inv_3',
            'depends_on': ['inv_0', 'inv_1', 'inv_2'],
            'max_ho': 3,
            'max_rules': 3
        },
        {
            'name': 'inv_4',
            'kb_path': 'experiments/programs/circuit/inv_4',
            'depends_on': ['inv_0', 'inv_1', 'inv_2', 'inv_3'],
            'max_ho': 3,
            'max_rules': 3,
            'max_body': 4
        }
    ]

    try:
        # Create a single pipeline instance to maintain learned program cache
        pipeline = ILPLearningPipeline()

        # Learn each task in sequence
        for i, task_config in enumerate(learning_sequence):
            print(f"📚 Episode {i+1}: Learning {task_config['name']}")

            # Create ILP learning task
            task = task_factory.create_ilp_learning_task(
                task_name=task_config['name'],
                description=f"Learn Prolog rules for {task_config['name']}",
                attributes=task_config
            )

            # Run learning (debug mode for demonstration)
            updated_tasks = pipeline.run([task], debug=False, verbose=False)

            learned_task = updated_tasks[0]
            print(f"✅ Learned program for {learned_task.task_name}")
            print(f"   Dependencies: {task_config['depends_on'] or 'None'}")
            print(
                f"   Cached programs: {list(pipeline.learned_programs.keys())}")
            print()

        print("🎉 Dependent learning sequence completed!")

        # Show final state
        print("\n📊 Final Results:")
        print(f"• Total learned programs: {len(pipeline.learned_programs)}")
        print(
            f"• Learning sequence: {' → '.join([t['name'] for t in learning_sequence])}")

        print("\n📋 Learned Programs Cache:")
        print('=' * 50)
        for _, program in pipeline.learned_programs.items():
            print(f"{program}")
            print('=' * 50)

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
