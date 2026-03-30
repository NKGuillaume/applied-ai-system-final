# PawPal+ Project Reflection

## 1. System Design
Add pet 
Sedule a wash and duration is based on size of the dog
 sehucle a walk

**a. Initial design**

- Briefly describe your initial UML design.
The owner is responsible for creating pets. Each pet maintains a collection of tasks that must be performed. These tasks are forwarded to a scheduler, which manages their execution.- What classes did you include, and what responsibilities did you assign to each?
Here’s your UML design written clearly as a paragraph:

The UML design consists of four main classes: Owner, Pet, Task, and Scheduler. The Owner class is responsible for managing pets and includes methods to add, remove, and retrieve pets, maintaining a list of Pet objects. Each Pet has attributes such as age, type, food type, and a list of tasks associated with it. The Pet class also provides methods to manage its tasks. The Task class represents activities that need to be performed and includes attributes like date, time, duration, and a description of the task. The Scheduler class is responsible for managing and organizing tasks; it maintains a list of tasks and provides methods to schedule a task, cancel a task, and retrieve upcoming tasks. In terms of relationships, an Owner can have multiple Pets, each Pet can have multiple Tasks, and the Scheduler handles and organizes these tasks for execution.

**b. Design changes**

- Did your design change during implementation? 
- If yes, describe at least one change and why you made it.
 Add pet: Optional[Pet] to Task and wire Scheduler to manage pet-associated tasks.
Replace time strings with datetime and implement sorting + get_upcoming_tasks.
Switch Scheduler to a priority queue (heap) and add simple persistence (JSON).
Add UUIDs and basic validation for Pet/Task.


---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?

The scheduler considers three constraints: scheduled time (tasks must have a `datetime` to be included), completion status (completed tasks are excluded from upcoming views), and time conflicts (tasks for the same pet within a 30-minute window trigger a warning).

- How did you decide which constraints mattered most?

Time was the most important constraint because without it there is no schedule — a task with no time cannot be ordered or displayed. Completion status was second because showing already-done tasks as "upcoming" would be misleading. Conflict detection was added last as a convenience warning rather than a hard rule, since pet care tasks often run back-to-back intentionally (e.g., bath then dry).

**b. Tradeoffs**

The scheduler checks for conflicts using a 30-minute window around a task's start time, but it does not check whether tasks actually overlap based on their duration. For example, if a "Bath" task starts at 9:00 AM and lasts 60 minutes, and a "Walk" task starts at 9:30 AM, the scheduler will warn about a nearby conflict — but if "Bath" only lasts 10 minutes, there is no real conflict at all.

This tradeoff is reasonable for this project because most pet care tasks are short and loosely scheduled (feeding, walks, grooming), so an exact start-time plus a proximity window is good enough to catch obvious double-bookings without requiring precise end-time tracking. A full overlap check using `start + duration_minutes` would be more accurate but adds complexity, and is only worth it if tasks are long or tightly packed.


**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?

AI was used throughout the project for multiple purposes. During design, it helped identify problems with the original system — such as the redundant `task_count` field and the circular reference between `Pet` and `Owner` — and suggested cleaner alternatives. During implementation, it helped write and refine methods like `next_occurrence()`, `check_conflict()`, and the Streamlit session state setup. It was also used for refactoring, such as simplifying `check_conflict` from three list passes down to one loop and flattening `get_all_tasks` into a single list comprehension.

- What kinds of prompts or questions were most helpful?

The most helpful prompts were specific and diagnostic: "what is wrong with this design and why", "how can this be simplified", and "fix all issues". Broad questions like those produced focused, actionable answers. Asking about a single concept at a time (e.g., how `st.session_state` works, how `timedelta` calculates next dates) also gave clear and directly usable answers.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
