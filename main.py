from pawpal_system import Pet, Owner, Task, Schedule
import logging
import os
import argparse
from src.retriever import load_local_docs, Retriever
from src.rag import RAGAgent
from src.agent import MultiStepAgent

# Create pets
pet1 = Pet(name="Mochi", species="dog", age=3, breed="Shih Tzu")
pet2 = Pet(name="Whiskers", species="cat", age=2)

# Create tasks (out of meaningful order intentionally)
task1 = Task(name="Morning walk",      category="walking",     duration=30, priority=5, preferred_time="morning")
task2 = Task(name="Feeding",           category="feeding",     duration=10, priority=4, preferred_time="morning")
task3 = Task(name="Playtime",          category="enrichment",  duration=20, priority=3, preferred_time="afternoon")
task4 = Task(name="Evening grooming",  category="grooming",    duration=25, priority=2, preferred_time="evening")
task5 = Task(name="Medication",        category="meds",        duration=5,  priority=5, preferred_time="morning")
# Two overlapping high-priority tasks to test conflict detection
task6 = Task(name="Vet appointment",   category="meds",        duration=40, priority=5, preferred_time="morning")
task7 = Task(name="Training session",  category="enrichment",  duration=35, priority=5, preferred_time="morning")

# Add tasks to pets out of order (append sequenced differently than priority)
pet1.tasks.append(task2)
pet1.tasks.append(task1)
pet1.tasks.append(task4)
pet1.tasks.append(task6)   # overlapping task for Mochi
pet2.tasks.append(task3)
pet2.tasks.append(task5)
pet2.tasks.append(task7)   # overlapping task for Whiskers

# Mark one task complete to exercise filter behavior
task2.mark_complete()      # Feeding is already done

# Create owner
owner = Owner(
    name="Jordan",
    available_time={"morning": (8, 12), "afternoon": (13, 17)},
    preferences={"walking": "high", "feeding": "high", "enrichment": "medium"},
)
owner.pets.append(pet1)
owner.pets.append(pet2)

# Generate today's schedule with warning detection
today = "2024-10-01"
schedule, warnings = Schedule.generate_plan_with_warnings(today, owner)

# Print the schedule
print("Today's Schedule:")
print(schedule.explain_plan())

# Print any detected warnings/conflicts
if warnings:
    print("\n[!] SCHEDULING CONFLICTS DETECTED:")
    for warning in warnings:
        print(f"  {warning}")
else:
    print("\n[OK] No scheduling conflicts detected.")

print("\nDetailed Plan:")
print(f"{'Task':<22} {'Start':<8} {'End':<8} {'Reason'}")
print("-" * 80)
for entry in schedule.get_plan_summary():
    task_name = entry['task'].name[:21]
    print(f"{task_name:<22} {entry['start_time']:<8} {entry['end_time']:<8} {entry['reason']}")
print(f"\nTotal time: {schedule.total_time} minutes")

# Filter examples
print("\nAll pending tasks:")
for t in owner.filter_tasks(completed=False):
    pet_name = next((p.name for p in owner.pets if t in p.tasks), "unknown")
    print(f"  - {t.name} (pet: {pet_name}, priority {t.priority})")

print("\nTasks for Mochi:")
for t in owner.filter_tasks(pet_name="Mochi"):
    print(f"  - {t.name} (completed={t.completed}, priority {t.priority})")

print("\nTasks sorted by priority & preferences:")
sorted_tasks = schedule.sort_tasks(owner.get_all_tasks(), owner.preferences)
for t in sorted_tasks:
    print(f"  - {t.name} (priority {t.priority}, completed={t.completed})")


# --- RAG demo (optional) -------------------------------------------------
logging.basicConfig(level=logging.INFO)
parser = argparse.ArgumentParser(description='Run PawPal demo and optional RAG demo')
parser.add_argument('--rag', action='store_true', help='Enable RAG demo (disabled by default)')
parser.add_argument('--agent', action='store_true', help='Enable multi-step agent demo')
args = parser.parse_args()

if args.rag:
    print("\n--- RAG Demo: retrieve local docs and answer sample queries ---\n")
    try:
        project_root = os.getcwd()
        docs = load_local_docs([project_root, os.path.join(project_root, 'assets')])
        if not docs:
            print("No local docs found for RAG demo (checked project root and assets/). Skipping RAG demo.")
        else:
            retriever = Retriever()
            retriever.build_index(docs)
            agent = RAGAgent(retriever)

            sample_queries = [
                "Summarize the project's testing approach",
                "Explain why genre and mood influence scheduling in this project",
            ]
            for q in sample_queries:
                print(f"Query: {q}")
                try:
                    answer = agent.answer(q)
                    print("Answer:")
                    # Backwards-compatible: support string or dict
                    if isinstance(answer, dict):
                        print(answer.get('text', ''))
                        print(f"[confidence={answer.get('confidence', 0.0):.2f}]")
                    else:
                        print(str(answer))
                except Exception as e:
                    logging.exception('RAG agent failed')
                    print(f"RAG error: {e}")
                print("\n" + ("-" * 60) + "\n")
    except Exception as e:
        logging.exception('Failed to run RAG demo')
        print(f"Failed to run RAG demo: {e}")
else:
    print('\nRAG demo disabled. Run with --rag to enable retrieval-augmented answers.')

if args.agent:
    print('\n--- Multi-step Agent Demo (observable steps) ---\n')
    try:
        project_root = os.getcwd()
        docs = load_local_docs([project_root, os.path.join(project_root, 'assets')])
        if not docs:
            print('No local docs found for agent demo (checked project root and assets/). Skipping agent demo.')
        else:
            retriever = Retriever()
            retriever.build_index(docs)
            agent = MultiStepAgent(retriever)

            sample_queries = [
                'Summarize the project\'s testing approach',
                'Explain why owner preferences change scheduling decisions',
            ]
            for q in sample_queries:
                print(f'Query: {q}')
                try:
                    result = agent.run(q)
                    print('\nIntermediate steps:')
                    for s in result.get('steps', []):
                        print(f"- {s.get('step')}: {s.get('detail')}")
                    print('\nFinal Answer:')
                    if isinstance(result, dict):
                        print(result.get('text', ''))
                        print(f"[confidence={result.get('confidence', 0.0):.2f}]")
                    else:
                        print(str(result))
                except Exception as e:
                    logging.exception('Agent failed')
                    print(f'Agent error: {e}')
                print('\n' + ('-' * 60) + '\n')
    except Exception as e:
        logging.exception('Failed to run agent demo')
        print(f'Failed to run agent demo: {e}')
else:
    print('\nAgent demo disabled. Run with --agent to enable observable multi-step agent.')
