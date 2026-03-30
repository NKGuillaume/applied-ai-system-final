# PawPal+ (Module 2 Project)

A Streamlit app that helps a pet owner plan daily care tasks for their pets, using priority-based scheduling, owner preferences, and automatic conflict detection.

---

## Features

- **Priority × preference sorting** — Tasks are ranked by `priority × preference_weight` before being scheduled. A walking task marked priority 5 with a "high" walking preference outranks a grooming task with the same priority but a "low" preference.

- **Time-slot scheduling** — The owner's day is divided into named slots (morning, afternoon, evening). Each task is placed into its preferred slot first, then falls back to the next available slot if the preferred one is full.

- **Conflict detection** — After scheduling, the system scans for tasks assigned the same start time and reports them as warnings. Tasks that are too long to fit in any slot are reported separately as unscheduled.

- **Recurring tasks** — Tasks can repeat `daily`, `weekly`, or not at all (`none`). Calling `mark_complete()` automatically returns the next occurrence with the correct due date using Python's `timedelta`.

- **Completed task filtering** — Only incomplete tasks are included when generating a schedule. Done tasks are silently excluded so they never clutter the plan.

- **Filtered task views** — `Owner.filter_tasks()` lets you query tasks by completion status or by pet name, useful for per-pet summaries.

---

## Smarter Scheduling

The scheduling algorithm in `Schedule.generate_plan_with_warnings()`:

1. Collects all incomplete tasks from the owner's pets
2. Sorts them by `priority × preference_weight` (highest first)
3. For each task, tries its preferred time slot first, then falls back to others in order
4. Tasks that don't fit in any slot generate an "unscheduled" warning
5. After placement, scans for start-time conflicts and adds conflict warnings
6. Returns `(schedule, warnings)` — the UI decides how to display each

---

## 📸 Demo

<a href="/course_image/image.png" target="_blank"><img src='/course_image/image.png' title='PawPal App' width='' alt='PawPal App' class='center-block' /></a>

---

## Testing PawPal+

### Run the tests

```bash
python -m pytest
```

### What the tests cover

| Behavior | Why it matters |
|---|---|
| `mark_complete()` sets `completed = True` | Core status change must be reliable |
| Adding a task increases `pet.tasks` count | Tasks must attach to pets correctly |
| `sort_tasks` ranks high priority + high preference first | Wrong ordering breaks the whole schedule |
| Preference weight boosts rank at equal priority | Owner preferences must be respected |
| Daily recurrence returns a task due tomorrow | Auto-scheduling must use correct `timedelta` |
| Weekly recurrence returns a task due next week | Same — different interval |
| `frequency="none"` returns `None` | Non-recurring tasks must not spawn copies |
| Next task copies name and duration | Recurrence must carry forward correct data |
| Task too long produces an unscheduled warning | Slot overflow must be detected and reported |
| Completed tasks excluded from the schedule | Done tasks must not reappear in the plan |
| Total scheduled time matches sum of durations | Schedule accounting must be accurate |
| Scheduled tasks appear in start-time order | Output must be chronological |

### Confidence level

⭐⭐⭐⭐ (4/5) — All 17 tests pass. The remaining gap is Streamlit UI testing (session state, form submission).

---

## UML Diagram

See `uml_final.md` for the Mermaid.js source. Render at [mermaid.live](https://mermaid.live) and export as `uml_final.png`.

**Class relationships:**

| Relationship | Description |
|---|---|
| `Owner → Pet` | One owner manages many pets |
| `Pet → Task` | One pet has many tasks |
| `Schedule → Owner` | Schedule reads pets and preferences from the owner |
| `Task → Task` | `mark_complete()` returns the next occurrence |

---

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Run the app

```bash
streamlit run app.py
```

### Run main.py demo

```bash
python main.py
```
