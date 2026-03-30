import streamlit as st
from pawpal_system import Owner, Pet, Task, Schedule

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to **PawPal+**, a pet care planning assistant that builds a daily schedule
for your pets based on task priority, owner preferences, and available time slots.
"""
)

st.divider()

# --- Session state ---
if "owner" not in st.session_state:
    st.session_state.owner = None
if "pets" not in st.session_state:
    st.session_state.pets = []
if "tasks" not in st.session_state:
    st.session_state.tasks = []

# ── Owner ──────────────────────────────────────────────────────────────────────
st.subheader("Owner + Pets")

st.markdown("#### Owner Information")
col1, col2, col3 = st.columns(3)
with col1:
    owner_name = st.text_input("Owner name", value="Jordan")
with col2:
    owner_pref_walking = st.selectbox("Walking preference", ["high", "medium", "low"], index=0)
with col3:
    owner_pref_feeding = st.selectbox("Feeding preference", ["high", "medium", "low"], index=0)

# ── Add a Pet ──────────────────────────────────────────────────────────────────
st.markdown("#### Add a Pet")
col1, col2, col3, col4 = st.columns(4)
with col1:
    pet_name = st.text_input("Pet name", value="Mochi", key="pet_name_input")
with col2:
    pet_species = st.selectbox("Species", ["dog", "cat", "other"])
with col3:
    pet_age = st.number_input("Age", min_value=0, max_value=30, value=3)
with col4:
    add_pet_btn = st.button("➕ Add Pet", use_container_width=True)

if add_pet_btn:
    existing_names = [p.name.lower() for p in st.session_state.pets]
    if pet_name.strip().lower() in existing_names:
        st.error(f"A pet named **{pet_name}** already exists. Please use a different name.")
    else:
        new_pet = Pet(name=pet_name.strip(), species=pet_species, age=int(pet_age))
        st.session_state.pets.append(new_pet)
        st.success(f"Added **{new_pet.name}** ({pet_species}, age {pet_age})")

if st.session_state.pets:
    st.markdown("#### Current Pets")
    st.table([
        {
            "Pet Name": p.name,
            "Species": p.species.capitalize(),
            "Age": f"{p.age} yr{'s' if p.age != 1 else ''}",
            "Tasks": len(p.tasks),
        }
        for p in st.session_state.pets
    ])
else:
    st.info("No pets yet. Add one above.")

st.divider()

# ── Add a Task ─────────────────────────────────────────────────────────────────
st.markdown("#### Add a Task")
if st.session_state.pets:
    selected_pet_name = st.selectbox("Select pet", [p.name for p in st.session_state.pets])

    col1, col2, col3 = st.columns(3)
    with col1:
        task_title = st.text_input("Task title", value="Morning walk", key="task_title_input")
    with col2:
        task_category = st.selectbox("Category", ["walking", "feeding", "meds", "enrichment", "grooming"])
    with col3:
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        priority = st.selectbox("Priority", [1, 2, 3, 4, 5], index=4, help="5 = Highest priority")
    with col2:
        preferred_time = st.selectbox("Preferred time", ["morning", "afternoon", "evening", "anytime"])
    with col3:
        frequency = st.selectbox("Frequency", ["daily", "weekly", "none"])
    with col4:
        add_task_btn = st.button("➕ Add Task", use_container_width=True)

    if add_task_btn:
        task = Task(
            name=task_title,
            category=task_category,
            duration=int(duration),
            priority=int(priority),
            preferred_time=preferred_time,
            frequency=frequency,
        )
        pet = next((p for p in st.session_state.pets if p.name == selected_pet_name), None)
        if pet is not None:
            pet.tasks.append(task)
            st.session_state.tasks.append(task)
            st.success(f"Added **{task.name}** to {pet.name}")

    if st.session_state.tasks:
        st.markdown("#### Current Tasks")
        st.table([
            {
                "Task": t.name,
                "Pet": next((p.name for p in st.session_state.pets if t in p.tasks), "?"),
                "Category": t.category.capitalize(),
                "Duration": f"{t.duration} min",
                "Priority": f"{'★' * t.priority}{'☆' * (5 - t.priority)}",
                "Preferred Time": t.preferred_time.capitalize(),
                "Frequency": t.frequency.capitalize(),
            }
            for t in st.session_state.tasks
        ])
else:
    st.info("Add at least one pet before adding tasks.")

st.divider()

# ── Generate Schedule ──────────────────────────────────────────────────────────
st.subheader("📅 Build Schedule")
st.caption("Sorts tasks by priority and owner preferences, then fills time slots. Flags anything that does not fit.")

if st.button("🔄 Generate Schedule", use_container_width=True, type="primary"):
    if not st.session_state.pets:
        st.error("No pets available. Add a pet first.")
    elif not st.session_state.tasks:
        st.warning("No tasks added. Add at least one task before generating a schedule.")
    else:
        owner = Owner(
            name=owner_name,
            available_time={"morning": (8, 12), "afternoon": (13, 17), "evening": (17, 21)},
            preferences={"walking": owner_pref_walking, "feeding": owner_pref_feeding},
            pets=st.session_state.pets,
        )
        st.session_state.owner = owner

        schedule, warnings = Schedule.generate_plan_with_warnings(date="today", owner=owner)

        # ── Summary metrics ────────────────────────────────────────────────────
        all_tasks = owner.get_all_tasks()
        pending   = [t for t in all_tasks if not t.completed]
        scheduled = schedule.get_plan_summary()
        unscheduled_warnings = [w for w in warnings if "Could not schedule" in w]
        conflict_warnings    = [w for w in warnings if "Could not schedule" not in w]

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Pets", len(st.session_state.pets))
        with col2:
            st.metric("Pending tasks", len(pending))
        with col3:
            st.metric("Scheduled", len(scheduled))
        with col4:
            st.metric("Unscheduled", len(unscheduled_warnings),
                      delta=f"-{len(unscheduled_warnings)}" if unscheduled_warnings else None,
                      delta_color="inverse")

        st.markdown("---")

        # ── Conflict / unscheduled warnings ───────────────────────────────────
        if conflict_warnings:
            st.markdown("#### ⚠️ Time Conflicts")
            st.caption("These tasks were still scheduled but share a start time with another task.")
            for w in conflict_warnings:
                st.warning(w)

        if unscheduled_warnings:
            st.markdown("#### ❌ Tasks That Did Not Fit")
            st.caption("These tasks could not be placed in any available time slot.")
            for w in unscheduled_warnings:
                st.error(w)

        if not warnings:
            st.success("No conflicts or unscheduled tasks — all tasks fit cleanly.")

        st.markdown("---")

        # ── Tasks sorted by priority × preference ─────────────────────────────
        st.markdown("#### 📌 Task Priority Ranking")
        st.caption("Sorted by priority × preference weight — this is the order the scheduler considers tasks.")
        sorted_tasks = schedule.sort_tasks(pending, owner.preferences)
        if sorted_tasks:
            st.table([
                {
                    "Rank": idx,
                    "Task": t.name,
                    "Pet": next((p.name for p in st.session_state.pets if t in p.tasks), "?"),
                    "Category": t.category.capitalize(),
                    "Priority": f"{'★' * t.priority}{'☆' * (5 - t.priority)}",
                    "Pref. Weight": {"high": "High (×3)", "medium": "Med (×2)", "low": "Low (×1)"}.get(
                        owner.preferences.get(t.category, "medium"), "Med (×2)"
                    ),
                    "Preferred Time": t.preferred_time.capitalize(),
                }
                for idx, t in enumerate(sorted_tasks, start=1)
            ])

        st.markdown("---")

        # ── Final schedule ─────────────────────────────────────────────────────
        st.markdown("#### ✅ Final Schedule")
        st.caption(schedule.explain_plan())
        if scheduled:
            st.table([
                {
                    "Task": e["task"].name,
                    "Pet": next((p.name for p in st.session_state.pets if e["task"] in p.tasks), "?"),
                    "Start": e["start_time"],
                    "End": e["end_time"],
                    "Duration": f"{e['task'].duration} min",
                    "Reason": e["reason"],
                }
                for e in scheduled
            ])
        else:
            st.warning("No tasks could be placed in the available slots.")
