# PawPal+ Project Reflection

---

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.

The UML design consists of four main classes: Owner, Pet, Task, and Schedule. The Owner class is responsible for managing pets and includes methods to add, remove, and retrieve pets, maintaining a list of Pet objects. Each Pet has attributes such as species, age, breed, and a list of tasks. The Task class represents activities that need to be performed and includes attributes like name, category, duration, priority, preferred time, and frequency. The Schedule class acts as the brain — it takes an Owner and builds a day's plan by fitting tasks into available time slots based on priority and preferences. In terms of relationships, an Owner can have multiple Pets, each Pet can have multiple Tasks, and the Schedule organizes those tasks into a timed plan.

- What classes did you include, and what responsibilities did you assign to each?

The Pet class stores information about each pet, including species, age, and breed, and maintains a list of associated tasks. The Owner class manages the pets, available time slots, and category preferences, acting as the central coordinator. The Task class represents an individual care activity, defined by its priority, duration, frequency, and preferred time. The Schedule class is responsible for organizing tasks by sorting them based on priority and preference weight, then assigning them to appropriate time slots.

**b. Design changes**

- Did your design change during implementation?

Yes.

- If yes, describe at least one change and why you made it.

The biggest change was replacing Scheduler (datetime-based) with Schedule (time-slot-based). The original design used exact datetime values for each task and kept a separate in-memory store inside the scheduler. This created two sources of truth — tasks lived on pets AND in the scheduler's dict — which could go out of sync. The new design removed that entirely. Tasks live only on pets, and Schedule.generate_plan_with_warnings() reads from the owner's pets directly. Scheduling is done by filling named time slots (morning, afternoon, evening) in priority order, which is simpler and more realistic for a pet care app.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?

The scheduler considers three constraints: available time slots (tasks must fit within the owner's morning/afternoon/evening windows), completion status (completed tasks are excluded from the plan), and priority combined with owner preferences (tasks are ranked by priority × preference_weight before being assigned to slots).

- How did you decide which constraints mattered most?

Available time was the most important — if a task cannot fit in any slot, it simply cannot be scheduled. Priority and preference together determine order, since a high-priority task in a preferred category should always be scheduled before a low-priority one. Completion status is a filter, not a ranking factor — done tasks are removed before any sorting happens.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.

The scheduler fills slots sequentially without looking ahead. If a low-priority long task fills the morning slot, a high-priority short task that preferred morning gets moved to afternoon — even though placing the short task first would have left room for both.

- Why is that tradeoff reasonable for this scenario?

Tasks are sorted by priority before scheduling, so high-priority tasks are always attempted first. The greedy approach only fails when a high-priority task is very long and fills the slot before a lower-priority short task can be placed — an edge case that rarely matters in real pet care scheduling.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?

AI was used throughout the project for multiple purposes. During design, it helped identify problems with the original system — such as the redundant task_count field, the circular reference between Pet and Owner, and the dual-store problem between pets and the scheduler.  It was also used for refactoring, such as removing unused attributes like special_needs and for rewriting tests after the system design changed.

- What kinds of prompts or questions were most helpful?

The most helpful prompts were specific and diagnostic: "what is wrong with this design and why", "how can this be simplified", and "fix all issues". Asking about one concept at a time (e.g. how st.session_state persists data, how timedelta calculates next dates) also gave clear and directly usable answers.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.

When AI rewrote the test suite, the first version still imported Scheduler and Recurrence from the old system, which caused import errors on every test file.

- How did you evaluate or verify what the AI suggested?

I ran python -m pytest to verify, saw the failures, and asked for the tests to be rewritten for the new Schedule-based API. This showed that AI suggestions always need to be run — generated code can look correct but still be wrong if it is based on a stale understanding of the codebase.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?

Here’s your table rewritten as a clean paragraph:

The mark_complete() function sets completed = True, which is essential because the core status change must be reliable. Adding a task increases the pet.tasks count, ensuring tasks properly attach to pets. The sort_tasks function ranks tasks with high priority and high preference first, since incorrect ordering would break the entire schedule. Preference weight boosts ranking when priorities are equal, ensuring owner preferences are respected. Daily recurrence generates a task due tomorrow, while weekly recurrence produces one due the following week—both confirming correct timedelta handling. When frequency = none, the function returns None, preventing non-recurring tasks from spawning copies. The next task in a recurrence correctly copies the name and duration, preserving key data. If a task is too long, it produces an unscheduled warning, allowing slot overflow to be detected and reported. Completed tasks are excluded from the schedule so they do not reappear. The total scheduled time matches the sum of task durations, ensuring accurate accounting, and scheduled tasks are ordered by start time so the output remains chronological.

- Why were these tests important?

These tests cover every distinct behavior the system claims to have. Without them, a refactor or class rename could silently break recurrence, conflict detection, or sorting with no visible error until a user runs the app.

**b. Confidence**

- How confident are you that your scheduler works correctly?

4 out of 5. All 17 tests pass and cover the core behaviors. The main gap is the Streamlit UI layer — session state persistence and form submission are not tested automatically.

- What edge cases would you test next if you had more time?

- A task whose preferred_time slot doesn't exist in 
available_time
- Two tasks with identical priority and preference weight — stable sort order
- An owner with no available time slots at all
- mark_complete() called on a task with no due_date — verifies it defaults to today correctly

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

The scheduling algorithm. generate_plan_with_warnings() is clean and readable — it sorts once, fills slots greedily, and reports both unscheduled tasks and start-time conflicts in a single pass. The design also has no hidden state: tasks live on pets, the schedule reads from the owner, and nothing can go out of sync.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

The slot-filling algorithm. Currently it is greedy and first-fit — it places tasks in priority order without checking whether a different arrangement would schedule more tasks total. A backtracking or bin-packing approach would handle tight schedules better. I would also add a fallback slot priority list to the owner so users can control which slot is tried second when the preferred one is full.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

Removing complexity is as important as adding features. The project started with UUIDs, datetime precision, circular object references, and redundant counters — none of which were needed for the actual use case. Simplifying down to time slots, string-based recurrence, and a single source of truth made the system easier to test and less likely to have subtle bugs. AI helped identify what to remove, but the decision to remove it required understanding what the system actually needed to do.
