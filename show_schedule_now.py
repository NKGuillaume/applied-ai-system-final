from datetime import datetime, timedelta, timezone
from pawpal_system import Scheduler, Owner, Pet, Task


def in_hours(h):
    return datetime.now(timezone.utc) + timedelta(hours=h)


owner = Owner(name="Alice", contact_info="alice@example.com")
pet = Pet(name="Fluffy", age=3, type_="Cat", food_type="Dry")
pet1 = Pet(name="Rover", age=5, type_="Dog", food_type="Wet")

t1 = Task(title="Feed", description="Breakfast", time=in_hours(0.25))
t2 = Task(title="Walk", description="Morning", time=in_hours(1))
t3 = Task(title="Meds", description="Pill", time=in_hours(24))

pet.add_task(t1)
pet1.add_task(t2)
pet1.add_task(t3)

owner.add_pet(pet)
owner.add_pet(pet1)

sched = Scheduler()
for p in owner.get_pets():
    for t in p.tasks:
        sched.schedule_task(t)

print("=== Upcoming ===")
sched.print_upcoming(owner)

print("\n=== Daily ===")
sched.print_daily_for_owner(owner)
