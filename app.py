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

st.subheader("Owner + Pets")

st.markdown("#### Owner Information")
col1, col2, col3 = st.columns(3)
with col1:
    owner_name = st.text_input("Owner name", value="Jordan")
with col2:
    owner_pref_walking = st.selectbox("Walking preference", ["high", "medium", "low"], index=0)
with col3:
    owner_pref_feeding = st.selectbox("Feeding preference", ["high", "medium", "low"], index=0)

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
    new_pet = Pet(name=pet_name, species=pet_species, age=int(pet_age))
    st.session_state.pets.append(new_pet)
    st.success(f"✅ Added pet: **{new_pet.name}** ({pet_species}, age {pet_age})")

if st.session_state.pets:
    st.markdown("#### Current Pets")
    pets_data = [
        {
            "Pet Name": p.name,
            "Species": p.species.capitalize(),
            "Age": f"{p.age} year{'s' if p.age != 1 else ''}",
            "Tasks": len(p.tasks),
        }
        for p in st.session_state.pets
    ]
    st.table(pets_data)
else:
    st.info("📋 No pets yet. Add one above.")

st.divider()

st.markdown("#### Add a Task")
if st.session_state.pets:
    current_pet_names = [p.name for p in st.session_state.pets]
    selected_pet_name = st.selectbox("Select pet", current_pet_names)

    col1, col2, col3 = st.columns(3)
    with col1:
        task_title = st.text_input("Task title", value="Morning walk", key="task_title_input")
    with col2:
        task_category = st.selectbox("Category", ["walking", "feeding", "meds", "enrichment", "grooming"])
    with col3:
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)

    col1, col2, col3 = st.columns(3)
    with col1:
        priority = st.selectbox("Priority", [1, 2, 3, 4, 5], index=4, help="5 = Highest priority")
    with col2:
        preferred_time = st.selectbox("Preferred time", ["morning", "afternoon", "evening", "anytime"])
    with col3:
        add_task_btn = st.button("➕ Add Task", use_container_width=True)

    if add_task_btn:
        task = Task(
            name=task_title,
            category=task_category,
            duration=int(duration),
            priority=int(priority),
            preferred_time=preferred_time,
        )
        pet = next((p for p in st.session_state.pets if p.name == selected_pet_name), None)
        if pet is not None:
            pet.tasks.append(task)
            st.session_state.tasks.append(task)
            st.success(f"✅ Added task to **{pet.name}**: {task.name}")

    if st.session_state.tasks:
        st.markdown("#### Current Tasks")
        tasks_data = [
            {
                "Task": t.name,
                "Pet": next((p.name for p in st.session_state.pets if t in p.tasks), "Unknown"),
                "Category": t.category.capitalize(),
                "Duration": f"{t.duration} min",
                "Priority": "🔴" * t.priority,
                "Time": t.preferred_time.capitalize(),
            }
            for t in st.session_state.tasks
        ]
        st.table(tasks_data)
else:
    st.info("📋 Add at least one pet before adding tasks.")

st.divider()

st.subheader("📅 Build Schedule")
st.caption("Generate a schedule from pets and tasks with automatic conflict detection.")

if st.button("🔄 Generate Schedule", use_container_width=True, type="primary"):
    if not st.session_state.pets:
        st.error("❌ No pets available. Add a pet first.")
    elif not st.session_state.tasks:
        st.warning("⚠️ No tasks added. Add at least one task before generating a schedule.")
    else:
        owner = Owner(
            name=owner_name,
            available_time={"morning": (8, 12), "afternoon": (13, 17), "evening": (17, 21)},
            preferences={"walking": owner_pref_walking, "feeding": owner_pref_feeding},
            pets=st.session_state.pets,
        )
        st.session_state.owner = owner

        schedule, warnings = Schedule.generate_plan_with_warnings(date="today", owner=owner)

        st.markdown("#### Owner Summary")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Owner", owner_name)
        with col2:
            st.metric("Pets", len(st.session_state.pets))
        with col3:
            st.metric("Total Tasks", len(st.session_state.tasks))

        st.markdown("---")

        st.markdown("#### 📋 Schedule Plan")
        st.info(schedule.explain_plan())

        if warnings:
            st.markdown("#### ⚠️ Conflict Warnings")
            with st.container(border=True):
                for warning in warnings:
                    st.warning(warning, icon="⚠️")
        else:
            st.success("✅ No scheduling conflicts detected!", icon="✅")

        st.markdown("---")

        all_tasks = owner.get_all_tasks()
        if all_tasks:
            st.markdown("#### 📌 Tasks Sorted by Priority & Preferences")
            sorted_tasks = schedule.sort_tasks(all_tasks, owner.preferences)
            sorted_tasks_data = [
                {
                    "Rank": idx,
                    "Task": task.name,
                    "Pet": next((p.name for p in st.session_state.pets if task in p.tasks), "Unknown"),
                    "Category": task.category.capitalize(),
                    "Duration": f"{task.duration} min",
                    "Priority": f"{task.priority}/5",
                    "Time": task.preferred_time.capitalize(),
                }
                for idx, task in enumerate(sorted_tasks, start=1)
            ]
            st.table(sorted_tasks_data)

        st.markdown("---")

        if schedule.get_plan_summary():
            st.markdown("#### ✅ Scheduled Tasks")
            scheduled_data = [
                {
                    "Task": e["task"].name,
                    "Pet": next((p.name for p in st.session_state.pets if e["task"] in p.tasks), "Unknown"),
                    "Start": e["start_time"],
                    "End": e["end_time"],
                    "Reason": e["reason"],
                }
                for e in schedule.get_plan_summary()
            ]
            st.table(scheduled_data)
        else:
            st.warning("📭 No tasks fit in the available slots.", icon="⚠️")
