from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Task:
	"""Represents a scheduled task for a pet (feeding, walk, meds, etc.)."""

	title: str
	description: str = ""
	time: str = ""
	recurrence: str = ""
	is_completed: bool = False

	def mark_complete(self) -> None:
		self.is_completed = True


@dataclass
class Pet:
	"""Represents a pet with basic info and a list of tasks."""

	name: str
	age: int
	type_: str
	food_type: str
	tasks: List[Task] = field(default_factory=list)

	def add_task(self, task: Task) -> None:
		self.tasks.append(task)

	def remove_task(self, task: Task) -> None:
		try:
			self.tasks.remove(task)
		except ValueError:
			pass

	def feed(self) -> None:
		# placeholder for feeding logic
		print(f"Feeding {self.name} with {self.food_type}")


@dataclass
class Owner:
	"""Represents a pet owner who may have one or more pets."""

	name: str
	contact_info: str = ""
	pets: List[Pet] = field(default_factory=list)

	def add_pet(self, pet: Pet) -> None:
		self.pets.append(pet)

	def remove_pet(self, pet: Pet) -> None:
		try:
			self.pets.remove(pet)
		except ValueError:
			pass

	def get_pets(self) -> List[Pet]:
		return self.pets


class Scheduler:
	"""Simple scheduler that manages tasks for pets."""

	def __init__(self) -> None:
		self.tasks: List[Task] = []

	def schedule_task(self, task: Task, time: Optional[str] = None) -> None:
		if time:
			task.time = time
		self.tasks.append(task)

	def cancel_task(self, task: Task) -> None:
		try:
			self.tasks.remove(task)
		except ValueError:
			pass

	def get_upcoming_tasks(self) -> List[Task]:
		return list(self.tasks)

