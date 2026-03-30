import pytest
from datetime import date, timedelta
from pawpal_system import Pet, Task, Owner, Schedule


# --- helpers ---

def make_owner_with_pet():
    owner = Owner(
        name="Alice",
        available_time={"morning": (8, 12), "afternoon": (13, 17)},
        preferences={"walking": "high", "feeding": "medium"},
    )
    pet = Pet(name="Fluffy", species="cat", age=3)
    owner.pets.append(pet)
    return owner, pet


# --- Task basics ---

def test_mark_complete_changes_status():
    t = Task(name="Feed", category="feeding", duration=10, priority=3)
    assert not t.completed
    t.mark_complete()
    assert t.completed


def test_adding_task_increases_pet_count():
    p = Pet(name="Kitty", species="cat", age=1)
    initial = len(p.tasks)
    t = Task(name="Feed", category="feeding", duration=10, priority=3)
    p.tasks.append(t)
    assert len(p.tasks) == initial + 1


# --- Sorting correctness ---

def test_sort_tasks_high_priority_first():
    prefs = {"walking": "high", "feeding": "medium", "grooming": "low"}
    t_low  = Task(name="Groom", category="grooming", duration=20, priority=1)
    t_mid  = Task(name="Feed",  category="feeding",  duration=10, priority=3)
    t_high = Task(name="Walk",  category="walking",  duration=30, priority=5)

    result = Schedule.sort_tasks([t_low, t_mid, t_high], prefs)
    assert result[0].name == "Walk"
    assert result[-1].name == "Groom"


def test_sort_tasks_preference_boosts_rank():
    # Same priority, but "walking" has high preference vs "grooming" low
    prefs = {"walking": "high", "grooming": "low"}
    t_walk  = Task(name="Walk",  category="walking",  duration=30, priority=3)
    t_groom = Task(name="Groom", category="grooming", duration=20, priority=3)

    result = Schedule.sort_tasks([t_groom, t_walk], prefs)
    assert result[0].name == "Walk"


def test_sort_completed_tasks_included_in_output():
    # sort_tasks does not filter — it just orders
    prefs = {"walking": "high"}
    t1 = Task(name="Done",    category="walking", duration=10, priority=5, completed=True)
    t2 = Task(name="Pending", category="walking", duration=10, priority=3)

    result = Schedule.sort_tasks([t1, t2], prefs)
    assert len(result) == 2
    assert result[0].name == "Done"


# --- Recurrence logic ---

def test_daily_recurrence_creates_next_day_task():
    today = date.today()
    task = Task(name="Walk", category="walking", duration=30, priority=5,
                frequency="daily", due_date=today)
    next_task = task.mark_complete()

    assert task.completed
    assert next_task is not None
    assert next_task.due_date == today + timedelta(days=1)
    assert not next_task.completed


def test_weekly_recurrence_creates_next_week_task():
    today = date.today()
    task = Task(name="Groom", category="grooming", duration=20, priority=3,
                frequency="weekly", due_date=today)
    next_task = task.mark_complete()

    assert next_task is not None
    assert next_task.due_date == today + timedelta(weeks=1)


def test_none_recurrence_returns_no_next_task():
    task = Task(name="One-off", category="meds", duration=5, priority=5, frequency="none")
    next_task = task.mark_complete()

    assert task.completed
    assert next_task is None


def test_next_task_copies_name_and_duration():
    today = date.today()
    task = Task(name="Feed", category="feeding", duration=15, priority=4,
                frequency="daily", due_date=today)
    next_task = task.mark_complete()

    assert next_task.name == task.name
    assert next_task.duration == task.duration
    assert next_task.frequency == task.frequency


# --- Conflict / schedule warnings ---

def test_task_too_long_produces_unscheduled_warning():
    owner = Owner(
        name="Test",
        available_time={"morning": (8, 9)},   # only 60 min available
        preferences={},
    )
    pet = Pet(name="Buddy", species="dog", age=2)
    owner.pets.append(pet)
    pet.tasks.append(Task(name="Long task", category="walking", duration=90, priority=5))

    _, warnings = Schedule.generate_plan_with_warnings("today", owner)
    assert any("Could not schedule" in w for w in warnings)


def test_completed_tasks_excluded_from_schedule():
    owner, pet = make_owner_with_pet()
    done = Task(name="Done",    category="feeding", duration=10, priority=5, completed=True)
    todo = Task(name="Pending", category="walking", duration=20, priority=4)
    pet.tasks.extend([done, todo])

    schedule, _ = Schedule.generate_plan_with_warnings("today", owner)
    names = [e["task"].name for e in schedule.get_plan_summary()]
    assert "Done" not in names
    assert "Pending" in names


def test_schedule_total_time_matches_tasks():
    owner, pet = make_owner_with_pet()
    t1 = Task(name="Walk", category="walking", duration=30, priority=5)
    t2 = Task(name="Feed", category="feeding", duration=10, priority=3)
    pet.tasks.extend([t1, t2])

    schedule, _ = Schedule.generate_plan_with_warnings("today", owner)
    assert schedule.total_time == 40


def test_schedule_tasks_sorted_by_start_time():
    owner, pet = make_owner_with_pet()
    pet.tasks.append(Task(name="Walk", category="walking", duration=30, priority=5, preferred_time="morning"))
    pet.tasks.append(Task(name="Feed", category="feeding", duration=10, priority=3, preferred_time="morning"))

    schedule, _ = Schedule.generate_plan_with_warnings("today", owner)
    summary = schedule.get_plan_summary()
    start_times = [e["start_time"] for e in summary]
    assert start_times == sorted(start_times)
