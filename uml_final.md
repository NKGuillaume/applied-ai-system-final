# PawPal+ Final UML Diagram

Paste the Mermaid code below into [https://mermaid.live](https://mermaid.live) and export as `uml_final.png`.

```mermaid
classDiagram
    class Pet {
        +str name
        +str species
        +int age
        +Optional[str] breed
        +List[Task] tasks
    }

    class Owner {
        +str name
        +Dict available_time
        +Dict preferences
        +List[Pet] pets
        +get_all_tasks() List[Task]
        +filter_tasks(completed, pet_name) List[Task]
    }

    class Task {
        +str name
        +str category
        +int duration
        +int priority
        +str frequency
        +str preferred_time
        +bool completed
        +Optional[date] due_date
        +mark_complete() Optional[Task]
    }

    class Schedule {
        +str date
        +Owner owner
        +List scheduled_tasks
        +int total_time
        +add_task(task, start_time, reason)
        +get_plan_summary() List
        +explain_plan() str
        +sort_tasks(tasks, preferences)$ List[Task]
        +generate_plan_with_warnings(date, owner)$ Tuple
    }

    Owner "1" --> "0..*" Pet : owns
    Pet "1" --> "0..*" Task : has
    Schedule "1" --> "1" Owner : reads from
    Task ..> Task : mark_complete() creates next occurrence
```

### Relationships

| Relationship | Description |
|---|---|
| `Owner → Pet` | One owner manages many pets |
| `Pet → Task` | One pet has many tasks |
| `Schedule → Owner` | Schedule reads pets and preferences from the owner |
| `Task ⟶ Task` | `mark_complete()` returns a new Task for the next recurrence |

### Notes on `$` (static/class methods)

- `sort_tasks` is a `@staticmethod` — called as `Schedule.sort_tasks(tasks, prefs)`
- `generate_plan_with_warnings` is a `@classmethod` — called as `Schedule.generate_plan_with_warnings(date, owner)`
