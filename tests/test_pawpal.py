import pytest
from datetime import datetime, timezone
from pawpal_system import Pet, Task


def test_mark_complete_changes_status():
	t = Task(title="Test", description="", time=datetime.now(timezone.utc))
	assert not t.is_completed
	t.mark_complete()
	assert t.is_completed


def test_adding_task_increases_pet_count():
	p = Pet(name="Kitty", age=1, type_="Cat", food_type="Dry")
	initial = len(p.tasks)
	t = Task(title="Feed", description="", time=datetime.now(timezone.utc))
	p.add_task(t)
	assert len(p.tasks) == initial + 1
	# the task should be linked to the pet
	assert p.tasks[-1].pet_id == p.id

