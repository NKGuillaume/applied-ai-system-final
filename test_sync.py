from pawpal_system import Owner, Pet, Task, Schedule


def test_schedule_reflects_pet_tasks():
    owner = Owner(
        name="Bob",
        available_time={"morning": (8, 12)},
        preferences={"feeding": "high"},
    )
    pet = Pet(name="Buddy", species="dog", age=2)
    pet.tasks.append(Task(name="Feed Buddy", category="feeding", duration=10, priority=5))
    owner.pets.append(pet)

    schedule, warnings = Schedule.generate_plan_with_warnings("today", owner)

    assert len(schedule.get_plan_summary()) == 1
    assert schedule.get_plan_summary()[0]["task"].name == "Feed Buddy"
    assert warnings == []
