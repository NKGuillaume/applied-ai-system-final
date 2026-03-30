from datetime import datetime, timedelta, timezone
from pawpal_system import Owner, Pet, Task, Scheduler


def in_hours(hours: int = 0) -> datetime:
    return datetime.now(timezone.utc) + timedelta(hours=hours)


def format_timedelta(delta: timedelta) -> str:
    total_seconds = int(delta.total_seconds())
    if total_seconds < 0:
        return "overdue"
    minutes = total_seconds // 60
    hours = minutes // 60
    minutes = minutes % 60
    if hours > 0:
        return f"in {hours}h {minutes}m"
    if minutes > 0:
        return f"in {minutes}m"
    return "now"


if __name__ == "__main__":
    # Demo owner + pets + tasks (replace with real data/load logic as needed)
    owner = Owner(name="Alice", contact_info="alice@example.com")
    c = Pet(name="Fluffy", age=3, type_="Cat", food_type="Dry")
    d = Pet(name="Rover", age=5, type_="Dog", food_type="Wet")

    t1 = Task(title="Morning Walk", description="Walk around block", time=in_hours(1))
    t2 = Task(title="Feed", description="Breakfast", time=in_hours(0.25))
    t3 = Task(title="Medication", description="Pill", time=in_hours(24))

    c.add_task(t2)
    d.add_task(t1)
    d.add_task(t3)

    owner.add_pet(c)
    owner.add_pet(d)

    sched = Scheduler()
    # register as the module-default so Pet.add_task auto-schedules
    from pawpal_system import set_default_scheduler
    set_default_scheduler(sched)
    # Sync tasks from owner (authoritative scheduler)
    sched.sync_tasks_from_owner(owner)

    # subscribe a printer so updates reprint the daily view
    def printer():
        print("\n--- schedule updated ---")
        sched.print_daily_for_owner(owner)

    sched.subscribe(printer)

    tasks = sched.get_tasks_for_owner(owner)
    now = datetime.now(timezone.utc)

    print("Schedule for owner:")
    # initial print
    printer()

    for t in tasks:
        due = t.time if t.time else now
        delta = due - now
        print(f"- {t.title} (pet_id={t.pet_id}) — urgency={t.urgency} — {format_timedelta(delta)} — completed={t.is_completed}")
