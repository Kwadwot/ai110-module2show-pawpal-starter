import streamlit as st

from pawpal_system import Task, Pet, Owner, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

st.subheader("Quick Demo Inputs (UI only)")
owner_name = st.text_input("Owner name", value="Jordan")
pet_name = st.text_input("Pet name", value="Mochi")
species = st.selectbox("Species", ["dog", "cat", "other"])
pet_age = st.number_input("Pet age (years)", min_value=0, max_value=40, value=2)
available_time_minutes = st.number_input(
    "Available care time today (minutes)", min_value=0, max_value=720, value=60
)

st.markdown("### Tasks")
st.caption("Add a few tasks. In your final version, these should feed into your scheduler.")

if "owner" not in st.session_state:
    st.session_state["owner"] = Owner(
        name=owner_name,
        available_time_minutes=int(available_time_minutes),
        preferences=[],
        pets=[],
    )

owner_obj = st.session_state["owner"]

if owner_obj.get_name() != owner_name:
    st.session_state["owner"] = Owner(
        name=owner_name,
        available_time_minutes=int(available_time_minutes),
        preferences=owner_obj.get_preferences(),
        pets=[],
    )
    owner_obj = st.session_state["owner"]

owner_obj.update_available_time(int(available_time_minutes))

if "scheduler" not in st.session_state or st.session_state["scheduler"].owner is not owner_obj:
    st.session_state["scheduler"] = Scheduler(owner_obj)

scheduler_obj = st.session_state["scheduler"]


def get_or_create_pet(owner: Owner, name: str, pet_species: str, age: int) -> Pet:
    for existing_pet in owner.get_pets():
        if existing_pet.name == name:
            return existing_pet

    new_pet = Pet(name=name, species=pet_species, age=age)
    owner.add_pet(new_pet)
    return new_pet

col1, col2, col3 = st.columns(3)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col3:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

if st.button("Add task"):
    try:
        pet_obj = get_or_create_pet(owner_obj, pet_name, species, int(pet_age))
        task_obj = Task(
            name=task_title,
            duration_minutes=int(duration),
            priority=priority,
            category="care",
            description=f"{priority.title()} priority task for {pet_name}",
        )
        pet_obj.add_task(task_obj)
        st.success(f"Added task '{task_obj.name}' for {pet_obj.name}.")
    except ValueError as error:
        st.error(str(error))

current_pet = None
for existing_pet in owner_obj.get_pets():
    if existing_pet.name == pet_name:
        current_pet = existing_pet
        break

if current_pet and current_pet.get_tasks():
    sorted_pet_tasks = scheduler_obj.sort_by_time(current_pet.get_tasks())
    current_tasks = [
        {
            "title": task.get_name(),
            "duration_minutes": task.get_duration(),
            "priority": task.get_priority(),
            "category": task.get_category(),
        }
        for task in sorted_pet_tasks
    ]
    st.write("Current tasks (sorted by duration):")
    st.table(current_tasks)

    st.markdown("### Optional task times (HH:MM)")
    st.caption("Enter times to check for conflicts using Scheduler.detect_schedule_conflicts().")

    scheduled_times_by_task_name: dict[str, str] = {}
    for task in sorted_pet_tasks:
        time_input = st.text_input(
            f"Time for {task.get_name()}",
            key=f"time_{current_pet.get_name()}_{task.get_name()}",
            placeholder="e.g., 08:30",
        )
        if time_input.strip():
            scheduled_times_by_task_name[task.get_name()] = time_input

    if scheduled_times_by_task_name:
        conflict_warnings = scheduler_obj.detect_schedule_conflicts(scheduled_times_by_task_name)
        if conflict_warnings:
            for warning in conflict_warnings:
                st.warning(warning)
        else:
            st.success("No schedule conflicts detected for the provided times.")
else:
    st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Build Schedule")
st.caption("This button should call your scheduling logic once you implement it.")

if st.button("Generate schedule"):
    owner_obj = st.session_state.get("owner")
    if not isinstance(owner_obj, Owner):
        st.error("Owner profile is missing from session state.")
    else:
        scheduler_obj = st.session_state.get("scheduler")
        if not isinstance(scheduler_obj, Scheduler):
            scheduler_obj = Scheduler(owner_obj)
            st.session_state["scheduler"] = scheduler_obj

        plan_result = scheduler_obj.generate_plan()
        explanation = scheduler_obj.explain_plan(plan_result)
        incomplete_tasks = scheduler_obj.filter_tasks(is_completed=False)
        sorted_incomplete_tasks = scheduler_obj.sort_by_time(incomplete_tasks)

        st.success("Schedule generated with Scheduler.generate_plan().")
        st.write(plan_result.summary)

        if sorted_incomplete_tasks:
            st.markdown("### Incomplete tasks (sorted by duration)")
            st.table(
                [
                    {
                        "task": task.get_name(),
                        "duration_minutes": task.get_duration(),
                        "priority": task.get_priority(),
                    }
                    for task in sorted_incomplete_tasks
                ]
            )

        if plan_result.scheduled_tasks:
            sorted_scheduled_tasks = scheduler_obj.sort_by_time(plan_result.scheduled_tasks)
            st.markdown("### Scheduled tasks")
            st.table(
                [
                    {
                        "task": task.get_name(),
                        "duration_minutes": task.get_duration(),
                        "priority": task.get_priority(),
                    }
                    for task in sorted_scheduled_tasks
                ]
            )

        if plan_result.skipped_tasks:
            st.markdown("### Skipped tasks")
            st.table(
                [
                    {
                        "task": task.get_name(),
                        "duration_minutes": task.get_duration(),
                        "priority": task.get_priority(),
                        "reason": plan_result.reasons_by_task_name.get(task.get_name(), ""),
                    }
                    for task in plan_result.skipped_tasks
                ]
            )

        with st.expander("Plan explanation"):
            st.text(explanation)
