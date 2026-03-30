from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone, timedelta
from enum import Enum
from uuid import UUID, uuid4
import json


class Recurrence(Enum):
	NONE = "none"
	DAILY = "daily"
	WEEKLY = "weekly"
	MONTHLY = "monthly"


_RECURRENCE_DAYS = {
	Recurrence.DAILY: 1,
	Recurrence.WEEKLY: 7,
	Recurrence.MONTHLY: 30,
}


def _dt_to_iso(dt: Optional[datetime]) -> Optional[str]:
	return dt.astimezone(timezone.utc).isoformat() if dt else None


def _iso_to_dt(s: Optional[str]) -> Optional[datetime]:
	return datetime.fromisoformat(s) if s else None


@dataclass
class Task:
	"""Represents a single activity (description, time, frequency, completion)."""

	title: str
	description: str = ""
	time: Optional[datetime] = None
	duration_minutes: int = 0
	recurrence: Recurrence = Recurrence.NONE
	is_completed: bool = False
	id: UUID = field(default_factory=uuid4)
	pet_id: Optional[UUID] = None

	def mark_complete(self) -> None:
		"""Mark the task as completed."""
		self.is_completed = True

	def next_occurrence(self) -> Optional["Task"]:
		"""Return a new Task scheduled for the next recurrence, or None if not recurring.

		Uses _RECURRENCE_DAYS to calculate the next time:
		  - DAILY:   self.time + 1 day
		  - WEEKLY:  self.time + 7 days
		  - MONTHLY: self.time + 30 days

		The new Task is a copy of this one (same title, description, duration, recurrence,
		pet_id) with a fresh id and is_completed=False. Returns None if recurrence is NONE
		or if this task has no scheduled time.
		"""
		if self.recurrence == Recurrence.NONE or self.time is None:
			return None
		next_time = self.time + timedelta(days=_RECURRENCE_DAYS[self.recurrence])
		return Task(
			title=self.title,
			description=self.description,
			time=next_time,
			duration_minutes=self.duration_minutes,
			recurrence=self.recurrence,
			pet_id=self.pet_id,
		)

	def to_dict(self) -> Dict[str, Any]:
		"""Serialize Task to a JSON-serializable dict."""
		return {
			"id": str(self.id),
			"title": self.title,
			"description": self.description,
			"time": _dt_to_iso(self.time),
			"duration_minutes": self.duration_minutes,
			"recurrence": self.recurrence.value,
			"is_completed": self.is_completed,
			"pet_id": str(self.pet_id) if self.pet_id else None,
		}

	@classmethod
	def from_dict(cls, data: Dict[str, Any]) -> "Task":
		"""Deserialize Task from a dict produced by `to_dict`."""
		t = cls(
			title=data["title"],
			description=data.get("description", ""),
			time=_iso_to_dt(data.get("time")),
			duration_minutes=int(data.get("duration_minutes", 0)),
			recurrence=Recurrence(data.get("recurrence", "none")),
			is_completed=data.get("is_completed", False),
		)
		t.id = UUID(data["id"]) if data.get("id") else uuid4()
		pet_id = data.get("pet_id")
		t.pet_id = UUID(pet_id) if pet_id else None
		return t


@dataclass
class Pet:
	"""Stores pet details and a list of tasks."""

	name: str
	age: int
	type_: str
	food_type: str
	id: UUID = field(default_factory=uuid4)
	tasks: List[Task] = field(default_factory=list)

	def __post_init__(self) -> None:
		if self.age < 0:
			raise ValueError("age must be non-negative")

	def add_task(self, task: Task) -> None:
		"""Attach a Task to this Pet."""
		task.pet_id = self.id
		self.tasks.append(task)

	def remove_task(self, task: Task) -> None:
		"""Remove a Task from this Pet if present."""
		try:
			self.tasks.remove(task)
			task.pet_id = None
		except ValueError:
			pass

	def to_dict(self) -> Dict[str, Any]:
		"""Serialize Pet to a JSON-serializable dict."""
		return {
			"id": str(self.id),
			"name": self.name,
			"age": self.age,
			"type_": self.type_,
			"food_type": self.food_type,
			"tasks": [t.to_dict() for t in self.tasks],
		}

	@classmethod
	def from_dict(cls, data: Dict[str, Any]) -> "Pet":
		"""Deserialize Pet from a dict produced by `to_dict`."""
		p = cls(
			name=data["name"],
			age=int(data.get("age", 0)),
			type_=data.get("type_", ""),
			food_type=data.get("food_type", ""),
		)
		p.id = UUID(data["id"]) if data.get("id") else uuid4()
		for td in data.get("tasks", []):
			p.tasks.append(Task.from_dict(td))
		return p


@dataclass
class Owner:
	"""Manages multiple pets and provides access to all their tasks."""

	name: str
	contact_info: str = ""
	id: UUID = field(default_factory=uuid4)
	pets: List[Pet] = field(default_factory=list)

	def add_pet(self, pet: Pet) -> None:
		"""Add a Pet to this Owner."""
		self.pets.append(pet)

	def remove_pet(self, pet: Pet) -> None:
		"""Remove a Pet from this Owner."""
		try:
			self.pets.remove(pet)
		except ValueError:
			pass

	def get_all_tasks(self) -> List[Task]:
		"""Return all tasks across the owner's pets."""
		return [t for p in self.pets for t in p.tasks]

	def to_dict(self) -> Dict[str, Any]:
		"""Serialize Owner to a JSON-serializable dict."""
		return {
			"id": str(self.id),
			"name": self.name,
			"contact_info": self.contact_info,
			"pets": [p.to_dict() for p in self.pets],
		}

	@classmethod
	def from_dict(cls, data: Dict[str, Any]) -> "Owner":
		"""Deserialize Owner and attach Pets."""
		o = cls(name=data["name"], contact_info=data.get("contact_info", ""))
		o.id = UUID(data["id"]) if data.get("id") else uuid4()
		for pd in data.get("pets", []):
			o.pets.append(Pet.from_dict(pd))
		return o


class Scheduler:
	"""The Brain that retrieves, organizes, and manages tasks across an owner's pets."""

	def __init__(self, owner: Owner) -> None:
		self._owner = owner

	def schedule_task(self, task: Task, pet: Pet, time: Optional[datetime] = None) -> None:
		"""Schedule a Task; returns a warning string on issues, otherwise None.

		If `task.time` is missing, returns a warning and does not schedule.
		If a time conflict is detected within 30 minutes, a warning is returned
		but the task is still scheduled.
		"""
		if time:
			task.time = time
		if not task.time:
			return "warning: task has no scheduled time; not scheduled"
		# check for lightweight conflicts (both exact-time and within a window)
		conflict = self.check_conflict(task, window_minutes=30)
		# always record the task, but return any conflict message(s)
		pet.add_task(task)
		return conflict

	def check_conflict(self, task: Task, window_minutes: int = 30) -> Optional[str]:
		"""Return a warning string if `task` conflicts with any already-scheduled task.

		Iterates all existing tasks once and classifies each into one of three buckets:
		  - exact_same:   same pet_id, exact same time  → hard conflict
		  - exact_other:  different pet, exact same time → cross-pet conflict
		  - window_close: same pet, within window_minutes of task.time → proximity warning

		All three types produce warning messages that are joined and returned as a single
		string. Returns None when there are no conflicts. This check is non-fatal — the
		caller decides whether to block or just warn.

		Args:
		    task: The candidate Task being evaluated (not yet added to the pet).
		    window_minutes: How many minutes around task.time to flag as "nearby" (default 30).
		"""
		if not task.time:
			return None

		# Gather all other tasks from the owner (excluding the candidate task itself)
		others = [t for t in self._owner.get_all_tasks() if t.id != task.id and t.time]

		window_sec = window_minutes * 60
		exact_same, exact_other, window_close = [], [], []
		for t in others:
			same_pet = t.pet_id == task.pet_id
			exact = t.time == task.time
			if exact and same_pet:
				exact_same.append(t)
			elif exact:
				exact_other.append(t)
			elif same_pet and abs((t.time - task.time).total_seconds()) <= window_sec:
				window_close.append(t)

		messages: List[str] = []
		if exact_same:
			ids = ", ".join(str(t.id) for t in exact_same[:5])
			messages.append(f"warning: exact-time conflict for same pet (ids: {ids})")
		if exact_other:
			ids = ", ".join(str(t.id) for t in exact_other[:5])
			messages.append(f"warning: exact-time conflict across pets (ids: {ids})")
		if window_close and not exact_same:
			ids = ", ".join(str(t.id) for t in window_close[:5])
			messages.append(f"warning: nearby tasks for same pet within {window_minutes} minutes (ids: {ids})")

		return "; ".join(messages) if messages else None

	def cancel_task(self, task: Task, pet: Pet) -> None:
		"""Remove a task from a pet."""
		pet.remove_task(task)

	def complete_task(self, task: Task, pet: Pet) -> None:
		"""Mark a task complete and automatically schedule its next occurrence if recurring.

		Calls task.mark_complete(), then task.next_occurrence(). If a next occurrence
		exists (i.e. recurrence is not NONE), it is added directly to the pet's task list
		via pet.add_task(), which also sets the new task's pet_id. If the task is not
		recurring, nothing further happens.
		"""
		task.mark_complete()
		next_task = task.next_occurrence()
		if next_task is not None:
			pet.add_task(next_task)

	def get_upcoming_tasks(self, limit: Optional[int] = None) -> List[Task]:
		"""Return upcoming incomplete tasks across all owner's pets, sorted by time.

		Filters out tasks that are already completed or scheduled in the past
		(i.e. task.time < now). Results are sorted ascending by time. An optional
		limit caps how many tasks are returned.

		Args:
		    limit: Maximum number of tasks to return. Returns all if None.
		"""
		now = datetime.now(timezone.utc)
		tasks = [
			t for t in self._owner.get_all_tasks()
			if t.time and not t.is_completed and t.time >= now
		]
		tasks.sort(key=lambda t: t.time)
		return tasks[:limit] if limit is not None else tasks

	def print_daily_for_owner(self, date: Optional[datetime] = None) -> None:
		"""Print a day-view schedule for the owner, skipping empty hours."""
		if date is None:
			date = datetime.now(timezone.utc)
		buckets: Dict[int, List[Task]] = {}
		for t in self._owner.get_all_tasks():
			if t.time and t.time.date() == date.date():
				buckets.setdefault(t.time.hour, []).append(t)

		print(f"Schedule for {self._owner.name} on {date.date()}:")
		if not buckets:
			print("  No tasks scheduled.")
			return
		for h in sorted(buckets):
			print(f"{h:02d}:00")
			for t in sorted(buckets[h], key=lambda x: x.time):
				print(f"  - {t.time.time()} {t.title} completed={t.is_completed}")

	def print_upcoming(self, limit: int = 10) -> None:
		"""Print the next `limit` upcoming incomplete tasks."""
		now = datetime.now(timezone.utc)
		tasks = self.get_upcoming_tasks(limit=limit)
		if not tasks:
			print("No upcoming tasks.")
			return
		print("Upcoming tasks:")
		for t in tasks:
			delta = t.time - now
			hours = int(delta.total_seconds() // 3600)
			mins = int((delta.total_seconds() % 3600) // 60)
			eta = f"in {hours}h {mins}m" if delta.total_seconds() > 60 else "now"
			print(f"- {t.title} @ {t.time.isoformat()} (pet_id={t.pet_id}) — {eta}")
