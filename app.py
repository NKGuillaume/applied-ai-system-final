import streamlit as st
from datetime import datetime, timezone, date, time as dtime
from pawpal_system import Owner, Pet, Task, Scheduler, Recurrence

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

# --- Session state init ---
if "owner" not in st.session_state:
    st.session_state.owner = Owner(name="", contact_info="")
if "scheduler" not in st.session_state:
    st.session_state.scheduler = Scheduler(st.session_state.owner)

owner: Owner = st.session_state.owner
scheduler: Scheduler = st.session_state.scheduler

# --- Owner setup ---
st.subheader("Owner")
with st.form("owner_form"):
    owner_name = st.text_input("Your name", value=owner.name or "Jordan")
    contact = st.text_input("Contact email", value=owner.contact_info or "")
    if st.form_submit_button("Save owner"):
        owner.name = owner_name
        owner.contact_info = contact
        st.success(f"Owner set to {owner.name}")

st.divider()

# --- Add a Pet ---
st.subheader("Add a Pet")
with st.form("add_pet_form"):
    pet_name = st.text_input("Pet name", value="Mochi")
    pet_age = st.number_input("Age (years)", min_value=0, max_value=30, value=2)
    pet_type = st.selectbox("Species", ["Dog", "Cat", "Other"])
    food_type = st.selectbox("Food type", ["Dry", "Wet", "Raw"])
    if st.form_submit_button("Add pet"):
        pet = Pet(name=pet_name, age=int(pet_age), type_=pet_type, food_type=food_type)
        owner.add_pet(pet)
        st.success(f"Added {pet.name} to {owner.name}'s pets.")

if owner.pets:
    st.markdown("**Current pets:**")
    for p in owner.pets:
        st.write(f"- {p.name} ({p.type_}, age {p.age}) — {len(p.tasks)} task(s)")
else:
    st.info("No pets yet. Add one above.")

st.divider()

# --- Schedule a Task ---
st.subheader("Schedule a Task")
if not owner.pets:
    st.warning("Add a pet first before scheduling tasks.")
else:
    with st.form("add_task_form"):
        pet_names = [p.name for p in owner.pets]
        selected_pet_name = st.selectbox("Select pet", pet_names)
        task_title = st.text_input("Task title", value="Morning walk")
        task_desc = st.text_input("Description", value="")
        task_date = st.date_input("Date", value=date.today())
        task_time = st.time_input("Time", value=dtime(8, 0))
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=480, value=30)
        recurrence = st.selectbox("Recurrence", [r.value for r in Recurrence])

        if st.form_submit_button("Schedule task"):
            selected_pet = next(p for p in owner.pets if p.name == selected_pet_name)
            scheduled_dt = datetime.combine(task_date, task_time, tzinfo=timezone.utc)
            task = Task(
                title=task_title,
                description=task_desc,
                duration_minutes=int(duration),
                recurrence=Recurrence(recurrence),
            )
            scheduler.schedule_task(task, selected_pet, time=scheduled_dt)
            st.success(f"Scheduled '{task.title}' for {selected_pet.name} at {scheduled_dt.strftime('%Y-%m-%d %H:%M')} UTC")

st.divider()

# --- View Schedule ---
st.subheader("Upcoming Schedule")
if st.button("Generate schedule"):
    upcoming = scheduler.get_upcoming_tasks()
    if not upcoming:
        st.info("No upcoming tasks.")
    else:
        rows = []
        now = datetime.now(timezone.utc)
        for t in upcoming:
            delta = t.time - now
            hours = int(delta.total_seconds() // 3600)
            mins = int((delta.total_seconds() % 3600) // 60)
            eta = f"in {hours}h {mins}m" if delta.total_seconds() > 60 else "now"
            pet = next((p for p in owner.pets if p.id == t.pet_id), None)
            rows.append({
                "Pet": pet.name if pet else "?",
                "Task": t.title,
                "Time": t.time.strftime("%Y-%m-%d %H:%M UTC"),
                "Duration (min)": t.duration_minutes,
                "ETA": eta,
                "Recurrence": t.recurrence.value,
            })
        st.table(rows)
