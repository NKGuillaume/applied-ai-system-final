from datetime import datetime, timedelta, timezone
from pawpal_system import Pet, Owner, Task


def in_hours(hours: int = 0) -> datetime:
    return datetime.now(timezone.utc) + timedelta(hours=hours)


if __name__ == "__main__":
    owner = Owner(name="Alice", contact_info="alice@example.com")
    pet = Pet(name="Fluffy", age=3, type_="Cat", food_type="Dry")
    pet1 = Pet(name="Rover", age=5, type_="Dog", food_type="Wet")

    task1 = Task(title="Walk", description="Go for a walk", time=in_hours(1), is_completed=False)
    task2 = Task(title="Fetch", description="Play fetch", time=in_hours(2), is_completed=False)

    pet1.add_task(task1)
    pet1.add_task(task2)
    pet1.tasks[0].is_completed = True

    owner.add_pet(pet)
    owner.add_pet(pet1)

    print(owner.to_dict())