# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Smarter Scheduling

The scheduler goes beyond simple task storage with three algorithmic features:

- **Recurring tasks** — Tasks can be set to repeat `daily`, `weekly`, or `monthly`. When `Scheduler.complete_task()` is called, it automatically creates the next occurrence using `timedelta` and adds it to the pet, so the schedule stays populated without any manual re-entry.

- **Conflict detection** — Before adding a task, `check_conflict()` scans existing tasks in a single pass and flags three types of problems: exact same time for the same pet (hard conflict), exact same time across different pets (cross-pet conflict), and any task within 30 minutes for the same pet (proximity warning). Conflicts are non-fatal — the task is still scheduled but the caller receives a warning string.

- **Filtered upcoming view** — `get_upcoming_tasks()` only returns tasks that are both incomplete and in the future, sorted by time. This means the schedule always shows what actually needs to be done next, not a mix of done and overdue items.

## Testing PawPal+

### Run the tests

```bash
python -m pytest
```

### What the tests cover

| Area | Tests |
|---|---|
| **Task completion** | Marking a task complete sets `is_completed = True` |
| **Pet task list** | Adding a task increases count and sets `pet_id` correctly |
| **Sorting correctness** | `get_upcoming_tasks` returns tasks in chronological order |
| **Filtering** | Completed and past tasks are excluded from upcoming view |
| **Recurrence — daily** | Completing a daily task auto-creates a task for the next day |
| **Recurrence — weekly** | Completing a weekly task auto-creates a task 7 days later |
| **Recurrence — none** | Non-recurring tasks do not produce a follow-up task |
| **Next occurrence copy** | The new task inherits title, duration, and recurrence; gets a fresh id |
| **Conflict — exact same pet** | Two tasks at the same time for the same pet trigger a warning |
| **Conflict — no overlap** | Well-spaced tasks produce no warning |
| **Conflict — proximity** | Tasks within 30 minutes for the same pet trigger a proximity warning |
| **Conflict — cross-pet** | Same time across different pets triggers a cross-pet warning |

### Confidence level

⭐⭐⭐⭐ (4/5)

The core scheduling behaviors — sorting, recurrence, and conflict detection — are fully tested and all 15 tests pass. The remaining gap is end-to-end UI testing (Streamlit forms, session state persistence) and edge cases like scheduling across midnight or month boundaries, which are not yet covered.

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.
