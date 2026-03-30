from datetime import date, timedelta
from pawpal_system import Owner, Pet, Task, Schedule


def make_owner(*pets):
    owner = Owner(
        name="Test",
        available_time={"morning": (8, 12), "afternoon": (13, 17)},
        preferences={"walking": "high", "feeding": "medium", "enrichment": "low"},
    )
    for pet in pets:
        owner.pets.append(pet)
    return owner


def test_sorting_correctness():
    pet = Pet(name="Fido", species="dog", age=3)
    owner = make_owner(pet)

    pet.tasks.append(Task(name="T_low",  category="enrichment", duration=10, priority=1))
    pet.tasks.append(Task(name="T_high", category="walking",    duration=20, priority=5))
    pet.tasks.append(Task(name="T_mid",  category="feeding",    duration=15, priority=3))

    sorted_tasks = Schedule.sort_tasks(owner.get_all_tasks(), owner.preferences)
    assert sorted_tasks[0].name == "T_high"
    assert sorted_tasks[-1].name == "T_low"


def test_recurrence_logic_daily_completion():
    today = date.today()
    task = Task(name="Feed", category="feeding", duration=10, priority=4,
                frequency="daily", due_date=today)

    next_task = task.mark_complete()

    assert task.completed
    assert next_task is not None
    assert next_task.due_date == today + timedelta(days=1)
    assert not next_task.completed
    assert next_task.name == task.name


def test_conflict_detection_task_does_not_fit():
    pet = Pet(name="Rover", species="dog", age=1)
    owner = Owner(
        name="Carol",
        available_time={"morning": (8, 9)},   # 60 min slot
        preferences={},
    )
    owner.pets.append(pet)
    pet.tasks.append(Task(name="Long walk", category="walking", duration=120, priority=5))

    _, warnings = Schedule.generate_plan_with_warnings("today", owner)
    assert len(warnings) == 1
    assert "Could not schedule" in warnings[0]
    assert "Long walk" in warnings[0]
