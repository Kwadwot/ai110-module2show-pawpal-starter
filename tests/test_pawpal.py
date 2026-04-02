import sys
from pathlib import Path
from datetime import date

# Add parent directory to path so we can import pawpal_system
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pawpal_system import Owner, Pet, Scheduler, Task


def test_task_completion():
    """Verify that calling mark_completed() changes the task's status."""
    task = Task(
        name="feed_lucky",
        duration_minutes=10,
        priority="high",
        category="feed",
        description="Feed the dog.",
    )

    # Initially, task should not be completed
    assert not task.is_done(), "Task should not be completed initially"

    # Mark task as completed
    task.mark_completed()

    # Now task should be completed
    assert task.is_done(), "Task should be completed after calling mark_completed()"

    # Mark task as incomplete
    task.mark_incomplete()

    # Task should no longer be completed
    assert not task.is_done(), "Task should not be completed after calling mark_incomplete()"


def test_task_addition():
    """Verify that adding a task to a Pet increases that pet's task count."""
    pet = Pet(name="Lucky", species="dog", age=4)

    # Initially, pet should have no tasks
    assert len(pet.get_tasks()) == 0, "Pet should have no tasks initially"

    # Create and add first task
    task1 = Task(
        name="feed_lucky",
        duration_minutes=10,
        priority="high",
        category="feed",
    )
    pet.add_task(task1)

    # Pet should now have 1 task
    assert len(pet.get_tasks()) == 1, "Pet should have 1 task after adding one"

    # Create and add second task
    task2 = Task(
        name="walk_lucky",
        duration_minutes=30,
        priority="medium",
        category="walk",
    )
    pet.add_task(task2)

    # Pet should now have 2 tasks
    assert len(pet.get_tasks()) == 2, "Pet should have 2 tasks after adding a second task"


def test_sort_by_time_ascending_uses_duration_minutes_hhmm():
    """Verify Scheduler.sort_by_time() sorts by HH:MM computed from duration_minutes."""
    owner = Owner(name="Jordan", available_time_minutes=60, preferences=[], pets=[])
    scheduler = Scheduler(owner)

    tasks = [
        Task(name="task_130", duration_minutes=130, priority="low", category="care"),
        Task(name="task_5", duration_minutes=5, priority="high", category="care"),
        Task(name="task_65", duration_minutes=65, priority="medium", category="care"),
    ]

    sorted_tasks = scheduler.sort_by_time(tasks)

    assert [task.name for task in sorted_tasks] == ["task_5", "task_65", "task_130"]


def test_sort_by_time_descending_uses_duration_minutes_hhmm():
    """Verify Scheduler.sort_by_time() supports descending chronological sort order."""
    owner = Owner(name="Jordan", available_time_minutes=60, preferences=[], pets=[])
    scheduler = Scheduler(owner)

    tasks = [
        Task(name="task_5", duration_minutes=5, priority="high", category="care"),
        Task(name="task_130", duration_minutes=130, priority="low", category="care"),
        Task(name="task_65", duration_minutes=65, priority="medium", category="care"),
    ]

    sorted_tasks = scheduler.sort_by_time(tasks, descending=True)

    assert [task.name for task in sorted_tasks] == ["task_130", "task_65", "task_5"]


def test_sort_by_time_uses_name_tie_breaker_for_equal_duration():
    """Verify deterministic ordering when two tasks have the same duration."""
    owner = Owner(name="Jordan", available_time_minutes=60, preferences=[], pets=[])
    scheduler = Scheduler(owner)

    tasks = [
        Task(name="beta", duration_minutes=30, priority="high", category="care"),
        Task(name="alpha", duration_minutes=30, priority="high", category="care"),
    ]

    sorted_tasks = scheduler.sort_by_time(tasks)

    assert [task.name for task in sorted_tasks] == ["alpha", "beta"]


def test_filter_tasks_by_completion_status_only():
    """Verify filtering by completion status returns only matching tasks."""
    lucky = Pet(name="Lucky", species="dog", age=4)
    feed_task = Task(name="feed_lucky", duration_minutes=10, priority="high", category="feed")
    walk_task = Task(name="walk_lucky", duration_minutes=30, priority="medium", category="walk")
    walk_task.mark_completed()
    lucky.add_task(feed_task)
    lucky.add_task(walk_task)

    owner = Owner(name="Jordan", available_time_minutes=60, preferences=[], pets=[lucky])
    scheduler = Scheduler(owner)

    completed_tasks = scheduler.filter_tasks(is_completed=True)
    incomplete_tasks = scheduler.filter_tasks(is_completed=False)

    assert [task.name for task in completed_tasks] == ["walk_lucky"]
    assert [task.name for task in incomplete_tasks] == ["feed_lucky"]


def test_filter_tasks_by_pet_name_only():
    """Verify filtering by pet name includes only tasks for that pet."""
    lucky = Pet(name="Lucky", species="dog", age=4)
    mochi = Pet(name="Mochi", species="cat", age=2)
    lucky.add_task(Task(name="feed_lucky", duration_minutes=10, priority="high", category="feed"))
    mochi.add_task(Task(name="litter_mochi", duration_minutes=15, priority="high", category="litter"))

    owner = Owner(name="Jordan", available_time_minutes=60, preferences=[], pets=[lucky, mochi])
    scheduler = Scheduler(owner)

    lucky_tasks = scheduler.filter_tasks(pet_name="  lucky  ")

    assert [task.name for task in lucky_tasks] == ["feed_lucky"]


def test_filter_tasks_by_completion_and_pet_name():
    """Verify filters can be combined to narrow the task list."""
    lucky = Pet(name="Lucky", species="dog", age=4)
    mochi = Pet(name="Mochi", species="cat", age=2)

    lucky_done = Task(name="walk_lucky", duration_minutes=30, priority="medium", category="walk")
    lucky_done.mark_completed()
    lucky_todo = Task(name="feed_lucky", duration_minutes=10, priority="high", category="feed")
    mochi_done = Task(name="litter_mochi", duration_minutes=15, priority="high", category="litter")
    mochi_done.mark_completed()

    lucky.add_task(lucky_done)
    lucky.add_task(lucky_todo)
    mochi.add_task(mochi_done)

    owner = Owner(name="Jordan", available_time_minutes=60, preferences=[], pets=[lucky, mochi])
    scheduler = Scheduler(owner)

    filtered = scheduler.filter_tasks(is_completed=True, pet_name="Lucky")

    assert [task.name for task in filtered] == ["walk_lucky"]


def test_daily_task_next_due_date_uses_timedelta_one_day():
    """Verify daily tasks advance to today + 1 day using timedelta."""
    task = Task(
        name="feed_lucky",
        duration_minutes=10,
        priority="high",
        category="feed",
        frequency="daily",
        due_date=date(2026, 4, 1),
    )

    next_due_date = task.get_next_due_date(date(2026, 4, 1))

    assert next_due_date == date(2026, 4, 2)


def test_weekly_task_next_due_date_uses_timedelta_seven_days():
    """Verify weekly tasks advance by exactly 7 days using timedelta."""
    task = Task(
        name="groom_lucky",
        duration_minutes=20,
        priority="medium",
        category="grooming",
        frequency="weekly",
        due_date=date(2026, 4, 1),
    )

    next_due_date = task.get_next_due_date(date(2026, 4, 1))

    assert next_due_date == date(2026, 4, 8)


def test_complete_task_for_pet_creates_next_recurring_instance():
    """Verify completing a recurring task appends the next occurrence to the same pet."""
    lucky = Pet(name="Lucky", species="dog", age=4)
    recurring_task = Task(
        name="feed_lucky",
        duration_minutes=10,
        priority="high",
        category="feed",
        frequency="daily",
        due_date=date(2026, 4, 1),
    )
    lucky.add_task(recurring_task)

    owner = Owner(name="Jordan", available_time_minutes=60, preferences=[], pets=[lucky])
    scheduler = Scheduler(owner)

    next_task = scheduler.complete_task_for_pet("Lucky", "feed_lucky", completed_on=date(2026, 4, 1))

    assert recurring_task.is_done()
    assert next_task is not None
    assert next_task.get_due_date() == date(2026, 4, 2)
    assert next_task.get_name() == "feed_lucky_2026-04-02"
    assert [task.get_name() for task in lucky.get_tasks()] == ["feed_lucky", "feed_lucky_2026-04-02"]


def test_detect_schedule_conflicts_for_different_pets_returns_warning():
    """Verify conflicts at the same time across pets produce a warning message."""
    lucky = Pet(name="Lucky", species="dog", age=4)
    mochi = Pet(name="Mochi", species="cat", age=2)
    lucky.add_task(Task(name="feed_lucky", duration_minutes=10, priority="high", category="feed"))
    mochi.add_task(Task(name="litter_mochi", duration_minutes=15, priority="high", category="litter"))

    owner = Owner(name="Jordan", available_time_minutes=90, preferences=[], pets=[lucky, mochi])
    scheduler = Scheduler(owner)

    warnings = scheduler.detect_schedule_conflicts(
        {"feed_lucky": "09:00", "litter_mochi": "09:00"}
    )

    assert len(warnings) == 1
    assert "multi-pet conflict at 09:00" in warnings[0]


def test_detect_schedule_conflicts_for_same_pet_returns_warning():
    """Verify two tasks for one pet at the same time produce a same-pet warning."""
    lucky = Pet(name="Lucky", species="dog", age=4)
    lucky.add_task(Task(name="feed_lucky", duration_minutes=10, priority="high", category="feed"))
    lucky.add_task(Task(name="walk_lucky", duration_minutes=30, priority="medium", category="walk"))

    owner = Owner(name="Jordan", available_time_minutes=90, preferences=[], pets=[lucky])
    scheduler = Scheduler(owner)

    warnings = scheduler.detect_schedule_conflicts(
        {"feed_lucky": "07:30", "walk_lucky": "07:30"}
    )

    assert len(warnings) == 1
    assert "same-pet conflict at 07:30" in warnings[0]


def test_detect_schedule_conflicts_invalid_time_returns_warning_not_exception():
    """Verify invalid times are reported as warnings without raising exceptions."""
    lucky = Pet(name="Lucky", species="dog", age=4)
    lucky.add_task(Task(name="feed_lucky", duration_minutes=10, priority="high", category="feed"))

    owner = Owner(name="Jordan", available_time_minutes=90, preferences=[], pets=[lucky])
    scheduler = Scheduler(owner)

    warnings = scheduler.detect_schedule_conflicts({"feed_lucky": "9:00"})

    assert len(warnings) == 1
    assert "invalid time '9:00'" in warnings[0]
