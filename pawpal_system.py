from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import List, Dict, Optional, Tuple


@dataclass
class Pet:
    """Stores pet details and a list of tasks."""

    name: str
    species: str
    age: int
    breed: Optional[str] = None
    tasks: List['Task'] = field(default_factory=list)


@dataclass
class Owner:
    """Manages multiple pets, available time slots, and scheduling preferences."""

    name: str
    available_time: Dict[str, Tuple[int, int]]
    preferences: Dict[str, str]
    pets: List[Pet] = field(default_factory=list)

    def get_all_tasks(self) -> List['Task']:
        """Collect and return all tasks from every pet."""
        return [t for pet in self.pets for t in pet.tasks]

    def filter_tasks(
        self,
        completed: Optional[bool] = None,
        pet_name: Optional[str] = None,
    ) -> List['Task']:
        """Return tasks filtered by completion status and/or pet name.

        Args:
            completed: If given, only return tasks matching this completion state.
            pet_name: If given, only return tasks belonging to this pet.
        """
        filtered = []
        for pet in self.pets:
            if pet_name is not None and pet.name != pet_name:
                continue
            for task in pet.tasks:
                if completed is not None and task.completed != completed:
                    continue
                filtered.append(task)
        return filtered


@dataclass
class Task:
    """Represents a single pet care activity with priority, duration, and recurrence."""

    name: str
    category: str
    duration: int
    priority: int
    frequency: str = "daily"         # "daily", "weekly", or "none"
    preferred_time: str = "anytime"  # "morning", "afternoon", "evening", or "anytime"
    completed: bool = False
    due_date: Optional[date] = None

    def mark_complete(self) -> Optional['Task']:
        """Mark this task complete and return the next occurrence if recurring.

        For daily tasks: next due date = today + 1 day.
        For weekly tasks: next due date = today + 7 days.
        For non-recurring tasks: returns None.
        """
        self.completed = True

        if self.frequency not in ("daily", "weekly"):
            return None

        next_date = self.due_date if self.due_date else date.today()
        if self.frequency == "daily":
            next_date = next_date + timedelta(days=1)
        else:
            next_date = next_date + timedelta(weeks=1)

        return Task(
            name=self.name,
            category=self.category,
            duration=self.duration,
            priority=self.priority,
            frequency=self.frequency,
            preferred_time=self.preferred_time,
            completed=False,
            due_date=next_date,
        )


class Schedule:
    """Builds and stores a day's task schedule for an owner's pets.

    Uses available time slots (e.g. morning: 8–12) and owner preferences to
    assign tasks in priority order. Detects conflicts and tasks that don't fit.
    """

    def __init__(self, date: str, owner: Owner) -> None:
        self.date = date
        self.owner = owner
        self.scheduled_tasks: List[Dict] = []
        self.total_time: int = 0

    def add_task(self, task: Task, start_time: str, reason: str) -> None:
        """Add a task entry to the schedule.

        Calculates end_time from start_time + task.duration and appends a dict
        with keys: task, start_time, end_time, reason.
        """
        h, m = map(int, start_time.split(':'))
        end_total = h * 60 + m + task.duration
        end_time = f"{end_total // 60:02d}:{end_total % 60:02d}"
        self.scheduled_tasks.append({
            "task": task,
            "start_time": start_time,
            "end_time": end_time,
            "reason": reason,
        })
        self.total_time += task.duration

    def get_plan_summary(self) -> List[Dict]:
        """Return the list of scheduled task entries."""
        return self.scheduled_tasks

    def explain_plan(self) -> str:
        """Return a human-readable summary of the schedule."""
        if not self.scheduled_tasks:
            return "No tasks could be scheduled for this day."
        lines = [f"Schedule for {self.date} — {self.owner.name}:"]
        for e in self.scheduled_tasks:
            lines.append(f"  {e['start_time']}–{e['end_time']}: {e['task'].name} — {e['reason']}")
        lines.append(f"\nTotal scheduled time: {self.total_time} minutes")
        return "\n".join(lines)

    @staticmethod
    def sort_tasks(tasks: List[Task], preferences: Dict[str, str]) -> List[Task]:
        """Return tasks sorted descending by combined priority × preference weight.

        Tasks with a high-preference category and high priority rank first.
        Tasks with equal scores preserve their original relative order.
        """
        weights = {"high": 3, "medium": 2, "low": 1}

        def score(t: Task) -> Tuple[int, int]:
            pref_weight = weights.get(preferences.get(t.category, "medium"), 2)
            return (t.priority * pref_weight, t.priority)

        return sorted(tasks, key=score, reverse=True)

    @classmethod
    def generate_plan_with_warnings(
        cls,
        date: str,
        owner: Owner,
    ) -> Tuple['Schedule', List[str]]:
        """Build a full day schedule and return (schedule, warnings).

        Algorithm:
        1. Collect all incomplete tasks from owner's pets.
        2. Sort by priority × preference weight (highest first).
        3. For each task, try to fit it into its preferred slot first,
           then fall back to other available slots in order.
        4. Tasks that don't fit in any slot produce an unscheduled warning.
        5. After scheduling, scan for exact start-time conflicts (same start
           time assigned to two different tasks) and add conflict warnings.

        Args:
            date: Date string for display (e.g. "2024-10-01").
            owner: Owner whose pets and preferences are used.
        """
        schedule = cls(date=date, owner=owner)
        warnings: List[str] = []

        pending = [t for t in owner.get_all_tasks() if not t.completed]
        sorted_tasks = cls.sort_tasks(pending, owner.preferences)

        # Current minute pointer per slot (e.g. "morning" -> 480 for 08:00)
        slot_current: Dict[str, int] = {
            name: start * 60
            for name, (start, _) in owner.available_time.items()
        }
        slot_end: Dict[str, int] = {
            name: end * 60
            for name, (_, end) in owner.available_time.items()
        }
        default_slot_order = list(owner.available_time.keys())

        for task in sorted_tasks:
            preferred = task.preferred_time
            if preferred == "anytime":
                slots_to_try = default_slot_order
            else:
                slots_to_try = [preferred] + [s for s in default_slot_order if s != preferred]

            scheduled = False
            for slot in slots_to_try:
                if slot not in slot_current:
                    continue
                cur = slot_current[slot]
                if cur + task.duration <= slot_end[slot]:
                    start_h, start_m = divmod(cur, 60)
                    start_time = f"{start_h:02d}:{start_m:02d}"
                    pref_label = owner.preferences.get(task.category, "medium")
                    reason = f"Priority {task.priority}/5, {pref_label} preference"
                    if slot != preferred and preferred != "anytime":
                        reason += f" (rescheduled: {preferred} slot full)"
                    schedule.add_task(task, start_time, reason)
                    slot_current[slot] += task.duration
                    scheduled = True
                    break

            if not scheduled:
                warnings.append(
                    f"Could not schedule '{task.name}' — no available slot fits {task.duration} min"
                )

        # Detect exact start-time conflicts across tasks
        seen: Dict[str, Task] = {}
        for entry in schedule.scheduled_tasks:
            st_key = entry["start_time"]
            if st_key in seen:
                warnings.append(
                    f"Time conflict at {st_key}: '{entry['task'].name}' overlaps with '{seen[st_key].name}'"
                )
            else:
                seen[st_key] = entry["task"]

        return schedule, warnings
