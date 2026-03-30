from pawpal_system import Owner, Pet, Task, Scheduler
from datetime import datetime, timezone, timedelta


def in_hours(h=0):
    return datetime.now(timezone.utc) + timedelta(hours=h)


if __name__ == "__main__":
    owner = Owner(name="Bob", contact_info="bob@example.com")
    p = Pet(name="Buddy", age=2, type_="Dog", food_type="Dry")
    t1 = Task(title="Feed", description="Feed Buddy", time=in_hours(1))
    p.add_task(t1)
    owner.add_pet(p)

    sched = Scheduler()
    print("Before sync, scheduler tasks:", sched.get_upcoming_tasks())
    sched.sync_tasks_from_owner(owner)
    print("After sync, scheduler tasks:", [(t.title, str(t.pet_id)) for t in sched.get_upcoming_tasks()])
